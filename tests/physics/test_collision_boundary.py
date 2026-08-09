from __future__ import annotations

import ast
from pathlib import Path

from parking_rl.core.actions import PhysicalControl
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
from parking_rl.physics.collision import solid_obstacles, state_collides


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
    ego_pose: RearAxleWorldPose,
    objects: tuple[ObjectState, ...],
    bounds: Bounds2D | None = None,
) -> WorldState:
    spec = vehicle()
    bounds = bounds or Bounds2D(-10.0, 10.0, -10.0, 10.0)
    static = StaticWorld(bounds=bounds, objects=objects, goal_object_id="goal")
    return WorldState(
        vehicle=spec,
        static_world=static,
        ego=EgoState(ego_pose, 0.0, 0.0),
        objects=objects,
        settle=SettleProgress(0, 10),
        actuator=ActuatorState(PhysicalControl(0.0, 0.0), (), 0),
    )


def test_goal_slot_is_not_a_solid_obstacle() -> None:
    goal = object_state("goal", ObjectKind.GOAL_SLOT, ObjectRole.GOAL_SLOT, 1.25, 0.0, length_m=4.7)
    state = world(RearAxleWorldPose(0.0, 0.0, 0.0), (goal,))
    assert solid_obstacles(state.objects) == ()
    assert not state_collides(state)


def test_exact_obb_contact_with_a_vehicle_is_collision() -> None:
    goal = object_state("goal", ObjectKind.GOAL_SLOT, ObjectRole.GOAL_SLOT, 7.0, 0.0)
    obstacle = object_state("front", ObjectKind.VEHICLE, ObjectRole.FRONT_VEHICLE, 4.6, 0.0)
    state = world(RearAxleWorldPose(0.0, 0.0, 0.0), (goal, obstacle))
    assert state_collides(state)


def test_touching_the_closed_world_boundary_is_collision() -> None:
    goal = object_state("goal", ObjectKind.GOAL_SLOT, ObjectRole.GOAL_SLOT, 7.0, 0.0)
    bounds = Bounds2D(-1.1, 10.0, -10.0, 10.0)
    state = world(RearAxleWorldPose(0.0, 0.0, 0.0), (goal,), bounds)
    assert state_collides(state)


def test_a_strictly_in_bounds_footprint_is_not_collision() -> None:
    goal = object_state("goal", ObjectKind.GOAL_SLOT, ObjectRole.GOAL_SLOT, 7.0, 0.0)
    state = world(RearAxleWorldPose(0.0, 0.0, 0.0), (goal,))
    assert not state_collides(state)


def test_collision_termination_path_cannot_import_reward_geometry() -> None:
    collision_path = Path(__file__).parents[2] / "src" / "parking_rl" / "physics" / "collision.py"
    module = ast.parse(collision_path.read_text(encoding="utf-8"))
    imported_modules = {
        node.module
        for node in ast.walk(module)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    imported_modules.update(
        alias.name
        for node in ast.walk(module)
        if isinstance(node, ast.Import)
        for alias in node.names
    )
    assert imported_modules <= {
        "__future__",
        "parking_rl.core.state",
        "parking_rl.physics.geometry",
    }
    assert not any(
        "reward_geometry" in module_name or "circles" in module_name
        for module_name in imported_modules
    )
