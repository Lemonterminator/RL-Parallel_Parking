# ROADMAP

*Decomposed from `PLAN_MACRO.md` — the orthogonal material: §0 (0.1–0.5), §1, §2 (A1–A28), §3
(I1–I10), §4/§4.1/§4.2, §6 (the whole observation ladder, O0–O4, including §6.4, §6.5, §6.6's
EXIT‑6.x), §7 (reward), §8 (evaluation protocol), §9 (failure‑mode table), §10 (reading list), §11
(notation), and the Appendix. Per‑stage build plans (§5.0–§5.5) belong to sibling files — this
document is not a substitute for them. Every substantive statement below carries a back‑pointer to
its source in `PLAN_MACRO.md`; anything without one is either a verbatim copy under its own
whole‑block pointer, or is explicitly marked as this decomposition's own synthesis (the artefact
graph and the stage‑map paragraphs are necessarily synthesis — each edge/claim in them still carries
a pointer to the specific line of PLAN_MACRO.md that licenses it). Numbers are transcribed
character‑for‑character; where a value disagrees with itself elsewhere in the source, both values
are reported side by side rather than resolved. `[V]`/`[C]`/`[?]`/`[D]` markers are carried through
unchanged.*

---

## How to read this, and verification status (§0.1–§0.5)

**Document identity, as stated at the top of PLAN_MACRO.md:**

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
> v1.2 change is marked inline, and every one of them is now itself unreviewed. Read §0.2. [banner, pre‑§0.1]

The document's own frontmatter reads **"Version 1.2 · 2026-08-06 · self-contained (no prior
conversation required)"** [banner, line 5] — but §0.4 and §0.5 (dated 2026‑08‑07) and the Appendix's
last entry, **"v1.4 (2026-08-07) — preference-based fine-tuning"** [Appendix], were added after that
header was written and the header was never bumped. Read the frontmatter as stale; the true state is
v1.4, with the fatal caveat that follows applying to *all* of v1.2/v1.3/v1.4 alike (see Findings,
below).

The organisation, as PLAN_MACRO.md states it: §1–§4 is what the project is, what it assumes, and the
invariants that hold at every stage; §5 is six sequential stages with hard exit criteria; §6 is an
*orthogonal* observation-degradation ladder mapped onto those stages; §7–§11 is reward, evaluation
protocol, failure-mode diagnostics, reading list, notation. [§0, intro]

**Exit criteria are contractual.** Every one is a number, a statistical test, or a boolean assertion
checkable by a script with no human judgement. Wherever this plan is tempted to say "the trajectories
look smooth" it says instead "p95 of `Jbar_ddelta` ≤ X on the frozen test set." [§0, intro]

### 0.1 Citation verification status

| Marker | Meaning |
|---|---|
| `[V]` | **Independently verified in the v1.1 pass** against a retrieved publisher record, DOI resolver, dblp, PMLR, arXiv, JMLR or the PDF itself. |
| `[C]` | Standard, widely-cited reference; existence certain, page/volume numbers **not** independently checked. |
| `[?]` | **Unverified.** Author list, venue, year, or page range may be wrong. Verify before it enters a bibliography. |
| `[D]` | *(added v1.3)* **Not a citation.** Derived inside this document and checked against an independent numerical construction, with the agreement figure stated. Carries no literature claim — if a published result contradicts it, the published result has not been consulted. |

**Rule: no `[?]` reference may be cited in a thesis without opening it first.** [§0.1]

**v1.1 outcome across 57 checked citations: 39 exact · 7 wrong in detail (corrected inline) · 11
unverifiable · 0 fabricated.** The seven corrections were: the Skalse camera-ready title is *"Reward
Gaming"*; "ALP-GMM" is Portelas et al.'s *algorithm*, not their paper title; Vorobieva is **two**
distinct papers with different author orders; "Learning by Cheating" should drop its bare "(2020)";
Banzhaf's full title and six authors; and — the only genuine misattribution — v1.0 presented
"case (a)"/"case (b)" as Pardo et al.'s own notation, but the paper labels those regimes (i) and
(ii). The policy recommendation was represented correctly; only the labels were invented. [§0.1]

Several `[?]` markers were **upgraded** on verification — Wilson (1927), McNemar (1947), Åström
(1965), Pinto et al., Patterson et al. and Ni et al. all check out exactly; the drafting agents'
stated uncertainty about them was unwarranted. [§0.1]

**Coverage gap:** the low-priority tail of the Stage-4 statistics list (Holm, Clopper–Pearson,
Agresti–Coull, Schuirmann, Goodman, Efron–Tibshirani, Dolan–Moré, Vargha–Delaney, Machado et al.,
Pineau et al., Kapturowski et al., Zaheer et al., and the Stage-5 block) was **not reached** before
the checker's budget ran out. Those remain `[C]`/`[?]` and are not a clean bill of health. [§0.1]
**Already known: the Stage-4 statistics citation tail was never checked** — carried here per the
known-items list, not as a new finding.

Two known citation traps are documented in §10 (carried below). [§0.1]

### 0.2 What v1.1 changed *(historical — superseded by §0.3)*

**Fatal (§4.1, rewritten).** The "feasibility knife edge" was wrong three ways: the inequality is not
an *iff* (`a_max` is an upper bound, not a mandate, so a dwell-free reversal is *always* available);
the parameter set does not sit *on* the edge (under bang-bang it holds only at exactly `v_max`, while
real cusps happen at 0.3–0.7 m/s); and **two of the three stated randomisation directions were
inverted** — lowering `a_max` makes a cusp *easier*, not harder. [§0.2]

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
[§0.2]

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
  numbers. Removed. [§0.3]

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
  integrator scheme, one-vs-two policies, `L_oracle` definition). [§0.3]

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
[§0.3] — **all seven items already known** per the brief; carried here for completeness. Item 4 (the
ordering leftovers) is expanded with the artefact-graph detail below, including one further instance
this decomposition found (EXIT‑0.14(c)) that item 4's prose does not separately count.

### 0.4 What v1.3 changed — the reverse-bay geometry that was never there

v1.3 closes open item 2 of §0.3: **reverse bay parking, half the headline task, had no geometry at
all.** It is now derived, in closed form, and machine-checked. [§0.4]

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
  distribution, not from the manoeuvre. [§0.4]

**And the same caveat as always, which v1.2 proved is not rhetorical: everything in §0.4 is new,
and therefore unreviewed.** The derivation is machine-checked against an independent numerical
sweep, which is stronger than v1.1's corrections ever were — but the *framing* around it (which
model is conservative, which gate belongs where, whether the single-arc family is the right one)
has had exactly one pair of eyes on it. [§0.4]

### 0.5 What v1.4 changed — preference learning as a Stage-5 direction

Content, not correction. Answers "where would a DPO variant go?" with a placement, a shape, and two
cheap kill-switches. [§0.5]

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
- **§10** — a preference-based-RL reading block, **entirely `[?]`**. [§0.5]

**Unreviewed, and this one is weaker than §0.4:** §0.4's arithmetic was machine-checked against an
independent construction. Nothing here is. The citations are from memory, the four-arm design has had
one pair of eyes on it, and the claim that CPL's max-entropy identity composes cleanly with this
plan's SAC configuration is an **argument**, not a verified derivation. [§0.5]

---

## Project statement and scope (§1)

Build and evaluate a reinforcement-learning controller for low-speed car parking in 2D, and
compare it honestly against classical motion planning. [§1]

**Scope.** Rigid rectangular ego vehicle; static rectangular obstacles; kinematic bicycle
dynamics; two task families (parallel parking, reverse bay parking); continuous control. [§1]

**What this project is *not*.** It is not an attempt to beat Hybrid A* at path planning on a known
static map. On a known static map with exact geometry, search and optimisation essentially solve
this problem: Hybrid A* plus gradient smoothing finds a drivable, collision-checked path in well
under a second. A pure-RL success rate on that setting is a **sanity check on the MDP, reward and
simulator — not a contribution.** The contribution has to live where RL is genuinely better, which
is §5.5. [§1] — §5.5 (Stage 5, the contribution slot) belongs to the sibling `PLAN_S5.md`.

**Two task families, one policy [A25]:** the document specifies parallel parking and reverse bay
parking as two families solved by a single scenario-conditioned policy, not two policies. Anywhere
this ROADMAP or PLAN_MACRO.md discusses only one family without saying so explicitly, that is a gap,
not a generalisation — see A25's row in the Assumptions table below and Finding F16.

---

## Stage map

*Synthesis: one paragraph per stage, assembled from each stage's Goal line and Build/consumer
sections. Per‑stage exit criteria, theory reading, and detailed build order belong to the sibling
stage files (§5.0 → a Stage‑0 file, …, §5.5 → `PLAN_S5.md`); this section exists only to give the
dependency graph below somewhere to point.*

**Stage 0 — Geometry and kinematics kernel (no RL).** Goal: "A unit-tested geometric and kinematic
core. Everything downstream consumes it, so a bug here is a bug in every later result." [§5.0]
Produces: `worldstate.py` (the `WorldState` dataclass, **including `settle_counter` as part of the
state**), `dynamics.py` (rear-axle bicycle, explicit substep integration, action clamping),
`geometry.py` (`obb_corners`, `sat_overlap`, `obb_signed_distance`, `body_circles`, `ccd_sweep`),
`render.py` (trajectory replay) [§5.0 Build]; plus hand-derived closed-form geometry: the two-arc
lateral-shift relation, the parallel-parking minimum-slot-length frame (deliberately left to be
derived, not copied), and — closed in v1.3 — the reverse-bay single-cut feasibility boundary and the
any-number-of-cuts static containment bound [§5.0(b), §5.0(c), §5.0(c′)]. Unlocks: the SAT/footprint
code Stage 1's planner shares byte-for-byte with the environment [§5.1, "the same exact SAT test the
environment uses, with the same footprint"]; the `Δs ≤ 0.026 m` collision-check resolution every
downstream path validator inherits [§5.0(f)]; the 3-circle reward-potential body model [§5.0(e)].

**Stage 1 — Classical planning baselines (still no RL).** Goal, stated directly: "This stage is
infrastructure, not an afterthought. Its outputs are consumed by every later stage: the feasibility
oracle filters curriculum sampling, the path length is the optimality denominator, the
reverse-curriculum generator comes from it, and it is the demonstration source. Building it after the
RL is the single most common ordering mistake in projects like this." [§5.1] Produces: the RS closed
form, a collision-checked path validator shared by everything downstream, the feasibility oracle
`is_feasible`, `h_nhwo`/`h_hwo` heuristics, Hybrid A*, a speed profiler, and a rear-axle pure-pursuit
tracker [§5.1 build order]; the "four consumers" — feasibility oracle, optimality denominator
(`ell_RS`/`ell_HA*`/`ell_OBCA`), reverse-curriculum generator (source), demonstrations (source)
[§5.1(a)–(d)]; plus, added in v1.4, a teleoperation front end + logger and a drawn-path trackability
probe [§5.5.1 prerequisites table]. Unlocks: Stage 2's frozen-eval-set generation (Hybrid A* filters
the scenario distribution) and reward calibration against "the Stage-1 planner, not intuition" [§7.2,
§8]; Stage 3's reverse curriculum and demonstration corpus [§5.3 Build]; Stage 4's optimality-ratio
denominators [§5.4 metric table]; Stage 5's teleoperation/preference-pairing infrastructure
[§5.5.1]. **Also consumes a Stage-0 artefact it does not yet have when EXIT-0.8/0.14(c) are due to
run** — see Ordering inversions, below.

**Stage 2 — Minimal viable RL (full-state MDP, O0).** Goal: "A working SAC agent on the
fully-observable task, with the evaluation protocol frozen **before** any tuning happens." [§5.2]
Produces: the `Observer` interface and its concrete implementations (`FullObserver`,
`DropoutObserver`, `FOVObserver`, `OccludedObserver`, `BeliefObserver`) [§5.2 Build]; the SAC
implementation including the tanh log-probability correction [§5.2(b)]; the frozen `γ = 0.995` choice
via EXIT-2.11's sweep [§5.2 hyperparameters, EXIT-2.11]; the frozen eval set (VAL/TEST/INFEASIBLE
CONTROL, hashed) [§8]; the O0 policy that later becomes both `pi_ref` (§5.5.1) and the free
teacher for distillation (§6.5). Unlocks: Stage 3's O1/O2 rungs, which wrap the Stage-2 `Observer`
[§6.1]; Stage 4's O3 arms, all built on the Stage-2 SAC/Observer machinery [§5.4]; Stage 5's `pi_ref`
and exact-log-prob prerequisites [§5.5.1 prerequisites table]. **Is itself consumed backward by
Stage 1's EXIT-1.12**, which needs the `Observer` — see Ordering inversions.

**Stage 3 — Curriculum and robustness.** Goal: "From 'works on the easy distribution' to 'works on
the full distribution under perturbation.' This stage also carries observation rungs **O1** and
**O2**." [§5.3] Produces: the reverse-curriculum generator (built on the Stage-1 oracle and reference
path) [§5.3 Build]; tolerance annealing gated on measured success rate [§5.3 Build]; the
demonstration corpus, generated by "running the Stage-1 tracker inside the real environment" with
DART-style noise [§5.3 Build, "Demonstrations (if used)"]; dynamics/scene domain-randomisation
configs and observation-domain randomisation (O1) [§5.3 Build]; the O2 FOV mask and O2a range-limited
sensor [§6.1, §6.2]. Unlocks: Stage 4's mandatory DR-on replication (EXIT-4.11) and its
O2/O2a-conditioned arms.

**Stage 4 — Evaluation, baselines, and the O3 memory comparison.** Goal: "Turn results into evidence.
The protocol was frozen at Stage 2; this stage executes it." [§5.4] Produces: the trained five-arm
O3 comparison (Arm A1–Arm A5 in this document's notation — see the disambiguation note in
Assumptions, below) [§5.4 arm table]; the success-rate surface with feasibility overlay [§5.4]; the
statistical reporting machinery (Wilson, Clopper–Pearson, McNemar, TOST, IQM) [§5.4 "statistics you
will actually use"]; the pre-registered H_A/H_B/H_C results [§5.4]. Costed at **~860 GPU-hours**
before evaluation, with a six-rung fallback ladder if the budget binds [§5.4.1, reproduced in full
below]. Unlocks: Stage 5's "the machinery works" baseline [§5.5].

**Stage 5 — Research contribution (optional).** Not detailed here — owned by the sibling
`PLAN_S5.md`, which decomposes §5.5/§5.5.1/§0.5/§10's preference-RL block in full. Noted here only
for the dependency graph: Stage 5 is explicitly **optional** [§5.5, "(optional)"] and its six
candidate directions (Degraded perception/O4, zero-shot slot geometry, robustness to model error,
Safe RL, sample efficiency of planner-guided RL, preference-based fine-tuning/CPL) compete for a
budget "not additive" with the ~860 GPU-hours Stage 4 already spent [§5.5.1, "the cost, stated
plainly"]. This has a direct consequence for the O4 observation rung — see Finding F8.

---

## Compute budget and the six-rung fallback ladder (§5.4.1)

*Table copied intact per instruction, even though §5.4.1 sits inside Stage 4's section — it is
cross-cutting: it determines which artefacts in the dependency graph below are guaranteed versus
conditional on budget.*

**Stage 4 as specified in v1.1 costs roughly 860 GPU-hours of training**, and that is before
evaluation. The audit costed it: 5 headline arms x 10 seeds, **plus** the mandatory DR-on
replication of all five arms that EXIT-4.11 requires, **plus** the O2a sweep, H_B, a TD3 baseline
and the gamma sweep, at an assumed 3M environment steps per run. The EXIT-4.7 success surface alone
needs a further **40-200M environment steps** of pure evaluation, which v1.1 never costed at all.
[§5.4.1]

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
| 1 | Drop the DR-on replication of all five arms (EXIT-4.11) to **two** arms (A3, A4) | ~35% | the DR-on comparison covers only the two arms H_A is about |
| 2 | Cut the O2a sweep from 5 radii to **2** (6 m, 12 m) | ~10% | coarser radius resolution; EXIT-6.4 reports the two-point sweep |
| 3 | Reduce the success surface to a **6x6** grid at 30 episodes/cell | ~60% of eval | contour band widens; state it in the figure |
| 4 | Reduce K from 10 to **7** for non-headline arms (A1, A2, A5), keep **K=10 for A3 and A4** | ~20% | only the H_A pair retains full power — which is the pair the pre-registration is about |
| 5 | Drop A5 (asymmetric critic) entirely | ~15% | lose the asymmetric-critic arm; it is the least load-bearing of the five |

[§5.4.1]

**Do not descend below rung 5 by cutting seeds on A3/A4.** That pair is the entire pre-registered
experiment, and the TOST margin already has a power problem (below). [§5.4.1]

**The 3 pp TOST margin has no power analysis, and K=10 is probably not enough for it.** At plausible
between-seed standard deviations the equivalence test needs **16-44 seeds**, not 10. Either widen
the margin, or measure the between-seed sd in Stage 2 and **re-derive K before Stage 4 starts** —
`d_MDE = sqrt(15.7/K)` gives the detectable effect, and the margin must exceed `d_MDE * sd`. Report
the retrospective power alongside any equivalence claim (EXIT-4.8 already demands this; this is the
number it demands). [§5.4.1]

---

## Artefact dependency graph

*This is a synthesis, not a verbatim block: PLAN_MACRO.md never draws this graph explicitly. Every
edge below is licensed by a specific consumer statement in the source, cited per row. Nodes are
artefacts, not stages — per the task brief's instruction to graph artefacts, not stages.*

### Overview

```mermaid
flowchart LR
    subgraph S0["Stage 0 — Geometry & kinematics"]
        GEOM[geometry.py: SAT / OBB / CCD]
        WS[WorldState + settle_counter]
        DYN[dynamics.py: rear-axle bicycle]
        BAYGEO[reverse-bay closed form + containment bound]
        SLOTGEO[parallel-parking slot-length frame]
    end
    subgraph S1["Stage 1 — Classical planning"]
        RS[RS closed form]
        VALID[collision-checked path validator]
        ORACLE[feasibility oracle]
        HYBRID[Hybrid A*]
        TRACK[rear-axle pure pursuit tracker]
        DENOM[ell_RS / ell_HA* / ell_OBCA]
        TELE[teleop front end + logger]
        DRAWN[drawn-path probe]
    end
    subgraph S2["Stage 2 — Minimal viable RL"]
        OBS[Observer interface + variants]
        SAC[SAC + tanh correction]
        EVALSET[frozen eval set, hashed]
        PIREF0[O0 policy -> pi_ref precursor]
    end
    subgraph S3["Stage 3 — Curriculum & robustness"]
        CURR[reverse curriculum generator]
        DEMO[demonstration corpus]
        DR[dynamics/scene DR configs]
        O2MASK[O2 FOV mask / O2a sensor]
    end
    subgraph S4["Stage 4 — Evaluation & O3"]
        ARMS[Arm A1-A5 trained policies]
        SURFACE[success-rate surface]
    end
    subgraph S5["Stage 5 — optional, PLAN_S5.md"]
        PIFINAL[CPL / PbRL arms, O4 etc.]
    end

    GEOM -->|"same exact SAT test the environment uses [§5.1(a)]"| VALID
    GEOM -->|footprint shared, EXIT-0.10 risk if wrong| ORACLE
    WS -->|"settle_counter part of state, A22"| SAC
    DYN --> VALID
    SLOTGEO -.->|EXIT-0.8 needs Hybrid A* to validate| HYBRID
    BAYGEO -.->|EXIT-0.14(c) needs Hybrid A* to bisect W_aisle| HYBRID
    RS --> VALID --> ORACLE --> HYBRID
    HYBRID -->|"h = max(h_nhwo,h_hwo); denominator ell_HA*"| DENOM
    HYBRID -->|"filters curriculum sampling [§5.1 goal]"| CURR
    HYBRID -->|"generator_seed filtered by Hybrid A*, L_oracle stored [§8]"| EVALSET
    TRACK -->|"tracked-expert length; EXIT-1.8"| DENOM
    TRACK -->|"generate demos: run Stage-1 tracker + DART noise [§5.3 Build]"| DEMO
    TRACK -->|"EXIT-1.13, curvature-limited refit tracked"| DRAWN
    EVALSET -.->|"EXIT-1.12 needs Stage-2 Observer to re-render O0/O1/O2"| OBS
    OBS --> DR
    OBS --> O2MASK
    SAC --> ARMS
    EVALSET --> ARMS
    CURR --> SAC
    DEMO --> SAC
    DR --> ARMS
    O2MASK --> ARMS
    ARMS --> SURFACE
    PIREF0 -->|"pi_ref, frozen eval set, metric set [§5.5.1 prereqs]"| PIFINAL
    TELE -->|"EXIT-1.14 replay; pairing corpus [§5.5.1]"| PIFINAL
    DRAWN -->|"EXIT-1.13 gate, kills sketch input if it fails"| PIFINAL
    SURFACE -->|"Stage 4 establishes the machinery works [§5.5]"| PIFINAL
```

Dashed edges are the **ordering inversions**: a later-stage artefact required by an earlier-numbered
stage's own exit criterion. See below for the full list with pointers.

### Key artefacts, their producer, and every criterion/build item that consumes them

| Artefact | Produced (§) | Consumed by | Consuming criterion / build item | Pointer |
|---|---|---|---|---|
| Exact SAT / OBB signed-distance code (`geometry.py`) | §5.0 build | Stage 1 planner and validator; Stage 2 environment collision/termination test (I5) | "the **same exact SAT test the environment uses, with the same footprint**" | [§5.1(a)], [I5] |
| Body footprint placement relative to rear axle | §5.0 build, tested EXIT-0.10 | Every downstream collision/termination check, the planner, the oracle | "the planner and the environment **share the footprint**, so EXIT-2.2's 'checkers agree' confirms they agree while both are wrong" | [§0.3], [EXIT-0.10] |
| `settle_counter` (part of `WorldState`) | §5.0 build (A22) | Stage-2 observation vector; §7.5 success test; §7.6 persisted struct | "`settle_counter` is not optional... Normalise by `K_settle` and include it at **every** rung" | [A22], [§5.2 Build] |
| Reverse-bay closed-form boundary + static containment bound | §5.0(c′) | Stage-1 planner cross-check (EXIT-0.14c); Stage 2/3 bay-family gates (η_bay) | "at Stage 1, bisect `W_aisle` with Hybrid A* and assert the result lies in [3.5100, 4.3519]" | [EXIT-0.14], [A28] |
| Collision-checked path validator (Δs ≤ 0.026 m) | §5.1 build order item 2 | "shared by everything downstream" — feasibility oracle, tracker error bound, demo replay fidelity | — | [§5.1 build order] |
| Feasibility oracle `is_feasible` | §5.1(a) | Reverse curriculum's rejection step (§5.3 Build step 5); frozen eval-set generation (§8); EXIT-3.3/3.5 | "REJECT unless collision-free under exact SAT **AND** the feasibility oracle finds a solution" | [§5.3 Build], [EXIT-3.3] |
| Hybrid A* planner | §5.1 build order item 6 | Frozen eval-set generation (§8, "filter with Hybrid A* using the ENVIRONMENT's exact SAT checker"); reverse-curriculum reference path (§5.3 Build step 1); EXIT-0.8; EXIT-0.14(c) | "the feasibility oracle filters curriculum sampling, the path length is the optimality denominator, the reverse-curriculum generator comes from it" | [§5.1 goal], [§8] |
| `ell_RS` / `ell_HA*` / `ell_OBCA` (optimality denominators) | §5.1(b) | §5.4's optimality-ratio metric ρ; A26 (which one is `L_oracle`) | "only one can be *the* frozen one" — **but no criterion asserts which** (Finding F6) | [A26], [§5.1(b)] |
| Rear-axle pure-pursuit tracker | §5.1 build order item 8 | Demonstration generation (§5.3 Build); EXIT-1.13's drawn-path gate; EXIT-1.8 | "Generate by **running the Stage-1 tracker inside the real environment**" | [§5.3 Build] |
| `Observer` interface + `FullObserver`/`DropoutObserver`/`FOVObserver`/`OccludedObserver`/`BeliefObserver` | §5.2 build | Stage-1's EXIT-1.12 (backward!); Stage 3's O1/O2/O2a rungs; Stage 4's O3 arms | "for 500 recorded episodes, observations re-rendered under O0/O1/O2 have identical shape and dtype" | [EXIT-1.12], [§6.1] |
| Frozen eval set (VAL/TEST/INFEASIBLE CONTROL, SHA-256 hashed) | §8, gated EXIT-2.1/2.2 | Every Stage-3/4 performance gate; §5.4's success surface | "SHA-256 matches a hash literal committed in the eval module; abort on mismatch" | [EXIT-2.1], [§8] |
| SAC implementation + tanh log-prob correction | §5.2 build | Reverse curriculum training; demo-seeded replay buffer (A11); all O3 arms; Stage-5's exact `log π_θ(a\|s)` (marked "free" because Stage 2 already tests it) | "Exact `log pi_theta(a\|s)` with the tanh Jacobian \| Stage 2 \| free — **EXIT-2.17/2.18/2.19 already test it**" | [§5.5.1 prereqs] |
| Reverse-curriculum generator | §5.3 build | Stage-2/3 SAC training start-state distribution | consumes Stage-1's Hybrid A* reference path **and** feasibility oracle | [§5.3 Build] |
| Demonstration corpus | §5.3 build | Replay-buffer seeding (A11); BC pre-training; `pi_ref` | "demonstrations -> replay-buffer seeding (the stated reason A11 chose off-policy SAC), BC pre-training, and pi_ref" | [§5.5.1] |
| Domain-randomisation configs (dynamics/scene, observation) | §5.3 build | Stage 4's mandatory DR-on replication (EXIT-4.11) and O1/O2 rungs | — | [§5.3 Build], [EXIT-4.11] |
| O0 SAC policy | Stage 2 output | `pi_ref` (§5.5.1 P0); teacher for distillation (§6.5 route 1, "Stage 2 produces the teacher for free") | "**P0** \| The Stage-2/3 SAC policy \| `pi_ref`, and the safety floor everything else is measured against" | [§5.5.1 four-arm table], [§6.5] |
| Trained Arm A1–A5 policies | Stage 4 | Success-rate surface; H_A/H_B/H_C conclusions | — | [§5.4] |
| Success-rate surface + oracle/containment overlays | Stage 4, EXIT-4.7 | Stage 5's "machinery works" framing; a human-contour overlay if teleoperation is pursued (§5.5.1) | — | [EXIT-4.7], [§5.5.1] |
| Teleoperation front end + logger | Stage 1 (v1.4 addition) | Stage 5's pairing corpus (P1/P2 arms); a "human contour" figure | "Replay a human trajectory against a planner path or a policy rollout **from a bitwise-identical initial state** (EXIT-0.9)" | [§5.5.1] |
| Drawn-path trackability probe | Stage 1 (v1.4 addition), EXIT-1.13 | Gates whether sketch input is pursued at all in Stage 5 | "Below that, **sketch input is dead** — say so and stop, do not add a repair pipeline" | [EXIT-1.13] |
| `render.py` (trajectory replay) | Stage 0 build | Teleoperation logging pipeline reuses it ("this is input handling plus a logger") | — | [§5.5.1 prereqs table] |
| EXIT-0.9 bitwise determinism | Stage 0 | The whole "determinism dividend" argument for CPL/DPO reductions and teleop replay fidelity | "**EXIT-0.9 asserts bitwise determinism**, so with a fixed seed the reduction is *exact* here" | [§5.5.1] |

### Ordering inversions (backward edges) — every one found

1. **EXIT-0.8 needs Hybrid A\* (Stage 1).** EXIT-0.8's own threshold is "agreement within one grid
   cell of the bisection resolution" against a numerical bisection that the derivation text specifies
   as run with "**your own single-cusp-restricted Hybrid A\***" — a Stage-1 build item. A Stage-0
   exit gate cannot close until Stage 1 exists. *(Already known.)* [EXIT-0.8], [§5.0(c)]
2. **EXIT-0.14(c) needs Hybrid A\* (Stage 1) too** — a second, uncounted instance of the same pattern
   as (1), on a different Stage-0 criterion: "**At Stage 1**, bisect `W_aisle` with Hybrid A\* at
   `W_bay = 2.50` and assert the result lies in [3.5100, 4.3519]." The criterion is numbered as a
   Stage-0 gate (EXIT-0.14) but its part (c) is explicitly a Stage-1 measurement. *(Found by this
   decomposition — not separately counted in §0.3's item 4, which names only EXIT-0.8, EXIT-1.12,
   EXIT-1.4 and the `ell_OBCA` denominator.)* [EXIT-0.14], [§0.3]
3. **EXIT-1.12 needs the Stage-2 `Observer`.** "for 500 recorded episodes, observations re-rendered
   under O0/O1/O2 have identical shape and dtype" — O1/O2 rendering requires the `Observer` classes
   that §5.2 builds. A Stage-1 exit gate depends on a Stage-2 artefact. *(Already known.)*
   [EXIT-1.12], [§5.2 Build]
4. **EXIT-1.4 and the `ell_OBCA` denominator need solvers absent from Stage 1's build list.**
   EXIT-1.4 requires "an independent numerical OCP" solver that "shares no code" with the RS
   implementation, and `ell_OBCA` is defined as "NLP warm-started from HA\*" — neither an OCP solver
   nor an NLP/OBCA solver appears anywhere in §5.1's eight-item build order. This is not a backward
   *stage* edge (no later stage is named as the producer either) — it is an artefact **required by a
   Stage-1 criterion and Stage-1's own denominator table, but scheduled in no stage at all.**
   *(Already known.)* [EXIT-1.4], [§5.1(b)]

No further backward edges were found among the artefacts this file owns (§6 observation ladder, §7
reward, §8 evaluation protocol) — those sections' own cross-references all point forward or
sideways within the same stage (e.g. EXIT-6.2's "each sensor configuration used by any O3 arm" is
measured at Stage 4, consistent with §6.1's own O3→Stage 4 mapping) or to Stage 0 for the
determinism guarantee (EXIT-0.9), which is a Stage-0-before-everything dependency and therefore not
an inversion.

---

## Reference parameters (§4, §4.1, §4.2)

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
[§4]

**Note (this decomposition):** `R_rear_inner = 3.2156 m` and `outer turning diameter = 12.115 m` are
defined here and never referenced again anywhere in PLAN_MACRO.md — see Finding F13.

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
[§4.1, in full]

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
`gamma_new = exp(-dt_new/tau)`. [§4.2, in full]

**Note (this decomposition):** the "modest dense stream of `|c| = 0.05/step`" introduced here as an
illustrative example is the same `c_max = 0.05` that §5.3(e)'s anti-suicide bound and EXIT-2.7/
EXIT-2.28 treat as an established constant — but §7.4, where the corresponding `−w_time` reward term
is actually specified, never itself assigns it the value 0.05. See Finding F11.

---

## Assumptions A1–A28 (§2)

**Disambiguation note (already known — carried per the brief's known-items list).** Assumption IDs
A1–A5 here **collide** with the Stage-4 O3 memory-comparison arm names A1–A5 in §5.4. This
decomposition disambiguates by always writing the arms as **"Arm A1"–"Arm A5"** and leaving the
assumptions as bare **A1–A28**; every other reference in this file follows that convention.
**Proposed rename** (not in PLAN_MACRO.md — this decomposition's own suggestion, offered because the
brief asked for one): rename the five O3 arms to **M1–M5** ("M" for memory-architecture arm) in
§5.4/§5.4.1/§6, leaving the assumption numbering A1–A28 untouched, since the assumption table is
referenced far more densely throughout §2–§9 than the arm labels are. [A1]–[A5], [§5.4 arm table]

Also note (already known — carried per the brief): all of A22–A28 were appended to the **same
§2.5 "Research framing" table** as A19–A21, with no new subsection header, even though A22 (settle
counter, a state-representation fact), A24 (integrator scheme), A26 (`L_oracle` definition) and
A27/A28 (bay-scene parameters) are not research-framing claims in the sense A19–A21 are. The table
below reproduces the source's actual grouping rather than re-sorting it.

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

[§2, all 28 rows, all four columns, verbatim]

---

## Invariants I1–I10 (§3)

These hold at **every** stage. Violating one invalidates results silently, which is why each has a
test attached. [§3]

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

[§3, all 10 rows, verbatim]

**Already known (carried per the brief): I3 and I7 have no executable test** — their "Test" column
reads "§7.1" and "static check" respectively, neither of which is an EXIT-numbered, thresholded,
scriptable assertion.

**Not previously known — found by this decomposition:** the "Test" column for I1, I4 and I5 is each
**narrower than the invariant it is attached to**, and in two of the three cases a criterion exists
elsewhere in the document that *does* cover the missing half but is not cross-referenced in this
table. See Finding F1 (I4), Finding F3 (I5), Finding F4 (I1) below.

---

## The observation ladder O0–O4 (§6, intact)

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
[§6.1, in full]

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
[§6.2, in full]

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
[§6.3, in full]

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
[§6.4, in full]

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
[§6.5, in full]

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

[§6.6, all five EXIT-6.x criteria, in full — ID, criterion text, and complete threshold/rationale
text including every italic "why an earlier version got this wrong" clause]

---

## Reward specification (§7)

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
[§7.1, in full]

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
[§7.2, in full — see Finding F9 on this requirement's lack of an attached EXIT ID]

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
"improvement" that reintroduces a plateau. *(This is EXIT-0.12, owned by the Stage-0 file.)*
[§7.3, in full]

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
[§7.4, in full — see Finding F9 on the numeric weights (`w_gear`, `w_th`, `w_x`, `w_v`, `w_d`) that
have thresholds but no attached, config-asserting EXIT criterion, and Finding F11 on `β`'s undefined
numeric value]

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
[§7.5, in full — see Finding F2 on the absence of any EXIT criterion testing the settle-window logic
itself]

### 7.6 Store components, not the scalar

Persist a small named struct per transition (`phi_s`, `phi_s_next`, `terminal_kind`, `time_cost_raw`,
`action_cost_raw`, `gear_flag`, `clearance_penetration`, `settle_counter`) and **recompose the scalar
at sample time** from the current weights. This makes four otherwise painful things cheap: reweighting
without invalidating the buffer; the per-term reward-hacking diagnostics; Devlin–Kudenko dynamic
potentials across curriculum phases; and post-hoc analysis of which term dominated on the episodes
that collided.
[§7.6, in full]

---

## Evaluation protocol (§8, frozen at Stage 2, executed at Stage 4)

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
[§8, in full]

---

## Failure-mode diagnostic table (§9)

Each row: what you will *see* before you know the cause. [§9]

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

[§9, every row, verbatim — see Finding F12 on the two rows whose "Fix / test" column names a design
mitigation rather than an EXIT-numbered detection criterion]

---

## Consolidated reading list (§10)

Ordered by stage. `[V]` verified against the source · `[C]` certain to exist, details unchecked ·
`[?]` **unverified — open it before citing.** [§10]

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

[§10, in full, all rows and both citation traps, markers unchanged, no citations added or corrected]

---

## Notation (§11)

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

[§11, in full — note the table's own final row, `A1–A5 | the five arms of the O3 memory comparison`,
is the source of the assumption/arm-ID collision this decomposition disambiguates above]

---

## Contradictions and gaps found during decomposition

Ranked fatal → serious → minor. Two source pointers each. Items already told to me as known are
marked **(known)** and carried for completeness at the end, not claimed as discoveries.

### Fatal

**F1 — FATAL.** Invariant **I4** — guarding what the document itself calls "the most common silent
bug in the project" [A17] — cites only **EXIT-2.5** as its test, but by the document's own account
EXIT-2.5 checks a single one of the invariant's five named consumers (TD bootstrap mask). The
criterion that actually audits all five (Φ zeroing, n-step cut, episode logger, curriculum counter,
plus the bootstrap mask) is **EXIT-2.29**, added specifically to fix this ("I4 named five consumers
of terminated/truncated and gated one. → EXIT-2.29"), yet §3's invariant table was never updated to
cite it. A reader trusting the table alone would conclude I4 is protected by a test that covers one
of its five named failure sites — for the single bug class the whole document treats as the most
dangerous. [I4, §3] [§0.3, EXIT-2.29 note]

**F2 — FATAL.** **A22** (`settle_counter` is part of the state, "Revisit at: Never," i.e. a
permanent invariant-strength assumption whose absence in earlier versions made "the entire premise
of §5.2, §6.1 and H_A… false") has **no EXIT-numbered criterion anywhere in the document** that
tests it. Nothing scripted verifies that `settle_counter` increments correctly, resets on a tolerance
breach, is present in the observation at every rung, or that success genuinely requires
`K_settle = 5` *consecutive* qualifying steps rather than 4 or a non-consecutive count. A22 exists
specifically because this exact gap silently broke the "O0 is a full-state MDP" premise the whole
document is built on — the fix that was supposed to close it has no test that could catch a
regression back to the same bug. [A22, §2.5] [§7.5, success test]

### Serious

**F3.** Invariant **I5** ("the 3-circle body model appears only in the smooth reward term, never in
a metric **or a termination test**") cites only **EXIT-2.8** — but EXIT-2.8 tests only the *metric*
half ("Clearance metric uses exact OBB, not circles"). The *termination-test* half is actually
asserted by **EXIT-0.6**'s addendum ("and an assertion that the circle model is not importable by the
termination path"), a criterion the I5 row never cites. [I5, §3] [EXIT-0.6, §5.0]

**F4.** Invariant **I1** ("Rear-axle reference point **everywhere**") cites only **EXIT-0.2**, which
tests the kinematic turning-radius formula (`R_fit = L/tan δ`) — it says nothing about where the
*body footprint* sits relative to the rear axle. That question is exactly what **EXIT-0.10** was
added in v1.2 to close, described in the document's own words as "the largest hole in the whole
audit" — but I1's table row was never updated to add it. [I1, §3] [EXIT-0.10, §0.3]

**F5.** **A23** (actuator latency requires state augmentation with the in-flight command buffer) has
**no EXIT-numbered criterion** asserting that the augmentation is actually implemented when latency
domain-randomisation is enabled — no test that the observation gains the command-buffer slot, or
that the critic is not biased by state aliasing under randomised latency. [A23, §2.5] [§5.3 Build,
dynamics/scene randomisation list]

**F6.** **A26** declares that `L_oracle` is frozen as **specifically** the post-smoothing Hybrid A*
length, and §5.1(b) states plainly that of the three candidate denominators (`ell_RS`, `ell_HA*`,
`ell_OBCA`) "only one can be *the* frozen one" — but no criterion asserts, on the config or the
stored scenario data, that the shipped `L_oracle` actually equals `ell_HA*` rather than `ell_RS` or
`ell_OBCA`. EXIT-2.1 only checks that `L_oracle` is "present and finite," not which quantity it is. A
silently wrong denominator would corrupt every ρ metric in Stage 4 without tripping any gate. [A26,
§2.5] [§5.1(b)]

**F7.** **A27** was added specifically because deriving `W_gap` from `W_bay` inside the generator
(instead of declaring it) is "how this becomes a silent 0.69 m error in the difficulty label of every
frozen bay scenario" — but no criterion asserts the generator actually treats `W_gap` as an
independently declared config value rather than computing it from `W_bay`. EXIT-0.13 sweeps over a
`W_gap` grid as an *input* to the geometry check; it does not test the generator's own wiring. [A27,
§2.5] [§5.0(c′), "W_gap is not W_bay" box]

**F8.** The observation ladder's **O4** rung — "where the hand filter starts to fail… where the GRU
earns its keep," the row that §6.4's entire seven-item failure-precondition table builds toward —
lands only in **Stage 5** [§6.1], which is explicitly **optional** [§5.5, "(optional)"] and where
"Degraded perception (O4)" is just one of six candidate directions competing for a budget that is
"not additive" with the ~860 GPU-hours Stage 4 already spends [§5.5.1, "the cost, stated plainly"].
Nothing in the document guarantees O4 — the ladder's own narrative payoff — is ever built or tested.
[§6.1] [§5.5.1]

**F9.** §7.2's per-term weight-calibration requirement ("each non-terminal term's `|sum|` ≤
0.10·`R_success`… total ≤ 0.30·`R_success`") and §7.4's derived numeric weights (`w_th = 10.50`,
`w_x = 0.25`, `w_gear ≲ 1.0` for n=4) carry explicit thresholds but **no EXIT-ID and no "asserted on
the config object" pattern** — contrast EXIT-2.7, which *is* "asserted on the config object, so it
re-runs on every config change" for `P_collision`. Nothing in the exit-criteria machinery would catch
a shipped reward config whose weights have drifted from these derived values. [§7.2] [§7.4, EXIT-2.7
pattern for comparison]

**F10.** The document's own frontmatter still reads "Version 1.2 · 2026-08-06" although §0.4 (dated
2026-08-07) and §0.5 (dated 2026-08-07) were added afterward and the Appendix's last dated entry is
"v1.4 (2026-08-07)". The header was never bumped past v1.2 despite two further content passes, so a
reader who stops at the frontmatter believes the document is one version and one open-items list
behind where it actually is. [banner, line 5] [Appendix, v1.4]

### Minor

**F11.** `β`, the terminal-bonus grading multiplier in §7.4's `R_success(1 + β·g(final error))`, is
used without ever being assigned a numeric value in §7 where it is introduced. Its implied value can
only be back-calculated from EXIT-2.28's worked arithmetic elsewhere (`max(|R_success|·(1+β),
|P_collision|) = 120` with `R_success = 100` ⇒ `β = 0.2`), which is never stated as such. Similarly,
`c_max = 0.05` (the time-cost constant driving EXIT-2.7, EXIT-2.28 and §5.3(e)'s anti-suicide bound)
is never assigned to `−w_time` in §7.4 where that reward term is specified — it first appears only as
an illustrative "modest dense stream of `|c| = 0.05/step`" in §4.2's discount-arithmetic example.
[§7.4] [§4.2]

**F12.** Two rows of the §9 failure-mode table ("Checkpoint scores well in training and near-randomly
in a fresh process… VecNormalize statistics not saved" and "Performance collapses the moment O2 is
switched on… Binary flags were being normalised") give a design mitigation in the Fix/test column
("use fixed analytic scaling") rather than an EXIT-numbered detection criterion — unlike every other
row in the table. For the first, **EXIT-2.3** ("two runs of the same checkpoint in separate
processes: terminal class and episode length identical for 100%") is exactly positioned to catch
this symptom as a determinism failure, but the row does not cite it. [§9] [EXIT-2.3, §5.2]

**F13.** §4's DERIVED GEOMETRY block defines `R_rear_inner = 3.2156 m` and `outer turning diameter =
12.115 m`; neither value is referenced anywhere else in PLAN_MACRO.md. `R_front_inner = 4.7000 m`
fares only slightly better — it is used once, in §5.0(c)'s prose frame-setting, but no EXIT criterion
pins its numeric use down. [§4] [§5.0(c)]

**F14.** §4's bay reference-point table states `W_aisle = 5.005 m` at `η_bay = 1.15` and `W_aisle =
6.745 m` at `η_bay = 1.55` — but **EXIT-3.1** states the first point as `W_aisle = 5.00 m` and
**EXIT-2.27** states the second as `W_aisle ≥ 6.75 m`. Per the no-pick-a-value rule, both figures are
reported here rather than resolved: 5.005 vs. 5.00, and 6.745 vs. 6.75. [§4] [EXIT-3.1 / EXIT-2.27,
§5.3/§5.2]

**F15 — organisational (known-adjacent).** A22–A28 were appended to the **§2.5 "Research framing"**
table with no new subsection heading, even though A22 (state representation), A24 (integrator
scheme), A26 (Stage-1 protocol convention) and A27/A28 (bay-scene declarations) are not
research-framing claims in the sense A19–A21 are. This is a labelling/taxonomy issue, not a
falsifiability gap. [§2.5] [A22–A28 rows]

**F16.** **A25** ("Parallel parking and reverse bay parking are solved by **one policy** conditioned
on the scenario, not two") has no criterion that would fail if two separately trained policies were
shipped instead of one. EXIT-2.27 and EXIT-3.1 both gate per-family *numbers* ("Report the two
families separately — A25 buys one *policy*, not one *number*"), but reporting two family-specific
success rates is equally consistent with one conditioned policy or two independently trained ones —
nothing distinguishes them. Given A25's own "If wrong" column ("every 'success rate' in the document
is two numbers, K doubles, and the Stage-4 compute estimate doubles with it"), an undetected split
would silently double the §5.4.1 compute budget without tripping any gate. [A25, §2.5] [EXIT-3.1,
§5.3]

**Already-known items carried, not re-claimed as discoveries (per the brief):** I3/I7 have no
executable test [I3, I7, §3]; the A1–A5 assumption/arm-name collision (disambiguated and a rename
proposed above) [A1–A5, §5.4 arm table]; §0.3/§0.4/§0.5 each declare their own changes unreviewed
[§0.3, §0.4, §0.5]; the Fraichard & Scheuer "infinite chattering" claim is not verbatim-confirmed
[Appendix]; the Stage-4 statistics citation tail was never checked [§0.1].

---

## Coverage audit

**Sections this file carries in full:**

| § | Content | Status |
|---|---|---|
| Banner / §0 intro | Version header, organisation overview | carried, with F10 noted |
| §0.1 | Citation verification status table + summary | carried in full |
| §0.2 | What v1.1 changed (historical) | carried in full |
| §0.3 | What v1.2 changed, incl. all "still open" items | carried in full |
| §0.4 | What v1.3 changed (bay geometry) | carried in full |
| §0.5 | What v1.4 changed (preference learning placement) | carried in full |
| §1 | Project statement and scope | carried in full |
| §2.1–§2.5 | Assumptions A1–A28, all four columns | carried in full, **28/28 rows confirmed** |
| §3 | Invariants I1–I10, both columns | carried in full, **10/10 rows confirmed** |
| §4 | Reference parameters (VEHICLE / DERIVED GEOMETRY / BAY SCENE / DERIVED BAY GEOMETRY / INTEGRATION AND LEARNING) | carried in full, verbatim code block |
| §4.1 | Cusps and the cost of a steering reversal | carried in full |
| §4.2 | Discount arithmetic | carried in full |
| §5.4.1 | Compute budget and six-rung fallback ladder | carried in full (cross-cutting table, explicitly required even though nested in Stage 4's section) |
| §6.1 | The observation ladder table + decisions (a)/(b) | carried in full |
| §6.2 | Deliberately excluded (O2a radius-sensor reversal, occupancy grids, frame stacking) | carried in full |
| §6.3 | Encoding rules | carried in full |
| §6.4 | The O3 hypothesis, all six/seven preconditions, the failure-precondition table | carried in full |
| §6.5 | Privileged training caveat and the three cleaner formulations | carried in full |
| §6.6 | EXIT-6.1 through EXIT-6.5 | carried in full, **5/5 criteria, ID + criterion + complete threshold/rationale text** |
| §7.1–§7.6 | Reward specification, all six subsections | carried in full |
| §8 | Evaluation protocol | carried in full |
| §9 | Failure-mode diagnostic table | carried in full, **every row** |
| §10 | Consolidated reading list, all five stage blocks + two citation traps + preference-RL block | carried in full, no citations added or corrected |
| §11 | Notation table | carried in full |
| Appendix | Provenance, both verification-pass tables (v1.1's nine agents, v1.2's two audits), v1.3/v1.4 validation tables and open-items lists | carried in full |

**Sections belonging to sibling stage files (not carried here, by design — this file's scope is
everything orthogonal to the stages):**

| § | Belongs to |
|---|---|
| §5.0 (incl. 5.0(a)–(g), 5.0(c′), EXIT-0.1–EXIT-0.15) | Stage-0 plan file |
| §5.1 (incl. EXIT-1.1–EXIT-1.14) | Stage-1 plan file |
| §5.2 (incl. EXIT-2.1–EXIT-2.29) | Stage-2 plan file |
| §5.3 (incl. EXIT-3.1–EXIT-3.11) | Stage-3 plan file |
| §5.4, §5.4.1's narrative text beyond the table itself (incl. EXIT-4.1–EXIT-4.12) | Stage-4 plan file |
| §5.5, §5.5.1 | `stages/PLAN_S5.md` (already produced by a sibling agent) |

**Nothing was dropped.** Every §-numbered subsection within this file's assigned scope (§0.1–0.5,
§1, §2.1–2.5, §3, §4/§4.1/§4.2, §6.1–6.6, §7.1–7.6, §8, §9, §10, Appendix) is carried above in full.
The only content omitted from verbatim transcription is the Stage 0–5 build/theory/derivation
sections themselves (§5.0–§5.5's bodies), which belong to sibling files by explicit assignment, and
which this file instead references only through the Stage map and artefact-dependency-graph
synthesis, each claim there pointing back to its source line.

**Assumption and invariant counts, stated explicitly:** A1–A28 = **28 assumptions**, all four
columns (#, Assumption, If wrong, Revisit at), confirmed transcribed. I1–I10 = **10 invariants**,
both columns (Invariant, Test), confirmed transcribed.

**EXIT-6.x carried:** EXIT-6.1, EXIT-6.2, EXIT-6.3, EXIT-6.4, EXIT-6.5 — **5 of 5**, each with full
ID/criterion/threshold text including every italicised rationale clause.

**Forced drops or unfaithful transcriptions:** none identified. Every table this file's scope
requires intact (§2's 28-row/4-column assumption table, §3's 10-row invariant table, §9's full
failure-mode table, §5.4.1's compute-budget and fallback-ladder table, and all five EXIT-6.x
criteria) was reproduced without shortening, paraphrase, or bullet-ising.

**Claims relayed from another section's authority rather than checked directly by this
decomposition:** the Appendix's "Numerical claims computed independently by two or more agents, in
agreement" list (`R_min = 3.9466`, `R_front_outer = 6.0574`, `R_swept_inner = 3.0216`, the γ^N table,
the 3-circle covering radius 1.2121 m) is carried as PLAN_MACRO.md states it, not independently
recomputed by this decomposition (recomputing would violate the no-re-derivation constraint in any
case). Likewise, the v1.3 swept-body agreement figures (2.5e-11 m, ≤1e-9 m / 1.5e-5 m, 1.1e-16 m) and
the v1.1 nine-agent verification-pass results table are relayed exactly as reported in the
Appendix — this file did not re-run or re-check those agents' work, only transcribed their reported
outcome.
