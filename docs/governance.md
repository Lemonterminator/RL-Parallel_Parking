# Research governance

This bootstrap turns three roadmap promises into executable repository contracts.

## Resolved configuration fingerprints

Only resolved JSON configuration is hashed. Parsing occurs before hashing, so whitespace and object
key order do not change the result. Arrays remain ordered because their order can be semantically
meaningful. Non-finite floating-point values are rejected.

```powershell
parking-governance config-hash configs/reference.json --write configs/reference.hash.json
parking-governance config-verify configs/reference.hash.json
```

Every run must retain the resolved config and the reported SHA-256 digest.

## EXIT registry

`contracts/exit_registry.json` enumerates every EXIT contract in the roadmap. An individual ID may be
marked `implemented` only after it has pytest node IDs in the `tests` map. Cross-stage gates remain
under their original IDs, but their true execution owner and prerequisites are recorded as overrides.

## TEST evaluation ledger

`governance/test_usage.jsonl` is append-only. Its initialization record fixes the maximum number of
headline TEST evaluations at three. Each subsequent record contains the evaluated commit and the
SHA-256 fingerprints of the resolved config, frozen eval set, and checkpoint.

Record an evaluation only after it has completed, from the same clean commit that was evaluated:

```powershell
parking-governance test-record governance/test_usage.jsonl `
  --config-sha256 <64-hex> `
  --eval-set-sha256 <64-hex> `
  --checkpoint-sha256 <64-hex>
```

The command refuses dirty worktrees, nondeterministic policy modes, malformed hashes, duplicate
records, and a fourth TEST use. Commit the appended ledger record immediately after recording it.
