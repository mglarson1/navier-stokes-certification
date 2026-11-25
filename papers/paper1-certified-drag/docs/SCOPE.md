# What the T = 2 certificate establishes

The certificate concerns the drag functional defined in the manuscript for the
rotational-slip cylinder model in a periodic three-dimensional finite annulus
with the specified sponge, Re = 500 and viscosity 1/250. The initial total
velocity is the exact archived Newton field U + y; the weak perturbation starts
from w₀ = y. The weak-solution class must satisfy the stated energy inequality.

For every solution in that class, the drag lies in
`[0.112699029269657744, 0.112852594864699145]`. This is a functional statement
without an assumption or conclusion of uniqueness of weak solutions. It does
not assert pointwise accuracy of the computed state.

The variational strain parameters are β = 1/2 and γ = 27/10. The full physical
residual bound is ρ = 92103/10⁹. The factor 1/β is present in the linear budget;
the nonlinear remainder contributes about 42% of the total radius. The holding
force has not been subtracted from the physical residual. The exact rational
budget and its outward decimal endpoints are in `Newton_T2_variational.json`.

The authoritative certificate record has SHA-256
`97e24fa6e41af04bbf430db7a5ab30432f322ffc3e090787c7e8f1f412a9a651`.
It is bound to the full release and strain/audit records in the T2 archive.
The convenience JSON in this repository is not a standalone proof.

## Verification levels

1. Hashes establish identity of the files being checked.
2. Exact arithmetic and record checks establish the documented assembly,
   completeness and algebraic consistency of the archived enclosure records.
3. The portable replays rerun the frozen independent scalar/time, geometric and
   physical-cover programs against the extracted inputs.
4. The native independent numerical audit covers the recorded selection of
   546 new strain cells and six complete load cells, with the inherited evidence
   bound into the release. This is not an exhaustive independent numerical
   recomputation of all production spatial enclosures.

The complete mathematical claim retains the manuscript's model, weak-class,
initial-field and bounded-arithmetic assumptions. Neither this repository nor a
successful run claims formal verification of the entire software/hardware stack.

## Boundaries of the result

- T = 2 is a completed certificate. Longer-window results, including T = 10,
  remain diagnostics. A continuous interval of certified window lengths is not
  inferred from finitely many certified points.
- The earlier archive's conditional T = 2 record is superseded by this release.
  Historical finite-volume diagnostics are not premises of the certificate.
- Not all large regenerable production point caches are redistributed. The
  documented seven portable checks do not require them; complete production
  regeneration is a different task.
- The missing historical source snapshot for the original candidate-976
  construction run remains documented. Its exact field coefficients and the
  stated enclosure-source coverage are preserved. No later source copy has been
  presented as the missing executed snapshot.

The deposit's `T2_Verification_Guide.pdf` provides the detailed evidence map and
the original commands, including the optional platform-dependent numerical load
replay. Historical README text and manuscript snapshots inside frozen archives
record their original preparation state; the publication README explains the
subsequent manuscript alignment without changing those archive bytes.
