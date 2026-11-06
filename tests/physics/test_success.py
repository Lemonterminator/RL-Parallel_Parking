import math

import pytest

from parking_rl.core.frames import GoalRearAxleWorldPose, RearAxleWorldPose
from parking_rl.core.state import EgoState, SettleProgress, VehicleSpec
from parking_rl.physics.geometry import obb_corners, vehicle_obb
from parking_rl.physics.success import (
    SuccessTolerance,
    advance_settle,
    modulo_pi_heading_match,
    success_candidate,
)


def reference_vehicle() -> VehicleSpec:
    return VehicleSpec(2.7, 4.7, 1.85, 0.9, 1.1, 0.6, 0.6, 1.5, 1.5)


def tolerance() -> SuccessTolerance:
    return SuccessTolerance(0.1, 0.1, 0.05, 0.05, 0.05)


def test_reverse_bay_goal_footprint_has_expected_clearances() -> None:
    pose = RearAxleWorldPose(0.0, -3.9, math.pi / 2)
    corners = obb_corners(vehicle_obb(pose, reference_vehicle()))

    assert min(x for x, _ in corners) == pytest.approx(-0.925, abs=1e-12)
    assert max(x for x, _ in corners) == pytest.approx(0.925, abs=1e-12)
    assert min(y for _, y in corners) == pytest.approx(-5.0, abs=1e-12)
    assert max(y for _, y in corners) == pytest.approx(-0.3, abs=1e-12)


def _footprint_corner_match(pose: RearAxleWorldPose, goal: RearAxleWorldPose, tol_m: float) -> bool:
    """The §5.0(g) footprint two-corner matching EXIT-0.15 forbids; used only as positive control.

    Accepts a pose whose body occupies the goal footprint, in either of the two corner
    correspondences (nose-out or nose-in).
    """

    vehicle = reference_vehicle()
    actual = obb_corners(vehicle_obb(pose, vehicle))
    target = obb_corners(vehicle_obb(goal, vehicle))
    return all(
        min(math.hypot(ax - tx, ay - ty) for tx, ty in target) <= tol_m for ax, ay in actual
    )


def test_success_uses_directed_heading_and_rejects_nose_in() -> None:
    """EXIT-0.15 (v1.6): the same-footprint nose-in pose is (0, -1.40, -pi/2), not (0, -3.90, ...).

    The reference point is the rear axle, so flipping the heading about a fixed rear axle moves
    the body by 2.5 m. The true nose-in pose puts the rear axle where the nose-out front sits.
    """

    goal = GoalRearAxleWorldPose(0.0, -3.9, math.pi / 2)
    goal_pose = RearAxleWorldPose(0.0, -3.9, math.pi / 2)
    nose_out = EgoState(goal_pose, 0.0, 0.0)
    nose_in = EgoState(RearAxleWorldPose(0.0, -1.4, -math.pi / 2), 0.0, 0.0)
    heading_flip_only = EgoState(RearAxleWorldPose(0.0, -3.9, -math.pi / 2), 0.0, 0.0)

    # Same footprint: every nose-in corner coincides with some goal corner (unordered match,
    # because float noise can reorder a sorted corner list).
    assert _footprint_corner_match(nose_in.pose, goal_pose, 1e-12)

    assert success_candidate(nose_out, goal, tolerance())
    assert not success_candidate(nose_in, goal, tolerance())
    # The rejection must come from the heading channel, not the 2.5 m position offset alone.
    assert not success_candidate(heading_flip_only, goal, tolerance())
    assert modulo_pi_heading_match(heading_flip_only.pose, goal, tolerance().heading_rad)

    # Positive control: footprint matching rejects the v1.3 pose (0, -3.90, -pi/2), so that pose
    # could never have shown the directed-heading check doing any work.
    assert not _footprint_corner_match(heading_flip_only.pose, goal_pose, 1e-9)


@pytest.mark.parametrize(
    "ego",
    [
        EgoState(RearAxleWorldPose(0.11, -3.9, math.pi / 2), 0.0, 0.0),
        EgoState(RearAxleWorldPose(0.0, -3.79, math.pi / 2), 0.0, 0.0),
        EgoState(RearAxleWorldPose(0.0, -3.9, math.pi / 2 + 0.06), 0.0, 0.0),
        EgoState(RearAxleWorldPose(0.0, -3.9, math.pi / 2), 0.06, 0.0),
        EgoState(RearAxleWorldPose(0.0, -3.9, math.pi / 2), 0.0, 0.06),
    ],
)
def test_success_checks_every_tolerance_channel(ego: EgoState) -> None:
    assert not success_candidate(ego, GoalRearAxleWorldPose(0.0, -3.9, math.pi / 2), tolerance())


def test_settle_progress_requires_consecutive_candidates_and_caps() -> None:
    progress = SettleProgress(0, 5)
    for expected in (1, 2, 3):
        progress = advance_settle(True, progress)
        assert progress.count == expected
    progress = advance_settle(False, progress)
    assert progress.count == 0
    for _ in range(9):
        progress = advance_settle(True, progress)
    assert progress.count == progress.required_steps == 5
