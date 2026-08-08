import json
from pathlib import Path

import pytest

from parking_rl.governance.exit_registry import (
    ExitRegistryError,
    validate_exit_registry,
)

ROOT = Path(__file__).resolve().parents[1]


def test_checked_in_registry_covers_all_roadmap_exit_contracts():
    assert validate_exit_registry(ROOT / "contracts" / "exit_registry.json") == 86


def test_missing_exit_contract_is_rejected(tmp_path):
    source = ROOT / "contracts" / "exit_registry.json"
    registry = json.loads(source.read_text(encoding="utf-8"))
    registry["groups"][0]["ids"].remove("EXIT-0.1")
    target = tmp_path / "exit_registry.json"
    target.write_text(json.dumps(registry), encoding="utf-8")

    with pytest.raises(ExitRegistryError, match="missing"):
        validate_exit_registry(target)


def test_implemented_exit_requires_pytest_node_ids(tmp_path):
    source = ROOT / "contracts" / "exit_registry.json"
    registry = json.loads(source.read_text(encoding="utf-8"))
    registry["statuses"]["EXIT-0.1"] = "implemented"
    target = tmp_path / "exit_registry.json"
    target.write_text(json.dumps(registry), encoding="utf-8")

    with pytest.raises(ExitRegistryError, match="lack tests"):
        validate_exit_registry(target)
