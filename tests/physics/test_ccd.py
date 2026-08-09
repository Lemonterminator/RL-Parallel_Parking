from __future__ import annotations

import math
from dataclasses import FrozenInstanceError
from itertools import pairwise

import pytest

from parking_rl.core.actions import NormalizedAction, PhysicalControl
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
from parking_rl.physics.ccd import (
    SweepConfig,
    SweepResult,
    bounded_sweep_poses,
    interpolate_pose,
    pose_motion_bound_m,
    sweep_collides,
    world_step_collides,
)
from parking_rl.physics.dynamics import PolicyStepTrace
from parking_rl.physics.geometry import (
    OBB,
    minimum_turn_radius_m,
    sat_overlap,
    vehicle_farthest_corner_m,
    vehicle_obb,
)


def vehicle() -> VehicleSpec:
    return VehicleSpec(
        wheelbase_m=2.7,
        length_m=4.7,
        width_m=1.85,
        front_overhang_m=0.9,
        rear_overhang_m=1.1,
        max_steering_angle_rad=0.6,
        max_steering_rate_radps=0.6,
        max_speed_mps=1.5,
        max_acceleration_mps2=1.5,
    )


def object_state(
    identifier: str,
    kind: ObjectKind,
    role: ObjectRole,
    x_m: float,
    y_m: float,
    *,
    length_m: float = 2.0,
    width_m: float = 2.0,
) -> ObjectState:
    return ObjectState(
        id=identifier,
        kind=kind,
        role=role,
        pose=ObjectCentroidWorldPose(x_m, y_m, 0.0),
        length_m=length_m,
        width_m=width_m,
    )


def world(
    pose: RearAxleWorldPose,
    objects: tuple[ObjectState, ...],
    bounds: Bounds2D | None = None,
) -> WorldState:
    spec = vehicle()
    return WorldState(
        vehicle=spec,
        static_world=StaticWorld(
            bounds=bounds or Bounds2D(-20.0, 20.0, -20.0, 20.0),
            objects=objects,
            goal_object_id="goal",
        ),
        ego=EgoState(pose, 0.0, 0.0),
        objects=objects,
        settle=SettleProgress(0, 10),
        actuator=ActuatorState(PhysicalControl(0.0, 0.0), (), 0),
    )


def trace(poses: tuple[RearAxleWorldPose, ...]) -> PolicyStepTrace:
    assert len(poses) == 5
    zero_action = NormalizedAction(0.0, 0.0)
    return PolicyStepTrace(
        requested_action=zero_action,
        applied_action=zero_action,
        applied_control=PhysicalControl(0.0, 0.0),
        substeps=tuple(EgoState(pose, 0.0, 0.0) for pose in poses),
    )


@pytest.mark.parametrize("bad_value", [True, 0.0, -0.1, math.inf, math.nan])
def test_sweep_config_rejects_nonfinite_or_nonpositive_resolution(bad_value: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        SweepConfig(bad_value)  # type: ignore[arg-type]


def test_full_lock_reference_motion_factor_locks_rotation_term() -> None:
    spec = vehicle()
    d_max = vehicle_farthest_corner_m(spec)
    kappa_max = 1.0 / minimum_turn_radius_m(spec)
    factor = 1.0 + d_max * kappa_max
    distance_m = 0.026
    start = RearAxleWorldPose(0.0, 0.0, 0.0)
    end = RearAxleWorldPose(distance_m, 0.0, distance_m * kappa_max)

    assert d_max == pytest.approx(3.71694, abs=1e-4)
    assert kappa_max == pytest.approx(0.25338, abs=1e-5)
    assert factor == pytest.approx(1.9419, abs=1e-4)
    assert pose_motion_bound_m(start, end, spec) == pytest.approx(distance_m * factor)


def test_interpolation_uses_shortest_wrapped_heading() -> None:
    start = RearAxleWorldPose(0.0, 0.0, math.radians(170.0))
    end = RearAxleWorldPose(2.0, 4.0, math.radians(-170.0))
    midpoint = interpolate_pose(start, end, 0.5)
    assert midpoint.x_m == 1.0
    assert midpoint.y_m == 2.0
    assert midpoint.heading_rad == pytest.approx(-math.pi)


def test_densification_respects_farthest_point_motion_bound() -> None:
    spec = vehicle()
    config = SweepConfig(0.025)
    poses = (
        RearAxleWorldPose(-1.0, 0.5, -0.8),
        RearAxleWorldPose(1.0, 0.25, 0.9),
        RearAxleWorldPose(1.2, 0.4, 1.1),
    )
    samples = bounded_sweep_poses(poses, spec, config)
    interval_bounds = tuple(
        pose_motion_bound_m(start, end, spec)
        for start, end in pairwise(samples)
    )
    assert samples[0] is poses[0]
    assert samples[-1] == poses[-1]
    assert max(interval_bounds) <= config.max_point_motion_m + 1e-12
    assert samples.count(poses[1]) == 1


def test_rotational_tunnelling_through_thin_wall_is_detected() -> None:
    spec = vehicle()
    start = RearAxleWorldPose(0.0, 0.0, -math.pi / 4.0)
    end = RearAxleWorldPose(0.0, 0.0, math.pi / 4.0)
    thin_wall = OBB(3.6275, 0.0, math.pi / 2.0, 0.5, 0.055)

    assert start.heading_rad != end.heading_rad
    assert not sat_overlap(vehicle_obb(start, spec), thin_wall)
    assert not sat_overlap(vehicle_obb(end, spec), thin_wall)
    result = sweep_collides((start, end), spec, (thin_wall,), SweepConfig(0.025))
    assert result.collides
    assert result.first_collision_pose is not None
    assert result.first_collision_pose.heading_rad != pytest.approx(start.heading_rad)
    assert result.first_collision_pose.heading_rad != pytest.approx(end.heading_rad)
    assert result.max_interval_motion_bound_m <= 0.025 + 1e-12


def test_perpendicular_translational_tunnelling_is_detected() -> None:
    spec = vehicle()
    start = RearAxleWorldPose(-5.0, 0.0, 0.0)
    end = RearAxleWorldPose(5.0, 0.0, 0.0)
    thin_wall = OBB(0.0, 0.0, math.pi / 2.0, 4.0, 0.055)
    assert not sat_overlap(vehicle_obb(start, spec), thin_wall)
    assert not sat_overlap(vehicle_obb(end, spec), thin_wall)
    assert sweep_collides((start, end), spec, (thin_wall,)).collides


def test_safe_sweep_reports_every_sample_checked() -> None:
    spec = vehicle()
    poses = (
        RearAxleWorldPose(0.0, 0.0, 0.0),
        RearAxleWorldPose(0.5, 0.0, 0.0),
    )
    samples = bounded_sweep_poses(poses, spec)
    result = sweep_collides(poses, spec, (OBB(0.0, 10.0, 0.0, 1.0, 1.0),))
    assert result == SweepResult(False, len(samples), None, result.max_interval_motion_bound_m)


def test_world_sweep_ignores_goal_slot_even_when_overlapping() -> None:
    goal = object_state(
        "goal",
        ObjectKind.GOAL_SLOT,
        ObjectRole.GOAL_SLOT,
        1.25,
        0.0,
        length_m=4.7,
        width_m=1.85,
    )
    initial = RearAxleWorldPose(0.0, 0.0, 0.0)
    state = world(initial, (goal,))
    result = world_step_collides(state, trace((initial,) * 5))
    assert not result.collides


def test_world_sweep_detects_closed_boundary_between_trace_states() -> None:
    goal = object_state("goal", ObjectKind.GOAL_SLOT, ObjectRole.GOAL_SLOT, 10.0, 10.0)
    initial = RearAxleWorldPose(0.0, 0.0, 0.0)
    state = world(initial, (goal,), Bounds2D(-2.0, 5.0, -2.0, 2.0))
    poses = tuple(RearAxleWorldPose(0.3 * index, 0.0, 0.0) for index in range(1, 6))
    result = world_step_collides(state, trace(poses))
    assert result.collides
    assert result.first_collision_pose is not None
    assert result.max_interval_motion_bound_m <= SweepConfig().max_point_motion_m + 1e-12


def test_sweep_result_is_frozen_and_self_consistent() -> None:
    pose = RearAxleWorldPose(0.0, 0.0, 0.0)
    result = SweepResult(False, 1, None, 0.0)
    with pytest.raises(FrozenInstanceError):
        result.samples_checked = 2  # type: ignore[misc]
    with pytest.raises(ValueError, match="agree"):
        SweepResult(True, 1, None, 0.0)
    with pytest.raises(TypeError, match="bool"):
        SweepResult(1, 1, pose, 0.0)  # type: ignore[arg-type]


def test_sweep_rejects_mutable_or_mistyped_inputs() -> None:
    spec = vehicle()
    pose = RearAxleWorldPose(0.0, 0.0, 0.0)
    with pytest.raises(TypeError, match="poses must be exactly tuple"):
        bounded_sweep_poses([pose], spec)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="RearAxleWorldPose"):
        bounded_sweep_poses((object(),), spec)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="obstacles must be exactly tuple"):
        sweep_collides((pose,), spec, [])  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="OBB"):
        sweep_collides((pose,), spec, (object(),))  # type: ignore[arg-type]
    with pytest.raises((TypeError, ValueError)):
        interpolate_pose(pose, pose, math.nan)
