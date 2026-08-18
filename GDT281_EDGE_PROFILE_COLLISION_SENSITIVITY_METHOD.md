# GDT281 — collision-free sensitivity of the GDT280 edge profile

## Purpose

GDT280 used the inherited 256-context SHA-256 ceiling.  That kept every model
capacity-matched to GDT276, but adding even a constant tuple coordinate can
reassign hash collisions.  GDT281 asks only whether the categorical profile
found in GDT280 survives when context identities are represented exactly.

GDT280 is byte-frozen.  This method and `gdt281_design.json` are frozen before
the exact-context score is run.  No corpus, feature, endpoint, substring, or
semantic field is added.

## Frozen panel

Primary native panels:

- `LATIN_SCHOLASTIC_GRAPHEMATIC`;
- `LATIN_MEDICAL_GRAPHEMATIC`;
- `LATIN_15C_GRAPHEMATIC`;
- `VOYNICH_REFERENCE`.

Existing layout sensitivities are retained for Latin medical, mixed 15c Latin,
and Voynich in `LENGTH_MATCHED_OVERLAY` and
`MATCHED_SAMPLE_NATIVE_LAYOUT`.  No other control is selected or scored.

## Exact-context instrument

Reuse GDT280's fixed opportunity-plus-closure base, four edge blocks, all 16
subsets, host strings, held-folio splits, priors, prequential page history and
64 event permutations.  Replace only

```text
SHA256(context_tuple) mod 256
```

with the exact immutable context tuple itself as the categorical key.

This removes collisions but does not preserve equal occupied-context counts
across subsets.  The inherited hierarchical prior penalizes sparse contexts in
held prediction, but no separate model-key charge is introduced.  Therefore
exact-context absolute bits are a **sensitivity**, not a replacement for the
frozen GDT278 magnitude endpoint and not directly comparable to the 256-bucket
MDL magnitude.

For published representations, compute the same
`null mean minus observed bits/event` and exact four-player Shapley allocation
over 64 shared null worlds.  For LOFO-safe representations, relearn parser and
alphabet without the held folio and allocate observed
`BASE_NO_EDGE minus subset` bits/event.  Alternate readings remain
sensitivities of one manuscript, not samples.

## Frozen checks and decision

Three checks are predeclared:

1. every Latin native panel remains positively `RIGHT_FAMILY`-led;
2. Voynich native remains positively `OUTER_WRAPPER`-led;
3. constant Latin `DISPLAY_RENDERER=NONE` has exactly zero Shapley allocation
   (absolute tolerance `1e-10`) in the exact-context published analysis.

If all three pass under both published and LOFO-safe profile directions, report
`HASH_COLLISION_SENSITIVITY_PRESERVES_LATIN_RIGHT_VOYNICH_WRAPPER_SPLIT`.
Otherwise report `HASH_COLLISION_SENSITIVITY_CHANGES_EDGE_PROFILE`.

No tolerance is applied to the nonzero leaders; only sign and literal largest
block are used.  All component values and negative interactions remain public.

## Claim ceiling and f84 seal

This experiment can establish only whether a compression-profile distinction
is robust to hashed-context collisions.  It cannot establish abbreviation,
morphology, a q-prefix function, sound, language, code, notation, meaning,
plaintext, or translation.

Only the already-published f84-free event panel is allowed.  No f84 row may be
opened, parsed, retained, joined, or scored.
