"""Stable canonical serialization for immutable research contracts."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import fields, is_dataclass
from enum import Enum
from typing import Any


class FingerprintError(ValueError):
    """Raised when a value cannot be represented by the canonical contract format."""


def canonical_data(value: object) -> Any:
    """Convert a contract value to JSON data without losing its declared structure."""

    if value is None or type(value) in {bool, int, str}:
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise FingerprintError("canonical floating-point values must be finite")
        return value
    if isinstance(value, Enum):
        return canonical_data(value.value)
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: canonical_data(getattr(value, field.name)) for field in fields(value)}
    if type(value) in {tuple, list}:
        return [canonical_data(item) for item in value]
    if type(value) is dict:
        if any(type(key) is not str for key in value):
            raise FingerprintError("canonical object keys must be strings")
        return {key: canonical_data(item) for key, item in value.items()}
    raise FingerprintError(f"unsupported canonical value: {type(value).__name__}")


def canonical_json_bytes(value: object) -> bytes:
    """Serialize a contract value as sorted, whitespace-free UTF-8 JSON."""

    data = canonical_data(value)
    return json.dumps(
        data,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def sha256_fingerprint(value: object) -> str:
    """Return the SHA-256 digest of a canonical contract value."""

    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()
