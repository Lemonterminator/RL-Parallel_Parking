"""Goal-frame terminal-success and settle-window contracts."""

from __future__ import annotations

import math
from dataclasses import dataclass
from numbers import Real

from parking_rl.core.frames import (
    GoalRearAxleWorldPose,
    RearAxleWorldPose,
    rear_axle_world_to_goal_error,
)
from parking_rl.core.state import EgoState, SettleProgress


def _positive(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and positive")


@dataclass(frozen=True, slots=True)
class SuccessTolerance:
    longitudinal_m: float
    lateral_m: float
    heading_rad: float
    speed_mps: float
    steering_rad: float

    def __post_init__(self) -> None:
        for field in (
            "longitudinal_m",
            "lateral_m",
            "heading_rad",
            "speed_mps",
            "steering_rad",
        ):
            _positive(field, getattr(self, field))


def success_candidate(
    ego: EgoState,
    goal: GoalRearAxleWorldPose,
    tolerance: SuccessTolerance,
) -> bool:
    """Check directed rear-axle pose, speed, and steering tolerances."""

    if type(ego) is not EgoState:
        raise TypeError("ego must be exactly EgoState")
    if type(goal) is not GoalRearAxleWorldPose:
        raise TypeError("goal must be exactly GoalRearAxleWorldPose")
    if type(tolerance) is not SuccessTolerance:
        raise TypeError("tolerance must be exactly SuccessTolerance")
    error = rear_axle_world_to_goal_error(ego.pose, goal)
    return (
        abs(error.longitudinal_m) <= tolerance.longitudinal_m
        and abs(error.lateral_m) <= tolerance.lateral_m
        and abs(error.heading_error_rad) <= tolerance.heading_rad
        and abs(ego.speed_mps) <= tolerance.speed_mps
        and abs(ego.steering_rad) <= tolerance.steering_rad
    )


def advance_settle(candidate: bool, progress: SettleProgress) -> SettleProgress:
    """Advance a consecutive-success counter, resetting immediately on failure."""

    if type(candidate) is not bool:
        raise TypeError("candidate must be exactly bool")
    if type(progress) is not SettleProgress:
        raise TypeError("progress must be exactly SettleProgress")
    count = min(progress.required_steps, progress.count + 1) if candidate else 0
    return SettleProgress(count=count, required_steps=progress.required_steps)


def modulo_pi_heading_match(
    pose: RearAxleWorldPose,
    goal: GoalRearAxleWorldPose,
    heading_tolerance_rad: float,
) -> bool:
    """Diagnostic two-corner matching; never use for reverse-bay success."""

    _positive("heading_tolerance_rad", heading_tolerance_rad)
    error = abs(rear_axle_world_to_goal_error(pose, goal).heading_error_rad)
    return min(error, abs(math.pi - error)) <= heading_tolerance_rad
