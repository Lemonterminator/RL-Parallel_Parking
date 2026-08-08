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
    del registry["tests"]["EXIT-0.1"]
    target = tmp_path / "exit_registry.json"
    target.write_text(json.dumps(registry), encoding="utf-8")

    with pytest.raises(ExitRegistryError, match="lack tests"):
        validate_exit_registry(target)


def test_registry_rejects_missing_pytest_function(tmp_path):
    source = ROOT / "contracts" / "exit_registry.json"
    registry = json.loads(source.read_text(encoding="utf-8"))
    registry["tests"]["EXIT-0.1"] = [
        "tests/exit_criteria/test_stage0_exit.py::test_does_not_exist"
    ]
    target = tmp_path / "exit_registry.json"
    target.write_text(json.dumps(registry), encoding="utf-8")

    with pytest.raises(ExitRegistryError, match="function does not exist"):
        validate_exit_registry(target)


def test_implemented_clause_requires_its_own_test_mapping(tmp_path):
    source = ROOT / "contracts" / "exit_registry.json"
    registry = json.loads(source.read_text(encoding="utf-8"))
    del registry["clause_tests"]["EXIT-0.14"]["a"]
    target = tmp_path / "exit_registry.json"
    target.write_text(json.dumps(registry), encoding="utf-8")

    with pytest.raises(ExitRegistryError, match=r"clauses.*lack tests"):
        validate_exit_registry(target)


def test_composite_exit_cannot_close_before_every_clause(tmp_path):
    source = ROOT / "contracts" / "exit_registry.json"
    registry = json.loads(source.read_text(encoding="utf-8"))
    registry["statuses"]["EXIT-0.14"] = "implemented"
    registry["tests"]["EXIT-0.14"] = [
        "tests/physics/test_bay_geometry.py::test_static_containment_design_table_and_single_cut_bracket"
    ]
    target = tmp_path / "exit_registry.json"
    target.write_text(json.dumps(registry), encoding="utf-8")

    with pytest.raises(ExitRegistryError, match="cannot be implemented"):
        validate_exit_registry(target)
