"""Validation for the machine-readable ROADMAP EXIT registry."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ExitRegistryError(ValueError):
    """Raised when the EXIT registry does not cover the roadmap exactly."""


_EXIT_COUNTS = {"0": 15, "1": 14, "2": 29, "3": 11, "4": 12, "6": 5}
EXPECTED_EXIT_IDS = frozenset(
    f"EXIT-{stage}.{index}"
    for stage, count in _EXIT_COUNTS.items()
    for index in range(1, count + 1)
)


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ExitRegistryError(f"Cannot read EXIT registry {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ExitRegistryError("EXIT registry root must be a JSON object")
    return value


def validate_exit_registry(registry_path: str | Path) -> int:
    """Validate complete coverage, ownership, overrides, and implemented test mappings."""
    data = _load(Path(registry_path))
    if data.get("schema_version") != 1:
        raise ExitRegistryError("Unsupported EXIT registry schema")

    groups = data.get("groups")
    if not isinstance(groups, list) or not groups:
        raise ExitRegistryError("EXIT registry groups must be a non-empty list")

    seen: list[str] = []
    for group in groups:
        if not isinstance(group, dict):
            raise ExitRegistryError("Every EXIT group must be an object")
        for field in ("owner_phase", "spec", "ids"):
            if field not in group:
                raise ExitRegistryError(f"EXIT group is missing {field}")
        if not isinstance(group["ids"], list) or not all(
            isinstance(exit_id, str) for exit_id in group["ids"]
        ):
            raise ExitRegistryError("EXIT group ids must be a list of strings")
        seen.extend(group["ids"])

    duplicates = sorted({exit_id for exit_id in seen if seen.count(exit_id) > 1})
    if duplicates:
        raise ExitRegistryError(f"Duplicate EXIT IDs: {', '.join(duplicates)}")
    actual = set(seen)
    missing = sorted(EXPECTED_EXIT_IDS - actual)
    unknown = sorted(actual - EXPECTED_EXIT_IDS)
    if missing or unknown:
        raise ExitRegistryError(f"EXIT coverage mismatch; missing={missing}, unknown={unknown}")

    overrides = data.get("overrides", {})
    statuses = data.get("statuses", {})
    tests = data.get("tests", {})
    if not isinstance(overrides, dict) or not set(overrides).issubset(actual):
        raise ExitRegistryError("EXIT overrides must be an object keyed only by registered IDs")
    if not isinstance(statuses, dict) or not set(statuses).issubset(actual):
        raise ExitRegistryError("EXIT statuses must be an object keyed only by registered IDs")
    if any(status not in {"planned", "implemented", "retired"} for status in statuses.values()):
        raise ExitRegistryError("EXIT statuses may only be planned, implemented, or retired")
    if not isinstance(tests, dict) or not set(tests).issubset(actual):
        raise ExitRegistryError("EXIT tests must be an object keyed only by registered IDs")
    for exit_id, node_ids in tests.items():
        if (
            not isinstance(node_ids, list)
            or not node_ids
            or not all(isinstance(node_id, str) and "::" in node_id for node_id in node_ids)
        ):
            raise ExitRegistryError(f"Test mapping for {exit_id} must contain pytest node IDs")

    implemented_ids = {exit_id for exit_id, status in statuses.items() if status == "implemented"}
    missing_tests = sorted(implemented_ids - set(tests))
    if missing_tests:
        raise ExitRegistryError(f"Implemented EXIT IDs lack tests: {', '.join(missing_tests)}")
    return len(actual)
