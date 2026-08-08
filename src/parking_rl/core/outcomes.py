"""Mutually exclusive episode-boundary contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class EpisodeEndReason(StrEnum):
    """The exclusive reason a policy step ended an episode, if any."""

    NONE = "none"
    COLLISION = "collision"
    OUT_OF_BOUNDS = "out_of_bounds"
    SUCCESS = "success"
    TIME_LIMIT = "time_limit"


_BOUNDARY_FLAGS = {
    EpisodeEndReason.NONE: (False, False),
    EpisodeEndReason.COLLISION: (True, False),
    EpisodeEndReason.OUT_OF_BOUNDS: (True, False),
    EpisodeEndReason.SUCCESS: (True, False),
    EpisodeEndReason.TIME_LIMIT: (False, True),
}


@dataclass(frozen=True, slots=True)
class StepBoundary:
    """Gymnasium-style terminal flags coupled to their unique reason."""

    reason: EpisodeEndReason
    terminated: bool
    truncated: bool

    def __post_init__(self) -> None:
        if type(self.reason) is not EpisodeEndReason:
            raise TypeError("reason must be exactly EpisodeEndReason")
        if type(self.terminated) is not bool or type(self.truncated) is not bool:
            raise TypeError("terminated and truncated must be bool")
        expected = _BOUNDARY_FLAGS[self.reason]
        if (self.terminated, self.truncated) != expected:
            raise ValueError(
                f"{self.reason.value} requires terminated={expected[0]} and truncated={expected[1]}"
            )

    @classmethod
    def from_reason(cls, reason: EpisodeEndReason) -> StepBoundary:
        """Construct the only valid flag pair for ``reason``."""

        if type(reason) is not EpisodeEndReason:
            raise TypeError("reason must be exactly EpisodeEndReason")
        terminated, truncated = _BOUNDARY_FLAGS[reason]
        return cls(reason=reason, terminated=terminated, truncated=truncated)


@dataclass(frozen=True, slots=True)
class EpisodeRuntime:
    """Episode clock and RNG identity, kept deliberately outside ``WorldState``."""

    episode_id: str
    step_index: int
    max_steps: int
    rng_seed: int

    def __post_init__(self) -> None:
        if type(self.episode_id) is not str or not self.episode_id:
            raise ValueError("episode_id must be a non-empty string")
        for name in ("step_index", "max_steps", "rng_seed"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an int")
        if self.step_index < 0 or self.rng_seed < 0 or self.max_steps <= 0:
            raise ValueError("step_index/rng_seed must be nonnegative and max_steps positive")
        if self.step_index > self.max_steps:
            raise ValueError("step_index must not exceed max_steps")

    @property
    def time_limit_reached(self) -> bool:
        return self.step_index >= self.max_steps


def resolve_end_reason(
    *,
    collision: bool,
    out_of_bounds: bool,
    success: bool,
    time_limit: bool,
) -> EpisodeEndReason:
    """Resolve simultaneous conditions using the documented safety-first priority."""

    conditions = (collision, out_of_bounds, success, time_limit)
    if any(type(condition) is not bool for condition in conditions):
        raise TypeError("episode-end conditions must be bool")
    if collision:
        return EpisodeEndReason.COLLISION
    if out_of_bounds:
        return EpisodeEndReason.OUT_OF_BOUNDS
    if success:
        return EpisodeEndReason.SUCCESS
    if time_limit:
        return EpisodeEndReason.TIME_LIMIT
    return EpisodeEndReason.NONE
