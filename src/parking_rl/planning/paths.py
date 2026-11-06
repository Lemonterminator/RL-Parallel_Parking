"""Piecewise-constant-curvature paths shared by the Reeds-Shepp and Dubins planners.

A path is a sequence of signed segments driven by the rear-axle reference point (I1). Each
segment has a kind (left arc, right arc, straight) and a signed metric length: positive is
forward gear, negative is reverse. Arcs always use the planner's turning radius ``rho``.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from itertools import pairwise
from numbers import Real

from parking_rl.core.frames import wrap_angle


def _require_finite(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number, not {type(value).__name__}")
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")


def _require_positive(name: str, value: object) -> None:
    _require_finite(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be positive")


class SegmentKind(StrEnum):
    LEFT = "L"
    RIGHT = "R"
    STRAIGHT = "S"

    @property
    def curvature_sign(self) -> int:
        return {SegmentKind.LEFT: 1, SegmentKind.RIGHT: -1, SegmentKind.STRAIGHT: 0}[self]


class Gear(StrEnum):
    FORWARD = "+"
    REVERSE = "-"


@dataclass(frozen=True, slots=True)
class Pose2:
    """Planar rear-axle pose used inside the planners (heading is not wrapped on input)."""

    x_m: float
    y_m: float
    heading_rad: float

    def __post_init__(self) -> None:
        _require_finite("x_m", self.x_m)
        _require_finite("y_m", self.y_m)
        _require_finite("heading_rad", self.heading_rad)


@dataclass(frozen=True, slots=True)
class Segment:
    """One constant-curvature piece; ``length_m`` is signed (negative is reverse gear)."""

    kind: SegmentKind
    length_m: float

    def __post_init__(self) -> None:
        if type(self.kind) is not SegmentKind:
            raise TypeError("kind must be exactly SegmentKind")
        _require_finite("length_m", self.length_m)

    @property
    def gear(self) -> Gear:
        return Gear.REVERSE if self.length_m < 0 else Gear.FORWARD


def _advance(pose: Pose2, kind: SegmentKind, signed_length_m: float, rho_m: float) -> Pose2:
    """Exact closed-form end pose of one segment."""

    x, y, theta = pose.x_m, pose.y_m, pose.heading_rad
    if kind is SegmentKind.STRAIGHT:
        return Pose2(
            x + signed_length_m * math.cos(theta),
            y + signed_length_m * math.sin(theta),
            theta,
        )
    sign = kind.curvature_sign
    delta = sign * signed_length_m / rho_m
    return Pose2(
        x + sign * rho_m * (math.sin(theta + delta) - math.sin(theta)),
        y - sign * rho_m * (math.cos(theta + delta) - math.cos(theta)),
        theta + delta,
    )


def path_end_pose(start: Pose2, segments: Sequence[Segment], rho_m: float) -> Pose2:
    """Return the exact end pose of ``segments`` driven from ``start``."""

    _require_positive("rho_m", rho_m)
    pose = start
    for segment in segments:
        pose = _advance(pose, segment.kind, segment.length_m, rho_m)
    return Pose2(pose.x_m, pose.y_m, wrap_angle(pose.heading_rad))


def sample_path(
    start: Pose2, segments: Sequence[Segment], rho_m: float, step_m: float
) -> tuple[Pose2, ...]:
    """Sample poses along the path with arc-length spacing at most ``step_m``.

    Every segment boundary (including cusps) is emitted exactly, so a collision checker that
    places the footprint at each sample never skips a cusp pose.
    """

    _require_positive("rho_m", rho_m)
    _require_positive("step_m", step_m)
    poses = [Pose2(start.x_m, start.y_m, wrap_angle(start.heading_rad))]
    pose = start
    for segment in segments:
        magnitude = abs(segment.length_m)
        if magnitude == 0.0:
            continue
        count = max(1, math.ceil(magnitude / step_m))
        direction = math.copysign(1.0, segment.length_m)
        for index in range(1, count + 1):
            partial = _advance(pose, segment.kind, direction * magnitude * index / count, rho_m)
            poses.append(Pose2(partial.x_m, partial.y_m, wrap_angle(partial.heading_rad)))
        pose = _advance(pose, segment.kind, segment.length_m, rho_m)
    return tuple(poses)


def integrate_segments_numerically(
    start: Pose2, segments: Sequence[Segment], rho_m: float, step_m: float = 0.05
) -> Pose2:
    """Integrate the control sequence with RK4 on the kinematic ODE.

    This deliberately shares no code with :func:`_advance`: it treats each segment as a control
    ``(gear, curvature)`` held for ``|length|`` of arc length and integrates
    ``x' = g cos θ, y' = g sin θ, θ' = g κ`` numerically.
    """

    _require_positive("rho_m", rho_m)
    _require_positive("step_m", step_m)
    x, y, theta = start.x_m, start.y_m, start.heading_rad
    for segment in segments:
        magnitude = abs(segment.length_m)
        if magnitude == 0.0:
            continue
        gear = 1.0 if segment.length_m > 0 else -1.0
        curvature = segment.kind.curvature_sign / rho_m
        count = max(1, math.ceil(magnitude / step_m))
        h = magnitude / count
        for _ in range(count):
            k1 = theta
            k2 = theta + 0.5 * h * gear * curvature
            k4 = theta + h * gear * curvature
            # θ is linear in s within a segment, so the RK4 stages for θ are exact and the
            # position stages only need θ at the start, midpoint, and end of the step.
            x += h * gear * (math.cos(k1) + 4.0 * math.cos(k2) + math.cos(k4)) / 6.0
            y += h * gear * (math.sin(k1) + 4.0 * math.sin(k2) + math.sin(k4)) / 6.0
            theta = k4
    return Pose2(x, y, wrap_angle(theta))


def path_word(segments: Sequence[Segment], zero_tol_m: float = 1e-10) -> str:
    """Render a path in gear notation, e.g. ``L+R-L+``; zero-length pieces render as ``0``."""

    parts = []
    for segment in segments:
        gear = "0" if abs(segment.length_m) <= zero_tol_m else segment.gear.value
        parts.append(f"{segment.kind.value}{gear}")
    return "".join(parts)


def path_cusps(segments: Sequence[Segment], zero_tol_m: float = 1e-10) -> int:
    """Count gear reversals between consecutive non-degenerate segments."""

    gears = [segment.gear for segment in segments if abs(segment.length_m) > zero_tol_m]
    return sum(1 for first, second in pairwise(gears) if first is not second)
