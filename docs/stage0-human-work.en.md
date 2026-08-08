# Stage 0: Theory and Research Work Requiring Human Review

This checklist was extracted from `stages/PLAN_S0.md`, as organized by Claude. Code and automated tests can only validate a model that has already been written down. The reading, independent derivations, research decisions, and visual judgments below still require human responsibility and cannot be replaced by a passing test suite.

## 1. Theory Reading

- [ ] Required: LaValle, *Planning Algorithms*, Sections 13.1.2 and 15.3. Focus on the simple-car/bicycle model, nonholonomic constraints, and configuration space.
- [ ] Required: Rajamani, *Vehicle Dynamics and Control*, Chapter 2. Focus on Ackermann geometry, the instantaneous center of rotation (ICR), and the distinction between rear-axle and center-of-gravity (CoG) reference points.
- [ ] Recommended: Ericson, *Real-Time Collision Detection*, Chapters 4-5. The plan still marks this source as `[?]`; before citing it in the thesis, personally open it and verify the edition, chapters, and conclusions.
- [ ] Minimum parallel-parking-space literature: verify the two distinct Vorobieva et al. papers from 2012 and 2013 rather than merging them into one source. Confirm each formula's conventions for body length, wheelbase, front and rear overhangs, and reference point.
- [ ] Blackburn, *The Geometry of Perfect Parking*: the document exists, but the plan still treats its algebraic conclusions as unverified. Check every equation before citing or adopting it.

## 2. Material That Must Be Derived Independently by Hand

- [ ] Re-derive `R=L/tan(delta)` from the rear-axle bicycle equations and explain how it differs from the CoG formulation. Check the sign conventions for forward/reverse motion and left/right steering.
- [ ] Derive the ideal two-arc, equal-and-opposite-curvature S-curve. Confirm that `sqrt(4 R d - d^2)` is only a geometric lower bound in the infinite steering-rate limit; defer practical feasibility with steering-rate ramps to Stage 1.
- [ ] Independently derive the minimum parallel-parking slot. Fix the kerb side and steering-angle sign, label the turning radii of all four corners, and write four sets of clearance inequalities for the front vehicle, rear vehicle, kerb side, and traffic side. Do not reproduce a closed-form expression from memory.
- [ ] Review the reverse-bay single-cut boundary and static-containment lower bound, including the physical meanings and signs of `W_gap`, `W_bay`, clearance, and the mouth clip.
- [ ] Derive OBB signed distance by case: vertex-edge Euclidean distance when separated, the four-axis minimum translation vector (MTV) when intersecting, and translation depth under complete containment.
- [ ] Derive the centers and radii of the three-circle body cover and prove that it conservatively covers the vehicle. Also confirm that it is restricted to smooth reward terms and cannot enter termination or metric paths.
- [ ] Derive the CCD motion bound `translation + d_max*abs(delta_heading)`. Explain why it establishes only a sampling-resolution bound and is not an analytic time of impact (TOI).
- [ ] Derive the heading potential and its derivative, including the semantics of the successful orientation. Check errors near 0, pi/2, and pi, as well as reverse-bay nose-out and nose-in configurations.
- [ ] Manually verify the explicit-Euler update order, zero-order hold, action clamp, state clamp, latency FIFO, and the audit boundary around all five substeps.

## 3. Human Decisions or a Second Pair of Eyes Required

- [ ] Review the material introduced in plan versions 1.2 and 1.3: A22, A24, A27, and EXIT-0.10 through EXIT-0.15. The plan explicitly identifies these additions as unreviewed.
- [ ] Choose the scenario model for `W_gap`: a conservative wall model or an adjacent-vehicle model. It must not be derived silently from `W_bay`.
- [ ] Decide whether the single circular arc is only an analytical baseline and which operational oracle will ultimately define the bay-difficulty threshold.
- [ ] Confirm that the reverse-bay task accepts only nose-out parking. If nose-in should also be accepted, change the task definition and baseline rather than weakening the current success test.
- [ ] Decide whether the documentation should continue to use the term "exact CCD." The current implementation and proof provide motion-bounded sampled CCD. Analytic TOI would require a separate implementation and EXIT contract.
- [ ] Decide whether `steering_gain` and `steering_offset` apply to the target steering angle, steering rate, or sensor mapping. Stage 0 currently rejects non-default values to avoid silently selecting the wrong semantics.
- [ ] Revise EXIT-0.12. Recommended wording: "No additional stationary points outside the success tolerance, with a lower bound maintained over a specified interval near pi." Do not require a derivative greater than 0.1 over all `(0,pi]`.
- [ ] Revise EXIT-0.13. `max_y` should be measured over the complete sweep, while only the bay-row x extent is clipped to `y<=0`. Infeasible grid entries satisfying `W_gap-2c < w` should explicitly expect `InfeasibleBayGeometry`.
- [ ] Run the full EXIT-0.11 stress test: `10^6` sequences, 400 policy steps per sequence, and 5 substeps per policy step. Preserve the seed, configuration hash, commit hash, sample count, zero-violation result, and positive-control result. The registry must remain `planned` until this run is complete.

## 4. Manual Animation Acceptance

After installing `.[replay]`, record and inspect the following trajectories frame by frame. Retain the trace hash and screenshots or video as research notes:

- [ ] The rotation directions under positive speed, negative speed, positive full lock, and negative full lock all agree with the coordinate conventions.
- [ ] Constant-steering trajectories follow a circle around the rear-axle ICR; the front and rear overhangs are not mistakenly used as the reference point.
- [ ] The continuous sweep does not miss a collision at full lock when passing a 0.055 m thin wall or crossing a thin wall perpendicularly.
- [ ] The S-curve and direction changes contain no teleportation, steering-angle discontinuity, or extra one-policy-step latency offset.
- [ ] Saved and replayed trajectories are identical frame by frame for the same initial state, actions, seed, configuration, and commit.
- [ ] Reverse-bay nose-out succeeds, while the geometrically identical nose-in footprint is explicitly rejected.

## 5. Work That Can Only Be Completed in Stage 1

- [ ] EXIT-0.8: numerically bisect the minimum parallel-parking-slot curve with single-cusp Hybrid A*.
- [ ] EXIT-0.14(c): with `W_bay=2.50`, use Hybrid A* to bisect `W_aisle`; the result must lie in `[3.5100, 4.3519]`.
- [ ] Validate the steering-rate-limited feasibility of the S-curve (EXIT-1.8) and use the planner as the operational bay-feasibility oracle.
