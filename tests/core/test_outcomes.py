import pytest

from parking_rl.core.outcomes import (
    EpisodeEndReason,
    EpisodeRuntime,
    StepBoundary,
    resolve_end_reason,
)


@pytest.mark.parametrize(
    ("reason", "terminated", "truncated"),
    [
        (EpisodeEndReason.NONE, False, False),
        (EpisodeEndReason.COLLISION, True, False),
        (EpisodeEndReason.OUT_OF_BOUNDS, True, False),
        (EpisodeEndReason.SUCCESS, True, False),
        (EpisodeEndReason.TIME_LIMIT, False, True),
    ],
)
def test_reason_has_exactly_one_valid_boundary(
    reason: EpisodeEndReason,
    terminated: bool,
    truncated: bool,
) -> None:
    assert StepBoundary.from_reason(reason) == StepBoundary(reason, terminated, truncated)


@pytest.mark.parametrize(
    ("reason", "terminated", "truncated"),
    [
        (EpisodeEndReason.NONE, True, False),
        (EpisodeEndReason.NONE, False, True),
        (EpisodeEndReason.COLLISION, False, False),
        (EpisodeEndReason.COLLISION, True, True),
        (EpisodeEndReason.OUT_OF_BOUNDS, False, True),
        (EpisodeEndReason.SUCCESS, False, True),
        (EpisodeEndReason.TIME_LIMIT, True, False),
        (EpisodeEndReason.TIME_LIMIT, True, True),
    ],
)
def test_boundary_rejects_illegal_flag_combinations(
    reason: EpisodeEndReason,
    terminated: bool,
    truncated: bool,
) -> None:
    with pytest.raises(ValueError, match="requires"):
        StepBoundary(reason, terminated, truncated)


def test_boundary_rejects_non_bool_flags() -> None:
    with pytest.raises(TypeError, match="must be bool"):
        StepBoundary(EpisodeEndReason.COLLISION, 1, False)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("conditions", "expected"),
    [
        ((False, False, False, False), EpisodeEndReason.NONE),
        ((False, False, False, True), EpisodeEndReason.TIME_LIMIT),
        ((False, False, True, True), EpisodeEndReason.SUCCESS),
        ((False, True, True, True), EpisodeEndReason.OUT_OF_BOUNDS),
        ((True, True, True, True), EpisodeEndReason.COLLISION),
        ((True, False, False, True), EpisodeEndReason.COLLISION),
    ],
)
def test_end_reason_uses_safety_first_priority(
    conditions: tuple[bool, bool, bool, bool],
    expected: EpisodeEndReason,
) -> None:
    assert (
        resolve_end_reason(
            collision=conditions[0],
            out_of_bounds=conditions[1],
            success=conditions[2],
            time_limit=conditions[3],
        )
        is expected
    )


def test_end_reason_rejects_numeric_truthiness() -> None:
    with pytest.raises(TypeError, match="must be bool"):
        resolve_end_reason(collision=1, out_of_bounds=False, success=False, time_limit=False)  # type: ignore[arg-type]


def test_episode_runtime_owns_clock_and_rng_outside_world_state():
    before_limit = EpisodeRuntime("episode-7", step_index=399, max_steps=400, rng_seed=123)
    at_limit = EpisodeRuntime("episode-7", step_index=400, max_steps=400, rng_seed=123)
    assert not before_limit.time_limit_reached
    assert at_limit.time_limit_reached


@pytest.mark.parametrize(
    "changes",
    [
        {"step_index": True},
        {"step_index": -1},
        {"max_steps": 0},
        {"step_index": 401},
        {"rng_seed": -1},
    ],
)
def test_episode_runtime_rejects_invalid_clock_or_rng(changes):
    values = {"episode_id": "episode-7", "step_index": 1, "max_steps": 400, "rng_seed": 2}
    values.update(changes)
    with pytest.raises((TypeError, ValueError)):
        EpisodeRuntime(**values)
