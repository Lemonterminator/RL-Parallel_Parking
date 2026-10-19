import math

import pytest

from parking_rl.reward.heading import (
    heading_half_angle_cost,
    heading_half_angle_gradient_magnitude,
)


def test_half_angle_cost_has_no_pi_plateau() -> None:
    assert heading_half_angle_cost(0.0) == 0.0
    assert heading_half_angle_cost(math.pi) == pytest.approx(1.0, abs=1e-15)
    assert heading_half_angle_gradient_magnitude(math.pi) == pytest.approx(0.5, abs=1e-15)
    assert heading_half_angle_gradient_magnitude(math.pi - 1e-6) > 0.49


@pytest.mark.parametrize("error_rad", [0.2, 0.7, 1.5, 2.8])
def test_half_angle_gradient_matches_centered_finite_difference(error_rad: float) -> None:
    step = 1e-7
    numeric = (
        heading_half_angle_cost(error_rad + step) - heading_half_angle_cost(error_rad - step)
    ) / (2.0 * step)

    assert heading_half_angle_gradient_magnitude(error_rad) == pytest.approx(abs(numeric), abs=2e-9)


def test_literal_exit_0_12_threshold_is_contradicted_near_zero() -> None:
    """A smooth minimum cannot have gradient magnitude > 0.1 for every error > 0."""

    gradient = heading_half_angle_gradient_magnitude(1e-6)

    assert 0.0 < gradient < 0.1
