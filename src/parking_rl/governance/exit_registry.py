"""Validation for the machine-readable ROADMAP EXIT registry."""

from __future__ import annotations

import ast
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
_STATUSES = frozenset({"planned", "implemented", "retired"})


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ExitRegistryError(f"Cannot read EXIT registry {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ExitRegistryError("EXIT registry root must be a JSON object")
    return value


def _repository_root(registry_path: Path) -> Path:
    """Locate the checkout for checked-in and temporary registry copies."""

    if registry_path.parent.name == "contracts":
        return registry_path.parent.parent.resolve()
    return Path.cwd().resolve()


def _validate_node_ids(
    mapping_name: str,
    mappings: dict[str, Any],
    repository_root: Path,
) -> None:
    """Require every registry node ID to name an existing top-level pytest function."""

    for exit_id, node_ids in mappings.items():
        if (
            not isinstance(node_ids, list)
            or not node_ids
            or not all(isinstance(node_id, str) and "::" in node_id for node_id in node_ids)
        ):
            raise ExitRegistryError(
                f"{mapping_name} mapping for {exit_id} must contain pytest node IDs"
            )
        for node_id in node_ids:
            relative_file, _, selector = node_id.partition("::")
            candidate = Path(relative_file)
            if candidate.is_absolute() or candidate.suffix != ".py":
                raise ExitRegistryError(f"Invalid pytest node ID for {exit_id}: {node_id}")
            test_file = (repository_root / candidate).resolve()
            try:
                test_file.relative_to(repository_root)
            except ValueError as exc:
                raise ExitRegistryError(
                    f"Pytest node ID escapes the repository for {exit_id}: {node_id}"
                ) from exc
            if not test_file.is_file():
                raise ExitRegistryError(f"Pytest file does not exist for {exit_id}: {node_id}")
            function_name = selector.partition("[")[0]
            try:
                tree = ast.parse(test_file.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, SyntaxError) as exc:
                raise ExitRegistryError(f"Cannot inspect pytest node ID {node_id}: {exc}") from exc
            functions = {
                node.name
                for node in tree.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
            if function_name not in functions:
                raise ExitRegistryError(
                    f"Pytest function does not exist for {exit_id}: {node_id}"
                )


def validate_exit_registry(registry_path: str | Path) -> int:
    """Validate complete coverage, ownership, overrides, and implemented test mappings."""
    registry_path = Path(registry_path)
    data = _load(registry_path)
    if data.get("schema_version") != 2:
        raise ExitRegistryError("Unsupported EXIT registry schema")

    default_status = data.get("default_status")
    if default_status not in _STATUSES:
        raise ExitRegistryError("EXIT registry default_status is invalid")

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
    if any(status not in _STATUSES for status in statuses.values()):
        raise ExitRegistryError("EXIT statuses may only be planned, implemented, or retired")
    if not isinstance(tests, dict) or not set(tests).issubset(actual):
        raise ExitRegistryError("EXIT tests must be an object keyed only by registered IDs")
    _validate_node_ids("Test", tests, _repository_root(registry_path))

    implemented_ids = {exit_id for exit_id, status in statuses.items() if status == "implemented"}
    missing_tests = sorted(implemented_ids - set(tests))
    if missing_tests:
        raise ExitRegistryError(f"Implemented EXIT IDs lack tests: {', '.join(missing_tests)}")

    clause_statuses = data.get("clause_statuses", {})
    clause_tests = data.get("clause_tests", {})
    if not isinstance(clause_statuses, dict) or not set(clause_statuses).issubset(actual):
        raise ExitRegistryError("clause_statuses must be keyed only by registered IDs")
    if not isinstance(clause_tests, dict) or not set(clause_tests).issubset(actual):
        raise ExitRegistryError("clause_tests must be keyed only by registered IDs")
    flattened_clause_tests: dict[str, Any] = {}
    for exit_id, per_clause_status in clause_statuses.items():
        expected_clauses = overrides.get(exit_id, {}).get("clauses")
        if not isinstance(expected_clauses, dict):
            raise ExitRegistryError(f"{exit_id} has clause statuses but no declared clauses")
        if not isinstance(per_clause_status, dict) or set(per_clause_status) != set(
            expected_clauses
        ):
            raise ExitRegistryError(
                f"{exit_id} clause statuses must cover declared clauses exactly"
            )
        if any(status not in _STATUSES for status in per_clause_status.values()):
            raise ExitRegistryError(f"{exit_id} has an invalid clause status")
        per_clause_tests = clause_tests.get(exit_id, {})
        if not isinstance(per_clause_tests, dict) or not set(per_clause_tests).issubset(
            expected_clauses
        ):
            raise ExitRegistryError(f"{exit_id} clause tests must target declared clauses")
        implemented_clauses = {
            clause for clause, status in per_clause_status.items() if status == "implemented"
        }
        missing_clause_tests = sorted(implemented_clauses - set(per_clause_tests))
        if missing_clause_tests:
            raise ExitRegistryError(
                f"Implemented clauses for {exit_id} lack tests: {', '.join(missing_clause_tests)}"
            )
        for clause, node_ids in per_clause_tests.items():
            flattened_clause_tests[f"{exit_id}({clause})"] = node_ids
        effective_status = statuses.get(exit_id, default_status)
        if effective_status == "implemented" and any(
            status != "implemented" for status in per_clause_status.values()
        ):
            raise ExitRegistryError(
                f"{exit_id} cannot be implemented while one of its clauses is not implemented"
            )
    unknown_clause_test_ids = set(clause_tests) - set(clause_statuses)
    if unknown_clause_test_ids:
        raise ExitRegistryError("clause_tests require matching clause_statuses")
    _validate_node_ids("Clause test", flattened_clause_tests, _repository_root(registry_path))

    blocked_evidence = data.get("blocked_evidence", {})
    if not isinstance(blocked_evidence, dict) or not set(blocked_evidence).issubset(actual):
        raise ExitRegistryError("blocked_evidence must be keyed only by registered IDs")
    evidence_tests: dict[str, Any] = {}
    for exit_id, evidence in blocked_evidence.items():
        if statuses.get(exit_id, default_status) != "planned":
            raise ExitRegistryError(f"Blocked evidence for {exit_id} requires planned status")
        if (
            not isinstance(evidence, dict)
            or not isinstance(evidence.get("reason"), str)
            or not evidence["reason"].strip()
        ):
            raise ExitRegistryError(f"Blocked evidence for {exit_id} requires a reason")
        if "tests" in evidence:
            evidence_tests[exit_id] = evidence["tests"]
    _validate_node_ids("Evidence test", evidence_tests, _repository_root(registry_path))
    return len(actual)
