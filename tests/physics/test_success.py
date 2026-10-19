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


def test_success_uses_directed_heading_and_rejects_nose_in() -> None:
    goal = GoalRearAxleWorldPose(0.0, -3.9, math.pi / 2)
    nose_out = EgoState(RearAxleWorldPose(0.0, -3.9, math.pi / 2), 0.0, 0.0)
    nose_in = EgoState(RearAxleWorldPose(0.0, -3.9, -math.pi / 2), 0.0, 0.0)

    assert success_candidate(nose_out, goal, tolerance())
    assert not success_candidate(nose_in, goal, tolerance())
    assert modulo_pi_heading_match(nose_in.pose, goal, tolerance().heading_rad)


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
