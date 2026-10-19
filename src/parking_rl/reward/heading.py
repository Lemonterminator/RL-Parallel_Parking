"""Directed heading potential for parking tasks."""

from __future__ import annotations

import math
from numbers import Real

from parking_rl.core.frames import wrap_angle


def _wrapped_magnitude(error_rad: float) -> float:
    if isinstance(error_rad, bool) or not isinstance(error_rad, Real):
        raise TypeError("error_rad must be a real number")
    if not math.isfinite(error_rad):
        raise ValueError("error_rad must be finite")
    return abs(wrap_angle(float(error_rad)))


def heading_half_angle_cost(error_rad: float) -> float:
    """Return ``1 - cos(|wrap(error)| / 2)``.

    The half-angle form removes the stationary point at pi. Like every smooth
    minimum, however, its gradient still tends to zero near zero.
    """

    return 1.0 - math.cos(0.5 * _wrapped_magnitude(error_rad))


def heading_half_angle_gradient_magnitude(error_rad: float) -> float:
    """Return the analytic magnitude ``0.5 sin(|wrap(error)| / 2)``.

    Consequently the literal EXIT-0.12 threshold ``> 0.1`` for *all* positive
    errors is mathematically impossible for this smooth potential.
    """

    return 0.5 * math.sin(0.5 * _wrapped_magnitude(error_rad))
