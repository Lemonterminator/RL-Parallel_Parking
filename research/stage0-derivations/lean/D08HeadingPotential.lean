import Mathlib

/-!
On the principal positive branch 0 <= e <= pi,
  1-cos(abs(wrap(e))/2) = 1-cos(e/2).
The following theorems concern that smooth branch. At the wrap seam pi the
wrapped periodic function has different left and right derivatives; the
positive branch value at pi is its LEFT derivative, not a two-sided one.
-/

namespace Stage0

noncomputable section

def headingPhi (e : ℝ) : ℝ := 1 - Real.cos (e / 2)

theorem headingPhi_hasDerivAt (e : ℝ) :
    HasDerivAt headingPhi (Real.sin (e / 2) / 2) e := by
  unfold headingPhi
  convert (hasDerivAt_const e (1 : ℝ)).sub
    ((Real.hasDerivAt_cos (e / 2)).comp e ((hasDerivAt_id e).div_const 2)) using 1
  · ext x
    simp
  · ring

theorem headingPhi_deriv (e : ℝ) :
    deriv headingPhi e = Real.sin (e / 2) / 2 :=
  (headingPhi_hasDerivAt e).deriv

theorem headingPhi_deriv_zero : deriv headingPhi 0 = 0 := by
  simp [headingPhi_deriv]

theorem headingPhi_deriv_pi_div_two :
    deriv headingPhi (Real.pi / 2) = Real.sqrt 2 / 4 := by
  rw [headingPhi_deriv, show Real.pi / 2 / 2 = Real.pi / 4 by ring,
    Real.sin_pi_div_four]
  ring

theorem headingPhi_deriv_pi : deriv headingPhi Real.pi = 1 / 2 := by
  simp [headingPhi_deriv]

/-- There are no stationary points in the positive principal branch. -/
theorem headingPhi_deriv_pos (e : ℝ) (he : 0 < e) (hepi : e ≤ Real.pi) :
    0 < deriv headingPhi e := by
  rw [headingPhi_deriv]
  apply div_pos
  · exact Real.sin_pos_of_pos_of_lt_pi (by linarith) (by linarith [Real.pi_pos])
  · norm_num

theorem headingPhi_deriv_continuous : Continuous (deriv headingPhi) := by
  have hfun : deriv headingPhi = (fun e => Real.sin (e / 2) / 2) :=
    funext headingPhi_deriv
  rw [hfun]
  fun_prop

/-- A correct replacement: the derivative is bounded away from zero near the wrap seam. -/
theorem headingPhi_near_pi_bound (eps e : ℝ)
    (heps : eps ≤ Real.pi / 2) (he : Real.pi - eps ≤ e) (hepi : e ≤ Real.pi) :
    Real.sqrt 2 / 4 ≤ deriv headingPhi e := by
  have hs := Real.sin_le_sin_of_le_of_le_pi_div_two
    (x := Real.pi / 4) (y := e / 2)
    (by linarith [Real.pi_pos]) (by linarith) (by linarith)
  rw [Real.sin_pi_div_four] at hs
  rw [headingPhi_deriv]
  linarith

/-- If a derivative is continuous and zero at the origin, it cannot have a
strict positive absolute lower bound at every positive error. -/
theorem no_uniform_deriv_lower_of_zero (f : ℝ → ℝ)
    (hzero : deriv f 0 = 0) (hcont : ContinuousAt (deriv f) 0)
    (c : ℝ) (hc : 0 < c) :
    ¬ (∀ e : ℝ, 0 < e → e ≤ Real.pi → c < |deriv f e|) := by
  intro hall
  obtain ⟨delta, hdelta, hclose⟩ := Metric.continuousAt_iff.mp hcont c hc
  let e : ℝ := min delta Real.pi / 2
  have he : 0 < e := div_pos (lt_min hdelta Real.pi_pos) (by norm_num)
  have hmin1 : min delta Real.pi ≤ delta := min_le_left _ _
  have hmin2 : min delta Real.pi ≤ Real.pi := min_le_right _ _
  have hedelta : e < delta := by dsimp [e]; linarith
  have hepi : e ≤ Real.pi := by dsimp [e]; linarith [Real.pi_pos]
  have hdist : dist e 0 < delta := by simpa [Real.dist_eq, abs_of_pos he] using hedelta
  have hsmall : |deriv f e| < c := by
    simpa [Real.dist_eq, hzero] using hclose hdist
  exact (not_lt_of_ge hsmall.le) (hall e he hepi)

/-- Fermat's theorem supplies the zero derivative at any smooth local minimum.
Continuity of the derivative at zero is the C1 hypothesis used here. -/
theorem no_uniform_deriv_lower_of_local_min (f : ℝ → ℝ)
    (hmin : IsLocalMin f 0) (hcont : ContinuousAt (deriv f) 0)
    (c : ℝ) (hc : 0 < c) :
    ¬ (∀ e : ℝ, 0 < e → e ≤ Real.pi → c < |deriv f e|) := by
  exact no_uniform_deriv_lower_of_zero f hmin.deriv_eq_zero hcont c hc

theorem headingPhi_not_uniform_point_one :
    ¬ (∀ e : ℝ, 0 < e → e ≤ Real.pi → (1 / 10 : ℝ) < |deriv headingPhi e|) := by
  exact no_uniform_deriv_lower_of_zero headingPhi headingPhi_deriv_zero
    headingPhi_deriv_continuous.continuousAt (1 / 10) (by norm_num)

end
end Stage0
