"""Hand-built scenes for the Stage-2 smoke rehearsal.

These scenes are **not** the frozen evaluation set: that set must be filtered by Stage 1's
Hybrid A* and hashed (EXIT-2.1, EXIT-2.2). They exist only to check that the environment
wiring, reward and observation can be learned from at all.

Parallel frame (§5.0(c)): kerb on +y, goal rear axle at the origin with heading 0, so the
parked body occupies ``x in [-r, L+f]`` and ``y in [-w/2, +w/2]``. The traffic lane is -y.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from parking_rl.core.frames import GoalRearAxleWorldPose, ObjectCentroidWorldPose, RearAxleWorldPose
from parking_rl.core.state import (
    Bounds2D,
    EgoState,
    ObjectKind,
    ObjectRole,
    ObjectState,
    StaticWorld,
    VehicleSpec,
)
from parking_rl.physics.geometry import obb_corners, object_obb, sat_overlap, vehicle_obb


def reference_vehicle() -> VehicleSpec:
    return VehicleSpec(2.7, 4.7, 1.85, 0.9, 1.1, 0.6, 0.6, 1.5, 1.5)


@dataclass(frozen=True, slots=True)
class ParallelScene:
    static_world: StaticWorld
    goal: GoalRearAxleWorldPose
    slot_length_m: float


def parallel_scene(
    vehicle: VehicleSpec,
    slot_length_m: float,
    kerb_clearance_m: float = 0.4,
) -> ParallelScene:
    """A slot of ``slot_length_m`` between two parked cars, centred on the goal footprint."""

    if slot_length_m <= vehicle.length_m:
        raise ValueError("slot_length_m must exceed the vehicle length")
    half_width = 0.5 * vehicle.width_m
    body_centre_x = 0.5 * (vehicle.wheelbase_m + vehicle.front_overhang_m - vehicle.rear_overhang_m)
    slot_rear = body_centre_x - 0.5 * slot_length_m
    slot_front = body_centre_x + 0.5 * slot_length_m
    neighbour_length = vehicle.length_m
    kerb_thickness = 0.5
    kerb_inner_y = half_width + kerb_clearance_m

    def box(object_id: str, kind: ObjectKind, role: ObjectRole, x: float, y: float, length: float,
            width: float) -> ObjectState:
        return ObjectState(object_id, kind, role, ObjectCentroidWorldPose(x, y, 0.0), length, width)

    objects = (
        box("rear_car", ObjectKind.VEHICLE, ObjectRole.REAR_VEHICLE,
            slot_rear - 0.5 * neighbour_length, 0.0, neighbour_length, vehicle.width_m),
        box("front_car", ObjectKind.VEHICLE, ObjectRole.FRONT_VEHICLE,
            slot_front + 0.5 * neighbour_length, 0.0, neighbour_length, vehicle.width_m),
        box("kerb", ObjectKind.KERB, ObjectRole.KERB,
            body_centre_x, kerb_inner_y + 0.5 * kerb_thickness, 40.0, kerb_thickness),
        box("goal", ObjectKind.GOAL_SLOT, ObjectRole.GOAL_SLOT,
            body_centre_x, 0.0, slot_length_m, vehicle.width_m),
    )
    bounds = Bounds2D(body_centre_x - 19.0, body_centre_x + 19.0, -6.5, kerb_inner_y + 0.4)
    return ParallelScene(
        static_world=StaticWorld(bounds, objects, "goal"),
        goal=GoalRearAxleWorldPose(0.0, 0.0, 0.0),
        slot_length_m=slot_length_m,
    )


def pose_is_clear(pose: RearAxleWorldPose, scene: ParallelScene, vehicle: VehicleSpec) -> bool:
    """Exact-SAT clearance of a pose against solids and the closed world bounds."""

    ego = vehicle_obb(pose, vehicle)
    for obj in scene.static_world.objects:
        if obj.kind is not ObjectKind.GOAL_SLOT and sat_overlap(ego, object_obb(obj)):
            return False
    bounds = scene.static_world.bounds
    return all(
        bounds.min_x_m < x < bounds.max_x_m and bounds.min_y_m < y < bounds.max_y_m
        for x, y in obb_corners(ego)
    )


def sample_easy_start(
    rng: random.Random, scene: ParallelScene, vehicle: VehicleSpec, max_tries: int = 1000
) -> EgoState:
    """Rejection-sample a collision-free rest pose in the lane beside or just ahead of the slot.

    A stand-in for reverse-curriculum rung 0 until Stage 1 can supply reference paths.
    """

    for _ in range(max_tries):
        pose = RearAxleWorldPose(
            rng.uniform(-0.5, 4.0),
            rng.uniform(-2.6, -0.2),
            rng.uniform(-0.35, 0.35),
        )
        if pose_is_clear(pose, scene, vehicle):
            return EgoState(pose, 0.0, 0.0)
    raise RuntimeError("could not sample a collision-free start pose")


__all__ = [
    "ParallelScene",
    "parallel_scene",
    "pose_is_clear",
    "reference_vehicle",
    "sample_easy_start",
]
