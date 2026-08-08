from __future__ import annotations

import builtins
import subprocess
import sys

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
    ReplayFrame,
    ReplayProvenance,
    animate_trajectory,
    obb_corners,
    record_episode,
    replay_frames,
    vehicle_obb,
)


def _trace():  # type: ignore[no-untyped-def]
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
        max_latency_steps=1,
    )
    parked = ObjectState(
        "front",
        ObjectKind.VEHICLE,
        ObjectRole.FRONT_VEHICLE,
        ObjectCentroidWorldPose(8.0, 1.0, 0.0),
        4.7,
        1.9,
    )
    goal = ObjectState(
        "goal",
        ObjectKind.GOAL_SLOT,
        ObjectRole.GOAL_SLOT,
        ObjectCentroidWorldPose(2.0, 1.0, 0.0),
        6.0,
        2.5,
    )
    static_world = StaticWorld(
        Bounds2D(-20.0, 20.0, -20.0, 20.0),
        (parked, goal),
        "goal",
    )
    world = WorldState(
        vehicle,
        static_world,
        EgoState(RearAxleWorldPose(-2.0, 0.0, 0.0), 0.0, 0.0),
        static_world.objects,
        SettleProgress(0, 10),
        ActuatorState(PhysicalControl(0.0, 0.0), (ZERO_NORMALIZED_ACTION,), 0),
    )
    return record_episode(
        world,
        (NormalizedAction(0.5, 0.4), NormalizedAction(0.2, -0.3)),
        ReplayProvenance(3, "a" * 64, "b" * 64, "c" * 40),
    )


def test_replay_frames_include_initial_and_every_substep() -> None:
    trace = _trace()
    frames = replay_frames(trace)
    assert len(frames) == 1 + 5 * len(trace.requested_actions)
    assert frames[0].policy_step_index == frames[0].substep_index == 0
    assert frames[0].time_s == 0.0
    assert frames[-1].policy_step_index == 2
    assert frames[-1].substep_index == 5
    assert tuple(frame.time_s for frame in frames) == tuple(
        index * trace.dynamics_config.dt_sub_s for index in range(len(frames))
    )
    assert frames[0].body_corners == obb_corners(
        vehicle_obb(trace.initial_state.ego.pose, trace.initial_state.vehicle)
    )
    assert frames[-1].body_corners == obb_corners(
        vehicle_obb(trace.states[-1].ego.pose, trace.initial_state.vehicle)
    )


def test_replay_frame_freezes_and_validates_corners() -> None:
    trace = _trace()
    source = [list(point) for point in replay_frames(trace)[0].body_corners]
    frame = ReplayFrame(0, 0, 0.0, trace.initial_state.ego.pose, source)  # type: ignore[arg-type]
    source[0][0] = 999.0
    assert frame.body_corners[0][0] != 999.0
    with pytest.raises(ValueError, match="four 2D"):
        ReplayFrame(0, 0, 0.0, trace.initial_state.ego.pose, ((0.0, 0.0),))  # type: ignore[arg-type]


def test_importing_render_does_not_import_matplotlib() -> None:
    script = r"""
import builtins
original = builtins.__import__
def guarded(name, *args, **kwargs):
    if name == "matplotlib" or name.startswith("matplotlib."):
        raise AssertionError("matplotlib imported eagerly")
    return original(name, *args, **kwargs)
builtins.__import__ = guarded
import parking_rl.physics.render
print("ok")
"""
    result = subprocess.run(
        [sys.executable, "-c", script], check=True, capture_output=True, text=True
    )
    assert result.stdout.strip() == "ok"


def test_animate_reports_a_clear_optional_dependency_error(monkeypatch: pytest.MonkeyPatch) -> None:
    original_import = builtins.__import__

    def reject_matplotlib(name: str, *args: object, **kwargs: object) -> object:
        if name == "matplotlib" or name.startswith("matplotlib."):
            raise ModuleNotFoundError("simulated missing matplotlib")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", reject_matplotlib)
    with pytest.raises(RuntimeError, match="optional 'matplotlib'"):
        animate_trajectory(_trace())
