from __future__ import annotations

import math

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
    advance_actuator,
    clamp_control,
    integrate_substep,
    scale_action,
    step_world_state,
)


def vehicle(
    *, latency_steps: int = 0, max_latency_steps: int = 2, **changes: object
) -> VehicleSpec:
    values: dict[str, object] = {
        "wheelbase_m": 2.8,
        "length_m": 4.7,
        "width_m": 1.9,
        "front_overhang_m": 1.0,
        "rear_overhang_m": 0.9,
        "max_steering_angle_rad": 0.6,
        "max_steering_rate_radps": 0.5,
        "max_speed_mps": 3.0,
        "max_acceleration_mps2": 2.0,
        "latency_steps": latency_steps,
        "max_latency_steps": max_latency_steps,
    }
    values.update(changes)
    return VehicleSpec(**values)  # type: ignore[arg-type]


def actuator(spec: VehicleSpec) -> ActuatorState:
    return ActuatorState(
        applied_control=PhysicalControl(0.0, 0.0),
        pending_commands=(ZERO_NORMALIZED_ACTION,) * spec.max_latency_steps,
        latency_steps=spec.latency_steps,
    )


def world(spec: VehicleSpec | None = None) -> WorldState:
    spec = spec or vehicle()
    goal = ObjectState(
        id="goal",
        kind=ObjectKind.GOAL_SLOT,
        role=ObjectRole.GOAL_SLOT,
        pose=ObjectCentroidWorldPose(8.0, 1.0, 0.0),
        length_m=6.0,
        width_m=2.5,
    )
    static = StaticWorld(
        bounds=Bounds2D(-20.0, 20.0, -20.0, 20.0),
        objects=(goal,),
        goal_object_id=goal.id,
    )
    return WorldState(
        vehicle=spec,
        static_world=static,
        ego=EgoState(RearAxleWorldPose(0.0, 0.0, 0.0), 0.0, 0.0),
        objects=static.objects,
        settle=SettleProgress(0, 10),
        actuator=actuator(spec),
    )


def test_action_scaling_is_the_exact_normalized_to_physical_boundary() -> None:
    spec = vehicle()
    assert scale_action(NormalizedAction(-0.25, 0.4), spec) == PhysicalControl(-0.5, 0.2)
    with pytest.raises(TypeError, match="exactly NormalizedAction"):
        scale_action(object(), spec)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="exactly VehicleSpec"):
        scale_action(NormalizedAction(0.0, 0.0), object())  # type: ignore[arg-type]


@pytest.mark.parametrize("bad_dt", [True, 0.0, -0.1, math.inf, math.nan])
def test_dynamics_config_rejects_invalid_policy_period(bad_dt: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        DynamicsConfig(dt_policy_s=bad_dt)  # type: ignore[arg-type]


@pytest.mark.parametrize("bad_substeps", [True, 4, 6, 5.0])
def test_dynamics_config_fixes_the_stage_zero_substep_count(bad_substeps: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        DynamicsConfig(substeps=bad_substeps)  # type: ignore[arg-type]


def test_integrate_substep_matches_old_state_explicit_euler_golden_values() -> None:
    spec = vehicle()
    initial = EgoState(RearAxleWorldPose(1.0, -2.0, 0.3), 2.0, 0.2)
    control = PhysicalControl(1.0, -0.1)
    dt_s = 0.02

    actual = integrate_substep(initial, control, spec, dt_s)

    assert actual.pose.x_m == pytest.approx(1.0 + 2.0 * math.cos(0.3) * dt_s)
    assert actual.pose.y_m == pytest.approx(-2.0 + 2.0 * math.sin(0.3) * dt_s)
    assert actual.pose.heading_rad == pytest.approx(
        0.3 + 2.0 / spec.wheelbase_m * math.tan(0.2) * dt_s
    )
    assert actual.speed_mps == pytest.approx(2.0 + 1.0 * dt_s)
    assert actual.steering_rad == pytest.approx(0.2 - 0.1 * dt_s)


def test_integrate_substep_always_clamps_physical_control() -> None:
    spec = vehicle()
    initial = EgoState(RearAxleWorldPose(0.0, 0.0, 0.0), 0.0, 0.0)
    actual = integrate_substep(initial, PhysicalControl(20.0, -20.0), spec, 0.02)
    assert actual.speed_mps == pytest.approx(spec.max_acceleration_mps2 * 0.02)
    assert actual.steering_rad == pytest.approx(-spec.max_steering_rate_radps * 0.02)
    assert clamp_control(PhysicalControl(20.0, -20.0), spec) == PhysicalControl(2.0, -0.5)


@pytest.mark.parametrize(
    ("ego", "message"),
    [
        (EgoState(RearAxleWorldPose(0.0, 0.0, 0.0), 3.01, 0.0), "speed_mps"),
        (EgoState(RearAxleWorldPose(0.0, 0.0, 0.0), 0.0, -0.61), "steering_rad"),
    ],
)
def test_integrate_substep_rejects_initial_state_outside_limits(
    ego: EgoState, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        integrate_substep(ego, PhysicalControl(0.0, 0.0), vehicle(), 0.02)


@pytest.mark.parametrize(
    "changes",
    [{"steering_gain": 1.01}, {"steering_offset_rad": 0.01}],
)
def test_stage_zero_rejects_uncalibrated_steering_semantics(changes: dict[str, float]) -> None:
    with pytest.raises(ValueError, match=r"steering_gain=1\.0"):
        integrate_substep(
            EgoState(RearAxleWorldPose(0.0, 0.0, 0.0), 0.0, 0.0),
            PhysicalControl(0.0, 0.0),
            vehicle(**changes),
            0.02,
        )


def test_latency_zero_applies_current_request_and_preserves_zero_padding() -> None:
    spec = vehicle(latency_steps=0, max_latency_steps=2)
    requested = NormalizedAction(0.5, -0.25)
    applied, next_actuator = advance_actuator(actuator(spec), requested, spec)
    assert applied is requested
    assert next_actuator.applied_control == PhysicalControl(1.0, -0.125)
    assert next_actuator.pending_commands == (ZERO_NORMALIZED_ACTION,) * 2


def test_latency_one_delays_request_by_one_policy_step() -> None:
    spec = vehicle(latency_steps=1, max_latency_steps=3)
    first = NormalizedAction(0.5, 0.25)
    second = NormalizedAction(-0.5, -0.25)
    applied_1, state_1 = advance_actuator(actuator(spec), first, spec)
    applied_2, state_2 = advance_actuator(state_1, second, spec)
    assert applied_1 == ZERO_NORMALIZED_ACTION
    assert applied_2 == first
    assert state_1.pending_commands == (first, ZERO_NORMALIZED_ACTION, ZERO_NORMALIZED_ACTION)
    assert state_2.pending_commands == (second, ZERO_NORMALIZED_ACTION, ZERO_NORMALIZED_ACTION)


def test_latency_two_is_fifo_and_keeps_inactive_padding_zero() -> None:
    spec = vehicle(latency_steps=2, max_latency_steps=3)
    first = NormalizedAction(0.1, 0.2)
    second = NormalizedAction(0.3, 0.4)
    third = NormalizedAction(0.5, 0.6)
    applied_1, state = advance_actuator(actuator(spec), first, spec)
    applied_2, state = advance_actuator(state, second, spec)
    applied_3, state = advance_actuator(state, third, spec)
    assert (applied_1, applied_2, applied_3) == (
        ZERO_NORMALIZED_ACTION,
        ZERO_NORMALIZED_ACTION,
        first,
    )
    assert state.pending_commands == (second, third, ZERO_NORMALIZED_ACTION)


def test_policy_step_uses_zero_order_hold_for_exactly_five_substeps() -> None:
    initial = world()
    requested = NormalizedAction(1.0, 1.0)
    advanced, trace = step_world_state(initial, requested)
    assert len(trace.substeps) == 5
    assert trace.applied_action == requested
    assert trace.applied_control == PhysicalControl(2.0, 0.5)
    assert advanced.ego is trace.substeps[-1]
    assert advanced.objects is initial.objects
    assert advanced.static_world is initial.static_world
    assert advanced.settle is initial.settle
    for before, after in zip((initial.ego, *trace.substeps[:-1]), trace.substeps, strict=True):
        assert after.speed_mps - before.speed_mps == pytest.approx(0.04)
        assert after.steering_rad - before.steering_rad == pytest.approx(0.01)


@pytest.mark.parametrize("longitudinal", [-1.0, 1.0])
@pytest.mark.parametrize("steering_rate", [-1.0, 1.0])
def test_four_corner_saturation_respects_bounds_at_every_substep(
    longitudinal: float, steering_rate: float
) -> None:
    spec = vehicle()
    current = world(spec)
    action = NormalizedAction(longitudinal, steering_rate)
    previous = current.ego
    for _ in range(400):
        current, trace = step_world_state(current, action)
        for state in trace.substeps:
            assert abs(state.speed_mps) <= spec.max_speed_mps
            assert abs(state.steering_rad) <= spec.max_steering_angle_rad
            assert abs(state.speed_mps - previous.speed_mps) <= (
                spec.max_acceleration_mps2 * DynamicsConfig().dt_sub_s + 1e-15
            )
            assert abs(state.steering_rad - previous.steering_rad) <= (
                spec.max_steering_rate_radps * DynamicsConfig().dt_sub_s + 1e-15
            )
            previous = state
    assert current.ego.speed_mps == longitudinal * spec.max_speed_mps
    assert current.ego.steering_rad == steering_rate * spec.max_steering_angle_rad


def test_policy_step_replay_is_bitwise_deterministic_in_process() -> None:
    actions = tuple(NormalizedAction(math.sin(index), math.cos(index)) for index in range(100))

    def replay() -> tuple[WorldState, tuple[object, ...]]:
        current = world()
        traces: list[object] = []
        for action in actions:
            current, trace = step_world_state(current, action)
            traces.append(trace)
        return current, tuple(traces)

    assert replay() == replay()
