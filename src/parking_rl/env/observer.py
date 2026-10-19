"""Minimal O0 observer: the full-state, ego-centric vector of ``ObservationLayout``.

Every object slot is valid and visible (O0 has no sensor model) and tau fields are zero.
Object poses are expressed in the ego rear-axle frame.
"""

from __future__ import annotations

import math

import numpy as np

from parking_rl.core.observation import ObservationLayout
from parking_rl.core.scenario import TaskFamily
from parking_rl.core.state import ObjectKind, WorldState


def observe_o0(world: WorldState, layout: ObservationLayout, family: TaskFamily) -> np.ndarray:
    values = np.zeros(layout.width, dtype=np.float32)
    index = {name: position for position, name in enumerate(layout.field_names)}
    vehicle = world.vehicle
    ego = world.ego
    settle = world.settle

    values[index["ego.speed_fraction"]] = ego.speed_mps / vehicle.max_speed_mps
    values[index["ego.steering_fraction"]] = ego.steering_rad / vehicle.max_steering_angle_rad
    values[index["ego.settle_progress_fraction"]] = settle.count / settle.required_steps
    values[index[f"task.{family.value}"]] = 1.0
    if layout.max_latency_steps:
        values[index["actuator.latency_steps_fraction"]] = (
            world.actuator.latency_steps / layout.max_latency_steps
        )
        for slot, command in enumerate(world.actuator.active_pending_commands):
            prefix = f"actuator.queue_{slot}"
            values[index[f"{prefix}.longitudinal"]] = command.longitudinal
            values[index[f"{prefix}.steering_rate"]] = command.steering_rate
            values[index[f"{prefix}.valid"]] = 1.0

    c, s = math.cos(ego.pose.heading_rad), math.sin(ego.pose.heading_rad)
    by_role = {obj.role: obj for obj in world.objects}
    for role in layout.object_slots:
        obj = by_role[role]
        prefix = f"object.{role.value}"
        dx = obj.pose.x_m - ego.pose.x_m
        dy = obj.pose.y_m - ego.pose.y_m
        relative_heading = obj.pose.heading_rad - ego.pose.heading_rad
        values[index[f"{prefix}.relative_x_m"]] = c * dx + s * dy
        values[index[f"{prefix}.relative_y_m"]] = -s * dx + c * dy
        values[index[f"{prefix}.heading_sin"]] = math.sin(relative_heading)
        values[index[f"{prefix}.heading_cos"]] = math.cos(relative_heading)
        values[index[f"{prefix}.length_m"]] = obj.length_m
        values[index[f"{prefix}.width_m"]] = obj.width_m
        values[index[f"{prefix}.type_vehicle"]] = obj.kind is ObjectKind.VEHICLE
        values[index[f"{prefix}.type_kerb"]] = obj.kind is ObjectKind.KERB
        values[index[f"{prefix}.type_goal_slot"]] = obj.kind is ObjectKind.GOAL_SLOT
        values[index[f"{prefix}.valid"]] = 1.0
        values[index[f"{prefix}.visible_now"]] = 1.0
    return values
