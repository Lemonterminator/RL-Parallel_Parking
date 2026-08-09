"""Collision predicates built exclusively on exact physics geometry."""

from __future__ import annotations

from parking_rl.core.state import ObjectKind, ObjectState, WorldState
from parking_rl.physics.geometry import obb_corners, object_obb, sat_overlap, vehicle_obb


def solid_obstacles(objects: tuple[ObjectState, ...]) -> tuple[ObjectState, ...]:
    """Filter non-solid semantic goal markers from physical obstacles."""

    return tuple(obj for obj in objects if obj.kind is not ObjectKind.GOAL_SLOT)


def state_collides(state: WorldState) -> bool:
    """Return whether the ego touches an obstacle or the closed world boundary."""

    if type(state) is not WorldState:
        raise TypeError("state must be exactly WorldState")
    ego_box = vehicle_obb(state.ego.pose, state.vehicle)
    if any(sat_overlap(ego_box, object_obb(obj)) for obj in solid_obstacles(state.objects)):
        return True
    bounds = state.static_world.bounds
    return any(
        x <= bounds.min_x_m or x >= bounds.max_x_m or y <= bounds.min_y_m or y >= bounds.max_y_m
        for x, y in obb_corners(ego_box)
    )
