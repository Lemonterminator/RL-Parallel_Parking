"""Dubins (forward-only) shortest paths: six words, at most three pieces.

Used as the sanity anchor ``d_Dubins >= d_RS`` (Dubins 1957). For the CCC words (LRL, RLR) the
middle arc of any returned solution is strictly greater than pi.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from parking_rl.planning.paths import Pose2, Segment, SegmentKind, _require_positive, path_word

L, R, S = SegmentKind.LEFT, SegmentKind.RIGHT, SegmentKind.STRAIGHT


def _mod2pi_positive(angle: float) -> float:
    value = math.fmod(angle, math.tau)
    return value + math.tau if value < 0 else value


@dataclass(frozen=True, slots=True)
class DubinsPath:
    segments: tuple[Segment, ...]
    rho_m: float

    @property
    def length_m(self) -> float:
        return math.fsum(segment.length_m for segment in self.segments)

    @property
    def word(self) -> str:
        return path_word(self.segments).replace("+", "")


def _solutions(alpha: float, beta: float, d: float) -> list[tuple[tuple[SegmentKind, ...], tuple]]:
    sa, ca = math.sin(alpha), math.cos(alpha)
    sb, cb = math.sin(beta), math.cos(beta)
    cab = math.cos(alpha - beta)
    out = []

    p2 = 2.0 + d * d - 2.0 * cab + 2.0 * d * (sa - sb)
    if p2 >= 0.0:
        tmp = math.atan2(cb - ca, d + sa - sb)
        out.append(
            (
                (L, S, L),
                (_mod2pi_positive(tmp - alpha), math.sqrt(p2), _mod2pi_positive(beta - tmp)),
            )
        )

    p2 = 2.0 + d * d - 2.0 * cab + 2.0 * d * (sb - sa)
    if p2 >= 0.0:
        tmp = math.atan2(ca - cb, d - sa + sb)
        out.append(
            (
                (R, S, R),
                (_mod2pi_positive(alpha - tmp), math.sqrt(p2), _mod2pi_positive(tmp - beta)),
            )
        )

    p2 = -2.0 + d * d + 2.0 * cab + 2.0 * d * (sa + sb)
    if p2 >= 0.0:
        p = math.sqrt(p2)
        tmp = math.atan2(-ca - cb, d + sa + sb) - math.atan2(-2.0, p)
        out.append(((L, S, R), (_mod2pi_positive(tmp - alpha), p, _mod2pi_positive(tmp - beta))))

    p2 = -2.0 + d * d + 2.0 * cab - 2.0 * d * (sa + sb)
    if p2 >= 0.0:
        p = math.sqrt(p2)
        tmp = math.atan2(ca + cb, d - sa - sb) - math.atan2(2.0, p)
        out.append(((R, S, L), (_mod2pi_positive(alpha - tmp), p, _mod2pi_positive(beta - tmp))))

    c = (6.0 - d * d + 2.0 * cab + 2.0 * d * (sa - sb)) / 8.0
    if abs(c) <= 1.0:
        p = _mod2pi_positive(math.tau - math.acos(c))
        t = _mod2pi_positive(alpha - math.atan2(ca - cb, d - sa + sb) + 0.5 * p)
        out.append(((R, L, R), (t, p, _mod2pi_positive(alpha - beta - t + p))))

    c = (6.0 - d * d + 2.0 * cab + 2.0 * d * (sb - sa)) / 8.0
    if abs(c) <= 1.0:
        p = _mod2pi_positive(math.tau - math.acos(c))
        t = _mod2pi_positive(-alpha - math.atan2(ca - cb, d + sa - sb) + 0.5 * p)
        out.append(((L, R, L), (t, p, _mod2pi_positive(beta - alpha - t + p))))
    return out


def dubins_candidates(start: Pose2, goal: Pose2, rho_m: float) -> list[DubinsPath]:
    _require_positive("rho_m", rho_m)
    dx = goal.x_m - start.x_m
    dy = goal.y_m - start.y_m
    d = math.hypot(dx, dy) / rho_m
    theta = math.atan2(dy, dx) if d > 0 else 0.0
    alpha = _mod2pi_positive(start.heading_rad - theta)
    beta = _mod2pi_positive(goal.heading_rad - theta)
    paths = [
        DubinsPath(
            segments=tuple(
                Segment(kind, value * rho_m) for kind, value in zip(kinds, values, strict=True)
            ),
            rho_m=rho_m,
        )
        for kinds, values in _solutions(alpha, beta, d)
    ]
    paths.sort(key=lambda path: path.length_m)
    return paths


def dubins_path(start: Pose2, goal: Pose2, rho_m: float) -> DubinsPath:
    candidates = dubins_candidates(start, goal, rho_m)
    if not candidates:
        raise AssertionError("Dubins family returned no candidate")
    return candidates[0]


def dubins_distance(start: Pose2, goal: Pose2, rho_m: float) -> float:
    return dubins_path(start, goal, rho_m).length_m
