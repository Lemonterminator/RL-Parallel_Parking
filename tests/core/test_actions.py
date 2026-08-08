import math

import pytest

from parking_rl.core.actions import (
    ZERO_NORMALIZED_ACTION,
    NormalizedAction,
    PhysicalControl,
)


@pytest.mark.parametrize("value", [-1.0, 0.0, 1.0])
def test_normalized_action_accepts_closed_boundaries(value: float) -> None:
    action = NormalizedAction(longitudinal=value, steering_rate=value)

    assert action.longitudinal == value
    assert action.steering_rate == value


@pytest.mark.parametrize("value", [-1.000001, 1.000001])
@pytest.mark.parametrize("field", ["longitudinal", "steering_rate"])
def test_normalized_action_rejects_values_outside_bounds(field: str, value: float) -> None:
    values = {"longitudinal": 0.0, "steering_rate": 0.0, field: value}

    with pytest.raises(ValueError, match=r"\[-1, 1\]"):
        NormalizedAction(**values)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
@pytest.mark.parametrize("field", ["longitudinal", "steering_rate"])
def test_normalized_action_rejects_non_finite_values(field: str, value: float) -> None:
    values = {"longitudinal": 0.0, "steering_rate": 0.0, field: value}

    with pytest.raises(ValueError, match="finite"):
        NormalizedAction(**values)


@pytest.mark.parametrize("field", ["longitudinal", "steering_rate"])
def test_normalized_action_rejects_bool(field: str) -> None:
    values = {"longitudinal": 0.0, "steering_rate": 0.0, field: True}

    with pytest.raises(TypeError, match="real number"):
        NormalizedAction(**values)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
@pytest.mark.parametrize("field", ["acceleration_mps2", "steering_rate_radps"])
def test_physical_control_rejects_non_finite_values(field: str, value: float) -> None:
    values = {"acceleration_mps2": 0.0, "steering_rate_radps": 0.0, field: value}

    with pytest.raises(ValueError, match="finite"):
        PhysicalControl(**values)


def test_physical_control_is_not_artificially_bounded() -> None:
    control = PhysicalControl(acceleration_mps2=12.0, steering_rate_radps=-8.0)

    assert control.acceleration_mps2 == 12.0
    assert control.steering_rate_radps == -8.0
    assert NormalizedAction(0.0, 0.0) == ZERO_NORMALIZED_ACTION


def test_physical_control_rejects_bool() -> None:
    with pytest.raises(TypeError, match="real number"):
        PhysicalControl(acceleration_mps2=False, steering_rate_radps=0.0)
