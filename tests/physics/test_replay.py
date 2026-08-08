from __future__ import annotations

import math
import subprocess
import sys
from dataclasses import replace

import pytest

from parking_rl.core.actions import ZERO_NORMALIZED_ACTION, NormalizedAction, PhysicalControl
from parking_rl.core.frames import ObjectCentroidWorldPose, RearAxleWorldPose
from parking_rl.core.state import (
    ActuatorState,
    Bounds2D,
    EgoState,
    ObjectKind,
    ObjectRole,
    ObjectState,
    SettleProgress,
    StaticWorld,
    VehicleSpec,
    WorldState,
)
from parking_rl.physics import (
    DynamicsConfig,
    EpisodeTrace,
    PolicyStepTrace,
    ReplayProvenance,
    bitwise_equal,
    ieee_canonical_bytes,
    record_episode,
    replay_episode,
    replay_matches,
)


def _world(*, latency_steps: int = 0) -> WorldState:
    vehicle = VehicleSpec(
        wheelbase_m=2.8,
        length_m=4.7,
        width_m=1.9,
        front_overhang_m=1.0,
        rear_overhang_m=0.9,
        max_steering_angle_rad=0.6,
        max_steering_rate_radps=0.5,
        max_speed_mps=3.0,
        max_acceleration_mps2=2.0,
        latency_steps=latency_steps,
        max_latency_steps=2,
    )
    goal = ObjectState(
        id="goal",
        kind=ObjectKind.GOAL_SLOT,
        role=ObjectRole.GOAL_SLOT,
        pose=ObjectCentroidWorldPose(8.0, 1.0, 0.0),
        length_m=6.0,
        width_m=2.5,
    )
    static_world = StaticWorld(
        bounds=Bounds2D(-20.0, 20.0, -20.0, 20.0),
        objects=(goal,),
        goal_object_id=goal.id,
    )
    return WorldState(
        vehicle=vehicle,
        static_world=static_world,
        ego=EgoState(RearAxleWorldPose(0.0, 0.0, 0.0), 0.0, 0.0),
        objects=static_world.objects,
        settle=SettleProgress(0, 10),
        actuator=ActuatorState(
            applied_control=PhysicalControl(0.0, 0.0),
            pending_commands=(ZERO_NORMALIZED_ACTION,) * 2,
            latency_steps=latency_steps,
        ),
    )


def _provenance() -> ReplayProvenance:
    return ReplayProvenance(
        rng_seed=17,
        config_sha256="a" * 64,
        scenario_sha256="b" * 64,
        implementation_commit="c" * 40,
    )


def _trace(*, latency_steps: int = 0) -> EpisodeTrace:
    return record_episode(
        _world(latency_steps=latency_steps),
        (
            NormalizedAction(0.8, 0.5),
            NormalizedAction(-0.2, -0.75),
            NormalizedAction(0.1, 0.25),
        ),
        _provenance(),
        DynamicsConfig(dt_policy_s=0.1, substeps=5),
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"rng_seed": True},
        {"rng_seed": -1},
        {"config_sha256": "A" * 64},
        {"scenario_sha256": "a" * 63},
        {"implementation_commit": "g" * 40},
    ],
)
def test_replay_provenance_is_strict(changes: dict[str, object]) -> None:
    values: dict[str, object] = {
        "rng_seed": 17,
        "config_sha256": "a" * 64,
        "scenario_sha256": "b" * 64,
        "implementation_commit": "c" * 40,
    }
    values.update(changes)
    with pytest.raises((TypeError, ValueError)):
        ReplayProvenance(**values)  # type: ignore[arg-type]


def test_record_and_replay_are_bitwise_equal() -> None:
    trace = _trace()
    replayed = replay_episode(trace)
    assert trace.dynamics_config == DynamicsConfig(0.1, 5)
    assert len(trace.requested_actions) == len(trace.policy_steps) == len(trace.states) == 3
    assert all(
        state.ego == step.substeps[-1]
        for state, step in zip(trace.states, trace.policy_steps, strict=True)
    )
    assert bitwise_equal(trace, replayed)
    assert replay_matches(trace)
    assert trace.sha256 == replayed.sha256


def test_changed_action_and_tampered_state_do_not_match() -> None:
    trace = _trace()
    changed_action = record_episode(
        trace.initial_state,
        (*trace.requested_actions[:-1], NormalizedAction(0.2, 0.25)),
        trace.provenance,
        trace.dynamics_config,
    )
    assert not bitwise_equal(trace, changed_action)

    final = trace.states[-1]
    tampered_ego = replace(
        final.ego,
        pose=replace(final.ego.pose, x_m=math.nextafter(final.ego.pose.x_m, math.inf)),
    )
    final_step = trace.policy_steps[-1]
    tampered_step = replace(
        final_step,
        substeps=(*final_step.substeps[:-1], tampered_ego),
    )
    tampered = EpisodeTrace(
        provenance=trace.provenance,
        initial_state=trace.initial_state,
        requested_actions=trace.requested_actions,
        policy_steps=(*trace.policy_steps[:-1], tampered_step),
        states=(*trace.states[:-1], replace(final, ego=tampered_ego)),
        dynamics_config=trace.dynamics_config,
    )
    assert not replay_matches(tampered)


def test_latency_keeps_requested_and_applied_actions_in_trace() -> None:
    trace = _trace(latency_steps=1)
    assert trace.policy_steps[0].requested_action == NormalizedAction(0.8, 0.5)
    assert trace.policy_steps[0].applied_action == ZERO_NORMALIZED_ACTION
    assert trace.policy_steps[0].applied_control == PhysicalControl(0.0, 0.0)
    assert trace.policy_steps[1].applied_action == trace.requested_actions[0]
    assert trace.policy_steps[1].applied_control == PhysicalControl(1.6, 0.25)


def test_episode_trace_deep_freezes_input_sequences() -> None:
    trace = _trace()
    actions = list(trace.requested_actions)
    steps = list(trace.policy_steps)
    states = list(trace.states)
    frozen = EpisodeTrace(
        trace.provenance,
        trace.initial_state,
        actions,  # type: ignore[arg-type]
        steps,  # type: ignore[arg-type]
        states,  # type: ignore[arg-type]
        trace.dynamics_config,
    )
    actions.clear()
    steps.clear()
    states.clear()
    assert len(frozen.requested_actions) == len(frozen.policy_steps) == len(frozen.states) == 3
    with pytest.raises(AttributeError):
        frozen.states.append(trace.initial_state)  # type: ignore[attr-defined]


def test_ieee_encoding_distinguishes_signed_zero_and_adjacent_floats() -> None:
    positive_zero = record_episode(_world(), (NormalizedAction(0.0, 0.1),), _provenance())
    negative_zero = record_episode(_world(), (NormalizedAction(-0.0, 0.1),), _provenance())
    adjacent = record_episode(
        _world(),
        (NormalizedAction(math.nextafter(0.0, 1.0), 0.1),),
        _provenance(),
    )
    encoded = ieee_canonical_bytes(positive_zero)
    assert b"__float_hex__" in encoded
    assert b"0x0.0p+0" in encoded
    assert ieee_canonical_bytes(positive_zero) != ieee_canonical_bytes(negative_zero)
    assert ieee_canonical_bytes(positive_zero) != ieee_canonical_bytes(adjacent)


def test_trace_digest_is_stable_across_independent_processes() -> None:
    script = r"""
from parking_rl.core.actions import ZERO_NORMALIZED_ACTION, NormalizedAction, PhysicalControl
from parking_rl.core.frames import ObjectCentroidWorldPose, RearAxleWorldPose
from parking_rl.core.state import (
    ActuatorState, Bounds2D, EgoState, ObjectKind, ObjectRole, ObjectState,
    SettleProgress, StaticWorld, VehicleSpec, WorldState,
)
from parking_rl.physics.replay import ReplayProvenance, record_episode
vehicle = VehicleSpec(2.8, 4.7, 1.9, 1.0, 0.9, 0.6, 0.5, 3.0, 2.0, max_latency_steps=2)
goal = ObjectState(
    "goal", ObjectKind.GOAL_SLOT, ObjectRole.GOAL_SLOT,
    ObjectCentroidWorldPose(8.0, 1.0, 0.0), 6.0, 2.5,
)
static = StaticWorld(Bounds2D(-20.0, 20.0, -20.0, 20.0), (goal,), "goal")
world = WorldState(
    vehicle, static, EgoState(RearAxleWorldPose(0.0, 0.0, 0.0), 0.0, 0.0),
    static.objects, SettleProgress(0, 10),
    ActuatorState(PhysicalControl(0.0, 0.0), (ZERO_NORMALIZED_ACTION,) * 2, 0),
)
provenance = ReplayProvenance(17, "a" * 64, "b" * 64, "c" * 40)
actions = (
    NormalizedAction(0.8, 0.5), NormalizedAction(-0.2, -0.75),
    NormalizedAction(0.1, 0.25),
)
print(record_episode(world, actions, provenance).sha256)
"""
    first = subprocess.run(
        [sys.executable, "-c", script], check=True, capture_output=True, text=True
    ).stdout.strip()
    second = subprocess.run(
        [sys.executable, "-c", script], check=True, capture_output=True, text=True
    ).stdout.strip()
    assert first == second == _trace().sha256


def test_episode_trace_rejects_misaligned_boundary_records() -> None:
    trace = _trace()
    with pytest.raises(ValueError, match="equal length"):
        replace(trace, states=trace.states[:-1])
    with pytest.raises(ValueError, match="does not match"):
        replace(
            trace,
            policy_steps=(
                replace(
                    trace.policy_steps[0],
                    requested_action=NormalizedAction(0.7, 0.5),
                ),
                *trace.policy_steps[1:],
            ),
        )
    with pytest.raises(ValueError, match="final substep"):
        replace(
            trace,
            states=(replace(trace.states[0], ego=trace.initial_state.ego), *trace.states[1:]),
        )


def test_policy_step_trace_remains_the_physical_audit_boundary() -> None:
    trace = _trace()
    assert all(type(step) is PolicyStepTrace for step in trace.policy_steps)
    assert all(len(step.substeps) == trace.dynamics_config.substeps for step in trace.policy_steps)
