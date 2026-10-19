"""Command-line entry point for governance checks."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Sequence
from pathlib import Path

from parking_rl.core.config import load_reference_config
from parking_rl.governance.clamp_stress import StressSpec, run_stress, summary
from parking_rl.governance.config_hash import (
    config_sha256,
    verify_hash_manifest,
    write_hash_manifest,
)
from parking_rl.governance.exit_registry import validate_exit_registry
from parking_rl.governance.test_ledger import (
    append_test_evaluation,
    validate_test_ledger,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="parking-governance")
    commands = parser.add_subparsers(dest="command", required=True)

    hash_command = commands.add_parser("config-hash", help="print or write a config hash")
    hash_command.add_argument("config")
    hash_command.add_argument("--write", metavar="MANIFEST")

    verify_command = commands.add_parser("config-verify", help="verify a config hash manifest")
    verify_command.add_argument("manifest")

    validate_command = commands.add_parser(
        "config-validate", help="validate resolved config schema"
    )
    validate_command.add_argument("config")

    exits_command = commands.add_parser("exit-validate", help="validate the EXIT registry")
    exits_command.add_argument("registry")

    ledger_command = commands.add_parser("ledger-validate", help="validate TEST usage")
    ledger_command.add_argument("ledger")

    stress_command = commands.add_parser(
        "exit-0-11-stress", help="run the EXIT-0.11 actuator-clamp stress audit"
    )
    stress_command.add_argument("config")
    stress_command.add_argument("--sequences", type=int, default=StressSpec().sequences)
    stress_command.add_argument("--chunk-size", type=int, default=StressSpec().chunk_size)
    stress_command.add_argument("--seed", type=int, default=StressSpec().base_seed)
    stress_command.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    stress_command.add_argument(
        "--disable-clamps", action="store_true", help="positive control: clamps become identity"
    )
    stress_command.add_argument("--out", metavar="JSON")

    record_command = commands.add_parser("test-record", help="append one TEST evaluation")
    record_command.add_argument("ledger")
    record_command.add_argument("--config-sha256", required=True)
    record_command.add_argument("--eval-set-sha256", required=True)
    record_command.add_argument("--checkpoint-sha256", required=True)
    record_command.add_argument("--workdir", default=".")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "config-hash":
        if args.write:
            result = write_hash_manifest(args.config, args.write)["digest"]
        else:
            result = config_sha256(args.config)
        print(result)
    elif args.command == "config-verify":
        print(verify_hash_manifest(args.manifest))
    elif args.command == "config-validate":
        config = load_reference_config(args.config)
        print(f"validated resolved config schema v{config.schema_version}")
    elif args.command == "exit-validate":
        print(f"validated {validate_exit_registry(args.registry)} EXIT contracts")
    elif args.command == "ledger-validate":
        print(f"validated {validate_test_ledger(args.ledger)} TEST evaluations")
    elif args.command == "exit-0-11-stress":
        config = load_reference_config(args.config)
        spec = StressSpec(
            sequences=args.sequences, chunk_size=args.chunk_size, base_seed=args.seed
        )
        result, seconds = run_stress(
            spec,
            config.vehicle,
            workers=args.workers,
            disable_clamps=args.disable_clamps,
            progress=True,
        )
        record = summary(result, spec, seconds)
        record["config_sha256"] = config_sha256(args.config)
        record["clamps_disabled"] = args.disable_clamps
        record["workers"] = args.workers
        text = json.dumps(record, indent=2, sort_keys=True)
        if args.out:
            Path(args.out).write_text(text + "\n", encoding="utf-8")
        print(text)
        if not args.disable_clamps and record["total_violations"]:
            return 1
        if args.disable_clamps and not record["total_violations"]:
            return 1
    elif args.command == "test-record":
        event = append_test_evaluation(
            args.ledger,
            config_sha256=args.config_sha256,
            eval_set_sha256=args.eval_set_sha256,
            checkpoint_sha256=args.checkpoint_sha256,
            workdir=args.workdir,
        )
        print(event["evaluation_id"])
    return 0
