from __future__ import annotations

import math
import random

import pytest

from parking_rl.core.frames import ObjectCentroidWorldPose, RearAxleWorldPose
from parking_rl.core.state import ObjectKind, ObjectRole, ObjectState, VehicleSpec
from parking_rl.physics.geometry import (
    OBB,
    minimum_turn_radius_m,
    obb_corners,
    obb_signed_distance,
    object_obb,
    sat_face_normal_gap,
    sat_overlap,
    sat_penetration_depth,
    vehicle_farthest_corner_m,
    vehicle_front_extent_m,
    vehicle_obb,
)
from parking_rl.reward_geometry import body_circle_cover


def vehicle() -> VehicleSpec:
    return VehicleSpec(
        wheelbase_m=2.7,
        length_m=4.7,
        width_m=1.85,
        front_overhang_m=0.9,
        rear_overhang_m=1.1,
        max_steering_angle_rad=0.6,
        max_steering_rate_radps=0.6,
        max_speed_mps=1.5,
        max_acceleration_mps2=1.5,
    )


def test_obb_rejects_invalid_geometry() -> None:
    with pytest.raises(TypeError, match="real number"):
        OBB(True, 0.0, 0.0, 1.0, 1.0)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="finite"):
        OBB(0.0, math.inf, 0.0, 1.0, 1.0)
    with pytest.raises(ValueError, match="positive"):
        OBB(0.0, 0.0, 0.0, 0.0, 1.0)
    with pytest.raises(ValueError, match=r"\[-pi, pi\)"):
        OBB(0.0, 0.0, math.pi, 1.0, 1.0)


def test_axis_aligned_corners_have_stable_counter_clockwise_order() -> None:
    box = OBB(2.0, -1.0, 0.0, 4.0, 2.0)
    assert obb_corners(box) == (
        (0.0, -2.0),
        (4.0, -2.0),
        (4.0, 0.0),
        (0.0, 0.0),
    )


def test_rotated_corners_match_a_direct_hand_rotation() -> None:
    angle = 0.7
    cosine = math.cos(angle)
    sine = math.sin(angle)
    expected = tuple(
        (
            1.25 + cosine * local_x - sine * local_y,
            -0.5 + sine * local_x + cosine * local_y,
        )
        for local_x, local_y in ((-2.0, -1.0), (2.0, -1.0), (2.0, 1.0), (-2.0, 1.0))
    )
    actual = obb_corners(OBB(1.25, -0.5, angle, 4.0, 2.0))
    for actual_point, expected_point in zip(actual, expected, strict=True):
        assert actual_point == pytest.approx(expected_point, abs=1e-15)


def test_exit_0_10_vehicle_footprint_is_placed_from_rear_axle() -> None:
    spec = vehicle()
    corners = obb_corners(vehicle_obb(RearAxleWorldPose(0.0, 0.0, 0.0), spec))
    x_values = tuple(point[0] for point in corners)
    y_values = tuple(point[1] for point in corners)
    assert min(x_values) == pytest.approx(-1.1, abs=1e-12)
    assert max(x_values) == pytest.approx(3.6, abs=1e-12)
    assert min(y_values) == pytest.approx(-0.925, abs=1e-12)
    assert max(y_values) == pytest.approx(0.925, abs=1e-12)
    assert spec.length_m == spec.wheelbase_m + spec.front_overhang_m + spec.rear_overhang_m
    assert vehicle_front_extent_m(spec) == pytest.approx(3.6, abs=1e-15)
    assert vehicle_farthest_corner_m(spec) == pytest.approx(3.71694, abs=1e-4)


def test_exit_0_10_rotated_vehicle_matches_hand_computed_rear_axle_footprint() -> None:
    spec = vehicle()
    angle = 0.7
    cosine = math.cos(angle)
    sine = math.sin(angle)
    expected = tuple(
        (
            cosine * local_x - sine * local_y,
            sine * local_x + cosine * local_y,
        )
        for local_x, local_y in (
            (-1.1, -0.925),
            (3.6, -0.925),
            (3.6, 0.925),
            (-1.1, 0.925),
        )
    )
    actual = obb_corners(vehicle_obb(RearAxleWorldPose(0.0, 0.0, angle), spec))
    for actual_point, expected_point in zip(actual, expected, strict=True):
        assert actual_point == pytest.approx(expected_point, abs=1e-12)


def test_object_obb_preserves_centroid_semantics() -> None:
    obj = ObjectState(
        id="kerb",
        kind=ObjectKind.KERB,
        role=ObjectRole.KERB,
        pose=ObjectCentroidWorldPose(2.0, 3.0, 0.4),
        length_m=5.0,
        width_m=0.2,
    )
    assert object_obb(obj) == OBB(2.0, 3.0, 0.4, 5.0, 0.2)


def test_minimum_turn_radius_uses_rear_axle_bicycle_geometry() -> None:
    spec = vehicle()
    assert minimum_turn_radius_m(spec) == pytest.approx(
        spec.wheelbase_m / math.tan(spec.max_steering_angle_rad)
    )


def test_sat_distinguishes_separation_contact_and_overlap() -> None:
    base = OBB(0.0, 0.0, 0.0, 2.0, 2.0)
    separated = OBB(2.1, 0.0, 0.0, 2.0, 2.0)
    touching = OBB(2.0, 0.0, 0.0, 2.0, 2.0)
    overlapping = OBB(1.5, 0.0, 0.0, 2.0, 2.0)
    assert not sat_overlap(base, separated)
    assert sat_overlap(base, touching)
    assert sat_overlap(base, overlapping)
    assert sat_penetration_depth(base, separated) == 0.0
    assert sat_penetration_depth(base, touching) == 0.0
    assert sat_penetration_depth(base, overlapping) == pytest.approx(0.5)
    assert obb_signed_distance(base, separated) == pytest.approx(0.1)
    assert obb_signed_distance(base, touching) == 0.0
    assert obb_signed_distance(base, overlapping) == pytest.approx(-0.5)


def test_sat_penetration_accounts_for_axis_aligned_containment() -> None:
    outer = OBB(0.0, 0.0, 0.0, 10.0, 8.0)
    inner = OBB(1.0, 0.5, 0.0, 2.0, 1.0)
    assert sat_penetration_depth(outer, inner) == pytest.approx(4.0)
    assert sat_penetration_depth(inner, outer) == pytest.approx(4.0)
    assert obb_signed_distance(outer, inner) == pytest.approx(-4.0)


def test_sat_penetration_accounts_for_rotated_containment() -> None:
    angle = 0.7
    cosine = math.cos(angle)
    sine = math.sin(angle)
    center_x = cosine * 1.0 - sine * 0.5
    center_y = sine * 1.0 + cosine * 0.5
    outer = OBB(0.0, 0.0, angle, 10.0, 8.0)
    inner = OBB(center_x, center_y, angle, 2.0, 1.0)
    assert sat_penetration_depth(outer, inner) == pytest.approx(4.0)
    assert obb_signed_distance(outer, inner) == pytest.approx(-4.0)


def test_vertex_vertex_distance_is_not_the_sat_gap() -> None:
    first = OBB(-0.5, -0.5, 0.0, 1.0, 1.0)
    second = OBB(1.5, 1.5, 0.0, 1.0, 1.0)
    exact = obb_signed_distance(first, second)
    gap = sat_face_normal_gap(first, second)
    assert exact == pytest.approx(math.sqrt(2.0))
    assert gap == pytest.approx(1.0)
    assert exact - gap == pytest.approx(math.sqrt(2.0) - 1.0)


def test_twenty_degree_vertex_edge_regression_keeps_sat_gap_a_lower_bound() -> None:
    first = OBB(0.0, 0.0, 0.0, 2.0, 2.0)
    second = OBB(3.0, 3.0, math.radians(20.0), 2.0, 2.0)
    exact = obb_signed_distance(first, second)
    gap = sat_face_normal_gap(first, second)
    assert exact > 0.0
    assert gap > 0.0
    assert exact > gap


def test_signed_distance_is_symmetric_for_random_boxes() -> None:
    generator = random.Random(20260808)
    for _ in range(1_000):
        first = OBB(
            generator.uniform(-5.0, 5.0),
            generator.uniform(-5.0, 5.0),
            generator.uniform(-math.pi, math.pi),
            generator.uniform(0.1, 5.0),
            generator.uniform(0.1, 3.0),
        )
        second = OBB(
            generator.uniform(-5.0, 5.0),
            generator.uniform(-5.0, 5.0),
            generator.uniform(-math.pi, math.pi),
            generator.uniform(0.1, 5.0),
            generator.uniform(0.1, 3.0),
        )
        assert obb_signed_distance(first, second) == pytest.approx(
            obb_signed_distance(second, first), abs=1e-12
        )


def test_three_circle_cover_matches_the_analytic_radius() -> None:
    circles = body_circle_cover(vehicle())
    assert tuple(circle.center_x_m for circle in circles) == pytest.approx(
        (-1.1 + 4.7 / 6.0, -1.1 + 4.7 / 2.0, -1.1 + 5.0 * 4.7 / 6.0)
    )
    assert {circle.center_y_m for circle in circles} == {0.0}
    assert all(circle.radius_m == pytest.approx(1.2121, abs=1e-4) for circle in circles)


@pytest.mark.parametrize("count", [True, 0, -1, 1.5])
def test_circle_cover_rejects_invalid_counts(count: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        body_circle_cover(vehicle(), count=count)  # type: ignore[arg-type]
