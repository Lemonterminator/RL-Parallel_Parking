from __future__ import annotations

import math
import random
from itertools import pairwise

import pytest

from parking_rl.planning import (
    RS_WORD_TABLE,
    Pose2,
    Segment,
    SegmentKind,
    path_end_pose,
    reeds_shepp_distance,
    reeds_shepp_path,
    sample_path,
    word_in_rs_table,
)
from parking_rl.planning import reeds_shepp as rs

RHO = 2.7 / math.tan(0.6)
ORIGIN = Pose2(0.0, 0.0, 0.0)


def test_word_table_has_48_words_with_at_most_two_cusps() -> None:
    assert len(RS_WORD_TABLE) == 48
    for word in RS_WORD_TABLE:
        gears = word[1::2]
        assert sum(a != b for a, b in pairwise(gears)) <= 2


@pytest.mark.parametrize(
    ("goal", "expected"),
    [
        (Pose2(5.0, 0.0, 0.0), 5.0),
        (Pose2(-5.0, 0.0, 0.0), 5.0),
        (Pose2(RHO, RHO, math.pi / 2), RHO * math.pi / 2),
        (Pose2(-RHO, RHO, -math.pi / 2), RHO * math.pi / 2),
    ],
)
def test_elementary_paths_have_textbook_lengths(goal: Pose2, expected: float) -> None:
    assert reeds_shepp_distance(ORIGIN, goal, RHO) == pytest.approx(expected, abs=1e-12)


def test_reverse_straight_path_is_in_reverse_gear() -> None:
    path = reeds_shepp_path(ORIGIN, Pose2(-5.0, 0.0, 0.0), RHO)
    moving = [segment for segment in path.segments if abs(segment.length_m) > 1e-12]
    assert [segment.kind for segment in moving] == [SegmentKind.STRAIGHT]
    assert moving[0].length_m == pytest.approx(-5.0)


def test_sampling_respects_spacing_and_hits_every_boundary() -> None:
    segments = (
        Segment(SegmentKind.LEFT, 2.0),
        Segment(SegmentKind.STRAIGHT, -1.0),
        Segment(SegmentKind.RIGHT, 0.5),
    )
    poses = sample_path(ORIGIN, segments, RHO, 0.026)
    steps = [math.hypot(b.x_m - a.x_m, b.y_m - a.y_m) for a, b in pairwise(poses)]
    assert max(steps) <= 0.026
    end = path_end_pose(ORIGIN, segments, RHO)
    assert (poses[-1].x_m, poses[-1].y_m) == pytest.approx((end.x_m, end.y_m), abs=1e-12)
    cusp = path_end_pose(ORIGIN, segments[:1], RHO)
    assert any(math.hypot(p.x_m - cusp.x_m, p.y_m - cusp.y_m) < 1e-12 for p in poses), (
        "the cusp pose must be sampled exactly"
    )


def test_zero_length_pieces_may_take_either_gear() -> None:
    segments = (
        Segment(SegmentKind.LEFT, 1.0),
        Segment(SegmentKind.STRAIGHT, 0.0),
        Segment(SegmentKind.LEFT, -1.0),
    )
    # L+S?L- is in the table only as part of a longer word; as a 3-word it is not.
    assert not word_in_rs_table(segments)
    assert word_in_rs_table((Segment(SegmentKind.LEFT, 1.0), *segments[1:2], segments[0]))


def test_metric_tests_are_sensitive_to_a_missing_family(monkeypatch: pytest.MonkeyPatch) -> None:
    """Positive control: without the backwards change of variables, symmetry must break."""

    monkeypatch.setattr(rs, "_FAMILIES", tuple(family for family in rs._FAMILIES if not family[3]))
    rng = random.Random(5)
    asymmetric = 0
    for _ in range(3000):
        a = Pose2(rng.uniform(-3, 3), rng.uniform(-3, 3), rng.uniform(-math.pi, math.pi))
        b = Pose2(rng.uniform(-3, 3), rng.uniform(-3, 3), rng.uniform(-math.pi, math.pi))
        if abs(reeds_shepp_distance(a, b, RHO) - reeds_shepp_distance(b, a, RHO)) > 1e-9:
            asymmetric += 1
    assert asymmetric > 0
