# Core contracts

PR #2 freezes the dependency-free data boundary that later physics, sensing, planning, learning,
and evaluation packages must share. These contracts are intentionally implementations of data
shape and invariants only; they do not claim that the corresponding EXIT criteria are complete.

## Dependency boundary

`parking_rl.core` may use only the Python standard library. Higher layers may import it, while core
must never import simulation, sensing, planning, reward, learning, or workflow code.

The public contract separates:

- `NormalizedAction` from simulator-unit `PhysicalControl`;
- rear-axle world poses, object-centroid world poses, ego-frame object poses, and goal-frame errors;
- physical `WorldState` from `EpisodeRuntime` clock/RNG metadata;
- generated `Scenario` truth from later `OracleAnnotation` planner output;
- policy `Observation.values` from layout and observer configuration provenance.

## State and episode endings

`WorldState` contains the realized vehicle parameters, immutable static world, current ego/object
truth, settle progress, and a fixed-capacity actuator queue. The queue is padded with zero actions,
so its shape cannot change when latency changes. Episode time, maximum steps, and RNG seed live in
`EpisodeRuntime`, not the physical state.

`EpisodeEndReason` has one legal `(terminated, truncated)` pair per value. Safety-first resolution is
`collision > out_of_bounds > success > time_limit`; a collision on the final step is therefore a
termination, never a timeout truncation.

## Scenario and frozen oracle

Reverse-bay `BayDifficulty` requires `free_mouth_width_m` (`W_gap`) as an explicit input. It is not
derived from bay width, and `eta_bay` is deliberately absent until one authoritative geometry
function is implemented. `OracleAnnotation` accepts only post-smoothed Hybrid A* provenance and
records its config hash, implementation commit/version, resolution, path-artifact hash, path length,
and gear changes. A `FrozenScenarioRecord` combines the two without contaminating generator output.

All frozen contracts use canonical sorted-key JSON and SHA-256 fingerprints. Floating-point NaN and
infinity are rejected.

## Observation schema

O0 through O4 share one `float32` field order and `layout_hash`. Observer rung, field of view, range,
noise, dropout, and tau behavior instead contribute to `observer_config_hash`. Each semantic object
slot contains relative position, heading sine/cosine, dimensions, type one-hot values, validity,
current visibility, and a reserved tau slot. The vector also includes task-family conditioning,
settle progress, and fixed-capacity actuator queue slots.

O0--O2 require every tau value to be exactly zero; O3--O4 enable tau without changing vector shape.

## Resolved configuration

The checked-in reference JSON has an exact version-1 schema. The parser rejects missing and unknown
keys at every level, booleans used as numbers, non-finite JSON numbers, invalid enums, nonpositive
counts, vehicle geometry inconsistency, integrator drift, terminal-priority drift, an invalid TEST
budget, and disagreement between state and observation latency capacity.

Run all contract checks with:

```powershell
parking-governance config-validate configs/reference.json
parking-governance config-verify configs/reference.hash.json
pytest tests/core
```
