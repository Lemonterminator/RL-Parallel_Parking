# PLAN_S2 — Stage 2: Minimal viable RL (full-state MDP, O0)

*Decomposed from `PLAN_MACRO.md` §5.2 in full (theory table, "Derive by hand", Build, EXIT-2.1..
EXIT-2.29), plus §4.2's discount arithmetic. Context read in full: §0.1, §0.3, §0.4, §0.5, §2, §3,
§4, §7. Context read selectively, only where Stage 2 itself cross-references it: §5.0 (Stage 0
Build/EXIT block), §5.1 (Stage 1 Build order/EXIT block), §8 (evaluation-protocol generation
recipe). §5.3, §5.4, §5.5 and §6 were **not** read for this file except where a fragment of them is
quoted verbatim *inside* §5.2 itself (e.g. the τ_since_seen blockquote's reference to EXIT-6.1).
Every substantive line ends with a bracketed source pointer. Nothing has been verified, corrected,
resolved, or fact-checked in producing this file — it is a reorganisation, not a review.*

---

## READ FIRST — verification status this whole file inherits

> **v1.2 — the verification is now complete... The prose did not hold up.** Across v1.0 and v1.1 the
> audits found **9 fatal and 55 serious defects** — and **4 of the 9 fatal ones were introduced by
> v1.1's own corrections**... **This is the load-bearing lesson of the whole exercise: a correction is
> a new claim. Every v1.2 change is marked inline, and every one of them is now itself unreviewed.**
> [header, v1.2]

Stage 2's own exit-criteria block carries three v1.2 corrections (EXIT-2.27, EXIT-2.28, EXIT-2.29)
and one v1.2-added invariant dependency (A22). Under the rule quoted above, **all four are
themselves unreviewed** — see "Known-unreviewed content this stage depends on" below. [§0.3]

---

## Goal (verbatim)

> **Goal.** A working SAC agent on the fully-observable task, with the evaluation protocol frozen
> **before** any tuning happens. [§5.2]

Stage 2 is titled "Minimal viable RL (full-state MDP, O0)" [§5.2 heading]. The document's own
framing of why this stage cannot be the project's contribution: **A19** — "On a known static map,
classical planning solves this problem, so the O0 RL result is a sanity check and not a
contribution." If wrong: "the first question in a defence is why Hybrid A* is not simply better."
Revisit: Never. [A19] [§2.5]

---

## Entry conditions — what Stages 0-1 must have produced, by artefact

Collected from the artefacts Stage 2's own theory/build/exit-criteria text names or presupposes.
This file did not read §5.0/§5.1 cover-to-cover; only the fragments below were consulted because
Stage 2 cites them directly or because they are the closest available definition of a term Stage 2
uses without redefining.

- **`worldstate.py` — the `WorldState` dataclass (truth)**, with fields `ego (x,y,theta,v,delta)`,
  `objects (N,6)`, `bounds`, and **`settle_counter (int, 0..K_settle)`**, annotated *"`***`settle_counter`
  IS PART OF THE STATE. See A22. Omitting it makes even O0..."* [§5.0 Build] [A22] — Stage 2's Build
  block depends on this field existing already; see the honouring discussion below.
- **`dynamics.py`** — rear-axle bicycle, explicit substep integration, action clamping. [§5.0 Build]
  — Stage 2's action-scaling and clamp-adjacent criteria (EXIT-2.14) presuppose this exists and is
  correct; its own correctness gate is **EXIT-0.11** (Stage 0, not read in full here). [EXIT-0.11]
- **`geometry.py`** — `obb_corners`, `sat_overlap`, `obb_signed_distance`, `body_circles`,
  `ccd_sweep`. [§5.0 Build] — this is what **EXIT-2.8** ("Clearance metric uses exact OBB, not
  circles") and **I5** ("Exact SAT decides collision/termination... 3-circle body model appears only
  in the smooth reward term") test against; Stage 2 does not rebuild it. [EXIT-2.8] [I3 table row]
- **`render.py`** — trajectory replay. [§5.0 Build] — named again as a Stage-5 dependency
  ("`render.py` (Stage 0) already has trajectory replay") but that is outside this file's scope.
  [§5.0 Build]
- **EXIT-0.9 (Determinism)** — "same initial state + same action sequence → bitwise-identical
  `WorldState` trajectory, across processes." [EXIT-0.9] — the closest available prerequisite for
  **EXIT-2.3**'s "two runs of the same checkpoint in separate processes" determinism requirement,
  though EXIT-2.3 is stated as its own criterion, not explicitly as "EXIT-0.9 applied to the
  checkpoint." [EXIT-2.3]
- **EXIT-0.10 (Body footprint placement relative to the rear axle)** — asserts
  `obb_corners(WorldState(x=0,y=0,theta=0))` against exact corner coordinates, and specifically that
  `min_x == −r` and `max_x == L+f` as *separate* assertions ("a symmetric length check would not
  catch an f/r swap"). [EXIT-0.10] — foundational for **I1** (rear-axle reference everywhere) and for
  every distance/clearance quantity Stage 2's Φ and EXIT-2.8 compute; the plan itself calls this "the
  largest hole in the whole audit." [EXIT-0.10] [I1 table row]
- **EXIT-0.11 (Actuator and state clamps are actually enforced)** — zero violations of `|δ|≤δ_max`,
  `|v|≤v_max`, and the rate clamps, over 10⁶ random 400-step sequences, with a positive control.
  [EXIT-0.11] — the plan states explicitly this is what stops the RL car from having "a turning
  radius smaller than `R_min = 3.9466 m` — a capability Reeds–Shepp, Hybrid A\* and the tracked
  expert all lack," which would otherwise inflate Stage 2's own success numbers. [EXIT-0.11]
- **EXIT-0.12 (The heading potential has no gradient plateau)** — `|dΦ_heading/dΔθ| > 0.1` for all
  `Δθ ∈ (0,π]`. [EXIT-0.12] — this is what makes the `w_th = 10.50` calibration Stage 2's Φ uses
  (§7.2, read in full as context) legitimate; the test itself lives in Stage 0, not Stage 2. [EXIT-0.12]
  [§7.2]
- **RS closed form, collision-checked path validator, feasibility oracle, `h_nhwo`/`h_hwo`, Hybrid
  A\*, speed profiler, rear-axle pure-pursuit tracker** — Stage 1's eight-item build order.
  [§5.1 Build order] — Stage 2 names two direct consumers of this stack: the **"Stage-1 expert"**
  used as one of six scripted policies in **EXIT-2.25**, and the **"Stage-1 tracked-expert length"**
  used as the path-length comparator in **EXIT-2.27**. Neither term is re-defined inside §5.2 itself;
  see the findings list for the ambiguity this creates around the second one. [EXIT-2.25] [EXIT-2.27]
- **A26 — `L_oracle` is the post-smoothing Hybrid A\* path length, frozen with the scenario set.**
  [A26] — this is the quantity **EXIT-2.1** requires present and finite per scenario
  ("Per-scenario `L_oracle`, `g_oracle`, `oracle_min_clearance`, `planner_resolution` present and
  finite"). [EXIT-2.1]
- **EXIT-1.9 (Feasibility oracle is sound wrt the environment)** — 100% of oracle-approved initial
  states produce no instant termination on reset; ≥90% of witness paths execute collision-free under
  closed-loop tracking. [EXIT-1.9] — the implicit soundness precondition behind **EXIT-2.2**'s "every
  frozen scenario is oracle-feasible... feasible fraction of VAL and TEST == 1.000 exactly."
  [EXIT-2.2]
- **A15 — RS demonstrations must be executed through the environment by a tracking controller, never
  used as raw (state, action) pairs.** [A15] — governs how the "Stage-1 expert" referenced in
  EXIT-2.25 must have been produced.
- **The frozen-eval-set generation recipe** ("filter with Hybrid A\* using the ENVIRONMENT's exact
  SAT checker and footprint; store `L_oracle`, `g_oracle`, `oracle_min_clearance`,
  `planner_resolution` with each scenario; serialize; SHA-256; hard-code the hash") is stated under
  §8, captioned "frozen **at Stage 2**." [§8] — so this is not strictly a Stage-0/1 entry artefact;
  it is a Stage-2 Protocol-gate activity (EXIT-2.1) that *consumes* Stage 1's Hybrid A\* as its
  filtering oracle. Flagged here because EXIT-2.1's threshold cannot be understood without it, and
  because this file was not asked to read §8 but did so to resolve that dependency. [§8] [EXIT-2.1]

No other Stage-0/1 artefact is named by §5.2's theory table, Derive-by-hand section, Build section,
or EXIT-2.1..2.29 block. This list is therefore bounded by what Stage 2's own text cites — it is not
a claim that Stage 0/1 produce *only* these artefacts. [scope disclosure]

---

## Assumptions live here

Reproduced verbatim from §2, restricted to rows tagged "Revisit at: Stage 2" / "Stage 2 exit" and
rows Stage 2's own text (theory, Derive-by-hand, Build, EXIT criteria) directly invokes.

| # | Assumption | If wrong | Revisit at |
|---|---|---|---|
| **A7** | Success requires position, heading, **and near-zero speed**, sustained for a settle window. | Without the speed and settle conditions the agent flies through the goal pose at 1.5 m/s and claims success on one frame. | Never |
| **A9** | The scenario distribution is fixed and defined by a generator with a recorded seed. | Every historical comparison becomes incomparable. Enforced by hashing (EXIT-2.1). | Never |
| **A10** | "Feasible" means **"solvable by our Hybrid A* at the declared grid resolution"**, not "geometrically possible". Hybrid A* is resolution-complete, not complete. | The frozen eval set is biased toward scenarios the planner can solve; the RL success rate is measured against a denominator that is itself a lower bound on true feasibility. **State this in the thesis rather than hide it.** | Never — state it |
| **A11** | SAC is the default learner; off-policy is chosen specifically so demonstrations can seed the replay buffer. | If you switch to PPO for wall-clock reasons you lose demo seeding and gain a second horizon parameter (GAE λ). See §5.2. | Stage 2 exit, Stage 4 |
| **A12** | γ = 0.995 with `max_steps` = 400, chosen from the manoeuvre timescale (a real park is 120–250 policy steps). | γ = 0.99 makes the terminal bonus invisible; γ = 0.998 pushes the effective horizon past the episode limit. Both are measured, not assumed — see EXIT-2.11. | Stage 2 exit |
| **A13** | The dense reward term is **strictly potential-based**, so it cannot change the optimal policy or be farmed. | Any non-potential dense term reintroduces hovering/farming. Enforced by an executable identity test (EXIT-2.6). | Never |
| **A14** | The policy is evaluated **deterministically** (`a = a_scale·tanh(μ)`, the mode). | The max-entropy objective is a training device; reporting the stochastic policy measures the wrong objective and inflates the collision rate by an amount that depends on the learned α. | Never |
| **A15** | Reeds–Shepp demonstrations must be **executed through the environment by a tracking controller**, never used as raw (state, action) pairs. | RS paths have discontinuous curvature; the implied `δ̇` is unbounded. Raw RS actions lie outside the action box. | Never |
| **A16** | `WorldState` (truth) and `Observation` (policy-visible) are distinct types from day one. | The entire O1–O4 ladder becomes a rewrite instead of a config change, and reward/collision leaks are undetectable. | Never — invariant I2 |
| **A17** | `terminated` and `truncated` are carried as two separate booleans all the way into the replay buffer. | The most common silent bug in the project. See §5.2. | Never — invariant I4 |
| **A18** | The simulator is cheap enough to vectorise (2D integrator + SAT on a handful of OBBs), so throughput is not the binding constraint at Stage 2. | If it is, that changes the SAC-vs-PPO calculus, not the plan structure. | Stage 4 |
| **A19** | On a known static map, classical planning solves this problem, so the O0 RL result is a sanity check and not a contribution. | If you present O0 as the result, the first question in a defence is why Hybrid A* is not simply better. | Never |
| **A20** | For static, noise-free, known-association obstacles, a hand-written filter storing `(last-seen pose, seen flag)` is an **exact** sufficient statistic, so a feedforward policy on it can be optimal and a GRU can at best tie it. | This is the project's central falsifiable hypothesis. It is pre-registered, not assumed true. See §6.4. | Tested at Stage 4 |
| **A22** | **`settle_counter` is part of the state and is observable at every rung.** Success requires the tolerance conditions to hold for `K_settle` consecutive steps, which is not a function of a single pose. | Without it the task is a **POMDP even at O0**, and the "full-state MDP" premise of §5.2, §6.1 and H_A is false. Added in v1.2; v1.0 and v1.1 both omitted it. | Never |
| **A25** | Parallel parking and reverse bay parking are solved by **one policy** conditioned on the scenario, not two. | If two, every "success rate" in the document is two numbers, K doubles, and the Stage-4 compute estimate doubles with it. Never stated. | Stage 2 |

[§2.1–§2.5, full table rows quoted]

A20 is included because §5.2's own settle_counter callout invokes "H_A's entire sufficiency
argument" by name; A20 is the source of H_A and is not itself a Stage-2 assumption ("Tested at
Stage 4"). Quoted here only as the referent of that name. [§5.2] [A20]

---

## Invariants live here

The full table, reproduced verbatim — these "hold at every stage," and several of their tests live
inside Stage 2's own EXIT block.

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

[§3, full table]

**Already known, not a new finding:** I3's test is "§7.1" and I7's test is "static check" — neither
is an EXIT-numbered, scripted criterion. Both are named in the task's own known-items list as having
"no executable test." [§3] [ALREADY KNOWN per task instructions]

**Cross-stage note (not verified here, only observed):** I8's test is **EXIT-1.12**, a Stage-1
criterion, for a property ("identical width at every observation stage") whose O0 instance is built
in Stage 2. See "Blocked / out-of-order items." [I8] [EXIT-1.12]

---

## Theory to read

Reproduced verbatim, citation markers unchanged.

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

[§5.2, both tables, verbatim including markers]

---

## Derive by hand

Reproduced verbatim, formulas and callouts unchanged.

**(a) γ-contraction.** `‖TV − TW‖∞ ≤ γ‖V − W‖∞` for both `T^π` and `T*`, using
`|max_a f − max_a g| ≤ max_a|f − g|`. Then Banach ⇒ unique fixed point, geometric convergence, and
`‖V*‖∞ ≤ R_max/(1−γ)`. **Preconditions:** γ ∈ [0,1) *strictly*; bounded rewards. The contraction
**fails** at γ = 1 — undiscounted episodic uniqueness needs a proper-policy assumption. [§5.2]

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
*hours* into a run, after the policy becomes confident. [§5.2]

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
[§5.2]

**Exception (Pardo et al.):** if you *deliberately* make the task time-limited, append remaining time
to the observation; then the limit **is** a genuine terminal. These are two different MDPs. **Pick
the time-unaware option** — bootstrap on truncation — and say so in writing. [§5.2]

> **Do not call these "case (a)" and "case (b)".** v1.0 presented that labelling as if it were
> Pardo et al.'s own notation; the paper labels the two regimes **(i)** and **(ii)**. The policy
> recommendation is correctly represented — only the labels were invented. Say "the time-aware and
> time-unaware formulations of Pardo et al. (2018)". [§5.2]

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
> the same shape as the binary-feature normalisation trap below. [§5.2] — note: EXIT-6.1 lives in §6,
> which this file did not read; quoted here only because §5.2 itself quotes it.

**(d) GAE has its own, much shorter horizon** (PPO branch only). The advantage horizon is
`1/(1−γλ)`: at γ=0.995, λ=0.95 that is **18.3 steps = 1.8 s**, against a 200-step return horizon. To
propagate a terminal bonus 200 steps back you need λ ≈ 0.99 (67 steps) or a very good value
function. State which you chose. [§5.2]

---

## Discount arithmetic (§4.2)

Reproduced verbatim — do not recompute any entry in this table.

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
`gamma_new = exp(-dt_new/tau)`. [§4.2, full section]

**Cross-reference to §4's reference-parameter block** (read for context, not part of §4.2 itself):

```
INTEGRATION AND LEARNING
  dt_policy   0.10 s        n_substeps  5  (dt_sub = 0.02 s)
  max_steps   400  (= 40 s = 2 x effective horizon)
  gamma       0.995         -> H_eff = 1/(1-gamma) = 200 steps = 20 s
```

[§4]

**A12, restated as the assumption this arithmetic exists to test:** "γ = 0.995 with `max_steps` =
400, chosen from the manoeuvre timescale (a real park is 120–250 policy steps). If wrong: γ = 0.99
makes the terminal bonus invisible; γ = 0.998 pushes the effective horizon past the episode limit.
Both are measured, not assumed — see EXIT-2.11." Revisit at: Stage 2 exit. [A12]

Note this table's 173.07 (rounded) is the same quantity spelled 173.068 (three-decimal) inside
**EXIT-2.7** and **EXIT-2.28**'s formulas below — reproduced here exactly as each source prints it,
per the "numbers are verbatim" rule; the difference is presentation precision in two different parts
of the source document, not a computation this file performed. [§4.2] [EXIT-2.7] [EXIT-2.28]

---

## Build

Reproduced verbatim.

**Observation (O0) — no rays, no occupancy grid.** Fixed semantic slots (front car / rear car /
kerb / goal-slot), ego frame. Per-object feature vector, **identical width at every stage**:

```
(dx, dy, sin_theta, cos_theta, l, w, type_onehot(3), valid, visible_now, log1p(tau_since_seen))
```

plus the ego block `(v, delta, settle_counter/K_settle)`. `valid` (this slot holds a real object —
padding bit) and `visible_now` (currently sensed) are **two different bits**; conflating them is a
bug. [§5.2]

> **`settle_counter` is not optional and v1.1 omitted it (A22).** §7.5 requires the tolerance
> conditions to hold for `K_settle = 5` **consecutive** steps, so success is a function of history,
> not of a single `WorldState`. If the counter is not in the state and in the observation, then
> (a) I2's "success reads `WorldState`" is false, and (b) the agent cannot tell 1 step into the
> settle window from 4 — **so O0 is not observation-Markov**, and §5.2's title, §6.1's "Full state"
> label and H_A's entire sufficiency argument are all built on a premise that does not hold. The
> symptom is §9's "error histogram piles up just outside the tolerance", misdiagnosed as a tolerance
> problem. Normalise by `K_settle` and include it at **every** rung. [§5.2]

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
constructor. Reward and termination read `WorldState` directly. [§5.2]

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
(where `visible_now` is always 1) and **detonates exactly when you switch on O2**. [§5.2]

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

[§5.2]

> **Naming hazard:** SAC's Polyak rate is `tau = 0.005`, but `1 − tau = 0.995` is numerically
> identical to the discount factor and completely unrelated to it — and `tau` is *also* the name of
> `log1p(tau_since_seen)` in the observation. **Rename at least two of these three before you write
> them twice.** [§5.2]

> **n-step returns are not optional at γ = 0.995 over 200-step episodes.** 1-step TD needs O(200)
> sequential backups to move the terminal bonus to the start state. This is likely the largest
> single sample-efficiency factor after the curriculum. [§5.2]

---

## Exit criteria (ALL 29, whole)

Reproduced whole — ID, criterion text, and the full threshold/rationale text, including italic
"why an earlier version got this wrong" clauses and every "Positive control" requirement. [§5.2]

### Implementation gates (must pass before *any* parking experiment)

| ID | Criterion | Threshold |
|---|---|---|
| **EXIT-2.15** | The exact SAC implementation solves Pendulum-v1 | mean eval return ≥ −200 by 20k env steps, **3/3 seeds** |
| **EXIT-2.16** | The same code solves a 2D point-mass reach with **sparse +100**, −0.05/step, γ=0.995, `max_steps`=400 | success ≥ 90% on a fixed 200-episode set, **3/3 seeds**, 300k steps. *This is the important one:* it is the minimal environment exercising sparse bonus + long horizon + time limit, and it separates "my SAC is broken" from "parking is hard" |

### Correctness gates

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

### Protocol gates (freeze these before any tuning)

| ID | Criterion | Threshold |
|---|---|---|
| **EXIT-2.1** | Frozen eval set integrity | SHA-256 matches a hash literal committed in the eval module; abort on mismatch (**no warn-and-continue path may exist**). Per-scenario `L_oracle`, `g_oracle`, `oracle_min_clearance`, `planner_resolution` present and finite |
| **EXIT-2.2** | Every frozen scenario is oracle-feasible | feasible fraction of VAL and TEST **== 1.000 exactly**; the INFEASIBLE control set == 0.000 at 4× resolution; planner and env collision checkers agree on 10⁴ random configurations |
| **EXIT-2.3** | Evaluation determinism | two runs of the same checkpoint in separate processes: terminal class and episode length identical for **100%**; final pose and `c_min` to 1e-9 |
| **EXIT-2.26** | No eval transitions enter the replay buffer | counter == 0; eval curriculum level == MAX for 100%; eval DR flag == False |
| **EXIT-2.10** | Diagnostic logging completeness | every required key present, finite, at the declared cadence, over a 5000-step smoke run; per-term reward sums reconstruct the episode total to 1e-9 |

### Performance gates

| ID | Criterion | Threshold |
|---|---|---|
| **EXIT-2.27** | Performance on the **Stage-2 easy sub-distribution** (reverse-curriculum rung 0: start pose within 3 m of the goal along the reference path, slot length ≥ 1.5·l; **bay family: `η_bay ≥ 1.55`, i.e. `W_aisle ≥ 6.75 m` at `W_bay = 2.50 m`** *(v1.3)*), at `eps_final`, no randomisation | success ≥ **0.90**; collision ≤ **0.02**; timeout ≤ **0.08**; out-of-bounds ≤ **0.005**; mean path length ≤ **1.5×** the Stage-1 tracked-expert length. **Report the full-difficulty number too, as the Stage-3 baseline — but do not gate on it.** *v1.1 gated Stage 2 on ≥0.90 at **full** difficulty with **no curriculum**, which is strictly harder than EXIT-3.1's ≥0.80 at full difficulty **with** curriculum. Stage 2 would therefore either deadlock forever or, if passed, guarantee that Stage 3 — weeks of curriculum work — is a null result by construction. A stage gate must be easier than the stage that follows it.* |
| **EXIT-2.11** | γ sweep, run as an actual experiment and put in the thesis | γ ∈ {0.99, 0.995, 0.998}, **5 seeds each** (not 3 — §5.4 bans K=3 and EXIT-4.8 asserts K==10 for headline tables; a 3-seed result "put in the thesis" contradicts both. K=5 is the document's own exploratory floor, and this sweep is exploratory), everything else identical. **γ = 0.995 must attain the highest IQM success rate, with its CI not overlapping γ=0.99's upper bound.** If γ = 0.99 wins, the discount analysis is wrong for this reward and the reward scale must be re-derived before Stage 3 |
| **EXIT-2.28** | Critic magnitude bound holds throughout | Compute **programmatically** from the reward config: `B = c_max·(1−γ^max_steps)/(1−γ) + max(\|R_success\|·(1+β), \|P_collision\|) + Φ_clip = 0.05·173.068 + 120 + 30 = 158.65`. **Raise** at `max\|Q\| > 2B ≈ 320`; **warn** at `1.2B ≈ 190`. **Positive control:** with γ dropped from `F` (the EXIT-2.23 bug) the assertion must trip within 200k steps. *v1.1's two-bound rewrite (hard 12280 / soft 600) was **44× too loose**, and it got there by ignoring the very identity a sibling criterion enforces: by Ng–Harada–Russell, `Q′(s,a) = Q(s,a) − Φ(s)` **exactly**, so shaping contributes at most `\|Φ\|_max = 30` — **not** `30/(1−γ) = 6000`. The worst-case step cannot recur every step; that is what telescoping means. v1.1 also summed `R_success = 100` and `P_collision = 40`, which are **mutually exclusive** terminals — the correct term is `max(·)`, not the sum. Both v1.1 numbers were dead: at 12280 the raise fires long after the run is over; at 600 the "warn" fires only when the critic is already 4× beyond anything legitimate.* |
| **EXIT-2.29** | **Five-consumer truncation audit** *(added v1.2)* | I4 names **five** consumers of the terminated/truncated distinction; v1.1 gated **one**. On EXIT-2.5's degenerate MDP (r=+1, γ=0.995, T=10) assert each against a closed form: **(i)** n-step with n=5, λ_n=0.5 — the target at t=T−2 equals the analytic mixed value to 1e-9 and **differs** from the terminated-treatment value by the analytic gap; **(ii)** the last transition's shaping term equals `γΦ(s₄₀₀) − Φ(s₃₉₉)` **bitwise**, NOT `−Φ(s₃₉₉)`; **(iii)** terminal class == TIMEOUT; **(iv)** the curriculum counter increments *attempts* and not *successes*; **(v)** source-level assertion that `terminated or truncated`, `terminated \| truncated` and a bare `done =` appear **nowhere** in the codebase. Threshold: all exact, **and each of (i)–(iv) must FAIL when the flags are deliberately conflated.** *The n-step cut is the more dangerous untested site — at λ_n ≈ 0.5 a wrong cut biases half the target — and the Φ-zeroing site injects a fictitious `−Φ(s₄₀₀)` into every truncated return, which §7.1 warns about and nothing checked. Passing EXIT-2.5 while failing either produces exactly the symptom §9 attributes to EXIT-2.5, sending you to a test that already passes.* |

[§5.2, all 29 criteria, whole]

---

## Blocked / out-of-order items

- **I8's test is EXIT-1.12, a Stage-1 criterion, for "identical width at every observation stage" —
  but EXIT-1.12 itself requires the very thing Stage 2 builds:** "for 500 recorded episodes,
  observations re-rendered under O0/O1/O2 have identical shape and dtype and identical
  `(valid, visible_now)` semantics; O0 recoverable from `WorldState` alone." [EXIT-1.12] [I8 table row]
  §0.3 names this explicitly as a stage-ordering leftover: **"Stage-ordering leftovers: EXIT-0.8
  needs Hybrid A\* (Stage 1); EXIT-1.12 needs the Stage-2 Observer; EXIT-1.4 and the `ell_OBCA`
  denominator need two solvers absent from Stage 1's build list."** [§0.3] — the middle clause is the
  one that touches this file directly: Stage 1's own exit gate cannot run until Stage 2's `Observer`
  hierarchy exists, yet Stage 1 nominally precedes Stage 2 in the stage ladder. [§5, stage ordering]
  [§0.3]
- **`n-step returns... NOT OPTIONAL, see below`** is a Build requirement [§5.2 Build] with the
  accompanying claim that it is "likely the largest single sample-efficiency factor after the
  curriculum" [§5.2], but — already known, not reported as a new finding per this task's
  instructions — **it has no dedicated EXIT-2.x criterion of its own.** The closest thing is
  **EXIT-2.29(i)**, which exercises an n=5, λ_n=0.5 n-step target, but only to test that it respects
  the terminated/truncated distinction (I4's fifth consumer) — it is not a general correctness or
  off-policy-bias test of the n-step mechanism itself. [EXIT-2.29] [§5.2 Build]
- **§7.4's non-positive running reward invariant** — "Every non-terminal reward term other than the
  PBRS term is **≤ 0**, and the **only positive rewards in the entire MDP are terminal**" [§7.4] — is
  the sole stated defence against reward farming, and farming is explicitly a live risk for this
  action space ("for a car with `(a_long, δ̇)` actions, closed cycles in the full state are trivially
  realisable... so this is not hypothetical") [§7.4]. Its only named executable test anywhere in the
  document is **EXIT-3.9**, cited from §9's failure-mode table: "A positive sustainable per-step term
  is being farmed | non-positive running reward invariant; EXIT-3.9" [§9]. EXIT-3.9 is a Stage-3
  criterion, outside this file's scope, and this file has not read it directly. Yet Stage 2's own
  Protocol gates require the reward configuration to be calibrated and **frozen** before Stage 3
  begins ("Calibrate ONCE, on the hardest distribution, then FREEZE" [§7.2]; "**Protocol gates
  (freeze these before any tuning)**" heading over EXIT-2.1 [§5.2]).

[Full elaboration of the consequence of the last item is in the findings section of this file's
accompanying report, not repeated here to avoid duplicating an assessment inside a "verbatim
transcription" section.]

---

## Known-unreviewed content this stage depends on

- **Marker legend, unchanged:** `[V]` independently verified in the v1.1 pass; `[C]` standard,
  existence certain, details unchecked; `[?]` **unverified** — "Verify before it enters a
  bibliography"; `[D]` not a citation, derived and numerically checked, "carries no literature
  claim." **Rule: no `[?]` reference may be cited in a thesis without opening it first.** [§0.1]
- Within Stage 2's own reading list, marked `[?]`: **Puterman (1994/2005)**, **Singh & Yee (1994)**,
  **Jiang, Kulesza, Singh & Lewis (2015)**, **Tallec, Blier & Ollivier (2019)**, **Nikishin et al.
  (2022)**, **Ball, Smith, Kostrikov & Levine (2023)**. [§5.2 Theory table]
- The primary SAC citation itself carries a caveat even at `[C]`: "(Appendix exists; its exact
  equation number was **not** verified)" — this is the paper Stage 2's central tanh-correction
  derivation is attributed to. [§5.2 Theory table]
- **"Every v1.2 correction... is now itself unreviewed"** [header, v1.2] applies in full to this
  stage's three v1.2-corrected performance/correctness criteria — **EXIT-2.27** (rebased onto the
  easy sub-distribution to fix the deadlock-vs-Stage-3 problem), **EXIT-2.28** (the 158.65 bound,
  replacing a v1.1 value the document itself calls "44× too loose"), and **EXIT-2.29** (added
  because v1.1 gated one of I4's five consumers) — and to **A22** ("Added in v1.2; v1.0 and v1.1 both
  omitted it"). [§0.3]
- **EXIT-2.27's bay-family clause (`η_bay ≥ 1.55`, `W_aisle ≥ 6.75 m`) is a v1.3 addition** — "§5.4's
  success surface — all three named a parallel-parking difficulty axis only, so the bay family had no
  gate and no defined surface. Each now carries its `η_bay` counterpart" [§0.4] — and v1.3's own
  closing caveat applies to it: "everything in §0.4 is new, and therefore unreviewed... the *framing*
  around it... has had exactly one pair of eyes on it." [§0.4]
- **Already known, per this task's brief, not reported as a new finding:** n-step returns are
  declared "NOT OPTIONAL" with no dedicated exit criterion, and the off-policy bias mixing n-step
  with 1-step returns introduces is nowhere acknowledged in the text this file read. [§5.2 Build]
  [§0.3, open item 3]
- **Already known:** I3 and I7 still have no executable test (I3: "§7.1"; I7: "static check").
  [§3] [§0.3, open item 5]
- **Already known:** A22 (`settle_counter` is part of the state) was added late, in v1.2. [A22]
  [§0.3]

---

## Failure modes that show up here (§9 rows, pointers only)

Rows whose cause, fix, or explicit EXIT pointer sits inside Stage 2's scope, or whose symptom this
file's own text (§5.2, §7) names directly. Reproduced verbatim; pointer is [§9] for all, plus the
specific EXIT/section each row itself cites.

| Symptom | Likely cause | Fix / test |
|---|---|---|
| Success rate plateaus below the Hybrid A* ceiling; agent seems "less committed" late in episodes; **only the hardest (longest) starts fail** | Truncation treated as termination | EXIT-2.5 |
| Measured entropy drifts monotonically away from −2.0; α collapses < 1e-4 or explodes; later NaN | tanh log-prob correction missing / sign-flipped / naive form | EXIT-2.17/18/19 |
| Car drives smoothly to just outside the slot, then oscillates or creeps forever. Success ≈ 0 | γ too low (0.99) — terminal bonus discounted to 1.8 vs a shaping stream worth up to 98 | γ = 0.995; EXIT-2.11 |
| Slower, much noisier learning; large seed variance; critic loss stays high | γ too high (0.998) — `H_eff = 500 > max_steps = 400` | keep `H_eff` ≲ `max_steps/2` |
| Return climbs steadily and impressively; success flat at zero; episode length saturates at 400; path/RS ratio explodes; video shows something rhythmic and pointless | A positive sustainable per-step term is being farmed | non-positive running reward invariant; EXIT-3.9 *(Stage 3, outside this file's scope)* |
| Higher-than-expected collision rate appearing mid-training and not going away; agent gives up on hard starts and drives into things; return curves look fine | γ dropped from the shaping term → hidden running cost `0.005025·Φ` up to 0.151/step | EXIT-2.6 + EXIT-2.23 |
| Collision rate rises steadily **while return also rises**; the agent drives purposefully into the nearest parked car | Collision penalty sized against per-step rather than **accumulated discounted** cost | EXIT-2.7 |
| Agent approaches confidently, stops 1–2 m short, holds station. Success ≈ 0, collisions ≈ 0 | Safety-margin term is a running cost — a permanent tax on the only successful behaviour | move it inside Φ |
| Flat-zero success with smoothly decreasing pose error; end-of-episode error histogram piles up just outside the tolerance | Hard tolerance, no annealing, no settle window | §5.3 annealing *(Stage 3, outside this file's scope; note the "no settle window" branch of this cause is A22's territory, addressed by Stage 2's own Build, not by §5.3)* |
| Actor loss → −∞; `max\|Q\|` crosses ~300 and keeps climbing; NaN | Deadly-triad divergence | EXIT-2.28; then the ordered fix list: truncation bootstrap → tanh log-prob → normalisation → replay ratio 1 → critic LayerNorm → smaller τ |
| Return curve flat and noisy; car drives in random directions indefinitely | Action detached before entering the critic in the actor loss | EXIT-2.20 |
| Everything is 5× too large; `\|V\|` runs to 1000+ | Reward summed over substeps | EXIT-2.13 |
| Checkpoint scores well in training and near-randomly in a fresh process | VecNormalize statistics not saved with the model | use fixed analytic scaling (§5.2) |
| Performance collapses **the moment O2 is switched on** | Binary flags were being normalised; latent at O0 where `visible_now ≡ 1` | mask them, or use fixed scaling |

[§9, rows as quoted]

---

## Derived by this decomposition (not in PLAN_MACRO)

The section headers, the grouping of entry-condition artefacts "by artefact," and the grouping of
assumptions/theory-table markers under "Known-unreviewed content this stage depends on" are this
file's own organisational choices, following the template given for this task — not text found
verbatim at any single location in `PLAN_MACRO.md`. Every factual claim inside those groupings is
individually back-pointed to its source above. The selection of which §9 rows "belong" to Stage 2
(as opposed to Stage 0/1/3/4) is this file's own judgement call, made from each row's own EXIT
pointer or explicit textual tie to §5.2/§7; rows pointing to Stage-3+ criteria are retained where
Stage 2's own text (Build, §7.2, §7.4, A22) makes the underlying cause a Stage-2 matter even though
the cited fix is not.
