"""Frame-specific planar poses and the explicit conversions between them."""

from __future__ import annotations

import math
from dataclasses import dataclass
from numbers import Real


def _require_finite(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number, not {type(value).__name__}")
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")


def _require_heading(name: str, value: object) -> None:
    _require_finite(name, value)
    if not -math.pi <= value < math.pi:
        raise ValueError(f"{name} must be within [-pi, pi)")


def _require_exact_type(name: str, value: object, expected: type[object]) -> None:
    if type(value) is not expected:
        raise TypeError(f"{name} must be exactly {expected.__name__}")


def wrap_angle(angle_rad: float) -> float:
    """Wrap a finite angle to the half-open interval ``[-pi, pi)``."""

    _require_finite("angle_rad", angle_rad)
    return (angle_rad + math.pi) % math.tau - math.pi


@dataclass(frozen=True, slots=True)
class RearAxleWorldPose:
    """Ego rear-axle midpoint pose in the world frame."""

    x_m: float
    y_m: float
    heading_rad: float

    def __post_init__(self) -> None:
        _require_finite("x_m", self.x_m)
        _require_finite("y_m", self.y_m)
        _require_heading("heading_rad", self.heading_rad)


@dataclass(frozen=True, slots=True)
class GoalRearAxleWorldPose:
    """Desired rear-axle midpoint pose in the world frame."""

    x_m: float
    y_m: float
    heading_rad: float

    def __post_init__(self) -> None:
        _require_finite("x_m", self.x_m)
        _require_finite("y_m", self.y_m)
        _require_heading("heading_rad", self.heading_rad)


@dataclass(frozen=True, slots=True)
class ObjectCentroidWorldPose:
    """Object-centroid pose in the world frame."""

    x_m: float
    y_m: float
    heading_rad: float

    def __post_init__(self) -> None:
        _require_finite("x_m", self.x_m)
        _require_finite("y_m", self.y_m)
        _require_heading("heading_rad", self.heading_rad)


@dataclass(frozen=True, slots=True)
class ObjectEgoFramePose:
    """Object-centroid pose expressed relative to the ego rear-axle frame."""

    dx_m: float
    dy_m: float
    relative_heading_rad: float

    def __post_init__(self) -> None:
        _require_finite("dx_m", self.dx_m)
        _require_finite("dy_m", self.dy_m)
        _require_heading("relative_heading_rad", self.relative_heading_rad)


@dataclass(frozen=True, slots=True)
class GoalFrameError:
    """Ego rear-axle error expressed in the desired rear-axle frame."""

    longitudinal_m: float
    lateral_m: float
    heading_error_rad: float

    def __post_init__(self) -> None:
        _require_finite("longitudinal_m", self.longitudinal_m)
        _require_finite("lateral_m", self.lateral_m)
        _require_heading("heading_error_rad", self.heading_error_rad)


def object_world_to_ego(
    object_pose: ObjectCentroidWorldPose,
    ego_pose: RearAxleWorldPose,
) -> ObjectEgoFramePose:
    """Express a world-frame object centroid in the ego rear-axle frame."""

    _require_exact_type("object_pose", object_pose, ObjectCentroidWorldPose)
    _require_exact_type("ego_pose", ego_pose, RearAxleWorldPose)
    dx = object_pose.x_m - ego_pose.x_m
    dy = object_pose.y_m - ego_pose.y_m
    cosine = math.cos(ego_pose.heading_rad)
    sine = math.sin(ego_pose.heading_rad)
    return ObjectEgoFramePose(
        dx_m=cosine * dx + sine * dy,
        dy_m=-sine * dx + cosine * dy,
        relative_heading_rad=wrap_angle(object_pose.heading_rad - ego_pose.heading_rad),
    )


def object_ego_to_world(
    object_pose: ObjectEgoFramePose,
    ego_pose: RearAxleWorldPose,
) -> ObjectCentroidWorldPose:
    """Convert an ego-frame object centroid back to the world frame."""

    _require_exact_type("object_pose", object_pose, ObjectEgoFramePose)
    _require_exact_type("ego_pose", ego_pose, RearAxleWorldPose)
    cosine = math.cos(ego_pose.heading_rad)
    sine = math.sin(ego_pose.heading_rad)
    return ObjectCentroidWorldPose(
        x_m=ego_pose.x_m + cosine * object_pose.dx_m - sine * object_pose.dy_m,
        y_m=ego_pose.y_m + sine * object_pose.dx_m + cosine * object_pose.dy_m,
        heading_rad=wrap_angle(ego_pose.heading_rad + object_pose.relative_heading_rad),
    )


def rear_axle_world_to_goal_error(
    ego_pose: RearAxleWorldPose,
    goal_pose: GoalRearAxleWorldPose,
) -> GoalFrameError:
    """Express the ego rear-axle pose as an error in the goal frame."""

    _require_exact_type("ego_pose", ego_pose, RearAxleWorldPose)
    _require_exact_type("goal_pose", goal_pose, GoalRearAxleWorldPose)
    dx = ego_pose.x_m - goal_pose.x_m
    dy = ego_pose.y_m - goal_pose.y_m
    cosine = math.cos(goal_pose.heading_rad)
    sine = math.sin(goal_pose.heading_rad)
    return GoalFrameError(
        longitudinal_m=cosine * dx + sine * dy,
        lateral_m=-sine * dx + cosine * dy,
        heading_error_rad=wrap_angle(ego_pose.heading_rad - goal_pose.heading_rad),
    )


def goal_error_to_rear_axle_world(
    error: GoalFrameError,
    goal_pose: GoalRearAxleWorldPose,
) -> RearAxleWorldPose:
    """Reconstruct a world rear-axle pose from its goal-frame error."""

    _require_exact_type("error", error, GoalFrameError)
    _require_exact_type("goal_pose", goal_pose, GoalRearAxleWorldPose)
    cosine = math.cos(goal_pose.heading_rad)
    sine = math.sin(goal_pose.heading_rad)
    return RearAxleWorldPose(
        x_m=goal_pose.x_m + cosine * error.longitudinal_m - sine * error.lateral_m,
        y_m=goal_pose.y_m + sine * error.longitudinal_m + cosine * error.lateral_m,
        heading_rad=wrap_angle(goal_pose.heading_rad + error.heading_error_rad),
    )
