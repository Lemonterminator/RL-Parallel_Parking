import json

import pytest

from parking_rl.governance.config_hash import (
    ConfigHashError,
    config_sha256,
    verify_hash_manifest,
    write_hash_manifest,
)


def test_hash_is_independent_of_object_key_order_and_whitespace(tmp_path):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text('{"b": [2, 1], "a": 3}\n', encoding="utf-8")
    second.write_text('{\n  "a": 3,\n  "b": [2, 1]\n}', encoding="utf-8")

    assert config_sha256(first) == config_sha256(second)


def test_hash_changes_when_config_value_changes(tmp_path):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text('{"discount": 0.995}', encoding="utf-8")
    second.write_text('{"discount": 0.99}', encoding="utf-8")

    assert config_sha256(first) != config_sha256(second)


def test_manifest_round_trip_and_tamper_detection(tmp_path):
    config = tmp_path / "config.json"
    manifest = tmp_path / "config.hash.json"
    config.write_text('{"seed": 7}', encoding="utf-8")
    written = write_hash_manifest(config, manifest)

    assert verify_hash_manifest(manifest) == written["digest"]

    config.write_text('{"seed": 8}', encoding="utf-8")
    with pytest.raises(ConfigHashError, match="mismatch"):
        verify_hash_manifest(manifest)


def test_non_object_config_is_rejected(tmp_path):
    config = tmp_path / "config.json"
    config.write_text(json.dumps([1, 2, 3]), encoding="utf-8")

    with pytest.raises(ConfigHashError, match="root"):
        config_sha256(config)
