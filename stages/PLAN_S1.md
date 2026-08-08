# PLAN_S1 — Stage 1

Source of truth: `PLAN_MACRO.md`. This document decomposes **§5.1 Stage 1 — Classical planning
baselines** in full, plus **§4.1** ("Cusps and the cost of a steering reversal"), plus
**EXIT-1.1 .. EXIT-1.14** whole. Supporting reads: §0.1, §0.3, §0.4, §0.5, §2, §3, §4, §11, and
(for cross-checking only) §9 and §10. All citation markers `[V]/[C]/[?]/[D]` and every
"unreviewed" warning are carried through unchanged [§0.1].

---

## Goal (verbatim)

§5.1 has **no bolded `**Goal.**` label** the way §5.0 does (§5.0 opens "**Goal.** A unit-tested
geometric and kinematic core..." [§5.0]). §5.1 opens directly with its rationale paragraph, which
is the closest thing to a goal statement this stage has:

> "**This stage is infrastructure, not an afterthought.** Its outputs are consumed by every later
> stage: the feasibility oracle filters curriculum sampling, the path length is the optimality
> denominator, the reverse-curriculum generator comes from it, and it is the demonstration source.
> Building it after the RL is the single most common ordering mistake in projects like this."
> [§5.1]

Stage title, verbatim: "### 5.1 Stage 1 — Classical planning baselines *(still no RL)*" [§5.1].

---

## Entry conditions — what Stage 0 must have produced, by artefact

Stage 0's **Build** section lists the artefacts Stage 1 is built on top of:

```
worldstate.py   WorldState dataclass (truth). ego (x,y,theta,v,delta); objects (N,6) =
                (x,y,theta,l,w,type); bounds; settle_counter (int, 0..K_settle).
dynamics.py     Rear-axle bicycle, explicit substep integration, action clamping.
geometry.py     obb_corners, sat_overlap, obb_signed_distance (32 point-segment),
                body_circles, ccd_sweep.
render.py       matplotlib patches + trajectory replay.
tests/          see exit criteria
```
[§5.0 Build]

Specific Stage-1 dependencies on these artefacts, traced through §5.1's own text:

- **`geometry.py`'s exact SAT** is reused directly by the feasibility oracle: "run **the same exact
  SAT test the environment uses, with the same footprint**. A mismatch here presents as an
  unexplained success-rate ceiling." [§5.1(a) step 3]
- **`Δs ≤ 0.026 m`**, the collision-check discretisation used throughout Stage 1 (feasibility oracle,
  build-order step 2, EXIT-1.5), is imported "from EXIT-0.5's bound" [§5.1(a) step 2; §5.1 Build
  order step 2].
- **`R_min = 3.9466 m`**, used to fix RS candidate words at "ρ = R_min" [§5.1(a) step 1], and
  **`kappa_max = 0.25338`**, used in the curvature-discontinuity arithmetic [§5.1 curvature section],
  both come from §4's `DERIVED GEOMETRY` block [§4].
- **Correct footprint placement (EXIT-0.10)** is a load-bearing precondition, not merely nice to
  have: EXIT-0.10's own rationale states that if the footprint is wrong, "**every Stage-0, Stage-1
  and Stage-2 criterion still passes**... and **EXIT-1.9's oracle-soundness check is consistent
  with the same error**." [EXIT-0.10]
- **Enforced actuator clamps (EXIT-0.11)** are a precondition for every Stage-1 baseline comparison
  to be meaningful: "An environment that lets `δ` drift gives the RL car a turning radius smaller
  than `R_min`... a capability Reeds–Shepp, Hybrid A\* and the tracked expert all lack." [EXIT-0.11]
- **The bay closed form (EXIT-0.13, EXIT-0.14, EXIT-0.15)** supplies the analytic bracket
  `[3.5100, 4.3519]` that Stage 1's Hybrid A\* is cross-checked against, and the goal-pose /
  nose-in-rejection test the bay family's success test must satisfy. [EXIT-0.13, EXIT-0.14,
  EXIT-0.15]

**Caveat — two of these entry gates cannot actually complete before Stage 1 exists.** EXIT-0.8
("Hand-derived minimum-slot-length curve validated against numerical bisection... bisect on slot
length using your own single-cusp-restricted Hybrid A\*" [EXIT-0.8, §5.0(c)]) and EXIT-0.14(c)
("At Stage 1, bisect `W_aisle` with Hybrid A\*... Threshold: **all three**." [EXIT-0.14]) both
require Hybrid A\*, which is Stage 1 Build-order step 6 [§5.1 Build order step 6]. §0.3 itself
already lists the EXIT-0.8 instance as an open "Stage-ordering leftover" [§0.3 item 4]; see
**Blocked / out-of-order items** below for the EXIT-0.14(c) instance, which is not on that list.

---

## Assumptions live here

Reproduced verbatim from §2, restricted to the assumptions this stage's build, exit criteria, or
rationale text actually invoke.

| # | Assumption | If wrong | Revisit at |
|---|---|---|---|
| **A2** | The reference point is the **rear-axle midpoint**, not the CoG. | The heading ODE `θ̇=(v/L)tan δ` is *only* valid at the rear axle. Using it with a CoG reference gives a systematically wrong turning radius. | Never — this is invariant I1 |
| **A6** | Actuators are rate-limited but otherwise ideal: no backlash, no deadband, no latency. | Real steering has 100–200 ms latency. Deliberately introduced as a Stage 3 randomisation. | Stage 3 |
| **A9** | The scenario distribution is fixed and defined by a generator with a recorded seed. | Every historical comparison becomes incomparable. Enforced by hashing (EXIT-2.1). | Never |
| **A10** | "Feasible" means **"solvable by our Hybrid A\* at the declared grid resolution"**, not "geometrically possible". Hybrid A\* is resolution-complete, not complete. | The frozen eval set is biased toward scenarios the planner can solve; the RL success rate is measured against a denominator that is itself a lower bound on true feasibility. **State this in the thesis rather than hide it.** | Never — state it |
| **A15** | Reeds–Shepp demonstrations must be **executed through the environment by a tracking controller**, never used as raw (state, action) pairs. | RS paths have discontinuous curvature; the implied `δ̇` is unbounded. Raw RS actions lie outside the action box. | Never |
| **A24** | Integration is **explicit Euler with zero-order hold** on the action across the 5 substeps. | Never stated in v1.0/v1.1, yet EXIT-0.2's closure tolerance and EXIT-0.5's per-substep displacement bound both depend on it. A switch to RK4 changes both. | Stage 0 |
| **A25** | Parallel parking and reverse bay parking are solved by **one policy** conditioned on the scenario, not two. | If two, every "success rate" in the document is two numbers, K doubles, and the Stage-4 compute estimate doubles with it. Never stated. | Stage 2 |
| **A26** | `L_oracle` is the **post-smoothing Hybrid A\*** path length, frozen with the scenario set. | ρ is not comparable across experiments if this drifts. §5.1 offers three denominators; only one can be *the* frozen one. | Stage 1 |
| **A27** | **`W_gap` — the free lateral width at the bay mouth — is a declared scene parameter, not something the generator derives from `W_bay`.** Default is the conservative wall model `W_gap = W_bay`. | The two models differ by `W_bay − w` = 0.65 m, which is **0.69 m of required aisle**. Derived silently, every frozen bay scenario carries a mislabelled difficulty and the EXIT-0.14 bracket is checked against the wrong number. Added v1.3. | Stage 0 |
| **A28** | The bay family's difficulty scalar is the **aisle slack ratio** `η_bay = W_aisle / W_aisle_min(W_gap; R_min, c=0)`, and `W_aisle` — not `W_bay` — is the axis that gets varied. | `W_bay` has ~0.7 m of usable range against `W_aisle`'s ~2.8 m; banding on `W_bay` gives a curriculum with almost no dynamic range and a Stage-3 gate that means nothing. Added v1.3. | Stage 3 |

A26 is the one whose "Revisit at" column literally says **Stage 1** — see **Derived by this
decomposition** below for what happens when its text is checked against §5.1(b)'s own denominator
table.

---

## Invariants live here

Reproduced verbatim from §3, restricted to invariants this stage's text or exit criteria invoke.

| # | Invariant | Test |
|---|---|---|
| **I1** | Rear-axle reference point everywhere. `R = L/tan δ` refers to the rear axle only. | EXIT-0.2 |
| **I5** | Exact SAT decides collision/termination. The 3-circle body model appears **only** in the smooth reward term, never in a metric or a termination test. | EXIT-2.8 |
| **I8** | The per-object feature vector has **identical width at every observation stage** O0–O4. | EXIT-1.12 |
| **I9** | The frozen eval set is hashed and never regenerated. | EXIT-2.1 |

I5's discipline ("3-circle model only in the smooth reward, exact SAT for termination/metrics") is
exactly what §5.1(a) step 3 imports for the feasibility oracle [§5.1(a); §5.0(e)]. I8 is tested
*at* this stage, by EXIT-1.12 [I8; EXIT-1.12] — that criterion's own dependency issue is listed
under **Known-unreviewed content** below (it needs the Stage-2 Observer). I9's formal test
(EXIT-2.1) is a Stage-2 criterion even though the invariant itself is stated to hold at "every
stage" [I9] — Stage 1's "400-scenario set" [EXIT-1.7] and "frozen set" [EXIT-1.9, EXIT-1.11] are
presumably the same frozen object I9 governs, but nothing in §5.1 formally checks the hash before
Stage 2.

---

## Theory to read

Reproduced verbatim from §5.1.

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

**Not part of my assigned scope but flagged for coverage:** §10's "Stage 1 — classical planning"
consolidated list carries additional citations not in the table above — most notably the two OBCA
solver papers (Zhang, Liniger, Sakai & Borrelli 2018, CDC; Zhang, Liniger & Borrelli, *IEEE TCST*
29(3)) and the original A\* paper (Hart, Nilsson & Raphael 1968) — all `[?]` — plus the Stanley
citation-trap pair (Hoffmann et al. 2007 for the controller, Thrun et al. 2006 for the system)
[§10]. §10 also documents the Fraichard & Scheuer venue trap: "*IEEE Transactions on **Robotics***
20(6):1025–1035 — **not** *Transactions on Robotics and Automation*" [§10, "Two citation traps
already identified", item 1]. These are reading-list rows, copied here only to note their
existence, not corrected or added to — per the "no new citations" rule, I have not verified or
altered any marker.

---

## Get these numbers right

Verbatim from §5.1:

> **48 = WORDS** (path types) in the sufficient set, RS Table 1. **68 = FORMULAS** (some words admit
> two solutions of the minimising equations; RS observed empirically that one per word always
> suffices but explicitly did **not** prove it). **46 = Sussmann & Tang's reduction** (L⁻L⁺L⁻ and
> R⁻R⁺R⁻ are unnecessary). **9 = compact base families.** Max 5 pieces, max 2 cusps.
> Dubins: **6 words**, max 3 pieces, and for LRL/RLR the middle arc must be **strictly > π**.
>
> Write it as: *"48 words (Reeds & Shepp 1990, Table 1), of which 46 suffice (Sussmann & Tang 1991)."*
> [§5.1, "Get these numbers right"]

Supporting provenance (not part of §5.1 itself): the Appendix lists `R_min = 3.9466`,
`R_front_outer = 6.0574`, `R_swept_inner = 3.0216` and the 3-circle covering radius `1.2121 m` as
"computed independently by two or more agents, in agreement" [Appendix], and explicitly warns that
the `v_max/a_max = delta_max/delta_dot_max = 1.000` "knife edge" arithmetic is **not** on that
corroborated list any more — "the arithmetic is right but its interpretation was refuted in v1.1
(§4.1); listing it as corroborated was itself an error, since only the arithmetic was ever
corroborated, not the conclusion drawn from it" [Appendix]. This bears directly on how much weight
to put on §4.1's numbers, reproduced next.

---

## The curvature-discontinuity problem (including §4.1)

### §4.1 — Cusps and the cost of a steering reversal (verbatim)

> **Version 1.1 correction.** v1.0 of this document presented the material below as a "feasibility
> knife edge" and got it wrong in three ways: the inequality is not an *iff*, the parameter set does
> not sit *on* the edge in any operationally meaningful sense, and two of the three stated
> randomisation directions were **inverted**. The corrected treatment follows. Retained because the
> underlying quantity — what a cusp costs — is real and matters for the reward and the curriculum.
>
> **The bang-bang statement.** *Under a bang-bang reversal at `|a_long| = a_max`*, a cusp absorbs a
> full lock-to-lock steering swing without dwelling at v = 0 iff
>
> ```
> v / a_max  >=  delta_max / delta_dot_max
> ```
>
> with `v` the speed at which the cusp is entered. At `v = v_max` both sides equal exactly 1.000 s.
>
> **But `a_max` is an upper bound, not a mandate, so this is not a feasibility boundary at all.**
> The reversal takes `T = 2v/|a|`; the swing needs `T_s = 2·delta_max/delta_dot_max = 2.0 s`; the
> policy needs `T >= T_s`, i.e. `|a| <= 2v/T_s`. Since `|a|` may be chosen arbitrarily small, **a
> dwell-free reversal is always available at any `v > 0`, and `a_max` never binds.** The deceleration
> required to reverse in exactly `T_s` is `a_req = v·delta_dot_max/delta_max = v`, which is `<= a_max`
> at every admissible speed.
>
> **What actually varies is cost, not feasibility:**
>
> ```
> dwell-free reversal:  extra travel = v * delta_max/delta_dot_max metres
>                       (0.50 m at v = 0.5 m/s), versus v^2/a_max = 0.167 m for bang-bang
> dwelling reversal:    extra time >= 1.33 s at v = 0.5 m/s, at ~zero extra distance
> ```
>
> This is a trade-off the **reward** resolves, not a constraint the dynamics impose.
>
> **The speed dependence is the real design fact, and it points the opposite way to v1.0's warning.**
> Under the bang-bang reading the available reversal time `2v/a_max` shrinks linearly with approach
> speed while the 2.0 s swing time is fixed:
>
> ```
> v = 1.5 -> 2.000 s   fits exactly, zero margin
> v = 1.0 -> 1.333 s   short by 0.667 s =  6.7 policy steps
> v = 0.7 -> 0.933 s   short by 1.067 s = 10.7 policy steps
> v = 0.5 -> 0.667 s   short by 1.333 s = 13.3 policy steps
> v = 0.3 -> 0.400 s   short by 1.600 s = 16.0 policy steps
> ```
>
> Parking cusps happen at 0.3–0.7 m/s, never at 1.5 m/s. So the parameter set does not sit *on* an
> edge — under bang-bang it sits on the **wrong side of it for every realistic cusp**, before any
> randomisation. The 1.000 s coincidence at `v_max` is real but operationally irrelevant.
>
> **Budget it.** A 4-cusp manoeuvre in which the policy dwells rather than decelerating gently costs
> roughly **53 policy steps of pure dwell** against `max_steps = 400`. That is 13% of the episode
> budget and it interacts directly with §5.3(e)'s succeed-versus-stall margin, which is already
> labelled MARGINAL at N = 400.
>
> **Randomisation directions — v1.0 had these backwards.** Let the slack be
> `S = v/a_max − delta_max/delta_dot_max`. Then `dS/da_max = −v/a_max² < 0` and `dS/dv = +1/a_max > 0`:
> **lowering `a_max` makes a cusp *easier*** (the reversal takes longer, giving the steering more time),
> and **raising `v_max` also makes it easier.** The parameters that make a cusp harder are those that
> shorten the reversal or lengthen the slew:
>
> | Randomising… | Effect on the cusp |
> |---|---|
> | `delta_dot_max` **down** | harder — longer slew |
> | `delta_max` **up** | harder — longer slew |
> | `a_max` **up** | harder — shorter reversal |
> | `v_max` **down** | harder — shorter reversal |
>
> **Action:** treat cusp cost as a reward-design and curriculum question (§7.4's `w_gear` budget), not
> as a feasibility constraint. If you randomise the four parameters above, know which direction makes
> the task harder — and note that it is the opposite of what intuition suggests for `a_max`.
> [§4.1, whole section]

**Family attribution note (mine, not the document's):** §4.1's text is written generically ("a
cusp", "the reversal") and its worked "4-cusp manoeuvre" example [§4.1, "Budget it"] is not
attributed to either task family. §5.0(c′) states the *canonical* bay manoeuvre is single-cut —
"(1) forward along the aisle... (2) **one reverse arc**... (3) reverse straight down" [§5.0(c′),
"The manoeuvre"] — i.e. exactly **one** gear change, one cusp, not four. So the "4-cusp" budget
figure is not executable by the canonical bay manoeuvre as described and is most plausibly a
parallel-parking illustration (parallel parking's multi-shunt tight-slot case), but §4.1 never says
so. Per this stage's mandate to flag single-family coverage explicitly [hard constraint 6], I note
it rather than assume it.

### §5.1 — The curvature-discontinuity problem, quantified (verbatim)

> This is more severe than intuition suggests. An RS path has piecewise-constant curvature, so
> `δ(σ) = atan(L κ(σ))` jumps instantaneously between {−0.6, 0, +0.6} rad. At `δ̇_max = 0.6 rad/s`:
>
> ```
> Steering slew time and consumed arc length:
>     0 -> full lock         t = 1.0 s   ell = 1.5 m at v_max,  0.5 m at v = 0.5
>     full lock -> full lock t = 2.0 s   ell = 3.0 m at v_max,  1.0 m at v = 0.5
>     (a quarter circle at R_min is only 6.199 m long — a lock-to-lock slew consumes 48% of it)
>
> Clothoid ramp deflection, EXACT for a linear-in-time steering ramp at constant speed:
>     Dtheta_ramp = -( v / (L * delta_dot_max) ) * ln( cos(delta_max) )
>     v=0.3 -> 2.04 deg    v=0.5 -> 3.39 deg    v=1.0 -> 6.79 deg    v=1.5 -> 10.18 deg
>
> Open-loop pose error, rate-limited vehicle vs ideal RS (RK4 @ 2e-4 s):
>     (A) NON-CUSP C->C join (delta: +0.6 -> -0.6), the worst case:
>             v=0.5 : 0.684 m, 14.52 deg      v=1.5 : 1.540 m, 43.55 deg
>     (B) NON-CUSP C->S join (delta: +0.6 -> 0):
>             v=0.5 : 0.168 m,  3.39 deg      v=1.5 : 0.446 m, 10.18 deg
>     (C) CUSP join with a trapezoidal speed profile at a_max, full lock-to-lock:
>             0.245 m, -8.02 deg
> ```
>
> **The key design insight, and it falls out of the already-chosen action space:** because the action
> is `(a_long, δ̇)` with bounded `a_long`, the car **must** decelerate through zero at every gear
> reversal, and that dead time is free steering-slew time. So a curvature discontinuity **at a cusp is
> nearly free** (0.245 m), while the same discontinuity at a **non-cusp C→C join costs 6.3× more**
> (1.540 m at v_max — one third of the car's own length). This is why HC (Hybrid Curvature) steering
> is the right choice over full CC: pay for continuity only where it is not already free.
>
> Note also (Fraichard & Scheuer): for the curvature-rate-constrained car, whenever the true shortest
> path contains a line segment, the optimum involves **infinite chattering** — an infinite number of
> clothoid arcs accumulating at the segment endpoints. There is therefore **no clean closed-form
> optimum** for the vehicle you actually simulate. This matters for how you word optimality claims.
> [§5.1, "The curvature-discontinuity problem, quantified"]

**Uncertainty marker carried through [hard constraint 4]:** the citation Fraichard & Scheuer (2004)
is itself `[V]` — independently verified to exist, at the correct venue [§5.1 reading table; §10
trap 1] — but the specific "infinite chattering" *claim* attributed to it above is **not**
verbatim-confirmed: "the checker could not retrieve readable full text (HAL bot-blocked,
ResearchGate 403, CiteSeerX 404). Secondary sources are consistent with it but it is **not
verbatim-confirmed**. Treat as plausible, not established." [Appendix, v1.2 pass, open item 4;
also §0.3 item 7]. Do not treat the chattering claim as settled.

---

## The four consumers

Verbatim from §5.1:

> **(a) Feasibility oracle** `is_feasible(q_start, slot) -> bool`
> 1. Compute all RS candidate words at ρ = R_min; take in increasing length order.
> 2. Discretise each at Δs ≤ 0.026 m (from EXIT-0.5's bound).
> 3. At each sample place the oriented rectangle and run **the same exact SAT test the environment
>    uses, with the same footprint**. A mismatch here presents as an unexplained success-rate ceiling.
> 4. Accept on the first clean path.
>
> **Soundness caveat:** collision-checked RS is **sound but incomplete**. RS-feasible ⇒ feasible; but
> RS-**in**feasible does **not** imply infeasible, because RS restricts to ≤2 cusps and minimum-radius
> arcs, while tight parking often needs more shunts. Use RS as a fast **accept**, Hybrid A* as the
> **reject** authority.
>
> **(b) Optimality denominator.** Measure `ell_RL` as `∫|v| dt` over **substeps** (arc length, not
> displacement — a 3-point turn has near-zero displacement). Report three denominators:
>
> | Denominator | Meaning | Caveat |
> |---|---|---|
> | `ell_RS` (obstacle-free) | lower bound on any bounded-curvature path | only meaningful when the RS path is itself collision-free; otherwise ratio < 1 is possible and the metric is meaningless |
> | `ell_HA*` (collision-checked, smoothed) | feasible and obstacle-aware | neither optimal nor complete, so not a bound |
> | `ell_OBCA` (NLP warm-started from HA*) | closest to a true optimum | uses the **same exact convex-body collision model** as your SAT check |
>
> **The achievable floor is strictly greater than 1 and is not a property of the policy**: since
> `|δ̇| ≤ 0.6 rad/s`, no controller can execute an RS path. Report `ratio_floor = ell_HC / ell_RS > 1`.
> Without it a reported ratio of 1.15 is uninterpretable.
>
> **(c) Reverse-curriculum generator.** See §5.3.
>
> **(d) Demonstrations.** See §5.3, and **A15**.
> [§5.1, "The four consumers"]

The `ell_HC` symbol in (b) is examined under **Derived by this decomposition** below — it does not
match any of the three denominators the same subsection just named.

(c) and (d) are cross-checked against §5.3's own text (not part of my assigned scope, read only for
this cross-check): §5.3's "Build" opens "**Reverse curriculum from the Stage-1 oracle**" and its
step 1 is "Plan a collision-free reference path `P(sigma)`... Cache it" [§5.3 Build, step 1], and
its "Demonstrations" block opens "Generate by **running the Stage-1 tracker inside the real
environment**" [§5.3 Build, "Demonstrations"] — both consistent with (c) and (d) being genuine
consumers of Stage-1 outputs (RS/Hybrid A* paths, the feasibility oracle, the pure-pursuit tracker)
built later, not artefacts Stage 1 itself must produce.

---

## Build order

Verbatim from §5.1:

> 1. RS closed form (9 base families, symmetry-expanded) — **validate against the metric axioms before
>    anything consumes it**
> 2. Collision-checked path validator at Δs ≤ 0.026 m — shared by everything downstream
> 3. Feasibility oracle
> 4. `h_nhwo` lookup table (this is just RS distance — free once (1) works)
> 5. `h_hwo` 2D Dijkstra on the obstacle grid
> 6. Hybrid A* (bucketed continuous state; `h = max(h_nhwo, h_hwo)`; analytic RS expansion near the
>    goal, **collision-checked**; gradient post-smoothing)
> 7. **Speed profiler** — *not part of any of these planners.* Dolgov et al. explicitly do not model
>    speed. RS and Dubins are pure path planners with no notion of time. Your action space is
>    `(a_long, δ̇)`, so every baseline needs its own speed profile.
> 8. Rear-axle **pure pursuit** tracker
>
> **Use pure pursuit, not Stanley.** Stanley is a **front-axle** law derived for forward motion; in
> reverse the feedback sign makes the cross-track loop **unstable**, and the failure is a smooth
> divergence that looks like a tuning problem. Pure pursuit is rear-axle referenced — already your
> kinematic reference — and extends to reverse by looking backwards. Size the lookahead against the
> **rate** limit, not the speed: `ell_min` must exceed the lock-up length `v·Δδ/δ̇_max`
> (≥ 0.75 m at v = 0.5), or you get a steering limit cycle riding against the `δ̇` clamp.
> [§5.1, "Build order"]

Step 6's "gradient post-smoothing" is what makes the collision-checked Hybrid A\* output the
`ell_HA*` denominator of (b) [§5.1(b); §5.1 Build order step 6]. No step in this list produces the
OBCA-warm-started `ell_OBCA` denominator or an independent numerical OCP solver, needed by EXIT-1.4
— already flagged; see **Blocked / out-of-order items**.

---

## Exit criteria (ALL of EXIT-1.1 .. 1.14, whole)

Copied whole, table rows verbatim, including every italic rationale/positive-control clause.

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

[EXIT-1.1 .. EXIT-1.14, whole table]

---

## Blocked / out-of-order items

**Already documented in PLAN_MACRO itself:**
- EXIT-1.12 needs the Stage-2 Observer — an ordering inversion the document does not resolve within
  Stage 1's own text [EXIT-1.12; cf. §6, Observer, not in my scope].
- EXIT-1.4's independent numerical OCP, and the `ell_OBCA` denominator in §5.1(b), both "need two
  solvers absent from Stage 1's build list" [§0.3 item 4; §5.1(b); §5.1 Build order — no NLP/OCP
  step appears in steps 1–8].
- EXIT-0.8 needs Hybrid A\*, itself a Stage-1 artefact (Build order step 6) — flagged in §0.3 as a
  "Stage-ordering leftover" [§0.3 item 4; §5.0(c); §5.1 Build order step 6].

**Not on that list — see Derived by this decomposition below for the argument:**
- EXIT-0.14(c) has the same defect as the already-documented EXIT-0.8 case (Stage-0 exit criterion
  requiring Stage-1's Hybrid A\*), but was added in v1.3, after the v1.2 audit that produced §0.3's
  "Stage-ordering leftovers" list, and is not on it.

---

## Known-unreviewed content this stage depends on

- **EXIT-1.13 and EXIT-1.14 are new in v1.4 and entirely unreviewed** — v1.4's own preface: "Nothing
  here is [machine-checked]. The citations are from memory, the four-arm design has had one pair of
  eyes on it..." [§0.5]. Both criteria are reproduced above and belong to Stage 1's gate.
- **The bay geometry that EXIT-0.13/0.14/0.15 certify, and that Stage 1's EXIT-1.7 bay-column and
  EXIT-0.14(c)'s Hybrid A\* cross-check depend on, is v1.3 content**, machine-checked against an
  independent numerical sweep but with unreviewed *framing*: "everything in §0.4 is new, and
  therefore unreviewed... has had exactly one pair of eyes on it" [§0.4, closing paragraph].
- **The Fraichard & Scheuer "infinite chattering" claim, quoted in the curvature-discontinuity
  section above, is not verbatim-confirmed** [Appendix v1.2 pass, open item 4; §0.3 item 7].
- **Every v1.2 correction — which includes all of §4.1 as currently written — is itself unreviewed**:
  "Every v1.2 correction above is itself unreviewed. That is exactly the state v1.1 was in when it
  shipped four fatal errors. A fourth verification pass is warranted before any of this is built on."
  [§0.3, "Still open after v1.2", item 1]. §4.1 in its present form is a v1.1 rewrite that received
  further edits in v1.2 (the appendix note on the corroborated-numbers list is one such edit)
  [Appendix].
- **The low-priority tail of the Stage-4 statistics citations was never checked** [§0.1] — not
  Stage-1 content, noted only because §5.1's own reading list is clean by contrast (all rows in
  §5.1's table carry `[V]`, `[C]`, or `[?]` markers that *were* reached by the v1.1 citation pass,
  per the "planning" section's coverage: "opened the actual PDFs of Reeds & Shepp 1990, Sussmann &
  Tang SYCON-91-10, Fraichard & Scheuer 2004, Banzhaf et al. 2017, Dolgov et al. 2010, and LaValle
  §15.3.2" [Appendix, provenance]).

---

## Failure modes here

Pulled from §9 (outside my assigned read list, consulted only to populate this template section;
rows unmodified), restricted to rows whose "Fix / test" column points at a Stage-1 criterion or
Stage-1 build content:

| Symptom | Likely cause | Fix / test |
|---|---|---|
| Every agent, including the Stage-1 tracker, shows ρ > 1 that never improves | `ell_RS` used as the denominator — it is an **infeasible** lower bound | report `ratio_floor`; EXIT-1.11 |
| Forward segments track well; the moment the car reverses, cross-track error grows smoothly and it jackknifes | Stanley used in reverse (front-axle law, wrong feedback sign) | rear-axle pure pursuit |
| Steering command is a visible triangle wave riding against the `δ̇` clamp; the car weaves | Pure-pursuit lookahead sized from speed, ignoring the **rate** limit | `ell_min > v·Δδ/δ̇_max` |
| Hybrid A* suddenly much faster, paths longer and oddly angled, RL optimality ratio mysteriously improves | `h_nhwo` table built with an inflated turning radius → heuristic inadmissible → greedy search | EXIT-1.6 |
| Planning suspiciously fast, ~100% success including on infeasible scenarios, occasional path straight through a parked car | Analytic RS expansion not collision-checked | EXIT-1.7 |
| Success degrades under Stage-3 randomisation in a way uncorrelated with observation noise | Cusp cost rose: `δ̇_max` lowered, `δ_max` raised, `a_max` **raised**, or `v_max` **lowered**. *(v1.1's "knife edge" framing was withdrawn — see §4.1)* | §4.1 |
| Reported clearances systematically slightly too small, worst when nosing diagonally into a bay corner | SAT face-normal gap used as the separation distance (vertex–vertex case) | EXIT-0.4 |

[§9, rows keyed to EXIT-1.6, EXIT-1.7, EXIT-1.11, §4.1, EXIT-0.4, and the two unkeyed pure-pursuit
rows immediately below EXIT-1.11's row]

---

## Derived by this decomposition (not in PLAN_MACRO)

Everything below is my own cross-reference analysis, built by comparing verbatim spans of
PLAN_MACRO against each other. None of it is a PLAN_MACRO claim in its own right — the raw
material each conclusion rests on is pointed to individually.

1. **`ell_HC` is used by `ratio_floor` and by EXIT-1.11, but is never one of the three denominators
   §5.1(b) offers, and nothing in the Build order produces it.** §5.1(b)'s own denominator table
   names exactly three quantities: `ell_RS`, `ell_HA*`, `ell_OBCA` [§5.1(b) table]. The very next
   paragraph in the same subsection instead reports `ratio_floor = ell_HC / ell_RS` [§5.1(b),
   "achievable floor" paragraph], and EXIT-1.11 makes that same `ell_HC/ell_RS` ratio a mandatory,
   100%-of-frozen-set, ">1.0 for 100%" Stage-1 gate [EXIT-1.11]. The string `HC` appears exactly
   four times in the whole document: once in the Stage-1 reading list ("Banzhaf, H. et al. (2017).
   'Hybrid Curvature Steer.'... HC (not CC) is the right steering function" [§5.1 reading table]),
   once introducing "HC (Hybrid Curvature) steering" as a *method* for producing continuous-curvature
   references [§5.1, curvature-discontinuity section, "key design insight" paragraph], and the two
   occurrences in `ratio_floor`/EXIT-1.11 already cited. At no point does the document define an
   `ell_HC` *symbol* — a path length — the way it defines `ell_RL`, `ell_RS`, `ell_HA*`, and
   `ell_OBCA` [§5.1(b)]. §11's Notation table, which lists `ρ = ell_RL/ell_oracle` and defines
   `Δs`, does not mention `ell_HC` or `ell_HA*` either [§11]. The Build order's 8 steps produce RS
   (step 1), Hybrid-A\*-with-gradient-smoothing (step 6), and a pure-pursuit tracker (step 8)
   [§5.1 Build order] — no step produces an "HC-steered" reference path. Two readings are both
   consistent with the text and neither is confirmed: (i) `ell_HC` is a typo/rename for `ell_HA*`,
   in which case EXIT-1.11 silently duplicates whatever `ell_HA*`-based metric Stage 1 already
   reports; or (ii) `ell_HC` genuinely denotes the length of a separately HC-steered reference path
   (consistent with EXIT-1.8's "on an HC/CC reference" clause [EXIT-1.8]), in which case a required,
   graded Stage-1 exit criterion depends on an artefact the Build order never schedules.

2. **EXIT-0.14(c) has the same Stage-0-needs-Stage-1 defect as EXIT-0.8, but is not on §0.3's list of
   known Stage-ordering leftovers.** EXIT-0.14 is a **Stage 0** exit criterion whose part (c) reads:
   "**At Stage 1**, bisect `W_aisle` with Hybrid A\* at `W_bay = 2.50` and assert the result lies in
   **[3.5100, 4.3519]**. Threshold: **all three**." [EXIT-0.14] — i.e. EXIT-0.14 cannot pass, by its
   own stated threshold, until Hybrid A\* exists, and Hybrid A\* is Stage-1 Build-order step 6
   [§5.1 Build order]. §0.3's "Stage-ordering leftovers" paragraph lists exactly this failure mode
   for a different criterion — "EXIT-0.8 needs Hybrid A\* (Stage 1); EXIT-1.12 needs the Stage-2
   Observer; EXIT-1.4 and the `ell_OBCA` denominator need two solvers absent from Stage 1's build
   list" [§0.3 item 4] — but does not mention EXIT-0.14. That is explained by timing, not by the
   issue being absent: EXIT-0.14 was added in v1.3 [EXIT-0.14, "added v1.3"], and §0.3 is v1.2
   content, dated before v1.3 existed [§0.3 heading; §0.4 heading]. The stage-gate premise stated in
   §0 — "hard exit criteria that must pass before the next stage begins" [§0] — is violated by
   EXIT-0.14 in the same way it is already acknowledged to be violated by EXIT-0.8, just not yet
   written down anywhere.

3. **No EXIT-1.x criterion isolates the speed profiler.** Build-order step 7 introduces it as a
   distinct, necessary artefact — "**Speed profiler** — *not part of any of these planners*...
   every baseline needs its own speed profile" [§5.1 Build order step 7] — but none of EXIT-1.1
   through EXIT-1.14 names "speed" or "profile" anywhere in its criterion or threshold text (checked
   against the full table above). The closest indirect test is EXIT-1.8's tracking-error bound
   [EXIT-1.8], which is a joint pass/fail on {reference path + speed profile + tracking controller}
   together — a speed profile that mis-handles the cusp dwell described in §4.1 (e.g. wrong
   trapezoidal timing at `a_max`, the "(C) CUSP join" case computed at "0.245 m, -8.02 deg"
   [§5.1, curvature-discontinuity section]) could still pass EXIT-1.8 if the tracking controller's
   own feedback happens to absorb the error, leaving the speed profiler's correctness unverified.

4. **The bay family has Stage-1 exit-criterion coverage narrower than the parallel family's, and
   only EXIT-1.7 says so explicitly.** Of EXIT-1.1 through EXIT-1.14, only EXIT-1.7 contains the
   words "bay" or "parallel" ("success ≥ 99% on oracle-feasible scenarios, **reported separately for
   bay and parallel**" [EXIT-1.7]) — checked by grep against the full Stage-1 exit-criteria block.
   EXIT-1.9 (oracle soundness against the environment), EXIT-1.11 (`ratio_floor`), and EXIT-1.13
   (freehand-path trackability) all operate on "the frozen set" / "the reference scenes" without a
   per-family split requirement [EXIT-1.9; EXIT-1.11; EXIT-1.13], even though A25 explicitly warns
   that with two families "every 'success rate' in the document is two numbers" [A25], and later
   stages *do* add the split where it was found missing — EXIT-3.1 "Report the two families
   separately — A25 buys one *policy*, not one *number*, and a headline average hides a family that
   never learned" [EXIT-3.1, not in my scope, cited only for contrast] and §0.4's own account of
   fixing exactly this gap for EXIT-2.27/EXIT-3.1/§5.4's success surface, "all three named a
   parallel-parking difficulty axis only, so the bay family had no gate" [§0.4]. Stage 1 was not
   included in that v1.3 sweep. A criterion like EXIT-1.9 could therefore be satisfied by evidence
   drawn entirely from parallel-parking scenarios, leaving the newly-derived (and, per item 2 above
   and §0.4's own caveat, unreviewed) bay geometry's interaction with the feasibility oracle
   completely unverified at Stage-1 exit.

5. **EXIT-1.8's RS-reference clause has no numeric tolerance, unlike its HC/CC-reference clause.**
   The first half of EXIT-1.8 states hard numbers (peak lateral ≤ 0.05 m, RMS ≤ 0.02 m, terminal
   ≤ 0.05 m and ≤ 2°); its second half reads only "peak error near non-cusp joins must be
   **consistent with the open-loop prediction**" [EXIT-1.8], with no stated band around the
   open-loop numbers it is presumably being checked against (0.684 m / 14.52° at v=0.5 for a
   non-cusp C→C join [§5.1, curvature-discontinuity section, case (A)]). "Consistent with" is not a
   falsifiable threshold as written — nothing in §5.1 states whether ±5%, ±25%, or "same order of
   magnitude" is the passing band.

---

**Coverage note.** This document carries §5.1 in full (theory table, "Get these numbers right", the
curvature-discontinuity section, "The four consumers", "Build order") and §4.1 in full, plus
EXIT-1.1 through EXIT-1.14 whole, per the assignment. Supporting sections §0.1, §0.3, §0.4, §0.5,
§2, §3, §4, §11 were read in full; §9 and §10 were consulted only for the specific cross-checks
cited above and are not otherwise summarised. §5.0(c)/(c′), §5.3, and §6 are cited only where §5.1's
own text points at them and are not decomposed here — they belong to Stage 0 and Stage 3
respectively.
