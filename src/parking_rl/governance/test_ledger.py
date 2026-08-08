"""Append-only accounting for the roadmap's at-most-three TEST evaluations."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


class TestLedgerError(ValueError):
    """Raised when a TEST usage ledger violates its contract."""


_HEX_40 = re.compile(r"^[0-9a-f]{40}$")
_HEX_64 = re.compile(r"^[0-9a-f]{64}$")


def _records(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise TestLedgerError(f"Cannot read TEST ledger {path}: {exc}") from exc
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise TestLedgerError(f"Invalid JSON on ledger line {line_number}: {exc}") from exc
        if not isinstance(value, dict):
            raise TestLedgerError(f"Ledger line {line_number} must be a JSON object")
        records.append(value)
    return records


def validate_test_ledger(ledger_path: str | Path) -> int:
    """Validate the initialization record and every immutable evaluation record."""
    records = _records(Path(ledger_path))
    if not records or records[0].get("record_type") != "ledger_init":
        raise TestLedgerError("The first ledger record must be ledger_init")
    init = records[0]
    if init.get("schema_version") != 1:
        raise TestLedgerError("Unsupported TEST ledger schema")
    max_evaluations = init.get("max_evaluations")
    if not isinstance(max_evaluations, int) or not 1 <= max_evaluations <= 3:
        raise TestLedgerError("max_evaluations must be an integer between 1 and 3")

    events = records[1:]
    if len(events) > max_evaluations:
        raise TestLedgerError(f"TEST evaluation budget exceeded: {len(events)} > {max_evaluations}")
    event_ids: set[str] = set()
    required = {
        "evaluation_id",
        "timestamp_utc",
        "commit",
        "config_sha256",
        "eval_set_sha256",
        "checkpoint_sha256",
        "policy_mode",
    }
    for index, event in enumerate(events, start=2):
        if event.get("record_type") != "test_evaluation":
            raise TestLedgerError(f"Ledger line {index} has an unknown record_type")
        missing = sorted(required - set(event))
        if missing:
            raise TestLedgerError(f"Ledger line {index} is missing {missing}")
        event_id = event["evaluation_id"]
        if not isinstance(event_id, str) or not event_id or event_id in event_ids:
            raise TestLedgerError(f"Ledger line {index} has an invalid or duplicate evaluation_id")
        event_ids.add(event_id)
        if event["policy_mode"] != "deterministic":
            raise TestLedgerError("Headline TEST evaluation policy_mode must be deterministic")
        if not isinstance(event["commit"], str) or not _HEX_40.fullmatch(event["commit"]):
            raise TestLedgerError(f"Ledger line {index} commit must be a 40-character SHA")
        for field in ("config_sha256", "eval_set_sha256", "checkpoint_sha256"):
            value = event[field]
            if not isinstance(value, str) or not _HEX_64.fullmatch(value):
                raise TestLedgerError(f"Ledger line {index} {field} must be a SHA-256 digest")
        try:
            datetime.fromisoformat(event["timestamp_utc"].replace("Z", "+00:00"))
        except (AttributeError, ValueError) as exc:
            raise TestLedgerError(f"Ledger line {index} timestamp_utc is invalid") from exc
    return len(events)


def _git_output(workdir: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=workdir,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _require_sha256(field: str, value: str) -> str:
    normalized = value.lower()
    if not _HEX_64.fullmatch(normalized):
        raise TestLedgerError(f"{field} must be a 64-character SHA-256 digest")
    return normalized


def append_test_evaluation(
    ledger_path: str | Path,
    *,
    config_sha256: str,
    eval_set_sha256: str,
    checkpoint_sha256: str,
    workdir: str | Path = ".",
) -> dict[str, Any]:
    """Append one deterministic TEST evaluation after checking Git cleanliness and budget."""
    ledger = Path(ledger_path)
    root = Path(workdir)
    config_digest = _require_sha256("config_sha256", config_sha256)
    eval_set_digest = _require_sha256("eval_set_sha256", eval_set_sha256)
    checkpoint_digest = _require_sha256("checkpoint_sha256", checkpoint_sha256)
    if _git_output(root, "status", "--porcelain"):
        raise TestLedgerError("Refusing to record TEST usage from a dirty Git worktree")
    validate_test_ledger(ledger)
    commit = _git_output(root, "rev-parse", "HEAD").lower()
    event = {
        "record_type": "test_evaluation",
        "evaluation_id": str(uuid4()),
        "timestamp_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "commit": commit,
        "config_sha256": config_digest,
        "eval_set_sha256": eval_set_digest,
        "checkpoint_sha256": checkpoint_digest,
        "policy_mode": "deterministic",
    }
    candidate = [*_records(ledger), event]
    max_evaluations = candidate[0]["max_evaluations"]
    if len(candidate) - 1 > max_evaluations:
        raise TestLedgerError("Refusing to exceed the TEST evaluation budget")
    with ledger.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(event, separators=(",", ":"), sort_keys=True) + "\n")
    return event
