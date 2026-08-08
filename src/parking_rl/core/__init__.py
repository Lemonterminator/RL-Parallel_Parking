"""Stable, dependency-free contracts shared by parking subsystems."""

from parking_rl.core.actions import (
    ZERO_NORMALIZED_ACTION,
    NormalizedAction,
    PhysicalControl,
)
from parking_rl.core.frames import (
    GoalFrameError,
    GoalRearAxleWorldPose,
    ObjectCentroidWorldPose,
    ObjectEgoFramePose,
    RearAxleWorldPose,
    goal_error_to_rear_axle_world,
    object_ego_to_world,
    object_world_to_ego,
    rear_axle_world_to_goal_error,
    wrap_angle,
)
from parking_rl.core.outcomes import EpisodeEndReason, StepBoundary, resolve_end_reason
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

__all__ = [
    "ZERO_NORMALIZED_ACTION",
    "ActuatorState",
    "Bounds2D",
    "EgoState",
    "EpisodeEndReason",
    "GoalFrameError",
    "GoalRearAxleWorldPose",
    "NormalizedAction",
    "ObjectCentroidWorldPose",
    "ObjectEgoFramePose",
    "ObjectKind",
    "ObjectRole",
    "ObjectState",
    "PhysicalControl",
    "RearAxleWorldPose",
    "SettleProgress",
    "StaticWorld",
    "StepBoundary",
    "VehicleSpec",
    "WorldState",
    "goal_error_to_rear_axle_world",
    "object_ego_to_world",
    "object_world_to_ego",
    "rear_axle_world_to_goal_error",
    "resolve_end_reason",
    "wrap_angle",
]
