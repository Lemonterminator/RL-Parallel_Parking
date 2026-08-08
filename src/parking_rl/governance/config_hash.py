"""Deterministic fingerprints for resolved JSON configuration."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

ALGORITHM = "sha256"
CANONICALIZATION = "json-sort-keys-utf8-v1"


class ConfigHashError(ValueError):
    """Raised when a configuration or hash manifest is invalid."""


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ConfigHashError(f"Cannot read JSON from {path}: {exc}") from exc


def canonical_json_bytes(value: Any) -> bytes:
    """Return the canonical UTF-8 representation used by every config fingerprint."""
    try:
        text = json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    except (TypeError, ValueError) as exc:
        raise ConfigHashError(f"Configuration is not canonical JSON: {exc}") from exc
    return text.encode("utf-8")


def config_sha256(config_path: str | Path) -> str:
    """Hash parsed JSON so whitespace and object-key order cannot change the digest."""
    path = Path(config_path)
    value = _load_json(path)
    if not isinstance(value, dict):
        raise ConfigHashError("The resolved configuration root must be a JSON object")
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def build_hash_manifest(config_path: str | Path, manifest_path: str | Path) -> dict[str, Any]:
    """Build a portable manifest whose source path is relative to the manifest file."""
    config = Path(config_path).resolve()
    manifest = Path(manifest_path).resolve()
    source = Path(os.path.relpath(config, start=manifest.parent)).as_posix()
    return {
        "schema_version": 1,
        "algorithm": ALGORITHM,
        "canonicalization": CANONICALIZATION,
        "source": source,
        "digest": config_sha256(config),
    }


def write_hash_manifest(config_path: str | Path, manifest_path: str | Path) -> dict[str, Any]:
    """Write a canonical hash manifest and return its data."""
    path = Path(manifest_path)
    data = build_hash_manifest(config_path, path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return data


def verify_hash_manifest(manifest_path: str | Path) -> str:
    """Verify a config against its checked-in manifest and return the digest."""
    path = Path(manifest_path)
    data = _load_json(path)
    if not isinstance(data, dict):
        raise ConfigHashError("Hash manifest root must be a JSON object")
    if data.get("schema_version") != 1:
        raise ConfigHashError("Unsupported config hash manifest schema")
    if data.get("algorithm") != ALGORITHM:
        raise ConfigHashError(f"Hash algorithm must be {ALGORITHM}")
    if data.get("canonicalization") != CANONICALIZATION:
        raise ConfigHashError(f"Canonicalization must be {CANONICALIZATION}")
    source = data.get("source")
    expected = data.get("digest")
    if not isinstance(source, str) or not source:
        raise ConfigHashError("Hash manifest source must be a non-empty string")
    if not isinstance(expected, str) or len(expected) != 64:
        raise ConfigHashError("Hash manifest digest must be a SHA-256 hexadecimal string")
    config_path = (path.parent / source).resolve()
    actual = config_sha256(config_path)
    if actual != expected.lower():
        raise ConfigHashError(
            f"Configuration hash mismatch for {config_path}: expected {expected}, got {actual}"
        )
    return actual
