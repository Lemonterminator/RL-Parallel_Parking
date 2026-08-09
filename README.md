# RL-Parallel_Parking

Reproducible reinforcement-learning research for parallel parking and reverse-bay parking. The
research plan lives in [`PLAN_MACRO.md`](PLAN_MACRO.md), with stage-specific contracts under
[`stages/`](stages/).

## Governance bootstrap

The initial package provides three executable safeguards required by the roadmap:

- deterministic SHA-256 fingerprints for resolved JSON configuration;
- a complete registry for every `EXIT-*` contract, including cross-stage prerequisites;
- an append-only ledger that limits headline TEST evaluations to three.

```powershell
python -m pip install -e ".[dev]"
parking-governance config-verify configs/reference.hash.json
parking-governance config-validate configs/reference.json
parking-governance exit-validate contracts/exit_registry.json
parking-governance ledger-validate governance/test_usage.jsonl
pytest
```

See [`docs/governance.md`](docs/governance.md) for the operating rules.
The immutable state, scenario, observation, and episode-boundary interfaces are documented in
[`docs/core-contracts.md`](docs/core-contracts.md).

## Stage 0 physics kernel

Stage 0 provides a deterministic rear-axle kinematic bicycle, explicit Euler integration with five
substeps per policy action, actuator/state clamps, exact OBB SAT and signed distance, bounded swept
collision checks, analytic parking-geometry checks, directed success semantics, and bitwise episode
replay. See [`docs/stage0-physics.md`](docs/stage0-physics.md) for contracts and EXIT status.

Trajectory rendering is an optional dependency:

```powershell
python -m pip install -e ".[replay]"
```

The reading, hand derivations, research decisions, and visual checks that still require a human are
tracked in [`docs/stage0-human-work.md`](docs/stage0-human-work.md).
