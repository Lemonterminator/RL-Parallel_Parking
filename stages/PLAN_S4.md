# PLAN_S4 — Stage 4: Evaluation, baselines, and the O3 memory comparison

*Decomposed from `PLAN_MACRO.md` §5.4 in full (theory table, "The statistics you will actually use,"
"The full metric set," "The O3 memory comparison — five arms," §5.4.1 the compute budget and fallback
ladder) plus all EXIT-4.x, and §8 (the evaluation protocol, executed at this stage). Context read in
full: §0.1, §0.3, §0.4, §0.5, §2, §6.4, §6.5, §8. §5.1/§5.2/§5.3/§5.5 and the rest of §6/§9/§10 were
**not** read in full for this file except where a fragment is quoted verbatim because §5.4 or §8
itself names or presupposes it (e.g. A26, the `Observer`/`BeliefObserver` interface, specific §9
rows whose own text ties them to Stage 4). Every substantive line ends with a bracketed source
pointer. Nothing has been verified, corrected, resolved, or fact-checked in producing this file — it
is a reorganisation, not a review.*

**Disambiguation, not a correction:** Stage 4's five O3-comparison arms are named **A1–A5**, which
collide textually with assumption IDs **A1–A5** in §2. This file writes bare **A1, A2, …** only for
assumption-table entries, and **arm A1, arm A2, …** (the source's own usage at least once — "Defines
**arm A5**" [§5.4 theory table, Pinto row]) for the five O3 arms, throughout. [§5.4] [§2]

---

## READ FIRST — verification status this whole file inherits

> **v1.2 — the verification is now complete... The prose did not hold up.** Across v1.0 and v1.1 the
> audits found **9 fatal and 55 serious defects** — and **4 of the 9 fatal ones were introduced by
> v1.1's own corrections**... **This is the load-bearing lesson of the whole exercise: a correction is
> a new claim. Every v1.2 change is marked inline, and every one of them is now itself unreviewed.**
> [header, v1.2]

Stage 4 is disproportionately built from v1.2/v1.3 material: **§5.4.1 (the whole compute-budget
subsection), EXIT-4.10, and EXIT-4.11 are v1.2 additions** [§0.3: "→ **§5.4.1**, with a six-rung
fallback ladder and step budgets"; "EXIT-4.10 ended up with no threshold at all... Numbers now
specified"], and the bay-family clauses inside EXIT-4.7's success surface are v1.3 additions
[§0.4: "§5.4's success surface — all three named a parallel-parking difficulty axis only, so the bay
family had no gate and no defined surface. Each now carries its `η_bay` counterpart"]. Under the rule
quoted above, **all of this is itself unreviewed.** [§0.3] [§0.4]

---

## Goal (verbatim)

> **Goal.** Turn results into evidence. The protocol was frozen at Stage 2; this stage executes it.
> [§5.4]

---

## Entry conditions — what Stages 0–3 must have produced, by artefact

This file did not read §5.0/§5.1/§5.2/§5.3 cover-to-cover; only the fragments below were consulted
because §5.4/§8 cite them directly or because they are the closest available definition of a term
Stage 4 uses without redefining.

- **A trained policy at O0** — "The teacher policy. Success ≥ 0.90," landing in Stage 2. [§6.1, O0 row]
- **The `Observer` interface and a `BeliefObserver` that wraps another `Observer`**, described as "the
  whole trick... ~30 lines," with `FullObserver`/`DropoutObserver`/`FOVObserver`/`OccludedObserver`
  as siblings, "so 'with or without the belief filter' is a pluggable layer, which is exactly the O3
  ablation." [§5.2 Build, quoted in the course of reading §6.4's cross-references] — this is the
  mechanism arm A3 and arm A4 plug into; this file did not read §5.2's Build section beyond this
  fragment.
- **O1, O2, O2a rungs exercised and gated** at Stage 3 / Stage 3 end [§6.1: O1 "Stage 3," O2 "Stage 3
  end," O2a "Stage 3 end"] — Stage 4's O3 arms are defined at observation level **O2** specifically
  (H_A: "At observation level O2... `SR(A3) ≥ SR(A4) − 0.03`") [§5.4], so O2's own bite (EXIT-3.11,
  not read directly) is a precondition for H_A meaning anything.
- **Both task families curriculum-trained to the full-difficulty gate**, per EXIT-3.1 (Stage 3, not
  read in full here): success ≥ 0.80 at slot length 1.2·l (parallel) and at `η_bay = 1.15`
  (`W_aisle = 5.00 m`) (bay), "Report the two families separately — A25 buys one *policy*, not one
  *number*." [EXIT-3.1, quoted because §5.4/EXIT-4.1 inherit its per-family reporting convention] [A25]
- **The frozen VAL/TEST/INFEASIBLE-CONTROL sets**, generated once, hashed, SHA-256 hard-coded, each
  scenario carrying `L_oracle, g_oracle, oracle_min_clearance, planner_resolution` from a Hybrid A*
  run "using the ENVIRONMENT's exact SAT checker and footprint." [§8] This is Stage 4's central input;
  see I9 below and Finding 1 in the accompanying report.
- **`L_oracle` fixed as the post-smoothing Hybrid A\* path length, frozen with the scenario set**
  (A26) — "ρ is not comparable across experiments if this drifts. §5.1 offers three denominators; only
  one can be *the* frozen one." [A26] — this is the denominator EXIT-4.4's optimality-ratio metric
  divides by.
- **A Stage-1 planner and tracking controller**, referenced only as the thing "planner per-scenario"
  and "planner per-replan" timings in the metric table are measured against [§5.4, full metric set,
  "Inference vs planning time" row], and as the source of the "empirical oracle boundary (bisect on
  slot length with Hybrid A*)" overlay curve on the success surface [§5.4]. §5.1 itself was not read
  for this file.
- **The evaluation protocol itself, frozen at Stage 2** — the Goal line states this explicitly: "The
  protocol was frozen at Stage 2; this stage executes it." [§5.4] §8's block ("SETS," "GENERATION,"
  "AT EVAL") is therefore an entry condition as much as a Stage-4 procedure; it is carried in full
  below because the task brief requires it.

---

## Assumptions live here (A20 is the central hypothesis)

Only assumptions §5.4/§5.4.1/§8/§6.4/§6.5's own text names, presupposes, or whose "Revisit at" column
names Stage 4. Full text and "if wrong" columns are in §2; not re-derived here.

- **A20 (the central hypothesis).** "For static, noise-free, known-association obstacles, a
  hand-written filter storing `(last-seen pose, seen flag)` is an **exact** sufficient statistic, so a
  feedforward policy on it can be optimal and a GRU can at best tie it. This is the project's central
  falsifiable hypothesis. It is pre-registered, not assumed true." Revisit at: **Tested at Stage 4.**
  [A20] This is H_A's justification, restated at length in §6.4 with the theorem's full six
  preconditions (§2's three-precondition version is itself incomplete — see §6.4 below). [§6.4]
- **A11.** SAC is the default learner, "off-policy is chosen specifically so demonstrations can seed
  the replay buffer." If wrong: switching to PPO loses demo seeding, gains GAE λ. Revisit at:
  **Stage 2 exit, Stage 4.** [A11] — the only assumption in §2 whose revisit column explicitly names
  Stage 4 alongside Stage 2.
- **A18.** "The simulator is cheap enough to vectorise... so throughput is not the binding constraint
  at Stage 2." If wrong: "that changes the SAC-vs-PPO calculus, not the plan structure." Revisit at:
  **Stage 4.** [A18] — Stage 4 is where the ~860 GPU-hour figure (§5.4.1) either does or does not
  confirm this; the document does not connect the two explicitly.
- **A14.** "The policy is evaluated **deterministically** (`a = a_scale·tanh(μ)`, the mode)... reporting
  the stochastic policy measures the wrong objective and inflates the collision rate." Revisit at:
  Never. [A14] — directly operative in §8's `AT EVAL` block ("deterministic policy `a = a_scale *
  tanh(mu)` -- the MODE, since `E[tanh u] != tanh(E u)`") [§8] and in EXIT-4.5, which is the one
  criterion that formally checks the stochastic policy too.
- **A19.** "On a known static map, classical planning solves this problem, so the O0 RL result is a
  sanity check and not a contribution." Revisit at: Never — state it. [A19] — the reason Stage 4 must
  keep the Hybrid A* comparison (oracle contour, `ρ`, inference-vs-planning-time) rather than reporting
  RL success rate alone.
- **A9.** "The scenario distribution is fixed and defined by a generator with a recorded seed... Every
  historical comparison becomes incomparable [otherwise]. Enforced by hashing (EXIT-2.1)." Revisit at:
  Never. [A9] — backs §8's `GENERATION` block.
- **A10.** "'Feasible' means 'solvable by our Hybrid A* at the declared grid resolution', not
  'geometrically possible'... the RL success rate is measured against a denominator that is itself a
  lower bound on true feasibility. **State this in the thesis rather than hide it.**" Revisit at:
  Never — state it. [A10] — bears directly on how EXIT-4.7's "empirical oracle boundary" and "gap
  between the agent contour and the oracle contour" should be interpreted; the plan's own text ties
  the two ("Hybrid A* is resolution-complete, not complete").
- **A21.** `τ_since_seen` is "redundant" for the static, noise-free state posterior, "It earns its
  place only once objects can move or detections can be false." **v1.2 weakens this** — see §6.4's
  refinement below. Revisit at: O2. [A21]
- **A22.** `settle_counter` is part of the state, observable at every rung; success requires the
  tolerance conditions to hold for `K_settle` consecutive steps. If omitted: "the task is a **POMDP
  even at O0**." Revisit at: Never. [A22] — this is a precondition of what "success" means for every
  success-rate number EXIT-4.1 reports.
- **A25.** "Parallel parking and reverse bay parking are solved by **one policy** conditioned on the
  scenario, not two." If wrong: "every 'success rate' in the document is two numbers, K doubles, and
  the Stage-4 compute estimate doubles with it. **Never stated.**" Revisit at: Stage 2. [A25] — that
  last clause, "never stated," is the assumption's own text, about itself, and is the seed of Finding
  3 in the accompanying report: whether the doubling it warns against was actually costed into §5.4.1.
- **A26.** `L_oracle` is the post-smoothing Hybrid A* path length, frozen with the scenario set.
  Revisit at: Stage 1. [A26] — already listed under Entry conditions; repeated here because it is
  itself an assumption, not a derived fact.
- **A28.** The bay family's difficulty scalar is `η_bay = W_aisle / W_aisle_min(W_gap; R_min, c=0)`,
  and `W_aisle`, not `W_bay`, is the axis varied. Revisit at: Stage 3. [A28] — this is the axis
  EXIT-4.7's bay heatmap uses ("bay: `W_aisle`").

---

## Invariants live here

Only invariants §5.4/§8's own text operationalises.

- **I9.** "The frozen eval set is hashed and never regenerated." Test: EXIT-2.1 (Stage 2, not read in
  full). [I9] — the invariant Finding 1 (accompanying report) argues EXIT-4.7 may not actually satisfy.
- **I4.** "`terminated` ≠ `truncated`... Never construct `done = terminated or truncated`." Test:
  EXIT-2.5 (Stage 2). [I4] — backs §8's terminal-classification block below.
- **I3.** "Observation is **ego-frame**; pose error / reward is **goal(slot)-frame**." Test: §7.1
  (not read in full). [I3] — this is the precondition whose consequence the A3/A4 confound box in
  §5.4 spells out at length (A4 must dead-reckon to render A3's feature in the current ego frame).
- **I2.** "Reward, success test, and collision test read `WorldState`. **Never** `Observation`." Test:
  EXIT-2.12 (Stage 2). [I2] — presupposed by every truth-based metric in the full metric set (success,
  collision, pose error, clearance).
- **I5 / I6.** "Exact SAT decides collision/termination. The 3-circle body model appears **only** in
  the smooth reward term" / "Collision detection runs at every physics substep; reward is evaluated
  once per policy step." Tests: EXIT-2.8, EXIT-2.9/2.13 (Stage 2). [I5] [I6] — backs the "Min
  clearance: exact OBB, at **substep** resolution" and "Collision rate" rows of the full metric set.

---

## Theory to read

*(Reproduced from §5.4's own table; markers unchanged. `[V]`/`[C]`/`[?]` per §0.1, never upgraded or
downgraded here.)*

| Priority | Source | Covers |
|---|---|---|
| must | `[C]` Henderson, Islam, Bachman, Pineau, Precup & Meger (2018). "Deep RL that Matters." AAAI 2018, 3207–3214 | The justification for the 10-seed minimum and the ban on seed pruning |
| must | `[C]` Agarwal, Schwarzer, Castro, Courville & Bellemare (2021). NeurIPS 2021, arXiv:2108.13264 + the **rliable** library | IQM, stratified bootstrap CIs, performance profiles, probability of improvement |
| must | `[?]` Patterson, Neumann, White & White (2024). "Empirical Design in RL." *JMLR* 25(318), 1–63 | The most complete single reference here. Its **hyperparameter-budget accounting** is what lets you claim arms got equal tuning |
| must | `[?]` Colas, Sigaud & Oudeyer (2018). "How Many Random Seeds?" arXiv:1806.08295 | The number behind "n=3 has 80% power only against d ≈ 2.3" |
| must | `[C]` Brown, Cai & DasGupta (2001). *Statistical Science* 16(2), 101–133 | Your citation for "we do not use Wald" |
| must | `[?]` Wilson, E. B. (1927). *JASA* 22(158), 209–212 | The interval you print in every table (issue/page **unverified**) |
| should | `[C]` Clopper & Pearson (1934). *Biometrika* 26(4), 404–413 | For the **collision** rate specifically, and the zero-event case |
| must | `[C]` Newcombe, R. G. (1998). *Statistics in Medicine* 17(22), 2635–2650 | **Every arm-vs-arm comparison here is PAIRED** (same frozen set). Unpaired intervals throw away most of your power |
| must | `[?]` McNemar, Q. (1947). *Psychometrika* 12(2), 153–157 | The exact paired test. Use the **exact binomial** version — b+c is often < 25 |
| must | `[C]` Schuirmann, D. J. (1987). *J. Pharmacokinet. Biopharm.* 15(6), 657–680 | **TOST** — how to report the O3 null as a *claim* rather than an absence of one |
| must | `[?]` Holm, S. (1979). *Scand. J. Statist.* 6(2), 65–70 | 5 arms → 10 pairs → ~40% family-wise false-positive rate at α=0.05 |
| must | `[C]` Kaelbling, Littman & Cassandra (1998). *Artificial Intelligence* 101(1–2), 99–134 (belief sufficiency traces to `[?]` Åström 1965, *JMAA* 10, 174–205) | The theory behind the O3 hypothesis |
| must | `[?]` Ni, Eysenbach & Salakhutdinov (2022). "Recurrent Model-Free RL Can Be a Strong Baseline for Many POMDPs." ICML 2022 | **If your GRU arm loses, the first objection is "your GRU was badly tuned."** This is the reference recipe that lets you rebut it. Match its sequence-replay and burn-in choices and say so |
| should | `[?]` Pinto, Andrychowicz, Welinder, Zaremba & Abbeel (2018). "Asymmetric Actor Critic." RSS 2018 | Defines arm A5 — it changes **only the critic input**, keeping the arm comparable |
| should | `[C]` Efron & Tibshirani (1993). *An Introduction to the Bootstrap*, Ch. 8, 12–14 | Why a bootstrap CI from 3 seeds is meaningless: only C(2n−1,n) = **10** distinct resamples at n=3, versus 92,378 at n=10 |

[§5.4, theory table, whole]

---

## The statistics you will actually use

*(Verbatim, including every stated number. None recomputed.)*

```
WILSON SCORE INTERVAL (the headline interval for every rate):
    denom      = 1 + z^2/n
    center     = ( p_hat + z^2/(2n) ) / denom
    halfwidth  = ( z / denom ) * sqrt( p_hat(1-p_hat)/n + z^2/(4n^2) )        z = 1.959964
  Meaning: the set of pi satisfying the SCORE test, i.e. the standard error uses the NULL
  variance pi(1-pi)/n, not the plug-in p_hat(1-p_hat)/n. That is the whole difference from Wald.

  Half-widths at p_hat = 0.85 (all cross-checked against statsmodels proportion_confint):
    n=50 ->  9.86pp   n=100 -> 6.99pp   n=200 -> 4.95pp   n=400 -> 3.50pp
    n=500 ->  3.13pp   <-- RECOMMENDED    n=1000 -> 2.21pp  n=2000 -> 1.56pp
  NOTE on n=50: p_hat = 0.85 needs k = 42.5, which is not an integer. 9.86pp is the value at
  p_hat = 0.85 exactly; v1.0 printed 10.09pp, which is the value at the nearest ACHIEVABLE
  p_hat = 42/50 = 0.84. Either figure is defensible; the label "at p_hat = 0.85" is not.

ZERO-EVENT (your collision rate). Exact one-sided upper bound at k = 0:
    p_upper = 1 - alpha^(1/n)         ~  3/n   (the "rule of three")
    n=500 -> 0.597%      n=1000 -> 0.299%      n=3000 -> 0.0999%
  READ THIS: with N = 500 you CANNOT claim a collision rate below 0.6%, however clean the runs
  look. If the thesis wants "< 0.1% collisions", N must be >= 3000. Decide in Stage 2, not Stage 4.

WHY NOT WALD: at k=n it gives [1.0, 1.0]; at k=0 it gives [0.0, 0.0]; coverage oscillates and is
  well below nominal near p = 0.95 -- and p ~ 0.95 and p ~ 0.00 are exactly your operating points.

SEED-COUNT POWER:   d_MDE ~= sqrt(15.7 / K)
    K=3 -> 2.29     K=5 -> 1.77     K=10 -> 1.25     K=20 -> 0.89
  DECISION: K = 10 for every headline table. K = 5 only for exploratory sweeps whose numbers never
  appear in a results table. K = 3 is banned.

PAIRED COMPARISON (McNemar), MDE at alpha=0.05, power=0.80, f = discordance fraction n_d/N:
    delta_MDE = 2.8016 * sqrt(f/N)
    N=500, f=0.05 -> 2.80pp    f=0.10 -> 3.96pp    f=0.15 -> 4.85pp
  versus UNPAIRED at N=500: 6.33pp. Pairing roughly halves your minimum detectable effect.

IQM -- THE STEP EVERYONE SKIPS: collapse episodes to a per-run RATE first,
  s[seed, family] = successes/N. NEVER feed raw 0/1 outcomes to IQM: a 25%-trimmed mean of
  Bernoulli values returns 1.000 for any rate above 0.75 and destroys all resolution.
  Then IQM over the K x T matrix, with a stratified bootstrap (B = 50,000) resampling RUNS.

TOST (equivalence): conclude equivalence iff the 100(1-2*alpha)% CI on the difference lies
  entirely inside [-delta, +delta]. For alpha = 0.05 that is the 90% CI, NOT the 95% CI.
  Pre-register delta = 0.03 absolute success rate -- justified because at N=500 the Wilson
  half-width is 3.1pp, so a smaller margin is not measurable.

CHECKPOINT-SELECTION OPTIMISM:  optimism ~= sigma_val * E[max of m iid N(0,1)]
    sigma_val = sqrt(p(1-p)/N_val) = 2.525pp at p = 0.85, N_val = 200
    EXACT E[max] (numerical integration, confirmed by 2e6-draw Monte Carlo):
        m=10 -> 1.5388    m=40 -> 2.1608    m=100 -> 2.5076
    optimism:  m=10 -> +3.89pp   m=40 -> +5.46pp   m=100 -> +6.34pp
  v1.0 printed 3.44 / 5.08 / 5.97pp. Those come from the classical ASYMPTOTIC approximation
  sqrt(2 ln m) - (ln ln m + ln 4pi)/(2 sqrt(2 ln m)), which under-estimates the true E[max]
  by 11-14% at these m. Use the exact figures: the real optimism is WORSE than v1.0 claimed.

  Best-of-40 checkpoint selection on a 200-scenario val set injects ~5.5pp of PURE NOISE --
  larger than most effects the O3 ablation is trying to measure. This is the whole argument
  for select-on-VAL / report-on-TEST.
```

[§5.4, "The statistics you will actually use," whole, all numbers verbatim]

---

## The full metric set

| Metric | How reported |
|---|---|
| Success rate | Wilson 95%, **per seed**; IQM + stratified bootstrap over seeds as the headline. **Two variance components, two intervals, both printed.** |
| Collision rate | Clopper–Pearson 95% **upper** bound; print as `0/500, 95% upper bound 0.60%`, never "0%" |
| Timeout / out-of-bounds | Wilson 95%; Goodman simultaneous intervals if claiming anything about the 4-cell vector at once |
| Final pose error | **p50 and p95**, never the mean (the distribution is truncated at the success tolerance by construction, so the mean says nothing about the marginal cases — which are the ones that matter) |
| Optimality ratio ρ | `∫\|v\|dt` over **substeps** ÷ frozen `L_oracle`; p50, p95, `P(ρ<1)`, and the full **performance profile** `F(τ) = P(success ∧ ρ ≤ τ)`, which is unconditional and therefore free of survivorship bias |
| Gear changes | with 0.05 m/s hysteresis; report `g_agent − g_oracle` |
| Control effort | `J_δ`, `J_δ̇`, **and** the time-averaged `J̄ = J/T` — otherwise a policy that crashes at step 20 has the "smoothest" control in the table |
| Min clearance | exact OBB, at **substep** resolution |
| Inference vs planning time | **same machine, same process**, governor pinned, 100 warm-up calls discarded; four numbers: policy per-step (mean, p99), policy per-episode, planner per-scenario (mean, p95, **max**), planner per-replan |

[§5.4, "The full metric set," whole]

**The success-rate surface is the deliverable that turns this from a demo into a result.** Two
heatmaps per family, with the family's own difficulty axis on x — **parallel: slot length; bay:
`W_aisle`** *(v1.3; v1.0–v1.2 named only the parallel axis, so the bay surface had no definition)* —
against (initial lateral offset) and (initial heading error). 10×10, ≥50 episodes/cell. At 50 episodes/cell the Wilson half-width is 10.1 pp — fine for
**shape**, useless for a per-cell claim, so **never quote a cell in text**. Fit a logistic surface,
extract the agent's **50% contour** with a bootstrap band, and overlay: the empirical oracle boundary
(bisect on slot length with Hybrid A*), the static containment bound, and your hand-derived analytic
single-cusp bound. **Report the gap between the agent contour and the oracle contour**, with a band —
that gap is the result. [§5.4, success-surface paragraph, whole]

---

## The O3 memory comparison — five arms

| Arm | Definition | Role |
|---|---|---|
| **arm A1** | MLP + instantaneous local observation (incl. `valid`, `visible_now`), no history | amnesiac lower bound |
| **arm A2** | MLP + frame stack (k=8) | **NEGATIVE CONTROL — label it as such.** k=8 covers 0.8 s; the required memory horizon is the whole manoeuvre, 100–400 steps. It is off by two orders of magnitude, not merely weaker |
| **arm A3** | MLP + **hand-written static belief filter** | the strong, boring baseline. **Predicted winner** |
| **arm A4** | GRU + instantaneous local observation | learned memory |
| **arm A5** | GRU + **privileged full-state critic** (asymmetric) | changes only the critic input, so it stays comparable |
| *(arm A6)* | distilled student from a full-state teacher | optional; a **different training algorithm** — belongs in a separate row, never conflated with arm A5 |

[§5.4, five-arms table, whole]

> **⚠ arm A3 and arm A4 are not information-symmetric, and no v1.0 criterion covered it.** I3 mandates
> an **ego-frame** observation. To render a stored obstacle pose in the *current* ego frame, the
> `BeliefObserver` needs the ego's motion since that observation — and as a wrapper over `WorldState`
> it simply reads the true ego pose. **arm A4 has no such access:** it sees ego-frame quantities plus
> `(v, δ)`, so to reproduce arm A3's feature it must dead-reckon the bicycle model over 100–400 steps
> and will accumulate drift. arm A4's policy class therefore does not straightforwardly contain arm
> A3's, and a loss by arm A4 is partly attributable to a **dead-reckoning burden rather than to
> memory**.
>
> **Fix:** give arm A4 the same ego-motion information arm A3's filter implicitly uses — a per-step
> delta-pose input — and add it to the EXIT-4.9 key list. (The alternative escape hatch, exempting
> the goal slot from the FOV mask so the ego is permanently localised against a fixed anchor,
> threatens EXIT-3.11: if a goal anchor plus a memorised layout prior suffices, the FOV rung will not
> bite and O3 has no partial observability left to study. §6.1(b) resolves this the other way.) [§5.4]

**Pre-register this before running any arm** (commit it, cite the hash):

> **H_A (primary).** At observation level O2 (static obstacles, limited FOV, known association,
> noise-free), `SR(arm A3) ≥ SR(arm A4) − 0.03`: the hand-written belief filter is equivalent to or
> better than the GRU within a 3 pp margin.
> **Rationale (v1.1 — v1.0 overclaimed here).** For static, noise-free, known-association obstacles
> the belief over each obstacle's pose collapses to a point mass at the last observed pose, so
> `(last-seen pose, seen flag)` **is** the belief and hence a sufficient statistic (Åström 1965;
> Kaelbling, Littman & Cassandra 1998). What follows is that **the arm A3 policy class contains an
> optimal policy**, so any arm A4 advantage must come from optimisation, exploration or approximation
> effects rather than from *information* — which is exactly what the linear probe (EXIT-4.10) and the
> τ ablation (H_B) are for.
>
> v1.0 said "a GRU can at best tie it", stated as a prediction about measured success rate. That does
> not follow: the theorem bounds *optima*, the hypothesis is about *estimates*. At least four routes
> let arm A4 beat arm A3 with every word of the theory intact — (1) the internal clock, on a
> finite-horizon success metric; (2) recurrent state gives temporally correlated exploration, which
> §5.3 notes this task benefits from; (3) the hidden state is a *learned* basis and may approximate Q
> better than a hand-chosen 12-dim-per-object encoding, independently of sufficiency; (4) arm A3's
> advantage is contingent on its encoding faithfully rendering `b`, which precondition (vii) puts in
> doubt. The one-sided 3 pp margin remains a reasonable pre-registration; the rationale does not.
> **H_B (secondary, A21).** At O2, adding `τ_since_seen` to arm A3's features does **not** improve
> success rate. If it does, assumption A4 (static world) is being violated somewhere.
> **H_C.** At O4 (occlusion + missed detections + association ambiguity), the ordering **reverses**.

[§5.4, pre-registration box, whole]

---

## Compute budget and the fallback ladder (§5.4.1)

**Stage 4 as specified in v1.1 costs roughly 860 GPU-hours of training**, and that is before
evaluation. The audit costed it: 5 headline arms x 10 seeds, **plus** the mandatory DR-on
replication of all five arms that EXIT-4.11 requires, **plus** the O2a sweep, H_B, a TD3 baseline
and the gamma sweep, at an assumed 3M environment steps per run. The EXIT-4.7 success surface alone
needs a further **40-200M environment steps** of pure evaluation, which v1.1 never costed at all. [§5.4.1]

**Worse, v1.0/v1.1 stated no training-step budget for any stage — which makes every performance
gate unfalsifiable.** "Success >= 0.90" with no step budget is not a criterion; it is a wish that
can always be deferred by training longer. [§5.4.1]

**Fix, in two parts.**

**(1) Every performance gate gets a step budget.** State it as `success >= X within N environment
steps`. Starting values: Stage 2 gates at **3M** steps, Stage 3 at **10M**, Stage 4 arms at **3M**
each. A gate not met within budget is a **failure**, not an invitation to train longer. [§5.4.1]

**(2) A pre-declared fallback ladder, descended in this order when the budget binds.** v1.1 forbade
its own cheapest fallback — it banned K=3 and asserted K==10 — leaving no legal way to reduce cost:

| Rung | Action | Cost saved | What it costs you |
|---|---|---|---|
| 0 | Full spec as written | — | ~860 GPU-h |
| 1 | Drop the DR-on replication of all five arms (EXIT-4.11) to **two** arms (arm A3, arm A4) | ~35% | the DR-on comparison covers only the two arms H_A is about |
| 2 | Cut the O2a sweep from 5 radii to **2** (6 m, 12 m) | ~10% | coarser radius resolution; EXIT-6.4 reports the two-point sweep |
| 3 | Reduce the success surface to a **6x6** grid at 30 episodes/cell | ~60% of eval | contour band widens; state it in the figure |
| 4 | Reduce K from 10 to **7** for non-headline arms (arm A1, arm A2, arm A5), keep **K=10 for arm A3 and arm A4** | ~20% | only the H_A pair retains full power — which is the pair the pre-registration is about |
| 5 | Drop arm A5 (asymmetric critic) entirely | ~15% | lose the asymmetric-critic arm; it is the least load-bearing of the five |

[§5.4.1, fallback ladder table, whole]

**Do not descend below rung 5 by cutting seeds on arm A3/arm A4.** That pair is the entire
pre-registered experiment, and the TOST margin already has a power problem (below). [§5.4.1]

**The 3 pp TOST margin has no power analysis, and K=10 is probably not enough for it.** At plausible
between-seed standard deviations the equivalence test needs **16-44 seeds**, not 10. Either widen
the margin, or measure the between-seed sd in Stage 2 and **re-derive K before Stage 4 starts** —
`d_MDE = sqrt(15.7/K)` gives the detectable effect, and the margin must exceed `d_MDE * sd`. Report
the retrospective power alongside any equivalence claim (EXIT-4.8 already demands this; this is the
number it demands). [§5.4.1]

---

## Evaluation protocol (§8)

*Heading verbatim: "## 8. Evaluation protocol (frozen at Stage 2, executed at Stage 4)." The
parenthetical is the document's own statement of why this section belongs in this file.* [§8]

```
SETS       TRAIN (generated on the fly)
           VAL   200 per family    -- checkpoint and hyperparameter selection ONLY
           TEST  500 per family    -- evaluated <= 3 times in the whole project
           INFEASIBLE CONTROL  100 -- oracle-unsolvable; correct behaviour is to NOT crash

GENERATION generator_seed recorded in this document; sample from the FULL difficulty
           distribution; v0 = 0, delta0 = 0; filter with Hybrid A* using the ENVIRONMENT's
           exact SAT checker and footprint; store L_oracle, g_oracle, oracle_min_clearance,
           planner_resolution with each scenario; serialize; SHA-256; hard-code the hash.

AT EVAL    deterministic policy  a = a_scale * tanh(mu)   -- the MODE, since E[tanh u] != tanh(E u)
           curriculum PINNED AT MAX          domain randomization OFF
           tolerance == eps_final            normalizer frozen (or fixed analytic constants)
           separate env instances with their own RNG stream
           evaluate at FIXED GRADIENT-STEP counts, never wall-clock
           report BOTH x-axes: environment steps and gradient steps
```

[§8, verbatim block]

**Terminal classification must be mutually exclusive and exhaustive, evaluated on truth, checked at
every substep, first match wins:** `COLLISION > OUT_OF_BOUNDS > SUCCESS > TIMEOUT`. [§8]

**Report percentiles, not means, for every continuous metric.** Conditioned on success, the
final-pose-error distribution is bounded below by 0 and above by the tolerance, so it is strongly
right-skewed and truncated; its mean is dominated by the bulk and says nothing about the marginal
cases — which are exactly the ones that decide whether the result survives a tighter tolerance. [§8]

**Note the arithmetic this file does not resolve:** VAL and TEST are each declared as fixed
per-family counts (200, 500) generated once and hashed [§8], while the success-surface deliverable in
§5.4 calls for "10×10, ≥50 episodes/cell" — at minimum 5,000 episodes per family — against a
parametrised grid of (initial lateral offset, initial heading error) [§5.4]. Nothing in §8 or §5.4
states which set the grid is drawn from, or whether it is itself frozen and hashed under I9. See
Finding 1 in the accompanying report.

---

## Exit criteria (ALL EXIT-4.x, whole)

*Reproduced in full: ID, criterion text, and the complete threshold/rationale text, including every
italicised "why an earlier version got this wrong" clause. Nothing shortened.*

| ID | Criterion | Threshold |
|---|---|---|
| **EXIT-4.1** | Headline success rate | stratified-bootstrap 95% **lower** bound on IQM ≥ **0.90** on each family, K=10 seeds, N=500/family. Programmatic assertion that **no rate is ever printed without an interval** |
| **EXIT-4.2** | Collision upper bound | Clopper–Pearson 95% upper bound ≤ **0.01** pooled over seeds (n=5000/family). Also reported on the INFEASIBLE control set, where the correct behaviour is *not to crash* |
| **EXIT-4.3** | Pose-error margin (fragility check) | p95(\|e_lat\|) ≤ **0.08 m** (80% of the 0.10 m tolerance); p95(\|e_θ\|) ≤ **0.04 rad**; p95(final \|v\|) ≤ **0.03 m/s**; and `P(\|e_lat\| > 0.8·tol \| success)` reported — if 30% of successes sit in the outer 20% of the band, the result will not survive a 1 cm tightening |
| **EXIT-4.4** | Optimality | p50(ρ) ≤ **1.30**, p95(ρ) ≤ **2.00**, `P(ρ<1)` ≤ **0.05** (if exceeded, the planner resolution is too coarse and the metric is not reportable); p50 gear-change excess ≤ 1, p95 ≤ 3; the performance profile **plotted, not summarised** |
| **EXIT-4.5** | Deterministic-vs-stochastic brittleness | `SR_det − SR_stoch ≤ 0.05` **and** `collision_stoch − collision_det ≤ 0.02`. Report both regardless |
| **EXIT-4.6** | Val/test discipline | TEST evaluated ≤ **3 times** over the whole project, each logged with a commit hash and date; no config commit timestamped between a TEST evaluation and the next; both final-checkpoint and best-val-checkpoint TEST scores reported |
| **EXIT-4.7** | Success surface with feasibility overlay | all four curves present in every figure; median agent-to-oracle contour gap ≤ **0.35 m**, with a bootstrap band plotted (never a single number) |
| **EXIT-4.8** | Seed count and completeness | K == **10** for every headline arm; seeds excluded from any aggregate == **0** (a diverged seed is reported as 0.0, never dropped); `d_MDE·σ_between` printed alongside every equivalence claim |
| **EXIT-4.9** | O3 confound audit | differing config keys ⊆ `{policy_architecture, observation_builder, critic_input_source, hidden_width, sequence_length, batch_size}`; parameter counts within **5%**; a derived key `transitions_per_update` held **equal** across arms with `batch_size` free. **State which of the two you hold fixed and report both if the result is close.** *v1.0's version was mutually unsatisfiable: it demanded 8192 transitions per update (256 sequences × 32) while forbidding `batch_size` to differ and pinning it to 256 in Stage 2 — the MLP arms would have to run at a 32× larger batch than anything validated, changing gradient noise and the effective learning rate. The choice is not neutral for a 3 pp equivalence margin.* Also: **define `in`** — the `in=64` in v1.0's parameter arithmetic appears nowhere else in the document; the Stage-2 feature list implies an observation dimension of ~50 |
| **EXIT-4.10** | O3 belief probe (mechanistic evidence) | **(a)** episode-level 60/20/20 split; ridge λ chosen on val; R² on test for poses, **AUC** for the binary `seen` flags. **(b)** three baselines on the identical split: **observation-only probe** (the real floor), an **untrained-GRU reservoir of equal width**, and a **shuffled-target permutation**. **(c)** causal test: project out the probe's top-k subspace (k = rank capturing 95% of probe variance) versus ablating a **random** k-dim subspace, 10 draws, same seeds. **THRESHOLDS:** `R²(hidden) − R²(obs-only) ≥ 0.15` **AND** `R²(hidden)` above the reservoir's 95% bootstrap upper bound **AND** `AUC(seen) − AUC(obs-only) ≥ 0.05`; causal drop **≥ 10 pp** absolute success **AND ≥ 3×** the median random-subspace drop. *v1.1 rewrote this criterion specifically to fix a threshold problem — and left it with **no threshold at all**: "R²(hidden) − R²(obs-only) ≥ X" with X never given, "measure the success-rate drop" with no drop threshold, and the reservoir number deferred to a pilot. As written it could not be failed by any result. It also lacked a random-subspace control, so a causal drop was uninterpretable — ablating **any** subspace degrades performance — which repeats the exact decodability-is-not-use error the criterion was added to prevent. 0.15 R² is about the smallest gap surviving an episode-block bootstrap at these sample sizes; 10 pp is this document's own material-degradation unit (EXIT-3.2/3.10); 3× separates a targeted ablation from generic capacity damage.* |
| **EXIT-4.11** | Dynamics DR is **off** during O3 | programmatic assertion. Hidden dynamics parameters make the MDP partially observed for a **second, unrelated** reason (the agent must implicitly system-identify), a direct confound for H_A. Run condition (B) with DR on, separately and clearly labelled |
| **EXIT-4.12** | Multiple-comparison discipline | ≤ 4 pre-registered comparisons, Holm-corrected; all other pairs explicitly labelled exploratory with no significance claims |

[§5.4, "EXIT CRITERIA — Stage 4," all twelve rows, whole]

> **How to report the null honestly.** If `SR(arm A3) ≈ SR(arm A4)`, the sentence is: *"At observation
> level O2 the parking task is empirically observation-Markov with respect to the hand-written belief
> statistic: a feedforward policy on (last-seen pose, seen flag) is statistically equivalent to a
> recurrent policy within 3 pp (90% CI on the difference: [x, y]; TOST p = z; K = 10 seeds), and a
> linear probe recovers the hand-written statistic from the GRU's hidden state at R² = w."*
> That is a finding about **the task**, not a failure of the experiment. [§5.4]

---

## The O3 hypothesis, stated precisely (§6.4 — read as theory this stage's H_A/H_B rest on)

**Claim.** For obstacles that are (i) static, (ii) observed without noise, and (iii) with known data
association, the map `b_t = { for each object j: (last observed pose q_j, seen_j) }` is an **exact
belief** — the posterior over each object's pose is a point mass at its last observation, and nothing
further can be learned or forgotten. By the belief-MDP sufficiency theorem (Åström 1965; Kaelbling,
Littman & Cassandra 1998), the POMDP reduces to a fully-observable MDP over `b_t`, so a **feedforward**
policy on `b_t` can be optimal and a recurrent policy can at best tie it. [§6.4]

**The theorem, stated properly** (v1.0 stated three preconditions where six are needed): "For a POMDP
with **known** `T, Z, R` and a **known initial belief** `b₀`, the belief `b_t(s) = P(s_t = s | b₀, a₀,
o₁, …, a_{t−1}, o_t)`, updated by `b′ = SE(b,a,o)` via Bayes, is a sufficient statistic for the
history. The induced belief MDP is Markov, and for bounded `R` and `γ < 1` an optimal stationary
deterministic `π*: B → A` exists and is optimal for the POMDP." [§6.4]

Three preconditions v1.0 omitted, two load-bearing here: **(iv)** the model must be known — "exactly
why EXIT-4.11's ban on dynamics randomisation during O3 is load-bearing"; **(v)** `b₀` must be known
and fixed; **(vi)** the belief must cover the entire hidden state — `b_t` as written omits ego state
and object extents `(l,w)`. [§6.4]

**(vii) — THE REAL HOLE — objects never yet seen.** "For an unseen object the belief is the **prior**,
not a point mass... the exact belief for an unseen object is the prior **truncated to the region not
yet swept by the sensor** — a history-dependent statistic of unbounded complexity that a fixed-width
per-object feature vector **provably cannot represent**." Gated by **EXIT-6.2** (§6.6, not read in
full for this file). [§6.4]

**Refinement (A21) — right about τ, wrong about what it means.** Under (i)–(iii), `τ_since_seen` is
genuinely redundant for the state posterior, but τ is **an episode-clock proxy**, normalised by
`max_steps` in §5.2. "**A GRU can learn a clock; an MLP on `b_t` cannot.** This is a legitimate route
by which arm A4 beats arm A3 with every word of the theory intact." H_B is restated: *"if τ helps at
O2, the cause is one of {static-world violated, finite-horizon clock, exploration}, and the τ-zeroed
control (EXIT-6.1) distinguishes the first from the rest."* [§6.4]

> **The never-seen-object row changes the framing of O2.** O2 is *not* cleanly "exact belief, memory
> unnecessary" unless every valid object is visible at `t = 0`. Either enforce that (EXIT-6.2) and
> keep the clean claim, or accept it and state that the exact-belief argument holds only on the
> sub-distribution of episodes where it does. [§6.4]

---

## Privileged training — the caveat (§6.5 — read as theory backing arm A5)

Asymmetric actor-critic (actor sees `o_t`, critic sees `s_t`) is sound and well-established, **but it
is biased.** [§6.5]

> **v1.1 correction — the conclusion was right, the mechanism was wrong.** The critic in asymmetric AC
> estimates `V^π(s)` — the value of *the actor's own history-dependent policy evaluated from a
> state* — **not** the fully-observable optimum `V*(s)`. **The actual defect** (Baisero & Amato,
> "Unbiased Asymmetric Reinforcement Learning under Partial Observability," AAMAS 2022,
> arXiv:2105.11674): their Thm 4.1 — "a time-invariant state value function `V^π(s)` is generally
> ill-defined"; Thm 4.2 — "even when well-defined, `V^π(s)` is generally a biased estimate of
> `V^π(h)`." Their Thm 5.1 establishes a **history-state critic `V(h,s)`** is unbiased. [§6.5]

Cleaner formulations, in the document's stated order of preference: **(1)** teacher–student
distillation — "fits this plan perfectly — Stage 2 produces the teacher for free"; **(2)** critic sees
state plus the actor's hidden state/history — "exactly Baisero & Amato's proposed fix `V(h,s)`";
**(3)** plain asymmetric critic (arm A5) — "keep it because it changes only one thing... But report it
as *biased by construction*, citing the theorems above." [§6.5]

---

## Blocked / out-of-order items

- **EXIT-6.1, EXIT-6.2, EXIT-6.3** govern preconditions H_A/H_B directly depend on — τ-slot discipline
  across arm A1–arm A5, the visibility-floor gate on precondition (vii), and observation-noise-off
  during O3 — but all three are formally §6.6 criteria, not §5.4/EXIT-4.x. [§6.4] [§5.4 pre-registration
  box] This file's brief did not include §6.6 in full, so these are named here as dependencies rather
  than carried whole.
- **§5.4.1 costs "the O2a sweep" and "H_B" into the ~860 GPU-hour Stage-4 training total** [§5.4.1],
  but O2a's own ladder entry is tagged **"Stage 3 end,"** not Stage 4 [§6.1, O2a row], and its
  criterion (EXIT-6.4) lives in §6.6. It is not stated whether §5.4.1 is re-costing an
  already-Stage-3-gated sweep for Stage-4 bookkeeping purposes, or introducing an uncosted-elsewhere
  per-arm replication of O2a across the five O3 arms. Not in the "already known" list for this task;
  see the accompanying report.
- **§0.3's own list of stage-ordering leftovers** — "EXIT-0.8 needs Hybrid A\* (Stage 1); EXIT-1.12
  needs the Stage-2 Observer; EXIT-1.4 and the `ell_OBCA` denominator need two solvers absent from
  Stage 1's build list" [§0.3] — does not name any Stage-4 item; this file found the O2a/H_B item above
  independently and it is of the same family.
- **I3 and I7 still have no executable test** [§0.3, open item 5] — I3 is directly load-bearing for
  the arm A3/arm A4 confound box in §5.4; this file did not locate an executable I3 test beyond the
  pointer "§7.1," which was not read in full.

---

## Known-unreviewed content this stage depends on

*(Per the task brief: these are given, not reported as new findings.)*

- **§5.4.1 in its entirety, EXIT-4.10, and EXIT-4.11 are v1.2 additions.** §0.3 lists "→ **§5.4.1**,
  with a six-rung fallback ladder and step budgets" as one of v1.2's fixes for a hole "open since
  v1.0" (no step budget, ~860 GPU-hours uncosted) [§0.3], and states EXIT-4.10 "ended up with no
  threshold at all... Numbers now specified" [§0.3]. Under "Every v1.2 correction above is itself
  unreviewed. That is exactly the state v1.1 was in when it shipped four fatal errors" [§0.3], all of
  this — the whole compute-budget subsection, its fallback ladder, and two of Stage 4's twelve exit
  criteria — is unreviewed material.
- **The 3 pp TOST margin has a power problem, and K=10 is probably insufficient.** Stated directly:
  "At plausible between-seed standard deviations the equivalence test needs **16-44 seeds**, not 10."
  [§5.4.1]
- **The Stage-4 statistics citation tail was never verified.** §0.1's coverage gap: "the low-priority
  tail of the Stage-4 statistics list (Holm, Clopper–Pearson, Agresti–Coull, Schuirmann, Goodman,
  Efron–Tibshirani, Dolan–Moré, Vargha–Delaney, Machado et al., Pineau et al., Kapturowski et al.,
  Zaheer et al., and the Stage-5 block) was **not reached** before the checker's budget ran out. Those
  remain `[C]`/`[?]` and are not a clean bill of health." [§0.1]
- **Marker legend, unchanged:** `[V]` independently verified in the v1.1 pass; `[C]` standard,
  existence certain, details unchecked; `[?]` **unverified** — "no `[?]` reference may be cited in a
  thesis without opening it first." `[D]` does not appear in this stage's own reading table. [§0.1]
- Within §5.4's own theory table, marked `[?]`: **Patterson, Neumann, White & White (2024)**,
  **Colas, Sigaud & Oudeyer (2018)**, **Wilson (1927)** *(later upgraded — see below)*, **McNemar
  (1947)** *(later upgraded)*, **Holm (1979)**, **Ni, Eysenbach & Salakhutdinov (2022)** *(later
  upgraded)*, **Pinto, Andrychowicz, Welinder, Zaremba & Abbeel (2018)** *(later upgraded)*. [§5.4
  theory table]
- **Some `[?]` markers in §5.4's list were upgraded on verification elsewhere in the document:**
  "Wilson (1927), McNemar (1947), Åström (1965), Pinto et al., Patterson et al. and Ni et al. all
  check out exactly; the drafting agents' stated uncertainty about them was unwarranted." [§0.1] This
  file leaves the §5.4 table's markers exactly as printed there, per the no-upgrade rule, and notes
  the upgrade only as cross-reference.
- **§5.4/§0.4's bay-family clauses are v1.3 material**, hence unreviewed under the same rule: "the
  bay family had no gate and no defined surface. Each now carries its `η_bay` counterpart" [§0.4], and
  "everything in §0.4 is new, and therefore unreviewed... the *framing* around it... has had exactly
  one pair of eyes on it." [§0.4]
- **Already known, per this task's brief, not reported as a new finding:** the Stage-4 arm names
  **arm A1–arm A5** collide with assumption IDs **A1–A5** in §2; this file's disambiguation convention
  is stated at the top of this document. [§5.4] [§2]

---

## Failure modes here (§9 rows whose own text ties them to Stage 4)

*Reproduced verbatim; pointer is [§9] for all, plus the specific EXIT/section each row itself cites.
§9 was not read in full for this file — only rows a keyword match (arm names, IQM, K, checkpoint,
EXIT-4.x, EXIT-4.11) surfaced.*

| Symptom | Likely cause | Fix / test |
|---|---|---|
| A perfect arm reports "100.0% ± 0.0%"; a zero-collision arm reports "0.0% ± 0.0%" | Wald interval | Wilson / Clopper–Pearson |
| Every arm's IQM is exactly 1.000 with a zero-width CI | IQM applied to raw binary outcomes instead of per-run rates | §5.4 |
| A 4 pp ordering flips when a fourth seed lands | K = 3 | K = 10; EXIT-4.8 |
| The reported number is 4–6 pp above any nearby checkpoint, and moves down that much on a re-eval | Checkpoint selected by argmax on the reported set | select on VAL, report on TEST; EXIT-4.6 |
| GRU arm learns visibly faster per gradient step | It is receiving 32× more transitions per update (sequences vs transitions) | EXIT-4.9 |
| GRU beats the belief-MLP, apparently refuting H_A — **and the effect persists even with perfect visibility** | Dynamics randomisation left on: the agent must system-identify, a second and unrelated source of partial observability | EXIT-4.11 |

[§9, rows as quoted]

---

## Derived by this decomposition (not in PLAN_MACRO)

The section headers, the "arm A#" vs bare "A#" disambiguation convention, and the grouping of
assumptions/invariants under "live here" headings are this file's own organisational choices,
following the template given for this task — not text found verbatim at any single location in
`PLAN_MACRO.md`. Every factual claim inside those groupings is individually back-pointed to its source
above. The selection of which §9 rows "belong" to Stage 4 is this file's own judgement call, made from
each row's own EXIT pointer (EXIT-4.6, EXIT-4.8, EXIT-4.9, EXIT-4.11) or explicit textual tie to §5.4.
Adversarial analysis of internal consistency (the full argument behind each item in "Blocked /
out-of-order items" and any numbered finding) belongs in this file's accompanying report, not repeated
here to avoid duplicating an assessment inside a verbatim-transcription section.
