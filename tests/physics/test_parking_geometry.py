import math

import pytest

from parking_rl.physics.parking_geometry import (
    ideal_two_arc_longitudinal_m,
    integrate_ideal_two_arc,
)


@pytest.mark.parametrize("radius_m", [1.0, 3.946579057110876, 8.0])
@pytest.mark.parametrize("fraction", [0.0, 0.05, 0.3, 0.75, 1.0])
def test_two_arc_closed_form_matches_independent_midpoint_integration(
    radius_m: float, fraction: float
) -> None:
    lateral_m = 2.0 * radius_m * fraction
    result = integrate_ideal_two_arc(radius_m, lateral_m, heading_steps=5_000)

    assert result.lateral_m == pytest.approx(lateral_m, abs=1e-6)
    assert result.longitudinal_m == pytest.approx(
        ideal_two_arc_longitudinal_m(radius_m, lateral_m), abs=1e-6
    )
    assert result.path_length_m == pytest.approx(2.0 * radius_m * result.turn_angle_rad, abs=1e-12)


def test_two_arc_reference_is_a_lateral_shift_not_a_slot_length() -> None:
    assert ideal_two_arc_longitudinal_m(3.9466, 2.35) == pytest.approx(5.62, abs=2e-3)


@pytest.mark.parametrize("lateral_m", [-0.01, 2.01])
def test_two_arc_rejects_shift_outside_geometric_domain(lateral_m: float) -> None:
    with pytest.raises(ValueError):
        ideal_two_arc_longitudinal_m(1.0, lateral_m)


def test_two_arc_requires_a_high_resolution_independent_integration() -> None:
    with pytest.raises(ValueError, match="at least 1000"):
        integrate_ideal_two_arc(3.0, 1.0, heading_steps=999)


def test_two_arc_turn_angle_at_maximal_shift() -> None:
    assert integrate_ideal_two_arc(2.0, 4.0).turn_angle_rad == pytest.approx(
        math.pi / 2.0, abs=1e-12
    )
