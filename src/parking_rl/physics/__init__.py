"""Deterministic physics primitives for the parking simulator."""

from parking_rl.physics.action_scaling import scale_action
from parking_rl.physics.collision import solid_obstacles, state_collides
from parking_rl.physics.dynamics import (
    DynamicsConfig,
    PolicyStepTrace,
    advance_actuator,
    clamp_control,
    integrate_substep,
    step_world_state,
)
from parking_rl.physics.geometry import (
    OBB,
    Point2,
    minimum_turn_radius_m,
    obb_corners,
    obb_signed_distance,
    object_obb,
    sat_face_normal_gap,
    sat_overlap,
    sat_penetration_depth,
    vehicle_farthest_corner_m,
    vehicle_front_extent_m,
    vehicle_obb,
)

__all__ = [
    "OBB",
    "DynamicsConfig",
    "Point2",
    "PolicyStepTrace",
    "advance_actuator",
    "clamp_control",
    "integrate_substep",
    "minimum_turn_radius_m",
    "obb_corners",
    "obb_signed_distance",
    "object_obb",
    "sat_face_normal_gap",
    "sat_overlap",
    "sat_penetration_depth",
    "scale_action",
    "solid_obstacles",
    "state_collides",
    "step_world_state",
    "vehicle_farthest_corner_m",
    "vehicle_front_extent_m",
    "vehicle_obb",
]
