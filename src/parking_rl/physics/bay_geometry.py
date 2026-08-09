"""Closed-form and numerical geometry for reverse-bay parking."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from numbers import Real

from parking_rl.core.frames import RearAxleWorldPose
from parking_rl.core.state import VehicleSpec
from parking_rl.physics.geometry import (
    minimum_turn_radius_m,
    obb_corners,
    vehicle_front_extent_m,
    vehicle_obb,
)

Point2 = tuple[float, float]


class InfeasibleBayGeometry(ValueError):
    """Raised when the requested clear mouth cannot contain the vehicle."""


@dataclass(frozen=True, slots=True)
class BayTurnRadii:
    rear_outer_m: float
    swept_inner_m: float
    front_outer_m: float
    front_inner_m: float
    turn_radius_m: float


@dataclass(frozen=True, slots=True)
class BayBoundary:
    free_mouth_width_m: float
    side_clearance_m: float
    usable_width_m: float
    u_m: float
    final_rear_axle_x_m: float
    aisle_width_m: float
    radii: BayTurnRadii

    def shifted_u(self, delta_m: float) -> BayBoundary:
        """Return a diagnostic variant without claiming it is feasible."""

        return replace(
            self,
            u_m=self.u_m + delta_m,
            aisle_width_m=self.radii.front_outer_m - self.u_m - delta_m,
        )


@dataclass(frozen=True, slots=True)
class SweepExtents:
    max_y_m: float
    bay_row_min_x_m: float
    bay_row_max_x_m: float


@dataclass(frozen=True, slots=True)
class ContainmentBound:
    aisle_width_m: float
    binding_heading_rad: float


def _finite(name: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def bay_turn_radii(vehicle: VehicleSpec, turn_radius_m: float | None = None) -> BayTurnRadii:
    """Return the four rear-axle-frame radii used by the bay derivation."""

    if type(vehicle) is not VehicleSpec:
        raise TypeError("vehicle must be exactly VehicleSpec")
    radius = (
        minimum_turn_radius_m(vehicle)
        if turn_radius_m is None
        else _finite("turn_radius_m", turn_radius_m)
    )
    if radius <= 0.0:
        raise ValueError("turn_radius_m must be positive")
    half_width = 0.5 * vehicle.width_m
    front = vehicle_front_extent_m(vehicle)
    return BayTurnRadii(
        rear_outer_m=math.hypot(radius + half_width, vehicle.rear_overhang_m),
        swept_inner_m=radius - half_width,
        front_outer_m=math.hypot(radius + half_width, front),
        front_inner_m=math.hypot(radius - half_width, front),
        turn_radius_m=radius,
    )


def _footprint_width_at_u(radii: BayTurnRadii, u_m: float) -> float:
    right = -math.sqrt(max(0.0, radii.swept_inner_m**2 - max(u_m, 0.0) ** 2))
    left = -math.sqrt(max(0.0, radii.rear_outer_m**2 - min(u_m, 0.0) ** 2))
    return right - left


def single_cut_boundary(
    vehicle: VehicleSpec,
    free_mouth_width_m: float,
    side_clearance_m: float,
    turn_radius_m: float | None = None,
) -> BayBoundary:
    """Solve the exact constant-radius, single-cut reverse-bay boundary."""

    width = _finite("free_mouth_width_m", free_mouth_width_m)
    clearance = _finite("side_clearance_m", side_clearance_m)
    if width <= 0.0:
        raise ValueError("free_mouth_width_m must be positive")
    if clearance < 0.0:
        raise ValueError("side_clearance_m must be nonnegative")
    radii = bay_turn_radii(vehicle, turn_radius_m)
    if radii.swept_inner_m <= 0.0:
        raise InfeasibleBayGeometry("turn radius must exceed half the vehicle width")

    usable_width = width - 2.0 * clearance
    if usable_width < vehicle.width_m:
        raise InfeasibleBayGeometry(
            "free mouth minus two side clearances is narrower than the vehicle"
        )

    branch_threshold = radii.rear_outer_m - radii.swept_inner_m
    cap = radii.swept_inner_m - clearance
    if cap < -vehicle.rear_overhang_m:
        raise InfeasibleBayGeometry("side clearance leaves no admissible approach")

    if usable_width >= _footprint_width_at_u(radii, cap):
        u_m = cap
    elif usable_width >= branch_threshold:
        radicand = radii.swept_inner_m**2 - (radii.rear_outer_m - usable_width) ** 2
        u_m = math.sqrt(max(0.0, radicand))
    else:
        radicand = radii.rear_outer_m**2 - (radii.swept_inner_m + usable_width) ** 2
        if radicand < -1e-12:
            raise InfeasibleBayGeometry("requested bay geometry has no real lower-branch solution")
        u_m = -math.sqrt(max(0.0, radicand))
    u_m = min(u_m, cap)

    if usable_width >= branch_threshold:
        final_x = radii.rear_outer_m - radii.turn_radius_m - 0.5 * width + clearance
    else:
        final_x = 0.5 * width - clearance - 0.5 * vehicle.width_m

    return BayBoundary(
        free_mouth_width_m=width,
        side_clearance_m=clearance,
        usable_width_m=usable_width,
        u_m=u_m,
        final_rear_axle_x_m=final_x,
        aisle_width_m=radii.front_outer_m - u_m,
        radii=radii,
    )


def _clip_below_mouth(polygon: tuple[Point2, ...]) -> tuple[Point2, ...]:
    clipped: list[Point2] = []
    for start, end in zip(polygon, polygon[1:] + polygon[:1], strict=True):
        start_inside = start[1] <= 0.0
        end_inside = end[1] <= 0.0
        if start_inside:
            clipped.append(start)
        if start_inside != end_inside:
            fraction = -start[1] / (end[1] - start[1])
            clipped.append((start[0] + fraction * (end[0] - start[0]), 0.0))
    return tuple(clipped)


def explicit_reverse_arc_sweep(
    boundary: BayBoundary,
    vehicle: VehicleSpec,
    *,
    samples: int = 20_000,
) -> SweepExtents:
    """Sample exact OBBs along the prescribed reverse quarter-circle.

    Aisle height is measured from the complete sweep. Bay-row x extents are
    measured separately after clipping each OBB polygon to ``y <= 0``.
    """

    if type(boundary) is not BayBoundary:
        raise TypeError("boundary must be exactly BayBoundary")
    if type(vehicle) is not VehicleSpec:
        raise TypeError("vehicle must be exactly VehicleSpec")
    if isinstance(samples, bool) or not isinstance(samples, int):
        raise TypeError("samples must be an int")
    if samples < 20_000:
        raise ValueError("samples must be at least 20000")

    radius = boundary.radii.turn_radius_m
    center_x = boundary.final_rear_axle_x_m + radius
    max_y = -math.inf
    row_min_x = math.inf
    row_max_x = -math.inf
    for index in range(samples + 1):
        alpha = 0.5 * math.pi * index / samples
        pose = RearAxleWorldPose(
            x_m=center_x - radius * math.sin(alpha),
            y_m=-boundary.u_m + radius * math.cos(alpha),
            heading_rad=alpha,
        )
        corners = obb_corners(vehicle_obb(pose, vehicle))
        max_y = max(max_y, *(point[1] for point in corners))
        clipped = _clip_below_mouth(corners)
        if clipped:
            row_min_x = min(row_min_x, *(point[0] for point in clipped))
            row_max_x = max(row_max_x, *(point[0] for point in clipped))

    if not math.isfinite(row_min_x) or not math.isfinite(row_max_x):
        raise RuntimeError("reverse arc never intersects the bay row")
    return SweepExtents(max_y, row_min_x, row_max_x)


def _minimum_y_outside(polygon: tuple[Point2, ...], boundary_x: float, *, left: bool) -> float:
    values: list[float] = []
    for start, end in zip(polygon, polygon[1:] + polygon[:1], strict=True):
        start_out = start[0] < boundary_x if left else start[0] > boundary_x
        end_out = end[0] < boundary_x if left else end[0] > boundary_x
        if start_out:
            values.append(start[1])
        if start_out != end_out:
            fraction = (boundary_x - start[0]) / (end[0] - start[0])
            values.append(start[1] + fraction * (end[1] - start[1]))
    return min(values, default=math.inf)


def required_aisle_for_heading(
    vehicle: VehicleSpec,
    bay_width_m: float,
    heading_rad: float,
) -> float:
    """Minimise aisle height for a fixed heading in the bay-mouth L-shape."""

    if type(vehicle) is not VehicleSpec:
        raise TypeError("vehicle must be exactly VehicleSpec")
    width = _finite("bay_width_m", bay_width_m)
    heading = _finite("heading_rad", heading_rad)
    if width <= 0.0:
        raise ValueError("bay_width_m must be positive")
    if not 0.0 <= heading <= 0.5 * math.pi:
        raise ValueError("heading_rad must be within [0, pi/2]")

    cosine = math.cos(heading)
    sine = math.sin(heading)
    front = vehicle_front_extent_m(vehicle)
    half_width = 0.5 * vehicle.width_m
    local = (
        (-vehicle.rear_overhang_m, -half_width),
        (front, -half_width),
        (front, half_width),
        (-vehicle.rear_overhang_m, half_width),
    )
    polygon = tuple((cosine * x - sine * y, sine * x + cosine * y) for x, y in local)
    minimum_x = min(point[0] for point in polygon)
    maximum_x = max(point[0] for point in polygon)
    if maximum_x - minimum_x <= width + 1e-12:
        return 0.0

    def required_at(horizontal_shift: float) -> float:
        shifted = tuple((x + horizontal_shift, y) for x, y in polygon)
        outside_minimum = min(
            _minimum_y_outside(shifted, -0.5 * width, left=True),
            _minimum_y_outside(shifted, 0.5 * width, left=False),
        )
        if outside_minimum == math.inf:
            return 0.0
        return max(point[1] for point in polygon) - outside_minimum

    lower = -2.0 * (vehicle.length_m + width)
    upper = -lower
    for _ in range(80):
        midpoint = 0.5 * (lower + upper)
        shifted = tuple((x + midpoint, y) for x, y in polygon)
        left_minimum = _minimum_y_outside(shifted, -0.5 * width, left=True)
        right_minimum = _minimum_y_outside(shifted, 0.5 * width, left=False)
        if left_minimum < right_minimum:
            lower = midpoint
        else:
            upper = midpoint

    balanced = required_at(0.5 * (lower + upper))
    left_flush = required_at(-0.5 * width - minimum_x)
    right_flush = required_at(0.5 * width - maximum_x)
    return min(balanced, left_flush, right_flush)


def static_containment_bound(
    vehicle: VehicleSpec,
    bay_width_m: float,
    bay_depth_m: float,
    end_clearance_m: float,
    *,
    heading_samples: int = 2_048,
) -> ContainmentBound:
    """Maximise the fixed-heading L-shape containment requirement."""

    depth = _finite("bay_depth_m", bay_depth_m)
    clearance = _finite("end_clearance_m", end_clearance_m)
    if depth <= 0.0 or clearance < 0.0:
        raise ValueError("bay depth must be positive and end clearance nonnegative")
    if depth + 1e-12 < vehicle.length_m + clearance:
        raise InfeasibleBayGeometry("bay depth cannot contain the parked vehicle")
    if isinstance(heading_samples, bool) or not isinstance(heading_samples, int):
        raise TypeError("heading_samples must be an int")
    if heading_samples < 256:
        raise ValueError("heading_samples must be at least 256")

    step = 0.5 * math.pi / heading_samples
    coarse = max(
        (
            required_aisle_for_heading(vehicle, bay_width_m, index * step),
            index * step,
        )
        for index in range(heading_samples + 1)
    )
    lower = max(0.0, coarse[1] - step)
    upper = min(0.5 * math.pi, coarse[1] + step)
    golden = 0.5 * (math.sqrt(5.0) - 1.0)
    for _ in range(64):
        left = upper - golden * (upper - lower)
        right = lower + golden * (upper - lower)
        if required_aisle_for_heading(vehicle, bay_width_m, left) > required_aisle_for_heading(
            vehicle, bay_width_m, right
        ):
            upper = right
        else:
            lower = left
    heading = 0.5 * (lower + upper)
    return ContainmentBound(
        aisle_width_m=required_aisle_for_heading(vehicle, bay_width_m, heading),
        binding_heading_rad=heading,
    )
