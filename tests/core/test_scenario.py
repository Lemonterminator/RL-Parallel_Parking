import dataclasses
import subprocess
import sys

import pytest

from parking_rl.core.fingerprint import FingerprintError, sha256_fingerprint
from parking_rl.core.frames import (
    GoalRearAxleWorldPose,
    ObjectCentroidWorldPose,
    RearAxleWorldPose,
)
from parking_rl.core.scenario import (
    BayDifficulty,
    FrozenScenarioRecord,
    GeneratorProvenance,
    OracleAnnotation,
    OracleSource,
    ParallelDifficulty,
    Scenario,
    TaskFamily,
)
from parking_rl.core.state import (
    Bounds2D,
    EgoState,
    ObjectKind,
    ObjectRole,
    ObjectState,
    StaticWorld,
    VehicleSpec,
)


def _vehicle() -> VehicleSpec:
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
        max_latency_steps=2,
    )


def _world() -> StaticWorld:
    objects = (
        ObjectState(
            "front",
            ObjectKind.VEHICLE,
            ObjectRole.FRONT_VEHICLE,
            ObjectCentroidWorldPose(3.0, 0.0, 0.0),
            4.7,
            1.85,
        ),
        ObjectState(
            "rear",
            ObjectKind.VEHICLE,
            ObjectRole.REAR_VEHICLE,
            ObjectCentroidWorldPose(-3.0, 0.0, 0.0),
            4.7,
            1.85,
        ),
        ObjectState(
            "kerb",
            ObjectKind.KERB,
            ObjectRole.KERB,
            ObjectCentroidWorldPose(0.0, -2.0, 0.0),
            20.0,
            0.2,
        ),
        ObjectState(
            "goal",
            ObjectKind.GOAL_SLOT,
            ObjectRole.GOAL_SLOT,
            ObjectCentroidWorldPose(0.0, 0.0, 0.0),
            5.5,
            2.5,
        ),
    )
    return StaticWorld(Bounds2D(-20.0, 20.0, -10.0, 10.0), objects, "goal")


def _generator() -> GeneratorProvenance:
    return GeneratorProvenance(7, 12, "a" * 64, "b" * 40, "generator-v1")


def _scenario(*, free_mouth_width_m: float = 2.5) -> Scenario:
    return Scenario(
        scenario_id="bay-000012",
        family=TaskFamily.REVERSE_BAY,
        static_world=_world(),
        initial_ego=EgoState(RearAxleWorldPose(0.0, 3.0, -1.5707963267948966), 0.0, 0.0),
        goal_pose=GoalRearAxleWorldPose(0.0, -3.9, 1.5707963267948966),
        vehicle=_vehicle(),
        difficulty=BayDifficulty(2.5, 5.3, free_mouth_width_m, 6.0, 0.3),
        generator=_generator(),
        max_steps=400,
        settle_steps=5,
    )


def _oracle(**changes: object) -> OracleAnnotation:
    values = {
        "source": OracleSource.POST_SMOOTHED_HYBRID_ASTAR,
        "planner_config_sha256": "c" * 64,
        "implementation_commit": "d" * 40,
        "implementation_version": "hybrid-astar-v1",
        "resolution_m": 0.1,
        "smoothed_path_sha256": "e" * 64,
        "length_m": 9.25,
        "gear_changes": 1,
    }
    values.update(changes)
    return OracleAnnotation(**values)


def test_scenario_is_separate_from_oracle_and_deeply_immutable():
    scenario = _scenario()
    assert not hasattr(scenario, "oracle")
    assert isinstance(scenario.static_world.objects, tuple)
    with pytest.raises(dataclasses.FrozenInstanceError):
        scenario.max_steps = 10

    record = FrozenScenarioRecord(scenario, _oracle())
    assert record.scenario is scenario
    assert record.oracle.source is OracleSource.POST_SMOOTHED_HYBRID_ASTAR


def test_w_gap_is_required_and_changes_scenario_hash():
    with pytest.raises(TypeError):
        BayDifficulty(bay_width_m=2.5, bay_depth_m=5.3, aisle_width_m=6.0, end_clearance_m=0.3)
    assert "eta_bay" not in {field.name for field in dataclasses.fields(BayDifficulty)}
    assert _scenario(free_mouth_width_m=2.5).sha256 != _scenario(free_mouth_width_m=2.6).sha256


def test_family_requires_its_own_difficulty_type():
    with pytest.raises(TypeError, match="ParallelDifficulty"):
        dataclasses.replace(
            _scenario(),
            family=TaskFamily.PARALLEL,
            difficulty=BayDifficulty(2.5, 5.3, 2.5, 6.0, 0.3),
        )
    parallel = dataclasses.replace(
        _scenario(), family=TaskFamily.PARALLEL, difficulty=ParallelDifficulty(5.5)
    )
    assert parallel.family is TaskFamily.PARALLEL


@pytest.mark.parametrize(
    ("changes", "match"),
    [
        ({"source": "post_smoothed_hybrid_astar"}, "source"),
        ({"planner_config_sha256": "x" * 64}, "digest"),
        ({"implementation_commit": "a" * 39}, "digest"),
        ({"resolution_m": float("nan")}, "finite"),
        ({"length_m": 0.0}, "positive"),
        ({"smoothed_path_sha256": "A" * 64}, "digest"),
    ],
)
def test_oracle_rejects_ambiguous_or_invalid_provenance(changes, match):
    with pytest.raises((TypeError, ValueError), match=match):
        _oracle(**changes)


def test_fingerprint_rejects_non_finite_values_and_is_cross_process_stable():
    with pytest.raises(FingerprintError, match="finite"):
        sha256_fingerprint({"value": float("inf")})
    local = sha256_fingerprint({"family": "reverse_bay", "values": (1, 2.5, True)})
    code = (
        "from parking_rl.core.fingerprint import sha256_fingerprint;"
        "print(sha256_fingerprint({'family':'reverse_bay','values':(1,2.5,True)}))"
    )
    remote = subprocess.check_output([sys.executable, "-c", code], text=True).strip()
    assert remote == local
