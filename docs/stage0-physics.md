# Stage 0 physics kernel

Stage 0 is a deterministic geometry and kinematics layer. It deliberately contains no RL algorithm,
policy, reward aggregation, or planner. Downstream stages consume immutable core state and the
interfaces exported by `parking_rl.physics`.

## Architecture

| Area | Modules | Contract |
|---|---|---|
| Dynamics | `physics/action_scaling.py`, `physics/dynamics.py` | Rear-axle bicycle; old-state simultaneous explicit Euler; `dt_policy=0.1 s`; exactly five `0.02 s` substeps; zero-order-held control; control and state clamps |
| Exact geometry | `physics/geometry.py`, `physics/collision.py` | Rear-axle-relative vehicle OBB; exact four-axis SAT; containment-aware penetration depth; exact vertex-edge Euclidean separation; closed world bounds |
| Continuous sweep | `physics/ccd.py` | Linear/shortest-heading interpolation of each explicit-Euler segment, densified until every footprint point has a motion bound of at most `0.025 m`; exact OBB overlap at each sample |
| Parking geometry | `physics/parking_geometry.py`, `physics/bay_geometry.py` | Ideal two-arc lower bound; reverse-bay single-cut boundary; explicit OBB sweep; static multi-cut containment lower bound |
| Terminal semantics | `physics/success.py`, `reward/heading.py` | Goal-frame directed heading, so reverse-bay nose-in is rejected; half-angle heading cost avoids the error-π plateau |
| Replay | `physics/replay.py`, `physics/render.py` | Complete policy/substep trace; seed/config/scenario/commit provenance; canonical IEEE-float digest; bitwise cross-process replay; optional lazy Matplotlib animation |
| Reward-only approximation | `reward_geometry/circles.py` | Three-circle conservative cover is physically separated from collision and termination imports |

“CCD” here means a bounded sampled sweep, not analytic time of impact. The bound is

`translation + d_max * abs(delta_heading)`,

where `d_max` is the farthest vehicle corner from the rear axle. Exact OBB/SAT is used at every
generated sample. This makes the approximation and its resolution auditable without claiming an
analytic bicycle-arc collision time.

## Ordering and state semantics

At a policy boundary, the latency FIFO selects the applied normalized action. Scaling to physical
acceleration and steering rate occurs once, then clamps are applied. The applied control is held for
five substeps. Each substep computes pose, speed, and steering from the same old state, then clamps
the new speed and steering. A `PolicyStepTrace` stores the requested action, applied action, applied
control, and all five substep states.

Stage 0 currently rejects non-default `steering_gain` or `steering_offset_rad` rather than silently
choosing ambiguous calibration semantics. A human decision for later domain randomisation is listed
in `stage0-human-work.md`.

## EXIT status

The source of record is `contracts/exit_registry.json`; validation also confirms that every mapped
pytest node ID exists.

| Status | EXIT contracts |
|---|---|
| Implemented | 0.1–0.7, 0.9, 0.10, 0.15 |
| Planned: Stage 1 dependency | 0.8; 0.14(c) |
| Implemented clauses | 0.14(a), 0.14(b) |
| Planned: full stress ledger required | 0.11 |
| Planned: protocol text requires revision | 0.12, 0.13 |

EXIT-0.11 has CI-scale random and saturation-corner evidence, but not the literal
`10^6 × 400 × 5` run and its evidence ledger. EXIT-0.12 cannot be closed literally because a smooth
potential with a minimum at zero necessarily has gradient tending to zero near zero; the implemented
potential does remove the plateau at π. EXIT-0.13 has corrected whole-sweep/row-clipped evidence,
but its literal text first clips to `y <= 0` and then requires a positive whole-manoeuvre `max_y`; its
Cartesian grid also contains physically infeasible width/clearance pairs.

Run all Stage 0 evidence with:

```powershell
python -m pytest tests/exit_criteria tests/physics tests/reward
parking-governance exit-validate contracts/exit_registry.json
```
