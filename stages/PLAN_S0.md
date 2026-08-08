# PLAN_S0 — Stage 0: Geometry and kinematics kernel (no RL)

*Decomposed from `PLAN_MACRO.md` §5.0 in full: Theory-to-read table, "Derive by hand" (a) through
(g) and (c′), Build block, EXIT-0.1 .. EXIT-0.15, whole. Context read in full per this task's brief:
§0.1, §0.3, §0.4, §0.5, §2, §3, §4, §11. Additionally consulted, outside that list, solely because
the file template below requires a "Failure modes here" section and no failure-mode table exists
inside §5.0 itself: §9 (Failure-mode diagnostic table) — the same scope extension the sibling
`PLAN_S2.md` made for its own equivalent section. §1 (Project statement) was read because it is the
closest thing to an "entry condition" for the first stage in the ladder. **Not** read for this file:
§5.1–§5.5, §6, §7, §8, §10, the Appendix. Every substantive line ends with a bracketed source
pointer. Nothing has been verified, corrected, resolved, or fact-checked in producing this file — it
is a reorganisation, not a review.*

---

## READ FIRST — verification status this whole file inherits

> **v1.2 — the verification is now complete.** All nine planned agents have run... **The citations
> held up: 39 exact, 7 corrected in detail, 11 unverifiable, zero fabricated.** Of 14 numeric claims
> recomputed from scratch, 10 reproduced exactly. **The prose did not hold up.** Across v1.0 and v1.1
> the audits found **9 fatal and 55 serious defects** — and, importantly, **4 of the 9 fatal ones
> were introduced by v1.1's own corrections**... **This is the load-bearing lesson of the whole
> exercise: a correction is a new claim.** Every v1.2 change is marked inline, and every one of them
> is now itself unreviewed. [header, v1.2]

Stage 0's own exit-criteria block carries three v1.2-added criteria (EXIT-0.10, EXIT-0.11, EXIT-0.12)
and three v1.3-added criteria (EXIT-0.13, EXIT-0.14, EXIT-0.15), plus a v1.2-added assumption (A22)
its Build block depends on. Under the rule quoted above, **all six of those criteria, and A22, A24,
A27, are themselves unreviewed** — see "Known-unreviewed content this stage depends on" below. [§0.3]
[§0.4]

---

## Goal (verbatim)

> **Goal.** A unit-tested geometric and kinematic core. Everything downstream consumes it, so a bug
> here is a bug in every later result. [§5.0]

Stage 0 is titled "Stage 0 — Geometry and kinematics kernel *(no RL)*" [§5.0 heading], the first of
"six sequential stages (0–5)" [§0, "organised as"], each with "goal, theory to read, math to derive
by hand, what to build, and **hard exit criteria** that must pass before the next stage begins."
[§0]

---

## Entry conditions

**PLAN_MACRO.md does not state entry conditions for Stage 0.** Unlike every later stage — which
consumes artefacts a prior stage's Build block produced — Stage 0's own Goal text frames it as the
thing everything *else* depends on ("Everything downstream consumes it") rather than as itself
consuming anything upstream [§5.0]. The closest available statement of what Stage 0 starts from is
the project's own scope declaration:

> Build and evaluate a reinforcement-learning controller for low-speed car parking in 2D, and
> compare it honestly against classical motion planning. **Scope.** Rigid rectangular ego vehicle;
> static rectangular obstacles; kinematic bicycle dynamics; two task families (parallel parking,
> reverse bay parking); continuous control. [§1]

No artefact list, no prior-stage output, and no numbered precondition is given anywhere in the read
scope of this file. Reporting this absence rather than inventing an entry-conditions list. [§1] [§5.0]

---

## Assumptions live here

Reproduced whole — all five subsections of §2, verbatim. "Numbered so they can be cited and
revisited. Each states what breaks if it is wrong." [§2]

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

[§2, all five subsections, whole]

**Stage-0 load-bearing subset, called out for convenience (the full table above is the source of
record, not this list):** A1, A2, A3 directly underlie §5.0(a)'s "use this / do NOT use this"
contrast between the rear-axle and CoG bicycle-model forms [§5.0(a)]. A5 (planar world) underlies the
whole of (d)–(f)'s 2D rectangle geometry [§5.0(d)–(f)]. A6 (rate-limited actuators) is what
EXIT-0.11 tests and what (b)'s rate-limited S-curve correction depends on [EXIT-0.11] [§5.0(b)]. A22
is cited by name inside the Build block itself [§5.0 Build] [A22]. A24 and A27 are the only two rows
in the whole table whose **Revisit at** column reads "Stage 0" [A24] [A27] — A24's own row text names
EXIT-0.2 and EXIT-0.5 directly [A24]; A27 is named explicitly inside §5.0(c′)'s `W_gap` warning block
[§5.0(c′)]. A28's `W_aisle` framing is echoed by §4's own inline comment on `W_aisle`, "`<- THE
difficulty axis for this family`" [§4 BAY SCENE], though A28's own **Revisit at** is Stage 3, not
Stage 0 [A28].

---

## Invariants live here

Reproduced whole. "These hold at **every** stage. Violating one invalidates results silently, which
is why each has a test attached." [§3]

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

[§3, whole]

**I1 is the only invariant whose named test (EXIT-0.2) is itself a Stage-0 criterion** [I1 table row]
[EXIT-0.2]. I5's content — "3-circle body model appears only in the smooth reward term, never in a
metric or a termination test" — is exactly what §5.0(e)'s "Division of labour" paragraph and
EXIT-0.6's "not importable by the termination path" clause enforce in code that Stage 0 itself
builds, even though I5's own **named** test, EXIT-2.8, is a Stage-2 criterion this file did not read
in full [I5 table row] [§5.0(e)] [EXIT-0.6]. I6's substep/policy-step split is exactly what §5.0(f)
derives, even though I6's own named tests, EXIT-2.9 and EXIT-2.13, are both Stage-2 criteria outside
this file's scope [I6 table row] [§5.0(f)]. I2, I3, I4, I7, I8, I9, I10 are reproduced above for
completeness because the invariants table states it holds "at every stage," but none of their named
tests are Stage-0 criteria, and this file makes no claim about how or whether Stage 0's own build
honours them beyond what §5.0's own text says. [§3]

---

## Theory to read

| Priority | Source | Covers |
|---|---|---|
| must | `[C]` LaValle, S. M. (2006). *Planning Algorithms*, CUP. §13.1.2 (simple car), §15.3. Free at lavalle.pl/planning/. | Bicycle model, nonholonomic constraint, configuration space |
| must | `[C]` Rajamani, R. *Vehicle Dynamics and Control*, Ch. 2. | Ackermann geometry, ICR, the rear-axle vs CoG distinction |
| should | `[?]` Ericson, C. (2005). *Real-Time Collision Detection*, Ch. 4–5. | SAT, OBB intersection, closest-point-on-segment |

[§5.0, Theory and mathematics to read, whole]

---

## Derive by hand (do not copy)

Reproduced whole — every formula, warning block, and numeric table inside §5.0(a)–(g) and (c′),
verbatim. [§5.0]

### (a) The two bicycle-model forms, and why mixing them is a bug

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
turning-radius discrepancy for this car and put the number in your notes. [§5.0(a)]

### (b) Two-arc lateral shift (the parallel-parking S-curve)

Two opposite full-lock arcs of radius R through angle φ:

```
lateral gain     d    = 2R (1 - cos phi)
longitudinal     ell  = 2R sin phi
eliminate phi:   ell  = sqrt(4Rd - d^2)          valid for d <= 2R
```

Evaluate at R = 3.9466 m, d = 2.35 m → ell = **5.62 m**. Note carefully what this *is*: a
**lateral-shift relation**, not a minimum-slot-length formula. It tells you the longitudinal run
needed to translate sideways by d; the slot-length question additionally involves body length,
overhangs, and the corner-clearance conditions against both neighbour cars. [§5.0(b)]

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
> is a separate matter and belongs in Stage 1 (EXIT-1.8). [§5.0(b)]

### (c) Minimum parallel-parking slot length — DERIVE IT YOURSELF

There is a known closed form in the literature. **This plan deliberately does not reproduce one.**
Two independent research agents converged on the same recommendation: published formulas are
inconsistent about whether "length" includes overhangs and whether the reference point is the rear
axle or the body centre, and with f = 0.9 and r = 1.1 that convention difference exceeds a metre.
A formula written from memory would be a fabrication. [§5.0(c)]

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

[§5.0(c)]

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
> half-width 0.925. With `c_lat = 0.5` it reproduces the d = 2.35 m used in (b).) [§5.0(c)]

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

[§5.0(c), whole — markers copied exactly as printed, not corrected or added to, per this task's
rule against citation fixes]

### (c′) Reverse bay parking — the geometry, which *does* close in closed form *(added v1.3)*

Everything above (c) is parallel parking. Reverse bay parking — **half the headline task** — had no
geometry at all in v1.0–v1.2: no dimensions, no feasibility boundary, no goal pose. This closes that.

Unlike (c), this one comes finished. The single-cut boundary for perpendicular back-in parking has an
exact closed form in the rear-axle frame, and **it is written entirely in three radii §4 already
tabulates for other reasons.** Derive it anyway; the derivation is four lines once the frame is right,
and the frame is the entire difficulty. [§5.0(c′)]

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
**counter-clockwise**, 0 → +π/2. Get that sign wrong and every corner label below flips. [§5.0(c′)]

> **`W_gap` is not `W_bay`, and the difference is 0.69 m of aisle.**
> ```
> walls / painted lines, no incursion permitted   : W_gap = W_bay        = 2.50 m
> both neighbours are cars centred in equal bays  : W_gap = 2*W_bay - w  = 3.15 m
> ```
> The second is the real parking lot; the first is the conservative one and does not depend on how
> your neighbours parked. **A27 declares `W_gap` a scene parameter with the wall model as default.**
> Deriving `W_gap` from `W_bay` inside the generator instead of declaring it is how this becomes a
> silent 0.69 m error in the difficulty label of every frozen bay scenario. [§5.0(c′)] [A27]

**The manoeuvre.** Single cut = one gear change: (1) forward along the aisle at heading 0;
(2) **one reverse arc** at radius `R`, turning heading 0 → π/2, turn centre
`C = (x_e + R, y_c)`; (3) reverse straight down `x = x_e` into the bay. Two free parameters:
`y_c` (how high the turn centre sits) and `x_e` (final lateral offset in the bay). [§5.0(c′)]

**Step 1 — move to the turn-centre frame.** Once `R` is fixed the swept set is a *fixed shape*; the
whole manoeuvre is a translation of it. Write **`u = −y_c`** — how far the turn centre sits *below*
the bay mouth line. The farthest body point from `C` is the front-outer corner, at `R_front_outer`,
and it passes through the top of its arc, so

```
max y over the whole manoeuvre = y_c + R_front_outer  =>   W_aisle = R_front_outer - u
```

**A narrow aisle means a large `u`.** That is the entire trade: pushing the turn centre down into the
bay row buys aisle width and spends bay width. [§5.0(c′)]

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
`-R_swept_inner`. The left boundary is the mirror argument on the rear-outer corner. [§5.0(c′)]

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

[§5.0(c′)]

**Four independent checks that this is right — all verified numerically against an explicit
40 001-sample swept body (§0.1 status: `[D]` — derived and machine-checked in this document):**

| Check | Consequence | Independent meaning |
|---|---|---|
| `W' = w` | `u* = −r` exactly, `W_aisle = R_front_outer + r = 7.1574` | the zero-clearance bay forces "align fully in the aisle, then reverse straight in", whose sweep never crosses the mouth line at all |
| `W' = R_rear_outer − R_swept_inner = 1.9726` | `u* = 0` | the two branches meet continuously |
| `W' = R_rear_outer = 4.9942` | `u* = R_swept_inner`, `W_aisle = R_front_outer − R_swept_inner = 3.0358` | **that is the swept-corridor width §4 already tabulates**, arrived at from a completely different direction |
| the cap `u <= R_swept_inner − c` | — | it is not an extra assumption: `y_c + R − w/2 = c` says the car's inner flank, *driving up the aisle before the arc starts*, sits exactly `c` above the mouth line. Verified to 1e-16 |

[§5.0(c′), table whole]

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

[§5.0(c′), design table verbatim]

> **No aisle width can buy more than `(W_bay − w)/2` of swing clearance** — 0.325 m at the reference
> bay — because at `u = −r` the footprint has already contracted to the car's own width and the
> *parked* car is what limits the rest. Saturation is reached at `W_aisle = R_front_outer + r = 7.1574 m`.
> Aisle beyond that is free space, not margin. Useful when someone proposes "just widen the aisle."
> [§5.0(c′)]

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
footprint, and EXIT-0.10 is the first place to look.** [§5.0(c′)]

**`R = R_min` is optimal and there is nothing to search over.** `W_aisle_min` is strictly increasing
in `R` (4.352 at `R_min`, 4.622 at 4.5, 5.481 at 6.0, 9.812 at 12.0, verified over `R ∈ [R_min, 20]`),
because `R_front_outer` grows roughly linearly in `R` while the usable `u*` grows sublinearly. Full
lock is the answer. Do not spend a parameter search on it. [§5.0(c′)]

**What this formula is *not*.** It is exact for the **constant-radius single-arc** family and is
therefore an **upper bound** for the general single-cut class (a varying-curvature reverse might do
better; this document does not claim it cannot). Per **A10**, the operational feasibility oracle
remains the Stage-1 planner, exactly as for parallel parking. The closed form's job is to be the
*independent analytic check* on that planner — EXIT-0.14. [§5.0(c′)] [A10]

**The goal pose, and the heading trap.** With `D_bay = 5.30 = l + 0.60`, centring the body gives

```
goal = (0, -3.90, +pi/2)     body spans y in [-5.00, -0.30], x in [-0.925, +0.925]
                             0.30 m clear at the bay end, 0.30 m inside the mouth,
                             0.325 m clear to each bay line
```

[§5.0(c′)]

> **§5.0(g) offers a min-over-two-corner-matchings for the heading term. For this family the answer
> is NO.** `theta = -pi/2` is nose-**in**: geometrically identical footprint, and a task the agent was
> not asked to do. Enabling two-corner matching silently converts "reverse bay parking" into "bay
> parking", makes the 180° plateau of §7.3 into a ±90° problem, and invalidates the comparison with
> a reverse-only Reeds–Shepp expert. **EXIT-0.15 asserts the nose-in pose is rejected.** [§5.0(c′)]

> **A refinement to the 180° claim made in §0.3, §5.0(g) and §7.3.** The *canonical* bay start —
> aisle-parallel, heading 0, goal `+pi/2` — has heading error **exactly π/2**, where
> `d(1−cos)/dΔθ = 1.0`, not 0. Heading errors near π arise from the **Stage-3 randomised start
> distribution**, not from the canonical manoeuvre. The plateau is still a real defect and the fix
> still stands; it just does not bite every bay episode, which matters when you are reading a learning
> curve and deciding what to blame. [§5.0(c′)]

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

[§5.0(c′), whole section]

### (d) Exact OBB–OBB signed distance

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
is non-zero but they overlap. Run SAT first; select by its boolean. [§5.0(d), whole]

### (e) Multi-circle body approximation and its conservatism

For a 4.7 × 1.85 m body split into 3 equal circles along the centreline, the covering radius is

```
rho = 0.5 * sqrt( (l/3)^2 + w^2 ) = 0.5 * sqrt( 1.5667^2 + 1.85^2 ) = 1.2121 m
```

against a true half-width of 0.9250 m — an over-estimate of **0.2871 m** in lateral extent. That is
large enough to declare a genuinely feasible tight slot infeasible.

**Division of labour, and it is not negotiable:**
- 3-circle model → the **smooth safety-margin term inside the reward potential** (fast, differentiable)
- exact OBB → **termination test and every reported clearance metric**

[§5.0(e), whole]

### (f) Continuous collision detection resolution

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
translation), or the substep count must rise. [§5.0(f), whole]

### (g) Pose-error metrics

Use `(1 − cos Δθ)` rather than `Δθ²`: it handles the 2π periodicity naturally and its small-angle
expansion is `Δθ²/2`, so weights transfer by a factor of 2. If either heading in the slot is
acceptable, take the min over the two corner matchings — but decide this explicitly, because it
changes the task. [§5.0(g)]

> **The periodicity is not free — it buys a plateau at 180°.** `d/dΔθ (1 − cos Δθ) = sin Δθ`, which
> **vanishes at Δθ = π**: gradient 1.0 at 90°, 0.50 at 150°, and 1.2e-16 at 180°. So the heading term
> of Φ has an unstable equilibrium at exactly 180° of heading error — and **reverse bay parking
> routinely starts at 90–180° from the goal heading.** This is structurally the same pathology as
> §7.3's Defect 2, relocated to the far field. It also saturates: `1 − cos ≤ 2`, so the heading
> contribution to `|Φ(s₀)|` is bounded. **§7.3 Defect 3 replaces this term with `1 − cos(Δθ/2)`;
> use that form.** Under it the bound is `w_th·1 = 10.50` (v1.1 printed `2·w_th = 5.25` for the old
> form). If you adopt the two-corner matching, **check whether it moves the plateau to Δθ = π/2**,
> which would be worse. [§5.0(g)]

---

## Build

Reproduced verbatim.

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

[§5.0 Build, whole]

---

## Exit criteria (ALL of EXIT-0.1 .. 0.15, whole)

Reproduced whole — ID, criterion text, and the full threshold/rationale text, including italic
"why an earlier version got this wrong" clauses and every "Positive control" requirement, exactly as
the source table presents them (one flat table; the source does not sub-group Stage 0's criteria the
way it does for some later stages). [§5.0]

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

[§5.0, EXIT CRITERIA — Stage 0, all 15 criteria, whole]

---

## Blocked / out-of-order items

- **EXIT-0.8 needs a working Hybrid A\* to validate against, and Hybrid A\* is a Stage-1 build item.**
  EXIT-0.8's own threshold text says "validated against numerical bisection" and (c)'s own text says
  "bisect on slot length using your own single-cusp-restricted Hybrid A\*" [§5.0(c)] [EXIT-0.8] — §0.3
  names this explicitly among "Stage-ordering leftovers": **"EXIT-0.8 needs Hybrid A\* (Stage 1)."**
  [§0.3] *(Already known per this task's brief — not reported as a new finding.)*
- **§5.0(c) deliberately gives no closed-form parallel slot-length formula.** "There is a known closed
  form in the literature. **This plan deliberately does not reproduce one.**" [§5.0(c)] *(Already known
  per this task's brief — not reported as a new finding.)*
- **§5.0(c′) is new in v1.3 and its framing is unreviewed.** "everything in §0.4 is new, and therefore
  unreviewed. The derivation is machine-checked against an independent numerical sweep, which is
  stronger than v1.1's corrections ever were — but the *framing* around it... has had exactly one pair
  of eyes on it." [§0.4] *(Already known per this task's brief — not reported as a new finding.)*
- **I3 and I7 still have no executable test.** I3's test column reads "§7.1"; I7's reads "static
  check" — neither is an EXIT-numbered, thresholded criterion. [§3, table rows] [§0.3, open item 5]
  *(Already known per this task's brief — not reported as a new finding.)*
- **EXIT-0.14(c) also needs Hybrid A\*, and is not on §0.3's list.** EXIT-0.14 part (c) reads: "*At
  Stage 1*, bisect `W_aisle` with Hybrid A\* at `W_bay = 2.50` and assert the result lies in
  **[3.5100, 4.3519]**." [EXIT-0.14] §0.3's "Stage-ordering leftovers" enumeration — "EXIT-0.8 needs
  Hybrid A\* (Stage 1); EXIT-1.12 needs the Stage-2 Observer; EXIT-1.4 and the `ell_OBCA` denominator
  need two solvers absent from Stage 1's build list" [§0.3] — predates v1.3 (§0.3 is dated in the
  v1.2 pass; EXIT-0.14 is a v1.3 addition, per its own "*(added v1.3)*" tag [EXIT-0.14]) and does not
  name it.

---

## Known-unreviewed content this stage depends on

- **Marker legend, unchanged:** `[V]` independently verified in the v1.1 pass against a retrieved
  publisher record, DOI resolver, dblp, PMLR, arXiv, JMLR or the PDF itself; `[C]` standard, widely
  cited, existence certain, page/volume numbers not independently checked; `[?]` **unverified** —
  "Verify before it enters a bibliography"; `[D]` *(added v1.3)* not a citation, derived inside this
  document and checked against an independent numerical construction, "carries no literature claim."
  **Rule: no `[?]` reference may be cited in a thesis without opening it first.** [§0.1]
- Within Stage 0's own theory table, marked `[?]`: **Ericson, C. (2005), *Real-Time Collision
  Detection*, Ch. 4–5.** [§5.0, Theory table]
- Within (c)'s reading list, marked `[?]` after verification: **Blackburn, S. R. (2009), *The
  Geometry of Perfect Parking*** — "Exists (verified), but not peer-reviewed, and its exact
  algebraic form was not verifiable." [§5.0(c)]
- (c)'s Vorobieva citations are marked `[V]` but with an embedded correction: "**Two distinct papers,
  not one ambiguous one**... Note the author order differs between them." [§5.0(c)]
- **§5.0(c′), the whole of it, is `[D]`-status content added in v1.3**, not independently reviewed by
  a second pass: "everything in §0.4 is new, and therefore unreviewed. The derivation is
  machine-checked against an independent numerical sweep... but the *framing* around it (which model
  is conservative, which gate belongs where, whether the single-arc family is the right one) has had
  exactly one pair of eyes on it." [§0.4] This directly covers EXIT-0.13, EXIT-0.14, and EXIT-0.15,
  all three tagged "*(added v1.3)*" in the exit-criteria table. [EXIT-0.13] [EXIT-0.14] [EXIT-0.15]
- **"Every v1.2 correction... is now itself unreviewed"** [header, v1.2] applies to this stage's
  three v1.2-added criteria — **EXIT-0.10** ("the largest hole in the whole audit"), **EXIT-0.11**,
  and **EXIT-0.12** — and to **A22**, added the same pass. [§0.3] [A22]
- **A24 and A27 are the only two Stage-0-tagged assumption rows**, and neither is flagged with a
  verification marker of its own in §2 (the `[V]/[C]/[?]/[D]` scheme in §0.1 applies to citations, not
  to assumption rows) — reported here for completeness, not as a discrepancy. [A24] [A27] [§0.1]
- **Open item, carried from §0.3 and still open per §0.4's own closing list:** "An independently
  derived minimum-slot-length formula — §5.0(c) still deliberately leaves this to be derived rather
  than copied, and the v1.1 pass found its frame under-specified. *(The **bay** analogue is now closed
  in §5.0(c′); this item is parallel-parking only.)*" [§0.3, open item 3, as restated in the v1.2
  provenance note]

---

## Failure modes that show up here (§9 rows, pointer only)

§9 is outside this file's assigned context-reading list; consulted only because the file template
requires this section and no failure-mode table exists inside §5.0 itself — the same scope extension
`PLAN_S2.md` made for its own equivalent section. Exactly one row in the whole §9 table names a
Stage-0 criterion:

| Symptom | Likely cause | Fix / test |
|---|---|---|
| Reported clearances systematically slightly too small, worst when nosing diagonally into a bay corner | SAT face-normal gap used as the separation distance (vertex–vertex case) | EXIT-0.4 |

[§9, row as quoted] — this is the executable version of the same warning already reproduced above in
(d): "the max-over-face-normal-axes SAT gap is only a **lower bound** on the true separation... and
**strictly under-estimates** in the vertex–vertex case — which is exactly the configuration when the
ego noses diagonally into a bay corner." [§5.0(d)]

No other §9 row names an EXIT-0.x ID or points its "Fix / test" column at Stage-0 material; this file
does not claim the remaining rows are irrelevant to Stage 0's *build*, only that none of them is
*addressed by* a Stage-0 exit criterion in the source text.

---

## Derived by this decomposition (not in PLAN_MACRO)

The section headers, the grouping of "Stage-0 load-bearing subset" under Assumptions, the annotation
of which invariants have Stage-0-internal tests versus Stage-2-named tests, and the collection of
"Blocked / out-of-order items" and "Known-unreviewed content" into single lists are this file's own
organisational choices, following the template given for this task — not text found verbatim at any
single location in `PLAN_MACRO.md`. Every factual claim inside those groupings is individually
back-pointed to its source above. The judgement that EXIT-0.14(c) belongs beside EXIT-0.8 in
"Blocked / out-of-order items" is this file's own inference from EXIT-0.14(c)'s text and §0.3's
"Stage-ordering leftovers" framing, not a sentence copied from PLAN_MACRO.md itself — the underlying
facts it rests on (EXIT-0.14(c)'s own wording, §0.3's list and its date relative to v1.3) are each
individually sourced above.
