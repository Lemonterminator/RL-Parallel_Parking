"""Exact oriented-box geometry shared by simulation and planning."""

from __future__ import annotations

import math
from dataclasses import dataclass
from numbers import Real

from parking_rl.core.frames import ObjectCentroidWorldPose, RearAxleWorldPose
from parking_rl.core.state import ObjectState, VehicleSpec

Point2 = tuple[float, float]


def _require_finite(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number, not {type(value).__name__}")
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")


def _require_positive(name: str, value: object) -> None:
    _require_finite(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def _require_exact_type(name: str, value: object, expected: type[object]) -> None:
    if type(value) is not expected:
        raise TypeError(f"{name} must be exactly {expected.__name__}")


@dataclass(frozen=True, slots=True)
class OBB:
    """A planar oriented bounding box referenced at its centroid."""

    center_x_m: float
    center_y_m: float
    heading_rad: float
    length_m: float
    width_m: float

    def __post_init__(self) -> None:
        _require_finite("center_x_m", self.center_x_m)
        _require_finite("center_y_m", self.center_y_m)
        _require_finite("heading_rad", self.heading_rad)
        if not -math.pi <= self.heading_rad < math.pi:
            raise ValueError("heading_rad must be within [-pi, pi)")
        _require_positive("length_m", self.length_m)
        _require_positive("width_m", self.width_m)


def obb_corners(box: OBB) -> tuple[Point2, Point2, Point2, Point2]:
    """Return the four box corners in a stable counter-clockwise order."""

    _require_exact_type("box", box, OBB)
    half_length = 0.5 * box.length_m
    half_width = 0.5 * box.width_m
    cosine = math.cos(box.heading_rad)
    sine = math.sin(box.heading_rad)

    def world(local_x: float, local_y: float) -> Point2:
        return (
            box.center_x_m + cosine * local_x - sine * local_y,
            box.center_y_m + sine * local_x + cosine * local_y,
        )

    return (
        world(-half_length, -half_width),
        world(half_length, -half_width),
        world(half_length, half_width),
        world(-half_length, half_width),
    )


def vehicle_front_extent_m(vehicle: VehicleSpec) -> float:
    """Return the longitudinal rear-axle-to-front-bumper distance."""

    _require_exact_type("vehicle", vehicle, VehicleSpec)
    return vehicle.wheelbase_m + vehicle.front_overhang_m


def vehicle_farthest_corner_m(vehicle: VehicleSpec) -> float:
    """Return the farthest footprint-corner radius from the rear axle."""

    _require_exact_type("vehicle", vehicle, VehicleSpec)
    longitudinal_extent = max(vehicle_front_extent_m(vehicle), vehicle.rear_overhang_m)
    return math.hypot(longitudinal_extent, 0.5 * vehicle.width_m)


def minimum_turn_radius_m(vehicle: VehicleSpec) -> float:
    """Return the rear-axle bicycle model's minimum turning radius."""

    _require_exact_type("vehicle", vehicle, VehicleSpec)
    return vehicle.wheelbase_m / math.tan(vehicle.max_steering_angle_rad)


def vehicle_obb(pose: RearAxleWorldPose, vehicle: VehicleSpec) -> OBB:
    """Place a vehicle footprint exactly relative to its rear-axle midpoint."""

    _require_exact_type("pose", pose, RearAxleWorldPose)
    _require_exact_type("vehicle", vehicle, VehicleSpec)
    rear_extent = vehicle.rear_overhang_m
    front_extent = vehicle_front_extent_m(vehicle)
    center_offset = 0.5 * (front_extent - rear_extent)
    return OBB(
        center_x_m=pose.x_m + center_offset * math.cos(pose.heading_rad),
        center_y_m=pose.y_m + center_offset * math.sin(pose.heading_rad),
        heading_rad=pose.heading_rad,
        length_m=vehicle.length_m,
        width_m=vehicle.width_m,
    )


def object_obb(obj: ObjectState) -> OBB:
    """Construct an object box whose source pose is explicitly centroid-based."""

    _require_exact_type("obj", obj, ObjectState)
    pose = obj.pose
    _require_exact_type("obj.pose", pose, ObjectCentroidWorldPose)
    return OBB(pose.x_m, pose.y_m, pose.heading_rad, obj.length_m, obj.width_m)


def _axes(box: OBB) -> tuple[Point2, Point2]:
    cosine = math.cos(box.heading_rad)
    sine = math.sin(box.heading_rad)
    return ((cosine, sine), (-sine, cosine))


def _project(corners: tuple[Point2, ...], axis: Point2) -> tuple[float, float]:
    projections = tuple(x * axis[0] + y * axis[1] for x, y in corners)
    return min(projections), max(projections)


def _interval_separation(first: tuple[float, float], second: tuple[float, float]) -> float:
    return max(second[0] - first[1], first[0] - second[1], 0.0)


def sat_overlap(first: OBB, second: OBB) -> bool:
    """Return whether two boxes overlap or touch, using exact SAT axes."""

    _require_exact_type("first", first, OBB)
    _require_exact_type("second", second, OBB)
    first_corners = obb_corners(first)
    second_corners = obb_corners(second)
    return all(
        _interval_separation(
            _project(first_corners, axis),
            _project(second_corners, axis),
        )
        == 0.0
        for axis in (*_axes(first), *_axes(second))
    )


def sat_penetration_depth(first: OBB, second: OBB) -> float:
    """Return the minimum SAT translation depth, including containment."""

    _require_exact_type("first", first, OBB)
    _require_exact_type("second", second, OBB)
    first_corners = obb_corners(first)
    second_corners = obb_corners(second)
    depths: list[float] = []
    for axis in (*_axes(first), *_axes(second)):
        first_min, first_max = _project(first_corners, axis)
        second_min, second_max = _project(second_corners, axis)
        if first_max < second_min or second_max < first_min:
            return 0.0
        depths.append(min(first_max - second_min, second_max - first_min))
    return max(0.0, min(depths))


def sat_face_normal_gap(first: OBB, second: OBB) -> float:
    """Return the SAT face-normal separation lower bound, not Euclidean distance."""

    _require_exact_type("first", first, OBB)
    _require_exact_type("second", second, OBB)
    first_corners = obb_corners(first)
    second_corners = obb_corners(second)
    return max(
        _interval_separation(
            _project(first_corners, axis),
            _project(second_corners, axis),
        )
        for axis in (*_axes(first), *_axes(second))
    )


def _point_segment_distance(point: Point2, start: Point2, end: Point2) -> float:
    segment_x = end[0] - start[0]
    segment_y = end[1] - start[1]
    squared_length = segment_x * segment_x + segment_y * segment_y
    projection = (
        (point[0] - start[0]) * segment_x + (point[1] - start[1]) * segment_y
    ) / squared_length
    fraction = min(1.0, max(0.0, projection))
    closest_x = start[0] + fraction * segment_x
    closest_y = start[1] + fraction * segment_y
    return math.hypot(point[0] - closest_x, point[1] - closest_y)


def _vertex_edge_distance(
    source: tuple[Point2, Point2, Point2, Point2],
    target: tuple[Point2, Point2, Point2, Point2],
) -> float:
    return min(
        _point_segment_distance(point, target[index], target[(index + 1) % 4])
        for point in source
        for index in range(4)
    )


def obb_signed_distance(first: OBB, second: OBB) -> float:
    """Return exact signed Euclidean distance: positive apart, negative inside."""

    _require_exact_type("first", first, OBB)
    _require_exact_type("second", second, OBB)
    if sat_overlap(first, second):
        penetration = sat_penetration_depth(first, second)
        return 0.0 if penetration == 0.0 else -penetration
    first_corners = obb_corners(first)
    second_corners = obb_corners(second)
    return min(
        _vertex_edge_distance(first_corners, second_corners),
        _vertex_edge_distance(second_corners, first_corners),
    )
