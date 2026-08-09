# `cho/che` paragraph-scope one-time target test

Status before execution: **REGISTERED_SINGLE_RUN**

## Authorization and frozen inputs

This target is authorized only by the unchanged scientific contract in
`CHO_CHE_SCOPE_SYNTHETIC_PREFLIGHT_SPEC.md`, the arithmetic-only v2 amendment,
and the independently reconstructed v2 preflight.

- `results/cho_che_scope_masked_events.tsv`, SHA-256
  `41f8b517419d2215a97db9ce245c5639f383b11c41d8c1377a245dea8e37abf3`
- `results/cho_che_scope_masked_universe_validation.json`, SHA-256
  `e7d37a23ca199e421946fab0c42f4547aade0a5fa27579b1e9e69518c0d376ec`
- `cho_che_scope_core.py`, SHA-256
  `b77dd67d49c4e173d16bce2409c8f691e9cf7aae30b1333ee0eeffd9a98193b8`
- `CHO_CHE_SCOPE_SYNTHETIC_PREFLIGHT_SPEC.md`, SHA-256
  `b2b51a91b999ae926170a76ce8ffe8f5b8a7d01f3e71200e93b26cefce900c94`
- `CHO_CHE_SCOPE_SYNTHETIC_PREFLIGHT_V2_AMENDMENT.md`, SHA-256
  `36c4bd9817a9583bc786b50a952b65b3d15caacd7077ccaca481ad28cf96ffc0`
- `results/cho_che_scope_synthetic_preflight_v2.json`, SHA-256
  `3748e03fb9217e7c7d389b887611407fc323a8b5526e7a369ac94f90aae5062e`
- `results/cho_che_scope_synthetic_preflight_v2_validation.json`, SHA-256
  `cc1a92ae052cf3b1e880732713c4b00362173f49ddfdfa177b45ddc28ce1de35`
- `results/source_sta_group_alignment.tsv`, SHA-256
  `f23654f1d4c854db6d458b418a0d3530115731604854cf0a0495565e58341840`
- `results/source_sta_group_alignment_validation.json`, SHA-256
  `cc53d32646b21e4135f0b23d98662e10835307ad860d021ea8c487261d7646fd`

The result and report must be absent before invocation and are installed with
no-clobber semantics. NumPy and BLAS thread counts are pinned to one before
import. The three readings are scored in three forked workers.

## Single target join

Join every one of the 30,160 frozen masked events to the source-alignment row
by exact `source_group_id`. Require the alignment row to have zero alternative
sites, a lowercase basic-EVA projection, and exactly one `ch/sh+o/e` site.
Replace that site's final character by `X` and require exact equality to the
frozen masked template. Encode `o=1`, `e=0`. Store only reading-level outcome
counts and cross-reading agreement diagnostics, never event-level outcomes or
unmasked surfaces.

Score each reading with exactly the frozen `LOCAL_T`, `BOUNDARY_T`, hierarchy,
two corrected rotation ensembles, gates, and concentration/deletion rules.
Use assignments 1 through 8,191, plus-one p-values, seed domain
`CHO_CHE_SCOPE_TARGET`, and no alternative analysis.

## Decision

- If `LOCAL_PASS` and `BOUNDARY_PASS`: retain a marked-span-aligned local
  persistence effect plus a distance-controlled association with the ZL
  editorial paragraph boundaries.
- If only `LOCAL_PASS`: retain marked-span-aligned local persistence, with
  boundary specificity unconfirmed.
- Otherwise: frozen local-scope nonconfirmation, regardless of the boundary
  diagnostic.

No rerun, threshold change, position-bin change, reading selection, template
subset, page-state selection, or post-hoc rescue is permitted.

The maximum claim is formal construction-site scope. Neither result makes the
ZL marks authorial or identifies a vowel, consonant, sound, word, language,
cipher operation, topic, meaning, plaintext, or translation.
