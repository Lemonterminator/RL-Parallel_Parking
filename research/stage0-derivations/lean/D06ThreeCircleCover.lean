import Mathlib

/-!
Three-circle cover of a rectangle, with generic dimensions.
The circle at longitudinal centre c is the closed disk
  (x - c)^2 + y^2 <= radius^2.
Coordinates are measured from the rear axle; set a=-r, ell=L+f+r,
h=w/2.  No assumption about the numerical vehicle parameters is used.
-/

namespace Stage0

noncomputable section

private lemma square_le_of_between (x c t : ℝ) (_ht : 0 ≤ t)
    (hlo : c - t ≤ x) (hhi : x ≤ c + t) :
    (x - c) ^ 2 ≤ t ^ 2 := by
  nlinarith [mul_nonneg (sub_nonneg.mpr hlo) (sub_nonneg.mpr hhi)]

def circleCenter (a ell : ℝ) (i : Fin 3) : ℝ :=
  a + ((i.val : ℝ) + 1 / 2) * ell / 3

def coverRadius (ell h : ℝ) : ℝ := Real.sqrt ((ell / 6) ^ 2 + h ^ 2)

theorem coverRadius_sq (ell h : ℝ) :
    coverRadius ell h ^ 2 = (ell / 6) ^ 2 + h ^ 2 := by
  exact Real.sq_sqrt (by positivity)

/-- Every point of the body rectangle belongs to at least one of the three disks. -/
theorem three_circles_cover (a ell h x y : ℝ)
    (hell : 0 ≤ ell) (hh : 0 ≤ h)
    (hxl : a ≤ x) (hxu : x ≤ a + ell)
    (hyl : -h ≤ y) (hyu : y ≤ h) :
    ∃ i : Fin 3,
      (x - circleCenter a ell i) ^ 2 + y ^ 2 ≤ coverRadius ell h ^ 2 := by
  have hy : y ^ 2 ≤ h ^ 2 := by
    simpa using square_le_of_between y 0 h hh (by simpa using hyl) (by simpa using hyu)
  rw [coverRadius_sq]
  by_cases hx0 : x ≤ a + ell / 3
  · refine ⟨0, ?_⟩
    have hx := square_le_of_between x (a + ell / 6) (ell / 6)
      (by positivity) (by linarith) (by linarith)
    norm_num [circleCenter]
    nlinarith
  · by_cases hx1 : x ≤ a + 2 * ell / 3
    · refine ⟨1, ?_⟩
      have hx := square_le_of_between x (a + ell / 2) (ell / 6)
        (by positivity) (by linarith) (by linarith)
      norm_num [circleCenter]
      nlinarith
    · refine ⟨2, ?_⟩
      have hx := square_le_of_between x (a + 5 * ell / 6) (ell / 6)
        (by positivity) (by linarith) (by linarith)
      norm_num [circleCenter]
      nlinarith

end
end Stage0
