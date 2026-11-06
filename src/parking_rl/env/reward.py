"""Potential-based shaped reward following ROADMAP §7 (smoke-rehearsal weights).

Components are returned separately (§7.6) so the scalar can be recomposed from new weights.
Only terminal rewards are positive (§7.4); every running term is <= 0 apart from the PBRS
difference ``gamma * Phi(s') - Phi(s)``. ``Phi`` is zero at terminal states but **not** at
truncation (§7.1).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from parking_rl.core.actions import NormalizedAction
from parking_rl.core.frames import GoalRearAxleWorldPose, rear_axle_world_to_goal_error
from parking_rl.core.outcomes import EpisodeEndReason
from parking_rl.core.state import EgoState, ObjectKind, ObjectState, VehicleSpec
from parking_rl.reward.heading import heading_half_angle_cost
from parking_rl.reward_geometry.circles import body_circle_cover


@dataclass(frozen=True, slots=True)
class RewardConfig:
    """§7.2 weights at the tolerances; ``k_scale`` is the frozen global multiplier."""

    gamma: float = 0.995
    max_steps: int = 400
    r_success: float = 100.0
    p_collision: float = 40.0
    phi_clip: float = 30.0
    k_scale: float = 1.0
    w_x: float = 0.25
    w_y: float = 1.0
    w_th: float = 10.50
    w_v: float = 0.3
    w_d: float = 0.3
    w_c: float = 100.0
    d_safe_m: float = 0.10
    w_time: float = 0.02
    w_a: float = 0.01
    w_s: float = 0.01
    w_gear: float = 0.01
    gear_hysteresis_mps: float = 0.05

    @property
    def c_max(self) -> float:
        """Largest per-step running cost magnitude."""

        return self.w_time + self.w_a + self.w_s + self.w_gear

    def no_suicide_bound(self) -> float:
        """EXIT-2.7 lower bound on the collision penalty."""

        return 2.0 * self.c_max * (1.0 - self.gamma**self.max_steps) / (1.0 - self.gamma)

    def critic_bound(self) -> float:
        """EXIT-2.28 magnitude bound ``B`` (with beta = 0: no graded success bonus here)."""

        discounted = self.c_max * (1.0 - self.gamma**self.max_steps) / (1.0 - self.gamma)
        return discounted + max(abs(self.r_success), abs(self.p_collision)) + self.phi_clip


@dataclass(frozen=True, slots=True)
class RewardComponents:
    phi_s: float
    phi_s_next: float
    terminal_kind: EpisodeEndReason
    time_cost_raw: float
    action_cost_raw: float
    gear_flag: bool
    clearance_penetration: float
    settle_counter: int

    def total(self, config: RewardConfig) -> float:
        shaping = config.gamma * self.phi_s_next - self.phi_s
        running = -(self.time_cost_raw + self.action_cost_raw + config.w_gear * self.gear_flag)
        terminal = {
            EpisodeEndReason.SUCCESS: config.r_success,
            EpisodeEndReason.COLLISION: -config.p_collision,
            EpisodeEndReason.OUT_OF_BOUNDS: -config.p_collision,
        }.get(self.terminal_kind, 0.0)
        return shaping + running + terminal


def _point_obb_distance(px: float, py: float, obj: ObjectState) -> float:
    c, s = math.cos(obj.pose.heading_rad), math.sin(obj.pose.heading_rad)
    dx, dy = px - obj.pose.x_m, py - obj.pose.y_m
    lx, ly = c * dx + s * dy, -s * dx + c * dy
    ex = max(abs(lx) - 0.5 * obj.length_m, 0.0)
    ey = max(abs(ly) - 0.5 * obj.width_m, 0.0)
    return math.hypot(ex, ey)


def clearance_penetration(
    ego: EgoState, vehicle: VehicleSpec, objects: tuple[ObjectState, ...], d_safe_m: float
) -> float:
    """``sum_j sum_k max(0, d_safe - dist(circle_j, obstacle_k))^2`` (reward path only, I5)."""

    total = 0.0
    c, s = math.cos(ego.pose.heading_rad), math.sin(ego.pose.heading_rad)
    for circle in body_circle_cover(vehicle):
        cx = ego.pose.x_m + c * circle.center_x_m - s * circle.center_y_m
        cy = ego.pose.y_m + s * circle.center_x_m + c * circle.center_y_m
        for obj in objects:
            if obj.kind is ObjectKind.GOAL_SLOT:
                continue
            gap = _point_obb_distance(cx, cy, obj) - circle.radius_m
            total += max(0.0, d_safe_m - gap) ** 2
    return total


def potential(
    ego: EgoState,
    goal: GoalRearAxleWorldPose,
    vehicle: VehicleSpec,
    objects: tuple[ObjectState, ...],
    config: RewardConfig,
) -> tuple[float, float]:
    """Return ``(Phi(s), clearance_penetration)`` for a non-terminal state."""

    error = rear_axle_world_to_goal_error(ego.pose, goal)
    penetration = clearance_penetration(ego, vehicle, objects, config.d_safe_m)
    raw = (
        config.w_x * error.longitudinal_m**2
        + config.w_y * error.lateral_m**2
        + config.w_th * heading_half_angle_cost(error.heading_error_rad)
        + config.w_v * ego.speed_mps**2
        + config.w_d * ego.steering_rad**2
        + config.w_c * penetration
    )
    return max(-config.phi_clip, -config.k_scale * raw), penetration


def running_costs(
    action: NormalizedAction, speed_before: float, speed_after: float, config: RewardConfig
) -> tuple[float, float, bool]:
    """``(time_cost, action_cost, gear_flag)``; the gear flag is a pure function of (s, s')."""

    action_cost = config.w_a * action.longitudinal**2 + config.w_s * action.steering_rate**2
    gear_flag = (
        speed_before * speed_after < 0.0
        and max(abs(speed_before), abs(speed_after)) >= config.gear_hysteresis_mps
    )
    return config.w_time, action_cost, gear_flag
