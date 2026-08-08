# PLAN_S3 — Stage 3: Curriculum and robustness (carries O1 and O2)

*Decomposed from `PLAN_MACRO.md` §5.3 in full (theory table, "Derive by hand" (a)–(f), Build,
EXIT-3.1..EXIT-3.11), plus §6.1 (the O1/O2 rungs Stage 3 carries) and the parts of §6.2/§6.3/§6.4/§6.6
needed to say precisely what Stage 3 owns there. Context read in full: §0.1, §0.3, §0.4, §0.5, §2, §3,
§4, §6 (all), §7 (all). Additionally read, for cross-reference resolution only (not transcribed
whole): §5.0 Build/EXIT block (Stage-0 artefacts §5.3 presupposes), §5.1 Build order/EXIT block
(Stage-1 oracle/tracker §5.3's curriculum and demonstrations pipeline consume), §5.2 in full (Stage-2
Observer stack, τ-slot resolution, EXIT-2.27/2.29), §5.4 in full (checked specifically for whether any
EXIT-3.x gate is harder than a Stage-4 requirement, and for the O3-arm vocabulary EXIT-3.11/EXIT-6.4
use without redefining), §5.5 (A23/teleoperation cross-references only), §8, §9, §11, and the
Appendix. §10's Stage-3 reading-list block was **not** additionally consulted — §5.3's own theory
table is the reading list for this file. Every substantive line ends with a bracketed source pointer.
Nothing has been verified, corrected, resolved, or fact-checked in producing this file — it is a
reorganisation, not a review.*

---

## READ FIRST — verification status this whole file inherits

> **v1.2 — the verification is now complete.** All nine planned agents have run... **The citations
> held up: 39 exact, 7 corrected in detail, 11 unverifiable, zero fabricated.** ... **The prose did
> not hold up.** Across v1.0 and v1.1 the audits found **9 fatal and 55 serious defects** — and,
> importantly, **4 of the 9 fatal ones were introduced by v1.1's own corrections**... **This is the
> load-bearing lesson of the whole exercise: a correction is a new claim. Every v1.2 change is marked
> inline, and every one of them is now itself unreviewed.** [header, v1.2]

Within Stage 3's own scope, only **EXIT-3.1**'s bay/`η_bay` clause carries an explicit inline revision
tag, `*(v1.3)*` [EXIT-3.1]. None of EXIT-3.2 through EXIT-3.11 carries an "(added vX)" marker in the
text read for this file — unlike, e.g., EXIT-0.10–0.15 or EXIT-2.27–2.29, which are individually
tagged or individually discussed as corrections in §0.3/§0.4. Whether this means EXIT-3.2..3.11 are
unrevised v1.0 content, or were revised without an inline tag, could not be determined from the text
this file read. [§5.3 EXIT block] [§0.3] Under the rule quoted above, **everything in this file is
unreviewed regardless of tag** — see "Known-unreviewed content this stage depends on" below.

---

## Goal (verbatim)

> **Goal.** From "works on the easy distribution" to "works on the full distribution under
> perturbation." This stage also carries observation rungs **O1** and **O2**. [§5.3]

Stage 3 is titled "Curriculum and robustness" [§5.3 heading]. Two orthogonal expansions happen at
once: the *scenario* distribution widens (curriculum, from the Stage-2 easy sub-distribution to full
difficulty) and the *observation* degrades (O1, then O2) — the file's own scope note is explicit that
both belong to the same stage. [§5.3 Goal] [§6.1 table]

---

## Entry conditions — what Stage 2 must have produced, by artefact

Collected from artefacts Stage 3's own theory/derive-by-hand/build/exit-criteria text names or
presupposes. This file did not read §5.2 cover-to-cover as its primary scope, but read it in full for
cross-reference resolution because Stage 3 depends on it directly.

- **A working SAC agent trained under Stage 2's protocol.** Not named as a file/artefact anywhere in
  §5.3's own text, but presupposed by the stage's framing ("From 'works on the easy distribution' to
  'works on the full distribution'" [§5.3 Goal]) — there must be something that already "works on the
  easy distribution" for Stage 3 to extend.
- **EXIT-2.27's reported full-difficulty number**, explicitly named as this stage's baseline: "Report
  the full-difficulty number too, as the Stage-3 baseline — but do not gate on it." [EXIT-2.27] This
  is a Stage-2 exit-criterion **output**, not merely a passed/failed boolean — Stage 3 consumes the
  actual reported value.
- **The `Observer` interface and its concrete implementations** — `Observer` protocol
  (`reset`/`observe`/`space`), and `FullObserver` / `DropoutObserver` / `FOVObserver` /
  `OccludedObserver`, plus `BeliefObserver` wrapping another `Observer`. [§5.2 Build] Stage 3's O1
  rung is "observation randomisation (O1) — perturbs `Observation` only (noise, delay, dropout
  `p: 0→0.1→0.3`)" [§5.3 Build], which presupposes `DropoutObserver` (and whatever carries the noise/
  delay perturbation — not named as a separate class in the text read). Stage 3's O2 rung is "limited
  field of view — rear invisible while reversing" [§6.1 table], which presupposes `FOVObserver`.
  Neither class's own correctness is tested by anything in EXIT-3.1..3.11 — the closest available test
  is Stage 1's **EXIT-1.12** ("observations re-rendered under O0/O1/O2 have identical shape and dtype
  and identical `(valid, visible_now)` semantics") [EXIT-1.12], which itself needs the Stage-2 Observer
  to exist before it can run — a stage-ordering point §0.3 already names (see Blocked/out-of-order).
- **The τ-slot resolution.** "hold the τ slot at exactly 0.0 for O0, O1 and O2 (preserving I8's fixed
  width), and enable it only at O3/O4... This is asserted by **EXIT-6.1**." [§5.2(c) boxed note] This
  is a Stage-2-authored design decision Stage 3's O1/O2 runs must honour; see "Observation rungs owned
  here" for how much of EXIT-6.1 is actually Stage-3's to satisfy versus Stage-4's.
- **Fixed analytic observation scaling**, not `VecNormalize` — "bake fixed analytic scaling into the
  observation builder" [§5.2 Build], with the binary-feature-masking trap documented ("latent at O0...
  and detonates exactly when you switch on O2" [§5.2 Build]) — directly relevant since O2 is owned
  here.
- **`settle_counter` in `WorldState` and normalised into the observation at every rung** (A22). [A22]
  [§5.2 Build] Not re-invoked by name inside §5.3's own text, but nothing in §5.3 revisits or redefines
  it, so it is inherited unchanged.
- **The frozen eval-set generation recipe and its SHA-256 hash** (§8, "frozen at Stage 2") [§8] —
  **EXIT-3.6** directly depends on it: "eval harness hard-asserts `eps == eps_final` and the eval-set
  hash" [EXIT-3.6].

**Also directly named, but from Stage 0/1, outside this section's literal "Stage 2" scope — flagged
for completeness since §5.3's own text depends on them just as directly:**
- **The Stage-1 oracle** — "Reverse curriculum from the **Stage-1 oracle**" [§5.3 Build header]; step 1
  of the curriculum recipe is "Plan a collision-free reference path `P(sigma)`... Cache it" [§5.3
  Build step 1], and step 5 is "REJECT unless collision-free under exact SAT **AND** the feasibility
  oracle finds a solution" [§5.3 Build step 5] — both Stage-1 artefacts (RS/Hybrid A* + feasibility
  oracle, §5.1 Build order items 1–6).
- **The Stage-1 tracker**, for demonstrations: "Generate by **running the Stage-1 tracker inside the
  real environment** with **DART-style injected noise**..." [§5.3 Build, Demonstrations].
- **Exact SAT / `obb_signed_distance`** (Stage 0), used directly in curriculum step 5's rejection test
  and (by I5) in the collision-free filtering everywhere else in this stage. [§5.3 Build step 5] [I5]

No other Stage-0/1/2 artefact is named by §5.3's theory table, Derive-by-hand section, Build section,
or EXIT-3.1..3.11 block. [scope disclosure]

---

## Assumptions live here

Reproduced verbatim from §2, restricted to rows tagged "Revisit at: Stage 3" / "Revisit at: O2" (an
observation rung this stage owns), plus rows Stage 3's own text directly invokes even without a
Stage-3 tag.

| # | Assumption | If wrong | Revisit at |
|---|---|---|---|
| **A6** | Actuators are rate-limited but otherwise ideal: no backlash, no deadband, no latency. | Real steering has 100–200 ms latency. Deliberately introduced as a Stage 3 randomisation. | Stage 3 |
| **A15** | Reeds–Shepp demonstrations must be **executed through the environment by a tracking controller**, never used as raw (state, action) pairs. | RS paths have discontinuous curvature; the implied `δ̇` is unbounded. Raw RS actions lie outside the action box. | Never |
| **A21** | `time-since-seen` (τ) is **redundant** in the strictly static, noise-free case (the object has not moved; staleness carries no information). It earns its place only once objects can move or detections can be false. | If including τ measurably helps at O2, assumption A4 (static world) is being violated somewhere in the implementation. This is a free extra ablation and a useful bug detector. **v1.2: the inference is weaker than this — see §6.4, τ is also a clock proxy.** | O2 |
| **A23** | Actuator **latency** (introduced by Stage-3 DR, A6) requires state augmentation with the in-flight command buffer. | Latency makes the reward a function of history in exactly the way §7.4 rules ILLEGAL for the action-rate term. If you randomise latency without augmenting, the critic is biased by state aliasing at every step, not just at reversals. | Stage 3 |
| **A28** | The bay family's difficulty scalar is the **aisle slack ratio** `η_bay = W_aisle / W_aisle_min(W_gap; R_min, c=0)`, and `W_aisle` — not `W_bay` — is the axis that gets varied. | `W_bay` has ~0.7 m of usable range against `W_aisle`'s ~2.8 m; banding on `W_bay` gives a curriculum with almost no dynamic range and a Stage-3 gate that means nothing. Added v1.3. | Stage 3 |

**Directly invoked though not Stage-3-tagged:**

| # | Assumption | If wrong | Revisit at |
|---|---|---|---|
| **A11** | SAC is the default learner; off-policy is chosen specifically so demonstrations can seed the replay buffer. | If you switch to PPO for wall-clock reasons you lose demo seeding and gain a second horizon parameter (GAE λ). See §5.2. | Stage 2 exit, Stage 4 |

A11 is invoked implicitly throughout the Build's Demonstrations block: RLPD-style symmetric sampling,
the Q-filter, and primacy-bias mitigation [§5.3 Build, Demonstrations] all presuppose off-policy SAC
with a replay buffer that demonstrations seed, which is exactly A11's stated reason for choosing SAC.
[A11]

A22 (`settle_counter`) governs the eps_v/settle-window terms the tolerance-annealing schedule anneals
(`eps_v 0.30 -> 0.05 m/s`) [§5.3 Build] but is not itself re-cited by ID inside §5.3; it is carried
forward unchanged from Stage 2 (see Entry conditions) rather than re-asserted here. [A22]

---

## Invariants live here

Reproduced verbatim from §3, restricted to rows Stage 3's own text directly invokes.

| # | Invariant | Test |
|---|---|---|
| **I2** | Reward, success test, and collision test read `WorldState`. **Never** `Observation`. | EXIT-2.12 |
| **I3** | Observation is **ego-frame**; pose error / reward is **goal(slot)-frame**. | §7.1 |
| **I4** | `terminated` ≠ `truncated`. Five consumers must be audited: TD bootstrap mask, Φ zeroing, n-step return cut, episode logger, **curriculum counter**. Never construct `done = terminated or truncated`. | EXIT-2.5 |
| **I5** | Exact SAT decides collision/termination. The 3-circle body model appears **only** in the smooth reward term, never in a metric or a termination test. | EXIT-2.8 |
| **I6** | Collision detection runs at **every physics substep**; reward is evaluated **once per policy step**. | EXIT-2.9, EXIT-2.13 |
| **I9** | The frozen eval set is hashed and never regenerated. | EXIT-2.1 |
| **I10** | Action space is `Box(-1, 1, shape=(2,))`. Physical scaling happens in exactly one place, inside the environment. | EXIT-2.14 |

**Why each is here:** I4 names **curriculum counter** as one of its five named consumers explicitly
[I4] — direct Stage-3 territory (the tolerance-annealing "every 200 training episodes" gate and the
sigma_max advancement gate, §5.3 Build). I3 bears on O1 ("perturbs `Observation` only" [§5.3 Build])
and O2 (limited FOV) both changing `Observation`, never the goal-frame reward computation. I5 is what
curriculum step 5's "collision-free under exact SAT" rejection test invokes directly. [§5.3 Build step
5] I2, I6, I9, I10 are invoked indirectly (I2/I9 via EXIT-3.6's "eval harness hard-asserts... the
eval-set hash" and its `eps_final`/DR-off/true-state requirements; I10 via "Store actions in
**normalised** units clipped to ±0.999" [§5.3 Build, Demonstrations]; I6 via the general SAT-based
collision-free filtering this stage relies on throughout).

---

## Observation rungs owned here (O1, O2 — what changes, which §6.6 criteria apply)

**From the §6.1 ladder table, verbatim:**

| Rung | Content | Lands in | Expected result / gate |
|---|---|---|---|
| **O1** | Observation-domain randomisation: pose noise, delay, dropout (`p: 0→0.1→0.3`), goal-pose noise | Stage 3 | Success drop ≤ 10 pp. Nearly free, and it makes the O2 transfer smooth |
| **O2** | **Limited field of view** — rear invisible while reversing | Stage 3 end | **The first rung that actually bites.** The reactive MLP *must* degrade measurably (EXIT-3.11) |
| **O2a** | **Range-limited 360° sensor at R ≈ 6–7 m** (added in v1.1; see §6.2) | Stage 3 end | Gated on measured bite, same standard as O2 |

[§6.1 table]

**O2a is included in this table because the source document's own ladder places its landing at
"Stage 3 end," identically to O2** [§6.1 table] — even though this file's assigned scope names only
"observation rungs O1 and O2." This is a genuine boundary question, not resolved by anything read for
this file, and is carried to the findings list rather than silently decided either way.

**What each rung changes, per §5.3's own Build text:**
- **O1** — "**observation randomisation (O1)** — perturbs `Observation` only (noise, delay, dropout
  `p: 0→0.1→0.3`)" [§5.3 Build]. Contrast with §6.1's own O1 row, which lists a fourth component,
  **goal-pose noise**, absent from this Build bullet's enumeration. [§6.1 table] [§5.3 Build]
- **O2** — no dedicated Build bullet of its own inside §5.3 (unlike O1's explicit "Two independent
  randomisation configs" bullet); its content is stated only in §6.1's table row ("rear invisible
  while reversing" [§6.1 table]) and the general sensor-modelling rule in §6.3: "Visibility is
  computed from the **sensor position**, not the body centre; the ego body **self-occludes** (a rear
  sensor cannot see forward). Occlusion is ray-based against the obstacle rectangles." [§6.3] No FOV
  cone angle, sensor mount position, or precise "reversing" trigger condition (sign of commanded
  `a_long`? sign of `v`?) is given anywhere in the text read for this file.
- **§6.1's own two orthogonality decisions, both explicitly settled and both bearing on O1/O2:**
  **(a)** "the rungs are independent configurations. O2 runs noise-free. O1 is a separate robustness
  result. Asserted by **EXIT-6.3**" [§6.1(a)] — EXIT-6.3 itself is a Stage-4 criterion (see below),
  not part of EXIT-3.1..3.11. **(b)** "the goal slot **IS** subject to the mask at O2 and above" [§6.1
  (b)] — asserted by **EXIT-6.5**.

**Which §6.6 criteria this stage owns, in whole or in part — determined from each criterion's own
text, not from an explicit "Stage 3 owns this" statement anywhere in the source (none exists):**

| ID | Verbatim | Stage-3 relevance |
|---|---|---|
| **EXIT-6.1** | "Config exposes a **required, non-defaulted** boolean `tau_enabled`. Assert `tau_enabled == False` for every **O0/O1/O2** run and for arms A1–A5; assert `obs[τ_idx] == 0.0` bitwise over 10⁴ observations whenever `tau_enabled == False`; assert `tau_enabled == True` for **exactly** the H_B ablation arm... Threshold: 100% of observations, 100% of runs." [EXIT-6.1] | The "O0/O1/O2" clause is squarely Stage-3's to satisfy (O1, O2 runs must hold τ at 0.0). The "arms A1–A5" and "H_B ablation arm" clauses are Stage-4 vocabulary (§5.4's five-arm O3 comparison), not defined anywhere in §5.3. **The criterion as a whole cannot be fully evaluated within Stage 3 alone.** |
| **EXIT-6.2** | "Over 5000 resets at each `sigma_max` **and each sensor configuration used by any O3 arm**, compute `f_vis = P(all valid objects visible at t=0)`... **Hard gate: `f_vis ≥ 0.50`.**" [EXIT-6.2] | The "each `sigma_max`" clause is Stage-3's curriculum parameter directly. The "each sensor configuration used by any O3 arm" and "the H_A comparison" clauses are Stage-4 vocabulary. **Spans both stages within one criterion, exactly as EXIT-6.1 does.** |
| **EXIT-6.3** | "programmatic assertion mirroring EXIT-4.11: `observation_randomisation_enabled == False` and `pose_noise_sigma == 0` for every arm." [EXIT-6.3] | This is explicitly "during O3" (Stage 4) — it constrains how Stage 3's own O1 machinery must be **switched off** when Stage 4's O3 arms run. **Not owned by Stage 3**, but directly references a config flag (`pose_noise_sigma`) that O1's build must expose. |
| **EXIT-6.4** | "at `R ∈ {5, 6, 7, 8, 12} m`, the reactive MLP's success rate is recorded. Include the rung at the smallest R whose drop exceeds **the EXIT-3.11 threshold**; if no `R < 12 m` produces a drop, exclude it **and report the sweep**" [EXIT-6.4] | Defined directly against a Stage-3 criterion's own threshold (EXIT-3.11), and O2a lands at "Stage 3 end" per the table above — yet this criterion lives in §6.6, **not** in the EXIT-3.1..3.11 block this file's scope names. |
| **EXIT-6.5** | "the config exposes `goal_subject_to_fov` as a required (non-defaulted) boolean, and its value is recorded in every run's metadata. A run whose metadata lacks it fails to load" [EXIT-6.5] | Directly implements §6.1(b)'s O2 decision (goal slot subject to the FOV mask). Squarely O2, though its "and above" framing (§6.1(b)) also binds O3/O4. |

None of EXIT-6.1, 6.2, 6.4, 6.5 is reproduced inside "Exit criteria" below — that section is restricted
to EXIT-3.1..3.11 exactly as scoped. They are quoted here only to answer "what does Stage 3 own in
§6," as instructed.

---

## Theory to read

Reproduced verbatim, including `[V]`/`[C]`/`[?]` markers, in table order. [§5.3 Theory table]

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

> **Honesty note:** there is **no canonical paper called "SACfD."** It is a folk name for applying the
> DDPGfD recipe to SAC. Do not cite it as a paper. Say "the DDPGfD recipe (Vecerik et al. 2017) applied
> to SAC", or "SAC + Q-filtered BC (Nair et al. 2018)", or cite AWAC `[V]` (arXiv:2006.09359). [§5.3]

---

## Derive by hand

Reproduced whole — (a) through (f), verbatim. [§5.3 Derive by hand]

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
(3) Φ bounded. (4) The episodic case requires **Φ(absorbing) = 0**. [§5.3(a)]

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
> [§5.3(b)]

**(c) The missing-γ bug is exactly a naive dense reward.**

```
sum_t gamma^t F_wrong  -  sum_t gamma^t F_right  =  ((1-gamma)/gamma) * sum_t gamma^t Phi(s_t)
```

Dropping γ is **algebraically identical** to correct PBRS **plus** a per-step running reward
`c_bug·Φ(s_t)` with `c_bug = (1−γ)/γ = 0.005025`. With |Φ| clipped at 30 that is a hidden running
cost of up to **0.151/step** — three times a nominal 0.05 time cost, pointing the same way (toward
early termination). Large enough to **induce deliberate collisions** if the collision penalty was
sized against the declared time cost only. It is not "a small perturbation"; it is an undeclared
second reward term. [§5.3(c)]

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
write-up's rigour — put it in the thesis.* [§5.3(d)]

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
under 300 steps. [§5.3(e)]

**(f) Sample-budget criterion for the easiest curriculum rung.** With per-episode success
probability p, episodes-to-first-success is Geometric(p). With 1e6 env steps at ~200 steps/episode
you get n₀ = 5000 episodes; demanding ≥50 successes gives

```
p_0 >= 50 / 5000 = 1e-2
```

**The easiest rung must be solvable roughly 1 time in 100 by the untrained, maximum-entropy SAC
policy.** This is a **measurement**, not an assumption — roll out the untrained policy 2000 times at
each candidate `sigma_max` and measure it (EXIT-3.5). [§5.3(f)]

> A pleasant free lunch: with `(a_long, δ̇)` as actions, i.i.d. Gaussian action noise **integrates**
> into a temporally correlated random walk in `(v, δ)` — you get Ornstein–Uhlenbeck-like exploration
> for free from the rate-based action space. **Do not add OU noise on top of SAC's stochastic
> policy**; you would be double-integrating. Worth one sentence in the thesis. [§5.3(f)]

---

## Build

Reproduced whole. [§5.3 Build]

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
> `δ` leaks the reference path's curvature and the policy learns to read it. [§5.3 Build]

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
[§5.3 Build]

**Once you have more than one difficulty axis, stop banding independently.** `sigma_max`, slot
length, tolerance and noise interact multiplicatively and independent controllers will fight. Switch
to ALP-GMM over the joint parameter vector. Plan for this by making difficulty a single named
parameter vector from the start. [§5.3 Build]

**Two independent randomisation configs, never enabled together in a causal-attribution run:**

- **dynamics/scene randomisation** — perturbs `WorldState` (wheelbase, δ_max, δ̇_max, `a_max`, steering gain/offset, actuator latency, body dimensions). *v1.2: v1.1 listed "friction", which does not exist in a kinematic model — there is no tyre force to scale. Delete it or move to a dynamic model.*
- **observation randomisation (O1)** — perturbs `Observation` only (noise, delay, dropout `p: 0→0.1→0.3`)

[§5.3 Build]

> **§4.1's "knife edge" was withdrawn in v1.1.** There is no feasibility boundary here. What §4.1 now
> gives is the *cost* of a cusp and the **corrected** direction table: lowering `a_max` or raising
> `v_max` makes cusps **easier**, not harder. Randomise knowing which way is which. [§5.3 Build]

**Demonstrations (if used):**
- Generate by **running the Stage-1 tracker inside the real environment** with **DART-style injected
  noise** (start at 20% of the action range) and start-state jitter; keep only collision-free successes.
- Store actions in **normalised** units clipped to ±0.999 (exactly ±1 sits where `log π → −∞`).
- **Recompute demo rewards with the agent's own reward function.** Never store a planner cost.
- **RLPD-style symmetric sampling** (half demo, half online) from the very first gradient step, or
  anneal the demo fraction 0.5 → 0.0 over ~200k steps. A 100%-demo buffer triggers primacy bias.
- **Q-filter the BC term** (Nair et al.), with an unfiltered warm-up of only ~5k gradient steps.

[§5.3 Build]

**HER: read it, then document why you are not using it.** Four reasons, in severity order.
(1) **Termination breaks relabelling**: your episode terminates on success, so under `g′ = s_k` the
episode *should have ended* at k; transitions k+1..T exist only because the real episode continued,
and feeding them to the critic teaches that trajectories heading into a wall are good. The standard
HER results come from **fixed-length, non-terminating** Fetch environments — that is precisely the
precondition you violate. (2) The goal region is obstacle-bounded. (3) Your goal is a fixed slot, not
a sampled point. (4) You already own a feasibility oracle and a demonstrator, which is a stronger
intervention. [§5.3 Build]

---

## Exit criteria (ALL of EXIT-3.1 .. 3.11, whole)

Reproduced whole — ID, criterion text, and the full threshold/rationale text, including italic
"why an earlier version got this wrong" clauses and every "Positive control" requirement (there are
none stated inside this block — see the findings list this file's accompanying report carries).
[§5.3 EXIT block]

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

[§5.3, all 11 criteria, whole]

---

## Blocked / out-of-order items

- **EXIT-1.12 (Stage 1) needs the Stage-2 Observer to exist before it can run**, and it is the closest
  available test of **I8** ("per-object feature vector has identical width at every observation stage
  O0–O4") [I8 table row], which O1/O2 (this stage) must not violate. §0.3 names this class of problem
  explicitly: "Stage-ordering leftovers: EXIT-0.8 needs Hybrid A\* (Stage 1); **EXIT-1.12 needs the
  Stage-2 Observer**..." [§0.3] — already known, not reported as a new finding per this task's
  instructions, but material here because it means the width-invariance test for the very Observer
  classes O1/O2 use is a Stage-1-numbered criterion that cannot execute until Stage 2 exists.
  [EXIT-1.12] [I8 table row]
- **EXIT-6.1 and EXIT-6.2 each mix Stage-3 content (O0/O1/O2 runs; `sigma_max`) with Stage-4-only
  content (arms A1–A5, the H_B ablation arm, "any O3 arm") inside a single criterion.** Neither
  criterion can be fully evaluated with only Stage-3 machinery in place; both require the Stage-4
  five-arm construction (§5.4) to exist before their own stated thresholds can be checked in full. See
  "Observation rungs owned here" for the criteria quoted whole. [EXIT-6.1] [EXIT-6.2]
- **EXIT-6.4 (the O2a exit gate) is defined directly in terms of "the EXIT-3.11 threshold"** [EXIT-6.4]
  — so it is ordered *after* EXIT-3.11 regardless of which stage nominally owns it — yet it lives in
  §6.6, outside the EXIT-3.1..3.11 block this file's scope names, even though §6.1's own table places
  O2a's landing at "Stage 3 end," identically to O2. [§6.1 table] [EXIT-6.4]
- **EXIT-3.1's own text calls Stage 2's EXIT-2.27 "the Stage-3 baseline"** [EXIT-2.27], and EXIT-2.27's
  own rationale is explicitly that it was rebased "because Stage 2's gate had been strictly HARDER
  than EXIT-3.1's" [EXIT-2.27 rationale] [§0.3] — already known, not reported as a new finding per this
  task's instructions. The two criteria are read together by construction; whatever value EXIT-3.1
  states for the bay gate is compared against EXIT-2.27's separately-stated bay clause
  (`η_bay ≥ 1.55`), not derived independently. [EXIT-2.27] [EXIT-3.1]
- **n-step returns remain "NOT OPTIONAL" with zero dedicated exit criterion** [§5.2 Build] [§0.3,
  open item 3] — already known, not reported as a new finding. Stage 3's curriculum continuously
  shifts the training-state distribution under a fixed n=5..10 mixed return; nothing in EXIT-3.1..3.11
  tests the off-policy bias this mixing introduces under a *non-stationary* curriculum distribution
  specifically (as opposed to EXIT-2.29(i)'s single synthetic-MDP check at Stage 2).

---

## Known-unreviewed content this stage depends on

- **Marker legend, unchanged:** `[V]` independently verified in the v1.1 pass; `[C]` standard,
  existence certain, details unchecked; `[?]` **unverified** — "Verify before it enters a
  bibliography"; `[D]` not a citation, derived and numerically checked, "carries no literature
  claim." **Rule: no `[?]` reference may be cited in a thesis without opening it first.** [§0.1]
- Within Stage 3's own reading list, marked `[?]`: **Peng, Andrychowicz, Zaremba & Abbeel (2018)** —
  the "correct citation for randomising wheelbase, steering gain, latency," i.e. the primary source
  for exactly the DR machinery this stage builds — and **Vecerik et al. (2017)**, DDPGfD, "the recipe
  you will actually implement, adapted to SAC." [§5.3 Theory table] The Grzes (2017) citation is `[V]`
  (identity verified) but its **text was not readable through the fetch tool** — a verified-identity,
  unread-content citation, distinct from both `[V]`-clean and `[?]`. [§5.3 Theory table]
- **EXIT-3.1's bay/`η_bay` clause is a v1.3 addition**, closing the gap that "§5.4's success surface —
  all three named a parallel-parking difficulty axis only, so the bay family had no gate" [§0.4], and
  v1.3's own closing caveat applies to it in full: "everything in §0.4 is new, and therefore
  unreviewed... the *framing* around it... has had exactly one pair of eyes on it." [§0.4]
- **A27/A28 (the `W_gap`/`W_aisle` bay-difficulty framework EXIT-3.1's bay clause depends on) are
  themselves v1.3 additions**, under the same "unreviewed" caveat. [A27] [A28] [§0.4]
- **A23 (latency ⇒ state augmentation) was added late, in v1.2**, per §0.3's own list of "six further
  unstated assumptions promoted to §2: A22–A26 (settle counter, **latency augmentation**, integrator
  scheme, one-vs-two policies, `L_oracle` definition)" [§0.3] — already known, not reported as a new
  finding per this task's brief. Whether §5.3's own Build text actually *implements* what A23 requires
  is a separate question this file's accompanying report addresses.
- **Already known:** I3 and I7 still have no executable test (I3: "§7.1"; I7: "static check"). I3 is
  directly relevant here (O1/O2 both modify `Observation`, which I3 constrains to ego-frame). [§3]
  [§0.3, open item 5]
- **§0.3's global caveat applies without exception:** "Every v1.2 correction above is itself
  unreviewed... A fourth verification pass is warranted before any of this is built on." [§0.3] Stage
  3's exit-criteria block, entered here whole, has not been separately audited by this file.

---

## Failure modes here

Rows whose cause, fix, or explicit EXIT pointer sits inside Stage 3's scope, or whose symptom §5.3's
own text names directly. Reproduced verbatim; pointer is [§9] for all, plus the specific EXIT/section
each row itself cites.

| Symptom | Likely cause | Fix / test |
|---|---|---|
| Return climbs steadily and impressively; success flat at zero; episode length saturates at 400; path/RS ratio explodes; video shows something rhythmic and pointless | A positive sustainable per-step term is being farmed | non-positive running reward invariant; EXIT-3.9 |
| Flat-zero success with smoothly decreasing pose error; end-of-episode error histogram piles up just outside the tolerance | Hard tolerance, no annealing, no settle window | §5.3 annealing |
| Success rises, then **collapses abruptly at a schedule boundary** and never recovers | Curriculum annealed on step count instead of measured success rate | gate on SR; implement the decrease branch |
| Curriculum-stage success looks excellent; frozen-set success is far lower and does not track it; policy behaves like an open-loop replay | Reverse-curriculum states lie exactly on the reference path, and/or `δ₀` leaks the path curvature | EXIT-3.3 / 3.4 |
| Critic will not converge on states where the agent reverses; large persistent gap between `V(s₀)` and the empirical return | Action-rate penalty added without augmenting the state → reward is a function of history | §7.4 |
| BC loss will not go below a floor; cloned policy undershoots turns | RS path samples used directly as (state, action) demos | A15; EXIT-3.7 |
| Fast initial improvement then a hard plateau at the demonstrator's level | Primacy bias from a 100%-demo buffer | RLPD symmetric sampling; Q-filter |
| Success degrades under Stage-3 randomisation in a way uncorrelated with observation noise | Cusp cost rose: `δ̇_max` lowered, `δ_max` raised, `a_max` **raised**, or `v_max` **lowered**. *(v1.1's "knife edge" framing was withdrawn — see §4.1)* | §4.1 |

[§9, rows as quoted]

**Note on coverage of this table:** two further §9 rows explicitly cite a Stage-3 criterion as their
fix/test column entry but are themselves about Stage-2-owned mechanisms (γ selection, truncation
bootstrapping); they are carried in `PLAN_S2.md`, not duplicated here, to avoid two files each
claiming the same row. This file's own selection criterion (stated once, applied consistently): a row
is included here only if its **cause** is something Stage 3 introduces or owns (curriculum, tolerance
annealing, demonstrations, farming/oscillation, DR), not merely because its fix column happens to
point at an EXIT-3.x ID.

---

## Derived by this decomposition (not in PLAN_MACRO)

The section headers, the grouping of entry-condition artefacts "by artefact," the "Also directly
named, but from Stage 0/1" subsection under Entry conditions, the table mapping §6.6 criteria to
Stage-3 relevance under "Observation rungs owned here," and the stated selection rule for which §9
rows appear under "Failure modes here," are this file's own organisational choices, following the
template given for this task — not text found verbatim at any single location in `PLAN_MACRO.md`.
Every factual claim inside those groupings is individually back-pointed to its source above. The
judgement that EXIT-6.1/6.2 "span" stages, that EXIT-6.4/O2a is ambiguously owned, and that O2's FOV
geometry is "descriptive, not numeric," are this file's own reading of the text quoted alongside each
claim — the source document does not state any of these three conclusions in those words itself.
