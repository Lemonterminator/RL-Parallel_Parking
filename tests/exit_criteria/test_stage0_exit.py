from __future__ import annotations

import math
import random

import numpy as np
import pytest
import shapely

from parking_rl.core.actions import PhysicalControl
from parking_rl.core.frames import RearAxleWorldPose
from parking_rl.core.state import EgoState, VehicleSpec
from parking_rl.physics.dynamics import integrate_substep
from parking_rl.physics.geometry import OBB, obb_corners, obb_signed_distance, sat_overlap


def _vehicle() -> VehicleSpec:
    return VehicleSpec(2.7, 4.7, 1.85, 0.9, 1.1, 0.6, 0.6, 1.5, 1.5)


def _random_box_arrays(count: int, seed: int) -> tuple[np.ndarray, ...]:
    generator = np.random.default_rng(seed)
    return (
        generator.uniform(-8.0, 8.0, count),
        generator.uniform(-8.0, 8.0, count),
        generator.uniform(-math.pi, math.pi, count),
        generator.uniform(0.1, 5.0, count),
        generator.uniform(0.1, 3.0, count),
    )


def _boxes_and_polygons(values: tuple[np.ndarray, ...]) -> tuple[tuple[OBB, ...], np.ndarray]:
    boxes = tuple(
        OBB(float(x), float(y), float(angle), float(body_length), float(body_width))
        for x, y, angle, body_length, body_width in zip(*values, strict=True)
    )
    coordinates = np.empty((len(boxes), 5, 2), dtype=np.float64)
    for index, box in enumerate(boxes):
        corners = obb_corners(box)
        coordinates[index, :4] = corners
        coordinates[index, 4] = corners[0]
    return boxes, shapely.polygons(coordinates)


def _independent_penetration_depth(first: OBB, second: OBB) -> float:
    """Independent four-axis 1-D MTV reference used only by this EXIT test."""

    first_points = np.asarray(obb_corners(first))
    second_points = np.asarray(obb_corners(second))
    axes = (
        (math.cos(first.heading_rad), math.sin(first.heading_rad)),
        (-math.sin(first.heading_rad), math.cos(first.heading_rad)),
        (math.cos(second.heading_rad), math.sin(second.heading_rad)),
        (-math.sin(second.heading_rad), math.cos(second.heading_rad)),
    )
    depths: list[float] = []
    for axis in axes:
        first_projection = first_points @ axis
        second_projection = second_points @ axis
        if first_projection.max() < second_projection.min() or (
            second_projection.max() < first_projection.min()
        ):
            return 0.0
        depths.append(
            min(
                float(first_projection.max() - second_projection.min()),
                float(second_projection.max() - first_projection.min()),
            )
        )
    return min(depths)


def test_exit_0_1_sat_matches_shapely_100k() -> None:
    first_boxes, first_polygons = _boxes_and_polygons(_random_box_arrays(100_000, 1001))
    second_boxes, second_polygons = _boxes_and_polygons(_random_box_arrays(100_000, 1002))

    reference = shapely.intersects(first_polygons, second_polygons)
    actual = np.fromiter(
        (
            sat_overlap(first, second)
            for first, second in zip(first_boxes, second_boxes, strict=True)
        ),
        dtype=np.bool_,
        count=100_000,
    )

    assert np.count_nonzero(actual != reference) == 0


@pytest.mark.parametrize("steering_rad", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
def test_exit_0_2_constant_steering_radius_and_closure(steering_rad: float) -> None:
    vehicle = _vehicle()
    speed_mps = vehicle.max_speed_mps
    dt_sub_s = 0.02
    heading_step = speed_mps / vehicle.wheelbase_m * math.tan(steering_rad) * dt_sub_s
    step_count = round(math.tau / heading_step)
    initial = EgoState(RearAxleWorldPose(0.0, 0.0, 0.0), speed_mps, steering_rad)
    state = initial
    samples = [(state.pose.x_m, state.pose.y_m)]
    for _ in range(step_count):
        state = integrate_substep(state, PhysicalControl(0.0, 0.0), vehicle, dt_sub_s)
        samples.append((state.pose.x_m, state.pose.y_m))

    points = np.asarray(samples)
    design = np.column_stack((2.0 * points[:, 0], 2.0 * points[:, 1], np.ones(len(points))))
    target = np.square(points).sum(axis=1)
    center_x, center_y, constant = np.linalg.lstsq(design, target, rcond=None)[0]
    fitted_radius = math.sqrt(constant + center_x**2 + center_y**2)
    expected_radius = vehicle.wheelbase_m / math.tan(steering_rad)
    closure_error = math.hypot(state.pose.x_m, state.pose.y_m)

    assert abs(fitted_radius - expected_radius) < 1e-3
    assert closure_error < 1.5 * speed_mps * dt_sub_s


def test_exit_0_3_signed_distance_matches_independent_reference_10k() -> None:
    first_boxes, first_polygons = _boxes_and_polygons(_random_box_arrays(10_000, 3001))
    second_boxes, second_polygons = _boxes_and_polygons(_random_box_arrays(10_000, 3002))
    overlaps = shapely.intersects(first_polygons, second_polygons)
    separated_distances = shapely.distance(first_polygons, second_polygons)

    maximum_error = 0.0
    overlap_count = 0
    separated_count = 0
    for index, (first, second) in enumerate(zip(first_boxes, second_boxes, strict=True)):
        actual = obb_signed_distance(first, second)
        if overlaps[index]:
            overlap_count += 1
            reference = -_independent_penetration_depth(first, second)
        else:
            separated_count += 1
            reference = float(separated_distances[index])
        maximum_error = max(maximum_error, abs(actual - reference))

    assert overlap_count > 0
    assert separated_count > 0
    assert maximum_error <= 1e-6


def test_exit_0_11_random_clamp_smoke_and_positive_control() -> None:
    """CI-scale evidence only; it does not claim the 10^6-sequence EXIT threshold."""

    generator = random.Random(11)
    vehicle = _vehicle()
    dt_sub_s = 0.02
    for _ in range(64):
        state = EgoState(RearAxleWorldPose(0.0, 0.0, 0.0), 0.0, 0.0)
        for _ in range(400):
            control = PhysicalControl(
                generator.uniform(-3.0, 3.0),
                generator.uniform(-1.2, 1.2),
            )
            for _ in range(5):
                previous = state
                state = integrate_substep(state, control, vehicle, dt_sub_s)
                assert abs(state.speed_mps) <= vehicle.max_speed_mps + 1e-12
                assert abs(state.steering_rad) <= vehicle.max_steering_angle_rad + 1e-12
                assert abs(state.speed_mps - previous.speed_mps) <= (
                    vehicle.max_acceleration_mps2 * dt_sub_s + 1e-12
                )
                assert abs(state.steering_rad - previous.steering_rad) <= (
                    vehicle.max_steering_rate_radps * dt_sub_s + 1e-12
                )

    unclamped_steering = 400 * 5 * vehicle.max_steering_rate_radps * dt_sub_s
    assert unclamped_steering > vehicle.max_steering_angle_rad
