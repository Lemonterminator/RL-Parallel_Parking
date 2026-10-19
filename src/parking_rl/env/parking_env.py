"""Gymnasium wrapper around the Stage-0 physics kernel (smoke rehearsal, O0, parallel only).

One policy step = zero-order hold over five explicit-Euler substeps (A24), swept for collision
with the bounded CCD of EXIT-0.5. Termination priority is collision > out-of-bounds > success >
time limit (``resolve_end_reason``). Success needs ``settle_steps`` consecutive in-tolerance
steps (A22), and the settle counter is part of the observation.
"""

from __future__ import annotations

import random
from dataclasses import replace
from typing import Any

import gymnasium as gym
import numpy as np

from parking_rl.core.actions import ZERO_NORMALIZED_ACTION, NormalizedAction, PhysicalControl
from parking_rl.core.observation import ObservationLayout
from parking_rl.core.outcomes import EpisodeEndReason, resolve_end_reason
from parking_rl.core.scenario import TaskFamily
from parking_rl.core.state import (
    ActuatorState,
    EgoState,
    ObjectKind,
    SettleProgress,
    VehicleSpec,
    WorldState,
)
from parking_rl.env.observer import observe_o0
from parking_rl.env.reward import RewardComponents, RewardConfig, potential, running_costs
from parking_rl.env.scenes import parallel_scene, sample_easy_start
from parking_rl.physics.ccd import world_step_collides
from parking_rl.physics.dynamics import DynamicsConfig, step_world_state
from parking_rl.physics.geometry import object_obb, sat_overlap, vehicle_obb
from parking_rl.physics.success import SuccessTolerance, advance_settle, success_candidate

# §7.2 tolerances: dx 0.20 m, dy 0.10 m, heading 5 deg, speed 0.05 m/s. §7.5 has no steering
# condition, so the steering channel is set to the actuator limit (non-binding).
SMOKE_TOLERANCE = SuccessTolerance(0.20, 0.10, 0.08727, 0.05, 0.6)

# §7.2 global scale, calibrated once so that p95 |Phi(s0)| = 20 over the smoke start distribution
# (20 000 samples from sample_easy_start, seed 123: p95 raw potential 12.68). Frozen here.
SMOKE_REWARD = RewardConfig(k_scale=1.58)


def smoke_vehicle() -> VehicleSpec:
    return VehicleSpec(2.7, 4.7, 1.85, 0.9, 1.1, 0.6, 0.6, 1.5, 1.5, max_latency_steps=2)


class ParallelParkingEnv(gym.Env[np.ndarray, np.ndarray]):
    metadata: dict[str, Any] = {"render_modes": []}  # noqa: RUF012

    def __init__(
        self,
        slot_length_m: float = 7.05,
        reward_config: RewardConfig | None = None,
        tolerance: SuccessTolerance = SMOKE_TOLERANCE,
        settle_steps: int = 5,
        vehicle: VehicleSpec | None = None,
    ) -> None:
        self.vehicle = vehicle or smoke_vehicle()
        self.scene = parallel_scene(self.vehicle, slot_length_m)
        self.reward_config = reward_config or SMOKE_REWARD
        self.tolerance = tolerance
        self.settle_steps = settle_steps
        self.layout = ObservationLayout(max_latency_steps=self.vehicle.max_latency_steps)
        self.dynamics = DynamicsConfig()
        self.observation_space = gym.spaces.Box(
            -np.inf, np.inf, shape=(self.layout.width,), dtype=np.float32
        )
        self.action_space = gym.spaces.Box(-1.0, 1.0, shape=(2,), dtype=np.float32)
        self._solids = tuple(
            obj for obj in self.scene.static_world.objects if obj.kind is not ObjectKind.GOAL_SLOT
        )
        self._rng = random.Random()
        self._world: WorldState | None = None
        self._phi = 0.0
        self._steps = 0

    def _initial_world(self, ego: EgoState | None) -> WorldState:
        if ego is None:
            ego = sample_easy_start(self._rng, self.scene, self.vehicle)
        return WorldState(
            vehicle=self.vehicle,
            static_world=self.scene.static_world,
            ego=ego,
            objects=self.scene.static_world.objects,
            settle=SettleProgress(0, self.settle_steps),
            actuator=ActuatorState(
                applied_control=PhysicalControl(0.0, 0.0),
                pending_commands=(ZERO_NORMALIZED_ACTION,) * self.vehicle.max_latency_steps,
                latency_steps=self.vehicle.latency_steps,
            ),
        )

    def reset(
        self, *, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[np.ndarray, dict[str, Any]]:
        super().reset(seed=seed)
        if seed is not None:
            self._rng.seed(seed)
        initial_ego = (options or {}).get("initial_ego")
        if initial_ego is not None and type(initial_ego) is not EgoState:
            raise TypeError("options['initial_ego'] must be exactly EgoState")
        self._world = self._initial_world(initial_ego)
        self._phi, _ = self._potential(self._world)
        self._steps = 0
        return observe_o0(self._world, self.layout, TaskFamily.PARALLEL), {}

    def _potential(self, world: WorldState) -> tuple[float, float]:
        return potential(
            world.ego, self.scene.goal, self.vehicle, self._solids, self.reward_config
        )

    def step(
        self, action: np.ndarray
    ) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        if self._world is None:
            raise RuntimeError("call reset() before step()")
        clipped = np.clip(np.asarray(action, dtype=np.float64), -1.0, 1.0)
        command = NormalizedAction(float(clipped[0]), float(clipped[1]))
        before = self._world
        after, trace = step_world_state(before, command, self.dynamics)
        sweep = world_step_collides(before, trace)
        self._steps += 1

        collision = out_of_bounds = False
        if sweep.collides:
            hit = vehicle_obb(sweep.first_collision_pose, self.vehicle)
            collision = any(sat_overlap(hit, object_obb(obj)) for obj in self._solids)
            out_of_bounds = not collision
        candidate = success_candidate(after.ego, self.scene.goal, self.tolerance)
        settle = advance_settle(candidate, after.settle)
        after = replace(after, settle=settle)
        reason = resolve_end_reason(
            collision=collision,
            out_of_bounds=out_of_bounds,
            success=settle.count >= settle.required_steps,
            time_limit=self._steps >= self.reward_config.max_steps,
        )
        terminated = reason in {
            EpisodeEndReason.COLLISION,
            EpisodeEndReason.OUT_OF_BOUNDS,
            EpisodeEndReason.SUCCESS,
        }
        truncated = reason is EpisodeEndReason.TIME_LIMIT

        phi_next, penetration = (0.0, 0.0) if terminated else self._potential(after)
        time_cost, action_cost, gear_flag = running_costs(
            command, before.ego.speed_mps, after.ego.speed_mps, self.reward_config
        )
        components = RewardComponents(
            phi_s=self._phi,
            phi_s_next=phi_next,
            terminal_kind=reason,
            time_cost_raw=time_cost,
            action_cost_raw=action_cost,
            gear_flag=gear_flag,
            clearance_penetration=penetration,
            settle_counter=settle.count,
        )
        reward = components.total(self.reward_config)
        self._world = after
        self._phi = phi_next
        info = {"end_reason": reason.value, "reward_components": components}
        return (
            observe_o0(after, self.layout, TaskFamily.PARALLEL),
            float(reward),
            terminated,
            truncated,
            info,
        )
