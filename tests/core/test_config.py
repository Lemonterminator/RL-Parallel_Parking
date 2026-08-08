import copy
import json
from pathlib import Path

import pytest

from parking_rl.core.config import ConfigSchemaError, load_reference_config
from parking_rl.core.scenario import TaskFamily

ROOT = Path(__file__).parents[2]
REFERENCE = ROOT / "configs" / "reference.json"


def _data():
    return json.loads(REFERENCE.read_text(encoding="utf-8"))


def _write(tmp_path, data) -> Path:
    path = tmp_path / "config.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_reference_config_parses_to_typed_contracts():
    config = load_reference_config(REFERENCE)
    assert config.project.task_families == (TaskFamily.PARALLEL, TaskFamily.REVERSE_BAY)
    assert config.vehicle.length_m == pytest.approx(4.7)
    assert config.observation_layout.width == 60
    assert config.observation_layout.max_latency_steps == config.vehicle.max_latency_steps
    assert config.reverse_bay_reference.difficulty.free_mouth_width_m == pytest.approx(2.5)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda data: data.update({"unknown": 1}),
        lambda data: data.pop("project"),
        lambda data: data["vehicle"].update({"mystery": 1}),
        lambda data: data["reverse_bay_reference"].pop("free_mouth_width_m"),
    ],
)
def test_unknown_and_missing_keys_are_rejected(tmp_path, mutation):
    data = _data()
    mutation(data)
    with pytest.raises(ConfigSchemaError, match=r"missing|unknown"):
        load_reference_config(_write(tmp_path, data))


@pytest.mark.parametrize(
    "mutation",
    [
        lambda data: data["integration"].update(max_steps=True),
        lambda data: data["integration"].update(substeps=4),
        lambda data: data["integration"].update(scheme="rk4"),
        lambda data: data["integration"].update(action_hold="linear"),
        lambda data: data["project"].update(single_scenario_conditioned_policy=False),
        lambda data: data["project"].update(task_families=["parallel"]),
        lambda data: data["task"].update(
            terminal_priority=["success", "collision", "out_of_bounds", "timeout"]
        ),
        lambda data: data["evaluation"].update(test_evaluation_budget=4),
        lambda data: data["vehicle"].update(length_m=4.8),
        lambda data: data["observation"].update(max_latency_steps=1),
        lambda data: data["learning"].update(discount=1.0),
    ],
)
def test_cross_field_and_type_mutations_are_rejected(tmp_path, mutation):
    data = copy.deepcopy(_data())
    mutation(data)
    with pytest.raises(ConfigSchemaError):
        load_reference_config(_write(tmp_path, data))


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_non_finite_json_numbers_are_rejected_before_schema_parse(tmp_path, constant):
    text = REFERENCE.read_text(encoding="utf-8").replace("0.995", constant)
    path = tmp_path / "config.json"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ConfigSchemaError, match="non-finite"):
        load_reference_config(path)
