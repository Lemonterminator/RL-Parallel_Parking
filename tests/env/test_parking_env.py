from __future__ import annotations

import math
import random

import numpy as np
import pytest
from gymnasium.utils.env_checker import check_env

from parking_rl.core.actions import NormalizedAction
from parking_rl.core.frames import RearAxleWorldPose
from parking_rl.core.state import EgoState
from parking_rl.env import SMOKE_REWARD, ParallelParkingEnv
from parking_rl.env.reward import running_costs


def test_env_passes_gymnasium_checker() -> None:
    check_env(ParallelParkingEnv(), skip_render_check=True)


def test_observation_matches_layout_and_is_reproducible() -> None:
    first, second = ParallelParkingEnv(), ParallelParkingEnv()
    obs_a, _ = first.reset(seed=7)
    obs_b, _ = second.reset(seed=7)
    assert obs_a.shape == (first.layout.width,)
    assert obs_a.dtype == np.float32
    np.testing.assert_array_equal(obs_a, obs_b)
    rng = np.random.default_rng(3)
    for _ in range(50):
        action = rng.uniform(-1, 1, 2).astype(np.float32)
        out_a = first.step(action)
        out_b = second.step(action)
        np.testing.assert_array_equal(out_a[0], out_b[0])
        assert out_a[1:4] == out_b[1:4]
        if out_a[2] or out_a[3]:
            break


def test_resting_at_goal_succeeds_after_exactly_the_settle_window() -> None:
    env = ParallelParkingEnv()
    env.reset(seed=0, options={"initial_ego": EgoState(RearAxleWorldPose(0.0, 0.0, 0.0), 0.0, 0.0)})
    zero = np.zeros(2, dtype=np.float32)
    for _ in range(env.settle_steps - 1):
        _, _, terminated, truncated, info = env.step(zero)
        assert not terminated and not truncated
        assert info["end_reason"] == "none"
    _, reward, terminated, _, info = env.step(zero)
    assert terminated and info["end_reason"] == "success"
    assert reward > SMOKE_REWARD.r_success - 1.0


def test_driving_into_the_rear_car_is_a_collision() -> None:
    env = ParallelParkingEnv()
    env.reset(seed=0, options={"initial_ego": EgoState(RearAxleWorldPose(0.0, 0.0, 0.0), 0.0, 0.0)})
    for _ in range(100):
        _, reward, terminated, _, info = env.step(np.array([-1.0, 0.0], dtype=np.float32))
        if terminated:
            break
    assert info["end_reason"] == "collision"
    components = info["reward_components"]
    # Phi(terminal) = 0, so the collision step refunds -Phi(s); the episode's total shaping
    # still telescopes to -Phi(s0) whatever the path.
    assert components.phi_s_next == 0.0
    assert reward == pytest.approx(
        -SMOKE_REWARD.p_collision
        - components.phi_s
        - components.time_cost_raw
        - components.action_cost_raw
        - SMOKE_REWARD.w_gear * components.gear_flag
    )


def test_shaping_telescopes_over_an_episode() -> None:
    """sum_t gamma^t F_t == gamma^T Phi(s_T) - Phi(s_0), with Phi(terminal) = 0."""

    env = ParallelParkingEnv()
    env.reset(seed=11)
    gamma = env.reward_config.gamma
    rng = np.random.default_rng(11)
    discounted, phi0, last = 0.0, None, None
    for t in range(400):
        _, _, terminated, truncated, info = env.step(rng.uniform(-1, 1, 2))
        components = info["reward_components"]
        if phi0 is None:
            phi0 = components.phi_s
        discounted += gamma**t * (gamma * components.phi_s_next - components.phi_s)
        last = (t, components.phi_s_next)
        if terminated or truncated:
            break
    t, phi_last = last
    assert discounted == pytest.approx(gamma ** (t + 1) * phi_last - phi0, abs=1e-9)


def test_reward_config_satisfies_exit_2_7_no_suicide_and_states_exit_2_28_bound() -> None:
    config = SMOKE_REWARD
    assert config.c_max == pytest.approx(0.05)
    assert config.no_suicide_bound() == pytest.approx(17.3068, abs=1e-3)
    assert config.p_collision >= config.no_suicide_bound()
    assert config.critic_bound() == pytest.approx(0.05 * 173.068 + 100 + 30, abs=1e-2)


def test_running_terms_are_never_positive() -> None:
    rng = random.Random(0)
    for _ in range(1000):
        action = NormalizedAction(rng.uniform(-1, 1), rng.uniform(-1, 1))
        time_cost, action_cost, _ = running_costs(
            action, rng.uniform(-1.5, 1.5), rng.uniform(-1.5, 1.5), SMOKE_REWARD
        )
        assert time_cost >= 0 and action_cost >= 0


def test_goal_pose_has_zero_clearance_penalty_and_maximal_potential() -> None:
    env = ParallelParkingEnv()
    goal = EgoState(RearAxleWorldPose(0.0, 0.0, 0.0), 0.0, 0.0)
    phi_goal, penetration = env._potential(env._initial_world(goal))
    assert penetration == 0.0
    assert phi_goal == 0.0
    off = EgoState(RearAxleWorldPose(0.5, -0.5, math.radians(10)), 0.0, 0.0)
    assert env._potential(env._initial_world(off))[0] < 0.0
