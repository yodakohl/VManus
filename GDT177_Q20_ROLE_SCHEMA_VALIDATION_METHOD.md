# GDT177 — source-native validation of the frozen Q20 role-like schema

## Question

GDT176 projected three supported abstract classes from a readable medieval
recipe instrument: `INSTRUCTION_CLAUSE_LIKE`, `SHORT_ARGUMENT_LIKE`, and
`RECORD_CLOSER_LIKE`. GDT177 asks whether those classes predict Q20 structure
that the external classifier did not use.

This is exploratory schema validation, not semantic confirmation. The GDT176
projection is byte-frozen; no class is relabelled or refit.

## Frozen panel

Primary analysis uses the 1,483 ZL3b fields in the f84-free Q20 inventory.
IT2a and RF1b are reading sensitivities, not replications. The 39 ZL
`UNRESOLVED_EDGE_CLASS` fields are excluded from class contrasts but retained
in coverage accounting.

## T1 — independent closure signature

Restrict to the final field of each ZL record. Compare
`RECORD_CLOSER_LIKE` to the other supported classes on `ends_b3` and `ends_dy`.
The classifier used only relative position and field size, not B3/DY. Report
raw risk differences and an exact permutation diagnostic within physical
folio × final-field group-count bucket (`1`, `2`, `3`, `4+`).

Prediction: closer-like fields have a higher B3 rate and/or lower DY rate. A
mechanical position explanation remains a confound even on a positive result.

## T2 — cross-folio opaque-host recurrence

For every held folio, mark a first PAGE_HOST as recurrent when it occurs on at
least two other physical folios. Compare recurrence of
`SHORT_ARGUMENT_LIKE` and `INSTRUCTION_CLAUSE_LIKE` events. Report raw and
matched effects. The matched permutation strata are physical folio × record
scope × line-depth bucket (`0`, `1`, `2`, `3+`) × field-group-count bucket.

Prediction: reusable arguments show higher cross-folio host recurrence. This is
an opaque-slot prediction; it does not imply ingredients, nouns, or words.

## T3 — unused compiler complexity

From the already frozen `compiler_skeleton`, calculate per-field counts of
non-empty wrapper, O/OT frame, right-family, DY, and B3 states. Compare
instruction-like to short-argument-like fields at the same matched strata as
T2. The primary effect is non-empty compiler states per source group.

Prediction: clause-like fields have greater compiler-state density. Because
the parser and target use the same source groups, this is structural support,
not independent semantics.

## T4 — held-folio host placement

Use GDT176's fixed per-event role probabilities as the baseline. In each held
folio, estimate a Dirichlet-smoothed abstract-role distribution for each first
PAGE_HOST from all other folios. Combine four host pseudo-observations with the
fixed external probabilities. Report held-folio log-loss gain, top-class
accuracy, coverage, and per-folio signs. Host identities unseen outside the
held folio receive no host update.

Prediction: if PAGE_HOST is a stable role address, the host update improves
held-folio prediction. Failure weakens host-level role stability without
invalidating the coarse positional schema.

## Nulls and multiplicity

T1–T3 use 4,096 deterministic within-stratum permutations and inclusive tails.
Report local and max-three p-values across the primary T1-B3, T2-recurrence,
and T3-complexity effects. The permutation diagnostics quantify interest; in
YOLO discovery they do not automatically stop other hypotheses.

## Claim ceiling and seal

A positive result supports only a source-native record-schema association. It
cannot identify an ingredient, tool, operation, word, language, plaintext, or
translation. f84r is absent and must not be accessed.
