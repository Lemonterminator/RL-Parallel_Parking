"""Immutable truth-state contracts for the parking simulator."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from numbers import Real
from typing import ClassVar

from parking_rl.core.actions import (
    ZERO_NORMALIZED_ACTION,
    NormalizedAction,
    PhysicalControl,
)
from parking_rl.core.frames import ObjectCentroidWorldPose, RearAxleWorldPose


def _require_finite(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number, not {type(value).__name__}")
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")


def _require_positive(name: str, value: object) -> None:
    _require_finite(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def _require_nonnegative_int(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an int, not {type(value).__name__}")
    if value < 0:
        raise ValueError(f"{name} must be nonnegative")


def _require_exact_type(name: str, value: object, expected: type[object]) -> None:
    if type(value) is not expected:
        raise TypeError(f"{name} must be exactly {expected.__name__}")


@dataclass(frozen=True, slots=True)
class VehicleSpec:
    """Episode-realized vehicle geometry, limits, and actuator latency."""

    wheelbase_m: float
    length_m: float
    width_m: float
    front_overhang_m: float
    rear_overhang_m: float
    max_steering_angle_rad: float
    max_steering_rate_radps: float
    max_speed_mps: float
    max_acceleration_mps2: float
    steering_gain: float = 1.0
    steering_offset_rad: float = 0.0
    latency_steps: int = 0
    max_latency_steps: int = 0

    def __post_init__(self) -> None:
        positive_fields = (
            "wheelbase_m",
            "length_m",
            "width_m",
            "front_overhang_m",
            "rear_overhang_m",
            "max_steering_angle_rad",
            "max_steering_rate_radps",
            "max_speed_mps",
            "max_acceleration_mps2",
            "steering_gain",
        )
        for name in positive_fields:
            _require_positive(name, getattr(self, name))
        _require_finite("steering_offset_rad", self.steering_offset_rad)
        if not math.isclose(
            self.length_m,
            self.wheelbase_m + self.front_overhang_m + self.rear_overhang_m,
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            raise ValueError("length_m must equal wheelbase_m + front_overhang_m + rear_overhang_m")
        _require_nonnegative_int("latency_steps", self.latency_steps)
        _require_nonnegative_int("max_latency_steps", self.max_latency_steps)
        if self.latency_steps > self.max_latency_steps:
            raise ValueError("latency_steps must not exceed max_latency_steps")


@dataclass(frozen=True, slots=True)
class Bounds2D:
    """Axis-aligned world bounds."""

    min_x_m: float
    max_x_m: float
    min_y_m: float
    max_y_m: float

    def __post_init__(self) -> None:
        for name in ("min_x_m", "max_x_m", "min_y_m", "max_y_m"):
            _require_finite(name, getattr(self, name))
        if self.min_x_m >= self.max_x_m:
            raise ValueError("min_x_m must be less than max_x_m")
        if self.min_y_m >= self.max_y_m:
            raise ValueError("min_y_m must be less than max_y_m")


class ObjectKind(StrEnum):
    VEHICLE = "vehicle"
    KERB = "kerb"
    GOAL_SLOT = "goal_slot"


class ObjectRole(StrEnum):
    FRONT_VEHICLE = "front_vehicle"
    REAR_VEHICLE = "rear_vehicle"
    KERB = "kerb"
    GOAL_SLOT = "goal_slot"


@dataclass(frozen=True, slots=True)
class ObjectState:
    """Typed object truth at its centroid reference point."""

    id: str
    kind: ObjectKind
    role: ObjectRole
    pose: ObjectCentroidWorldPose
    length_m: float
    width_m: float

    _ROLE_KINDS: ClassVar[dict[ObjectRole, ObjectKind]] = {
        ObjectRole.FRONT_VEHICLE: ObjectKind.VEHICLE,
        ObjectRole.REAR_VEHICLE: ObjectKind.VEHICLE,
        ObjectRole.KERB: ObjectKind.KERB,
        ObjectRole.GOAL_SLOT: ObjectKind.GOAL_SLOT,
    }

    def __post_init__(self) -> None:
        if type(self.id) is not str or not self.id:
            raise ValueError("id must be a non-empty string")
        if type(self.kind) is not ObjectKind:
            raise TypeError("kind must be exactly ObjectKind")
        if type(self.role) is not ObjectRole:
            raise TypeError("role must be exactly ObjectRole")
        _require_exact_type("pose", self.pose, ObjectCentroidWorldPose)
        _require_positive("length_m", self.length_m)
        _require_positive("width_m", self.width_m)
        if self._ROLE_KINDS[self.role] is not self.kind:
            raise ValueError(f"role {self.role.value} is incompatible with kind {self.kind.value}")


@dataclass(frozen=True, slots=True)
class StaticWorld:
    """Immutable bounds and typed static objects shared throughout an episode."""

    bounds: Bounds2D
    objects: tuple[ObjectState, ...]
    goal_object_id: str

    def __post_init__(self) -> None:
        _require_exact_type("bounds", self.bounds, Bounds2D)
        try:
            objects = tuple(self.objects)
        except TypeError as error:
            raise TypeError("objects must be an iterable of ObjectState") from error
        object.__setattr__(self, "objects", objects)
        if any(type(item) is not ObjectState for item in objects):
            raise TypeError("objects must contain only ObjectState values")
        ids = [item.id for item in objects]
        if len(ids) != len(set(ids)):
            raise ValueError("object IDs must be unique")
        if type(self.goal_object_id) is not str or not self.goal_object_id:
            raise ValueError("goal_object_id must be a non-empty string")
        goal = next((item for item in objects if item.id == self.goal_object_id), None)
        if goal is None:
            raise ValueError("goal_object_id must identify an object")
        if goal.kind is not ObjectKind.GOAL_SLOT or goal.role is not ObjectRole.GOAL_SLOT:
            raise ValueError("goal_object_id must identify a GOAL_SLOT object")


@dataclass(frozen=True, slots=True)
class EgoState:
    """Dynamic ego truth at the rear-axle midpoint."""

    pose: RearAxleWorldPose
    speed_mps: float
    steering_rad: float

    def __post_init__(self) -> None:
        _require_exact_type("pose", self.pose, RearAxleWorldPose)
        _require_finite("speed_mps", self.speed_mps)
        _require_finite("steering_rad", self.steering_rad)


@dataclass(frozen=True, slots=True)
class SettleProgress:
    """Consecutive in-tolerance policy steps toward success."""

    count: int
    required_steps: int

    def __post_init__(self) -> None:
        _require_nonnegative_int("count", self.count)
        _require_nonnegative_int("required_steps", self.required_steps)
        if self.required_steps == 0:
            raise ValueError("required_steps must be positive")
        if self.count > self.required_steps:
            raise ValueError("count must not exceed required_steps")


@dataclass(frozen=True, slots=True)
class ActuatorState:
    """Applied physical control and fixed-capacity normalized command buffer."""

    applied_control: PhysicalControl
    pending_commands: tuple[NormalizedAction, ...]
    latency_steps: int

    def __post_init__(self) -> None:
        _require_exact_type("applied_control", self.applied_control, PhysicalControl)
        try:
            pending_commands = tuple(self.pending_commands)
        except TypeError as error:
            raise TypeError("pending_commands must be an iterable of NormalizedAction") from error
        object.__setattr__(self, "pending_commands", pending_commands)
        if any(type(command) is not NormalizedAction for command in pending_commands):
            raise TypeError("pending_commands must contain only NormalizedAction values")
        _require_nonnegative_int("latency_steps", self.latency_steps)
        if self.latency_steps > len(pending_commands):
            raise ValueError("latency_steps must not exceed command-buffer capacity")
        if any(
            command != ZERO_NORMALIZED_ACTION
            for command in pending_commands[self.latency_steps :]
        ):
            raise ValueError("inactive command-buffer padding must contain only zero actions")

    @property
    def active_pending_commands(self) -> tuple[NormalizedAction, ...]:
        """Return active commands in oldest-to-newest order."""

        return self.pending_commands[: self.latency_steps]


@dataclass(frozen=True, slots=True)
class WorldState:
    """Complete Markov truth state, separate from observations and episode runtime."""

    vehicle: VehicleSpec
    static_world: StaticWorld
    ego: EgoState
    objects: tuple[ObjectState, ...]
    settle: SettleProgress
    actuator: ActuatorState

    def __post_init__(self) -> None:
        _require_exact_type("vehicle", self.vehicle, VehicleSpec)
        _require_exact_type("static_world", self.static_world, StaticWorld)
        _require_exact_type("ego", self.ego, EgoState)
        _require_exact_type("settle", self.settle, SettleProgress)
        _require_exact_type("actuator", self.actuator, ActuatorState)
        try:
            objects = tuple(self.objects)
        except TypeError as error:
            raise TypeError("objects must be an iterable of ObjectState") from error
        object.__setattr__(self, "objects", objects)
        if any(type(item) is not ObjectState for item in objects):
            raise TypeError("objects must contain only ObjectState values")
        ids = [item.id for item in objects]
        if len(ids) != len(set(ids)):
            raise ValueError("object IDs must be unique")
        if set(ids) != {item.id for item in self.static_world.objects}:
            raise ValueError("objects must have exactly the StaticWorld object IDs")
        static_by_id = {item.id: item for item in self.static_world.objects}
        if any(
            (item.kind, item.role)
            != (static_by_id[item.id].kind, static_by_id[item.id].role)
            for item in objects
        ):
            raise ValueError("dynamic object kind and role must match StaticWorld")
        if self.vehicle.latency_steps != self.actuator.latency_steps:
            raise ValueError("vehicle and actuator latency_steps must match")
        if len(self.actuator.pending_commands) != self.vehicle.max_latency_steps:
            raise ValueError("command-buffer capacity must equal vehicle.max_latency_steps")
