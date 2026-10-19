"""Conservative circle covers for reward shaping only.

This module must never be imported by collision, termination, or metric code.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from parking_rl.core.state import VehicleSpec


@dataclass(frozen=True, slots=True)
class BodyCircle:
    """One local-frame circle in a conservative vehicle-body cover."""

    center_x_m: float
    center_y_m: float
    radius_m: float


def body_circle_cover(vehicle: VehicleSpec, count: int = 3) -> tuple[BodyCircle, ...]:
    """Cover equal longitudinal footprint segments with circumscribed circles."""

    if type(vehicle) is not VehicleSpec:
        raise TypeError("vehicle must be exactly VehicleSpec")
    if isinstance(count, bool) or not isinstance(count, int):
        raise TypeError("count must be an int")
    if count <= 0:
        raise ValueError("count must be positive")
    segment_length = vehicle.length_m / count
    radius = 0.5 * math.hypot(segment_length, vehicle.width_m)
    return tuple(
        BodyCircle(
            center_x_m=-vehicle.rear_overhang_m + (index + 0.5) * segment_length,
            center_y_m=0.0,
            radius_m=radius,
        )
        for index in range(count)
    )
