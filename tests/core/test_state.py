import math
from dataclasses import FrozenInstanceError, fields

import pytest

from parking_rl.core.actions import (
    ZERO_NORMALIZED_ACTION,
    NormalizedAction,
    PhysicalControl,
)
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


def _vehicle(*, latency_steps: int = 0, max_latency_steps: int = 0) -> VehicleSpec:
    return VehicleSpec(
        wheelbase_m=2.7,
        length_m=4.7,
        width_m=1.8,
        front_overhang_m=1.1,
        rear_overhang_m=0.9,
        max_steering_angle_rad=0.6,
        max_steering_rate_radps=0.5,
        max_speed_mps=3.0,
        max_acceleration_mps2=2.0,
        latency_steps=latency_steps,
        max_latency_steps=max_latency_steps,
    )


def _objects() -> tuple[ObjectState, ...]:
    return (
        ObjectState(
            id="front",
            kind=ObjectKind.VEHICLE,
            role=ObjectRole.FRONT_VEHICLE,
            pose=ObjectCentroidWorldPose(3.0, 0.0, 0.0),
            length_m=4.7,
            width_m=1.8,
        ),
        ObjectState(
            id="goal",
            kind=ObjectKind.GOAL_SLOT,
            role=ObjectRole.GOAL_SLOT,
            pose=ObjectCentroidWorldPose(0.0, 0.0, 0.0),
            length_m=6.0,
            width_m=2.2,
        ),
    )


def _static_world(objects: object | None = None, goal_object_id: str = "goal") -> StaticWorld:
    return StaticWorld(
        bounds=Bounds2D(-10.0, 10.0, -8.0, 8.0),
        objects=_objects() if objects is None else objects,  # type: ignore[arg-type]
        goal_object_id=goal_object_id,
    )


def _ego() -> EgoState:
    return EgoState(RearAxleWorldPose(-4.0, 1.0, 0.0), speed_mps=0.0, steering_rad=0.0)


def _actuator(*, latency_steps: int = 0, capacity: int = 0) -> ActuatorState:
    return ActuatorState(
        applied_control=PhysicalControl(0.0, 0.0),
        pending_commands=(ZERO_NORMALIZED_ACTION,) * capacity,
        latency_steps=latency_steps,
    )


def _world(*, latency_steps: int = 0, capacity: int = 0) -> WorldState:
    static_world = _static_world()
    return WorldState(
        vehicle=_vehicle(latency_steps=latency_steps, max_latency_steps=capacity),
        static_world=static_world,
        ego=_ego(),
        objects=static_world.objects,
        settle=SettleProgress(0, 5),
        actuator=_actuator(latency_steps=latency_steps, capacity=capacity),
    )


def test_vehicle_spec_validates_geometry_limits_and_latency() -> None:
    assert _vehicle().steering_gain == 1.0
    assert _vehicle().steering_offset_rad == 0.0

    with pytest.raises(ValueError, match="must equal"):
        VehicleSpec(
            wheelbase_m=2.7,
            length_m=4.8,
            width_m=1.8,
            front_overhang_m=1.1,
            rear_overhang_m=0.9,
            max_steering_angle_rad=0.6,
            max_steering_rate_radps=0.5,
            max_speed_mps=3.0,
            max_acceleration_mps2=2.0,
        )
    with pytest.raises(ValueError, match="must not exceed"):
        _vehicle(latency_steps=2, max_latency_steps=1)


@pytest.mark.parametrize("value", [True, math.nan, math.inf])
def test_vehicle_spec_rejects_invalid_numeric_values(value: float) -> None:
    kwargs = {
        "wheelbase_m": value,
        "length_m": 4.7,
        "width_m": 1.8,
        "front_overhang_m": 1.1,
        "rear_overhang_m": 0.9,
        "max_steering_angle_rad": 0.6,
        "max_steering_rate_radps": 0.5,
        "max_speed_mps": 3.0,
        "max_acceleration_mps2": 2.0,
    }

    with pytest.raises((TypeError, ValueError)):
        VehicleSpec(**kwargs)


def test_bounds_are_strict_and_finite() -> None:
    with pytest.raises(ValueError, match="less than"):
        Bounds2D(1.0, 1.0, -1.0, 1.0)
    with pytest.raises(ValueError, match="finite"):
        Bounds2D(-1.0, math.inf, -1.0, 1.0)
    with pytest.raises(TypeError, match="real number"):
        Bounds2D(False, 1.0, -1.0, 1.0)


def test_object_role_must_match_kind() -> None:
    with pytest.raises(ValueError, match="incompatible"):
        ObjectState(
            id="bad",
            kind=ObjectKind.KERB,
            role=ObjectRole.FRONT_VEHICLE,
            pose=ObjectCentroidWorldPose(0.0, 0.0, 0.0),
            length_m=1.0,
            width_m=1.0,
        )


@pytest.mark.parametrize(
    ("count", "required_steps", "error"),
    [
        (0, 5, None),
        (5, 5, None),
        (-1, 5, ValueError),
        (6, 5, ValueError),
        (0, 0, ValueError),
        (False, 5, TypeError),
        (0, True, TypeError),
    ],
)
def test_settle_progress_boundaries(
    count: int,
    required_steps: int,
    error: type[Exception] | None,
) -> None:
    if error is None:
        assert SettleProgress(count, required_steps).count == count
    else:
        with pytest.raises(error):
            SettleProgress(count, required_steps)


def test_actuator_zero_latency_and_active_zero_command_are_distinct() -> None:
    zero_capacity = _actuator(latency_steps=0, capacity=0)
    padded = _actuator(latency_steps=0, capacity=1)
    active_zero = _actuator(latency_steps=1, capacity=1)

    assert zero_capacity.pending_commands == ()
    assert padded.active_pending_commands == ()
    assert active_zero.active_pending_commands == (ZERO_NORMALIZED_ACTION,)
    assert padded != active_zero


def test_actuator_rejects_nonzero_inactive_padding() -> None:
    with pytest.raises(ValueError, match="padding"):
        ActuatorState(
            applied_control=PhysicalControl(0.0, 0.0),
            pending_commands=[
                ZERO_NORMALIZED_ACTION,
                NormalizedAction(longitudinal=0.5, steering_rate=0.0),
            ],
            latency_steps=1,
        )


def test_iterable_inputs_are_deeply_frozen_as_tuples() -> None:
    source_objects = list(_objects())
    static_world = _static_world(source_objects)
    source_commands = [ZERO_NORMALIZED_ACTION]
    actuator = ActuatorState(PhysicalControl(0.0, 0.0), source_commands, latency_steps=0)

    source_objects.clear()
    source_commands.clear()

    assert static_world.objects == _objects()
    assert actuator.pending_commands == (ZERO_NORMALIZED_ACTION,)
    with pytest.raises(FrozenInstanceError):
        static_world.goal_object_id = "other"  # type: ignore[misc]


def test_static_world_rejects_missing_or_wrong_goal_id() -> None:
    with pytest.raises(ValueError, match="identify an object"):
        _static_world(goal_object_id="missing")
    with pytest.raises(ValueError, match="GOAL_SLOT"):
        _static_world(goal_object_id="front")


def test_world_state_requires_exact_object_id_set() -> None:
    static_world = _static_world()
    kwargs = {
        "vehicle": _vehicle(),
        "static_world": static_world,
        "ego": _ego(),
        "settle": SettleProgress(0, 5),
        "actuator": _actuator(),
    }

    with pytest.raises(ValueError, match="exactly"):
        WorldState(objects=static_world.objects[:-1], **kwargs)

    wrong_goal = ObjectState(
        id="goal",
        kind=ObjectKind.KERB,
        role=ObjectRole.KERB,
        pose=ObjectCentroidWorldPose(0.0, 0.0, 0.0),
        length_m=6.0,
        width_m=2.2,
    )
    with pytest.raises(ValueError, match="kind and role"):
        WorldState(objects=(static_world.objects[0], wrong_goal), **kwargs)


def test_world_state_rejects_latency_or_capacity_mismatch() -> None:
    static_world = _static_world()
    common = {
        "static_world": static_world,
        "ego": _ego(),
        "objects": static_world.objects,
        "settle": SettleProgress(0, 5),
    }
    with pytest.raises(ValueError, match="latency_steps"):
        WorldState(
            vehicle=_vehicle(latency_steps=0, max_latency_steps=1),
            actuator=_actuator(latency_steps=1, capacity=1),
            **common,
        )
    with pytest.raises(ValueError, match="capacity"):
        WorldState(
            vehicle=_vehicle(latency_steps=0, max_latency_steps=2),
            actuator=_actuator(latency_steps=0, capacity=1),
            **common,
        )


def test_world_state_freezes_object_list_and_excludes_runtime_or_done_fields() -> None:
    static_world = _static_world()
    source_objects = list(static_world.objects)
    world = WorldState(
        vehicle=_vehicle(),
        static_world=static_world,
        ego=_ego(),
        objects=source_objects,
        settle=SettleProgress(0, 5),
        actuator=_actuator(),
    )

    source_objects.clear()
    field_names = {field.name for field in fields(WorldState)}

    assert world.objects == static_world.objects
    assert "step_index" not in field_names
    assert "max_steps" not in field_names
    assert "done" not in field_names
    assert "episode_done" not in field_names
