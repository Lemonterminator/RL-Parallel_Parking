"""Deterministic rear-axle kinematic-bicycle dynamics."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from numbers import Real

from parking_rl.core.actions import ZERO_NORMALIZED_ACTION, NormalizedAction, PhysicalControl
from parking_rl.core.frames import RearAxleWorldPose, wrap_angle
from parking_rl.core.state import ActuatorState, EgoState, VehicleSpec, WorldState
from parking_rl.physics.action_scaling import scale_action


def _require_finite_positive(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number, not {type(value).__name__}")
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def _require_vehicle(vehicle: object) -> VehicleSpec:
    if type(vehicle) is not VehicleSpec:
        raise TypeError("vehicle must be exactly VehicleSpec")
    if vehicle.steering_gain != 1.0 or vehicle.steering_offset_rad != 0.0:
        raise ValueError("Stage 0 dynamics require steering_gain=1.0 and steering_offset_rad=0.0")
    return vehicle


def _clip(value: float, lower: float, upper: float) -> float:
    return min(max(value, lower), upper)


@dataclass(frozen=True, slots=True)
class DynamicsConfig:
    """Policy integration cadence fixed by the Stage 0 protocol."""

    dt_policy_s: float = 0.1
    substeps: int = 5

    def __post_init__(self) -> None:
        _require_finite_positive("dt_policy_s", self.dt_policy_s)
        if isinstance(self.substeps, bool) or not isinstance(self.substeps, int):
            raise TypeError(f"substeps must be an int, not {type(self.substeps).__name__}")
        if self.substeps != 5:
            raise ValueError("Stage 0 dynamics require exactly 5 integration substeps")

    @property
    def dt_sub_s(self) -> float:
        """Duration of one integration substep."""

        return self.dt_policy_s / self.substeps


@dataclass(frozen=True, slots=True)
class PolicyStepTrace:
    """Auditable action boundary and every state produced during a policy step."""

    requested_action: NormalizedAction
    applied_action: NormalizedAction
    applied_control: PhysicalControl
    substeps: tuple[EgoState, ...]

    def __post_init__(self) -> None:
        if type(self.requested_action) is not NormalizedAction:
            raise TypeError("requested_action must be exactly NormalizedAction")
        if type(self.applied_action) is not NormalizedAction:
            raise TypeError("applied_action must be exactly NormalizedAction")
        if type(self.applied_control) is not PhysicalControl:
            raise TypeError("applied_control must be exactly PhysicalControl")
        try:
            substeps = tuple(self.substeps)
        except TypeError as error:
            raise TypeError("substeps must be an iterable of EgoState") from error
        object.__setattr__(self, "substeps", substeps)
        if len(substeps) != 5:
            raise ValueError("a policy-step trace must contain exactly 5 substeps")
        if any(type(state) is not EgoState for state in substeps):
            raise TypeError("substeps must contain only EgoState values")


def clamp_control(control: PhysicalControl, vehicle: VehicleSpec) -> PhysicalControl:
    """Clamp both physical actuator channels to the realized vehicle limits."""

    if type(control) is not PhysicalControl:
        raise TypeError("control must be exactly PhysicalControl")
    vehicle = _require_vehicle(vehicle)
    return PhysicalControl(
        acceleration_mps2=_clip(
            control.acceleration_mps2,
            -vehicle.max_acceleration_mps2,
            vehicle.max_acceleration_mps2,
        ),
        steering_rate_radps=_clip(
            control.steering_rate_radps,
            -vehicle.max_steering_rate_radps,
            vehicle.max_steering_rate_radps,
        ),
    )


def advance_actuator(
    actuator: ActuatorState,
    requested_action: NormalizedAction,
    vehicle: VehicleSpec,
) -> tuple[NormalizedAction, ActuatorState]:
    """Advance the fixed-capacity latency queue once at a policy boundary."""

    if type(actuator) is not ActuatorState:
        raise TypeError("actuator must be exactly ActuatorState")
    if type(requested_action) is not NormalizedAction:
        raise TypeError("requested_action must be exactly NormalizedAction")
    vehicle = _require_vehicle(vehicle)
    if actuator.latency_steps != vehicle.latency_steps:
        raise ValueError("actuator and vehicle latency_steps must match")
    if len(actuator.pending_commands) != vehicle.max_latency_steps:
        raise ValueError("command-buffer capacity must equal vehicle.max_latency_steps")

    latency = actuator.latency_steps
    if latency == 0:
        applied_action = requested_action
        pending_commands = (ZERO_NORMALIZED_ACTION,) * vehicle.max_latency_steps
    else:
        applied_action = actuator.pending_commands[0]
        active = (*actuator.pending_commands[1:latency], requested_action)
        pending_commands = active + (ZERO_NORMALIZED_ACTION,) * (
            vehicle.max_latency_steps - latency
        )

    applied_control = clamp_control(scale_action(applied_action, vehicle), vehicle)
    return applied_action, ActuatorState(
        applied_control=applied_control,
        pending_commands=pending_commands,
        latency_steps=latency,
    )


def integrate_substep(
    ego: EgoState,
    control: PhysicalControl,
    vehicle: VehicleSpec,
    dt_s: float,
) -> EgoState:
    """Apply one simultaneous, old-state explicit-Euler bicycle update."""

    if type(ego) is not EgoState:
        raise TypeError("ego must be exactly EgoState")
    if type(control) is not PhysicalControl:
        raise TypeError("control must be exactly PhysicalControl")
    vehicle = _require_vehicle(vehicle)
    _require_finite_positive("dt_s", dt_s)
    if abs(ego.speed_mps) > vehicle.max_speed_mps:
        raise ValueError("initial speed_mps exceeds the vehicle limit")
    if abs(ego.steering_rad) > vehicle.max_steering_angle_rad:
        raise ValueError("initial steering_rad exceeds the vehicle limit")

    bounded = clamp_control(control, vehicle)
    old_pose = ego.pose
    old_speed = ego.speed_mps
    old_steering = ego.steering_rad
    return EgoState(
        pose=RearAxleWorldPose(
            x_m=old_pose.x_m + old_speed * math.cos(old_pose.heading_rad) * dt_s,
            y_m=old_pose.y_m + old_speed * math.sin(old_pose.heading_rad) * dt_s,
            heading_rad=wrap_angle(
                old_pose.heading_rad
                + old_speed / vehicle.wheelbase_m * math.tan(old_steering) * dt_s
            ),
        ),
        speed_mps=_clip(
            old_speed + bounded.acceleration_mps2 * dt_s,
            -vehicle.max_speed_mps,
            vehicle.max_speed_mps,
        ),
        steering_rad=_clip(
            old_steering + bounded.steering_rate_radps * dt_s,
            -vehicle.max_steering_angle_rad,
            vehicle.max_steering_angle_rad,
        ),
    )


def step_world_state(
    world: WorldState,
    requested_action: NormalizedAction,
    config: DynamicsConfig | None = None,
) -> tuple[WorldState, PolicyStepTrace]:
    """Advance one policy step using zero-order hold over exactly five substeps."""

    if type(world) is not WorldState:
        raise TypeError("world must be exactly WorldState")
    if type(requested_action) is not NormalizedAction:
        raise TypeError("requested_action must be exactly NormalizedAction")
    if config is None:
        config = DynamicsConfig()
    if type(config) is not DynamicsConfig:
        raise TypeError("config must be exactly DynamicsConfig")

    applied_action, next_actuator = advance_actuator(
        world.actuator, requested_action, world.vehicle
    )
    ego = world.ego
    states: list[EgoState] = []
    for _ in range(config.substeps):
        ego = integrate_substep(ego, next_actuator.applied_control, world.vehicle, config.dt_sub_s)
        states.append(ego)
    trace = PolicyStepTrace(
        requested_action=requested_action,
        applied_action=applied_action,
        applied_control=next_actuator.applied_control,
        substeps=tuple(states),
    )
    return replace(world, ego=ego, actuator=next_actuator), trace
