"""Closed-form and independently integrated ideal parking geometry."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TwoArcResult:
    """Net displacement of two equal, opposite, constant-curvature arcs."""

    lateral_m: float
    longitudinal_m: float
    path_length_m: float
    turn_angle_rad: float


def _validate_radius_and_shift(radius_m: float, lateral_shift_m: float) -> None:
    if isinstance(radius_m, bool) or not isinstance(radius_m, (int, float)):
        raise TypeError("radius_m must be a real number")
    if isinstance(lateral_shift_m, bool) or not isinstance(lateral_shift_m, (int, float)):
        raise TypeError("lateral_shift_m must be a real number")
    if not math.isfinite(radius_m) or radius_m <= 0.0:
        raise ValueError("radius_m must be finite and positive")
    if not math.isfinite(lateral_shift_m):
        raise ValueError("lateral_shift_m must be finite")
    if not 0.0 <= lateral_shift_m <= 2.0 * radius_m:
        raise ValueError("lateral_shift_m must be within [0, 2 * radius_m]")


def ideal_two_arc_longitudinal_m(radius_m: float, lateral_shift_m: float) -> float:
    """Return ``sqrt(4 R d - d^2)`` for the ideal two-arc S-curve."""

    _validate_radius_and_shift(radius_m, lateral_shift_m)
    return math.sqrt(4.0 * radius_m * lateral_shift_m - lateral_shift_m**2)


def integrate_ideal_two_arc(
    radius_m: float,
    lateral_shift_m: float,
    *,
    heading_steps: int = 10_000,
) -> TwoArcResult:
    """Numerically integrate the ideal arcs in heading space.

    This midpoint quadrature is intentionally independent of the simulator's
    dynamics integrator so it can act as a check on the closed form.
    """

    _validate_radius_and_shift(radius_m, lateral_shift_m)
    if isinstance(heading_steps, bool) or not isinstance(heading_steps, int):
        raise TypeError("heading_steps must be an int")
    if heading_steps < 1_000:
        raise ValueError("heading_steps must be at least 1000")

    turn_angle = math.acos(1.0 - lateral_shift_m / (2.0 * radius_m))
    if turn_angle == 0.0:
        return TwoArcResult(0.0, 0.0, 0.0, 0.0)

    heading_increment = turn_angle / heading_steps
    arc_increment_m = radius_m * heading_increment
    longitudinal_m = 0.0
    lateral_m = 0.0

    for index in range(heading_steps):
        heading = (index + 0.5) * heading_increment
        longitudinal_m += arc_increment_m * math.cos(heading)
        lateral_m += arc_increment_m * math.sin(heading)
    for index in range(heading_steps):
        heading = turn_angle - (index + 0.5) * heading_increment
        longitudinal_m += arc_increment_m * math.cos(heading)
        lateral_m += arc_increment_m * math.sin(heading)

    return TwoArcResult(
        lateral_m=lateral_m,
        longitudinal_m=longitudinal_m,
        path_length_m=2.0 * radius_m * turn_angle,
        turn_angle_rad=turn_angle,
    )
