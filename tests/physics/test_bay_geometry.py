import math

import pytest

from parking_rl.core.state import VehicleSpec
from parking_rl.physics.bay_geometry import (
    InfeasibleBayGeometry,
    bay_turn_radii,
    explicit_reverse_arc_sweep,
    single_cut_boundary,
    static_containment_bound,
)
from parking_rl.physics.geometry import minimum_turn_radius_m


def reference_vehicle() -> VehicleSpec:
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


def test_bay_turn_radii_reproduce_four_independent_identities() -> None:
    vehicle = reference_vehicle()
    radius = minimum_turn_radius_m(vehicle)
    radii = bay_turn_radii(vehicle)

    assert radii.turn_radius_m == radius
    assert radii.rear_outer_m == pytest.approx(4.9942, abs=5e-5)
    assert radii.swept_inner_m == pytest.approx(3.0216, abs=5e-5)
    assert radii.front_outer_m == pytest.approx(6.0574, abs=5e-5)
    assert radii.front_inner_m == pytest.approx(4.7000, abs=5e-5)


DESIGN_TABLE = {
    2.30: (4.690, 5.189, 6.906, None),
    2.40: (4.508, 4.908, 5.652, None),
    2.50: (4.352, 4.690, 5.189, 6.906),
    2.60: (4.214, 4.508, 4.908, 5.652),
    2.80: (3.980, 4.214, 4.508, 4.908),
    3.00: (3.787, 3.980, 4.214, 4.508),
}


@pytest.mark.parametrize(
    ("mouth_width_m", "clearance_m", "expected_aisle_m"),
    [
        (width, 0.1 * index, expected)
        for width, row in DESIGN_TABLE.items()
        for index, expected in enumerate(row)
    ],
)
def test_single_cut_design_grid_and_explicit_sweep(
    mouth_width_m: float,
    clearance_m: float,
    expected_aisle_m: float | None,
) -> None:
    vehicle = reference_vehicle()
    if expected_aisle_m is None:
        with pytest.raises(InfeasibleBayGeometry):
            single_cut_boundary(vehicle, mouth_width_m, clearance_m)
        return

    boundary = single_cut_boundary(vehicle, mouth_width_m, clearance_m)
    assert boundary.aisle_width_m == pytest.approx(expected_aisle_m, abs=5e-4)

    sweep = explicit_reverse_arc_sweep(boundary, vehicle, samples=20_000)
    allowed = 0.5 * mouth_width_m - clearance_m
    assert sweep.max_y_m <= boundary.aisle_width_m + 1e-8
    assert sweep.bay_row_min_x_m >= -allowed - 1e-7
    assert sweep.bay_row_max_x_m <= allowed + 1e-7


def test_sweep_positive_control_detects_incursion_when_u_is_too_large() -> None:
    vehicle = reference_vehicle()
    boundary = single_cut_boundary(vehicle, 2.5, 0.0)
    invalid = boundary.shifted_u(0.02)

    sweep = explicit_reverse_arc_sweep(invalid, vehicle, samples=20_000)

    assert sweep.bay_row_max_x_m > 1.25 + 0.01


@pytest.mark.parametrize(
    ("bay_width_m", "expected_aisle_m", "expected_heading_deg"),
    [
        (2.30, 3.7969, 57.2),
        (2.40, 3.6478, 55.1),
        (2.50, 3.5100, 53.0),
        (2.60, 3.3816, 51.2),
        (2.80, 3.1479, 47.7),
        (3.00, 2.9399, 44.5),
    ],
)
def test_static_containment_design_table_and_single_cut_bracket(
    bay_width_m: float,
    expected_aisle_m: float,
    expected_heading_deg: float,
) -> None:
    vehicle = reference_vehicle()
    containment = static_containment_bound(vehicle, bay_width_m, 5.3, 0.3)
    single_cut = single_cut_boundary(vehicle, bay_width_m, 0.0)

    assert containment.aisle_width_m == pytest.approx(expected_aisle_m, abs=1e-3)
    assert math.degrees(containment.binding_heading_rad) == pytest.approx(
        expected_heading_deg, abs=0.5
    )
    assert containment.aisle_width_m < single_cut.aisle_width_m


@pytest.mark.parametrize("bay_depth_m", [5.0, 5.3, 10.0])
def test_static_containment_is_invariant_once_depth_does_not_bind(
    bay_depth_m: float,
) -> None:
    result = static_containment_bound(reference_vehicle(), 2.5, bay_depth_m, 0.3)

    assert result.aisle_width_m == pytest.approx(3.510010816, abs=1e-8)
    assert math.degrees(result.binding_heading_rad) == pytest.approx(53.037, abs=1e-3)


def test_static_containment_rejects_bay_that_cannot_hold_parked_body() -> None:
    with pytest.raises(InfeasibleBayGeometry, match="depth"):
        static_containment_bound(reference_vehicle(), 2.5, 4.99, 0.3)
