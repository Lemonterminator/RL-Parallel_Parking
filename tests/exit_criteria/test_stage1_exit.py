from __future__ import annotations

import math
import random

from parking_rl.core.state import VehicleSpec
from parking_rl.physics.geometry import minimum_turn_radius_m
from parking_rl.planning import (
    Pose2,
    dubins_distance,
    dubins_path,
    integrate_segments_numerically,
    path_cusps,
    reeds_shepp_distance,
    reeds_shepp_path,
    word_in_rs_table,
)
from parking_rl.planning.dubins import dubins_candidates

TOL = 1e-9


def _rho() -> float:
    return minimum_turn_radius_m(VehicleSpec(2.7, 4.7, 1.85, 0.9, 1.1, 0.6, 0.6, 1.5, 1.5))


def _random_pose(rng: random.Random, half_width_m: float) -> Pose2:
    return Pose2(
        rng.uniform(-half_width_m, half_width_m),
        rng.uniform(-half_width_m, half_width_m),
        rng.uniform(-math.pi, math.pi),
    )


def _pairs(count: int, seed: int) -> list[tuple[Pose2, Pose2]]:
    """Stratified pairs: a third are close (≤ 2 m, the cusp-heavy regime), the rest wide."""

    rng = random.Random(seed)
    out = []
    for index in range(count):
        first = _random_pose(rng, 15.0)
        if index % 3 == 0:
            second = Pose2(
                first.x_m + rng.uniform(-2.0, 2.0),
                first.y_m + rng.uniform(-2.0, 2.0),
                rng.uniform(-math.pi, math.pi),
            )
        else:
            second = _random_pose(rng, 15.0)
        out.append((first, second))
    return out


def _transform(pose: Pose2, angle: float, tx: float, ty: float) -> Pose2:
    c, s = math.cos(angle), math.sin(angle)
    return Pose2(
        c * pose.x_m - s * pose.y_m + tx,
        s * pose.x_m + c * pose.y_m + ty,
        pose.heading_rad + angle,
    )


def _scale(pose: Pose2, factor: float) -> Pose2:
    return Pose2(pose.x_m * factor, pose.y_m * factor, pose.heading_rad)


def test_exit_1_1_reeds_shepp_metric_axioms_100k_pairs() -> None:
    rho = _rho()
    rng = random.Random(11)
    violations: dict[str, int] = {"symmetry": 0, "euclid": 0, "invariance": 0, "scaling": 0}
    for first, second in _pairs(100_000, seed=1):
        forward = reeds_shepp_distance(first, second, rho)
        if abs(forward - reeds_shepp_distance(second, first, rho)) > TOL:
            violations["symmetry"] += 1
        if forward < math.hypot(second.x_m - first.x_m, second.y_m - first.y_m) - TOL:
            violations["euclid"] += 1
        angle, tx, ty = rng.uniform(-math.pi, math.pi), rng.uniform(-50, 50), rng.uniform(-50, 50)
        moved = reeds_shepp_distance(
            _transform(first, angle, tx, ty), _transform(second, angle, tx, ty), rho
        )
        if abs(moved - forward) > TOL:
            violations["invariance"] += 1
        factor = rng.uniform(0.25, 4.0)
        scaled = reeds_shepp_distance(_scale(first, factor), _scale(second, factor), rho * factor)
        if abs(scaled - factor * forward) > TOL * max(1.0, factor):
            violations["scaling"] += 1
    assert violations == {"symmetry": 0, "euclid": 0, "invariance": 0, "scaling": 0}


def test_exit_1_1_reeds_shepp_identity_and_triangle_inequality_20k_triples() -> None:
    rho = _rho()
    rng = random.Random(12)
    identity_violations = 0
    triangle_violations = 0
    for _ in range(20_000):
        a, b, c = (_random_pose(rng, 10.0) for _ in range(3))
        if reeds_shepp_distance(a, a, rho) > TOL:
            identity_violations += 1
        ac = reeds_shepp_distance(a, c, rho)
        if ac > reeds_shepp_distance(a, b, rho) + reeds_shepp_distance(b, c, rho) + TOL:
            triangle_violations += 1
    assert identity_violations == 0
    assert triangle_violations == 0


def _flip(pose: Pose2) -> Pose2:
    return Pose2(pose.x_m, pose.y_m, pose.heading_rad + math.pi)


def test_exit_1_2_reeds_shepp_never_longer_than_dubins_and_dubins_asymmetry() -> None:
    rho = _rho()
    ordering_violations = 0
    reversal_violations = 0
    middle_arc_violations = 0
    max_asymmetry = 0.0
    for first, second in _pairs(100_000, seed=2):
        forward = dubins_path(first, second, rho)
        if reeds_shepp_distance(first, second, rho) > forward.length_m + TOL:
            ordering_violations += 1
        reversed_flipped = dubins_distance(_flip(second), _flip(first), rho)
        if abs(forward.length_m - reversed_flipped) > TOL:
            reversal_violations += 1
        max_asymmetry = max(
            max_asymmetry, abs(forward.length_m - dubins_distance(second, first, rho))
        )
        for candidate in dubins_candidates(first, second, rho):
            if candidate.word in {"LRL", "RLR"} and not (
                candidate.segments[1].length_m / rho > math.pi
            ):
                middle_arc_violations += 1
    assert ordering_violations == 0
    assert reversal_violations == 0
    assert middle_arc_violations == 0
    assert max_asymmetry > 0.1


def test_exit_1_3_reeds_shepp_control_sequence_reaches_goal_10k() -> None:
    rho = _rho()
    failures: list[str] = []
    for first, second in _pairs(10_000, seed=3):
        path = reeds_shepp_path(first, second, rho)
        end = integrate_segments_numerically(first, path.segments, rho)
        position_error = math.hypot(end.x_m - second.x_m, end.y_m - second.y_m)
        heading_error = abs(math.remainder(end.heading_rad - second.heading_rad, math.tau))
        if (
            position_error > 1e-4
            or heading_error > 1e-5
            or len(path.segments) > 5
            or path_cusps(path.segments) > 2
            or not word_in_rs_table(path.segments)
        ):
            failures.append(f"{first} -> {second}: {path.word} err={position_error:.2e}")
    assert failures == []
