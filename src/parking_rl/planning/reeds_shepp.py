"""Reeds-Shepp shortest paths for a car that drives forwards and backwards.

The candidate generator follows the nine base formulas of Reeds & Shepp (1990, §8), expanded by
the time-flip, reflection and backwards symmetries, in the compact form of LaValle (2006,
§15.3.2). All formulas work in a frame normalised so that the turning radius is 1; lengths are
converted back to metres on output.

Notation: ``+`` is forward gear, ``-`` reverse, ``|`` a cusp. "48 words (Reeds & Shepp 1990,
Table 1), of which 46 suffice (Sussmann & Tang 1991)."
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from itertools import product

from parking_rl.planning.paths import (
    Pose2,
    Segment,
    SegmentKind,
    _require_positive,
    path_cusps,
    path_word,
)

_ZERO = 1e-10
_HALF_PI = 0.5 * math.pi

L, R, S = SegmentKind.LEFT, SegmentKind.RIGHT, SegmentKind.STRAIGHT


def _rs_word_table() -> frozenset[str]:
    words: list[str] = []
    # C|C|C, CC|C, C|CC
    words += ["L+R-L+", "L-R+L-", "R+L-R+", "R-L+R-"]
    words += ["L+R+L-", "L-R-L+", "R+L+R-", "R-L-R+"]
    words += ["L+R-L-", "L-R+L+", "R+L-R-", "R-L+R+"]
    # CSC
    words += ["L+S+L+", "L-S-L-", "R+S+R+", "R-S-R-", "L+S+R+", "L-S-R-", "R+S+L+", "R-S-L-"]
    # CCu|CuC
    words += ["L+R+L-R-", "L-R-L+R+", "R+L+R-L-", "R-L-R+L+"]
    # C|CuCu|C
    words += ["L+R-L-R+", "L-R+L+R-", "R+L-R-L+", "R-L+R+L-"]
    # C|C(pi/2)SC
    words += [
        "L+R-S-L-",
        "L-R+S+L+",
        "R+L-S-R-",
        "R-L+S+R+",
        "L+R-S-R-",
        "L-R+S+R+",
        "R+L-S-L-",
        "R-L+S+L+",
    ]
    # CSC(pi/2)|C
    words += [
        "L+S+R+L-",
        "L-S-R-L+",
        "R+S+L+R-",
        "R-S-L-R+",
        "R+S+R+L-",
        "R-S-R-L+",
        "L+S+L+R-",
        "L-S-L-R+",
    ]
    # C|C(pi/2)SC(pi/2)|C
    words += ["L+R-S-L-R+", "L-R+S+L+R-", "R+L-S-R-L+", "R-L+S+R+L-"]
    table = frozenset(words)
    if len(table) != 48 or len(words) != 48:
        raise AssertionError("Reeds-Shepp word table must contain exactly 48 distinct words")
    return table


RS_WORD_TABLE: frozenset[str] = _rs_word_table()


def word_in_rs_table(segments: Sequence[Segment], zero_tol_m: float = 1e-10) -> bool:
    """True if some gear assignment of the zero-length pieces yields a Table-1 word."""

    pieces = path_word(segments, zero_tol_m)
    tokens = [pieces[index : index + 2] for index in range(0, len(pieces), 2)]
    free = [index for index, token in enumerate(tokens) if token[1] == "0"]
    for gears in product("+-", repeat=len(free)):
        candidate = list(tokens)
        for index, gear in zip(free, gears, strict=True):
            candidate[index] = candidate[index][0] + gear
        if "".join(candidate) in RS_WORD_TABLE:
            return True
    return False


@dataclass(frozen=True, slots=True)
class ReedsSheppPath:
    """A Reeds-Shepp path in metres; ``segments`` carry signed lengths."""

    segments: tuple[Segment, ...]
    rho_m: float

    @property
    def length_m(self) -> float:
        return math.fsum(abs(segment.length_m) for segment in self.segments)

    @property
    def word(self) -> str:
        return path_word(self.segments)

    @property
    def cusps(self) -> int:
        return path_cusps(self.segments)


def _mod2pi(angle: float) -> float:
    """Wrap to ``[-pi, pi]`` (formula convention, not the simulator's half-open wrap)."""

    value = math.fmod(angle, math.tau)
    if value < -math.pi:
        value += math.tau
    elif value > math.pi:
        value -= math.tau
    return value


def _polar(x: float, y: float) -> tuple[float, float]:
    return math.hypot(x, y), math.atan2(y, x)


def _tau_omega(u: float, v: float, xi: float, eta: float, phi: float) -> tuple[float, float]:
    delta = _mod2pi(u - v)
    a = math.sin(u) - math.sin(delta)
    b = math.cos(u) - math.cos(delta) - 1.0
    t1 = math.atan2(eta * a - xi * b, xi * a + eta * b)
    t2 = 2.0 * (math.cos(delta) - math.cos(v) - math.cos(u)) + 3.0
    tau = _mod2pi(t1 + math.pi) if t2 < 0 else _mod2pi(t1)
    omega = _mod2pi(tau - u + v - phi)
    return tau, omega


# Each base formula returns the normalised piece lengths or None. Formula numbers refer to
# Reeds & Shepp (1990) §8.
Triple = tuple[float, float, float]


def _lp_sp_lp(x: float, y: float, phi: float) -> Triple | None:  # 8.1
    u, t = _polar(x - math.sin(phi), y - 1.0 + math.cos(phi))
    if t >= -_ZERO:
        v = _mod2pi(phi - t)
        if v >= -_ZERO:
            return t, u, v
    return None


def _lp_sp_rp(x: float, y: float, phi: float) -> Triple | None:  # 8.2
    u1, t1 = _polar(x + math.sin(phi), y - 1.0 - math.cos(phi))
    u1 *= u1
    if u1 >= 4.0:
        u = math.sqrt(u1 - 4.0)
        theta = math.atan2(2.0, u)
        t = _mod2pi(t1 + theta)
        v = _mod2pi(t - phi)
        if t >= -_ZERO and v >= -_ZERO:
            return t, u, v
    return None


def _lp_rm_l(x: float, y: float, phi: float) -> Triple | None:  # 8.3 / 8.4
    xi = x - math.sin(phi)
    eta = y - 1.0 + math.cos(phi)
    u1, theta = _polar(xi, eta)
    if u1 <= 4.0:
        u = -2.0 * math.asin(0.25 * u1)
        t = _mod2pi(theta + 0.5 * u + math.pi)
        v = _mod2pi(phi - t + u)
        if t >= -_ZERO and u <= _ZERO:
            return t, u, v
    return None


def _lp_rup_lum_rm(x: float, y: float, phi: float) -> Triple | None:  # 8.7
    xi = x + math.sin(phi)
    eta = y - 1.0 - math.cos(phi)
    rho = 0.25 * (2.0 + math.hypot(xi, eta))
    if rho <= 1.0:
        u = math.acos(rho)
        t, v = _tau_omega(u, -u, xi, eta, phi)
        if t >= -_ZERO and v <= _ZERO:
            return t, u, v
    return None


def _lp_rum_lum_rp(x: float, y: float, phi: float) -> Triple | None:  # 8.8
    xi = x + math.sin(phi)
    eta = y - 1.0 - math.cos(phi)
    rho = (20.0 - xi * xi - eta * eta) / 16.0
    if 0.0 <= rho <= 1.0:
        u = -math.acos(rho)
        if u >= -_HALF_PI:
            t, v = _tau_omega(u, u, xi, eta, phi)
            if t >= -_ZERO and v >= -_ZERO:
                return t, u, v
    return None


def _lp_rm_sm_lm(x: float, y: float, phi: float) -> Triple | None:  # 8.9
    xi = x - math.sin(phi)
    eta = y - 1.0 + math.cos(phi)
    rho, theta = _polar(xi, eta)
    if rho >= 2.0:
        r = math.sqrt(rho * rho - 4.0)
        u = 2.0 - r
        t = _mod2pi(theta + math.atan2(r, -2.0))
        v = _mod2pi(phi - _HALF_PI - t)
        if t >= -_ZERO and u <= _ZERO and v <= _ZERO:
            return t, u, v
    return None


def _lp_rm_sm_rm(x: float, y: float, phi: float) -> Triple | None:  # 8.10
    xi = x + math.sin(phi)
    eta = y - 1.0 - math.cos(phi)
    rho, theta = _polar(-eta, xi)
    if rho >= 2.0:
        t = theta
        u = 2.0 - rho
        v = _mod2pi(t + _HALF_PI - phi)
        if t >= -_ZERO and u <= _ZERO and v <= _ZERO:
            return t, u, v
    return None


def _lp_rm_slm_rp(x: float, y: float, phi: float) -> Triple | None:  # 8.11
    xi = x + math.sin(phi)
    eta = y - 1.0 - math.cos(phi)
    rho, _ = _polar(xi, eta)
    if rho >= 2.0:
        u = 4.0 - math.sqrt(rho * rho - 4.0)
        if u <= _ZERO:
            t = _mod2pi(math.atan2((4.0 - u) * xi - 2.0 * eta, -2.0 * xi + (u - 4.0) * eta))
            v = _mod2pi(t - phi)
            if t >= -_ZERO and v >= -_ZERO:
                return t, u, v
    return None


Pieces = tuple[tuple[SegmentKind, float], ...]


def _swap(kinds: Iterable[SegmentKind]) -> tuple[SegmentKind, ...]:
    """Reflection about the x axis exchanges left and right arcs."""

    mapping = {L: R, R: L, S: S}
    return tuple(mapping[kind] for kind in kinds)


def _variants(
    formula: Callable[[float, float, float], Triple | None],
    kinds: tuple[SegmentKind, ...],
    shape: Callable[[float, float, float], tuple[float, ...]],
    x: float,
    y: float,
    phi: float,
) -> list[Pieces]:
    """Apply the time-flip and reflection symmetries to one base formula."""

    out: list[Pieces] = []
    for time_flip, reflect in ((False, False), (True, False), (False, True), (True, True)):
        qx = -x if time_flip else x
        qy = -y if reflect else y
        qphi = -phi if time_flip != reflect else phi
        solved = formula(qx, qy, qphi)
        if solved is None:
            continue
        lengths = shape(*solved)
        if time_flip:
            lengths = tuple(-value for value in lengths)
        word_kinds = _swap(kinds) if reflect else kinds
        out.append(tuple(zip(word_kinds, lengths, strict=True)))
    return out


# (formula, word kinds, shape of the piece lengths, uses the backwards change of variables)
_FAMILIES: tuple[
    tuple[
        Callable[[float, float, float], Triple | None],
        tuple[SegmentKind, ...],
        Callable[[float, float, float], tuple[float, ...]],
        bool,
    ],
    ...,
] = (
    # CSC
    (_lp_sp_lp, (L, S, L), lambda t, u, v: (t, u, v), False),
    (_lp_sp_rp, (L, S, R), lambda t, u, v: (t, u, v), False),
    # CCC, forwards and backwards
    (_lp_rm_l, (L, R, L), lambda t, u, v: (t, u, v), False),
    (_lp_rm_l, (L, R, L), lambda t, u, v: (v, u, t), True),
    # CCCC
    (_lp_rup_lum_rm, (L, R, L, R), lambda t, u, v: (t, u, -u, v), False),
    (_lp_rum_lum_rp, (L, R, L, R), lambda t, u, v: (t, u, u, v), False),
    # CCSC, forwards and backwards
    (_lp_rm_sm_lm, (L, R, S, L), lambda t, u, v: (t, -_HALF_PI, u, v), False),
    (_lp_rm_sm_rm, (L, R, S, R), lambda t, u, v: (t, -_HALF_PI, u, v), False),
    (_lp_rm_sm_lm, (L, S, R, L), lambda t, u, v: (v, u, -_HALF_PI, t), True),
    (_lp_rm_sm_rm, (R, S, R, L), lambda t, u, v: (v, u, -_HALF_PI, t), True),
    # CCSCC
    (
        _lp_rm_slm_rp,
        (L, R, S, L, R),
        lambda t, u, v: (t, -_HALF_PI, u, -_HALF_PI, v),
        False,
    ),
)


def _normalised_candidates(x: float, y: float, phi: float) -> list[Pieces]:
    xb = x * math.cos(phi) + y * math.sin(phi)
    yb = x * math.sin(phi) - y * math.cos(phi)
    out: list[Pieces] = []
    for formula, kinds, shape, backwards in _FAMILIES:
        if backwards:
            out += _variants(formula, kinds, shape, xb, yb, phi)
        else:
            out += _variants(formula, kinds, shape, x, y, phi)
    return out


def _relative(start: Pose2, goal: Pose2, rho_m: float) -> tuple[float, float, float]:
    dx = goal.x_m - start.x_m
    dy = goal.y_m - start.y_m
    c = math.cos(start.heading_rad)
    s = math.sin(start.heading_rad)
    return (
        (c * dx + s * dy) / rho_m,
        (-s * dx + c * dy) / rho_m,
        _mod2pi(goal.heading_rad - start.heading_rad),
    )


def reeds_shepp_candidates(start: Pose2, goal: Pose2, rho_m: float) -> list[ReedsSheppPath]:
    """All candidate paths from the symmetry-expanded base formulas, shortest first."""

    _require_positive("rho_m", rho_m)
    x, y, phi = _relative(start, goal, rho_m)
    paths = [
        ReedsSheppPath(
            segments=tuple(Segment(kind, value * rho_m) for kind, value in pieces),
            rho_m=rho_m,
        )
        for pieces in _normalised_candidates(x, y, phi)
    ]
    paths.sort(key=lambda path: path.length_m)
    return paths


def reeds_shepp_path(start: Pose2, goal: Pose2, rho_m: float) -> ReedsSheppPath:
    """The shortest Reeds-Shepp path from ``start`` to ``goal`` at turning radius ``rho_m``."""

    candidates = reeds_shepp_candidates(start, goal, rho_m)
    if not candidates:
        raise AssertionError("Reeds-Shepp family returned no candidate; formulas are incomplete")
    return candidates[0]


def reeds_shepp_distance(start: Pose2, goal: Pose2, rho_m: float) -> float:
    return reeds_shepp_path(start, goal, rho_m).length_m
