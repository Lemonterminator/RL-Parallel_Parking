import json
from pathlib import Path

import pytest

from parking_rl.governance.test_ledger import (
    TestLedgerError as LedgerValidationError,
)
from parking_rl.governance.test_ledger import (
    append_test_evaluation,
    validate_test_ledger,
)

ROOT = Path(__file__).resolve().parents[1]
HEX_40 = "a" * 40
HEX_64 = "b" * 64


def _init_record():
    return {
        "record_type": "ledger_init",
        "schema_version": 1,
        "max_evaluations": 3,
    }


def _event(index, *, policy_mode="deterministic"):
    return {
        "record_type": "test_evaluation",
        "evaluation_id": f"evaluation-{index}",
        "timestamp_utc": f"2026-08-0{index}T00:00:00Z",
        "commit": HEX_40,
        "config_sha256": HEX_64,
        "eval_set_sha256": HEX_64,
        "checkpoint_sha256": HEX_64,
        "policy_mode": policy_mode,
    }


def _write_ledger(path, records):
    path.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")


def test_checked_in_ledger_has_not_consumed_test_budget():
    assert validate_test_ledger(ROOT / "governance" / "test_usage.jsonl") == 0


def test_fourth_test_evaluation_is_rejected(tmp_path):
    ledger = tmp_path / "ledger.jsonl"
    _write_ledger(ledger, [_init_record(), *(_event(index) for index in range(1, 5))])

    with pytest.raises(LedgerValidationError, match="budget exceeded"):
        validate_test_ledger(ledger)


def test_stochastic_headline_evaluation_is_rejected(tmp_path):
    ledger = tmp_path / "ledger.jsonl"
    _write_ledger(ledger, [_init_record(), _event(1, policy_mode="stochastic")])

    with pytest.raises(LedgerValidationError, match="deterministic"):
        validate_test_ledger(ledger)


def test_record_rejects_malformed_hash_before_touching_git(tmp_path):
    ledger = tmp_path / "ledger.jsonl"
    _write_ledger(ledger, [_init_record()])

    with pytest.raises(LedgerValidationError, match="config_sha256"):
        append_test_evaluation(
            ledger,
            config_sha256="not-a-digest",
            eval_set_sha256=HEX_64,
            checkpoint_sha256=HEX_64,
            workdir=tmp_path,
        )
