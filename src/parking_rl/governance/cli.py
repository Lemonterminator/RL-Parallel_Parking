"""Command-line entry point for governance checks."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from parking_rl.core.config import load_reference_config
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
