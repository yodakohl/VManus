# GDT117 — Q20 same-page OPEN/BODY retrieval

Status: `INHERITED_GDT115_PREDICTIVE_RETRIEVAL`

Turn the GDT115 compiler-channel effect into a concrete held-folio task.  For
each BODY on an unseen physical folio, rank all OPENs on the same page with the
same exact source-member count.  The correct OPEN is hidden among those
candidates.  Singleton strata are reported but cannot test retrieval.

Fit on the other seven folios with ridge 1000 inherited from GDT115.  The BODY
target is the anonymous HPR2 compiler-rate vector.  The nuisance prediction
already sees record shape and the leave-one-record-out mean BODY profile of the
other records on the held folio.  Compare four OPEN representations:

- `WRAPPER7`;
- `COMPILER12` (wrapper + O/OT frame + RIGHT/DY/B3);
- `EDGE29`;
- `RAW_CHAR3_HASH32`.

For each candidate OPEN, generate its BODY prediction and rank by squared
error.  Report top-1 accuracy, mean reciprocal rank and pairwise accuracy.
Use 4,096 one-to-one permutations within the same candidate strata and max-four
correction.  ZL3b is primary; IT2a/RF1b are alternate-reading sensitivities.

This is formal record linkage only.  OPEN/BODY are physical positions, not a
heading and recipe.  f84r is excluded before formal retention and receives no
query or prediction.  No role, word, morpheme, POS, sound, language, plaintext,
meaning, or translation is assigned.
