"""Immutable scenario and frozen-oracle contracts."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from enum import StrEnum
from numbers import Real

from parking_rl.core.fingerprint import canonical_json_bytes, sha256_fingerprint
from parking_rl.core.frames import GoalRearAxleWorldPose
from parking_rl.core.state import EgoState, StaticWorld, VehicleSpec

_SHA256 = re.compile(r"[0-9a-f]{64}")
_GIT_COMMIT = re.compile(r"[0-9a-f]{40}")


def _finite_positive(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")


def _nonnegative_int(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an int")
    if value < 0:
        raise ValueError(f"{name} must be nonnegative")


def _nonempty(name: str, value: object) -> None:
    if type(value) is not str or not value:
        raise ValueError(f"{name} must be a non-empty string")


def _digest(name: str, value: object, pattern: re.Pattern[str]) -> None:
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise ValueError(f"{name} has an invalid lowercase hexadecimal digest")


class TaskFamily(StrEnum):
    """The two task families served by one conditioned policy."""

    PARALLEL = "parallel"
    REVERSE_BAY = "reverse_bay"


@dataclass(frozen=True, slots=True)
class GeneratorProvenance:
    """Inputs needed to identify how a candidate scenario was sampled."""

    seed: int
    sample_index: int
    config_sha256: str
    implementation_commit: str
    generator_version: str

    def __post_init__(self) -> None:
        _nonnegative_int("seed", self.seed)
        _nonnegative_int("sample_index", self.sample_index)
        _digest("config_sha256", self.config_sha256, _SHA256)
        _digest("implementation_commit", self.implementation_commit, _GIT_COMMIT)
        _nonempty("generator_version", self.generator_version)


@dataclass(frozen=True, slots=True)
class ParallelDifficulty:
    """Raw parallel-parking difficulty input."""

    slot_length_m: float

    def __post_init__(self) -> None:
        _finite_positive("slot_length_m", self.slot_length_m)


@dataclass(frozen=True, slots=True)
class BayDifficulty:
    """Raw reverse-bay geometry, including explicit free mouth width ``W_gap``."""

    bay_width_m: float
    bay_depth_m: float
    free_mouth_width_m: float
    aisle_width_m: float
    end_clearance_m: float

    def __post_init__(self) -> None:
        for name in (
            "bay_width_m",
            "bay_depth_m",
            "free_mouth_width_m",
            "aisle_width_m",
            "end_clearance_m",
        ):
            _finite_positive(name, getattr(self, name))


Difficulty = ParallelDifficulty | BayDifficulty


@dataclass(frozen=True, slots=True)
class Scenario:
    """Generator output containing physical truth but no planner oracle annotation."""

    scenario_id: str
    family: TaskFamily
    static_world: StaticWorld
    initial_ego: EgoState
    goal_pose: GoalRearAxleWorldPose
    vehicle: VehicleSpec
    difficulty: Difficulty
    generator: GeneratorProvenance
    max_steps: int
    settle_steps: int
    schema_version: int = 1

    def __post_init__(self) -> None:
        _nonempty("scenario_id", self.scenario_id)
        if type(self.family) is not TaskFamily:
            raise TypeError("family must be exactly TaskFamily")
        expected_difficulty = (
            ParallelDifficulty if self.family is TaskFamily.PARALLEL else BayDifficulty
        )
        if type(self.difficulty) is not expected_difficulty:
            raise TypeError(f"{self.family.value} requires {expected_difficulty.__name__}")
        for name, expected in (
            ("static_world", StaticWorld),
            ("initial_ego", EgoState),
            ("goal_pose", GoalRearAxleWorldPose),
            ("vehicle", VehicleSpec),
            ("generator", GeneratorProvenance),
        ):
            if type(getattr(self, name)) is not expected:
                raise TypeError(f"{name} must be exactly {expected.__name__}")
        _nonnegative_int("max_steps", self.max_steps)
        _nonnegative_int("settle_steps", self.settle_steps)
        _nonnegative_int("schema_version", self.schema_version)
        if self.max_steps == 0 or self.settle_steps == 0 or self.schema_version != 1:
            raise ValueError(
                "max_steps and settle_steps must be positive; schema_version must be 1"
            )

    def canonical_bytes(self) -> bytes:
        """Return stable bytes suitable for frozen-dataset storage."""

        return canonical_json_bytes(self)

    @property
    def sha256(self) -> str:
        """Fingerprint all physical and provenance fields in the scenario."""

        return sha256_fingerprint(self)


class OracleSource(StrEnum):
    """Permitted source for frozen-set oracle path lengths."""

    POST_SMOOTHED_HYBRID_ASTAR = "post_smoothed_hybrid_astar"


@dataclass(frozen=True, slots=True)
class OracleAnnotation:
    """Provenance-rich post-smoothed Hybrid A* oracle annotation."""

    source: OracleSource
    planner_config_sha256: str
    implementation_commit: str
    implementation_version: str
    resolution_m: float
    smoothed_path_sha256: str
    length_m: float
    gear_changes: int

    def __post_init__(self) -> None:
        if self.source is not OracleSource.POST_SMOOTHED_HYBRID_ASTAR:
            raise ValueError("oracle source must be post-smoothed Hybrid A*")
        _digest("planner_config_sha256", self.planner_config_sha256, _SHA256)
        _digest("implementation_commit", self.implementation_commit, _GIT_COMMIT)
        _nonempty("implementation_version", self.implementation_version)
        _finite_positive("resolution_m", self.resolution_m)
        _digest("smoothed_path_sha256", self.smoothed_path_sha256, _SHA256)
        _finite_positive("length_m", self.length_m)
        _nonnegative_int("gear_changes", self.gear_changes)


@dataclass(frozen=True, slots=True)
class FrozenScenarioRecord:
    """A scenario plus the immutable oracle produced by a later workflow."""

    scenario: Scenario
    oracle: OracleAnnotation
    schema_version: int = 1

    def __post_init__(self) -> None:
        if type(self.scenario) is not Scenario or type(self.oracle) is not OracleAnnotation:
            raise TypeError("scenario and oracle must use their exact contract types")
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise ValueError("schema_version must be integer 1")

    @property
    def sha256(self) -> str:
        return sha256_fingerprint(self)
