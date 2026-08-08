"""Deterministic recording and bitwise replay for physics trajectories."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
from typing import Any

from parking_rl.core.actions import NormalizedAction
from parking_rl.core.state import WorldState
from parking_rl.physics.dynamics import DynamicsConfig, PolicyStepTrace, step_world_state

_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
_COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")


def _require_lowercase_hex(name: str, value: object, pattern: re.Pattern[str], length: int) -> None:
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise ValueError(f"{name} must be lowercase hexadecimal of length {length}")


@dataclass(frozen=True, slots=True)
class ReplayProvenance:
    """Inputs needed to identify the exact experiment that produced a trace."""

    rng_seed: int
    config_sha256: str
    scenario_sha256: str
    implementation_commit: str

    def __post_init__(self) -> None:
        if isinstance(self.rng_seed, bool) or not isinstance(self.rng_seed, int):
            raise TypeError(f"rng_seed must be an int, not {type(self.rng_seed).__name__}")
        if self.rng_seed < 0:
            raise ValueError("rng_seed must be nonnegative")
        _require_lowercase_hex("config_sha256", self.config_sha256, _SHA256_PATTERN, 64)
        _require_lowercase_hex("scenario_sha256", self.scenario_sha256, _SHA256_PATTERN, 64)
        _require_lowercase_hex(
            "implementation_commit", self.implementation_commit, _COMMIT_PATTERN, 40
        )


@dataclass(frozen=True, slots=True)
class EpisodeTrace:
    """Complete policy-boundary and substep record for a deterministic episode."""

    provenance: ReplayProvenance
    initial_state: WorldState
    requested_actions: tuple[NormalizedAction, ...]
    policy_steps: tuple[PolicyStepTrace, ...]
    states: tuple[WorldState, ...]
    dynamics_config: DynamicsConfig

    def __post_init__(self) -> None:
        if type(self.provenance) is not ReplayProvenance:
            raise TypeError("provenance must be exactly ReplayProvenance")
        if type(self.initial_state) is not WorldState:
            raise TypeError("initial_state must be exactly WorldState")
        if type(self.dynamics_config) is not DynamicsConfig:
            raise TypeError("dynamics_config must be exactly DynamicsConfig")

        requested_actions = _freeze_tuple(
            "requested_actions", self.requested_actions, NormalizedAction
        )
        policy_steps = _freeze_tuple("policy_steps", self.policy_steps, PolicyStepTrace)
        states = _freeze_tuple("states", self.states, WorldState)
        object.__setattr__(self, "requested_actions", requested_actions)
        object.__setattr__(self, "policy_steps", policy_steps)
        object.__setattr__(self, "states", states)
        if not len(requested_actions) == len(policy_steps) == len(states):
            raise ValueError("requested_actions, policy_steps, and states must have equal length")
        for index, (requested, step, state) in enumerate(
            zip(requested_actions, policy_steps, states, strict=True)
        ):
            if step.requested_action != requested:
                raise ValueError(f"policy_steps[{index}] does not match requested_actions[{index}]")
            if step.substeps[-1] != state.ego:
                raise ValueError(f"states[{index}] is not the policy boundary's final substep")

    @property
    def sha256(self) -> str:
        """Stable IEEE-aware digest of the complete trace."""

        return trace_sha256(self)


def _freeze_tuple(name: str, value: object, expected: type[Any]) -> tuple[Any, ...]:
    try:
        frozen = tuple(value)  # type: ignore[arg-type]
    except TypeError as error:
        raise TypeError(f"{name} must be an iterable of {expected.__name__}") from error
    if any(type(item) is not expected for item in frozen):
        raise TypeError(f"{name} must contain only {expected.__name__} values")
    return frozen


def record_episode(
    initial_state: WorldState,
    actions: tuple[NormalizedAction, ...],
    provenance: ReplayProvenance,
    config: DynamicsConfig | None = None,
) -> EpisodeTrace:
    """Run and record an episode with every requested/applied action and substep."""

    if type(initial_state) is not WorldState:
        raise TypeError("initial_state must be exactly WorldState")
    if type(provenance) is not ReplayProvenance:
        raise TypeError("provenance must be exactly ReplayProvenance")
    if config is None:
        config = DynamicsConfig()
    if type(config) is not DynamicsConfig:
        raise TypeError("config must be exactly DynamicsConfig")
    requested_actions = _freeze_tuple("actions", actions, NormalizedAction)

    world = initial_state
    policy_steps: list[PolicyStepTrace] = []
    states: list[WorldState] = []
    for requested_action in requested_actions:
        world, policy_step = step_world_state(world, requested_action, config)
        policy_steps.append(policy_step)
        states.append(world)
    return EpisodeTrace(
        provenance=provenance,
        initial_state=initial_state,
        requested_actions=requested_actions,
        policy_steps=tuple(policy_steps),
        states=tuple(states),
        dynamics_config=config,
    )


def replay_episode(trace: EpisodeTrace) -> EpisodeTrace:
    """Recompute a trace exclusively from its captured initial inputs."""

    if type(trace) is not EpisodeTrace:
        raise TypeError("trace must be exactly EpisodeTrace")
    return record_episode(
        initial_state=trace.initial_state,
        actions=trace.requested_actions,
        provenance=trace.provenance,
        config=trace.dynamics_config,
    )


def _ieee_value(value: object) -> object:
    if is_dataclass(value) and not isinstance(value, type):
        value_type = type(value)
        return {
            "__dataclass__": f"{value_type.__module__}.{value_type.__qualname__}",
            "fields": {
                field.name: _ieee_value(getattr(value, field.name)) for field in fields(value)
            },
        }
    if isinstance(value, Enum):
        value_type = type(value)
        return {
            "__enum__": f"{value_type.__module__}.{value_type.__qualname__}",
            "value": _ieee_value(value.value),
        }
    if type(value) is tuple:
        return {"__tuple__": [_ieee_value(item) for item in value]}
    if type(value) is float:
        return {"__float_hex__": value.hex()}
    if value is None or type(value) in {bool, int, str}:
        return value
    raise TypeError(f"unsupported canonical value type: {type(value).__name__}")


def ieee_canonical_bytes(trace: EpisodeTrace) -> bytes:
    """Encode a trace without decimal-float formatting or platform defaults."""

    if type(trace) is not EpisodeTrace:
        raise TypeError("trace must be exactly EpisodeTrace")
    return json.dumps(
        _ieee_value(trace),
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def trace_sha256(trace: EpisodeTrace) -> str:
    """Return the stable SHA-256 digest for a trace."""

    return hashlib.sha256(ieee_canonical_bytes(trace)).hexdigest()


def bitwise_equal(first: EpisodeTrace, second: EpisodeTrace) -> bool:
    """Compare all trace fields by their canonical IEEE representation."""

    if type(first) is not EpisodeTrace or type(second) is not EpisodeTrace:
        raise TypeError("both traces must be exactly EpisodeTrace")
    return ieee_canonical_bytes(first) == ieee_canonical_bytes(second)


def replay_matches(trace: EpisodeTrace) -> bool:
    """Return whether a trace reproduces bit-for-bit from captured inputs."""

    return bitwise_equal(trace, replay_episode(trace))
