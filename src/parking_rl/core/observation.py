"""Fixed-width observation layout and observer provenance contracts."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from numbers import Real

from parking_rl.core.fingerprint import sha256_fingerprint
from parking_rl.core.scenario import TaskFamily
from parking_rl.core.state import ObjectRole


class ObservationRung(StrEnum):
    O0 = "O0"
    O1 = "O1"
    O2 = "O2"
    O3 = "O3"
    O4 = "O4"


@dataclass(frozen=True, slots=True)
class ObservationField:
    """One scalar field in the policy vector."""

    name: str

    def __post_init__(self) -> None:
        if type(self.name) is not str or not self.name:
            raise ValueError("observation field name must be a non-empty string")


_OBJECT_COMPONENTS = (
    "relative_x_m",
    "relative_y_m",
    "heading_sin",
    "heading_cos",
    "length_m",
    "width_m",
    "type_vehicle",
    "type_kerb",
    "type_goal_slot",
    "valid",
    "visible_now",
    "log1p_tau_steps",
)


@dataclass(frozen=True, slots=True)
class ObservationLayout:
    """One layout shared byte-for-byte by all O0--O4 observer rungs."""

    max_latency_steps: int
    object_slots: tuple[ObjectRole, ...] = (
        ObjectRole.FRONT_VEHICLE,
        ObjectRole.REAR_VEHICLE,
        ObjectRole.KERB,
        ObjectRole.GOAL_SLOT,
    )
    dtype: str = "float32"
    schema_version: int = 1

    def __post_init__(self) -> None:
        if isinstance(self.max_latency_steps, bool) or not isinstance(self.max_latency_steps, int):
            raise TypeError("max_latency_steps must be an int")
        if self.max_latency_steps < 0:
            raise ValueError("max_latency_steps must be nonnegative")
        try:
            slots = tuple(self.object_slots)
        except TypeError as error:
            raise TypeError("object_slots must be iterable") from error
        object.__setattr__(self, "object_slots", slots)
        if slots != (
            ObjectRole.FRONT_VEHICLE,
            ObjectRole.REAR_VEHICLE,
            ObjectRole.KERB,
            ObjectRole.GOAL_SLOT,
        ):
            raise ValueError("object_slots must use the fixed semantic slot order")
        if self.dtype != "float32" or type(self.schema_version) is not int:
            raise ValueError("dtype must be float32 and schema_version must be integer 1")
        if self.schema_version != 1:
            raise ValueError("schema_version must be 1")

    @property
    def fields(self) -> tuple[ObservationField, ...]:
        names = [
            "ego.speed_fraction",
            "ego.steering_fraction",
            "ego.settle_progress_fraction",
            "task.parallel",
            "task.reverse_bay",
            "actuator.latency_steps_fraction",
        ]
        for index in range(self.max_latency_steps):
            names.extend(
                (
                    f"actuator.queue_{index}.longitudinal",
                    f"actuator.queue_{index}.steering_rate",
                    f"actuator.queue_{index}.valid",
                )
            )
        for role in self.object_slots:
            names.extend(f"object.{role.value}.{component}" for component in _OBJECT_COMPONENTS)
        return tuple(ObservationField(name) for name in names)

    @property
    def field_names(self) -> tuple[str, ...]:
        return tuple(field.name for field in self.fields)

    @property
    def width(self) -> int:
        return len(self.fields)

    @property
    def layout_hash(self) -> str:
        return sha256_fingerprint(
            {
                "schema_version": self.schema_version,
                "dtype": self.dtype,
                "fields": self.field_names,
            }
        )

    def empty_values(self, family: TaskFamily) -> tuple[float, ...]:
        """Build a valid zero-filled vector with exactly one task-family bit set."""

        if type(family) is not TaskFamily:
            raise TypeError("family must be exactly TaskFamily")
        values = [0.0] * self.width
        names = self.field_names
        values[names.index(f"task.{family.value}")] = 1.0
        expected_type = {
            ObjectRole.FRONT_VEHICLE: "type_vehicle",
            ObjectRole.REAR_VEHICLE: "type_vehicle",
            ObjectRole.KERB: "type_kerb",
            ObjectRole.GOAL_SLOT: "type_goal_slot",
        }
        for role, component in expected_type.items():
            values[names.index(f"object.{role.value}.{component}")] = 1.0
        return tuple(values)


@dataclass(frozen=True, slots=True)
class ObserverConfig:
    """Sensor behavior fingerprint, deliberately separate from layout identity."""

    rung: ObservationRung
    tau_enabled: bool
    horizontal_fov_rad: float
    max_range_m: float
    position_noise_std_m: float = 0.0
    heading_noise_std_rad: float = 0.0
    dropout_probability: float = 0.0
    goal_subject_to_fov: bool = True
    schema_version: int = 1

    def __post_init__(self) -> None:
        if type(self.rung) is not ObservationRung:
            raise TypeError("rung must be exactly ObservationRung")
        for name in ("tau_enabled", "goal_subject_to_fov"):
            if type(getattr(self, name)) is not bool:
                raise TypeError(f"{name} must be bool")
        if self.tau_enabled != (self.rung in {ObservationRung.O3, ObservationRung.O4}):
            raise ValueError("tau is disabled for O0--O2 and enabled for O3--O4")
        for name in (
            "horizontal_fov_rad",
            "max_range_m",
            "position_noise_std_m",
            "heading_noise_std_rad",
            "dropout_probability",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, Real):
                raise TypeError(f"{name} must be a real number")
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
        if not 0 < self.horizontal_fov_rad <= math.tau:
            raise ValueError("horizontal_fov_rad must be in (0, 2*pi]")
        if self.max_range_m <= 0:
            raise ValueError("max_range_m must be positive")
        if self.position_noise_std_m < 0 or self.heading_noise_std_rad < 0:
            raise ValueError("noise standard deviations must be nonnegative")
        if not 0 <= self.dropout_probability <= 1:
            raise ValueError("dropout_probability must be in [0, 1]")
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise ValueError("schema_version must be integer 1")

    @property
    def config_hash(self) -> str:
        return sha256_fingerprint(self)


@dataclass(frozen=True, slots=True)
class Observation:
    """Policy values coupled to, but not mixed with, their schema provenance."""

    values: tuple[float, ...]
    layout: ObservationLayout
    observer: ObserverConfig

    def __post_init__(self) -> None:
        if type(self.layout) is not ObservationLayout:
            raise TypeError("layout must be exactly ObservationLayout")
        if type(self.observer) is not ObserverConfig:
            raise TypeError("observer must be exactly ObserverConfig")
        try:
            values = tuple(self.values)
        except TypeError as error:
            raise TypeError("values must be iterable") from error
        object.__setattr__(self, "values", values)
        if len(values) != self.layout.width:
            raise ValueError("observation value width does not match layout")
        for value in values:
            if isinstance(value, bool) or not isinstance(value, Real):
                raise TypeError("observation values must be real numbers")
            if not math.isfinite(value):
                raise ValueError("observation values must be finite")
        names = self.layout.field_names
        family_bits = tuple(values[names.index(f"task.{family.value}")] for family in TaskFamily)
        if family_bits not in {(1.0, 0.0), (0.0, 1.0)}:
            raise ValueError("observation must contain exactly one task-family bit")
        for name, value in zip(names, values, strict=True):
            if (name.endswith(".valid") or name.endswith(".visible_now")) and value not in {
                0.0,
                1.0,
            }:
                raise ValueError("validity fields must be binary")
            if not self.observer.tau_enabled and name.endswith(".log1p_tau_steps") and value != 0:
                raise ValueError("tau fields must be bitwise zero when tau is disabled")
        for name in ("ego.speed_fraction", "ego.steering_fraction"):
            if not -1 <= values[names.index(name)] <= 1:
                raise ValueError(f"{name} must be in [-1, 1]")
        settle = values[names.index("ego.settle_progress_fraction")]
        latency = values[names.index("actuator.latency_steps_fraction")]
        if not 0 <= settle <= 1 or not 0 <= latency <= 1:
            raise ValueError("settle and latency fractions must be in [0, 1]")
        queue_valid = []
        for index in range(self.layout.max_latency_steps):
            prefix = f"actuator.queue_{index}"
            valid = values[names.index(f"{prefix}.valid")]
            queue_valid.append(valid)
            if valid == 0 and any(
                values[names.index(f"{prefix}.{component}")] != 0
                for component in ("longitudinal", "steering_rate")
            ):
                raise ValueError("inactive actuator queue slots must be zero padded")
        if queue_valid != sorted(queue_valid, reverse=True):
            raise ValueError("active actuator queue slots must form a contiguous prefix")
        expected_latency = (
            sum(queue_valid) / self.layout.max_latency_steps
            if self.layout.max_latency_steps
            else 0.0
        )
        if latency != expected_latency:
            raise ValueError("latency fraction must match actuator queue validity")
        expected_types = {
            ObjectRole.FRONT_VEHICLE: (1.0, 0.0, 0.0),
            ObjectRole.REAR_VEHICLE: (1.0, 0.0, 0.0),
            ObjectRole.KERB: (0.0, 1.0, 0.0),
            ObjectRole.GOAL_SLOT: (0.0, 0.0, 1.0),
        }
        for role, expected in expected_types.items():
            actual = tuple(
                values[names.index(f"object.{role.value}.{component}")]
                for component in ("type_vehicle", "type_kerb", "type_goal_slot")
            )
            if actual != expected:
                raise ValueError(f"object.{role.value} has invalid type one-hot values")

    @property
    def layout_hash(self) -> str:
        return self.layout.layout_hash

    @property
    def observer_config_hash(self) -> str:
        return self.observer.config_hash

    @property
    def dtype(self) -> str:
        return self.layout.dtype
