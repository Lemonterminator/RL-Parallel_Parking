import Mathlib

/-!
The plane is identified isometrically with Complex. Multiplication by
exp(I*angle) is the ordinary counter-clockwise planar rotation. A translation
is a complex number. The statement concerns endpoint displacement; it does
not assert a time of impact or continuous collision detection.
-/

namespace Stage0

noncomputable section

def rotate (angle : ℝ) (p : ℂ) : ℂ :=
  Complex.exp (Complex.I * (angle : ℂ)) * p

theorem rotation_norm (angle : ℝ) (p : ℂ) : ‖rotate angle p‖ = ‖p‖ := by
  simp [rotate, Complex.norm_exp_I_mul_ofReal]

theorem rotate_add (theta angle : ℝ) (p : ℂ) :
    rotate (theta + angle) p = rotate angle (rotate theta p) := by
  have harg : Complex.I * ((theta + angle : ℝ) : ℂ) =
      Complex.I * (angle : ℂ) + Complex.I * (theta : ℂ) := by
    push_cast
    ring
  simp only [rotate, harg, Complex.exp_add]
  ring

/-- Rotation moves a point by no more than its radius times the absolute angle. -/
theorem rotation_displacement_bound (angle : ℝ) (p : ℂ) :
    ‖rotate angle p - p‖ ≤ ‖p‖ * |angle| := by
  have hfactor : rotate angle p - p =
      (Complex.exp (Complex.I * (angle : ℂ)) - 1) * p := by
    simp [rotate, sub_mul]
  rw [hfactor, norm_mul]
  have h := Real.norm_exp_I_mul_ofReal_sub_one_le (x := angle)
  calc
    ‖Complex.exp (Complex.I * (angle : ℂ)) - 1‖ * ‖p‖ ≤ |angle| * ‖p‖ := by
      simpa only [Real.norm_eq_abs] using mul_le_mul_of_nonneg_right h (norm_nonneg p)
    _ = ‖p‖ * |angle| := mul_comm _ _

/-- Any translation followed by rotation satisfies the requested triangle bound. -/
theorem rigid_displacement_bound (translation p : ℂ) (angle dmax : ℝ)
    (hp : ‖p‖ ≤ dmax) :
    ‖translation + rotate angle p - p‖ ≤ ‖translation‖ + dmax * |angle| := by
  calc
    ‖translation + rotate angle p - p‖ = ‖translation + (rotate angle p - p)‖ := by
      congr 1; ring
    _ ≤ ‖translation‖ + ‖rotate angle p - p‖ := norm_add_le _ _
    _ ≤ ‖translation‖ + ‖p‖ * |angle| := by
      gcongr
      exact rotation_displacement_bound angle p
    _ ≤ ‖translation‖ + dmax * |angle| := by gcongr

/-- The same statement with an arbitrary initial heading, as in a vehicle pose update. -/
theorem pose_displacement_bound (translation p : ℂ) (theta angle dmax : ℝ)
    (hp : ‖p‖ ≤ dmax) :
    ‖translation + rotate (theta + angle) p - rotate theta p‖ ≤
      ‖translation‖ + dmax * |angle| := by
  simpa only [rotate_add] using rigid_displacement_bound translation (rotate theta p)
    angle dmax (by simpa only [rotation_norm] using hp)

/-- Rear overhang is no larger than forward reach; hence every body point has this radius bound. -/
theorem body_radius_bound (p : ℂ) (r b h : ℝ)
    (_hr : 0 ≤ r) (hb : r ≤ b) (_hh : 0 ≤ h)
    (hxl : -r ≤ p.re) (hxu : p.re ≤ b)
    (hyl : -h ≤ p.im) (hyu : p.im ≤ h) :
    ‖p‖ ≤ Real.sqrt (b ^ 2 + h ^ 2) := by
  have hbl : -b ≤ p.re := by linarith
  have hx : p.re ^ 2 ≤ b ^ 2 := by
    nlinarith [mul_nonneg (sub_nonneg.mpr hbl) (sub_nonneg.mpr hxu)]
  have hy : p.im ^ 2 ≤ h ^ 2 := by
    nlinarith [mul_nonneg (sub_nonneg.mpr hyl) (sub_nonneg.mpr hyu)]
  have hnorm : ‖p‖ ^ 2 = p.re ^ 2 + p.im ^ 2 := by
    rw [Complex.sq_norm, Complex.normSq_apply]
    ring
  have hsqrt : (Real.sqrt (b ^ 2 + h ^ 2)) ^ 2 = b ^ 2 + h ^ 2 :=
    Real.sq_sqrt (by positivity)
  have hsnonneg := Real.sqrt_nonneg (b ^ 2 + h ^ 2)
  nlinarith [norm_nonneg p]

end
end Stage0
