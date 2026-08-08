"""Optional trajectory visualization built from recorded physics traces."""

from __future__ import annotations

import math
from dataclasses import dataclass
from numbers import Real
from typing import Any

from parking_rl.core.frames import RearAxleWorldPose
from parking_rl.physics.collision import solid_obstacles
from parking_rl.physics.geometry import Point2, obb_corners, object_obb, vehicle_obb
from parking_rl.physics.replay import EpisodeTrace


def _require_nonnegative_int(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an int, not {type(value).__name__}")
    if value < 0:
        raise ValueError(f"{name} must be nonnegative")


@dataclass(frozen=True, slots=True)
class ReplayFrame:
    """A renderable ego footprint at one recorded integration boundary."""

    policy_step_index: int
    substep_index: int
    time_s: float
    rear_axle_pose: RearAxleWorldPose
    body_corners: tuple[Point2, Point2, Point2, Point2]

    def __post_init__(self) -> None:
        _require_nonnegative_int("policy_step_index", self.policy_step_index)
        _require_nonnegative_int("substep_index", self.substep_index)
        if isinstance(self.time_s, bool) or not isinstance(self.time_s, Real):
            raise TypeError(f"time_s must be a real number, not {type(self.time_s).__name__}")
        if not math.isfinite(self.time_s) or self.time_s < 0:
            raise ValueError("time_s must be finite and nonnegative")
        if type(self.rear_axle_pose) is not RearAxleWorldPose:
            raise TypeError("rear_axle_pose must be exactly RearAxleWorldPose")
        try:
            corners = tuple(tuple(point) for point in self.body_corners)
        except TypeError as error:
            raise TypeError("body_corners must be an iterable of four 2D points") from error
        if len(corners) != 4 or any(len(point) != 2 for point in corners):
            raise ValueError("body_corners must contain exactly four 2D points")
        for point in corners:
            for coordinate in point:
                if isinstance(coordinate, bool) or not isinstance(coordinate, Real):
                    raise TypeError("body_corners coordinates must be real numbers")
                if not math.isfinite(coordinate):
                    raise ValueError("body_corners coordinates must be finite")
        object.__setattr__(self, "body_corners", corners)


def _frame(
    trace: EpisodeTrace,
    policy_step_index: int,
    substep_index: int,
    time_s: float,
    pose: RearAxleWorldPose,
) -> ReplayFrame:
    return ReplayFrame(
        policy_step_index=policy_step_index,
        substep_index=substep_index,
        time_s=time_s,
        rear_axle_pose=pose,
        body_corners=obb_corners(vehicle_obb(pose, trace.initial_state.vehicle)),
    )


def replay_frames(trace: EpisodeTrace) -> tuple[ReplayFrame, ...]:
    """Return the initial frame plus every one of the five recorded substeps."""

    if type(trace) is not EpisodeTrace:
        raise TypeError("trace must be exactly EpisodeTrace")
    frames = [_frame(trace, 0, 0, 0.0, trace.initial_state.ego.pose)]
    elapsed_substeps = 0
    for policy_index, policy_step in enumerate(trace.policy_steps, start=1):
        for substep_index, ego in enumerate(policy_step.substeps, start=1):
            elapsed_substeps += 1
            frames.append(
                _frame(
                    trace,
                    policy_index,
                    substep_index,
                    elapsed_substeps * trace.dynamics_config.dt_sub_s,
                    ego.pose,
                )
            )
    return tuple(frames)


def animate_trajectory(trace: EpisodeTrace, interval_ms: int = 50) -> Any:
    """Create a matplotlib animation without making matplotlib a core dependency."""

    if type(trace) is not EpisodeTrace:
        raise TypeError("trace must be exactly EpisodeTrace")
    if isinstance(interval_ms, bool) or not isinstance(interval_ms, int):
        raise TypeError(f"interval_ms must be an int, not {type(interval_ms).__name__}")
    if interval_ms <= 0:
        raise ValueError("interval_ms must be positive")
    try:
        from matplotlib import pyplot as plt
        from matplotlib.animation import FuncAnimation
        from matplotlib.patches import Polygon
    except (ImportError, ModuleNotFoundError) as error:
        raise RuntimeError(
            "trajectory animation requires the optional 'matplotlib' package"
        ) from error

    frames = replay_frames(trace)
    world = trace.initial_state.static_world
    figure, axes = plt.subplots()
    bounds = world.bounds
    axes.set_xlim(bounds.min_x_m, bounds.max_x_m)
    axes.set_ylim(bounds.min_y_m, bounds.max_y_m)
    axes.set_aspect("equal", adjustable="box")
    axes.set_xlabel("world x (m)")
    axes.set_ylabel("world y (m)")
    axes.set_title("Trajectory replay")

    for obstacle in solid_obstacles(trace.initial_state.objects):
        axes.add_patch(
            Polygon(
                obb_corners(object_obb(obstacle)),
                closed=True,
                facecolor="0.65",
                edgecolor="0.2",
            )
        )
    ego_patch = Polygon(
        frames[0].body_corners,
        closed=True,
        facecolor="tab:blue",
        edgecolor="navy",
        alpha=0.75,
    )
    axes.add_patch(ego_patch)
    timestamp = axes.text(0.02, 0.98, "", transform=axes.transAxes, va="top")

    def update(frame_index: int) -> tuple[Any, Any]:
        replay_frame = frames[frame_index]
        ego_patch.set_xy(replay_frame.body_corners)
        timestamp.set_text(
            f"step {replay_frame.policy_step_index}, "
            f"substep {replay_frame.substep_index}, t={replay_frame.time_s:.3f}s"
        )
        return ego_patch, timestamp

    animation = FuncAnimation(
        figure,
        update,
        frames=len(frames),
        interval=interval_ms,
        blit=True,
        repeat=False,
    )
    return animation
