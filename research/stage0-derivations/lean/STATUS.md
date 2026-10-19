# Lean 4 proof status

**第 6、7、8 项全部已实际编译通过。**

- Environment: WSL Ubuntu 22.04; Lean `4.36.0-rc1`.
- Mathlib revision: `9c6a29e8f339d650449067da68001b28a59a3d8c`.
- Compilation used the pinned Mathlib checkout `/home/linan/stage0-mathlib`.
- The final unedited source files were checked with `lake env lean <absolute-file>`.
- Each final command returned exit status `0`; see `COMPILE.log`.
- There is no `sorry`, `admit`, or user-declared axiom in the proof files.

## Formalized scope

| File | Theorems |
|---|---|
| `D06ThreeCircleCover.lean` | General rectangle `[a,a+ell] × [-h,h]`, `ell,h >= 0`; for every point there exists `i : Fin 3` whose disk of radius `sqrt((ell/6)^2+h^2)` contains it. The proof splits the longitudinal interval into thirds and bounds each squared coordinate. |
| `D07RigidDisplacement.lean` | Complex numbers represent the Euclidean plane. Multiplication by `exp(I*angle)` is counterclockwise rotation. Rotation displacement is at most `norm(p)*abs(angle)`; adding a translation and an arbitrary initial heading gives the full requested bound. A separate algebraic theorem establishes the body-radius bound when forward reach `b >= r >= 0`. |
| `D08HeadingPotential.lean` | Exact derivative of `1-cos(e/2)`, its values at `0`, `pi/2`, and `pi`, positivity for `0 < e <= pi`, a lower bound `sqrt(2)/4` whenever `pi-eps <= e <= pi` and `eps <= pi/2`, and impossibility of any strict positive derivative-magnitude lower bound on every positive error when the derivative is continuous and zero at the minimum. Fermat's theorem connects this to a local minimum. |

The heading file proves the smooth **positive principal branch**. It does not claim
that the periodically wrapped potential has a two-sided derivative at `e = pi`.
The branch derivative there is the left derivative of the wrapped potential.

The displacement file proves a displacement bound. It does not formalize a
collision detector, a wall model, collision times, or the claimed detection rate.

## Reproduce from this directory

Install `elan` if Lean is not already installed, then run:

```sh
lake update
lake exe cache get
lake env lean D06ThreeCircleCover.lean
lake env lean D07RigidDisplacement.lean
lake env lean D08HeadingPotential.lean
```

The checked environment's toolchain and Mathlib revision are pinned in
`lean-toolchain` and `lakefile.toml`. The large local cache and downloaded
Mathlib source are outside this delivery directory.
