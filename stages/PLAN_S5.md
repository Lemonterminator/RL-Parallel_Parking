# PLAN_S5 — Stage 5: Research contribution (optional)

*Decomposed from `PLAN_MACRO.md` (§5.5, §5.5.1, §0.5, §1, and §10's Preference-based RL block).
Every substantive line below carries a back-pointer to the source. Nothing has been verified,
corrected, or fact-checked in producing this file — it is a reorganisation, not a review.*

---

## READ FIRST — verification status (the v1.4 warnings, verbatim)

> **§5.5.1 is new in v1.4. It is unreviewed, and every entry in its reading list is marked `[?]`.
> Nothing in this document should be read as settled.** [§0.5] [§10]

The source states this directly, in two places. First, §0.5's own closing assessment of the material
this whole file is built from:

> **Unreviewed, and this one is weaker than §0.4:** §0.4's arithmetic was machine-checked against an
> independent construction. Nothing here is. The citations are from memory, the four-arm design has had
> one pair of eyes on it, and the claim that CPL's max-entropy identity composes cleanly with this
> plan's SAC configuration is an **argument**, not a verified derivation. [§0.5]

Second, the reading-list header in §10, immediately before the block copied in full below:

> **Preference-based RL — for §5.5.1.** *(added v1.4)* **Every entry below was written from memory and
> is `[?]`; the CPL author list in particular must be checked before it enters a bibliography (§0.1).**
> [§10]

And the document's own running "Open items" ledger, filed under v1.4, which post-dates and covers all
of §0.5 and §5.5.1:

> 1. **The whole of §0.5 is unreviewed and unverified**, and unlike §0.4 it has no numerical anchor.
> 2. **The reading list added to §10 is 100% `[?]`.** The CPL entry is load-bearing for §5.5.1's central
>    argument and is the single most important thing to verify in this document right now.
> 3. **CPL's assumptions have not been checked against this MDP line by line.** The regret-based
>    preference model, the segment-level formulation, and the conservative variant's role are asserted
>    from memory. Before building: read the paper and write the assumption list into §2 as A29+.
> 4. **The §5.5 contribution slot is now over-subscribed** — six candidates against a Stage-4 budget of
>    ~860 GPU-hours (§5.4.1). §5.5.1 says which pair composes; nothing says which one wins.
> 5. Everything still open from §0.3 and §0.4. [Appendix, v1.4 open items]

Also directly relevant, from §0.5's changelog paragraph:

> **§10** — a preference-based-RL reading block, **entirely `[?]`**. [§0.5]

**Do not treat any claim, number, or citation below as settled.** This file inherits §5.5.1's
unreviewed status in full — copying it into its own file changes nothing about its verification state.

---

## Entry conditions — what Stages 0-4 must have produced, by artefact

The plan states these explicitly, scattered across §5.5.1's prerequisites table and its surrounding
text; collected here by artefact rather than by stage:

- **`pi_ref`, the frozen eval set, and the metric set** — lands in Stage 2–4, marked "free" (i.e. no
  additional engineering beyond what those stages already build). [§5.5.1 prerequisites table]
- **The Stage-2/3 SAC policy itself**, which the four-arm design calls **P0** and treats as both
  `pi_ref` and "the safety floor everything else is measured against." [§5.5.1 four-arm table]
- **Exact `log pi_theta(a|s)` with the tanh Jacobian** — lands in Stage 2, marked "free — EXIT-2.17/
  2.18/2.19 already test it." [§5.5.1 prerequisites table]
- **The drawn-path trackability probe** — lands in Stage 1, "do it early," gated by **EXIT-1.13**.
  [§5.5.1 prerequisites table] [EXIT-1.13]
- **A teleoperation front end + logging pipeline** — lands in Stage 1; the note attached is
  "`render.py` (Stage 0) already has trajectory replay; this is input handling plus a logger," gated
  by **EXIT-1.14**. [§5.5.1 prerequisites table] [EXIT-1.14]
- **Bitwise-deterministic replay of `(seed, action sequence)`** — invoked by §5.5.1 as "the
  determinism dividend," sourced to EXIT-0.9, which this file has not read directly but which
  §5.5.1 and EXIT-1.14(a) both cite as already established. [§5.5.1 "Two structural facts"] [EXIT-1.14]
- **The Stage-4 compute budget the contribution slot competes against** — §5.5.1 states this as
  "~860 GPU-hours," itself pointing to §5.4.1, which this file has not read directly. [§5.5.1 "And the
  cost, stated plainly"]

No other Stage 0-4 artefact is named anywhere in §5.5 or §5.5.1 as a precondition for Stage 5.
Whether the six candidate directions' own **comparison baselines** (as opposed to the above shared
infrastructure) are actually built by Stage 4 is a separate question, addressed in the final report,
not in this section — this section only reports what the plan itself lists as a precondition.

---

## Candidate directions (all six, verbatim)

> Stage 4 establishes that the machinery works. Stage 5 is where a contribution can live. Candidates,
> ranked by strength, each with its fair baseline: [§5.5]

| Direction | Why it is defensible | Its fair baseline |
|---|---|---|
| **Degraded perception (O4)** — occlusion, missed detections, association ambiguity | Planning under partial observability needs either intractable belief-space planning or a hand-built filter plus replanning. RL learns a policy on the observation history directly. **Strongest.** | Hand-filter + Hybrid A* replanning each step |
| **Zero-shot generalisation over slot geometry** without replanning | Constant-time inference vs per-scenario search | Hybrid A* re-run per scenario, with its p95/max search time reported |
| **Robustness to model error and actuator latency** | Open-loop plans degrade; a closed-loop policy can absorb it | MPC with the nominal model |
| **Safe RL** — CBF / shielding for a zero-collision guarantee | Addresses the one thing the search baseline has and the policy does not | The unshielded policy, and the planner's guarantee |
| **Sample efficiency of planner-guided RL** | Quantifies what Stage 1's infrastructure actually bought | No-demo SAC at matched wall-clock **and** matched gradient steps |
| **Preference-based fine-tuning (CPL)** — learn the *style* component the programmatic reward cannot express *(added v1.4)* | This task has a **computable ground-truth reward**, so preferences can be synthesised with known provenance and recovery measured exactly — a controlled condition almost no preference-learning paper has. **§5.5.1** | PEBBLE-style PbRL (reward model + SAC), **and** the reward-optimal SAC policy, which it must not degrade |

[§5.5]

---

## What RL cannot claim here (verbatim, unsoftened)

> **What RL cannot claim here — write this in the thesis.** Do not claim shorter paths on a known
> static map (expect ρ > 1 and report it). Do not claim safety (the search baseline returns a
> collision-checked path; the policy returns nothing of the kind). Do not claim efficiency (training
> costs orders of magnitude more compute than planning). And do not present the classical baselines as
> strawmen — build them properly, which is what Stage 1 is for. [§5.5.1]

---

## §5.5.1 Preference-based fine-tuning (all subsections)

### Naming and framing

**Get the name right first.** The family is **preference-based RL (PbRL)** / RLHF for control, not
"trajectory learning". The DPO analogue for control is **CPL (Contrastive Preference Learning)**, and
**CPL, not DPO, is the right object here** — for a reason specific to this plan: [§5.5.1]

> DPO's Bradley–Terry model is built on **return** and treats the whole output as one bandit action.
> CPL replaces both: preferences are generated by **regret** (a sum of advantages), and it uses the
> maximum-entropy RL identity `A*(s,a) = alpha * log pi*(a|s)` to turn that regret into a sum of
> log-probabilities — yielding a DPO-shaped supervised loss with **no reward model and no RL loop**.
> **A11 already commits this project to SAC, which *is* max-entropy RL.** CPL's derivation sits on the
> framework you have already chosen; DPO's does not. [§5.5.1] [A11]

### Two structural facts before designing anything

1. **The determinism dividend.** DPO's bandit reduction is invalid in a stochastic MDP. **EXIT-0.9
   asserts bitwise determinism**, so with a fixed seed the reduction is *exact* here, and a human
   trajectory can be replayed against a policy rollout from a bitwise-identical initial state. Very
   few preference-learning settings have this.
2. **One bit per 400 steps.** A trajectory-level preference is ~1 bit of supervision for 400 actions.
   This, not the loss function, is the binding constraint. Plan the label budget first. [§5.5.1]

### The one thing that must not be the framing

**The one thing that must not be the framing.** Preference learning exists because the reward cannot
be written down. **Here it can** — collision, success, path length and cusp cost (§4.1) are all exactly
computable. Proposing to *learn the reward* invites exactly the objection **A19** raises against
presenting O0 as a result: "why not use the reward you already have?" The target must be the part the
programmatic reward provably does not express — style and margin discipline: *don't shave the
neighbour even when it is geometrically legal; keep the rear neighbour observable; prefer the
manoeuvre a person would recognise.* [§5.5.1] [A19]

### Four arms. P3 runs first and is a gate, not a result.

| Arm | Content | Role |
|---|---|---|
| **P3** | **Synthetic preferences generated from the known programmatic reward** | **Validity gate — run this before collecting a single human label.** If CPL cannot recover the policy when the preference-generating reward is one you fully control, human preferences never will. Near-zero cost, and it fails fast |
| **P0** | The Stage-2/3 SAC policy | `pi_ref`, and the safety floor everything else is measured against |
| **P1** | CPL fine-tune of `pi_ref`, **zero environment interaction** | the claim |
| **P2** | PEBBLE-style PbRL: learn a reward model, then run SAC | the baseline CPL claims to beat; without it "CPL works" is unfalsifiable |

P3 also converts a vague idea into a falsifiable study: **the sample complexity of preference learning
on a task with a known optimal policy, a known reward, and a known feasibility boundary.** Stages 0–4
build all three. That is the contribution, not "we applied DPO to parking". [§5.5.1]

### Two traps that will each cost a week

> **Trap 1 — tanh saturation.** CPL needs `log pi_theta(a|s)` evaluated on **executed** actions. Full
> lock is the *normal* action in this task, and the tanh-squashed Gaussian's log-density **diverges as
> `|a| -> 1`**. Any pair in which one branch saturates will dominate the loss. **Clip actions to
> `(-1+eps, 1-eps)` before computing log-probs**, `eps = 1e-6`, and assert it. This is the same
> numerical wall EXIT-2.19 documents for `|u| >= 10`, relocated.
>
> **Trap 2 — beta versus safety.** `beta` sets the KL leash to `pi_ref`. **Style preferences have no
> reason whatsoever to preserve safety.** Hard gate, on the §8 frozen set: the preference-tuned policy's
> collision rate must not exceed `pi_ref`'s, in the 10 pp units of EXIT-3.2/3.10. A style win bought
> with collisions is not a result. [§5.5.1]

### Human teleoperation data — what it is good for, and what it is not

A front-end where a person drives the simulated car and the full trajectory is logged is **worth more
than a drawing tool, and it is worth it for a reason that is easy to state**: the human is *in the
loop with the simulator*, so every action is already inside the action box and every transition is
already dynamically feasible. **A15's entire objection — that demonstrations must be executed through
the environment rather than used as raw `(state, action)` pairs — is satisfied by construction.** No
tracking controller, no curvature check, no resampling. Drawn paths need all three (EXIT-1.13).
[§5.5.1] [A15] [EXIT-1.13]

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
   knows about crashes. [§5.5.1] [A11] [EXIT-0.9 as cited by §5.5.1]

A fourth, nearly free: a **human contour** overlaid on §5.4's success-rate surface, alongside the
oracle boundary and the §5.0(c') containment bound. "Where does a person fail?" is a cheap and strong
figure, and it costs one extra pass over data collected anyway. [§5.5.1]

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
> the policy that actions outside the box exist. [§5.5.1] [A23] [EXIT-1.14]

### Prerequisites, and where each lands

| What | Stage | Note |
|---|---|---|
| Drawn-path trackability probe | **Stage 1**, do it early | **EXIT-1.13** — 1–2 days, kills the drawing idea cheaply if it is going to die |
| Teleoperation front end + logging | Stage 1 | `render.py` (Stage 0) already has trajectory replay; this is input handling plus a logger. **EXIT-1.14** |
| Exact `log pi_theta(a\|s)` with the tanh Jacobian | Stage 2 | free — **EXIT-2.17/2.18/2.19 already test it** |
| `pi_ref`, frozen eval set, the metric set | Stage 2–4 | free |

[§5.5.1]

### And the cost, stated plainly

**And the cost, stated plainly.** §5.5 is the *contribution slot* and Stage 4 already costs ~860
GPU-hours (§5.4.1). This direction is **not additive with the O3/memory comparison** — pick one as the
thesis contribution. The one candidate it *does* compose with is **"Sample efficiency of
planner-guided RL"**, which shares the demonstration pipeline, `pi_ref`, and the matched-budget
controls; if you want both, merge them into one experiment rather than running them side by side.
[§5.5.1]

---

## Supporting exit criteria (EXIT-1.13, EXIT-1.14, whole)

| ID | Criterion | Threshold |
|---|---|---|
| **EXIT-1.13** | **Hand-drawn paths are trackable at all** *(added v1.4 — the cheap kill-switch on the whole sketch-input idea)* | Collect **≥ 50** freehand paths over the reference scenes. Resample to arc length, fit a `C²` spline, and report: **(a)** the fraction with `max κ ≤ κ_max = 0.25338 1/m` **before** any repair, **(b)** the same fraction after curvature-limited refitting, **(c)** the fraction whose refitted path is still collision-free, **(d)** closed-loop tracking error under the §5.1 rear-axle pure-pursuit controller. **Gate: (d) must meet EXIT-1.8's bounds (peak lateral ≤ 0.05 m, terminal ≤ 0.05 m and ≤ 2°) on ≥ 80% of the corpus.** Below that, **sketch input is dead** — say so and stop, do not add a repair pipeline. *A15 forbids raw `(state, action)` demonstrations because RS paths have unbounded implied `δ̇`; a freehand path is strictly worse, since nothing constrains its curvature at all. This criterion costs 1–2 days and is the whole reason to run it before building anything on §5.5.1.* |
| **EXIT-1.14** | **Teleoperation logs are replayable, un-privileged, and not lag-poisoned** *(added v1.4)* | **(a) Bitwise replay:** feeding a logged episode's `(seed, action sequence)` back through the environment reproduces the recorded `WorldState` trajectory **bitwise**, for 100% of episodes — this is EXIT-0.9 applied to the game and it fails immediately if the logger records at render rate rather than `dt_policy`, or records the *requested* action rather than the **clamped** one. **(b) Lag:** cross-correlate each logged action channel against the state signal it responds to; report the argmax lag; **require ≤ 1 policy step** at the chosen time dilation (start at 1 sim-second ≥ 4 wall-clock seconds) and **report the dilation factor with the corpus**. **(c) Provenance:** every episode carries the observation rung it was collected under; assert no O0-collected episode is consumed by an O2+ arm. *(a) catches a silent corruption of the entire corpus; (b) is **A23** arriving through the human rather than the actuator — clone a lagged demonstrator and you clone the lag; (c) is §6.5's privileged-information caveat, which a full-screen game view violates by default.* |

[EXIT-1.13] [EXIT-1.14]

---

## Blocked / out-of-order items

- **P3 must run before a single human preference label is collected.** It is explicitly a "validity
  gate," not a result: "If CPL cannot recover the policy when the preference-generating reward is one
  you fully control, human preferences never will." [§5.5.1 four-arm table, P3 row]
- **The drawn-path trackability probe is sequenced into Stage 1, "do it early,"** specifically so it
  can kill the sketch-input idea "cheaply if it is going to die" before anything else in §5.5.1 is
  built on top of it. [§5.5.1 prerequisites table] [EXIT-1.13]
- **CPL's assumptions have not been checked against this MDP line by line**, and the plan's own
  instruction is: "Before building: read the paper and write the assumption list into §2 as A29+."
  Nothing under §5.5.1 should be built until that happens. [Appendix, v1.4 open items, item 3]
- **The CPL contribution is explicitly not additive with the Stage-4 O3/memory comparison** — the plan
  says "pick one as the thesis contribution," and separately identifies "Sample efficiency of
  planner-guided RL" as the one direction it *does* compose with, on condition the two are merged into
  one experiment rather than run side by side. [§5.5.1 "And the cost, stated plainly"]
- **The CPL reading-list entry is flagged as blocking its own citation:** "the CPL author list in
  particular must be checked before it enters a bibliography (§0.1)." [§10]

---

## Open questions that must be closed before any of this is built

Restated from the plan's own "Open items after v1.4" ledger and §0.5, verbatim in substance:

1. **The whole of §0.5 is unreviewed and unverified**, and unlike §0.4 (which was machine-checked
   against an independent numerical construction) it has no numerical anchor at all. [Appendix, v1.4
   open items, item 1] [§0.5]
2. **The reading list added to §10 is 100% `[?]`.** The CPL entry — Hejna, Rafailov, Sikchi, Finn,
   Niekum, Knox & Sadigh (2024), ICLR 2024 — is explicitly called "load-bearing for §5.5.1's central
   argument and ... the single most important thing to verify in this document right now."
   [Appendix, v1.4 open items, item 2] [§10]
3. **CPL's assumptions have not been checked against this MDP line by line.** The regret-based
   preference model, the segment-level formulation, and the conservative variant's role are all
   "asserted from memory." [Appendix, v1.4 open items, item 3]
4. **The §5.5 contribution slot is over-subscribed:** six candidates against a Stage-4 budget of
   ~860 GPU-hours. §5.5.1 states which pair composes (CPL + sample-efficiency); nothing in the source
   states which candidate should actually win the slot. [Appendix, v1.4 open items, item 4] [§5.5.1]
5. **Everything still open from §0.3 and §0.4** carries forward unresolved — this file has not read
   §0.3 or §0.4 and cannot enumerate their contents. [Appendix, v1.4 open items, item 5]
6. **Whether CPL's max-entropy identity actually composes cleanly with this plan's SAC configuration
   is, in the source's own words, "an argument, not a verified derivation."** [§0.5]

---

## Derived by this decomposition (not in PLAN_MACRO)

The section headers, the grouping of prerequisites "by artefact," and the restatement of already-open
items as forward-looking "questions that must be closed" in the section above are this file's own
organisational choices, not text found verbatim at any single location in `PLAN_MACRO.md`. Every
factual claim inside those sections is individually back-pointed to its source above; nothing has been
added, resolved, softened, or corrected beyond that reorganisation.
