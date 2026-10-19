"""EXIT-0.11 evidence: actuator and state clamps hold at every integration substep.

The audit drives the production dynamics (``step_world_state`` and
``integrate_substep``) rather than a re-implementation, so the evidence is about
the code the environment runs. Work is split into fixed, independently seeded
chunks; results are identical for any worker count.
"""

from __future__ import annotations

import hashlib
import math
import random
import struct
import time
from collections.abc import Iterator
from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field, replace

from parking_rl.core.actions import ZERO_NORMALIZED_ACTION, NormalizedAction, PhysicalControl
from parking_rl.core.frames import ObjectCentroidWorldPose, RearAxleWorldPose
from parking_rl.core.state import (
    ActuatorState,
    Bounds2D,
    EgoState,
    ObjectKind,
    ObjectRole,
    ObjectState,
    SettleProgress,
    StaticWorld,
    VehicleSpec,
    WorldState,
)
from parking_rl.physics import dynamics
from parking_rl.physics.ccd import SweepConfig, pose_motion_bound_m
from parking_rl.physics.dynamics import DynamicsConfig, integrate_substep, step_world_state
from parking_rl.physics.geometry import obb_corners, vehicle_obb

TOLERANCE = 1e-12
SATURATION_CORNERS = ((1.0, 1.0), (1.0, -1.0), (-1.0, 1.0), (-1.0, -1.0))
BOUND_NAMES = ("steering_angle", "speed", "steering_step", "speed_step")


@dataclass(frozen=True, slots=True)
class StressSpec:
    """Fixed protocol parameters; changing any of them changes the evidence."""

    sequences: int = 1_000_000
    policy_steps: int = 400
    chunk_size: int = 1_000
    base_seed: int = 20261019
    saturation_fraction: float = 0.04
    raw_control_fraction: float = 0.10
    ccd_audit_every: int = 100

    def __post_init__(self) -> None:
        for name in ("sequences", "policy_steps", "chunk_size", "ccd_audit_every"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive int")
        for name in ("saturation_fraction", "raw_control_fraction"):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be within [0, 1]")
        if self.saturation_fraction + self.raw_control_fraction > 1.0:
            raise ValueError("saturation and raw-control fractions must sum to at most 1")

    @property
    def chunks(self) -> int:
        return math.ceil(self.sequences / self.chunk_size)


@dataclass(slots=True)
class ChunkResult:
    """Counts and extremes for one chunk; merged in chunk order."""

    sequences: int = 0
    substeps: int = 0
    saturation_sequences: int = 0
    raw_control_sequences: int = 0
    latency_sequences: list[int] = field(default_factory=lambda: [0, 0, 0])
    violations: dict[str, int] = field(default_factory=lambda: dict.fromkeys(BOUND_NAMES, 0))
    max_ratio: dict[str, float] = field(default_factory=lambda: dict.fromkeys(BOUND_NAMES, 0.0))
    guard_trips: int = 0
    ccd_substeps: int = 0
    ccd_bound_samples: int = 0
    ccd_exact_samples: int = 0
    ccd_max_bound_samples: int = 0
    ccd_max_exact_samples: int = 0
    ccd_max_bound_m: float = 0.0
    ccd_max_exact_m: float = 0.0
    digest: str = ""

    def merge(self, other: ChunkResult) -> None:
        self.sequences += other.sequences
        self.substeps += other.substeps
        self.saturation_sequences += other.saturation_sequences
        self.raw_control_sequences += other.raw_control_sequences
        self.latency_sequences = [
            a + b for a, b in zip(self.latency_sequences, other.latency_sequences, strict=True)
        ]
        for name in BOUND_NAMES:
            self.violations[name] += other.violations[name]
            self.max_ratio[name] = max(self.max_ratio[name], other.max_ratio[name])
        self.guard_trips += other.guard_trips
        self.ccd_substeps += other.ccd_substeps
        self.ccd_bound_samples += other.ccd_bound_samples
        self.ccd_exact_samples += other.ccd_exact_samples
        self.ccd_max_bound_samples = max(self.ccd_max_bound_samples, other.ccd_max_bound_samples)
        self.ccd_max_exact_samples = max(self.ccd_max_exact_samples, other.ccd_max_exact_samples)
        self.ccd_max_bound_m = max(self.ccd_max_bound_m, other.ccd_max_bound_m)
        self.ccd_max_exact_m = max(self.ccd_max_exact_m, other.ccd_max_exact_m)
        self.digest = hashlib.sha256((self.digest + other.digest).encode()).hexdigest()


_ORIGINAL_CLIP = dynamics._clip


def dynamics_clamps_are_disabled() -> bool:
    return dynamics._clip is not _ORIGINAL_CLIP


@contextmanager
def clamps_disabled() -> Iterator[None]:
    """Positive control: replace the dynamics clip with the identity, then restore it."""

    original = dynamics._clip
    dynamics._clip = lambda value, lower, upper: value
    try:
        yield
    finally:
        dynamics._clip = original


def _world(vehicle: VehicleSpec, ego: EgoState) -> WorldState:
    goal = ObjectState(
        id="goal",
        kind=ObjectKind.GOAL_SLOT,
        role=ObjectRole.GOAL_SLOT,
        pose=ObjectCentroidWorldPose(0.0, 0.0, 0.0),
        length_m=6.0,
        width_m=2.5,
    )
    static = StaticWorld(
        bounds=Bounds2D(-1.0e6, 1.0e6, -1.0e6, 1.0e6),
        objects=(goal,),
        goal_object_id=goal.id,
    )
    return WorldState(
        vehicle=vehicle,
        static_world=static,
        ego=ego,
        objects=static.objects,
        settle=SettleProgress(0, 10),
        actuator=ActuatorState(
            applied_control=PhysicalControl(0.0, 0.0),
            pending_commands=(ZERO_NORMALIZED_ACTION,) * vehicle.max_latency_steps,
            latency_steps=vehicle.latency_steps,
        ),
    )


def _random_ego(generator: random.Random, vehicle: VehicleSpec) -> EgoState:
    return EgoState(
        RearAxleWorldPose(0.0, 0.0, generator.uniform(-math.pi, math.pi)),
        generator.uniform(-vehicle.max_speed_mps, vehicle.max_speed_mps),
        generator.uniform(-vehicle.max_steering_angle_rad, vehicle.max_steering_angle_rad),
    )


def _check(
    result: ChunkResult,
    previous: EgoState,
    state: EgoState,
    vehicle: VehicleSpec,
    dt_sub_s: float,
) -> None:
    limits = (
        (abs(state.steering_rad), vehicle.max_steering_angle_rad),
        (abs(state.speed_mps), vehicle.max_speed_mps),
        (
            abs(state.steering_rad - previous.steering_rad),
            vehicle.max_steering_rate_radps * dt_sub_s,
        ),
        (abs(state.speed_mps - previous.speed_mps), vehicle.max_acceleration_mps2 * dt_sub_s),
    )
    for name, (value, limit) in zip(BOUND_NAMES, limits, strict=True):
        if value > limit + TOLERANCE:
            result.violations[name] += 1
        ratio = value / limit
        if ratio > result.max_ratio[name]:
            result.max_ratio[name] = ratio


def _audit_ccd(
    result: ChunkResult,
    previous: EgoState,
    state: EgoState,
    vehicle: VehicleSpec,
    resolution_m: float,
) -> None:
    bound = pose_motion_bound_m(previous.pose, state.pose, vehicle)
    exact = max(
        math.hypot(after[0] - before[0], after[1] - before[1])
        for before, after in zip(
            obb_corners(vehicle_obb(previous.pose, vehicle)),
            obb_corners(vehicle_obb(state.pose, vehicle)),
            strict=True,
        )
    )
    bound_samples = max(1, math.ceil(bound / resolution_m))
    exact_samples = max(1, math.ceil(exact / resolution_m))
    result.ccd_substeps += 1
    result.ccd_bound_samples += bound_samples
    result.ccd_exact_samples += exact_samples
    result.ccd_max_bound_samples = max(result.ccd_max_bound_samples, bound_samples)
    result.ccd_max_exact_samples = max(result.ccd_max_exact_samples, exact_samples)
    result.ccd_max_bound_m = max(result.ccd_max_bound_m, bound)
    result.ccd_max_exact_m = max(result.ccd_max_exact_m, exact)


def _run_sequence(
    spec: StressSpec,
    vehicle: VehicleSpec,
    ego: EgoState,
    mode: str,
    generator: random.Random,
    result: ChunkResult,
    audit: bool,
    config: DynamicsConfig,
    resolution_m: float,
) -> EgoState:
    dt_sub_s = config.dt_sub_s
    if mode == "raw":
        # Out-of-range physical controls exercise clamp_control as well as state clips.
        for _ in range(spec.policy_steps):
            control = PhysicalControl(
                generator.uniform(-3.0, 3.0) * vehicle.max_acceleration_mps2,
                generator.uniform(-3.0, 3.0) * vehicle.max_steering_rate_radps,
            )
            for _ in range(config.substeps):
                previous = ego
                ego = integrate_substep(ego, control, vehicle, dt_sub_s)
                _check(result, previous, ego, vehicle, dt_sub_s)
                if audit:
                    _audit_ccd(result, previous, ego, vehicle, resolution_m)
                result.substeps += 1
        return ego

    corner = SATURATION_CORNERS[generator.randrange(4)] if mode == "saturation" else None
    world = _world(vehicle, ego)
    for _ in range(spec.policy_steps):
        if corner is None:
            action = NormalizedAction(generator.uniform(-1.0, 1.0), generator.uniform(-1.0, 1.0))
        else:
            action = NormalizedAction(*corner)
        previous = world.ego
        world, trace = step_world_state(world, action, config)
        for state in trace.substeps:
            _check(result, previous, state, vehicle, dt_sub_s)
            if audit:
                _audit_ccd(result, previous, state, vehicle, resolution_m)
            previous = state
            result.substeps += 1
    return world.ego


def run_chunk(
    spec: StressSpec,
    vehicle: VehicleSpec,
    chunk_index: int,
    *,
    disable_clamps: bool = False,
) -> ChunkResult:
    """Run one deterministic chunk of sequences against the production dynamics."""

    if disable_clamps:
        with clamps_disabled():
            return run_chunk(spec, vehicle, chunk_index)

    generator = random.Random(spec.base_seed * 1_000_003 + chunk_index)
    config = DynamicsConfig()
    resolution_m = SweepConfig().max_point_motion_m
    result = ChunkResult()
    hasher = hashlib.sha256()
    first = chunk_index * spec.chunk_size
    count = min(spec.chunk_size, spec.sequences - first)

    for offset in range(count):
        sequence_index = first + offset
        latency = generator.randrange(3)
        realized = replace(vehicle, latency_steps=latency, max_latency_steps=2)
        ego = _random_ego(generator, realized)
        draw = generator.random()
        audit = sequence_index % spec.ccd_audit_every == 0
        result.sequences += 1
        result.latency_sequences[latency] += 1
        if draw < spec.raw_control_fraction:
            result.raw_control_sequences += 1
            mode = "raw"
        elif draw < spec.raw_control_fraction + spec.saturation_fraction:
            result.saturation_sequences += 1
            mode = "saturation"
        else:
            mode = "random"
        try:
            ego = _run_sequence(
                spec, realized, ego, mode, generator, result, audit, config, resolution_m
            )
        except ValueError:
            # Only reachable with clamps disabled: the integrator's entry guard rejects
            # a state that already left its limits, after _check has counted it.
            if not dynamics_clamps_are_disabled():
                raise
            result.guard_trips += 1
            continue
        hasher.update(
            struct.pack(
                "<5d",
                ego.pose.x_m,
                ego.pose.y_m,
                ego.pose.heading_rad,
                ego.speed_mps,
                ego.steering_rad,
            )
        )

    result.digest = hasher.hexdigest()
    return result


def _run_chunk_star(arguments: tuple[StressSpec, VehicleSpec, int, bool]) -> ChunkResult:
    spec, vehicle, chunk_index, disable_clamps = arguments
    return run_chunk(spec, vehicle, chunk_index, disable_clamps=disable_clamps)


def run_stress(
    spec: StressSpec,
    vehicle: VehicleSpec,
    *,
    workers: int = 1,
    disable_clamps: bool = False,
    progress: bool = False,
) -> tuple[ChunkResult, float]:
    """Run every chunk, in parallel when ``workers > 1``; return the merged result and seconds."""

    started = time.perf_counter()
    jobs = [(spec, vehicle, index, disable_clamps) for index in range(spec.chunks)]
    merged = ChunkResult()
    if workers <= 1:
        results: Iterator[ChunkResult] = map(_run_chunk_star, jobs)
        for done, chunk in enumerate(results, start=1):
            merged.merge(chunk)
            if progress:
                _report(done, spec.chunks, started)
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            for done, chunk in enumerate(pool.map(_run_chunk_star, jobs, chunksize=1), start=1):
                merged.merge(chunk)
                if progress:
                    _report(done, spec.chunks, started)
    return merged, time.perf_counter() - started


def _report(done: int, total: int, started: float) -> None:
    if done == total or done % max(1, total // 100) == 0:
        elapsed = time.perf_counter() - started
        remaining = elapsed / done * (total - done)
        print(f"{done}/{total} chunks, {elapsed:.0f}s elapsed, ~{remaining:.0f}s left", flush=True)


def summary(result: ChunkResult, spec: StressSpec, seconds: float) -> dict[str, object]:
    """JSON-ready evidence record for one run."""

    ccd = result.ccd_substeps or 1
    return {
        "spec": asdict(spec),
        "seconds": round(seconds, 1),
        "sequences": result.sequences,
        "substeps": result.substeps,
        "saturation_sequences": result.saturation_sequences,
        "raw_control_sequences": result.raw_control_sequences,
        "latency_sequences": result.latency_sequences,
        "violations": result.violations,
        "total_violations": sum(result.violations.values()),
        "integrator_guard_trips": result.guard_trips,
        "max_value_over_limit": result.max_ratio,
        "ccd_audit": {
            "substeps": result.ccd_substeps,
            "mean_samples_conservative_bound": result.ccd_bound_samples / ccd,
            "mean_samples_exact_corner_motion": result.ccd_exact_samples / ccd,
            "max_samples_conservative_bound": result.ccd_max_bound_samples,
            "max_samples_exact_corner_motion": result.ccd_max_exact_samples,
            "max_conservative_bound_m": result.ccd_max_bound_m,
            "max_exact_corner_motion_m": result.ccd_max_exact_m,
        },
        "final_state_sha256": result.digest,
    }
