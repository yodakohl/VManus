# GDT174 — Voynich calibrated fingerprint report

Status: **VOYNICH_PARTLY_OUTSIDE_FROZEN_SYNTHETIC_ENVELOPE**.

The exact published lexical A, human-grown B2, and factorial B controls were
not regenerated or changed. The Voynich panel contains 8448
frozen HPR2 groups on 1143 complete physical lines and
91 physical folios. No f84 row was retained or scored; the
source contains zero f84r rows.

The three synthetic columns use the published GDT173 report's primary
`SURFACE_ONLY` coordinate. Annotation-assisted synthetic rows remain frozen in
the parent fingerprint and are not averaged into this table.

## Directly comparable coordinates

The full required side-by-side table is `gdt174_side_by_side.tsv`. On the
direct axes, 5 metric(s) lie outside the closed synthetic range.
The comparable metric placements are:

- `HOST_RECURRENCE_PROXY / recurrent_host_mass`: **OUTSIDE_SYNTHETIC_RANGE**.
- `HOST_RECURRENCE_PROXY / cross_folio_host_mass`: **OUTSIDE_SYNTHETIC_RANGE**.
- `LEFT_RIGHT_COMPATIBILITY / compatibility_density`: **FACTORIAL_B_LIKE**.
- `LEFT_RIGHT_COMPATIBILITY / null_density`: **OUTSIDE_SYNTHETIC_RANGE**.
- `LEFT_RIGHT_COMPATIBILITY / null_excess`: **B2_LIKE**.
- `SHORT_HOST_STRUCTURE / length_2_3_mass`: **OUTSIDE_SYNTHETIC_RANGE**.
- `EXTERNAL_SUBSTITUTION / mean_delta_cosine`: **OUTSIDE_SYNTHETIC_RANGE**.


Voynich raw-operation compatibility is 0.833333;
the frozen null mean density is 0.871365, leaving excess
-0.038032 with inclusive p
0.939512. This uses the exact GDT173 operation
and null definitions rather than GDT160's different degree-preserving graph
null.

The density alone is therefore misleading: Voynich is factorial-B-like on raw
density, but B2-like on null excess, and the observed density is actually below
its own frozen null expectation. This pass supplies no evidence that a new
control must reproduce factorial-B's specific compatibility excess.

## Direction-only and unresolved coordinates

- `NEXT_HOST`: OUTSIDE_SYNTHETIC_RANGE (-4935.492 raw bits).
- `WHOLE_LINE`: FACTORIAL_B_LIKE_DIRECTION (-3436.627 raw bits).
- Actual host recovery remains unresolved because there is no Voynich oracle.
- Same-group compiler coherence and closure are structurally analogous only.
- Register alignment is unresolved because Voynich registers are not parallel
  renderings of the same content.

## Architectural implication

The coordinates not covered by the frozen controls are: PAGE_HOST recurrence
and cross-folio recurrence (proxies, not recovery), the very high compatibility
null opportunity, length-2/3 host mass, external substitution coherence, and
the negative held NEXT_HOST direction. A future intermediate model would need
to address those coordinates without being tuned to their observed values.
The short-host and external-coherence exceedances are modest in absolute size;
the recurrence comparison is additionally sensitive to the controls' literal
escape population.

Already-covered coordinates do not motivate B3: raw compatibility density is
factorial-B-like, compatibility excess is B2-like, and negative WHOLE_LINE
direction is factorial-B-like. Actual host recovery, same-group compiler
coherence, closure and register alignment remain scientifically unresolved,
not missing-model requirements. These are separate statements, never a joint
score.

This is calibration, not identification. It establishes no Voynich encoder,
word, code, language, morphology, role, meaning, plaintext, or translation.
