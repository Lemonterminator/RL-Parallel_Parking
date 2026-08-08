import math

import pytest

from parking_rl.core.observation import (
    Observation,
    ObservationLayout,
    ObservationRung,
    ObserverConfig,
)
from parking_rl.core.scenario import TaskFamily


def _observer(rung: ObservationRung) -> ObserverConfig:
    return ObserverConfig(
        rung=rung,
        tau_enabled=rung in {ObservationRung.O3, ObservationRung.O4},
        horizontal_fov_rad=math.pi,
        max_range_m=20.0,
        position_noise_std_m=0.1 if rung is ObservationRung.O4 else 0.0,
        dropout_probability=0.05 if rung is ObservationRung.O4 else 0.0,
    )


def test_all_rungs_share_layout_width_order_dtype_and_layout_hash():
    layouts = [ObservationLayout(max_latency_steps=2) for _ in ObservationRung]
    observations = [
        Observation(layout.empty_values(TaskFamily.PARALLEL), layout, _observer(rung))
        for layout, rung in zip(layouts, ObservationRung, strict=True)
    ]
    assert {item.layout_hash for item in observations} == {layouts[0].layout_hash}
    assert {item.layout.field_names for item in observations} == {layouts[0].field_names}
    assert {item.dtype for item in observations} == {"float32"}
    assert {len(item.values) for item in observations} == {60}
    assert len({item.observer_config_hash for item in observations}) == 5


def test_layout_uses_periodic_heading_channels_and_fixed_semantic_slots():
    names = ObservationLayout(2).field_names
    assert not any("heading_rad" in name or "theta" in name for name in names)
    for role in ("front_vehicle", "rear_vehicle", "kerb", "goal_slot"):
        assert f"object.{role}.heading_sin" in names
        assert f"object.{role}.heading_cos" in names
        assert f"object.{role}.log1p_tau_steps" in names


@pytest.mark.parametrize("rung", [ObservationRung.O0, ObservationRung.O1, ObservationRung.O2])
def test_memoryless_rungs_require_bitwise_zero_tau(rung):
    layout = ObservationLayout(2)
    values = list(layout.empty_values(TaskFamily.REVERSE_BAY))
    tau_index = layout.field_names.index("object.front_vehicle.log1p_tau_steps")
    values[tau_index] = 1.0
    with pytest.raises(ValueError, match="bitwise zero"):
        Observation(tuple(values), layout, _observer(rung))


def test_history_rung_accepts_tau_without_changing_layout_hash():
    layout = ObservationLayout(2)
    values = list(layout.empty_values(TaskFamily.REVERSE_BAY))
    values[layout.field_names.index("object.front_vehicle.log1p_tau_steps")] = math.log1p(3)
    observed = Observation(tuple(values), layout, _observer(ObservationRung.O3))
    assert observed.layout_hash == ObservationLayout(2).layout_hash


def test_family_one_hot_and_latency_queue_are_part_of_values():
    layout = ObservationLayout(2)
    base = list(layout.empty_values(TaskFamily.PARALLEL))
    queue = base.copy()
    queue[layout.field_names.index("actuator.queue_0.longitudinal")] = -0.5
    queue[layout.field_names.index("actuator.queue_0.valid")] = 1.0
    queue[layout.field_names.index("actuator.latency_steps_fraction")] = 0.5
    first = Observation(tuple(base), layout, _observer(ObservationRung.O0))
    second = Observation(tuple(queue), layout, _observer(ObservationRung.O0))
    assert first.values != second.values

    invalid = base.copy()
    invalid[layout.field_names.index("task.parallel")] = 0.0
    with pytest.raises(ValueError, match="exactly one"):
        Observation(tuple(invalid), layout, _observer(ObservationRung.O0))


def test_observation_defensively_copies_values_and_rejects_bad_masks():
    layout = ObservationLayout(2)
    mutable = list(layout.empty_values(TaskFamily.PARALLEL))
    observation = Observation(mutable, layout, _observer(ObservationRung.O0))
    mutable[0] = 1.0
    assert observation.values[0] == 0.0

    invalid = list(observation.values)
    invalid[layout.field_names.index("actuator.queue_0.valid")] = 0.5
    with pytest.raises(ValueError, match="binary"):
        Observation(invalid, layout, _observer(ObservationRung.O0))


def test_tau_mode_is_fixed_by_rung():
    with pytest.raises(ValueError, match="tau"):
        ObserverConfig(ObservationRung.O2, True, math.pi, 20.0)
    with pytest.raises(ValueError, match="tau"):
        ObserverConfig(ObservationRung.O4, False, math.pi, 20.0)
