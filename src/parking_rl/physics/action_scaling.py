"""The single boundary from policy actions to simulator controls."""

from __future__ import annotations

from parking_rl.core.actions import NormalizedAction, PhysicalControl
from parking_rl.core.state import VehicleSpec


def scale_action(action: NormalizedAction, vehicle: VehicleSpec) -> PhysicalControl:
    """Scale a normalized policy action into physical actuator units.

    Keeping this conversion in one module prevents policies, wrappers, and the
    dynamics kernel from silently acquiring different actuator semantics.
    """

    if type(action) is not NormalizedAction:
        raise TypeError("action must be exactly NormalizedAction")
    if type(vehicle) is not VehicleSpec:
        raise TypeError("vehicle must be exactly VehicleSpec")
    return PhysicalControl(
        acceleration_mps2=vehicle.max_acceleration_mps2 * action.longitudinal,
        steering_rate_radps=vehicle.max_steering_rate_radps * action.steering_rate,
    )
