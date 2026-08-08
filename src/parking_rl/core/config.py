"""Strict, versioned parser for the resolved reference configuration."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from parking_rl.core.frames import GoalRearAxleWorldPose
from parking_rl.core.observation import ObservationLayout
from parking_rl.core.scenario import BayDifficulty, TaskFamily
from parking_rl.core.state import ObjectRole, VehicleSpec


class ConfigSchemaError(ValueError):
    """Raised when resolved configuration violates the versioned schema."""


@dataclass(frozen=True, slots=True)
class ProjectConfig:
    task_families: tuple[TaskFamily, ...]
    single_scenario_conditioned_policy: bool


@dataclass(frozen=True, slots=True)
class IntegrationConfig:
    action_hold: str
    dt_policy_s: float
    max_steps: int
    scheme: str
    substeps: int


@dataclass(frozen=True, slots=True)
class LearningConfig:
    algorithm: str
    discount: float


@dataclass(frozen=True, slots=True)
class EvaluationConfig:
    infeasible_control_count: int
    test_evaluation_budget: int
    test_per_family: int
    validation_per_family: int


@dataclass(frozen=True, slots=True)
class TaskConfig:
    settle_policy_steps: int
    terminal_priority: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ReverseBayReference:
    difficulty: BayDifficulty
    goal_rear_axle_pose: GoalRearAxleWorldPose


@dataclass(frozen=True, slots=True)
class ReferenceConfig:
    schema_version: int
    project: ProjectConfig
    integration: IntegrationConfig
    learning: LearningConfig
    evaluation: EvaluationConfig
    task: TaskConfig
    vehicle: VehicleSpec
    reverse_bay_reference: ReverseBayReference
    observation_layout: ObservationLayout


def _reject_constant(value: str) -> None:
    raise ConfigSchemaError(f"non-finite JSON number is forbidden: {value}")


def _object(value: object, path: str) -> dict[str, Any]:
    if type(value) is not dict:
        raise ConfigSchemaError(f"{path} must be an object")
    return value


def _exact_keys(value: dict[str, Any], required: set[str], path: str) -> None:
    missing = required - value.keys()
    unknown = value.keys() - required
    if missing or unknown:
        details = []
        if missing:
            details.append(f"missing {sorted(missing)}")
        if unknown:
            details.append(f"unknown {sorted(unknown)}")
        raise ConfigSchemaError(f"{path} has " + " and ".join(details))


def _string(value: object, path: str) -> str:
    if type(value) is not str or not value:
        raise ConfigSchemaError(f"{path} must be a non-empty string")
    return value


def _bool(value: object, path: str) -> bool:
    if type(value) is not bool:
        raise ConfigSchemaError(f"{path} must be bool")
    return value


def _integer(value: object, path: str, *, positive: bool = True) -> int:
    if type(value) is not int:
        raise ConfigSchemaError(f"{path} must be an integer (bool is not accepted)")
    if (positive and value <= 0) or (not positive and value < 0):
        qualifier = "positive" if positive else "nonnegative"
        raise ConfigSchemaError(f"{path} must be {qualifier}")
    return value


def _number(value: object, path: str, *, positive: bool = False) -> float:
    if type(value) not in {int, float}:
        raise ConfigSchemaError(f"{path} must be a number (bool is not accepted)")
    result = float(value)
    if not math.isfinite(result):
        raise ConfigSchemaError(f"{path} must be finite")
    if positive and result <= 0:
        raise ConfigSchemaError(f"{path} must be positive")
    return result


def _sequence(value: object, path: str) -> list[Any]:
    if type(value) is not list:
        raise ConfigSchemaError(f"{path} must be an array")
    return value


def _parse_reference(data: object) -> ReferenceConfig:
    root = _object(data, "config")
    _exact_keys(
        root,
        {
            "schema_version",
            "project",
            "integration",
            "learning",
            "evaluation",
            "task",
            "vehicle",
            "reverse_bay_reference",
            "observation",
        },
        "config",
    )
    schema_version = _integer(root["schema_version"], "schema_version")
    if schema_version != 1:
        raise ConfigSchemaError("schema_version must be 1")

    project_data = _object(root["project"], "project")
    _exact_keys(
        project_data,
        {"task_families", "single_scenario_conditioned_policy"},
        "project",
    )
    family_values = _sequence(project_data["task_families"], "project.task_families")
    try:
        families = tuple(
            TaskFamily(_string(item, "project.task_families[]")) for item in family_values
        )
    except ValueError as error:
        raise ConfigSchemaError("project.task_families contains an invalid family") from error
    if families != (TaskFamily.PARALLEL, TaskFamily.REVERSE_BAY):
        raise ConfigSchemaError("project.task_families must contain parallel then reverse_bay")
    single_policy = _bool(
        project_data["single_scenario_conditioned_policy"],
        "project.single_scenario_conditioned_policy",
    )
    if not single_policy:
        raise ConfigSchemaError("single_scenario_conditioned_policy must be true")
    project = ProjectConfig(families, single_policy)

    integration_data = _object(root["integration"], "integration")
    _exact_keys(
        integration_data,
        {"action_hold", "dt_policy_s", "max_steps", "scheme", "substeps"},
        "integration",
    )
    integration = IntegrationConfig(
        action_hold=_string(integration_data["action_hold"], "integration.action_hold"),
        dt_policy_s=_number(
            integration_data["dt_policy_s"], "integration.dt_policy_s", positive=True
        ),
        max_steps=_integer(integration_data["max_steps"], "integration.max_steps"),
        scheme=_string(integration_data["scheme"], "integration.scheme"),
        substeps=_integer(integration_data["substeps"], "integration.substeps"),
    )
    if (integration.scheme, integration.action_hold, integration.substeps) != (
        "explicit_euler",
        "zero_order",
        5,
    ):
        raise ConfigSchemaError("integration must use explicit_euler, zero_order, and 5 substeps")

    learning_data = _object(root["learning"], "learning")
    _exact_keys(learning_data, {"algorithm", "discount"}, "learning")
    learning = LearningConfig(
        algorithm=_string(learning_data["algorithm"], "learning.algorithm"),
        discount=_number(learning_data["discount"], "learning.discount"),
    )
    if learning.algorithm != "SAC" or not 0 < learning.discount < 1:
        raise ConfigSchemaError("learning must use SAC with discount in (0, 1)")

    evaluation_data = _object(root["evaluation"], "evaluation")
    evaluation_keys = {
        "infeasible_control_count",
        "test_evaluation_budget",
        "test_per_family",
        "validation_per_family",
    }
    _exact_keys(evaluation_data, evaluation_keys, "evaluation")
    evaluation = EvaluationConfig(
        **{key: _integer(evaluation_data[key], f"evaluation.{key}") for key in evaluation_keys}
    )
    if evaluation.test_evaluation_budget > 3:
        raise ConfigSchemaError("evaluation.test_evaluation_budget must not exceed 3")

    task_data = _object(root["task"], "task")
    _exact_keys(task_data, {"settle_policy_steps", "terminal_priority"}, "task")
    priority_values = _sequence(task_data["terminal_priority"], "task.terminal_priority")
    priority = tuple(_string(item, "task.terminal_priority[]") for item in priority_values)
    if priority != ("collision", "out_of_bounds", "success", "timeout"):
        raise ConfigSchemaError("task.terminal_priority does not match the safety-first contract")
    task = TaskConfig(
        settle_policy_steps=_integer(task_data["settle_policy_steps"], "task.settle_policy_steps"),
        terminal_priority=priority,
    )

    vehicle_data = _object(root["vehicle"], "vehicle")
    vehicle_keys = {
        "wheelbase_m",
        "length_m",
        "width_m",
        "front_overhang_m",
        "rear_overhang_m",
        "steering_limit_rad",
        "steering_rate_limit_radps",
        "speed_limit_mps",
        "acceleration_limit_mps2",
        "steering_gain",
        "steering_offset_rad",
        "latency_steps",
        "max_latency_steps",
    }
    _exact_keys(vehicle_data, vehicle_keys, "vehicle")
    try:
        vehicle = VehicleSpec(
            wheelbase_m=_number(vehicle_data["wheelbase_m"], "vehicle.wheelbase_m", positive=True),
            length_m=_number(vehicle_data["length_m"], "vehicle.length_m", positive=True),
            width_m=_number(vehicle_data["width_m"], "vehicle.width_m", positive=True),
            front_overhang_m=_number(
                vehicle_data["front_overhang_m"], "vehicle.front_overhang_m", positive=True
            ),
            rear_overhang_m=_number(
                vehicle_data["rear_overhang_m"], "vehicle.rear_overhang_m", positive=True
            ),
            max_steering_angle_rad=_number(
                vehicle_data["steering_limit_rad"], "vehicle.steering_limit_rad", positive=True
            ),
            max_steering_rate_radps=_number(
                vehicle_data["steering_rate_limit_radps"],
                "vehicle.steering_rate_limit_radps",
                positive=True,
            ),
            max_speed_mps=_number(
                vehicle_data["speed_limit_mps"], "vehicle.speed_limit_mps", positive=True
            ),
            max_acceleration_mps2=_number(
                vehicle_data["acceleration_limit_mps2"],
                "vehicle.acceleration_limit_mps2",
                positive=True,
            ),
            steering_gain=_number(
                vehicle_data["steering_gain"], "vehicle.steering_gain", positive=True
            ),
            steering_offset_rad=_number(
                vehicle_data["steering_offset_rad"], "vehicle.steering_offset_rad"
            ),
            latency_steps=_integer(
                vehicle_data["latency_steps"], "vehicle.latency_steps", positive=False
            ),
            max_latency_steps=_integer(
                vehicle_data["max_latency_steps"], "vehicle.max_latency_steps", positive=False
            ),
        )
    except (TypeError, ValueError) as error:
        raise ConfigSchemaError(f"vehicle violates its physical contract: {error}") from error

    bay_data = _object(root["reverse_bay_reference"], "reverse_bay_reference")
    bay_keys = {
        "aisle_width_m",
        "bay_depth_m",
        "bay_width_m",
        "end_clearance_m",
        "free_mouth_width_m",
        "goal_rear_axle_pose",
    }
    _exact_keys(bay_data, bay_keys, "reverse_bay_reference")
    difficulty = BayDifficulty(
        bay_width_m=_number(
            bay_data["bay_width_m"], "reverse_bay_reference.bay_width_m", positive=True
        ),
        bay_depth_m=_number(
            bay_data["bay_depth_m"], "reverse_bay_reference.bay_depth_m", positive=True
        ),
        free_mouth_width_m=_number(
            bay_data["free_mouth_width_m"],
            "reverse_bay_reference.free_mouth_width_m",
            positive=True,
        ),
        aisle_width_m=_number(
            bay_data["aisle_width_m"], "reverse_bay_reference.aisle_width_m", positive=True
        ),
        end_clearance_m=_number(
            bay_data["end_clearance_m"],
            "reverse_bay_reference.end_clearance_m",
            positive=True,
        ),
    )
    goal_data = _sequence(
        bay_data["goal_rear_axle_pose"], "reverse_bay_reference.goal_rear_axle_pose"
    )
    if len(goal_data) != 3:
        raise ConfigSchemaError("reverse_bay_reference.goal_rear_axle_pose must have length 3")
    try:
        goal = GoalRearAxleWorldPose(
            *(
                _number(value, f"reverse_bay_reference.goal_rear_axle_pose[{index}]")
                for index, value in enumerate(goal_data)
            )
        )
    except (TypeError, ValueError) as error:
        raise ConfigSchemaError(f"goal rear-axle pose is invalid: {error}") from error
    reverse_bay = ReverseBayReference(difficulty=difficulty, goal_rear_axle_pose=goal)

    observation_data = _object(root["observation"], "observation")
    _exact_keys(
        observation_data,
        {"dtype", "max_latency_steps", "object_slots"},
        "observation",
    )
    slot_values = _sequence(observation_data["object_slots"], "observation.object_slots")
    try:
        slots = tuple(
            ObjectRole(_string(item, "observation.object_slots[]")) for item in slot_values
        )
        observation_layout = ObservationLayout(
            max_latency_steps=_integer(
                observation_data["max_latency_steps"],
                "observation.max_latency_steps",
                positive=False,
            ),
            object_slots=slots,
            dtype=_string(observation_data["dtype"], "observation.dtype"),
        )
    except (TypeError, ValueError) as error:
        raise ConfigSchemaError(f"observation layout is invalid: {error}") from error
    if observation_layout.max_latency_steps != vehicle.max_latency_steps:
        raise ConfigSchemaError("observation and vehicle max_latency_steps must match")

    return ReferenceConfig(
        schema_version=schema_version,
        project=project,
        integration=integration,
        learning=learning,
        evaluation=evaluation,
        task=task,
        vehicle=vehicle,
        reverse_bay_reference=reverse_bay,
        observation_layout=observation_layout,
    )


def load_reference_config(path: str | Path) -> ReferenceConfig:
    """Load JSON and reject every unknown, missing, non-finite, or mistyped value."""

    config_path = Path(path)
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"), parse_constant=_reject_constant)
    except ConfigSchemaError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ConfigSchemaError(f"cannot read configuration {config_path}: {error}") from error
    return _parse_reference(data)
