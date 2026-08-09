"""Bounded sampled collision sweep for one policy-step trajectory.

The interpolation here follows the constant-derivative path represented by an
explicit-Euler substep.  It intentionally does not claim an analytic bicycle
arc or an exact time of impact.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import pairwise
from numbers import Real

from parking_rl.core.frames import RearAxleWorldPose, wrap_angle
from parking_rl.core.state import VehicleSpec, WorldState
from parking_rl.physics.collision import solid_obstacles
from parking_rl.physics.dynamics import PolicyStepTrace
from parking_rl.physics.geometry import (
    OBB,
    obb_corners,
    object_obb,
    sat_overlap,
    vehicle_farthest_corner_m,
    vehicle_obb,
)


def _require_exact_type(name: str, value: object, expected: type[object]) -> None:
    if type(value) is not expected:
        raise TypeError(f"{name} must be exactly {expected.__name__}")


def _require_finite(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number, not {type(value).__name__}")
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")


def _require_pose_tuple(poses: object) -> tuple[RearAxleWorldPose, ...]:
    if type(poses) is not tuple:
        raise TypeError("poses must be exactly tuple")
    if not poses:
        raise ValueError("poses must contain at least one pose")
    if any(type(pose) is not RearAxleWorldPose for pose in poses):
        raise TypeError("poses must contain only RearAxleWorldPose values")
    return poses


@dataclass(frozen=True, slots=True)
class SweepConfig:
    """Maximum permitted farthest-point motion between collision samples."""

    max_point_motion_m: float = 0.025

    def __post_init__(self) -> None:
        _require_finite("max_point_motion_m", self.max_point_motion_m)
        if self.max_point_motion_m <= 0.0:
            raise ValueError("max_point_motion_m must be positive")


@dataclass(frozen=True, slots=True)
class SweepResult:
    """Collision result and evidence for the bounded sampling resolution."""

    collides: bool
    samples_checked: int
    first_collision_pose: RearAxleWorldPose | None
    max_interval_motion_bound_m: float

    def __post_init__(self) -> None:
        if type(self.collides) is not bool:
            raise TypeError("collides must be exactly bool")
        if isinstance(self.samples_checked, bool) or not isinstance(self.samples_checked, int):
            raise TypeError("samples_checked must be an int")
        if self.samples_checked <= 0:
            raise ValueError("samples_checked must be positive")
        if self.first_collision_pose is not None:
            _require_exact_type(
                "first_collision_pose", self.first_collision_pose, RearAxleWorldPose
            )
        if self.collides != (self.first_collision_pose is not None):
            raise ValueError("collides must agree with first_collision_pose")
        _require_finite(
            "max_interval_motion_bound_m", self.max_interval_motion_bound_m
        )
        if self.max_interval_motion_bound_m < 0.0:
            raise ValueError("max_interval_motion_bound_m must be nonnegative")


def pose_motion_bound_m(
    start: RearAxleWorldPose,
    end: RearAxleWorldPose,
    vehicle: VehicleSpec,
) -> float:
    """Upper-bound every footprint point's motion between two poses."""

    _require_exact_type("start", start, RearAxleWorldPose)
    _require_exact_type("end", end, RearAxleWorldPose)
    _require_exact_type("vehicle", vehicle, VehicleSpec)
    translation_m = math.hypot(end.x_m - start.x_m, end.y_m - start.y_m)
    heading_change_rad = abs(wrap_angle(end.heading_rad - start.heading_rad))
    return translation_m + vehicle_farthest_corner_m(vehicle) * heading_change_rad


def interpolate_pose(
    start: RearAxleWorldPose,
    end: RearAxleWorldPose,
    fraction: float,
) -> RearAxleWorldPose:
    """Interpolate an explicit-Euler segment with the shortest wrapped heading."""

    _require_exact_type("start", start, RearAxleWorldPose)
    _require_exact_type("end", end, RearAxleWorldPose)
    _require_finite("fraction", fraction)
    if not 0.0 <= fraction <= 1.0:
        raise ValueError("fraction must be within [0, 1]")
    heading_change = wrap_angle(end.heading_rad - start.heading_rad)
    return RearAxleWorldPose(
        x_m=start.x_m + fraction * (end.x_m - start.x_m),
        y_m=start.y_m + fraction * (end.y_m - start.y_m),
        heading_rad=wrap_angle(start.heading_rad + fraction * heading_change),
    )


def bounded_sweep_poses(
    poses: tuple[RearAxleWorldPose, ...],
    vehicle: VehicleSpec,
    config: SweepConfig | None = None,
) -> tuple[RearAxleWorldPose, ...]:
    """Densify poses so each interval respects the configured motion bound."""

    poses = _require_pose_tuple(poses)
    _require_exact_type("vehicle", vehicle, VehicleSpec)
    if config is None:
        config = SweepConfig()
    _require_exact_type("config", config, SweepConfig)

    samples = [poses[0]]
    for start, end in pairwise(poses):
        interval_bound = pose_motion_bound_m(start, end, vehicle)
        interval_count = max(1, math.ceil(interval_bound / config.max_point_motion_m))
        samples.extend(
            end
            if index == interval_count
            else interpolate_pose(start, end, index / interval_count)
            for index in range(1, interval_count + 1)
        )
    return tuple(samples)


def _max_interval_bound(
    samples: tuple[RearAxleWorldPose, ...], vehicle: VehicleSpec
) -> float:
    return max(
        (
            pose_motion_bound_m(start, end, vehicle)
            for start, end in pairwise(samples)
        ),
        default=0.0,
    )


def sweep_collides(
    poses: tuple[RearAxleWorldPose, ...],
    vehicle: VehicleSpec,
    obstacles: tuple[OBB, ...],
    config: SweepConfig | None = None,
) -> SweepResult:
    """Test exact OBB overlap at every sample in a motion-bounded sweep."""

    poses = _require_pose_tuple(poses)
    _require_exact_type("vehicle", vehicle, VehicleSpec)
    if type(obstacles) is not tuple:
        raise TypeError("obstacles must be exactly tuple")
    if any(type(obstacle) is not OBB for obstacle in obstacles):
        raise TypeError("obstacles must contain only OBB values")
    if config is None:
        config = SweepConfig()
    _require_exact_type("config", config, SweepConfig)

    samples = bounded_sweep_poses(poses, vehicle, config)
    maximum_bound = _max_interval_bound(samples, vehicle)
    for index, pose in enumerate(samples, start=1):
        ego_box = vehicle_obb(pose, vehicle)
        if any(sat_overlap(ego_box, obstacle) for obstacle in obstacles):
            return SweepResult(True, index, pose, maximum_bound)
    return SweepResult(False, len(samples), None, maximum_bound)


def _touches_closed_bounds(pose: RearAxleWorldPose, world: WorldState) -> bool:
    bounds = world.static_world.bounds
    return any(
        x_m <= bounds.min_x_m
        or x_m >= bounds.max_x_m
        or y_m <= bounds.min_y_m
        or y_m >= bounds.max_y_m
        for x_m, y_m in obb_corners(vehicle_obb(pose, world.vehicle))
    )


def world_step_collides(
    world: WorldState,
    trace: PolicyStepTrace,
    config: SweepConfig | None = None,
) -> SweepResult:
    """Sweep the initial and five substep poses against solids and bounds."""

    _require_exact_type("world", world, WorldState)
    _require_exact_type("trace", trace, PolicyStepTrace)
    if config is None:
        config = SweepConfig()
    _require_exact_type("config", config, SweepConfig)

    poses = (world.ego.pose, *(state.pose for state in trace.substeps))
    samples = bounded_sweep_poses(poses, world.vehicle, config)
    obstacles = tuple(object_obb(obj) for obj in solid_obstacles(world.objects))
    maximum_bound = _max_interval_bound(samples, world.vehicle)

    for index, pose in enumerate(samples, start=1):
        ego_box = vehicle_obb(pose, world.vehicle)
        if _touches_closed_bounds(pose, world) or any(
            sat_overlap(ego_box, obstacle) for obstacle in obstacles
        ):
            return SweepResult(True, index, pose, maximum_bound)
    return SweepResult(False, len(samples), None, maximum_bound)
