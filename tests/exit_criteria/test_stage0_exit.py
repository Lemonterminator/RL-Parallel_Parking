from __future__ import annotations

import math
import random

import numpy as np
import pytest
import shapely

from parking_rl.core.actions import PhysicalControl
from parking_rl.core.frames import RearAxleWorldPose
from parking_rl.core.state import EgoState, VehicleSpec
from parking_rl.governance.clamp_stress import (
    StressSpec,
    dynamics_clamps_are_disabled,
    run_stress,
)
from parking_rl.physics.bay_geometry import (
    InfeasibleBayGeometry,
    explicit_reverse_arc_sweep,
    single_cut_boundary,
)
from parking_rl.physics.dynamics import integrate_substep
from parking_rl.physics.geometry import OBB, obb_corners, obb_signed_distance, sat_overlap
from parking_rl.reward.heading import (
    heading_half_angle_cost,
    heading_half_angle_gradient_magnitude,
)


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


def test_exit_0_11_random_clamp_smoke() -> None:
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


def test_exit_0_11_stress_harness_and_real_positive_control() -> None:
    """CI-scale run of the EXIT-0.11 harness; the 10^6 run is recorded as evidence."""

    spec = StressSpec(
        sequences=24,
        chunk_size=12,
        saturation_fraction=0.5,
        raw_control_fraction=0.25,
        ccd_audit_every=6,
    )
    vehicle = _vehicle()
    clamped, _ = run_stress(spec, vehicle)
    assert clamped.sequences == 24
    assert clamped.saturation_sequences > 0
    assert clamped.raw_control_sequences > 0
    assert sum(clamped.violations.values()) == 0
    assert clamped.guard_trips == 0
    assert max(clamped.max_ratio.values()) <= 1.0 + 1e-9
    assert clamped.ccd_max_bound_m >= clamped.ccd_max_exact_m
    assert run_stress(spec, vehicle)[0].digest == clamped.digest

    unclamped, _ = run_stress(spec, vehicle, disable_clamps=True)
    assert sum(unclamped.violations.values()) > 0
    assert not dynamics_clamps_are_disabled()


@pytest.mark.parametrize("success_tolerance_rad", [0.01, 0.05, 0.1])
def test_exit_0_12_no_stationary_point_outside_success_and_bounded_slope_near_pi(
    success_tolerance_rad: float,
) -> None:
    """EXIT-0.12 (v1.4): no stationary point outside the success tolerance on the
    positive branch, and a left slope of at least cos(eps/2)/2 on [pi - eps, pi]."""

    errors = np.linspace(success_tolerance_rad, math.pi, 200_001)
    gradients = np.array([heading_half_angle_gradient_magnitude(float(e)) for e in errors])
    assert np.all(gradients > 0.0)
    assert np.all(np.diff(gradients) > 0.0)

    eps = math.radians(10.0)
    near_pi = errors[errors >= math.pi - eps]
    lower_bound = 0.5 * math.cos(0.5 * eps)
    assert lower_bound == pytest.approx(0.498097349046, abs=1e-12)
    assert min(heading_half_angle_gradient_magnitude(float(e)) for e in near_pi) >= lower_bound

    step = 1e-7
    left_slope = (heading_half_angle_cost(math.pi) - heading_half_angle_cost(math.pi - step)) / step
    assert left_slope == pytest.approx(0.5, abs=1e-6)


def test_exit_0_12_positive_control_rejects_full_angle_plateau() -> None:
    """The v1.1 form (1 - cos e)/2 has a stationary point at pi and must fail."""

    def plateau_cost(error_rad: float) -> float:
        return 0.5 * (1.0 - math.cos(error_rad))

    eps = math.radians(10.0)
    lower_bound = 0.5 * math.cos(0.5 * eps)
    step = 1e-7
    slopes = [
        (plateau_cost(e) - plateau_cost(e - step)) / step
        for e in np.linspace(math.pi - eps, math.pi, 1_001)
    ]
    assert min(slopes) < lower_bound


_EXIT_0_13_MOUTHS = (None, 1.95, 2.10, 2.30, 2.50, 2.80, 3.15, 3.50, 4.00)
_EXIT_0_13_CLEARANCES = (0.0, 0.10, 0.25)


@pytest.mark.parametrize("mouth", _EXIT_0_13_MOUTHS)
@pytest.mark.parametrize("clearance", _EXIT_0_13_CLEARANCES)
def test_exit_0_13_closed_form_matches_explicit_swept_body(
    mouth: float | None, clearance: float
) -> None:
    """EXIT-0.13 (v1.4): max_y over the whole sweep; x extents of the y <= 0 clip."""

    vehicle = _vehicle()
    mouth_width = vehicle.width_m if mouth is None else mouth
    if mouth_width - 2.0 * clearance < vehicle.width_m:
        with pytest.raises(InfeasibleBayGeometry):
            single_cut_boundary(vehicle, mouth_width, clearance)
        return

    boundary = single_cut_boundary(vehicle, mouth_width, clearance)
    lower_branch = boundary.usable_width_m < (
        boundary.radii.rear_outer_m - boundary.radii.swept_inner_m
    )
    # The lower-branch left extent is set by a corner crossing y = 0, where the
    # sampled extent converges linearly in the heading step, so it is sampled finer.
    samples = 200_000 if lower_branch else 20_000
    sweep = explicit_reverse_arc_sweep(boundary, vehicle, samples=samples)
    allowed = 0.5 * mouth_width - clearance

    assert sweep.max_y_m == pytest.approx(boundary.radii.front_outer_m - boundary.u_m, abs=1e-8)
    assert sweep.bay_row_max_x_m == pytest.approx(allowed, abs=1e-5)
    assert sweep.bay_row_min_x_m == pytest.approx(-allowed, abs=1e-5)

    invalid = explicit_reverse_arc_sweep(boundary.shifted_u(0.02), vehicle, samples=20_000)
    incursion = max(invalid.bay_row_max_x_m - allowed, -allowed - invalid.bay_row_min_x_m)
    assert incursion > 0.0


def test_exit_0_13_branch_identities() -> None:
    vehicle = _vehicle()
    radii = single_cut_boundary(vehicle, 2.5, 0.0).radii

    assert single_cut_boundary(vehicle, vehicle.width_m, 0.0).u_m == pytest.approx(
        -vehicle.rear_overhang_m, abs=1e-9
    )
    seam = single_cut_boundary(vehicle, radii.rear_outer_m - radii.swept_inner_m, 0.0)
    assert seam.u_m == pytest.approx(0.0, abs=1e-9)
    wide = single_cut_boundary(vehicle, radii.rear_outer_m, 0.0)
    assert wide.u_m == pytest.approx(radii.swept_inner_m, abs=1e-9)
    for clearance in _EXIT_0_13_CLEARANCES:
        capped = single_cut_boundary(vehicle, 10.0, clearance)
        approach_flank_y = -capped.u_m + radii.turn_radius_m - 0.5 * vehicle.width_m
        assert approach_flank_y == pytest.approx(clearance, abs=1e-9)
