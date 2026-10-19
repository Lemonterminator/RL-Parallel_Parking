# EXIT-0.11 evidence: actuator-clamp stress run

Recorded 2026-10-19. These files back the `implemented` status of EXIT-0.11 in
`contracts/exit_registry.json`.

| File | Run |
|---|---|
| `exit_0_11_stress.json` | Full run: 10^6 sequences × 400 policy steps × 5 substeps = 2×10^9 substeps |
| `exit_0_11_positive_control.json` | Positive control: 10^4 sequences with the dynamics clamps replaced by the identity |

## Environment

- Commit: `88838b3b0004e0c584657d652a0bc637a39103c1` (`src/` and `configs/` are unchanged from
  that commit through the commit that adds this directory).
- Config: `configs/reference.json`, `config_sha256`
  `45fcb2ca5c3e8a0bb15360ec5fa3530c51af5dea5e9a1d5026c7c067cc36968d`.
- OS: Microsoft Windows 11 Pro 10.0.26300; Python 3.14.4 (native Windows venv).
- CPU: AMD Ryzen 9 9950X3D, 32 logical processors, 32 worker processes. No GPU is used.

## Commands and results

```powershell
# sanity: exit code 0, 0 violations
parking-governance exit-0-11-stress configs/reference.json --sequences 400 --chunk-size 100 --workers 4
# positive control: exit code 0 (the command fails if a positive control finds nothing)
parking-governance exit-0-11-stress configs/reference.json --sequences 10000 --workers 32 --disable-clamps --out exit_0_11_positive_control.json
# full run: exit code 0
parking-governance exit-0-11-stress configs/reference.json --workers 32 --out exit_0_11_stress.json
```

| | Full run | Positive control |
|---|---|---|
| Sequences | 1,000,000 | 10,000 |
| Substeps checked | 2,000,000,000 | 3,883,057 |
| Latency 0 / 1 / 2 sequences | 333,040 / 334,010 / 332,950 | 3,303 / 3,310 / 3,387 |
| Raw out-of-range control sequences | 99,953 | 1,038 |
| Saturated-corner sequences | 40,473 | 438 |
| Violations | **0** | **92,150** |
| Integrator guard trips | 0 | 9,740 |
| Wall time | 831.6 s | 3.0 s |

The positive control stops counting a sequence when the integrator's entry guard rejects an
out-of-range state, which is why it checks fewer substeps than it schedules.

## Notes for readers

- **`max_value_over_limit` of 1.0000000000000009** for `speed_step` and `steering_step` is
  floating-point rounding of `x + rate·dt_sub` at a saturated rate (a few ULP of the ratio). The
  checker uses an absolute tolerance of `1e-12` (`TOLERANCE` in
  `src/parking_rl/governance/clamp_stress.py`), so these are not violations.
- **The final-state digest is platform-specific.** Counts are identical for any worker count, but
  libm differs in the last ULP across platforms, so `final_state_sha256` differs between Windows
  and Linux. The Windows reference for the 400-sequence sanity run is
  `abfcce9057e6018af07701ee79d465229984c8b6a260599b4e4077fb512923ea`. Compare digests only
  within one platform.
- **CCD cost of the conservative motion bound** (sampled every 100th substep, 2×10^7 substeps):
  the bound `translation + d_max·|Δθ|` reaches at most 0.058254 m per substep, against 0.046113 m
  of true corner motion. With `max_point_motion_m = 0.025` this means 1.5138 CCD samples per
  substep on average instead of 1.3508 with the exact corner motion (12% more geometry work,
  at most 3 samples instead of 2). The bound never changes which collisions are found.
