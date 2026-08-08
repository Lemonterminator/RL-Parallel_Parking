# PLAN_MACRO.md — Reinforcement Learning for 2D Car Parking

**A staged project plan: assumptions, theory, build order, and stage-gate exit criteria.**

Version 1.2 · 2026-08-06 · self-contained (no prior conversation required)

> **v1.2 — the verification is now complete.** All nine planned agents have run: 4 citation
> checkers, 3 independent re-derivation agents, and the two audits (completeness critic,
> exit-criteria falsifiability auditor) that failed three times on session limits.
>
> **The citations held up: 39 exact, 7 corrected in detail, 11 unverifiable, zero fabricated.** Of 14
> numeric claims recomputed from scratch, 10 reproduced exactly. **The prose did not hold up.** Across
> v1.0 and v1.1 the audits found **9 fatal and 55 serious defects** — and, importantly,
> **4 of the 9 fatal ones were introduced by v1.1's own corrections**, which had been written in
> response to agent findings and reviewed by nobody. The most instructive example: v1.1 "fixed" a
> gradient plateau at 180° by proposing a term whose derivative is also exactly zero at 180°.
>
> **This is the load-bearing lesson of the whole exercise: a correction is a new claim.** Every
> v1.2 change is marked inline, and every one of them is now itself unreviewed. Read §0.2.

---

## 0. How to read this document

This plan describes a 2D reinforcement-learning agent that parks a rectangular car into a
rectangular slot — parallel parking and reverse bay parking — using a kinematic bicycle model
and exact rectangle collision geometry.

It is organised as:

- **§1–§4** — what the project is, what it assumes, and the invariants that hold at *every* stage.
- **§5** — six sequential stages (0–5). Each has: goal, theory to read, math to derive by hand,
  what to build, and **hard exit criteria** that must pass before the next stage begins.
- **§6** — an *orthogonal* observation-degradation ladder (O0–O4) mapped onto those stages.
- **§7–§11** — reward specification, evaluation protocol, failure-mode diagnostics, consolidated
  reading list, notation.

**Exit criteria are contractual.** Every one is a number, a statistical test, or a boolean
assertion checkable by a script with no human judgement. Wherever this plan is tempted to say
"the trajectories look smooth" it says instead "p95 of `Jbar_ddelta` ≤ X on the frozen test set."

### 0.1 Citation verification status — read this before citing anything

| Marker | Meaning |
|---|---|
| `[V]` | **Independently verified in the v1.1 pass** against a retrieved publisher record, DOI resolver, dblp, PMLR, arXiv, JMLR or the PDF itself. |
| `[C]` | Standard, widely-cited reference; existence certain, page/volume numbers **not** independently checked. |
| `[?]` | **Unverified.** Author list, venue, year, or page range may be wrong. Verify before it enters a bibliography. |
| `[D]` | *(added v1.3)* **Not a citation.** Derived inside this document and checked against an independent numerical construction, with the agreement figure stated. Carries no literature claim — if a published result contradicts it, the published result has not been consulted. |

**Rule: no `[?]` reference may be cited in a thesis without opening it first.**

**v1.1 outcome across 57 checked citations: 39 exact · 7 wrong in detail (corrected inline) · 11
unverifiable · 0 fabricated.** The seven corrections were: the Skalse camera-ready title is *"Reward
Gaming"*; "ALP-GMM" is Portelas et al.'s *algorithm*, not their paper title; Vorobieva is **two**
distinct papers with different author orders; "Learning by Cheating" should drop its bare "(2020)";
Banzhaf's full title and six authors; and — the only genuine misattribution — **v1.0 presented
"case (a)"/"case (b)" as Pardo et al.'s own notation, but the paper labels those regimes (i) and
(ii).** The policy recommendation was represented correctly; only the labels were invented.

Several `[?]` markers were **upgraded** on verification — Wilson (1927), McNemar (1947), Åström
(1965), Pinto et al., Patterson et al. and Ni et al. all check out exactly; the drafting agents'
stated uncertainty about them was unwarranted.

**Coverage gap:** the low-priority tail of the Stage-4 statistics list (Holm, Clopper–Pearson,
Agresti–Coull, Schuirmann, Goodman, Efron–Tibshirani, Dolan–Moré, Vargha–Delaney, Machado et al.,
Pineau et al., Kapturowski et al., Zaheer et al., and the Stage-5 block) was **not reached** before
the checker's budget ran out. Those remain `[C]`/`[?]` and are not a clean bill of health.

Two known citation traps are documented in §10.

### 0.2 What v1.1 changed *(historical — superseded by §0.3)*

**Fatal (§4.1, rewritten).** The "feasibility knife edge" was wrong three ways: the inequality is not
an *iff* (`a_max` is an upper bound, not a mandate, so a dwell-free reversal is *always* available);
the parameter set does not sit *on* the edge (under bang-bang it holds only at exactly `v_max`, while
real cusps happen at 0.3–0.7 m/s); and **two of the three stated randomisation directions were
inverted** — lowering `a_max` makes a cusp *easier*, not harder.

**Serious, by section.** §5.0(b): the 5.62 m two-arc figure is unexecutable — the rate-limited
vehicle needs 6.18 m at 0.5 m/s. §5.0(c): the frame was under-specified and condition (ii) named the
wrong corner; a whole constraint (swing into the traffic lane) was missing. §5.0(g)/§7.3: `1 − cos Δθ`
has **zero gradient at 180°**, exactly where reverse bay parking starts. **EXIT-0.2, 0.3, 0.4 and 0.5
would all have failed on correct code or passed trivially** — all four rewritten. §6.4: three of six
preconditions of the central theorem were missing, one of them a real hole (**objects never yet
seen**, whose exact belief is a truncated prior that a fixed-width vector cannot represent). §6.2:
the radius-sensor rung was excluded on a premise the geometry refutes — R ∈ [5,8] m bites hard.
§6.5: right conclusion, wrong mechanism (the correct citation is Baisero & Amato). §5.2: `τ_since_seen`
is a clock proxy normalised by `max_steps`, contradicting the time-unaware commitment. EXIT-4.9 was
mutually unsatisfiable; EXIT-4.10 conflated decodability with use and used a reservoir as its control.

### 0.3 What v1.2 changed — including four fatal defects introduced by v1.1 itself

**v1.1's own corrections, found wrong (the important category).**
- **§7.3 Defect 3.** v1.1 proposed adding a `(1 − cos Δθ)^(1/2)` term "which has non-zero slope at π".
  It does not: `sqrt(1 − cos x) = √2·|sin(x/2)|`, derivative `(√2/2)·cos(x/2)`, **exactly zero at π**.
  The sqrt form fixes the *near*-field plateau (Defect 2), not the 180° one. v1.1 had the two
  defects' fixes crossed and presented a broken option beside a correct one.
- **The `w_th` factor-4 change was never propagated.** §7.2 still printed `w_th = 2.63` from the old
  expansion, and §5.0(g) still printed the old saturation bound. Both corrected.
- **EXIT-2.28 was 44× too loose.** v1.1's `12280` assumed the worst-case shaping step could recur
  every step — contradicting the telescoping identity that a *sibling criterion* enforces. It also
  summed two mutually exclusive terminals. Correct supremum ≈ 158.65; raise at ~320.
- **EXIT-4.10 ended up with no threshold at all.** Rewritten in v1.1 specifically to fix a threshold
  problem, it shipped with "≥ X" where X was never given. Numbers now specified.
- **EXIT-6.1 forbade the observation H_B is defined to test**; **EXIT-6.2 contradicted EXIT-6.4** and
  carried an opt-out that made it unfailable. Both rewritten.
- **Stale cross-references** to the withdrawn "§4.1 knife edge" survived in §5.3, §9 and the
  provenance appendix — which still listed the *retracted* claim among independently corroborated
  numbers. Removed.

**Holes that had been open since v1.0.**
- **No criterion asserted where the body rectangle sits relative to the rear axle.** If the footprint
  is centred, or f and r swapped, *every* Stage-0/1/2 criterion still passes — the planner and the
  environment share the footprint, so "the checkers agree" confirms they agree while both are wrong.
  Collision geometry off by up to 1.25 m, invisibly. → **EXIT-0.10**.
- **Nothing tested that the simulator enforces its own actuator limits.** A drifting `δ` gives the RL
  car a turning radius the baselines lack — inflated success and an artefactual win. → **EXIT-0.11**.
- **`settle_counter` was hidden state.** Success needs 5 consecutive in-tolerance steps, but the
  counter was in no state, no observation, no assumption — so **O0 was not observation-Markov**, and
  the "full-state MDP" premise of §5.2, §6.1 and H_A was false. → **A22**, plus the observation block.
- **I4 named five consumers of terminated/truncated and gated one.** → **EXIT-2.29**.
- **Stage 2's gate was strictly harder than Stage 3's**, so Stage 2 would deadlock or make Stage 3 a
  null result by construction. → EXIT-2.27 rebased onto the easy sub-distribution.
- **Stage 4 costs ~860 GPU-hours** and no stage had a step budget, making every performance gate
  unfalsifiable — while v1.1 forbade its own cheapest fallback (K=3 banned, K==10 asserted).
  → **§5.4.1**, with a six-rung fallback ladder and step budgets.
- Six further unstated assumptions promoted to §2: **A22–A26** (settle counter, latency augmentation,
  integrator scheme, one-vs-two policies, `L_oracle` definition).

**Still open after v1.2 — read this before trusting the document.**
1. **Every v1.2 correction above is itself unreviewed.** That is exactly the state v1.1 was in when it
   shipped four fatal errors. A fourth verification pass is warranted before any of this is built on.
2. ~~**Reverse bay parking has no geometry.**~~ **Closed in v1.3 — see §0.4 and §5.0(c′).**
3. **n-step returns are "NOT OPTIONAL" and have no exit criterion**, and the off-policy bias they
   introduce is nowhere acknowledged.
4. Stage-ordering leftovers: EXIT-0.8 needs Hybrid A\* (Stage 1); EXIT-1.12 needs the Stage-2
   Observer; EXIT-1.4 and the `ell_OBCA` denominator need two solvers absent from Stage 1's build list.
5. I3 and I7 still have no executable test.
6. The Stage-4 statistics citation tail and the whole Stage-5 block were never checked (§0.1).
7. The Fraichard & Scheuer "infinite chattering" claim could not be verbatim-confirmed (appendix).

### 0.4 What v1.3 changed — the reverse-bay geometry that was never there

v1.3 closes open item 2 of §0.3: **reverse bay parking, half the headline task, had no geometry at
all.** It is now derived, in closed form, and machine-checked.

- **§5.0(c′)** — new. Frame, manoeuvre, the swept-footprint decomposition, and the exact single-cut
  feasibility boundary. The whole boundary turns out to be expressible in **three radii §4 already
  tabulated**: `W_aisle_min = R_front_outer − sqrt(R_swept_inner² − (R_rear_outer − W′)²)`. Four
  independent identities check it, including one that reproduces §4's swept-corridor width
  (3.0358 m) from a different direction. Validated against an explicit 40 001-sample swept body to
  **1e-10 m**.
- **A static containment lower bound valid for any number of cuts** — 3.5100 m at `psi = 53.0°` for
  the reference bay — bracketing the true boundary in **[3.5100, 4.3519]**.
- **§4** — a `BAY SCENE` block: `W_bay = 2.50`, `D_bay = 5.30`, `W_aisle = 6.00`, `c_end = 0.30`,
  goal pose `(0, −3.90, +π/2)`, plus the derived quantities.
- **A27** (`W_gap` is declared, not derived — the wall vs. neighbour-car model is worth 0.69 m of
  aisle) and **A28** (`W_aisle`, not `W_bay`, is the difficulty axis).
- **EXIT-0.13 / 0.14 / 0.15** — closed form vs. swept body with a positive control; the multi-cut
  bracket plus a Stage-1 planner cross-check; the goal pose and the **nose-in trap** (enabling the
  §5.0(g) two-corner heading matching silently converts the task into forward bay parking).
- **EXIT-2.27, EXIT-3.1, §5.4's success surface** — all three named a parallel-parking difficulty
  axis only, so the bay family had no gate and no defined surface. Each now carries its `η_bay`
  counterpart.
- A refinement, not a correction, to the 180°-plateau discussion: the *canonical* bay start sits at
  `Δθ = π/2` where the gradient is 1.0. The π case comes from the Stage-3 randomised start
  distribution, not from the manoeuvre.

**And the same caveat as always, which v1.2 proved is not rhetorical: everything in §0.4 is new,
and therefore unreviewed.** The derivation is machine-checked against an independent numerical
sweep, which is stronger than v1.1's corrections ever were — but the *framing* around it (which
model is conservative, which gate belongs where, whether the single-arc family is the right one)
has had exactly one pair of eyes on it.

---

### 0.5 What v1.4 changed — preference learning as a Stage-5 direction

Content, not correction. Answers "where would a DPO variant go?" with a placement, a shape, and two
cheap kill-switches.

- **§5.5 candidate table** — a sixth direction, and **§5.5.1**: why **CPL** rather than DPO (its
  max-entropy derivation sits on the SAC commitment **A11** already made), the four-arm design with
  **P3 — synthetic preferences from the known reward — as a gate that runs first**, the tanh-saturation
  and `beta`-versus-safety traps, and a full treatment of **human teleoperation data**.
- **The framing that keeps it defensible:** this task has a *computable* reward, so the target is the
  **style** component the reward cannot express, and the contribution is a controlled measurement of
  preference-learning sample complexity — not "we applied DPO to parking", which walks straight into
  **A19**.
- **EXIT-1.13** — freehand paths are strictly worse than the RS paths **A15** already forbids as raw
  demonstrations, because nothing bounds their curvature. A 1–2 day probe that kills sketch input
  cheaply if it is going to die.
- **EXIT-1.14** — teleoperation logs must replay bitwise, must not encode the operator's ~250 ms
  reaction lag (**A23** arriving through the human), and must not smuggle O0 visibility into an O2+
  arm (**§6.5**).
- **§10** — a preference-based-RL reading block, **entirely `[?]`**.

**Unreviewed, and this one is weaker than §0.4:** §0.4's arithmetic was machine-checked against an
independent construction. Nothing here is. The citations are from memory, the four-arm design has had
one pair of eyes on it, and the claim that CPL's max-entropy identity composes cleanly with this
plan's SAC configuration is an **argument**, not a verified derivation.

---

## 1. Project statement

Build and evaluate a reinforcement-learning controller for low-speed car parking in 2D, and
compare it honestly against classical motion planning.

**Scope.** Rigid rectangular ego vehicle; static rectangular obstacles; kinematic bicycle
dynamics; two task families (parallel parking, reverse bay parking); continuous control.

**What this project is *not*.** It is not an attempt to beat Hybrid A* at path planning on a known
static map. On a known static map with exact geometry, search and optimisation essentially solve
this problem: Hybrid A* plus gradient smoothing finds a drivable, collision-checked path in well
under a second. A pure-RL success rate on that setting is a **sanity check on the MDP, reward and
simulator — not a contribution.** The contribution has to live where RL is genuinely better, which
is §5.5.

---

## 2. Assumptions

Numbered so they can be cited and revisited. Each states what breaks if it is wrong.

### 2.1 Physical / modelling

| # | Assumption | If wrong | Revisit at |
|---|---|---|---|
| **A1** | Kinematic bicycle model is adequate; no tyre slip, no load transfer, no body roll. | Trajectories diverge from a dynamic model above ~2 m/s. At parking speeds (≤1.5 m/s) the error is negligible. | Stage 5, only if pursuing sim-to-real |
| **A2** | The reference point is the **rear-axle midpoint**, not the CoG. | The heading ODE `θ̇=(v/L)tan δ` is *only* valid at the rear axle. Using it with a CoG reference gives a systematically wrong turning radius. | Never — this is invariant I1 |
| **A3** | Steering angle `δ` is the equivalent single-track road-wheel angle, not the steering-wheel angle. | All turning-radius arithmetic is off by the steering ratio (~15:1). | Never |
| **A4** | Obstacles are **static** within an episode, and their count and identity are known. | The O3 hypothesis (§6.4) becomes false, and the hand-written belief filter stops being an exact sufficient statistic. | Deliberately broken at O4 |
| **A5** | The world is planar. No kerb height, no ramps, no 3D clearance. | The kerb becomes a 2D polygon obstacle rather than a mountable edge — a modelling choice, stated explicitly. | Never |
| **A6** | Actuators are rate-limited but otherwise ideal: no backlash, no deadband, no latency. | Real steering has 100–200 ms latency. Deliberately introduced as a Stage 3 randomisation. | Stage 3 |

### 2.2 Task definition

| # | Assumption | If wrong | Revisit at |
|---|---|---|---|
| **A7** | Success requires position, heading, **and near-zero speed**, sustained for a settle window. | Without the speed and settle conditions the agent flies through the goal pose at 1.5 m/s and claims success on one frame. | Never |
| **A8** | The goal slot pose is **known** to the agent (part of the observation) through O3. | At O4 the slot must be detected, with noise. Design the slot as a typed object in the object list *now* so this costs nothing later. | O4 |
| **A9** | The scenario distribution is fixed and defined by a generator with a recorded seed. | Every historical comparison becomes incomparable. Enforced by hashing (EXIT-2.1). | Never |
| **A10** | "Feasible" means **"solvable by our Hybrid A* at the declared grid resolution"**, not "geometrically possible". Hybrid A* is resolution-complete, not complete. | The frozen eval set is biased toward scenarios the planner can solve; the RL success rate is measured against a denominator that is itself a lower bound on true feasibility. **State this in the thesis rather than hide it.** | Never — state it |

### 2.3 Algorithmic

| # | Assumption | If wrong | Revisit at |
|---|---|---|---|
| **A11** | SAC is the default learner; off-policy is chosen specifically so demonstrations can seed the replay buffer. | If you switch to PPO for wall-clock reasons you lose demo seeding and gain a second horizon parameter (GAE λ). See §5.2. | Stage 2 exit, Stage 4 |
| **A12** | γ = 0.995 with `max_steps` = 400, chosen from the manoeuvre timescale (a real park is 120–250 policy steps). | γ = 0.99 makes the terminal bonus invisible; γ = 0.998 pushes the effective horizon past the episode limit. Both are measured, not assumed — see EXIT-2.11. | Stage 2 exit |
| **A13** | The dense reward term is **strictly potential-based**, so it cannot change the optimal policy or be farmed. | Any non-potential dense term reintroduces hovering/farming. Enforced by an executable identity test (EXIT-2.6). | Never |
| **A14** | The policy is evaluated **deterministically** (`a = a_scale·tanh(μ)`, the mode). | The max-entropy objective is a training device; reporting the stochastic policy measures the wrong objective and inflates the collision rate by an amount that depends on the learned α. | Never |
| **A15** | Reeds–Shepp demonstrations must be **executed through the environment by a tracking controller**, never used as raw (state, action) pairs. | RS paths have discontinuous curvature; the implied `δ̇` is unbounded. Raw RS actions lie outside the action box. | Never |

### 2.4 Engineering

| # | Assumption | If wrong | Revisit at |
|---|---|---|---|
| **A16** | `WorldState` (truth) and `Observation` (policy-visible) are distinct types from day one. | The entire O1–O4 ladder becomes a rewrite instead of a config change, and reward/collision leaks are undetectable. | Never — invariant I2 |
| **A17** | `terminated` and `truncated` are carried as two separate booleans all the way into the replay buffer. | The most common silent bug in the project. See §5.2. | Never — invariant I4 |
| **A18** | The simulator is cheap enough to vectorise (2D integrator + SAT on a handful of OBBs), so throughput is not the binding constraint at Stage 2. | If it is, that changes the SAC-vs-PPO calculus, not the plan structure. | Stage 4 |

### 2.5 Research framing

| # | Assumption | If wrong | Revisit at |
|---|---|---|---|
| **A19** | On a known static map, classical planning solves this problem, so the O0 RL result is a sanity check and not a contribution. | If you present O0 as the result, the first question in a defence is why Hybrid A* is not simply better. | Never |
| **A20** | For static, noise-free, known-association obstacles, a hand-written filter storing `(last-seen pose, seen flag)` is an **exact** sufficient statistic, so a feedforward policy on it can be optimal and a GRU can at best tie it. | This is the project's central falsifiable hypothesis. It is pre-registered, not assumed true. See §6.4. | Tested at Stage 4 |
| **A21** | `time-since-seen` (τ) is **redundant** in the strictly static, noise-free case (the object has not moved; staleness carries no information). It earns its place only once objects can move or detections can be false. | If including τ measurably helps at O2, assumption A4 (static world) is being violated somewhere in the implementation. This is a free extra ablation and a useful bug detector. **v1.2: the inference is weaker than this — see §6.4, τ is also a clock proxy.** | O2 |
| **A22** | **`settle_counter` is part of the state and is observable at every rung.** Success requires the tolerance conditions to hold for `K_settle` consecutive steps, which is not a function of a single pose. | Without it the task is a **POMDP even at O0**, and the "full-state MDP" premise of §5.2, §6.1 and H_A is false. Added in v1.2; v1.0 and v1.1 both omitted it. | Never |
| **A23** | Actuator **latency** (introduced by Stage-3 DR, A6) requires state augmentation with the in-flight command buffer. | Latency makes the reward a function of history in exactly the way §7.4 rules ILLEGAL for the action-rate term. If you randomise latency without augmenting, the critic is biased by state aliasing at every step, not just at reversals. | Stage 3 |
| **A24** | Integration is **explicit Euler with zero-order hold** on the action across the 5 substeps. | Never stated in v1.0/v1.1, yet EXIT-0.2's closure tolerance and EXIT-0.5's per-substep displacement bound both depend on it. A switch to RK4 changes both. | Stage 0 |
| **A25** | Parallel parking and reverse bay parking are solved by **one policy** conditioned on the scenario, not two. | If two, every "success rate" in the document is two numbers, K doubles, and the Stage-4 compute estimate doubles with it. Never stated. | Stage 2 |
| **A26** | `L_oracle` is the **post-smoothing Hybrid A\*** path length, frozen with the scenario set. | ρ is not comparable across experiments if this drifts. §5.1 offers three denominators; only one can be *the* frozen one. | Stage 1 |
| **A27** | **`W_gap` — the free lateral width at the bay mouth — is a declared scene parameter, not something the generator derives from `W_bay`.** Default is the conservative wall model `W_gap = W_bay`. | The two models differ by `W_bay − w` = 0.65 m, which is **0.69 m of required aisle**. Derived silently, every frozen bay scenario carries a mislabelled difficulty and the EXIT-0.14 bracket is checked against the wrong number. Added v1.3. | Stage 0 |
| **A28** | The bay family's difficulty scalar is the **aisle slack ratio** `η_bay = W_aisle / W_aisle_min(W_gap; R_min, c=0)`, and `W_aisle` — not `W_bay` — is the axis that gets varied. | `W_bay` has ~0.7 m of usable range against `W_aisle`'s ~2.8 m; banding on `W_bay` gives a curriculum with almost no dynamic range and a Stage-3 gate that means nothing. Added v1.3. | Stage 3 |

---

## 3. Invariants

These hold at **every** stage. Violating one invalidates results silently, which is why each has a
test attached.

| # | Invariant | Test |
|---|---|---|
| **I1** | Rear-axle reference point everywhere. `R = L/tan δ` refers to the rear axle only. | EXIT-0.2 |
| **I2** | Reward, success test, and collision test read `WorldState`. **Never** `Observation`. | EXIT-2.12 |
| **I3** | Observation is **ego-frame**; pose error / reward is **goal(slot)-frame**. | §7.1 |
| **I4** | `terminated` ≠ `truncated`. Five consumers must be audited: TD bootstrap mask, Φ zeroing, n-step return cut, episode logger, curriculum counter. Never construct `done = terminated or truncated`. | EXIT-2.5 |
| **I5** | Exact SAT decides collision/termination. The 3-circle body model appears **only** in the smooth reward term, never in a metric or a termination test. | EXIT-2.8 |
| **I6** | Collision detection runs at **every physics substep**; reward is evaluated **once per policy step**. | EXIT-2.9, EXIT-2.13 |
| **I7** | Angles enter observations as `(sin, cos)` pairs, never raw. | static check |
| **I8** | The per-object feature vector has **identical width at every observation stage** O0–O4. | EXIT-1.12 |
| **I9** | The frozen eval set is hashed and never regenerated. | EXIT-2.1 |
| **I10** | Action space is `Box(-1, 1, shape=(2,))`. Physical scaling happens in exactly one place, inside the environment. | EXIT-2.14 |

---

## 4. Reference parameters

```
VEHICLE
  L        wheelbase                     2.70 m
  l        total length                  4.70 m      (= L + f + r, exactly)
  w        width                         1.85 m
  f        front overhang                0.90 m
  r        rear overhang                 1.10 m
  delta_max      steering limit          0.60 rad  (34.4 deg road-wheel)
  delta_dot_max  steering rate limit     0.60 rad/s
  v_max          speed limit             1.50 m/s
  a_max          accel limit             1.50 m/s^2

DERIVED GEOMETRY  (independently computed by two agents; re-verify at Stage 0)
  kappa_max        = tan(0.6)/2.7                    = 0.25338  1/m
  R_min            = L/tan(delta_max) = 2.7/0.684137 = 3.9466 m   <- REAR AXLE only
  R_front_outer    = hypot(L+f, R_min + w/2)         = 6.0574 m   <- the binding radius
  R_front_inner    = hypot(L+f, R_min - w/2)         = 4.7000 m
  R_rear_outer     = hypot(r,   R_min + w/2)         = 4.9942 m
  R_rear_inner     = hypot(r,   R_min - w/2)         = 3.2156 m
  R_swept_inner    = R_min - w/2                     = 3.0216 m   <- inner flank at s=0
  swept corridor   = 6.0574 - 3.0216                 = 3.0358 m
  outer turning diameter = 2 * 6.0574                = 12.115 m   (realistic for a sedan)
  d_max (rear axle to farthest body point) = hypot(L+f, w/2)     = 3.7169 m

BAY SCENE  (reverse bay parking -- see 5.0(c'); added v1.3, previously absent entirely)
  W_bay    bay width                        2.50 m
  D_bay    bay depth                        5.30 m   (= l + 0.60; 0.30 m clear at each end)
  W_aisle  aisle width                      6.00 m   <- THE difficulty axis for this family
  W_gap    free lateral width at the mouth  2.50 m   (= W_bay, the wall model -- see A27)
  c_end    longitudinal clearance           0.30 m
  goal pose  rear axle (0, -3.90), theta = +pi/2  (nose OUT; body spans y in [-5.00, -0.30])

DERIVED BAY GEOMETRY  (single arc at R = R_min; closed form validated to 1e-10 -- see 5.0(c'))
  NOTE: the whole boundary is expressed in three radii ALREADY TABULATED ABOVE.
  u*  = sqrt(R_swept_inner^2 - (R_rear_outer - W_gap)^2)             = 1.7055 m
  W_aisle_min (zero side clearance)  = R_front_outer - u*            = 4.3519 m
  W_aisle for ZERO incursion past the mouth line = R_front_outer + r = 7.1574 m
  W_aisle absolute single-cut floor  = R_front_outer - R_swept_inner = 3.0358 m  (= swept corridor)
  containment lower bound, ANY number of cuts, W_bay = 2.50          = 3.5100 m  at psi = 53.0 deg
  side clearance at the 6.00 m design value                          = 0.2634 m
  MAX achievable side clearance = (W_bay - w)/2                      = 0.3250 m
  eta_bay = W_aisle / W_aisle_min   at the reference scene           = 1.379

INTEGRATION AND LEARNING
  dt_policy   0.10 s        n_substeps  5  (dt_sub = 0.02 s)
  max_steps   400  (= 40 s = 2 x effective horizon)
  gamma       0.995         -> H_eff = 1/(1-gamma) = 200 steps = 20 s
```

### 4.1 Cusps and the cost of a steering reversal

> **Version 1.1 correction.** v1.0 of this document presented the material below as a "feasibility
> knife edge" and got it wrong in three ways: the inequality is not an *iff*, the parameter set does
> not sit *on* the edge in any operationally meaningful sense, and two of the three stated
> randomisation directions were **inverted**. The corrected treatment follows. Retained because the
> underlying quantity — what a cusp costs — is real and matters for the reward and the curriculum.

**The bang-bang statement.** *Under a bang-bang reversal at `|a_long| = a_max`*, a cusp absorbs a
full lock-to-lock steering swing without dwelling at v = 0 iff

```
v / a_max  >=  delta_max / delta_dot_max
```

with `v` the speed at which the cusp is entered. At `v = v_max` both sides equal exactly 1.000 s.

**But `a_max` is an upper bound, not a mandate, so this is not a feasibility boundary at all.**
The reversal takes `T = 2v/|a|`; the swing needs `T_s = 2·delta_max/delta_dot_max = 2.0 s`; the
policy needs `T >= T_s`, i.e. `|a| <= 2v/T_s`. Since `|a|` may be chosen arbitrarily small, **a
dwell-free reversal is always available at any `v > 0`, and `a_max` never binds.** The deceleration
required to reverse in exactly `T_s` is `a_req = v·delta_dot_max/delta_max = v`, which is `<= a_max`
at every admissible speed.

**What actually varies is cost, not feasibility:**

```
dwell-free reversal:  extra travel = v * delta_max/delta_dot_max metres
                      (0.50 m at v = 0.5 m/s), versus v^2/a_max = 0.167 m for bang-bang
dwelling reversal:    extra time >= 1.33 s at v = 0.5 m/s, at ~zero extra distance
```

This is a trade-off the **reward** resolves, not a constraint the dynamics impose.

**The speed dependence is the real design fact, and it points the opposite way to v1.0's warning.**
Under the bang-bang reading the available reversal time `2v/a_max` shrinks linearly with approach
speed while the 2.0 s swing time is fixed:

```
v = 1.5 -> 2.000 s   fits exactly, zero margin
v = 1.0 -> 1.333 s   short by 0.667 s =  6.7 policy steps
v = 0.7 -> 0.933 s   short by 1.067 s = 10.7 policy steps
v = 0.5 -> 0.667 s   short by 1.333 s = 13.3 policy steps
v = 0.3 -> 0.400 s   short by 1.600 s = 16.0 policy steps
```

Parking cusps happen at 0.3–0.7 m/s, never at 1.5 m/s. So the parameter set does not sit *on* an
edge — under bang-bang it sits on the **wrong side of it for every realistic cusp**, before any
randomisation. The 1.000 s coincidence at `v_max` is real but operationally irrelevant.

**Budget it.** A 4-cusp manoeuvre in which the policy dwells rather than decelerating gently costs
roughly **53 policy steps of pure dwell** against `max_steps = 400`. That is 13% of the episode
budget and it interacts directly with §5.3(e)'s succeed-versus-stall margin, which is already
labelled MARGINAL at N = 400.

**Randomisation directions — v1.0 had these backwards.** Let the slack be
`S = v/a_max − delta_max/delta_dot_max`. Then `dS/da_max = −v/a_max² < 0` and `dS/dv = +1/a_max > 0`:
**lowering `a_max` makes a cusp *easier*** (the reversal takes longer, giving the steering more time),
and **raising `v_max` also makes it easier.** The parameters that make a cusp harder are those that
shorten the reversal or lengthen the slew:

| Randomising… | Effect on the cusp |
|---|---|
| `delta_dot_max` **down** | harder — longer slew |
| `delta_max` **up** | harder — longer slew |
| `a_max` **up** | harder — shorter reversal |
| `v_max` **down** | harder — shorter reversal |

**Action:** treat cusp cost as a reward-design and curriculum question (§7.4's `w_gear` budget), not
as a feasibility constraint. If you randomise the four parameters above, know which direction makes
the task harder — and note that it is the opposite of what intuition suggests for `a_max`.

### 4.2 Discount arithmetic — do this once, freeze it, test it

```
gamma^N = exp(N ln gamma)     ln(0.99)=-0.01005034  ln(0.995)=-0.00501254  ln(0.998)=-0.00200200

              gamma^300    gamma^400    sum_{t<400} gamma^t     H_eff
  0.990        0.04904      0.01795          98.20            100 steps = 10 s
  0.995        0.22229      0.13466         173.07            200 steps = 20 s
  0.998        0.54848      0.44897         275.52            500 steps = 50 s
```

A +100 terminal bonus, seen from t = 0 at N = 400, is worth **1.80** at γ=0.99, **13.47** at
γ=0.995, **44.90** at γ=0.998. Against a modest dense stream of |c| = 0.05/step accumulating to
8.65 at γ=0.995, only γ ≥ 0.995 leaves the terminal bonus visible.

γ = 0.998 is rejected because `H_eff = 500 > max_steps = 400`: the effective horizon must stay
**strictly below** the episode limit, ideally near half of it.

If `dt` ever changes, hold the continuous time constant `tau = -dt/ln(gamma)` fixed and recompute
`gamma_new = exp(-dt_new/tau)`.

---

## 5. Stage ladder

### 5.0 Stage 0 — Geometry and kinematics kernel *(no RL)*

**Goal.** A unit-tested geometric and kinematic core. Everything downstream consumes it, so a bug
here is a bug in every later result.

#### Theory and mathematics to read

| Priority | Source | Covers |
|---|---|---|
| must | `[C]` LaValle, S. M. (2006). *Planning Algorithms*, CUP. §13.1.2 (simple car), §15.3. Free at lavalle.pl/planning/. | Bicycle model, nonholonomic constraint, configuration space |
| must | `[C]` Rajamani, R. *Vehicle Dynamics and Control*, Ch. 2. | Ackermann geometry, ICR, the rear-axle vs CoG distinction |
| should | `[?]` Ericson, C. (2005). *Real-Time Collision Detection*, Ch. 4–5. | SAT, OBB intersection, closest-point-on-segment |

#### Derive by hand (do not copy)

**(a) The two bicycle-model forms, and why mixing them is a bug.**

```
REAR AXLE reference (use this):
    x_dot = v cos(theta)
    y_dot = v sin(theta)
    theta_dot = (v / L) tan(delta)

CENTRE OF GRAVITY reference at distance l_r from the rear axle (do NOT use):
    beta = arctan( (l_r / L) tan(delta) )
    x_dot = v cos(theta + beta)
    y_dot = v sin(theta + beta)
    theta_dot = (v cos(beta) / L) tan(delta)
```

Using the first set with a CoG reference point is not a rounding error — quantify the
turning-radius discrepancy for this car and put the number in your notes.

**(b) Two-arc lateral shift (the parallel-parking S-curve).** Two opposite full-lock arcs of
radius R through angle φ:

```
lateral gain     d    = 2R (1 - cos phi)
longitudinal     ell  = 2R sin phi
eliminate phi:   ell  = sqrt(4Rd - d^2)          valid for d <= 2R
```

Evaluate at R = 3.9466 m, d = 2.35 m → ell = **5.62 m**. Note carefully what this *is*: a
**lateral-shift relation**, not a minimum-slot-length formula. It tells you the longitudinal run
needed to translate sideways by d; the slot-length question additionally involves body length,
overhangs, and the corner-clearance conditions against both neighbour cars.

> **5.62 m is an ideal-steering value and your vehicle cannot execute it.** The two-arc construction
> requires an *instantaneous* reversal from `+delta_max` to `−delta_max` at the join — precisely the
> non-cusp C→C join that §5.1 identifies as the worst case. Simulating the actual rate-limited
> S-curve (δ ramped at 0.6 rad/s, bisecting the hold time for a net 2.35 m shift with final heading 0):
>
> ```
> v = 0.5 m/s : longitudinal 6.179 m (+0.560 m, +10.0%),  path length 6.802 m
> v = 1.0 m/s : longitudinal 6.792 m (+1.173 m, +20.9%),  path length 7.388 m
> v = 1.5 m/s : the ramps alone overshoot 2.35 m of shift with zero hold — no solution of this form
> ```
>
> Use `sqrt(4Rd − d²)` **only as a lower bound**. Note that EXIT-0.7 as written validates the algebra
> against integration of the *ideal* arcs and therefore can never catch this; the executability check
> is a separate matter and belongs in Stage 1 (EXIT-1.8).

**(c) Minimum parallel-parking slot length — DERIVE IT YOURSELF.**

There is a known closed form in the literature. **This plan deliberately does not reproduce one.**
Two independent research agents converged on the same recommendation: published formulas are
inconsistent about whether "length" includes overhangs and whether the reference point is the rear
axle or the body centre, and with f = 0.9 and r = 1.1 that convention difference exceeds a metre.
A formula written from memory would be a fabrication.

Set the derivation up exactly like this:

```
Frame: neighbour cars occupy y in [y_k, y_k + w_p]; the ego's final parked pose has heading 0,
rear axle at (0,0), body occupying x in [-r, L+f] = [-1.1, 3.6] and y in [-w/2, +w/2].
Ego starts in the driving lane at heading 0 with lateral offset  Delta = w + c_lat.
Two equal full-lock arcs, heading 0 -> -phi -> 0, both at radius R = R_min:
    Delta = 2R(1 - cos phi)                     solve for phi
    longitudinal extent = 2R sin phi
Then impose, as separate inequalities:
    (i)   the rear body corner clears the REAR neighbour throughout the first arc
    (ii)  the KERB-SIDE front corner clears the FRONT neighbour          <- see the warning below
    (iii) the final parked body fits between them with clearance c_end
    (iv)  the LANE-SIDE front corner (R_front_outer = 6.0574 m) does not swing into the
          adjacent traffic lane                                          <- v1.0 omitted this
```

> **Fix the frame before you derive anything.** v1.0 left the frame under-specified — it never stated
> which side the kerb is on, hence never fixed the sign of φ or which lateral corner is "outer" — and
> then named `R_front_outer = 6.0574 m` in condition (ii). That is by construction the corner on the
> side *away* from the turn centre, i.e. the one swinging **out into the traffic lane** during a
> kerb-side reverse park. The corner that actually approaches the **front neighbour** during the
> counter-steer arc is on the kerb side, at `R_front_inner = 4.700 m`. State the kerb side (say +y),
> fix the sign of φ, label all four corners with their radii in that frame, and *then* write the
> inequalities. Condition (iv) — clearance into the traffic lane — is a real constraint that v1.0
> dropped entirely. This feeds EXIT-0.8, which gates the whole slot-length derivation.
>
> (The lateral offset `Δ = w + c_lat` is correct: ego half-width 0.925 + gap `c_lat` + neighbour
> half-width 0.925. With `c_lat = 0.5` it reproduces the d = 2.35 m used in (b).)

Then **validate the closed form numerically**: bisect on slot length using your own
single-cusp-restricted Hybrid A* and require agreement within one grid cell. Candidate references
to consult (all `[?]` — verify before citing):

- `[V]` **Two distinct papers, not one ambiguous one.** (1) Vorobieva, H., Glaser, S., Minoiu-Enache, N.
  & Mammar, S. (2012). "Geometric Path Planning for Automatic Parallel Parking in Tiny Spots."
  13th IFAC Symp. on Control in Transportation Systems, IFAC Proc. Vol. 45(24):302–307.
  (2) Vorobieva, H., Minoiu-Enache, N., Glaser, S. & Mammar, S. (2013), geometric
  continuous-curvature parallel parking. *Note the author order differs between them.*
- Blackburn, S. R. (2009). *The Geometry of Perfect Parking*, Royal Holloway. **Exists** (verified),
  but **not peer-reviewed**, and its exact algebraic form was **not** verifiable. `[?]`

**(c′) Reverse bay parking — the geometry, which *does* close in closed form** *(added v1.3)*

Everything above (c) is parallel parking. Reverse bay parking — **half the headline task** — had no
geometry at all in v1.0–v1.2: no dimensions, no feasibility boundary, no goal pose. This closes that.

Unlike (c), this one comes finished. The single-cut boundary for perpendicular back-in parking has an
exact closed form in the rear-axle frame, and **it is written entirely in three radii §4 already
tabulates for other reasons.** Derive it anyway; the derivation is four lines once the frame is right,
and the frame is the entire difficulty.

**Frame — fix this before writing a single inequality.**

```
bay centreline      x = 0                    bay mouth line   y = 0
bay interior        -D_bay <= y <= 0         target bay       |x| <= W_bay/2
aisle               0 <= y <= W_aisle        far side: HARD WALL at y = W_aisle
neighbours          everything with |x| >= W_gap/2 AND y <= 0 is solid
goal pose           rear axle (0, y_goal), theta = +pi/2      <- NOSE OUT of the bay
approach            ego drives UP the aisle at theta = 0, bay on its RIGHT
```

Reversing into a bay on the right swings the **rear right** and therefore rotates the heading
**counter-clockwise**, 0 → +π/2. Get that sign wrong and every corner label below flips.

> **`W_gap` is not `W_bay`, and the difference is 0.69 m of aisle.**
> ```
> walls / painted lines, no incursion permitted   : W_gap = W_bay        = 2.50 m
> both neighbours are cars centred in equal bays  : W_gap = 2*W_bay - w  = 3.15 m
> ```
> The second is the real parking lot; the first is the conservative one and does not depend on how
> your neighbours parked. **A27 declares `W_gap` a scene parameter with the wall model as default.**
> Deriving `W_gap` from `W_bay` inside the generator instead of declaring it is how this becomes a
> silent 0.69 m error in the difficulty label of every frozen bay scenario.

**The manoeuvre.** Single cut = one gear change: (1) forward along the aisle at heading 0;
(2) **one reverse arc** at radius `R`, turning heading 0 → π/2, turn centre
`C = (x_e + R, y_c)`; (3) reverse straight down `x = x_e` into the bay. Two free parameters:
`y_c` (how high the turn centre sits) and `x_e` (final lateral offset in the bay).

**Step 1 — move to the turn-centre frame.** Once `R` is fixed the swept set is a *fixed shape*; the
whole manoeuvre is a translation of it. Write **`u = −y_c`** — how far the turn centre sits *below*
the bay mouth line. The farthest body point from `C` is the front-outer corner, at `R_front_outer`,
and it passes through the top of its arc, so

```
max y over the whole manoeuvre = y_c + R_front_outer  =>   W_aisle = R_front_outer - u
```

**A narrow aisle means a large `u`.** That is the entire trade: pushing the turn centre down into the
bay row buys aisle width and spends bay width.

**Step 2 — the footprint the sweep leaves inside the bay row.** In the turn-centre frame, restricted
to heights `eta <= u`:

```
right boundary  X_max(u) = -sqrt( R_swept_inner^2 - max(u,0)^2 )     <- the INNER ENVELOPE circle
left  boundary  X_min(u) = -sqrt( R_rear_outer^2  - min(u,0)^2 )     <- the REAR-OUTER corner circle
footprint width F(u) = X_max(u) - X_min(u)
```

*Derivation of the right boundary (the only one that needs work).* The body's inner flank is a line
at distance `R_swept_inner` from `C`; at rotation `alpha` it meets the height `eta = u` at
`x = (u cos alpha - R_swept_inner)/sin alpha`. Differentiate: stationary at `cos alpha = u/R_swept_inner`,
where `x = -sqrt(R_swept_inner^2 - u^2)`. So the right edge of the footprint **is the inner envelope
circle** — which is why no new radius appears. For `u < 0` the stationary point leaves
`alpha ∈ [0, π/2]` and the maximum sits at the endpoint `alpha = π/2`, giving the constant
`-R_swept_inner`. The left boundary is the mirror argument on the rear-outer corner.

**Step 3 — the whole feasibility question is one scalar inequality.** With `c` the side clearance
demanded of each neighbour and `W' = W_gap - 2c`, a feasible `x_e` exists **iff `F(u) <= W'`**.
(The two `x_e` bounds cross exactly when the footprint no longer fits; `x_e` drops out.) `F` is
increasing, so invert it:

```
u*  = + sqrt( R_swept_inner^2 - (R_rear_outer - W')^2 )     if  W' >= R_rear_outer - R_swept_inner
    = - sqrt( R_rear_outer^2  - (R_swept_inner + W')^2 )     if  w <= W' <  R_rear_outer - R_swept_inner
      capped at   u* <= R_swept_inner - c

W_aisle_min = R_front_outer - u*

x_e* = R_rear_outer - R - W_gap/2 + c        (upper branch)
     = W_gap/2 - c - w/2                     (lower branch)
```

**Four independent checks that this is right — all verified numerically against an explicit
40 001-sample swept body (§0.1 status: `[D]` — derived and machine-checked in this document):**

| Check | Consequence | Independent meaning |
|---|---|---|
| `W' = w` | `u* = −r` exactly, `W_aisle = R_front_outer + r = 7.1574` | the zero-clearance bay forces "align fully in the aisle, then reverse straight in", whose sweep never crosses the mouth line at all |
| `W' = R_rear_outer − R_swept_inner = 1.9726` | `u* = 0` | the two branches meet continuously |
| `W' = R_rear_outer = 4.9942` | `u* = R_swept_inner`, `W_aisle = R_front_outer − R_swept_inner = 3.0358` | **that is the swept-corridor width §4 already tabulates**, arrived at from a completely different direction |
| the cap `u <= R_swept_inner − c` | — | it is not an extra assumption: `y_c + R − w/2 = c` says the car's inner flank, *driving up the aisle before the arc starts*, sits exactly `c` above the mouth line. Verified to 1e-16 |

**The numbers, at `R = R_min` and the wall model `W_gap = W_bay`:**

```
W_bay | W_aisle_min at side clearance c =            | side clearance
      |  c=0      c=0.10    c=0.20    c=0.30         | bought by a 6.00 m aisle
------+---------------------------------------------+------------------------
 2.30 | 4.690     5.189     6.906     infeasible     | 0.163 m
 2.40 | 4.508     4.908     5.652     infeasible     | 0.213 m
 2.50 | 4.352     4.690     5.189     6.906          | 0.263 m   <- reference scene
 2.60 | 4.214     4.508     4.908     5.652          | 0.313 m
 2.80 | 3.980     4.214     4.508     4.908          | 0.413 m
 3.00 | 3.787     3.980     4.214     4.508          | 0.513 m
```

> **No aisle width can buy more than `(W_bay − w)/2` of swing clearance** — 0.325 m at the reference
> bay — because at `u = −r` the footprint has already contracted to the car's own width and the
> *parked* car is what limits the rest. Saturation is reached at `W_aisle = R_front_outer + r = 7.1574 m`.
> Aisle beyond that is free space, not margin. Useful when someone proposes "just widen the aisle".

**A lower bound that survives any number of cuts.** The single-cut formula is an *upper* bound on the
true boundary. For a bound in the other direction, use **static containment**: heading must pass
through every `psi ∈ [0, π/2]` by continuity, so at each `psi` the rigid body must fit in
(aisle ∪ bay). Minimise the required aisle over placements, maximise over `psi`. It ignores
nonholonomy entirely, so it is *necessary* for any manoeuvre whatsoever:

```
W_bay = 2.50, D_bay >= l + c_end :  W_aisle >= 3.5100 m, binding at psi = 53.0 deg
                                    (independent of D_bay -- the depth never binds)
   2.30 -> 3.7969 (57.2 deg)   2.40 -> 3.6478 (55.1 deg)   2.60 -> 3.3816 (51.2 deg)
   2.80 -> 3.1479 (47.7 deg)   3.00 -> 2.9399 (44.5 deg)
```

So for the reference bay the true multi-cut boundary lies in **[3.5100, 4.3519]** — a factor of 1.24.
Anything the Stage-1 planner returns outside that bracket is a **bug in the planner or in the
footprint, and EXIT-0.10 is the first place to look.**

**`R = R_min` is optimal and there is nothing to search over.** `W_aisle_min` is strictly increasing
in `R` (4.352 at `R_min`, 4.622 at 4.5, 5.481 at 6.0, 9.812 at 12.0, verified over `R ∈ [R_min, 20]`),
because `R_front_outer` grows roughly linearly in `R` while the usable `u*` grows sublinearly. Full
lock is the answer. Do not spend a parameter search on it.

**What this formula is *not*.** It is exact for the **constant-radius single-arc** family and is
therefore an **upper bound** for the general single-cut class (a varying-curvature reverse might do
better; this document does not claim it cannot). Per **A10**, the operational feasibility oracle
remains the Stage-1 planner, exactly as for parallel parking. The closed form's job is to be the
*independent analytic check* on that planner — EXIT-0.14.

**The goal pose, and the heading trap.** With `D_bay = 5.30 = l + 0.60`, centring the body gives

```
goal = (0, -3.90, +pi/2)     body spans y in [-5.00, -0.30], x in [-0.925, +0.925]
                             0.30 m clear at the bay end, 0.30 m inside the mouth,
                             0.325 m clear to each bay line
```

> **§5.0(g) offers a min-over-two-corner-matchings for the heading term. For this family the answer
> is NO.** `theta = -pi/2` is nose-**in**: geometrically identical footprint, and a task the agent was
> not asked to do. Enabling two-corner matching silently converts "reverse bay parking" into "bay
> parking", makes the 180° plateau of §7.3 into a ±90° problem, and invalidates the comparison with
> a reverse-only Reeds–Shepp expert. **EXIT-0.15 asserts the nose-in pose is rejected.**

> **A refinement to the 180° claim made in §0.3, §5.0(g) and §7.3.** The *canonical* bay start —
> aisle-parallel, heading 0, goal `+pi/2` — has heading error **exactly π/2**, where
> `d(1−cos)/dΔθ = 1.0`, not 0. Heading errors near π arise from the **Stage-3 randomised start
> distribution**, not from the canonical manoeuvre. The plateau is still a real defect and the fix
> still stands; it just does not bite every bay episode, which matters when you are reading a learning
> curve and deciding what to blame.

**Difficulty axis for this family.** `W_bay` has only ~0.7 m of usable range (below ~2.3 m barely
parkable, above ~3.0 m unrealistic) while `W_aisle` has ~2.8 m. So the difficulty scalar is the
**aisle slack ratio**

```
eta_bay = W_aisle / W_aisle_min(W_gap; R_min, c = 0)
```

`eta_bay = 1` is the zero-clearance geometric boundary — **never gate on it**; no real controller
achieves a manoeuvre with 0.000 m of clearance. Reference points at `W_bay = 2.50`:

```
eta = 1.00  W_aisle 4.352   geometric boundary, clearance 0.000 m   -- generator floor only
eta = 1.15  W_aisle 5.005   clearance 0.168 m                       -- Stage 3 gate (EXIT-3.1)
eta = 1.38  W_aisle 6.000   clearance 0.263 m                       -- the reference scene
eta = 1.55  W_aisle 6.745   clearance 0.288 m                       -- Stage 2 easy rung (EXIT-2.27)
eta = 1.64  W_aisle 7.157   clearance 0.325 m = saturated           -- zero incursion
```

**(d) Exact OBB–OBB signed distance.**

```
CASE 1 — SAT reports overlap:
    signed_distance = -penetration_depth
                    = -min over candidate axes of (projection overlap)
    For two rectangles only 4 candidate axes are needed (2 edge normals each);
    minimum translational distance in 2D is always along a face normal.

CASE 2 — SAT reports separation:
    d(A,B) = min over all (vertex v of A, edge e of B) of point_segment_dist(v, e)
             and all (vertex v of B, edge e of A)
           = 32 point-segment evaluations for two rectangles. Trivially cheap, fully vectorisable.

    point_segment_dist(P, Q0, Q1):
        D = Q1 - Q0
        t = clamp( dot(P - Q0, D) / dot(D, D), 0, 1 )
        return norm( P - (Q0 + t*D) )
```

**CRITICAL:** the max-over-face-normal-axes SAT gap is only a **lower bound** on the true
separation. It is exact when the closest feature pair is vertex–edge, and **strictly
under-estimates** in the vertex–vertex case — which is exactly the configuration when the ego noses
diagonally into a bay corner, i.e. the case you care most about. Never report the SAT gap as a
clearance metric.

Also note the containment edge case: if one rectangle is entirely inside another, edge-pair distance
is non-zero but they overlap. Run SAT first; select by its boolean.

**(e) Multi-circle body approximation and its conservatism.**

For a 4.7 × 1.85 m body split into 3 equal circles along the centreline, the covering radius is

```
rho = 0.5 * sqrt( (l/3)^2 + w^2 ) = 0.5 * sqrt( 1.5667^2 + 1.85^2 ) = 1.2121 m
```

against a true half-width of 0.9250 m — an over-estimate of **0.2871 m** in lateral extent. That is
large enough to declare a genuinely feasible tight slot infeasible.

**Division of labour, and it is not negotiable:**
- 3-circle model → the **smooth safety-margin term inside the reward potential** (fast, differentiable)
- exact OBB → **termination test and every reported clearance metric**

**(f) Continuous collision detection resolution.**

For a rigid body whose farthest point from the reference is `d_max`, between two samples separated
by arc length Δs and heading change Δθ:

```
max body-point displacement <= Ds + d_max |Dtheta| <= Ds (1 + d_max kappa_max)
    1 + d_max kappa_max = 1 + 3.7169 * 0.25338 = 1.9419

To guarantee no body point moves more than epsilon between checks:
    Ds <= epsilon / 1.9419
    epsilon = 0.05 m  ->  Ds <= 0.0258 m
    epsilon = 0.02 m  ->  Ds <= 0.0103 m

Simulator cross-check: 5 substeps of 0.02 s at v_max gives Ds = 0.030 m per substep,
hence max body-point motion 0.0583 m per substep.
```

Therefore: the generator must not place obstacles thinner than ~0.09 m (3× the per-substep
translation), or the substep count must rise.

**(g) Pose-error metrics.**

Use `(1 − cos Δθ)` rather than `Δθ²`: it handles the 2π periodicity naturally and its small-angle
expansion is `Δθ²/2`, so weights transfer by a factor of 2. If either heading in the slot is
acceptable, take the min over the two corner matchings — but decide this explicitly, because it
changes the task.

> **The periodicity is not free — it buys a plateau at 180°.** `d/dΔθ (1 − cos Δθ) = sin Δθ`, which
> **vanishes at Δθ = π**: gradient 1.0 at 90°, 0.50 at 150°, and 1.2e-16 at 180°. So the heading term
> of Φ has an unstable equilibrium at exactly 180° of heading error — and **reverse bay parking
> routinely starts at 90–180° from the goal heading.** This is structurally the same pathology as
> §7.3's Defect 2, relocated to the far field. It also saturates: `1 − cos ≤ 2`, so the heading
> contribution to `|Φ(s₀)|` is bounded. **§7.3 Defect 3 replaces this term with `1 − cos(Δθ/2)`;
> use that form.** Under it the bound is `w_th·1 = 10.50` (v1.1 printed `2·w_th = 5.25` for the old
> form). If you adopt the two-corner matching, **check whether it moves the plateau to Δθ = π/2**,
> which would be worse.

#### Build

```
worldstate.py   WorldState dataclass (truth). ego (x,y,theta,v,delta); objects (N,6) =
                (x,y,theta,l,w,type); bounds; settle_counter (int, 0..K_settle).
                *** settle_counter IS PART OF THE STATE. See A22. Omitting it makes even O0
                    a POMDP, which silently falsifies the premise of the whole O0-O4 ladder. ***
dynamics.py     Rear-axle bicycle, explicit substep integration, action clamping.
geometry.py     obb_corners, sat_overlap, obb_signed_distance (32 point-segment),
                body_circles, ccd_sweep.
render.py       matplotlib patches + trajectory replay. WRITE THIS EARLY — you will find
                80% of your bugs by watching the animation.
tests/          see exit criteria
```

#### EXIT CRITERIA — Stage 0

| ID | Criterion | Threshold |
|---|---|---|
| **EXIT-0.1** | SAT boolean agrees with Shapely on randomised rectangle pairs | 0 disagreements in 10⁵ pairs |
| **EXIT-0.2** | Constant-δ trajectory has the right radius, and closes to within one integration chord | **(a)** least-squares circle fit to the sampled trajectory: `\|R_fit − L/tan δ\| < 1e-3 m`, swept over δ ∈ {0.1,…,0.6} — *this is the half that tests the kinematics*. **(b)** closure error `< 1.5·v·dt_sub` (= 0.045 m at v_max), **not** 1e-3 m. *v1.0 demanded closure < 1e-3 m, which is unachievable: `2π/Δθ` is non-integral for every listed δ, and explicit-Euler closure residuals run to 0.015 m — the criterion would fail on correct code and be quietly relaxed, taking the useful radius assertion with it.* |
| **EXIT-0.3** | `obb_signed_distance` matches an **exact independent** reference | **Separated branch:** compare against Shapely `.distance()` or an independent GJK — max abs error ≤ 1e-6 m over 10⁴ random pairs. **Overlapping branch:** compare `−MTV` against an independent penetration-depth reference (1-D search along each of the 4 axes, separate code path) — ≤ 1e-6 m. *v1.0 specified boundary sampling at 10⁴ points/boundary, which (i) has spacing 1.31e-3 m and overshoots the true minimum by ~h²/(8d) — 4.3e-6 m at d = 0.05 m, 2.2e-5 m at d = 0.01 m, i.e. it fails on exactly the tight configurations the test exists for; and (ii) returns ≈0 for overlapping pairs, so it compares a different quantity from `−MTV` entirely.* |
| **EXIT-0.4** | Vertex–vertex regression: the SAT gap must **under-estimate** | Two **axis-aligned** boxes offset diagonally, e.g. A = [−1,0]², B = [1,2]²: assert exact = √2 = 1.41421 and SAT face-normal gap = 1.0, i.e. **exact − gap = 0.41421 > 0**. Add a second case with a **20°** relative rotation. *v1.0 said "corner-to-corner at 45°", which is a false-negative generator: at 45° the rotated box's face normal lies along the corner-to-corner direction, so the closest pair is vertex–**edge**, SAT gap = exact distance, and the assertion fails on correct code.* |
| **EXIT-0.5** | Tunnelling, exercising the **rotational** term | Primary case: **full-lock turn** (δ = δ_max, v = v_max) with the front outer corner sweeping a thin wall tangentially — this is the configuration in which a corner moves 0.0505 m per sample. Assert 100% detection at Δs = 0.026 m for thickness **> 0.0505 m** (state 0.055 m), or shrink Δs to 0.025 m. Secondary, easier case: perpendicular approach. *v1.0 tested only the perpendicular approach, which is pure translation (Δθ = 0) and never exercises the `d_max·\|Δθ\|` term the bound exists for — it passes trivially and certifies nothing. Its stated 0.05 m threshold also sits just inside the un-guaranteed region, since 0.026 × 1.9419 = 0.0505 m.* |
| **EXIT-0.6** | 3-circle covering radius computed and asserted against the analytic value | 1.2121 m ± 1e-4; **and** an assertion that the circle model is not importable by the termination path |
| **EXIT-0.7** | Two-arc feasibility region reproduced numerically | analytic `sqrt(4Rd−d²)` matches brute-force integration to 1e-6 over the (d, R) grid |
| **EXIT-0.8** | Hand-derived minimum-slot-length curve validated against numerical bisection | agreement within one grid cell of the bisection resolution |
| **EXIT-0.9** | Determinism | same initial state + same action sequence → bitwise-identical `WorldState` trajectory, across processes |
| **EXIT-0.10** | **Body footprint placement relative to the rear axle** *(added v1.2 — the largest hole in the whole audit)* | `obb_corners(WorldState(x=0,y=0,theta=0))` equals `{(−1.100, ±0.925), (3.600, ±0.925)}` to **1e-12**. Assert `min_x == −r` and `max_x == L+f` as **separate** assertions — a symmetric length check would not catch an f/r swap. Assert `d_max == hypot(L+f, w/2) == 3.71694 ± 1e-4`; assert `l == L+f+r` exactly on the config object; repeat at θ = 0.7 rad against a hand-computed rotation. *Nothing in v1.1 asserted where the body sits. If `obb_corners` centres it (x ∈ [−2.35, 2.35]) or swaps f and r, **every Stage-0, Stage-1 and Stage-2 criterion still passes** — because the planner and the environment share the footprint, so EXIT-2.2's "checkers agree" confirms they agree while both are wrong, and EXIT-1.9's oracle-soundness check is consistent with the same error. Collision geometry would be displaced by up to 1.25 m longitudinally and the entire success surface would be internally consistent and externally wrong. `f ≠ r` is the only asymmetry distinguishing the correct placement from the plausible wrong ones, and 0.2 m is far above any tolerance.* |
| **EXIT-0.11** | **Actuator and state clamps are actually enforced** *(added v1.2)* | 10⁶ random 400-step action sequences (5 substeps each), including sustained saturation at each corner of the action box. At **every substep** assert `\|δ\| ≤ δ_max+1e-12`, `\|v\| ≤ v_max+1e-12`, `\|δ_(k+1)−δ_k\| ≤ δ̇_max·dt_sub+1e-12 = 0.012+1e-12`, `\|v_(k+1)−v_k\| ≤ a_max·dt_sub+1e-12 = 0.030+1e-12`. **Positive control:** with the clamp disabled at least one sequence must violate. Threshold: zero violations. *v1.1 tested only the linear action-scaling round-trip (EXIT-2.14), never that integrated `δ` stays inside `δ_max`. An environment that lets `δ` drift gives the RL car a turning radius smaller than `R_min = 3.9466 m` — a capability Reeds–Shepp, Hybrid A\* and the tracked expert all lack. Result: inflated success, deflated optimality ratio, and an "advantage" over the classical baselines that is a simulator bug. The only criterion that would see the symptom is EXIT-4.4's `P(ρ<1) ≤ 0.05`, whose own text pre-assigns the diagnosis ("the planner resolution is too coarse") and routes you away from the real cause.* |
| **EXIT-0.12** | **The heading potential has no gradient plateau** *(added v1.2)* | assert `\|dΦ_heading/dΔθ\| > 0.1` for **all** `Δθ ∈ (0, π]` under whichever heading form is adopted. *Catches §7.3 Defect 3 and any future "improvement" that reintroduces a plateau — including the wrong fix v1.1 itself proposed.* |
| **EXIT-0.13** | **The reverse-bay closed form matches an explicit swept body** *(added v1.3)* | Build the sweep by sampling the reverse arc at **≥ 2×10⁴** headings, take the exact OBB at each, clip to `y ≤ 0`, and over the grid `W_gap ∈ {w, 1.95, 2.10, 2.30, 2.50, 2.80, 3.15, 3.50, 4.00}` × `c ∈ {0, 0.10, 0.25}` assert **(i)** `max_y(sweep) = R_front_outer − u*` to **1e-8 m**; **(ii)** at `x_e*` the clipped x-extent equals `±(W_gap/2 − c)` to **1e-5 m** (both sides, so a sign error in `x_e*` cannot pass); **(iii)** the four identities of §5.0(c′) — `W′=w ⇒ u*=−r`, `W′=R_rear_outer−R_swept_inner ⇒ u*=0`, `W′=R_rear_outer ⇒ u*=R_swept_inner`, and `u=R_swept_inner−c ⇒` approach flank at `+c`, each to **1e-9**. **Positive control (mandatory):** `u* + 0.02` must produce a measured incursion `> W_gap/2 − c`. *Without the positive control this test passes on any monotone function of `W_gap`.* |
| **EXIT-0.14** | **The multi-cut bracket holds, and the planner lands inside it** *(added v1.3)* | **(a)** Compute the static containment bound by maximising over `psi ∈ [0,π/2]`; assert `3.5100 ± 1e-3 m` at `psi = 53.0° ± 0.5°` for `W_bay = 2.50`, and assert it is **invariant to `D_bay`** for `D_bay ≥ l + c_end` (a depth-dependent answer means the depth clip is mis-signed). **(b)** Assert `containment_LB < W_aisle_min` for **every** row of the §5.0(c′) design table. **(c)** *At Stage 1*, bisect `W_aisle` with Hybrid A\* at `W_bay = 2.50` and assert the result lies in **[3.5100, 4.3519]**. Threshold: all three. *(c) is the only cross-check in the document that ties the bay geometry to the planner. A result below the containment bound is geometrically impossible and means the footprint is wrong — go to EXIT-0.10 before touching the planner.* |
| **EXIT-0.15** | **Bay goal pose and the nose-in trap** *(added v1.3)* | Assert `obb_corners(0, −3.90, +π/2)` spans `y ∈ [−5.000, −0.300]` and `x ∈ [−0.925, +0.925]` to 1e-12, giving 0.300 m at each end and 0.325 m to each bay line. Assert the success test **rejects** `(0, −3.90, −π/2)` — the nose-in pose — at `eps_final`. **Positive control:** enabling the §5.0(g) two-corner matching must make the nose-in pose **pass**, proving the test discriminates. *Without this, "reverse bay parking" silently becomes "bay parking", the Reeds–Shepp reverse-only expert stops being a valid baseline, and the §7.3 heading analysis is about the wrong angle.* |

---

### 5.1 Stage 1 — Classical planning baselines *(still no RL)*

**This stage is infrastructure, not an afterthought.** Its outputs are consumed by every later
stage: the feasibility oracle filters curriculum sampling, the path length is the optimality
denominator, the reverse-curriculum generator comes from it, and it is the demonstration source.
Building it after the RL is the single most common ordering mistake in projects like this.

#### Theory and mathematics to read

| Priority | Source | Covers |
|---|---|---|
| must | `[V]` Reeds, J. A. & Shepp, L. A. (1990). "Optimal paths for a car that goes both forwards and backwards." *Pacific J. Math.* 145(2), 367–393. | The sufficient family; §8 + Table 1 is the implementation spec |
| must | `[V]` LaValle (2006), §15.3.1–15.3.2. | The 48 words in modern notation — far easier to implement from than RS's scanned table |
| must | `[C]` Dubins, L. E. (1957). *Amer. J. Math.* 79(3), 497–516. | Forward-only case; the sanity anchor `d_Dubins ≥ d_RS` |
| should | `[V]` Sussmann, H. J. & Tang, G. (1991). Report SYCON-91-10, Rutgers. | The 48→46 reduction; the Dubins CCC precondition (middle arc **> π**) |
| must | `[V]` Fraichard, T. & Scheuer, A. (2004). "From Reeds and Shepp's to Continuous-Curvature Paths." *IEEE Trans. Robotics* **20(6)**, 1025–1035. DOI 10.1109/TRO.2004.833789. | Why RS paths are untrackable; the honest optimality denominator |
| must | `[V]` Dolgov, D., Thrun, S., Montemerlo, M. & Diebel, J. (2010). *IJRR* 29(5), 485–501. | Hybrid A*, in full |
| should | `[V]` Banzhaf, H. et al. (2017). "Hybrid Curvature Steer." *IEEE ITSC 2017*. | HC (not CC) is the right steering function here — see below |
| must | `[?]` Coulter, R. C. (1992). CMU-RI-TR-92-01. | Pure pursuit, rear-axle referenced |
| should | `[?]` Souères, P. & Laumond, J.-P. (1996). *IEEE TAC* 41(5), 672–688. | Synthesis: *which* word for which relative pose |

#### Get these numbers right (they are cheap, visible errors)

> **48 = WORDS** (path types) in the sufficient set, RS Table 1. **68 = FORMULAS** (some words admit
> two solutions of the minimising equations; RS observed empirically that one per word always
> suffices but explicitly did **not** prove it). **46 = Sussmann & Tang's reduction** (L⁻L⁺L⁻ and
> R⁻R⁺R⁻ are unnecessary). **9 = compact base families.** Max 5 pieces, max 2 cusps.
> Dubins: **6 words**, max 3 pieces, and for LRL/RLR the middle arc must be **strictly > π**.

Write it as: *"48 words (Reeds & Shepp 1990, Table 1), of which 46 suffice (Sussmann & Tang 1991)."*

#### The curvature-discontinuity problem, quantified

This is more severe than intuition suggests. An RS path has piecewise-constant curvature, so
`δ(σ) = atan(L κ(σ))` jumps instantaneously between {−0.6, 0, +0.6} rad. At `δ̇_max = 0.6 rad/s`:

```
Steering slew time and consumed arc length:
    0 -> full lock         t = 1.0 s   ell = 1.5 m at v_max,  0.5 m at v = 0.5
    full lock -> full lock t = 2.0 s   ell = 3.0 m at v_max,  1.0 m at v = 0.5
    (a quarter circle at R_min is only 6.199 m long — a lock-to-lock slew consumes 48% of it)

Clothoid ramp deflection, EXACT for a linear-in-time steering ramp at constant speed:
    Dtheta_ramp = -( v / (L * delta_dot_max) ) * ln( cos(delta_max) )
    v=0.3 -> 2.04 deg    v=0.5 -> 3.39 deg    v=1.0 -> 6.79 deg    v=1.5 -> 10.18 deg

Open-loop pose error, rate-limited vehicle vs ideal RS (RK4 @ 2e-4 s):
    (A) NON-CUSP C->C join (delta: +0.6 -> -0.6), the worst case:
            v=0.5 : 0.684 m, 14.52 deg      v=1.5 : 1.540 m, 43.55 deg
    (B) NON-CUSP C->S join (delta: +0.6 -> 0):
            v=0.5 : 0.168 m,  3.39 deg      v=1.5 : 0.446 m, 10.18 deg
    (C) CUSP join with a trapezoidal speed profile at a_max, full lock-to-lock:
            0.245 m, -8.02 deg
```

**The key design insight, and it falls out of the already-chosen action space:** because the action
is `(a_long, δ̇)` with bounded `a_long`, the car **must** decelerate through zero at every gear
reversal, and that dead time is free steering-slew time. So a curvature discontinuity **at a cusp is
nearly free** (0.245 m), while the same discontinuity at a **non-cusp C→C join costs 6.3× more**
(1.540 m at v_max — one third of the car's own length). This is why HC (Hybrid Curvature) steering
is the right choice over full CC: pay for continuity only where it is not already free.

Note also (Fraichard & Scheuer): for the curvature-rate-constrained car, whenever the true shortest
path contains a line segment, the optimum involves **infinite chattering** — an infinite number of
clothoid arcs accumulating at the segment endpoints. There is therefore **no clean closed-form
optimum** for the vehicle you actually simulate. This matters for how you word optimality claims.

#### The four consumers

**(a) Feasibility oracle** `is_feasible(q_start, slot) -> bool`
1. Compute all RS candidate words at ρ = R_min; take in increasing length order.
2. Discretise each at Δs ≤ 0.026 m (from EXIT-0.5's bound).
3. At each sample place the oriented rectangle and run **the same exact SAT test the environment
   uses, with the same footprint**. A mismatch here presents as an unexplained success-rate ceiling.
4. Accept on the first clean path.

**Soundness caveat:** collision-checked RS is **sound but incomplete**. RS-feasible ⇒ feasible; but
RS-**in**feasible does **not** imply infeasible, because RS restricts to ≤2 cusps and minimum-radius
arcs, while tight parking often needs more shunts. Use RS as a fast **accept**, Hybrid A* as the
**reject** authority.

**(b) Optimality denominator.** Measure `ell_RL` as `∫|v| dt` over **substeps** (arc length, not
displacement — a 3-point turn has near-zero displacement). Report three denominators:

| Denominator | Meaning | Caveat |
|---|---|---|
| `ell_RS` (obstacle-free) | lower bound on any bounded-curvature path | only meaningful when the RS path is itself collision-free; otherwise ratio < 1 is possible and the metric is meaningless |
| `ell_HA*` (collision-checked, smoothed) | feasible and obstacle-aware | neither optimal nor complete, so not a bound |
| `ell_OBCA` (NLP warm-started from HA*) | closest to a true optimum | uses the **same exact convex-body collision model** as your SAT check |

**The achievable floor is strictly greater than 1 and is not a property of the policy**: since
`|δ̇| ≤ 0.6 rad/s`, no controller can execute an RS path. Report `ratio_floor = ell_HC / ell_RS > 1`.
Without it a reported ratio of 1.15 is uninterpretable.

**(c) Reverse-curriculum generator.** See §5.3.

**(d) Demonstrations.** See §5.3, and **A15**.

#### Build order (the dependency that is easy to miss)

1. RS closed form (9 base families, symmetry-expanded) — **validate against the metric axioms before
   anything consumes it**
2. Collision-checked path validator at Δs ≤ 0.026 m — shared by everything downstream
3. Feasibility oracle
4. `h_nhwo` lookup table (this is just RS distance — free once (1) works)
5. `h_hwo` 2D Dijkstra on the obstacle grid
6. Hybrid A* (bucketed continuous state; `h = max(h_nhwo, h_hwo)`; analytic RS expansion near the
   goal, **collision-checked**; gradient post-smoothing)
7. **Speed profiler** — *not part of any of these planners.* Dolgov et al. explicitly do not model
   speed. RS and Dubins are pure path planners with no notion of time. Your action space is
   `(a_long, δ̇)`, so every baseline needs its own speed profile.
8. Rear-axle **pure pursuit** tracker

> **Use pure pursuit, not Stanley.** Stanley is a **front-axle** law derived for forward motion; in
> reverse the feedback sign makes the cross-track loop **unstable**, and the failure is a smooth
> divergence that looks like a tuning problem. Pure pursuit is rear-axle referenced — already your
> kinematic reference — and extends to reverse by looking backwards. Size the lookahead against the
> **rate** limit, not the speed: `ell_min` must exceed the lock-up length `v·Δδ/δ̇_max`
> (≥ 0.75 m at v = 0.5), or you get a steering limit cycle riding against the `δ̇` clamp.

#### EXIT CRITERIA — Stage 1

| ID | Criterion | Threshold |
|---|---|---|
| **EXIT-1.1** | RS satisfies the SE(2) metric axioms | 0 violations in 10⁵ pairs / 2×10⁴ triples, tol 1e-9: symmetry, Euclidean lower bound, SE(2) invariance, scaling, identity, triangle inequality |
| **EXIT-1.2** | `d_RS ≤ d_Dubins`; Dubins asymmetry is correct | 0 ordering violations in 10⁵ pairs; reversal identity `d_D(q1,q2)=d_D(σq2,σq1)` to 1e-9; ≥1 pair with `\|d_D(q1,q2)−d_D(q2,q1)\| > 0.1 m`; every CCC solution has middle arc **> π** |
| **EXIT-1.3** | RS decomposition actually reaches the goal | forward-integrating the returned control sequence lands within 1e-4 m / 1e-5 rad in 10⁴ cases; ≤5 pieces; ≤2 cusps; word ∈ the 48-word table |
| **EXIT-1.4** | RS agrees with an independent numerical OCP (shares no code) | rel. length error ≤ 1e-3 on ≥95% of 200 stratified pairs; `L_OCP ≥ d_RS − 1e-6` on **100%** (RS is provably optimal — the solver must never beat it) |
| **EXIT-1.5** | Path collision checking is resolution-adequate | Δs = 0.026 m flags 100% of what Δs = 0.002 m flags, for thickness ≥ 0.05 m |
| **EXIT-1.6** | Hybrid A* heuristics are genuinely admissible | 0 violations of `h ≤ g*` over 10⁶ sampled states; **and** the deliberately inflated-radius control (1.1×, 1.2× R_min) **must** produce violations, or the test is not sensitive |
| **EXIT-1.7** | Hybrid A* quality on a 400-scenario set | success ≥ 99% on oracle-feasible scenarios, **reported separately for bay and parallel**; obstacle-free length ≤ 1.05× RS after smoothing; cluttered ≤ 1.5×; p99 wall-clock recorded |
| **EXIT-1.8** | Tracking controller error bound | on an HC/CC reference at v = 0.5 m/s: peak lateral ≤ 0.05 m, RMS ≤ 0.02 m, terminal ≤ 0.05 m and ≤ 2°. On an **RS** reference, peak error near non-cusp joins must be **consistent with the open-loop prediction** — if it is far below, the simulator is not enforcing `δ̇_max` |
| **EXIT-1.9** | Feasibility oracle is sound wrt the environment | **100%** of oracle-approved initial states produce no instant termination on reset (hard gate); ≥90% of witness paths execute collision-free under closed-loop tracking |
| **EXIT-1.10** | Baseline determinism | RS bitwise identical across 20 runs; Hybrid A* identical given a fixed tie-break; tie-break sensitivity study shows path-length variation < 5% |
| **EXIT-1.11** | `ratio_floor = ell_HC/ell_RS` computed and stored per scenario | present for 100% of the frozen set; > 1.0 for 100% |
| **EXIT-1.12** | Observation re-rendering is stage-invariant | for 500 recorded episodes, observations re-rendered under O0/O1/O2 have identical shape and dtype and identical `(valid, visible_now)` semantics; O0 recoverable from `WorldState` alone |
| **EXIT-1.13** | **Hand-drawn paths are trackable at all** *(added v1.4 — the cheap kill-switch on the whole sketch-input idea)* | Collect **≥ 50** freehand paths over the reference scenes. Resample to arc length, fit a `C²` spline, and report: **(a)** the fraction with `max κ ≤ κ_max = 0.25338 1/m` **before** any repair, **(b)** the same fraction after curvature-limited refitting, **(c)** the fraction whose refitted path is still collision-free, **(d)** closed-loop tracking error under the §5.1 rear-axle pure-pursuit controller. **Gate: (d) must meet EXIT-1.8's bounds (peak lateral ≤ 0.05 m, terminal ≤ 0.05 m and ≤ 2°) on ≥ 80% of the corpus.** Below that, **sketch input is dead** — say so and stop, do not add a repair pipeline. *A15 forbids raw `(state, action)` demonstrations because RS paths have unbounded implied `δ̇`; a freehand path is strictly worse, since nothing constrains its curvature at all. This criterion costs 1–2 days and is the whole reason to run it before building anything on §5.5.1.* |
| **EXIT-1.14** | **Teleoperation logs are replayable, un-privileged, and not lag-poisoned** *(added v1.4)* | **(a) Bitwise replay:** feeding a logged episode's `(seed, action sequence)` back through the environment reproduces the recorded `WorldState` trajectory **bitwise**, for 100% of episodes — this is EXIT-0.9 applied to the game and it fails immediately if the logger records at render rate rather than `dt_policy`, or records the *requested* action rather than the **clamped** one. **(b) Lag:** cross-correlate each logged action channel against the state signal it responds to; report the argmax lag; **require ≤ 1 policy step** at the chosen time dilation (start at 1 sim-second ≥ 4 wall-clock seconds) and **report the dilation factor with the corpus**. **(c) Provenance:** every episode carries the observation rung it was collected under; assert no O0-collected episode is consumed by an O2+ arm. *(a) catches a silent corruption of the entire corpus; (b) is **A23** arriving through the human rather than the actuator — clone a lagged demonstrator and you clone the lag; (c) is §6.5's privileged-information caveat, which a full-screen game view violates by default.* |

---

### 5.2 Stage 2 — Minimal viable RL (full-state MDP, O0)

**Goal.** A working SAC agent on the fully-observable task, with the evaluation protocol frozen
**before** any tuning happens.

#### Theory and mathematics to read

**Foundations**

| Priority | Source | Covers |
|---|---|---|
| must | `[C]` Sutton & Barto (2018), 2nd ed. **Ch. 3** (esp. §3.3–3.4), **Ch. 4** (§4.1–4.4), **Ch. 13** (§13.1–13.5, 13.7), **Ch. 11** (§11.2–11.3) | MDP formalism; the absorbing-state trick that makes "terminal ⇒ V=0" precise; DP as the template soft policy iteration copies; policy gradient theorem; the deadly triad |
| should | `[C]` Szepesvári, Cs. (2010). *Algorithms for RL*, Ch. 1–2 | Shortest rigorous γ-contraction / Banach fixed-point treatment; the bound `‖V‖∞ ≤ R_max/(1−γ)` used as a live divergence detector |
| should | `[?]` Puterman (1994/2005), Ch. 6 | The measure-theoretically careful version. Do **not** cite a theorem number without opening the book |
| should | `[?]` Singh & Yee (1994). *Machine Learning* 16(3), 227–233 | `‖Q−Q*‖∞ ≤ ε ⇒ greedy loss ≤ 2γε/(1−γ)`. At γ=0.995 that amplification is **200×** — the theoretical reason not to raise γ beyond what your critic supports |
| should | `[?]` Jiang, Kulesza, Singh & Lewis (2015), AAMAS | Why to choose γ from the task's own timescale rather than "as high as possible" |

**SAC and friends**

| Priority | Source | Covers |
|---|---|---|
| must | `[C]` Haarnoja, Zhou, Abbeel & Levine (2018). "Soft Actor-Critic." ICML 2018, PMLR 80, 1861–1870. §3, §4, App. A/B, **App. C "Enforcing Action Bounds"** | The primary source. App. C has the log-det-Jacobian correction — the single most common SAC bug. (Appendix exists; its exact equation number was **not** verified) |
| must | `[C]` Haarnoja et al. (2018/2019). "Soft Actor-Critic Algorithms and Applications." arXiv:1812.05905 | This, not the ICML paper, is what SB3 implements. Automatic temperature + target entropy |
| should | `[C]` Haarnoja, Tang, Abbeel & Levine (2017). "RL with Deep Energy-Based Policies." ICML 2017 | Where the soft-max-over-actions and Boltzmann policy form actually come from |
| must | `[C]` Fujimoto, van Hoof & Meger (2018). TD3. ICML 2018, PMLR 80, 1587–1596. §4–5 | SAC inherits clipped double-Q verbatim; the honest Stage-4 baseline |
| must | `[V]` Pardo, Tavakoli, Levdik & Kormushev (2018). "Time Limits in RL." ICML 2018, PMLR 80, 4045–4054. arXiv:1712.00378 | **The** citation for termination-vs-truncation. Highest value-per-page item in the stage |
| should | `[C]` Achiam, J. (2018). *Spinning Up in Deep RL*, OpenAI | The best cross-check when your code disagrees with the paper |
| should | `[?]` Tallec, Blier & Ollivier (2019). ICML 2019 | Why **not** to reduce the *policy* dt to 0.02 s to "match the physics". The substep split is the correct design |
| must | `[C]` Raffin et al. (2021). SB3. *JMLR* 22(268) + the VecNormalize docs + `handle_timeout_termination` | Verify against your **installed** version, not the documentation |
| should | `[?]` Nikishin et al. (2022). "The Primacy Bias in Deep RL." ICML 2022 | Directly relevant because you plan to **seed** the buffer with demos — exactly the condition where primacy bias bites |
| should | `[?]` Ball, Smith, Kostrikov & Levine (2023). RLPD. ICML 2023 | Symmetric demo/online sampling; the **LayerNorm-in-critic** finding is a cheap, high-value stabiliser |

#### Derive by hand

**(a) γ-contraction.** `‖TV − TW‖∞ ≤ γ‖V − W‖∞` for both `T^π` and `T*`, using
`|max_a f − max_a g| ≤ max_a|f − g|`. Then Banach ⇒ unique fixed point, geometric convergence, and
`‖V*‖∞ ≤ R_max/(1−γ)`. **Preconditions:** γ ∈ [0,1) *strictly*; bounded rewards. The contraction
**fails** at γ = 1 — undiscounted episodic uniqueness needs a proper-policy assumption.

**(b) The tanh log-probability correction.** This is the bug that costs people a week.

```
u     = mu(s) + sigma(s) * eps,   eps ~ N(0, I)      # PRE-squash, unbounded
a     = tanh(u)                                      # in (-1,1)^2

Change of variables, da_i/du_i = 1 - tanh(u_i)^2 :

    log pi(a|s) = sum_i [ log N(u_i; mu_i, sigma_i)  -  log( 1 - tanh(u_i)^2 ) ]
                                                      ^^^^^^^^ SUBTRACTED

NUMERICALLY STABLE IDENTITY — use this, never the naive form:
    log( 1 - tanh(u)^2 ) = 2 * ( log(2) - u - softplus(-2u) )
Derivation: 1 - tanh^2 u = sech^2 u = 4 e^{-2u} / (1 + e^{-2u})^2.
```

Three fatal variants: omitting it; **adding** instead of subtracting; and coding
`np.log(1 - np.tanh(u)**2)`, which returns `-inf` then `NaN` once |u| ≳ 9–10 in float32 — i.e.
*hours* into a run, after the policy becomes confident.

**(c) Termination vs truncation, and what the wrong version costs.**

```
terminated = True  <=>  s' is a genuine MDP terminal (absorbing; V(s') = 0 BY DEFINITION)
truncated  = True  <=>  cut for a reason OUTSIDE the MDP (t == max_steps == 400)

THE RULE:      y = r + gamma * (1 - terminated) * V(s')
NOT:           y = r + gamma * (1 - (terminated OR truncated)) * V(s')
```

Closed-form cost of getting it wrong (constant reward c = 1, γ = 0.995, true `V = 200.0`):

```
T =  10 ->   9.778  ( 4.9% of the truth)
T = 100 ->  78.846  (39.4%)          <- v1.0 printed 78.794; recomputed at 50-digit precision
T = 200 -> 126.608  (63.3%)
T = 400 -> 173.068  (86.5%)
```

The bias is a **ramp**: negligible early, total at the cut. Because the buffer mixes all t uniformly
and the observation contains no clock, the critic cannot represent a time-varying value — so it
learns one compromised value, biased **low everywhere**, with an irreducible regression residual.
The symptom is a mysterious success-rate ceiling on the **hardest (longest)** initial states only.

**Exception (Pardo et al.):** if you *deliberately* make the task time-limited, append remaining time
to the observation; then the limit **is** a genuine terminal. These are two different MDPs. **Pick
the time-unaware option** — bootstrap on truncation — and say so in writing.

> **Do not call these "case (a)" and "case (b)".** v1.0 presented that labelling as if it were
> Pardo et al.'s own notation; the paper labels the two regimes **(i)** and **(ii)**. The policy
> recommendation is correctly represented — only the labels were invented. Say "the time-aware and
> time-unaware formulations of Pardo et al. (2018)".

> **⚠ `τ_since_seen` is a clock proxy and contradicts this commitment.** The O0 observation vector
> below contains `log1p(τ_since_seen)`, normalised by `log1p(400)` — i.e. by `max_steps`. For an
> object that leaves view at step k, `τ = t − k`. The plan therefore commits in writing to a
> time-unaware observation and then ships a time-correlated feature scaled by the episode limit.
>
> **What this does and does not damage.** The truncation-bootstrap *target* is **not** biased by a
> clock: `y = r + γ(1−terminated)V(s′)` is unbiased for the infinite-horizon `Q*` whatever the
> observation contains, so §5.2(c)'s correctness argument survives. What a clock destroys is **the
> diagnostic**: the §9 failure table relies on "the observation contains no clock, so the critic
> cannot represent a time-varying value" to produce the signature symptom (only the longest starts
> fail). With τ present, the critic *can* fit a time-varying value, and a truncation bug becomes a
> consistent finite-horizon solution instead of a compromised one — **silent rather than diagnosable.**
>
> **Resolution: hold the τ slot at exactly 0.0 for O0, O1 and O2** (preserving I8's fixed width), and
> enable it only at O3/O4 where staleness carries real information. This is asserted by **EXIT-6.1**.
> Note the latency pattern: at O0/O1 τ is nearly always 0 anyway, so this detonates *exactly at O2* —
> the same shape as the binary-feature normalisation trap below.

**(d) GAE has its own, much shorter horizon** (PPO branch only). The advantage horizon is
`1/(1−γλ)`: at γ=0.995, λ=0.95 that is **18.3 steps = 1.8 s**, against a 200-step return horizon. To
propagate a terminal bonus 200 steps back you need λ ≈ 0.99 (67 steps) or a very good value
function. State which you chose.

#### Build

**Observation (O0) — no rays, no occupancy grid.** Fixed semantic slots (front car / rear car /
kerb / goal-slot), ego frame. Per-object feature vector, **identical width at every stage**:

```
(dx, dy, sin_theta, cos_theta, l, w, type_onehot(3), valid, visible_now, log1p(tau_since_seen))
```

plus the ego block `(v, delta, settle_counter/K_settle)`. `valid` (this slot holds a real object —
padding bit) and `visible_now` (currently sensed) are **two different bits**; conflating them is a bug.

> **`settle_counter` is not optional and v1.1 omitted it (A22).** §7.5 requires the tolerance
> conditions to hold for `K_settle = 5` **consecutive** steps, so success is a function of history,
> not of a single `WorldState`. If the counter is not in the state and in the observation, then
> (a) I2's "success reads `WorldState`" is false, and (b) the agent cannot tell 1 step into the
> settle window from 4 — **so O0 is not observation-Markov**, and §5.2's title, §6.1's "Full state"
> label and H_A's entire sufficiency argument are all built on a premise that does not hold. The
> symptom is §9's "error histogram piles up just outside the tolerance", misdiagnosed as a tolerance
> problem. Normalise by `K_settle` and include it at **every** rung.

**The `Observer` interface — this is the whole trick, and it is ~30 lines:**

```python
class Observer(Protocol):
    def reset(self) -> None: ...
    def observe(self, s: WorldState) -> np.ndarray: ...
    @property
    def space(self) -> gym.spaces.Space: ...
```

`FullObserver` / `DropoutObserver` / `FOVObserver` / `OccludedObserver`, plus a
**`BeliefObserver` that wraps another `Observer`** — so "with or without the belief filter" is a
pluggable layer, which is exactly the O3 ablation. The environment takes an `Observer` in its
constructor. Reward and termination read `WorldState` directly.

**Normalisation — a resolved conflict.** Two sources disagreed. **Recommendation: do not use running
observation normalisation at all.** Your observation is hand-designed with known physical ranges, so
bake **fixed analytic scaling** into the observation builder:

```
positions / 10.0 m    v / 1.5    delta / 0.6    l, w / 5.0    log1p(tau) / log1p(400)
sin/cos, one-hots, valid, visible_now : PASS THROUGH UNCHANGED
```

This eliminates an entire bug class (checkpoint/normaliser desync, eval-time contamination,
irreproducible eval scores). *If* you nevertheless use `VecNormalize`: index-mask the binary features
out of it. A rarely-set bit acquires a tiny running variance and, when it flips, produces a
normalised input of magnitude `1/sqrt(var)` that saturates `clip_obs = 10`. This is **latent at O0**
(where `visible_now` is always 1) and **detonates exactly when you switch on O2**.

**Starting hyperparameters**

```
gamma           0.995            buffer_size     1_000_000
batch_size      256              learning_starts max(10_000, |demo seed|)
lr              3e-4  Adam, THREE separate optimizers (actor / critics / log_alpha)
tau (Polyak)    0.005            train_freq 1, gradient_steps 1   (replay ratio G = 1)
net_arch        [256, 256] both; LayerNorm in the CRITIC
log_std bounds  [-20, +2]        target_entropy  -2.0 (= -dim(A), read from the action space)
log_alpha init  0.0
action_space    Box(-1, 1, shape=(2,))
    env applies   a_long = 1.5*a[0] [m/s^2]      delta_dot = 0.6*a[1] [rad/s]
norm_reward     False   -- NEVER True with a replay buffer
n-step returns  n = 5..10, mixed with 1-step at lambda_n ~ 0.5   -- NOT OPTIONAL, see below
```

> **Naming hazard:** SAC's Polyak rate is `tau = 0.005`, but `1 − tau = 0.995` is numerically
> identical to the discount factor and completely unrelated to it — and `tau` is *also* the name of
> `log1p(tau_since_seen)` in the observation. **Rename at least two of these three before you write
> them twice.**

> **n-step returns are not optional at γ = 0.995 over 200-step episodes.** 1-step TD needs O(200)
> sequential backups to move the terminal bonus to the start state. This is likely the largest
> single sample-efficiency factor after the curriculum.

#### EXIT CRITERIA — Stage 2

**Implementation gates (must pass before *any* parking experiment)**

| ID | Criterion | Threshold |
|---|---|---|
| **EXIT-2.15** | The exact SAC implementation solves Pendulum-v1 | mean eval return ≥ −200 by 20k env steps, **3/3 seeds** |
| **EXIT-2.16** | The same code solves a 2D point-mass reach with **sparse +100**, −0.05/step, γ=0.995, `max_steps`=400 | success ≥ 90% on a fixed 200-episode set, **3/3 seeds**, 300k steps. *This is the important one:* it is the minimal environment exercising sparse bonus + long horizon + time limit, and it separates "my SAC is broken" from "parking is hard" |

**Correctness gates**

| ID | Criterion | Threshold |
|---|---|---|
| **EXIT-2.5** | Truncation bootstrap, against an analytic answer | degenerate 1-state MDP, r=+1, γ=0.995, T=10. **(A)** with the bootstrap → Q → 200.0 ± 2.0. **(B)** treating truncation as termination → Q → 9.778 ± 0.2. **Both** must hold — (B) proves the code path is genuinely sensitive to the flag rather than accidentally correct |
| **EXIT-2.4** | Flag contract | 4 scripted rollouts (collide / succeed / time out / collide exactly at step 400) return `(T,F)`, `(T,F)`, `(F,T)`, `(T,F)`. Never both True. `step()` after episode end raises |
| **EXIT-2.17** | tanh log-prob integrates to 1 | ∫exp(log_prob) over the box = 1.0 ± 1e-3 for every tested (μ,σ), in dim 1 and dim 2 |
| **EXIT-2.18** | tanh log-prob matches a **finite-difference** Jacobian reference (assumes nothing about the softplus identity) | max abs diff < 1e-4 nats over u ∈ [−6,6]² |
| **EXIT-2.19** | tanh log-prob numerical stability | stable form finite at u ∈ {±30, ±20, ±12, 0}; naive form **must** produce −inf for \|u\| ≥ 10 in float32 (asserted explicitly, to document why the stable form exists) |
| **EXIT-2.20** | Actor gradient flows through the action | with a stub `Q = w·a`, α=0: autograd `dL/dμ_i` matches `−w_i(1−tanh²u_i)` to rel. 1e-5, **and is not the zero vector** |
| **EXIT-2.21** | Critic target resamples `a'` from the **current policy**, evaluated on the **target** critics | structural test with a sentinel buffer next-action; the sentinel must never be used |
| **EXIT-2.22** | α responds to entropy error with the right sign | measured entropy above target → α decreases monotonically; below → increases; α > 0 throughout; `target_entropy == −2.0` read from the action space |
| **EXIT-2.14** | Action scaling round-trip | 10⁴ random `a ∈ [−1,1]²` map into `[−1.5,1.5]×[−0.6,0.6]` and invert to 1e-9; endpoints pinned; declared space is `Box(-1,1)` |
| **EXIT-2.13** | Reward is **not** summed over substeps | returned reward equals a single post-step evaluation exactly; invariant to `n_substeps ∈ {1,5,10}` in the collision-free case to 1e-6; **and** the tunnelling case is missed at `n=1` and caught at `n=5` |
| **EXIT-2.12** | Reward reads truth, not observation | replace the `Observer` with a stub returning all-NaN; rewards, `terminated`, `truncated`, success must be **bitwise identical** to the real run. Any NaN reward fails |
| **EXIT-2.6** | Shaping genuinely telescopes | `\|Σ γᵗ F − (γᵀΦ(s_T) − Φ(s₀))\| ≤ 1e-9·max(1,\|P\|)` on 1000 synthetic + 200 real trajectories, at γ ∈ {0.9, 0.99, 0.995, 1.0} |
| **EXIT-2.23** | The telescoping test has **power** | deliberately construct `F_wrong = Φ(s′)−Φ(s)`; EXIT-2.6 **must fail** on it, and the discrepancy must match `((1−γ)/γ)·Σγᵗ Φ(s_t)` to rel. 1e-9 |
| **EXIT-2.24** | Φ is a pure function of state | same `WorldState` via two different histories → **bitwise** equal Φ; signature accepts only a `WorldState`; no drift under 100 interleaved calls at other states |
| **EXIT-2.7** | No-suicide reward configuration | `P_collision ≥ 2·c_max·(1−γ^400)/(1−γ)`. At c_max = 0.05 → ≥ 17.3; **use 40** with `R_success` = 100. Asserted on the **config object**, so it re-runs on every config change |
| **EXIT-2.25** | Reward sanity tournament | six scripted policies (zero action / full throttle / drive into obstacle / circles / hover 0.5 m short / **Stage-1 expert**). The expert must beat every other by ≥ 0.25·`R_success` on **every** scenario category |
| **EXIT-2.8** | Clearance metric uses exact OBB, not circles | max abs error ≤ 1e-6 m vs a brute-force reference over 10⁴ pairs; a car parked with its flank 0.10 m from a wall reports `c_min ∈ [0.0999, 0.1001]` |
| **EXIT-2.9** | Substep resolution prevents tunnelling | 0 tunnelling events over 10⁴ perpendicular-approach trials at every thickness present in the frozen set; generator's minimum obstacle thickness > 3 × 0.03 m |

**Protocol gates (freeze these before any tuning)**

| ID | Criterion | Threshold |
|---|---|---|
| **EXIT-2.1** | Frozen eval set integrity | SHA-256 matches a hash literal committed in the eval module; abort on mismatch (**no warn-and-continue path may exist**). Per-scenario `L_oracle`, `g_oracle`, `oracle_min_clearance`, `planner_resolution` present and finite |
| **EXIT-2.2** | Every frozen scenario is oracle-feasible | feasible fraction of VAL and TEST **== 1.000 exactly**; the INFEASIBLE control set == 0.000 at 4× resolution; planner and env collision checkers agree on 10⁴ random configurations |
| **EXIT-2.3** | Evaluation determinism | two runs of the same checkpoint in separate processes: terminal class and episode length identical for **100%**; final pose and `c_min` to 1e-9 |
| **EXIT-2.26** | No eval transitions enter the replay buffer | counter == 0; eval curriculum level == MAX for 100%; eval DR flag == False |
| **EXIT-2.10** | Diagnostic logging completeness | every required key present, finite, at the declared cadence, over a 5000-step smoke run; per-term reward sums reconstruct the episode total to 1e-9 |

**Performance gates**

| ID | Criterion | Threshold |
|---|---|---|
| **EXIT-2.27** | Performance on the **Stage-2 easy sub-distribution** (reverse-curriculum rung 0: start pose within 3 m of the goal along the reference path, slot length ≥ 1.5·l; **bay family: `η_bay ≥ 1.55`, i.e. `W_aisle ≥ 6.75 m` at `W_bay = 2.50 m`** *(v1.3)*), at `eps_final`, no randomisation | success ≥ **0.90**; collision ≤ **0.02**; timeout ≤ **0.08**; out-of-bounds ≤ **0.005**; mean path length ≤ **1.5×** the Stage-1 tracked-expert length. **Report the full-difficulty number too, as the Stage-3 baseline — but do not gate on it.** *v1.1 gated Stage 2 on ≥0.90 at **full** difficulty with **no curriculum**, which is strictly harder than EXIT-3.1's ≥0.80 at full difficulty **with** curriculum. Stage 2 would therefore either deadlock forever or, if passed, guarantee that Stage 3 — weeks of curriculum work — is a null result by construction. A stage gate must be easier than the stage that follows it.* |
| **EXIT-2.11** | γ sweep, run as an actual experiment and put in the thesis | γ ∈ {0.99, 0.995, 0.998}, **5 seeds each** (not 3 — §5.4 bans K=3 and EXIT-4.8 asserts K==10 for headline tables; a 3-seed result "put in the thesis" contradicts both. K=5 is the document's own exploratory floor, and this sweep is exploratory), everything else identical. **γ = 0.995 must attain the highest IQM success rate, with its CI not overlapping γ=0.99's upper bound.** If γ = 0.99 wins, the discount analysis is wrong for this reward and the reward scale must be re-derived before Stage 3 |
| **EXIT-2.28** | Critic magnitude bound holds throughout | Compute **programmatically** from the reward config: `B = c_max·(1−γ^max_steps)/(1−γ) + max(\|R_success\|·(1+β), \|P_collision\|) + Φ_clip = 0.05·173.068 + 120 + 30 = 158.65`. **Raise** at `max\|Q\| > 2B ≈ 320`; **warn** at `1.2B ≈ 190`. **Positive control:** with γ dropped from `F` (the EXIT-2.23 bug) the assertion must trip within 200k steps. *v1.1's two-bound rewrite (hard 12280 / soft 600) was **44× too loose**, and it got there by ignoring the very identity a sibling criterion enforces: by Ng–Harada–Russell, `Q′(s,a) = Q(s,a) − Φ(s)` **exactly**, so shaping contributes at most `\|Φ\|_max = 30` — **not** `30/(1−γ) = 6000`. The worst-case step cannot recur every step; that is what telescoping means. v1.1 also summed `R_success = 100` and `P_collision = 40`, which are **mutually exclusive** terminals — the correct term is `max(·)`, not the sum. Both v1.1 numbers were dead: at 12280 the raise fires long after the run is over; at 600 the "warn" fires only when the critic is already 4× beyond anything legitimate.* |
| **EXIT-2.29** | **Five-consumer truncation audit** *(added v1.2)* | I4 names **five** consumers of the terminated/truncated distinction; v1.1 gated **one**. On EXIT-2.5's degenerate MDP (r=+1, γ=0.995, T=10) assert each against a closed form: **(i)** n-step with n=5, λ_n=0.5 — the target at t=T−2 equals the analytic mixed value to 1e-9 and **differs** from the terminated-treatment value by the analytic gap; **(ii)** the last transition's shaping term equals `γΦ(s₄₀₀) − Φ(s₃₉₉)` **bitwise**, NOT `−Φ(s₃₉₉)`; **(iii)** terminal class == TIMEOUT; **(iv)** the curriculum counter increments *attempts* and not *successes*; **(v)** source-level assertion that `terminated or truncated`, `terminated \| truncated` and a bare `done =` appear **nowhere** in the codebase. Threshold: all exact, **and each of (i)–(iv) must FAIL when the flags are deliberately conflated.** *The n-step cut is the more dangerous untested site — at λ_n ≈ 0.5 a wrong cut biases half the target — and the Φ-zeroing site injects a fictitious `−Φ(s₄₀₀)` into every truncated return, which §7.1 warns about and nothing checked. Passing EXIT-2.5 while failing either produces exactly the symptom §9 attributes to EXIT-2.5, sending you to a test that already passes.* |

---

### 5.3 Stage 3 — Curriculum and robustness

**Goal.** From "works on the easy distribution" to "works on the full distribution under
perturbation." This stage also carries observation rungs **O1** and **O2**.

#### Theory and mathematics to read

| Priority | Source | Covers |
|---|---|---|
| must | `[V]` Ng, Harada & Russell (1999). "Policy Invariance Under Reward Transformations." ICML 1999, 278–287 | The one theorem that decides which reward terms you may tune freely |
| must | `[V]` Grzes, M. (2017). "Reward Shaping in Episodic RL." AAMAS 2017, 565–573 | The terminal-state corner your implementation lives in. (Paper identity verified; its text was **not** readable through the fetch tool — read it yourself) |
| should | `[V]` Wiewiora, E. (2003). "Potential-Based Shaping and Q-Value Initialization are Equivalent." *JAIR* 19, 205–208 | PBRS is an **initialisation**, not extra information. This is the null hypothesis your shaping ablation must beat. 4 pages — read all of it |
| must | `[V]` Devlin & Kudenko (2012). "Dynamic Potential-Based Reward Shaping." AAMAS 2012, 433–440 | The **only** form under which changing Φ across curriculum phases is still provably invariant |
| must | `[V]` Florensa, Held, Wulfmeier, Zhang & Abbeel (2017). "Reverse Curriculum Generation for RL." CoRL 2017, PMLR 78, 482–495 | Read for the success-rate banding rule and failure analysis. You will **replace** its Brownian walk with backward sampling along RS/Hybrid A* paths — which gives feasibility guarantees the paper's method lacks |
| should | `[V]` Portelas, Colas, Hofmann & Oudeyer (2019). ALP-GMM. CoRL 2019, PMLR 100 | The right automatic curriculum once you have **more than one** difficulty axis |
| must | `[C]` Bengio, Louradour, Collobert & Weston (2009). "Curriculum Learning." ICML 2009 | Tolerance annealing **is** a continuation method on `1[error < ε]` — the citation that makes it a method rather than a trick |
| must | `[C]` Tobin et al. (2017). Domain Randomization. IROS 2017 | Canonical DR citation — but note it is **visual** randomisation for a detector, not dynamics randomisation for a controller |
| must | `[?]` Peng, Andrychowicz, Zaremba & Abbeel (2018). "Sim-to-Real Transfer with Dynamics Randomization." ICRA 2018 | The **correct** citation for randomising wheelbase, steering gain, latency. Also documents why a recurrent policy helps under dynamics DR — a **direct confound** for your O3 experiment |
| should | `[V]` OpenAI et al. (2019). "Solving Rubik's Cube with a Robot Hand." arXiv:1910.07113 | The ADR update rule verbatim; implement ADR-lite over ~6 parameters and say so |
| must | `[C]` Andrychowicz et al. (2017). HER. NIPS 2017 | Required reading so you can write the critical assessment of why it does **not** apply here |
| must | `[V]` Nair, McGrew, Andrychowicz, Zaremba & Abbeel (2018). ICRA 2018, 6292–6299 | The **Q-filter** — one line of code, and the fix for demos anchoring you to a suboptimal trajectory family |
| should | `[?]` Vecerik et al. (2017). DDPGfD. arXiv:1707.08817 | The recipe you will actually implement, adapted to SAC |
| should | `[V]` Laskey, Lee, Fox, Dragan & Goldberg (2017). DART. CoRL 2017, PMLR 78 | A deterministic tracker produces a **measure-zero tube**; noise injection is the fix |

> **Honesty note:** there is **no canonical paper called "SACfD."** It is a folk name for applying
> the DDPGfD recipe to SAC. Do not cite it as a paper. Say "the DDPGfD recipe (Vecerik et al. 2017)
> applied to SAC", or "SAC + Q-filtered BC (Nair et al. 2018)", or cite AWAC `[V]` (arXiv:2006.09359).

#### Derive by hand

**(a) PBRS, stated exactly.**

```
r'(s,a,s') = r(s,a,s') + F(s,a,s'),     F(s,a,s') = gamma * Phi(s') - Phi(s)

THEOREM (Ng, Harada & Russell 1999). Sufficiency: for ALL T and ALL R, every optimal policy of
M' is optimal in M and conversely, via the pointwise identity
        Q*_{M'}(s,a) = Q*_M(s,a) - Phi(s)
Since -Phi(s) is independent of a, argmax_a is unchanged.
Necessity: if F is not of this form, there exist T and R for which some optimal policy of M'
is suboptimal in M.
```

**Preconditions that get botched:** (1) Φ depends on **state only** — not action, not timestep, not
curriculum level, not observation. (2) The γ inside F is **exactly** the γ in the Bellman backup.
(3) Φ bounded. (4) The episodic case requires **Φ(absorbing) = 0**.

**(b) The no-farming property — the slogan is wrong for γ < 1.**

Around a cycle `s₀ → … → s_n = s₀`:

```
(a) discounted sum from the cycle start:   c_n = (gamma^n - 1) * Phi(s_0)
(b) value of repeating it forever:         c_n / (1 - gamma^n) = -Phi(s_0)
(c) UNDISCOUNTED sum around the cycle:     (gamma - 1) * sum_i Phi(s_i)     -- zero only at gamma=1
```

So "PBRS sums to zero around any closed cycle" is exact **only** in the undiscounted case. The
correct — and **strictly stronger** — statement for γ < 1 is **(b)**: *the total discounted shaping
contribution of any trajectory from s₀ is the policy-independent constant −Φ(s₀), so no policy can
accumulate shaping reward by looping.*

> **Do not write a unit test asserting the undiscounted cycle sum is 0.0 at γ = 0.995.** It is not,
> the test will fail against a *correct* implementation, and someone will "fix" it by dropping γ.

**(c) The missing-γ bug is exactly a naive dense reward.**

```
sum_t gamma^t F_wrong  -  sum_t gamma^t F_right  =  ((1-gamma)/gamma) * sum_t gamma^t Phi(s_t)
```

Dropping γ is **algebraically identical** to correct PBRS **plus** a per-step running reward
`c_bug·Φ(s_t)` with `c_bug = (1−γ)/γ = 0.005025`. With |Φ| clipped at 30 that is a hidden running
cost of up to **0.151/step** — three times a nominal 0.05 time cost, pointing the same way (toward
early termination). Large enough to **induce deliberate collisions** if the collision penalty was
sized against the declared time cost only. It is not "a small perturbation"; it is an undeclared
second reward term.

**(d) PBRS invariance also holds under the max-entropy objective** (you need this because SAC's
objective is not the hard-max one Ng et al. proved). Four lines:

```
Assume V'_soft(s) = V_soft(s) - Phi(s). Then
    Q'_soft(s,a) = r + gamma Phi(s') - Phi(s) + gamma E[V_soft(s') - Phi(s')]
                 = Q_soft(s,a) - Phi(s)
and V'_soft(s) = alpha log Int exp((Q_soft - Phi(s))/alpha) = V_soft(s) - Phi(s).   Consistent.
Hence pi'(a|s) prop exp(Q'_soft/alpha) prop exp(Q_soft/alpha) = pi(a|s).
```

The max-entropy optimal policy is **unchanged**, and since the entropy of π is unchanged, the α
selected by the automatic-temperature constraint is unchanged too. **Preconditions:** fixed α, or
automatic α via an entropy *constraint* (standard SAC). It breaks if you anneal α on a hand schedule
keyed to reward magnitude. *This four-line derivation is a cheap, genuine contribution to the
write-up's rigour — put it in the thesis.*

**(e) Anti-suicide bound.**

```
Crashing immediately beats stalling to truncation iff  P_col < c_max (1 - gamma^N)/(1 - gamma).
REQUIRE the strict opposite with a factor-2 margin:
        P_col >= 2 c_max (1 - gamma^{N_max})/(1 - gamma)
gamma=0.995, N=400:  (1-0.13466)/0.005 = 173.07 ;  c_max = 0.05  ->  P_col >= 17.3.  Use 40.

Separately require that succeeding beats stalling for the SLOWEST successful episode:
    N=300: 0.2223*100 = 22.2  >  0.05*155.5 = 7.8     OK
    N=400: 0.1347*100 = 13.5  >  0.05*173.1 = 8.7     MARGINAL
```

That marginal line is the concrete reason the reverse curriculum must keep episode lengths well
under 300 steps.

**(f) Sample-budget criterion for the easiest curriculum rung.** With per-episode success
probability p, episodes-to-first-success is Geometric(p). With 1e6 env steps at ~200 steps/episode
you get n₀ = 5000 episodes; demanding ≥50 successes gives

```
p_0 >= 50 / 5000 = 1e-2
```

**The easiest rung must be solvable roughly 1 time in 100 by the untrained, maximum-entropy SAC
policy.** This is a **measurement**, not an assumption — roll out the untrained policy 2000 times at
each candidate `sigma_max` and measure it (EXIT-3.5).

> A pleasant free lunch: with `(a_long, δ̇)` as actions, i.i.d. Gaussian action noise **integrates**
> into a temporally correlated random walk in `(v, δ)` — you get Ornstein–Uhlenbeck-like exploration
> for free from the rate-based action space. **Do not add OU noise on top of SAC's stochastic
> policy**; you would be double-integrating. Worth one sentence in the thesis.

#### Build

**Reverse curriculum from the Stage-1 oracle** (strictly better than a Brownian walk):

```
1. Plan a collision-free reference path P(sigma), sigma in [0, Sigma], goal at Sigma. Cache it.
2. Sample:  sigma ~ U(0, sigma_max)                 # arc length BACK from the goal
            (x,y,theta) = P(Sigma - sigma)
            delta_0 = atan(L * kappa(Sigma - sigma))   # matched to path curvature
            v_0     = dir(...) * U(0, v_ref)
3. JITTER:  (x,y,theta) += N(0, diag(0.15 m, 0.15 m, 3 deg));  delta_0 += N(0, 0.05), clipped
4. SAMPLE v_0 AND delta_0 INDEPENDENTLY of the path for a fraction of samples
5. REJECT unless collision-free under exact SAT AND the feasibility oracle finds a solution
6. Advance sigma_max only on success rate measured on the FIXED eval set
```

> **Steps 3 and 4 are not optional.** Without perturbation every initial state lies exactly *on* an
> optimal path, the policy never sees an off-path state, and it collapses to an **open-loop replay**
> that succeeds during curriculum training and fails on the frozen set. Without step 4, the initial
> `δ` leaks the reference path's curvature and the policy learns to read it.

**Tolerance annealing — gate on measured success rate, never on step count:**

```
every 200 training episodes, SR = success rate at the CURRENT eps:
    if SR > 0.70:  eps <- max(eps_final,  0.80 * eps)     # tighten
    if SR < 0.30:  eps <- min(eps_start,  1.25 * eps)     # LOOSEN -- yes, implement this branch

    eps_x   0.60 -> 0.20 m       eps_th  20 -> 5 deg
    eps_y   0.40 -> 0.10 m       eps_v   0.30 -> 0.05 m/s
```

A step-count schedule fails catastrophically and silently: if the agent is behind, difficulty
tightens under it, success collapses to zero, the buffer fills with failures, and SAC does not
recover. **A curriculum parameter that only ever ratchets upward has a bug in its decrease branch.**

**Once you have more than one difficulty axis, stop banding independently.** `sigma_max`, slot
length, tolerance and noise interact multiplicatively and independent controllers will fight. Switch
to ALP-GMM over the joint parameter vector. Plan for this by making difficulty a single named
parameter vector from the start.

**Two independent randomisation configs, never enabled together in a causal-attribution run:**

- **dynamics/scene randomisation** — perturbs `WorldState` (wheelbase, δ_max, δ̇_max, `a_max`, steering gain/offset, actuator latency, body dimensions). *v1.2: v1.1 listed "friction", which does not exist in a kinematic model — there is no tyre force to scale. Delete it or move to a dynamic model.*
- **observation randomisation (O1)** — perturbs `Observation` only (noise, delay, dropout `p: 0→0.1→0.3`)

> **§4.1's "knife edge" was withdrawn in v1.1.** There is no feasibility boundary here. What §4.1 now gives is the *cost* of a cusp and the **corrected** direction table: lowering `a_max` or raising `v_max` makes cusps **easier**, not harder. Randomise knowing which way is which.

**Demonstrations (if used):**
- Generate by **running the Stage-1 tracker inside the real environment** with **DART-style injected
  noise** (start at 20% of the action range) and start-state jitter; keep only collision-free successes.
- Store actions in **normalised** units clipped to ±0.999 (exactly ±1 sits where `log π → −∞`).
- **Recompute demo rewards with the agent's own reward function.** Never store a planner cost.
- **RLPD-style symmetric sampling** (half demo, half online) from the very first gradient step, or
  anneal the demo fraction 0.5 → 0.0 over ~200k steps. A 100%-demo buffer triggers primacy bias.
- **Q-filter the BC term** (Nair et al.), with an unfiltered warm-up of only ~5k gradient steps.

**HER: read it, then document why you are not using it.** Four reasons, in severity order.
(1) **Termination breaks relabelling**: your episode terminates on success, so under `g′ = s_k` the
episode *should have ended* at k; transitions k+1..T exist only because the real episode continued,
and feeding them to the critic teaches that trajectories heading into a wall are good. The standard
HER results come from **fixed-length, non-terminating** Fetch environments — that is precisely the
precondition you violate. (2) The goal region is obstacle-bounded. (3) Your goal is a fixed slot, not
a sampled point. (4) You already own a feasibility oracle and a demonstrator, which is a stronger
intervention.

#### EXIT CRITERIA — Stage 3

| ID | Criterion | Threshold |
|---|---|---|
| **EXIT-3.1** | Full-difficulty performance | success ≥ **0.80** at slot length **1.2·l** (parallel) **and at `η_bay = 1.15`, i.e. `W_aisle = 5.00 m` at `W_bay = 2.50 m` (bay)** *(v1.3)*, random initial poses, `eps_final`, frozen set. **Report the two families separately** — A25 buys one *policy*, not one *number*, and a headline average hides a family that never learned |
| **EXIT-3.2** | Robustness to dynamics DR | success drops ≤ **10 percentage points** under ±15% parameter perturbation |
| **EXIT-3.3** | Curriculum start states are valid | 5000 draws at each of 5 `sigma_max`: **100%** collision-free under exact SAT, in bounds, `\|δ₀\| ≤ δ_max`, and **100%** pass the feasibility oracle. Pre-filter rejection rate logged; **> 50% at any `sigma_max` means the jitter is too large** |
| **EXIT-3.4** | Curriculum start states are non-degenerate and non-leaking | sd of perpendicular distance to the reference path **> 0.15 m** at every stage past the first; mutual information between sampled `δ₀` and the path's curvature indistinguishable from zero (permutation test, p > 0.05, n = 2×10⁴) |
| **EXIT-3.5** | The easiest rung is actually reachable | Wilson **lower** bound on `p₀` for the untrained policy **> 1e-2**, measured over 2000 rollouts. If not, loosen before training — do not start |
| **EXIT-3.6** | Tolerance-annealing honesty | eval harness hard-asserts `eps == eps_final` and the eval-set hash; DR off. Both curves (training-ε and final-ε) plotted for the whole run; **their gap must close to < 0.05 absolute by the end of Stage 3** |
| **EXIT-3.7** | Demo replay fidelity | for 100 stored episodes, replaying the action sequence from the stored initial `WorldState` reproduces the trajectory to **1e-6** per component; reward components to 1e-9 |
| **EXIT-3.8** | Reward-hacking monitor never fires | no sustained window (3 consecutive) with Spearman correlation ≤ −0.5 between normalised shaped return and `eps_final` success rate on the **frozen** set |
| **EXIT-3.9** | Farming / oscillation detectors | path-length ratio ≤ 2.0 median, ≤ 3.0 at p95; v zero-crossings (0.05 m/s hysteresis) ≤ 2× the RS cusp count at the median; near-tolerance dwell fraction ≤ 0.05 |
| **EXIT-3.10** | O1 rung passes | success drops ≤ **10 pp** under observation-domain randomisation at `p_drop = 0.3` |
| **EXIT-3.11** | **O2 rung actually bites** | under limited FOV (rear invisible while reversing), the reactive MLP's success rate must drop **measurably** — if it does not, the FOV is set too wide and must be tightened before Stage 4. *This is a gate on the experiment's validity, not on the agent* |

---

### 5.4 Stage 4 — Evaluation, baselines, and the O3 memory comparison

**Goal.** Turn results into evidence. The protocol was frozen at Stage 2; this stage executes it.

#### Theory and mathematics to read

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

#### The statistics you will actually use

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

#### The full metric set

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

**The success-rate surface is the deliverable that turns this from a demo into a result.** Two
heatmaps per family, with the family's own difficulty axis on x — **parallel: slot length; bay:
`W_aisle`** *(v1.3; v1.0–v1.2 named only the parallel axis, so the bay surface had no definition)* —
against (initial lateral offset) and (initial heading error). 10×10, ≥50 episodes/cell. At 50 episodes/cell the Wilson half-width is 10.1 pp — fine for
**shape**, useless for a per-cell claim, so **never quote a cell in text**. Fit a logistic surface,
extract the agent's **50% contour** with a bootstrap band, and overlay: the empirical oracle boundary
(bisect on slot length with Hybrid A*), the static containment bound, and your hand-derived analytic
single-cusp bound. **Report the gap between the agent contour and the oracle contour**, with a band —
that gap is the result.

#### The O3 memory comparison — five arms

| Arm | Definition | Role |
|---|---|---|
| **A1** | MLP + instantaneous local observation (incl. `valid`, `visible_now`), no history | amnesiac lower bound |
| **A2** | MLP + frame stack (k=8) | **NEGATIVE CONTROL — label it as such.** k=8 covers 0.8 s; the required memory horizon is the whole manoeuvre, 100–400 steps. It is off by two orders of magnitude, not merely weaker |
| **A3** | MLP + **hand-written static belief filter** | the strong, boring baseline. **Predicted winner** |
| **A4** | GRU + instantaneous local observation | learned memory |
| **A5** | GRU + **privileged full-state critic** (asymmetric) | changes only the critic input, so it stays comparable |
| *(A6)* | distilled student from a full-state teacher | optional; a **different training algorithm** — belongs in a separate row, never conflated with A5 |

> **⚠ A3 and A4 are not information-symmetric, and no v1.0 criterion covered it.** I3 mandates an
> **ego-frame** observation. To render a stored obstacle pose in the *current* ego frame, the
> `BeliefObserver` needs the ego's motion since that observation — and as a wrapper over `WorldState`
> it simply reads the true ego pose. **A4 has no such access:** it sees ego-frame quantities plus
> `(v, δ)`, so to reproduce A3's feature it must dead-reckon the bicycle model over 100–400 steps and
> will accumulate drift. A4's policy class therefore does not straightforwardly contain A3's, and a
> loss by A4 is partly attributable to a **dead-reckoning burden rather than to memory**.
>
> **Fix:** give A4 the same ego-motion information A3's filter implicitly uses — a per-step
> delta-pose input — and add it to the EXIT-4.9 key list. (The alternative escape hatch, exempting
> the goal slot from the FOV mask so the ego is permanently localised against a fixed anchor,
> threatens EXIT-3.11: if a goal anchor plus a memorised layout prior suffices, the FOV rung will not
> bite and O3 has no partial observability left to study. §6.1(b) resolves this the other way.)

**Pre-register this before running any arm** (commit it, cite the hash):

> **H_A (primary).** At observation level O2 (static obstacles, limited FOV, known association,
> noise-free), `SR(A3) ≥ SR(A4) − 0.03`: the hand-written belief filter is equivalent to or better
> than the GRU within a 3 pp margin.
> **Rationale (v1.1 — v1.0 overclaimed here).** For static, noise-free, known-association obstacles
> the belief over each obstacle's pose collapses to a point mass at the last observed pose, so
> `(last-seen pose, seen flag)` **is** the belief and hence a sufficient statistic (Åström 1965;
> Kaelbling, Littman & Cassandra 1998). What follows is that **the A3 policy class contains an
> optimal policy**, so any A4 advantage must come from optimisation, exploration or approximation
> effects rather than from *information* — which is exactly what the linear probe (EXIT-4.10) and the
> τ ablation (H_B) are for.
>
> v1.0 said "a GRU can at best tie it", stated as a prediction about measured success rate. That does
> not follow: the theorem bounds *optima*, the hypothesis is about *estimates*. At least four routes
> let A4 beat A3 with every word of the theory intact — (1) the internal clock, on a finite-horizon
> success metric; (2) recurrent state gives temporally correlated exploration, which §5.3 notes this
> task benefits from; (3) the hidden state is a *learned* basis and may approximate Q better than a
> hand-chosen 12-dim-per-object encoding, independently of sufficiency; (4) A3's advantage is
> contingent on its encoding faithfully rendering `b`, which precondition (vii) puts in doubt.
> The one-sided 3 pp margin remains a reasonable pre-registration; the rationale does not.
> **H_B (secondary, A21).** At O2, adding `τ_since_seen` to A3's features does **not** improve success
> rate. If it does, assumption A4 (static world) is being violated somewhere.
> **H_C.** At O4 (occlusion + missed detections + association ambiguity), the ordering **reverses**.

#### 5.4.1 Compute budget and the fallback ladder *(added v1.2)*

**Stage 4 as specified in v1.1 costs roughly 860 GPU-hours of training**, and that is before
evaluation. The audit costed it: 5 headline arms x 10 seeds, **plus** the mandatory DR-on
replication of all five arms that EXIT-4.11 requires, **plus** the O2a sweep, H_B, a TD3 baseline
and the gamma sweep, at an assumed 3M environment steps per run. The EXIT-4.7 success surface alone
needs a further **40-200M environment steps** of pure evaluation, which v1.1 never costed at all.

**Worse, v1.0/v1.1 stated no training-step budget for any stage — which makes every performance
gate unfalsifiable.** "Success >= 0.90" with no step budget is not a criterion; it is a wish that
can always be deferred by training longer.

**Fix, in two parts.**

**(1) Every performance gate gets a step budget.** State it as `success >= X within N environment
steps`. Starting values: Stage 2 gates at **3M** steps, Stage 3 at **10M**, Stage 4 arms at **3M**
each. A gate not met within budget is a **failure**, not an invitation to train longer.

**(2) A pre-declared fallback ladder, descended in this order when the budget binds.** v1.1 forbade
its own cheapest fallback — it banned K=3 and asserted K==10 — leaving no legal way to reduce cost:

| Rung | Action | Cost saved | What it costs you |
|---|---|---|---|
| 0 | Full spec as written | — | ~860 GPU-h |
| 1 | Drop the DR-on replication of all five arms (EXIT-4.11) to **two** arms (A3, A4) | ~35% | the DR-on comparison covers only the two arms H_A is about |
| 2 | Cut the O2a sweep from 5 radii to **2** (6 m, 12 m) | ~10% | coarser radius resolution; EXIT-6.4 reports the two-point sweep |
| 3 | Reduce the success surface to a **6x6** grid at 30 episodes/cell | ~60% of eval | contour band widens; state it in the figure |
| 4 | Reduce K from 10 to **7** for non-headline arms (A1, A2, A5), keep **K=10 for A3 and A4** | ~20% | only the H_A pair retains full power — which is the pair the pre-registration is about |
| 5 | Drop A5 (asymmetric critic) entirely | ~15% | lose the asymmetric-critic arm; it is the least load-bearing of the five |

**Do not descend below rung 5 by cutting seeds on A3/A4.** That pair is the entire pre-registered
experiment, and the TOST margin already has a power problem (below).

**The 3 pp TOST margin has no power analysis, and K=10 is probably not enough for it.** At plausible
between-seed standard deviations the equivalence test needs **16-44 seeds**, not 10. Either widen
the margin, or measure the between-seed sd in Stage 2 and **re-derive K before Stage 4 starts** —
`d_MDE = sqrt(15.7/K)` gives the detectable effect, and the margin must exceed `d_MDE * sd`. Report
the retrospective power alongside any equivalence claim (EXIT-4.8 already demands this; this is the
number it demands).

#### EXIT CRITERIA — Stage 4

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

> **How to report the null honestly.** If `SR(A3) ≈ SR(A4)`, the sentence is: *"At observation level
> O2 the parking task is empirically observation-Markov with respect to the hand-written belief
> statistic: a feedforward policy on (last-seen pose, seen flag) is statistically equivalent to a
> recurrent policy within 3 pp (90% CI on the difference: [x, y]; TOST p = z; K = 10 seeds), and a
> linear probe recovers the hand-written statistic from the GRU's hidden state at R² = w."*
> That is a finding about **the task**, not a failure of the experiment.

---

### 5.5 Stage 5 — Research contribution *(optional)*

Stage 4 establishes that the machinery works. Stage 5 is where a contribution can live. Candidates,
ranked by strength, each with its fair baseline:

| Direction | Why it is defensible | Its fair baseline |
|---|---|---|
| **Degraded perception (O4)** — occlusion, missed detections, association ambiguity | Planning under partial observability needs either intractable belief-space planning or a hand-built filter plus replanning. RL learns a policy on the observation history directly. **Strongest.** | Hand-filter + Hybrid A* replanning each step |
| **Zero-shot generalisation over slot geometry** without replanning | Constant-time inference vs per-scenario search | Hybrid A* re-run per scenario, with its p95/max search time reported |
| **Robustness to model error and actuator latency** | Open-loop plans degrade; a closed-loop policy can absorb it | MPC with the nominal model |
| **Safe RL** — CBF / shielding for a zero-collision guarantee | Addresses the one thing the search baseline has and the policy does not | The unshielded policy, and the planner's guarantee |
| **Sample efficiency of planner-guided RL** | Quantifies what Stage 1's infrastructure actually bought | No-demo SAC at matched wall-clock **and** matched gradient steps |
| **Preference-based fine-tuning (CPL)** — learn the *style* component the programmatic reward cannot express *(added v1.4)* | This task has a **computable ground-truth reward**, so preferences can be synthesised with known provenance and recovery measured exactly — a controlled condition almost no preference-learning paper has. **§5.5.1** | PEBBLE-style PbRL (reward model + SAC), **and** the reward-optimal SAC policy, which it must not degrade |

#### 5.5.1 Preference-based fine-tuning — the shape of the experiment *(added v1.4)*

**Get the name right first.** The family is **preference-based RL (PbRL)** / RLHF for control, not
"trajectory learning". The DPO analogue for control is **CPL (Contrastive Preference Learning)**, and
**CPL, not DPO, is the right object here** — for a reason specific to this plan:

> DPO's Bradley–Terry model is built on **return** and treats the whole output as one bandit action.
> CPL replaces both: preferences are generated by **regret** (a sum of advantages), and it uses the
> maximum-entropy RL identity `A*(s,a) = alpha * log pi*(a|s)` to turn that regret into a sum of
> log-probabilities — yielding a DPO-shaped supervised loss with **no reward model and no RL loop**.
> **A11 already commits this project to SAC, which *is* max-entropy RL.** CPL's derivation sits on the
> framework you have already chosen; DPO's does not.

**Two structural facts before designing anything.**

1. **The determinism dividend.** DPO's bandit reduction is invalid in a stochastic MDP. **EXIT-0.9
   asserts bitwise determinism**, so with a fixed seed the reduction is *exact* here, and a human
   trajectory can be replayed against a policy rollout from a bitwise-identical initial state. Very
   few preference-learning settings have this.
2. **One bit per 400 steps.** A trajectory-level preference is ~1 bit of supervision for 400 actions.
   This, not the loss function, is the binding constraint. Plan the label budget first.

**The one thing that must not be the framing.** Preference learning exists because the reward cannot
be written down. **Here it can** — collision, success, path length and cusp cost (§4.1) are all exactly
computable. Proposing to *learn the reward* invites exactly the objection **A19** raises against
presenting O0 as a result: "why not use the reward you already have?" The target must be the part the
programmatic reward provably does not express — style and margin discipline: *don't shave the
neighbour even when it is geometrically legal; keep the rear neighbour observable; prefer the
manoeuvre a person would recognise.*

**Four arms. P3 runs first and is a gate, not a result.**

| Arm | Content | Role |
|---|---|---|
| **P3** | **Synthetic preferences generated from the known programmatic reward** | **Validity gate — run this before collecting a single human label.** If CPL cannot recover the policy when the preference-generating reward is one you fully control, human preferences never will. Near-zero cost, and it fails fast |
| **P0** | The Stage-2/3 SAC policy | `pi_ref`, and the safety floor everything else is measured against |
| **P1** | CPL fine-tune of `pi_ref`, **zero environment interaction** | the claim |
| **P2** | PEBBLE-style PbRL: learn a reward model, then run SAC | the baseline CPL claims to beat; without it "CPL works" is unfalsifiable |

P3 also converts a vague idea into a falsifiable study: **the sample complexity of preference learning
on a task with a known optimal policy, a known reward, and a known feasibility boundary.** Stages 0–4
build all three. That is the contribution, not "we applied DPO to parking".

**Two traps that will each cost a week.**

> **Trap 1 — tanh saturation.** CPL needs `log pi_theta(a|s)` evaluated on **executed** actions. Full
> lock is the *normal* action in this task, and the tanh-squashed Gaussian's log-density **diverges as
> `|a| -> 1`**. Any pair in which one branch saturates will dominate the loss. **Clip actions to
> `(-1+eps, 1-eps)` before computing log-probs**, `eps = 1e-6`, and assert it. This is the same
> numerical wall EXIT-2.19 documents for `|u| >= 10`, relocated.
>
> **Trap 2 — beta versus safety.** `beta` sets the KL leash to `pi_ref`. **Style preferences have no
> reason whatsoever to preserve safety.** Hard gate, on the §8 frozen set: the preference-tuned policy's
> collision rate must not exceed `pi_ref`'s, in the 10 pp units of EXIT-3.2/3.10. A style win bought
> with collisions is not a result.

**Human teleoperation data — what it is good for, and what it is not.**

A front-end where a person drives the simulated car and the full trajectory is logged is **worth more
than a drawing tool, and it is worth it for a reason that is easy to state**: the human is *in the
loop with the simulator*, so every action is already inside the action box and every transition is
already dynamically feasible. **A15's entire objection — that demonstrations must be executed through
the environment rather than used as raw `(state, action)` pairs — is satisfied by construction.** No
tracking controller, no curvature check, no resampling. Drawn paths need all three (EXIT-1.13).

But **teleoperation yields demonstrations, not preferences.** They are different data types feeding
different machinery:

```
demonstrations  -> replay-buffer seeding (the stated reason A11 chose off-policy SAC),
                   BC pre-training, and pi_ref
preferences     -> CPL / PbRL   -- and these need PAIRWISE LABELS, which a single
                   human trajectory does not contain
```

Three uses, ranked:

1. **Pairing, which is where the value actually is.** Replay a human trajectory against a planner path
   or a policy rollout **from a bitwise-identical initial state** (EXIT-0.9) and label the pair. That
   is exactly CPL's `(x, y_w, y_l)` with `x` = the scenario seed. Cross-pairing multiplies a small
   human corpus by the whole planner/policy corpus; within-corpus pairing alone does not
   (30 scenarios x 5 human runs = only 300 dependent pairs, against the 10^3–10^4 CPL wants).
2. **A measurable definition of "human-like".** Behaviour-clone the human data and report the RL
   policy's likelihood under it. That converts "style" from hand-waving into a number, which is the
   thing the programmatic reward cannot supply.
3. **Negatives that actually carry information.** Human failures are near-misses and *wrong-strategy*
   failures — started the manoeuvre two metres late, took three cuts where one fits. These are the
   informative negatives; a deliberately-drawn crash is not, because the programmatic reward already
   knows about crashes.

A fourth, nearly free: a **human contour** overlaid on §5.4's success-rate surface, alongside the
oracle boundary and the §5.0(c') containment bound. "Where does a person fail?" is a cheap and strong
figure, and it costs one extra pass over data collected anyway.

> **Three teleoperation traps.**
>
> **(a) Reaction time is a hidden POMDP.** A human's ~250 ms latency against `dt_policy = 0.1 s` means
> the logged action is a response to `s_{t-2.5}`, not `s_t`. Behaviour-clone that and **you clone the
> lag**. This is mathematically **A23** (latency requires state augmentation), arriving from a
> different direction. Fix by **time-dilating the game: 1 simulated second >= 4 wall-clock seconds**,
> which puts the residual lag under one policy step — then **measure** it rather than assume it
> (EXIT-1.14), because dilation that is too aggressive changes how people drive.
>
> **(b) The player sees the whole screen, which is O0.** Data collected with full map visibility and
> then used to train or anchor an O2/O3 policy is **privileged information** in exactly the sense
> §6.5 warns about. Either restrict the player's view to the rung being studied, or label the corpus
> **O0-only** and never let it touch an O2+ arm.
>
> **(c) Log `WorldState`, not frames, at the policy rate, post-clamp.** Video is not a demonstration.
> The log must be the Stage-0 `WorldState` plus the pre-scaling `Box(-1,1)` action, so that a replay
> is bitwise (EXIT-1.14). Logging the *requested* action instead of the *clamped* one silently teaches
> the policy that actions outside the box exist.

**Prerequisites, and where each lands.**

| What | Stage | Note |
|---|---|---|
| Drawn-path trackability probe | **Stage 1**, do it early | **EXIT-1.13** — 1–2 days, kills the drawing idea cheaply if it is going to die |
| Teleoperation front end + logging | Stage 1 | `render.py` (Stage 0) already has trajectory replay; this is input handling plus a logger. **EXIT-1.14** |
| Exact `log pi_theta(a\|s)` with the tanh Jacobian | Stage 2 | free — **EXIT-2.17/2.18/2.19 already test it** |
| `pi_ref`, frozen eval set, the metric set | Stage 2–4 | free |

**And the cost, stated plainly.** §5.5 is the *contribution slot* and Stage 4 already costs ~860
GPU-hours (§5.4.1). This direction is **not additive with the O3/memory comparison** — pick one as the
thesis contribution. The one candidate it *does* compose with is **"Sample efficiency of
planner-guided RL"**, which shares the demonstration pipeline, `pi_ref`, and the matched-budget
controls; if you want both, merge them into one experiment rather than running them side by side.

**What RL cannot claim here — write this in the thesis.** Do not claim shorter paths on a known
static map (expect ρ > 1 and report it). Do not claim safety (the search baseline returns a
collision-checked path; the policy returns nothing of the kind). Do not claim efficiency (training
costs orders of magnitude more compute than planning). And do not present the classical baselines as
strawmen — build them properly, which is what Stage 1 is for.

---

## 6. The observation ladder (orthogonal to stages)

### 6.1 The ladder

| Rung | Content | Lands in | Expected result / gate |
|---|---|---|---|
| **O0** | Full state, ego frame, fixed semantic slots, no mask | Stage 2 | The teacher policy. Success ≥ 0.90 |
| **O1** | Observation-domain randomisation: pose noise, delay, dropout (`p: 0→0.1→0.3`), goal-pose noise | Stage 3 | Success drop ≤ 10 pp. Nearly free, and it makes the O2 transfer smooth |
| **O2** | **Limited field of view** — rear invisible while reversing | Stage 3 end | **The first rung that actually bites.** The reactive MLP *must* degrade measurably (EXIT-3.11) |
| **O2a** | **Range-limited 360° sensor at R ≈ 6–7 m** (added in v1.1; see §6.2) | Stage 3 end | Gated on measured bite, same standard as O2 |
| **O3** | Memory-architecture comparison (five arms) | Stage 4 | The headline experiment |
| **O4** | Occlusion + missed detections + association ambiguity + slow-moving obstacles | Stage 5 | Where the hand filter starts to fail — i.e. where the GRU earns its keep |

**Two things v1.0 left unstated. Both change what the central hypothesis means; decide them now.**

**(a) Are the rungs cumulative or independent configurations?** §6.1 reads as a ladder ("O1 makes the
O2 transfer smooth"); §5.4's H_A reads as independent ("O2 … noise-free"). **The central claim is
true under one reading and false under the other**: if O2 inherits O1's pose noise, precondition (ii)
fails and "last observed pose" is provably beaten by a running mean. **Decision: the rungs are
independent configurations.** O2 runs noise-free. O1 is a separate robustness result. Asserted by
**EXIT-6.3**, which mirrors EXIT-4.11's ban on dynamics randomisation during O3.

**(b) Is the goal-slot object subject to the O2 FOV mask?** This single unspecified bit determines
three things: whether the ego is permanently localised against a fixed anchor; whether arm A4 faces a
dead-reckoning burden that A3 does not (§5.4); and **whether O2 bites at all**. If the slot is exempt
and the generator places both neighbours at near-fixed offsets from it, the instantaneous observation
nearly determines the whole scene and EXIT-3.11 cannot pass. **Decision: the goal slot IS subject to
the mask at O2 and above**, so that the FOV rung has something to remove. If you exempt it instead,
EXIT-3.11 must be run *before* committing to the arm design.

### 6.2 Deliberately excluded

- ~~**A 360°, unlimited-FOV, radius-R sensor as a standalone rung.**~~ **v1.1: this exclusion was
  wrong and is withdrawn.** v1.0 argued that "both neighbours are within a few metres by the time you
  are manoeuvring", so a radius sensor would show ~zero drop. Computing the actual reference geometry
  refutes it. With the slot at `x ∈ [0, Ls]`, the rear neighbour at `x ∈ [−4.7, 0]`, the ego in the
  driving lane at offset `Δ = w + c_lat` and its rear axle just past the slot's front edge (a
  standard start), the distance from the ego **rear axle** to the feature that actually governs the
  manoeuvre — the rear neighbour's *front face*, the thing you must not hit while backing in — is:

  ```
  Ls = 5.5 m, c_lat = 0.5 : 6.17 m       (from a rear-bumper sensor: 5.07 m)
  Ls = 6.0 m, c_lat = 0.5 : 6.65 m
  Ls = 6.5 m, c_lat = 0.5 : 7.14 m
  the rear neighbour's REAR corner sits at 10.79 - 11.86 m
  ```

  So **R = 6 m hides the rear neighbour entirely at the start of the manoeuvre; R = 8 m hides its
  full extent; only R ≥ 12 m is genuinely non-binding.** The phrase "by the time you are
  manoeuvring" was carrying the whole argument, and it is true at the *end* of the manoeuvre and
  false at the *start* — which is where the plan commits and where the rear car's clearance decides
  feasibility. A range-limited 360° sensor at **R ∈ [5, 8] m** therefore forces exactly the memory
  requirement the ladder exists to probe: see the rear car, drive past it, lose it, reverse into it
  from memory.

  **Revised decision:** include it as rung **O2a** at R ≈ 6–7 m, gated on measured bite exactly as
  EXIT-3.11 gates the FOV rung. Excluding a rung by *prediction* while gating another by
  *measurement* is an inconsistent evidentiary standard. (Note the success surface in §5.4 sweeps
  initial lateral offset, so initial distances vary across precisely the cells where a radius limit
  bites hardest.)
- **Occupancy grids.** They force a CNN, and the resolution argument usually made for them is
  confused: ego and goal pose stay in the **low-dimensional vector part** at full float precision, so
  the grid only needs to encode obstacle *geometry*, where 10–20 cm is plenty. Vector → masked set is
  simpler and sufficient. Revisit only if the research question becomes "learn from raster perception
  output," which is a different project.
- **Frame stacking as a candidate.** It appears only as arm A2, explicitly labelled a negative control.

### 6.3 Encoding rules

**"Unknown ≠ free."** Zero-padding an unobserved object is ambiguous with "a small object at the
origin." Correct encodings: explicit `valid` + `visible_now` bits **consumed by a masked set
encoder**; or three-state free/occupied/unknown for grids.

**A mask bolted onto a flat MLP is decorative.** An MLP does not know what a mask is — it sees zeros,
which is exactly the "unknown = free" trap. A mask works only if the architecture consumes it via
masked pooling. For the fixed-slot MVP (two obstacles, always present) this never arises. When it
does arise, that is the signal to move to Deep Sets / attention.

**Do not "stably sort by distance to ego."** As the car moves, the order **flips discontinuously**
when two obstacles are equidistant — injecting discontinuities into an observation whose underlying
state is varying smoothly. This produces an intermittent, hard-to-reproduce instability. Safe
alternatives: **fixed semantic slots** (MVP), or **permutation-invariant set encoding** (variable N).
Avoid the middle option — a stably-sorted padded list — precisely because it looks fine.

**Sensor modelling.** Visibility is computed from the **sensor position**, not the body centre; the
ego body **self-occludes** (a rear sensor cannot see forward). Occlusion is ray-based against the
obstacle rectangles.

### 6.4 The O3 hypothesis, stated precisely

**Claim.** For obstacles that are (i) static, (ii) observed without noise, and (iii) with known data
association, the map

```
b_t = { for each object j:  (last observed pose q_j, seen_j) }
```

is an **exact belief** — the posterior over each object's pose is a point mass at its last
observation, and nothing further can be learned or forgotten. By the belief-MDP sufficiency theorem
(Åström 1965; Kaelbling, Littman & Cassandra 1998), the POMDP reduces to a fully-observable MDP over
`b_t`, so a **feedforward** policy on `b_t` can be optimal and a recurrent policy can at best tie it.

**The theorem, stated properly** (v1.0 stated three preconditions where six are needed):

> For a POMDP with **known** `T, Z, R` and a **known initial belief** `b₀`, the belief
> `b_t(s) = P(s_t = s | b₀, a₀, o₁, …, a_{t−1}, o_t)`, updated by `b′ = SE(b,a,o)` via Bayes, is a
> sufficient statistic for the history. The induced belief MDP is Markov, and for bounded `R` and
> `γ < 1` an optimal stationary deterministic `π*: B → A` exists and is optimal for the POMDP.

Three preconditions v1.0 omitted, two of which are load-bearing here:

**(iv) The model must be known.** The belief recursion is model-dependent — which is exactly why
EXIT-4.11's ban on dynamics randomisation during O3 is load-bearing. v1.0 never connected them.

**(v) `b₀` must be known and fixed.** Here `b₀` is the scenario generator's prior. It is fixed across
episodes, so a feedforward net can absorb it into its weights — *but only if it never has to be
updated within an episode.* See (vii).

**(vi) The belief must cover the *entire* hidden state.** `b_t` as written covers only obstacle
poses. It omits the ego state `(x,y,θ,v,δ)` and the object extents `(l,w)`, both of which are part
of the hidden state and both of which appear in the per-object feature vector.

**(vii) — THE REAL HOLE — objects never yet seen.** For an unseen object the belief is the **prior**,
not a point mass. With a deterministic FOV and no missed detections, *non-detection is conclusive
negative evidence*: the exact belief for an unseen object is the prior **truncated to the region not
yet swept by the sensor** — a history-dependent statistic of unbounded complexity that a fixed-width
per-object feature vector **provably cannot represent**. Whether this bites turns on whether every
object is visible at `t = 0`, which v1.0 neither stated nor gated — and which the reverse curriculum
of §5.3 actively breaks by sampling start states anywhere along the reference path.
**→ new gate EXIT-6.2.**

**Active information gathering does *not* break the argument** (v1.0 left this implicit). In a POMDP
the optimal policy may act purely to reduce uncertainty; a feedforward policy on an *exact* belief
can do this, because the belief MDP is Markov and admits a stationary deterministic optimum.

**Refinement (A21) — right about τ, wrong about what it means.** Under (i)–(iii), `τ_since_seen` is
genuinely **redundant** for the state posterior: the object has not moved, so staleness carries no
information about its pose. But τ is **an episode-clock proxy** — for an object that leaves view at
step k, `τ = t − k` — and §5.2 normalises it by `log1p(400)`, i.e. by `max_steps`. Consequences:

- **This contradicts §5.2's written commitment to a time-unaware observation.** See the boxed
  resolution in §5.2.
- **H_B's inference is therefore unsound as v1.0 stated it.** "If τ helps, the static-world
  assumption is violated" has at least three competing explanations: τ is a clock, and the reported
  metric is *success within 400 steps* — a finite-horizon objective whose optimum is non-stationary,
  with `γ⁴⁰⁰ = 0.1347` of the discounted weight beyond the cut and §5.3(e)'s succeed-versus-stall
  margin already labelled MARGINAL at N = 400. **A GRU can learn a clock; an MLP on `b_t` cannot.**
  This is a legitimate route by which A4 beats A3 with every word of the theory intact.
- Restate H_B as: *"if τ helps at O2, the cause is one of {static-world violated, finite-horizon
  clock, exploration}, and the τ-zeroed control (EXIT-6.1) distinguishes the first from the rest."*

**Which broken precondition makes learned memory necessary** — this list *is* the O4 experiment design:

| Broken precondition | Why the hand filter fails | Rung |
|---|---|---|
| **Objects never yet seen** | The belief is the prior truncated to the unswept region — unbounded complexity, not representable in a fixed-width vector | **O2** ← *not O4* |
| Obstacles move | The point mass must be propagated by an unknown motion model | O4 |
| Measurement noise | The belief is a distribution, not a point; needs accumulation (Kalman-like) | O4 |
| Missed detections | Absence of evidence must be distinguished from evidence of absence | O4 |
| False positives | Requires a track-confirmation policy | O4 |
| Association ambiguity | Which measurement belongs to which object becomes a latent variable | O4 |
| Unknown obstacle count | The state space of the filter is itself uncertain | O4 |
| **Ego self-localisation uncertain** | A8 says the slot is detected with noise at O4, so the agent's own pose relative to the goal becomes a belief and the reward's goal-frame error is no longer observable. **Probably the largest O4 effect**, and v1.0 omitted it | **O4** |
| **Unknown dynamics parameters** | The agent must implicitly system-identify — EXIT-4.11 already names this as "a second, unrelated reason", which is exactly a broken precondition of the same kind | O4 |

**The hand filter's failure conditions define the experiment.** That symmetry is what makes this a
research question rather than a benchmark run.

> **The never-seen-object row changes the framing of O2.** O2 is *not* cleanly "exact belief, memory
> unnecessary" unless every valid object is visible at `t = 0`. Either enforce that (EXIT-6.2) and
> keep the clean claim, or accept it and state that the exact-belief argument holds only on the
> sub-distribution of episodes where it does.

### 6.5 Privileged training — the caveat and the better route

Asymmetric actor-critic (actor sees `o_t`, critic sees `s_t`) is sound and well-established, **but it
is biased.**

> **v1.1 correction — the conclusion was right, the mechanism was wrong.** v1.0 said "`V(s)` under
> full observability is an upper bound on what a partially-observed actor can achieve, so advantages
> blame the actor for information it never had." That is not the published defect. The critic in
> asymmetric AC estimates the value of *the actor's own history-dependent policy evaluated from a
> state*, `V^π(s)` — **not** the fully-observable optimum `V*(s)`. `V*(s) ≥ V*(h)` is true but is not
> what asymmetric AC computes.
>
> **The actual defect** (Baisero & Amato, "Unbiased Asymmetric Reinforcement Learning under Partial
> Observability", AAMAS 2022, arXiv:2105.11674) is *ill-definedness* plus a *sign-indefinite* bias:
> their Thm 4.1 — "in partially observable control problems, a time-invariant state value function
> `V^π(s)` is generally ill-defined"; Thm 4.2 — "even when well-defined, `V^π(s)` is generally a
> biased estimate of `V^π(h)`", because the state alone does not determine the agent's future
> behaviour, which depends on the history. Their Thm 5.1 establishes that a **history-state critic
> `V(h,s)`** is unbiased.

Cleaner formulations, in order of preference:

1. **Teacher–student distillation.** Train a full-state teacher to convergence, then distil into a
   partial-observation student with on-policy student rollouts (DAgger). Usually more reliable than
   joint asymmetric training, and it **fits this plan perfectly — Stage 2 produces the teacher for
   free.** `[V]` Chen, Zhou, Koltun & Krähenbühl, "Learning by Cheating," CoRL 2019, PMLR 100:66-75;
   `[?]` Lee et al., *Science Robotics* 2020; `[?]` Ross, Gordon & Bagnell (DAgger), AISTATS 2011.
2. **Critic sees state *plus* the actor's hidden state / history** — this is **exactly Baisero &
   Amato's proposed fix** `V(h,s)`, not an unattributed suggestion as v1.0 presented it.
3. **Plain asymmetric critic** (arm A5) — keep it because it changes only one thing, which is what
   makes it the comparable arm. But report it as *biased by construction*, citing the theorems above.

### 6.6 EXIT CRITERIA — the observation ladder

*Added in v1.1. §6 was the least-gated section of a document whose stated principle is that every
criterion is a number checkable by a script: its "expected result" column contained predictions
("nearly free", "~zero performance drop") tied to no assertion anywhere.*

| ID | Criterion | Threshold |
|---|---|---|
| **EXIT-6.1** | The τ slot is held at 0.0 except in the one arm that studies it | Config exposes a **required, non-defaulted** boolean `tau_enabled`. Assert `tau_enabled == False` for every O0/O1/O2 run **and for arms A1–A5**; assert `obs[τ_idx] == 0.0` bitwise over 10⁴ observations whenever `tau_enabled == False`; assert `tau_enabled == True` for **exactly** the H_B ablation arm, recorded in that run's metadata; assert the H_B arm and its control differ in no other config key. Threshold: 100% of observations, 100% of runs. *v1.1 asserted τ ≡ 0 at O2 with no exception — but **H_B is literally defined as "at O2, adding τ to A3's features"**, so the criterion forbade the observation its own pre-registered hypothesis exists to test. It would have been silently disabled (destroying the O0/O2 protection) or the ablation quietly dropped.* |
| **EXIT-6.2** | The at-`t=0` visibility fraction is **measured**, reported, and above a floor | Over 5000 resets at each `sigma_max` **and each sensor configuration used by any O3 arm**, compute `f_vis = P(all valid objects visible at t=0)` with a Wilson 95% interval; record it in run metadata; assert the H_A comparison is computed on the `f_vis` sub-population and that **both** conditional and unconditional rates are printed. **Hard gate: `f_vis ≥ 0.50`.** *v1.1 demanded `f_vis == 1.00`, which is **mutually exclusive with EXIT-6.4** — §6.2's own geometry shows R ∈ [5,8] m hides the rear neighbour at the standard start, and §6.4 itself notes the reverse curriculum "actively breaks" t=0 visibility. v1.1 then attached an opt-out clause, so the criterion **could never fail**. 0.50 is where the conditional claim stops describing the modal episode; anything stricter is incompatible with a rung the document has independently decided to include.* |
| **EXIT-6.3** | Observation noise is OFF during O3 | programmatic assertion mirroring EXIT-4.11: `observation_randomisation_enabled == False` and `pose_noise_sigma == 0` for every arm. *Pose noise breaks precondition (ii) directly and would make A3's "last observed pose" provably worse than a running mean — the cheapest missing gate in the whole ladder* |
| **EXIT-6.4** | The O2a radius rung bites, or is excluded by measurement | at R ∈ {5, 6, 7, 8, 12} m, the reactive MLP's success rate is recorded. Include the rung at the smallest R whose drop exceeds the EXIT-3.11 threshold; if no R < 12 m produces a drop, exclude it **and report the sweep** |
| **EXIT-6.5** | Goal-slot masking is explicit and asserted | the config exposes `goal_subject_to_fov` as a required (non-defaulted) boolean, and its value is recorded in every run's metadata. A run whose metadata lacks it fails to load |

---

## 7. Reward specification

### 7.1 The potential (goal/slot frame, rear-axle reference)

```
[dx; dy] = Rot(-theta_g) * ( [x; y] - [x_g; y_g] )
cos_dth  = cos(theta) cos(theta_g) + sin(theta) sin(theta_g)          # no wrapping needed
sin_dth  = sin(theta) cos(theta_g) - cos(theta) sin(theta_g)

Phi(s) = -K * (  w_x  dx^2
               + w_y  dy^2
               + w_th (1 - cos_dth)
               + w_v  v^2
               + w_d  delta^2
               + w_c  sum_{j=1..3} sum_k max(0, d_safe - dist(circle_j, obstacle_k))^2 )

Phi(s) := 0  for every TERMINAL s.       (NOT for truncation -- see below.)
```

Every quantity is read from the true `WorldState`.

**Why each term is legal inside Φ:** `dx, dy, θ` are state; `v` is state, so putting "come to rest"
here instead of in a running cost keeps it policy-invariant; `δ` is state, so "return the wheel to
centre" is free and invariant; clearance is a pure function of `(x,y,θ)` and the *static* obstacles
(this is where assumption **A4** is load-bearing — it breaks at O4 with moving obstacles).

> **The clearance term must be inside Φ, not a running cost.** A running safety-margin cost is a
> **permanent tax on the only successful behaviour**: the slot is narrow, so entering it necessarily
> incurs proximity cost, and the agent's cleanest way to maximise return becomes hovering in the open
> road. The symptom is an agent that approaches confidently, stops 1–2 m short, and holds station.

> **PBRS under partial observability — v1.0 never took this step.** From O2 onward the agent is
> solving a POMDP, while Ng, Harada & Russell's theorem is stated for MDPs, and Φ reads hidden state
> the agent cannot compute. **The extension does hold**, via the induced belief potential: the shaped
> belief-MDP reward is `ρ′(b,a) = ρ(b,a) + γ·E_{b′}[Φ] − E_b[Φ]`, which is exactly potential-based
> shaping on the belief MDP with `Φ̄(b) = E_b[Φ(s)]`, and the telescoping survives by the tower
> property because `b′` is the posterior. **But the realised per-transition shaping uses `Φ(s)`, not
> `Φ̄(b)`** — so invariance carries over and *variance does not*: it adds zero-mean noise to the
> critic's regression target. State both facts in the thesis; an examiner will otherwise notice that
> an MDP theorem is being invoked inside a document whose headline experiment is about partial
> observability. Note also that A4 is load-bearing for the clearance term for the same reason.

**Truncation is not termination here either.** On `truncated = 1` do **not** apply the terminal form:
bootstrap the value *and* use the real `Φ(s_{t+1})`. Zeroing Φ at truncation injects a fictitious
`−Φ(s_400)` into the return at the time limit.

### 7.2 Weight calibration

Match weights **at the tolerances**, not at typical start states:

```
USING THE v1.2 HEADING TERM  w_th (1 - cos(dth/2)):
    small-angle expansion is (w_th/8) dth^2, so matching at the tolerance gives
    w_th = 8 w_y (dy_c/dth_c)^2 = 8 * 1.0 * (0.10/0.08727)^2 = 10.50        <- 4x the v1.1 value
    (v1.1 printed 2.63, which is correct only for the OLD 1 - cos(dth) form that has a
     zero-gradient plateau at 180 deg. See 7.3 Defect 3. Saturation bound is now w_th * 1 = 10.50.)
    w_x  =   w_y (dy_c/dx_c)^2  = 1.0 * (0.10/0.20)^2        = 0.25
    w_v  =   w_y (dy_c/dv_c)^2  = 4.0   -> reduce to ~0.3 in practice (v^2 dominates the far field)
    w_d  = 0.3

GLOBAL SCALE. Fix R_success = 100 as the numeraire. Choose the single multiplier K so that
    p95 over the HARDEST initial distribution of |Phi(s_0)| = 0.20 * R_success = 20.
Clip Phi at -30. Calibrate ONCE, on the hardest distribution, then FREEZE.
```

**Do not recalibrate per curriculum stage** — the curriculum moves the state distribution, and a Φ
rescaled per stage is a *different reward function per stage*. If you must change Φ mid-run, use the
Devlin–Kudenko **dynamic** form `F = γΦ(s′,t′) − Φ(s,t)`, which is the only version that stays
provably invariant.

**Calibrate against the Stage-1 planner, not against intuition.** Run the expert through the
environment on the frozen set and record its per-term reward decomposition. Require that on the
expert trajectory each non-terminal term's `|sum|` ≤ 0.10·`R_success` and their total ≤ 0.30·`R_success`.

### 7.3 Two structural defects of a quadratic potential

**Defect 1 — unbounded far field.** `Φ = −K e²` grows quadratically, so on distant starts `|Φ(s₀)|`
can exceed `R_success` and the shaping swamps the terminal signal in the critic's output range.
(Harmless to the *optimum* by the theorem; harmful to the *function approximator*.)
**Fix:** pseudo-Huber `Φ = −K c²(sqrt(1 + (e/c)²) − 1)`, still a pure state function hence still exact
PBRS. Or clip — not smooth, but still a state function. Clip **before** the F difference, never after.

**Defect 2 — vanishing near-field gradient.** `d/de(−K e²) = −2Ke → 0`. At e = 0.1 with a per-step
displacement of ~0.01 m the shaping signal is ~1e-3·K, below the critic's noise floor: **the final
centimetres are effectively unshaped.** Pseudo-Huber does **not** fix this (it is also quadratic near 0).
**Fix (legal):** a cone potential `Φ = −K sqrt(e² + ε²)` with ε at the final tolerance scale —
near-constant gradient down to ε, and still exact PBRS.
**Fix (illegal, do not):** a non-potential bonus for being near the goal. It is farmable by hovering
just outside the tolerance and it destroys invariance. Whatever you do to the near field, **keep it
inside Φ.**

**Defect 3 — a gradient plateau at 180° of heading error.** `d/dΔθ (1 − cos Δθ) = sin Δθ` vanishes
at `Δθ = π`, an unstable equilibrium that the **reverse-bay start distribution sits on**. Same
pathology as Defect 2, in the far field rather than the near field.
**Fix — use `1 − cos(Δθ/2)`, and only this.** Zero gradient only at `Δθ = 2π`, i.e. nowhere
reachable; monotone on `(−π, π)`; still a pure state function, so still exact PBRS.

> **v1.2 correction — v1.1 offered a second "fix" that was mathematically wrong.** v1.1 suggested
> adding a `(1 − cos Δθ)^(1/2)` term "which has non-zero slope at π". It does not:
> `sqrt(1 − cos x) = √2·|sin(x/2)|`, so `d/dx = (√2/2)·cos(x/2)`, which is **exactly zero at x = π**
> (numerically 1.8e-7). The sqrt form has slope `√2/2` at `x = 0` — it is a fix for **Defect 2**, the
> near field, not for the 180° plateau. v1.1 had the two defects' fixes crossed. Anyone who took that
> option would have implemented a term provably flat at exactly the heading error where reverse bay
> parking starts.

**Re-derive the §7.2 weight matching**: the small-angle expansion of `1 − cos(Δθ/2)` is `Δθ²/8`, not
`Δθ²/2`, so **`w_th` is 4× larger** — see the updated numbers in §7.2. The saturation bound also
changes: `1 − cos(Δθ/2) ≤ 1` (not 2) at `Δθ = π`, but with `w_th` 4× larger the heading contribution
to `|Φ(s₀)|` is `w_th·1 = 10.50`, not 5.25.

**Add to the Stage-0 tests:** assert `|dΦ_heading/dΔθ| > 0.1` for **all** `Δθ ∈ (0, π]` under
whichever form is adopted. That single assertion catches both this class of error and any future
"improvement" that reintroduces a plateau.

### 7.4 Non-potential terms and the farmability rule

A running term `g` is **farmable** iff some reachable cycle has `Σ γⁱ g(sᵢ,aᵢ,sᵢ₊₁) > 0`.

> **DESIGN RULE (non-positive running reward invariant).** Every non-terminal reward term other than
> the PBRS term is **≤ 0**, and the **only positive rewards in the entire MDP are terminal.** Then no
> cycle can pay, for any γ.

Note that for a car with `(a_long, δ̇)` actions, closed cycles in the full state are trivially
realisable (constant v, constant δ = a circle), so this is not hypothetical. Check farmability by
**integrating around a cycle**, not by inspecting the sign at one state.

| Term | Legality | Note |
|---|---|---|
| `−w_a (a_long/a_max)²` | legal | function of a |
| `−w_s (δ̇/δ̇_max)²` | legal | function of a |
| `−w_gear · 1[sign(v_t) ≠ sign(v_{t+1})]` | legal | `R(s,a,s′)` is a function of the (s,s′) pair by definition — no augmentation needed. Use 0.05 m/s hysteresis or chattering at v≈0 generates phantom counts |
| `−w_time` | legal | |
| `−w_rate ‖u_t − u_{t−1}‖²` | **ILLEGAL without augmentation** | depends on `u_{t−1}`, not in the state. The process is no longer an MDP and the SAC target is biased by state aliasing. Either augment `WorldState` with the previous action **and expose it in the observation**, or drop the term |
| `+w · min(clearance, d_max)` per step | **FORBIDDEN** | farmable: drive circles in open road forever, worth `200·w·d_max` at γ=0.995 |
| `+w` alive bonus | **FORBIDDEN** | farmable, worth 200w |
| `+w · 1[inside slot]` | **FORBIDDEN** | park badly and sit there |

**Gear-change weight must be budgeted against the number of cusps the task actually requires.**
Parallel parking provably requires at least one reversal; a typical RS solution has 1–4 cusps. Set
`w_gear ≤ 0.05·R_success / n_cusps_typical`, i.e. ≲ 1.0 for n = 4. Too large and the agent refuses to
reverse, which makes the task infeasible.

**Terminal bonuses may be graded.** `R_success(1 + β·g(final error))` with `g ∈ [0,1]` gives a
gradient inside the tolerance region and is unfarmable because it is terminal. But discounting rewards
**early** collection, so without the settle window the agent triggers it at the loose edge of the
tolerance the instant it can. **Settle window first, graded bonus second.**

**Size `d_safe` from the expert path, not from intuition.** Compute the minimum clearance along the
Stage-1 reference path for the *tightest* slot in the curriculum, and set `d_safe ≤ 0.5×` that value.
Then the clearance term is exactly zero along any reasonable trajectory and fires only on genuinely
dangerous ones. Starting guess 0.10 m — verify, do not assume.

### 7.5 Success test

```
SUCCESS (evaluated on TRUE WorldState only):
    |dx| <= eps_x  AND  |dy| <= eps_y  AND  |dtheta| <= eps_th  AND  |v| <= eps_v
    AND no collision (exact SAT)
    AND all of the above has held for K_settle = 5 CONSECUTIVE policy steps (0.5 s)
```

The settle window is not cosmetic. Without it the agent (i) flies through the goal at 1.5 m/s and
claims success on one frame, and (ii) triggers the bonus at the loose edge of the band as early as
possible, because discounting rewards early collection.

### 7.6 Store components, not the scalar

Persist a small named struct per transition (`phi_s`, `phi_s_next`, `terminal_kind`, `time_cost_raw`,
`action_cost_raw`, `gear_flag`, `clearance_penetration`, `settle_counter`) and **recompose the scalar
at sample time** from the current weights. This makes four otherwise painful things cheap: reweighting
without invalidating the buffer; the per-term reward-hacking diagnostics; Devlin–Kudenko dynamic
potentials across curriculum phases; and post-hoc analysis of which term dominated on the episodes
that collided.

---

## 8. Evaluation protocol (frozen at Stage 2, executed at Stage 4)

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

**Terminal classification must be mutually exclusive and exhaustive, evaluated on truth, checked at
every substep, first match wins:** `COLLISION > OUT_OF_BOUNDS > SUCCESS > TIMEOUT`.

**Report percentiles, not means, for every continuous metric.** Conditioned on success, the
final-pose-error distribution is bounded below by 0 and above by the tolerance, so it is strongly
right-skewed and truncated; its mean is dominated by the bulk and says nothing about the marginal
cases — which are exactly the ones that decide whether the result survives a tighter tolerance.

---

## 9. Failure-mode diagnostic table

Each row: what you will *see* before you know the cause.

| Symptom | Likely cause | Fix / test |
|---|---|---|
| Success rate plateaus below the Hybrid A* ceiling; agent seems "less committed" late in episodes; **only the hardest (longest) starts fail** | Truncation treated as termination | EXIT-2.5 |
| Measured entropy drifts monotonically away from −2.0; α collapses < 1e-4 or explodes; later NaN | tanh log-prob correction missing / sign-flipped / naive form | EXIT-2.17/18/19 |
| Car drives smoothly to just outside the slot, then oscillates or creeps forever. Success ≈ 0 | γ too low (0.99) — terminal bonus discounted to 1.8 vs a shaping stream worth up to 98 | γ = 0.995; EXIT-2.11 |
| Slower, much noisier learning; large seed variance; critic loss stays high | γ too high (0.998) — `H_eff = 500 > max_steps = 400` | keep `H_eff` ≲ `max_steps/2` |
| Return climbs steadily and impressively; success flat at zero; episode length saturates at 400; path/RS ratio explodes; video shows something rhythmic and pointless | A positive sustainable per-step term is being farmed | non-positive running reward invariant; EXIT-3.9 |
| Higher-than-expected collision rate appearing mid-training and not going away; agent gives up on hard starts and drives into things; return curves look fine | γ dropped from the shaping term → hidden running cost `0.005025·Φ` up to 0.151/step | EXIT-2.6 + EXIT-2.23 |
| Collision rate rises steadily **while return also rises**; the agent drives purposefully into the nearest parked car | Collision penalty sized against per-step rather than **accumulated discounted** cost | EXIT-2.7 |
| Agent approaches confidently, stops 1–2 m short, holds station. Success ≈ 0, collisions ≈ 0 | Safety-margin term is a running cost — a permanent tax on the only successful behaviour | move it inside Φ |
| Flat-zero success with smoothly decreasing pose error; end-of-episode error histogram piles up just outside the tolerance | Hard tolerance, no annealing, no settle window | §5.3 annealing |
| Success rises, then **collapses abruptly at a schedule boundary** and never recovers | Curriculum annealed on step count instead of measured success rate | gate on SR; implement the decrease branch |
| Curriculum-stage success looks excellent; frozen-set success is far lower and does not track it; policy behaves like an open-loop replay | Reverse-curriculum states lie exactly on the reference path, and/or `δ₀` leaks the path curvature | EXIT-3.3 / 3.4 |
| Critic will not converge on states where the agent reverses; large persistent gap between `V(s₀)` and the empirical return | Action-rate penalty added without augmenting the state → reward is a function of history | §7.4 |
| Actor loss → −∞; `max\|Q\|` crosses ~300 and keeps climbing; NaN | Deadly-triad divergence | EXIT-2.28; then the ordered fix list: truncation bootstrap → tanh log-prob → normalisation → replay ratio 1 → critic LayerNorm → smaller τ |
| Return curve flat and noisy; car drives in random directions indefinitely | Action detached before entering the critic in the actor loss | EXIT-2.20 |
| Everything is 5× too large; `\|V\|` runs to 1000+ | Reward summed over substeps | EXIT-2.13 |
| Checkpoint scores well in training and near-randomly in a fresh process | VecNormalize statistics not saved with the model | use fixed analytic scaling (§5.2) |
| Performance collapses **the moment O2 is switched on** | Binary flags were being normalised; latent at O0 where `visible_now ≡ 1` | mask them, or use fixed scaling |
| BC loss will not go below a floor; cloned policy undershoots turns | RS path samples used directly as (state, action) demos | A15; EXIT-3.7 |
| Fast initial improvement then a hard plateau at the demonstrator's level | Primacy bias from a 100%-demo buffer | RLPD symmetric sampling; Q-filter |
| Every agent, including the Stage-1 tracker, shows ρ > 1 that never improves | `ell_RS` used as the denominator — it is an **infeasible** lower bound | report `ratio_floor`; EXIT-1.11 |
| Forward segments track well; the moment the car reverses, cross-track error grows smoothly and it jackknifes | Stanley used in reverse (front-axle law, wrong feedback sign) | rear-axle pure pursuit |
| Steering command is a visible triangle wave riding against the `δ̇` clamp; the car weaves | Pure-pursuit lookahead sized from speed, ignoring the **rate** limit | `ell_min > v·Δδ/δ̇_max` |
| Hybrid A* suddenly much faster, paths longer and oddly angled, RL optimality ratio mysteriously improves | `h_nhwo` table built with an inflated turning radius → heuristic inadmissible → greedy search | EXIT-1.6 |
| Planning suspiciously fast, ~100% success including on infeasible scenarios, occasional path straight through a parked car | Analytic RS expansion not collision-checked | EXIT-1.7 |
| Success degrades under Stage-3 randomisation in a way uncorrelated with observation noise | Cusp cost rose: `δ̇_max` lowered, `δ_max` raised, `a_max` **raised**, or `v_max` **lowered**. *(v1.1's "knife edge" framing was withdrawn — see §4.1)* | §4.1 |
| Minimum-clearance metric is negative on **successful** episodes (logically impossible) | 3-circle proxy reported as the clearance metric (0.2871 m over-estimate) | EXIT-2.8 |
| Reported clearances systematically slightly too small, worst when nosing diagonally into a bay corner | SAT face-normal gap used as the separation distance (vertex–vertex case) | EXIT-0.4 |
| A perfect arm reports "100.0% ± 0.0%"; a zero-collision arm reports "0.0% ± 0.0%" | Wald interval | Wilson / Clopper–Pearson |
| Every arm's IQM is exactly 1.000 with a zero-width CI | IQM applied to raw binary outcomes instead of per-run rates | §5.4 |
| A 4 pp ordering flips when a fourth seed lands | K = 3 | K = 10; EXIT-4.8 |
| The reported number is 4–6 pp above any nearby checkpoint, and moves down that much on a re-eval | Checkpoint selected by argmax on the reported set | select on VAL, report on TEST; EXIT-4.6 |
| GRU arm learns visibly faster per gradient step | It is receiving 32× more transitions per update (sequences vs transitions) | EXIT-4.9 |
| GRU beats the belief-MLP, apparently refuting H_A — **and the effect persists even with perfect visibility** | Dynamics randomisation left on: the agent must system-identify, a second and unrelated source of partial observability | EXIT-4.11 |

---

## 10. Consolidated reading list

Ordered by stage. `[V]` verified against the source · `[C]` certain to exist, details unchecked ·
`[?]` **unverified — open it before citing.**

### Two citation traps already identified

1. **Fraichard & Scheuer (2004)** is in *IEEE Transactions on **Robotics*** 20(6):1025–1035 — **not**
   *Transactions on Robotics and Automation*. T-RA was renamed T-RO in 2004, so this paper sits
   exactly at the boundary and is very commonly miscited.
2. **The Stanley *controller*** is Hoffmann, Tomlin, Montemerlo & Thrun, **ACC 2007**. Thrun et al.
   (2006), *J. Field Robotics* 23(9):661–692, is the **system** paper. Citing the 2006 paper for the
   control law is a common but wrong attribution. Cite both, for different things.

### Stage 0 — geometry and kinematics
- `[C]` LaValle (2006), *Planning Algorithms*, §13.1.2, §15.3 — free at lavalle.pl/planning
- `[C]` Rajamani, *Vehicle Dynamics and Control*, Ch. 2
- `[?]` Ericson (2005), *Real-Time Collision Detection*, Ch. 4–5

### Stage 1 — classical planning
- `[V]` Reeds & Shepp (1990), *Pacific J. Math.* 145(2), 367–393
- `[V]` LaValle (2006), §15.3.1–15.3.2 — the practical implementation reference
- `[C]` Dubins (1957), *Amer. J. Math.* 79(3), 497–516
- `[V]` Sussmann & Tang (1991), SYCON-91-10, Rutgers
- `[V]` Fraichard & Scheuer (2004), *IEEE T-RO* 20(6), 1025–1035
- `[V]` Dolgov, Thrun, Montemerlo & Diebel (2010), *IJRR* 29(5), 485–501
- `[?]` Dolgov et al. (2008), STAIR-08 — the priority citation; **it is a workshop paper**
- `[V]` Banzhaf, H., Palmieri, L., Nienhüser, D., Schamm, T., Knoop, S. & Zöllner, J. M. (2017). "Hybrid Curvature Steer: A Novel Extend Function for Sampling-Based Nonholonomic Motion Planning in Tight Environments." IEEE ITSC 2017
- `[?]` Coulter (1992), CMU-RI-TR-92-01 — pure pursuit
- `[?]` Hoffmann, Tomlin, Montemerlo & Thrun (2007), ACC — the Stanley **controller**
- `[C]` Thrun et al. (2006), *JFR* 23(9), 661–692 — the Stanley **system**
- `[?]` Souères & Laumond (1996), *IEEE TAC* 41(5), 672–688
- `[?]` Zhang, Liniger, Sakai & Borrelli (2018), CDC — OBCA for parking
- `[?]` Zhang, Liniger & Borrelli, *IEEE TCST* 29(3), 972–983 — OBCA
- `[?]` Boissonnat, Cérézo & Leblond (1994), *JIRS* 11(1), 5–20
- `[?]` Hart, Nilsson & Raphael (1968), *IEEE Trans. SSC* 4(2), 100–107

### Stage 2 — core RL
- `[C]` Sutton & Barto (2018), Ch. 3, 4, 11, 13, §17.4
- `[C]` Szepesvári (2010), Ch. 1–2
- `[C]` Haarnoja, Zhou, Abbeel & Levine (2018), SAC, ICML 2018 PMLR 80:1861–1870 — **App. C**
- `[C]` Haarnoja et al. (2018/2019), arXiv:1812.05905 — what SB3 actually implements
- `[C]` Haarnoja, Tang, Abbeel & Levine (2017), Soft Q-Learning, ICML 2017
- `[C]` Fujimoto, van Hoof & Meger (2018), TD3, ICML 2018 PMLR 80:1587–1596
- `[V]` Pardo, Tavakoli, Levdik & Kormushev (2018), ICML 2018 PMLR 80:4045–4054
- `[C]` Raffin et al. (2021), SB3, *JMLR* 22(268)
- `[C]` Achiam (2018), *Spinning Up in Deep RL*
- `[C]` Sutton, McAllester, Singh & Mansour (2000), NIPS 12, 1057–1063
- `[C]` Williams (1992), *Machine Learning* 8(3–4), 229–256
- `[C]` Kingma & Welling (2014), ICLR — §2.4, reparameterisation and change-of-variables
- `[C]` Lillicrap et al. (2016), DDPG, ICLR — §3 only, for the Polyak update
- `[C]` Schulman et al. (2016), GAE, ICLR — **PPO branch only**
- `[C]` Schulman et al. (2017), PPO, arXiv:1707.06347 — **never formally published; cite as a preprint**
- `[C]` Schulman et al. (2015), TRPO, ICML 2015 PMLR 37:1889–1897
- `[?]` Singh & Yee (1994), *Machine Learning* 16(3), 227–233
- `[?]` Jiang, Kulesza, Singh & Lewis (2015), AAMAS
- `[?]` Tallec, Blier & Ollivier (2019), ICML 2019
- `[?]` Thomas (2014), ICML 2014 — for stating the policy-gradient bias honestly
- `[C]` van Hasselt et al. (2018), arXiv:1812.02648 — the deadly triad, made concrete
- `[?]` Nikishin et al. (2022), primacy bias, ICML 2022
- `[?]` Ball, Smith, Kostrikov & Levine (2023), RLPD, ICML 2023
- `[C]` Engstrom et al. (2020), "Implementation Matters," ICLR 2020

### Stage 3 — shaping, curriculum, robustness
- `[V]` Ng, Harada & Russell (1999), ICML 1999, 278–287
- `[V]` Grzes (2017), AAMAS 2017, 565–573
- `[V]` Wiewiora (2003), *JAIR* 19, 205–208
- `[V]` Devlin & Kudenko (2012), AAMAS 2012, 433–440
- `[V]` Randløv & Alstrøm (1998), ICML 1998
- `[V]` Skalse, J., Howe, N., Krasheninnikov, D. & Krueger, D. (2022). **"Defining and Characterizing Reward Gaming."** NeurIPS 35, pp. 20460–20475 — *this is the camera-ready title, verified on the proceedings page; cite it as primary.* The arXiv version (2209.13085, revised 2025) is retitled "…Reward Hacking", and ACM DL's mirror also says "hacking", so citation managers will disagree depending on source
- `[V]` Florensa, Held, Wulfmeier, Zhang & Abbeel (2017), CoRL 2017 PMLR 78:482–495
- `[V]` Portelas, R., Colas, C., Hofmann, K. & Oudeyer, P.-Y. (2019). **"Teacher Algorithms for Curriculum Learning of Deep RL in Continuously Parameterized Environments."** CoRL 2019, PMLR 100:835–853 — *"ALP-GMM" is the algorithm name, not the paper title; do not use it as a title in a reference list*
- `[C]` Bengio, Louradour, Collobert & Weston (2009), ICML 2009
- `[C]` Tobin et al. (2017), IROS 2017 — **visual** DR, not dynamics DR
- `[?]` Peng, Andrychowicz, Zaremba & Abbeel (2018), ICRA 2018 — **dynamics** DR
- `[V]` OpenAI et al. (2019), arXiv:1910.07113 — the ADR update rule
- `[C]` Andrychowicz et al. (2017), HER, NIPS 2017 — read it to justify not using it
- `[V]` Nair, McGrew, Andrychowicz, Zaremba & Abbeel (2018), ICRA 2018, 6292–6299 — the Q-filter
- `[?]` Vecerik et al. (2017), DDPGfD, arXiv:1707.08817
- `[V]` Nair, Gupta, Dalal & Levine (2020), AWAC, arXiv:2006.09359
- `[V]` Laskey, Lee, Fox, Dragan & Goldberg (2017), DART, CoRL 2017, PMLR 78:143–156
- `[?]` Narvekar et al. (2020), curriculum survey, *JMLR* 21
- `[?]` Wiewiora, Cottrell & Elkan (2003), ICML 2003 — only if shaping on the **action**

### Stage 4 — evaluation and POMDP theory
- `[C]` Henderson et al. (2018), AAAI 2018, 3207–3214
- `[C]` Agarwal et al. (2021), NeurIPS 2021, arXiv:2108.13264 + the **rliable** library
- `[V]` Patterson, Neumann, White & White (2024), *JMLR* 25(318), 1–63 — *the internal submission id "23-0183" could not be verified; omit it*
- `[V]` **Baisero, A. & Amato, C. (2022). "Unbiased Asymmetric Reinforcement Learning under Partial Observability." AAMAS 2022, arXiv:2105.11674** — the correct citation for §6.5; absent from v1.0
- `[V]` Belinkov, Y. (2022). "Probing Classifiers: Promises, Shortcomings, and Advances." *Computational Linguistics* 48(1), 207–219 — why decodability ≠ use (EXIT-4.10)
- `[V]` Lukoševičius, M. & Jaeger, H. (2009). "Reservoir Computing Approaches to Recurrent Neural Network Training." *Computer Science Review* 3(3), 127–149 — why an untrained-GRU probe control is a reservoir, not a floor
- `[?]` Colas, Sigaud & Oudeyer (2018), arXiv:1806.08295
- `[?]` Colas, Sigaud & Oudeyer (2019), arXiv:1904.06979
- `[V]` Brown, Cai & DasGupta (2001), *Statistical Science* 16(2), 101–133 — *Wald-coverage claim directly supported*
- `[V]` Wilson (1927), *JASA* 22(158), 209–212 — *verified exact; the drafting agent's uncertainty was unwarranted*
- `[C]` Clopper & Pearson (1934), *Biometrika* 26(4), 404–413
- `[C]` Agresti & Coull (1998), *The American Statistician* 52(2), 119–126
- `[V]` Newcombe (1998), *Stat. Med.* 17(22), 2635–2650 — **paired** intervals. *Distinct from Newcombe (1998), 17(8):857–872 (seven methods, single proportion); both verified and correctly matched to their claims*
- `[V]` McNemar (1947), *Psychometrika* 12(2), 153–157 — *verified exact*
- `[C]` Schuirmann (1987) — TOST
- `[?]` Holm (1979), *Scand. J. Statist.* 6(2), 65–70
- `[C]` Goodman (1965), *Technometrics* 7(2), 247–254 — simultaneous multinomial intervals
- `[C]` Efron & Tibshirani (1993), Ch. 8, 12–14
- `[?]` Dolan & Moré (2002), *Math. Prog.* 91(2), 201–213 — performance profiles
- `[?]` Vargha & Delaney (2000) — the statistic behind "probability of improvement"
- `[V]` Kaelbling, Littman & Cassandra (1998), *Artificial Intelligence* 101(1–2), 99–134
- `[V]` Åström (1965), *J. Math. Anal. Appl.* 10, 174–205 — *volume and pages verified; primary text not retrievable*
- `[V]` Ni, Eysenbach & Salakhutdinov (2022), ICML 2022, arXiv:2110.05038
- `[V]` Pinto, Andrychowicz, Welinder, Zaremba & Abbeel (2018), RSS 2018 — *RSS 2018 is correct, not the 2017 arXiv year*
- `[?]` Kapturowski et al. (2019), R2D2, ICLR 2019 — burn-in / stale hidden states
- `[?]` Zaheer et al. (2017), Deep Sets, NIPS 2017
- `[?]` Machado et al. (2018), *JAIR* 61, 523–562 — the frozen-protocol argument
- `[?]` Pineau et al. (2021), *JMLR* 22(164) — use the checklist verbatim as a thesis appendix

### Stage 5
- `[V]` Chen, D., Zhou, B., Koltun, V. & Krähenbühl, P. "Learning by Cheating." **CoRL 2019, PMLR 100:66–75** — *drop the bare "(2020)": PMLR dates the volume 2020 while the conference was 2019, and printing both reads as an error*
- `[?]` Lee et al. (2020), *Science Robotics*
- `[?]` Ross, Gordon & Bagnell (2011), DAgger, AISTATS
- `[?]` Ray, Achiam & Amodei (2019), Safety Gym; Achiam, Held, Tamar & Abbeel (2017), CPO, ICML 2017

**Preference-based RL — for §5.5.1.** *(added v1.4)* **Every entry below was written from memory and
is `[?]`; the CPL author list in particular must be checked before it enters a bibliography (§0.1).**

| Priority | Source | Covers |
|---|---|---|
| must | `[?]` Hejna, Rafailov, Sikchi, Finn, Niekum, Knox & Sadigh (2024). "Contrastive Preference Learning: Learning from Human Feedback without RL." ICLR 2024. | **The one that matters.** Regret-based preferences + the max-ent identity `A* = α log π*` ⇒ a DPO-shaped loss with no reward model |
| must | `[?]` Christiano, Leike, Brown, Martic, Legg & Amodei (2017). "Deep RL from Human Preferences." NeurIPS 2017. | The founding preference-based-RL-for-control paper; also the source of the realistic query-budget numbers (~10²–10³ human comparisons) |
| must | `[?]` Rafailov, Sharma, Mitchell, Ermon, Manning & Finn (2023). "Direct Preference Optimization." NeurIPS 2023. | DPO itself — read it for the `r = β log(π/π_ref) + β log Z` derivation and to see **exactly which step assumes a bandit** |
| should | `[?]` Lee, Smith & Abbeel (2021). PEBBLE. ICML 2021. | Off-policy preference-based RL with SAC and relabeling — **arm P2's baseline** |
| should | `[?]` Lee et al. (2021). "B-Pref." NeurIPS Datasets & Benchmarks 2021. | Benchmark conventions, synthetic-teacher models — **arm P3 is B-Pref's teacher idea used as a gate** |
| background | `[?]` Bradley & Terry (1952), *Biometrika* 39:324–345; Ziebart et al. (2008), MaxEnt IRL, AAAI | The preference model, and the max-entropy lineage CPL's identity comes from |

---

## 11. Notation

| Symbol | Meaning |
|---|---|
| `L, l, w, f, r` | wheelbase, total length, width, front overhang, rear overhang |
| `δ, δ̇` | road-wheel steering angle and its rate (**not** the steering-wheel angle) |
| `κ = tan δ / L` | path curvature at the rear axle |
| `R_min = L/tan δ_max` | minimum turning radius **of the rear axle** |
| `θ` | heading; enters observations as `(sin θ, cos θ)` |
| `Φ(s)` | shaping potential — a function of **state only**, zero at every terminal |
| `F = γΦ(s′) − Φ(s)` | the potential-based shaping term (**the γ is not optional**) |
| `γ = 0.995` | discount; `H_eff = 1/(1−γ) = 200` steps |
| `τ` (SAC) | Polyak rate, 0.005 — **rename in code**; it collides with `1−τ = 0.995` and with `τ_since_seen` |
| `ρ` | optimality ratio `ell_RL / ell_oracle` |
| `Δs` | collision-check arc-length resolution, ≤ 0.026 m |
| `K` | number of training seeds (10 for every headline table) |
| `N` | scenarios per family in an evaluation set (500 for TEST) |
| `d_MDE` | minimum detectable effect size, `≈ sqrt(15.7/K)` |
| O0–O4 | observation-degradation rungs (§6) |
| A1–A5 | the five arms of the O3 memory comparison (§5.4) |

---

## Appendix — provenance of this document

Assembled 2026-08-05 from a six-way parallel research fleet. **Four of six drafting agents completed**
(core RL; reward shaping and curriculum; classical planning; evaluation methodology); the geometry and
POMDP sections were written directly. **All six adversarial verification agents and both audit agents
failed to run** (session limit), so:

- The `planning` and `shaping` sections' citations were self-verified by their drafting agents, which
  report having opened the actual PDFs of Reeds & Shepp 1990, Sussmann & Tang SYCON-91-10, Fraichard &
  Scheuer 2004, Banzhaf et al. 2017, Dolgov et al. 2010, and LaValle §15.3.2, and having checked
  others against dblp / ACM DL records.
- The `core-rl` and `eval` sections carry per-citation self-reported confidence, propagated here as
  `[C]` / `[?]`.
- **No citation in this document has been independently checked by a second agent.** The `[?]` markers
  are therefore a floor on the uncertainty, not a complete audit.

Numerical claims computed independently by two or more agents, in agreement: `R_min = 3.9466`,
`R_front_outer = 6.0574`, `R_swept_inner = 3.0216`, the γ^N table, and the 3-circle covering radius
1.2121 m. **The `v_max/a_max = δ_max/δ̇_max = 1.000` "knife edge" is NOT in this list any more** — the
arithmetic is right but its interpretation was refuted in v1.1 (§4.1); listing it as corroborated was
itself an error, since only the arithmetic was ever corroborated, not the conclusion drawn from it.

### v1.1 verification pass (2026-08-05)

Nine agents in five sequential waves — citations on Sonnet, re-derivation and audits on the session
model — sequenced so that a session-limit hit could not destroy completed work, which is exactly what
happened on the two preceding attempts (both lost everything: 9/9 and 12/12 agents killed
mid-flight). **7 of 9 completed.**

| Agent | Model | Result |
|---|---|---|
| cite:planning | sonnet | 12 checks — Fraichard/Stanley/RS-counts/Dolgov all confirmed from primary PDFs |
| cite:shaping | sonnet | 10 checks — Grzes PDF retrieved; Skalse title resolved |
| cite:core-rl | sonnet | 9 checks — found the Pardo case-(a)/(b) misattribution |
| cite:eval | sonnet | 14 checks — Wilson/McNemar/Åström upgraded; low-priority tail not reached |
| verify:arithmetic | sonnet | 14 numeric claims recomputed; 10 exact, 3 imprecise, 1 unreproducible |
| verify:geometry | *(session model)* | 30 checks — **2 fatal**, 7 serious |
| verify:pomdp | *(session model)* | 25 checks — 8 serious, incl. the never-seen-object hole |
| audit:completeness | — | **FAILED (session limit)** |
| audit:exit-criteria | — | **FAILED (session limit)** |

Raw results: `scratchpad/v2/*.md`; workflow run `wf_bd46e476-05c`, resumable — the seven completed
agents replay from cache, so a resume costs only the two audits.

### v1.2 verification pass (2026-08-06)

The run above was **resumed** (`resumeFromRunId`) once the session limit reset: the seven completed
agents replayed from cache and only the two audits ran live, so the third attempt cost roughly a
fifth of a fresh run. **9/9 completed.** Before resuming, both audit prompts were amended to say that
the document was now v1.1 and that **the v1.1 corrections themselves had never been checked** — which
turned out to be where four of the nine fatal findings were.

| Audit | Findings |
|---|---|
| completeness critic | 37 — 2 fatal, 27 serious, 8 minor |
| exit-criteria falsifiability auditor | 41 — 7 fatal, 28 serious, 6 minor |

Raw results: `scratchpad/v3/*.md`.

**Open items:**
1. **Every v1.2 correction is unreviewed.** v1.1 was in exactly this state when it shipped four fatal
   errors. A fourth pass over §0.3's changes is the single highest-value remaining action.
2. The low-priority tail of the Stage-4 statistics citations (§0.1).
3. An independently derived minimum-slot-length formula — §5.0(c) still deliberately leaves this to
   be derived rather than copied, and the v1.1 pass found its frame under-specified. *(The **bay**
   analogue is now closed in §5.0(c′); this item is parallel-parking only.)*
4. The Fraichard & Scheuer "infinite chattering" claim: the checker could not retrieve readable full
   text (HAL bot-blocked, ResearchGate 403, CiteSeerX 404). Secondary sources are consistent with it
   but it is **not verbatim-confirmed**. Treat as plausible, not established.

### v1.3 (2026-08-07) — reverse-bay geometry

Not a verification pass: a **content** pass, closing the largest known gap rather than checking
existing claims. Derived by hand, then validated against an independent numerical construction —
an explicit swept body (40 001 arc samples, exact OBB corners, polygon clipping against the bay-row
half-planes) that shares no code with the closed form.

| Quantity | Closed form | Numerical sweep | Agreement |
|---|---|---|---|
| `max_y` over the manoeuvre | `R_front_outer − u*` | direct max over 40 001 samples | **2.5e-11 m** worst case over 27 (W_gap, c) cells |
| footprint edges at `x_e*` | `±(W_gap/2 − c)` | polygon clip to `y ≤ 0` | **≤ 1e-9 m** on the upper branch, **1.5e-5 m** on the lower (arc-sampling limited) |
| cap `u ≤ R_swept_inner − c` | approach flank at `+c` | direct | **1.1e-16 m** |

Scripts: `scratchpad/bay2.py` (sweep decomposition), `bay4.py` (closed form + validation),
`bay6.py` (static containment bound).

**Open items after v1.3:**
1. **§0.4 is unreviewed**, as is §0.3 before it. The arithmetic is machine-checked; the framing is not.
2. **The single-arc restriction is asserted, not proved.** `W_aisle_min` is exact for the
   constant-radius family and an upper bound for the general single-cut class. Whether a
   varying-curvature single cut beats it is open; the bracket `[3.5100, 4.3519]` is what is actually
   established.
3. **Two-family bookkeeping is still incomplete.** A25 says one policy; the eval protocol says
   "per family". EXIT-2.27, EXIT-3.1 and §5.4's surface now carry both axes, but the Stage-4 metric
   table, the §5.4.1 step budgets and the K-seed arithmetic were all costed for **one** family.
4. Everything still open from §0.3 (items 1, 3–7).

### v1.4 (2026-08-07) — preference-based fine-tuning

A **design** pass, not a verification or a derivation pass. Nothing in it is machine-checked and the
citations are unverified; §0.5 says so in place.

**Open items after v1.4:**
1. **The whole of §0.5 is unreviewed and unverified**, and unlike §0.4 it has no numerical anchor.
2. **The reading list added to §10 is 100% `[?]`.** The CPL entry is load-bearing for §5.5.1's central
   argument and is the single most important thing to verify in this document right now.
3. **CPL's assumptions have not been checked against this MDP line by line.** The regret-based
   preference model, the segment-level formulation, and the conservative variant's role are asserted
   from memory. Before building: read the paper and write the assumption list into §2 as A29+.
4. **The §5.5 contribution slot is now over-subscribed** — six candidates against a Stage-4 budget of
   ~860 GPU-hours (§5.4.1). §5.5.1 says which pair composes; nothing says which one wins.
5. Everything still open from §0.3 and §0.4.
