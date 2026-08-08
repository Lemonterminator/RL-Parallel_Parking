import math

import pytest

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


def test_heading_interval_is_half_open() -> None:
    assert RearAxleWorldPose(0.0, 0.0, -math.pi).heading_rad == -math.pi

    with pytest.raises(ValueError, match=r"\[-pi, pi\)"):
        RearAxleWorldPose(0.0, 0.0, math.pi)


@pytest.mark.parametrize("value", [True, math.nan, math.inf, -math.inf])
def test_pose_rejects_invalid_numeric_values(value: float) -> None:
    error = TypeError if isinstance(value, bool) else ValueError

    with pytest.raises(error):
        ObjectCentroidWorldPose(value, 0.0, 0.0)


def test_wrap_angle_uses_canonical_interval() -> None:
    assert wrap_angle(math.pi) == -math.pi
    assert wrap_angle(3.0 * math.pi) == -math.pi
    assert wrap_angle(-3.0 * math.pi) == -math.pi

    with pytest.raises(TypeError):
        wrap_angle(True)


def test_object_frame_conversion_round_trips() -> None:
    ego = RearAxleWorldPose(x_m=3.0, y_m=-2.0, heading_rad=0.7)
    world_object = ObjectCentroidWorldPose(x_m=-1.2, y_m=4.5, heading_rad=-2.7)

    ego_object = object_world_to_ego(world_object, ego)
    reconstructed = object_ego_to_world(ego_object, ego)

    assert reconstructed.x_m == pytest.approx(world_object.x_m)
    assert reconstructed.y_m == pytest.approx(world_object.y_m)
    assert reconstructed.heading_rad == pytest.approx(world_object.heading_rad)


def test_goal_frame_conversion_round_trips() -> None:
    ego = RearAxleWorldPose(x_m=-3.1, y_m=5.4, heading_rad=2.7)
    goal = GoalRearAxleWorldPose(x_m=1.0, y_m=-0.5, heading_rad=-2.9)

    error = rear_axle_world_to_goal_error(ego, goal)
    reconstructed = goal_error_to_rear_axle_world(error, goal)

    assert reconstructed.x_m == pytest.approx(ego.x_m)
    assert reconstructed.y_m == pytest.approx(ego.y_m)
    assert reconstructed.heading_rad == pytest.approx(ego.heading_rad)


def test_frame_conversion_rejects_structurally_similar_wrong_types() -> None:
    ego = RearAxleWorldPose(0.0, 0.0, 0.0)
    goal = GoalRearAxleWorldPose(0.0, 0.0, 0.0)
    world_object = ObjectCentroidWorldPose(0.0, 0.0, 0.0)
    ego_object = ObjectEgoFramePose(0.0, 0.0, 0.0)
    error = GoalFrameError(0.0, 0.0, 0.0)

    with pytest.raises(TypeError, match="ObjectCentroidWorldPose"):
        object_world_to_ego(goal, ego)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="RearAxleWorldPose"):
        object_world_to_ego(world_object, goal)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="ObjectEgoFramePose"):
        object_ego_to_world(world_object, ego)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="RearAxleWorldPose"):
        rear_axle_world_to_goal_error(goal, goal)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="GoalRearAxleWorldPose"):
        rear_axle_world_to_goal_error(ego, ego)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="GoalFrameError"):
        goal_error_to_rear_axle_world(ego_object, goal)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="GoalRearAxleWorldPose"):
        goal_error_to_rear_axle_world(error, ego)  # type: ignore[arg-type]
