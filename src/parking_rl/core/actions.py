"""Typed action contracts for the policy and the physical simulator."""

from __future__ import annotations

import math
from dataclasses import dataclass
from numbers import Real


def _require_finite(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number, not {type(value).__name__}")
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")


@dataclass(frozen=True, slots=True)
class NormalizedAction:
    """Policy action whose two channels are independently bounded by ``[-1, 1]``."""

    longitudinal: float
    steering_rate: float

    def __post_init__(self) -> None:
        for name in ("longitudinal", "steering_rate"):
            value = getattr(self, name)
            _require_finite(name, value)
            if not -1.0 <= value <= 1.0:
                raise ValueError(f"{name} must be within [-1, 1]")


@dataclass(frozen=True, slots=True)
class PhysicalControl:
    """Control in simulator units, deliberately distinct from a policy action."""

    acceleration_mps2: float
    steering_rate_radps: float

    def __post_init__(self) -> None:
        _require_finite("acceleration_mps2", self.acceleration_mps2)
        _require_finite("steering_rate_radps", self.steering_rate_radps)


ZERO_NORMALIZED_ACTION = NormalizedAction(longitudinal=0.0, steering_rate=0.0)
