# GDT226 — manuscript-wide specificity freeze for the recipe-role scaffold

## Question

GDT224 found that q13's aggregate field-position/length profile is unusually
close to the role distribution learned from readable medieval recipes, but it
compared q13 only with same-hand Herbal-B.  GDT226 asks whether that likeness
is specific to plausible practical/record registers or is a generic property
of Voynich line and paragraph lengths.

The GDT176 `POSITION_LENGTH` instrument is reused unchanged.  It sees only
relative field position, squared position, log field span, and log record
field count.  Fields remain the frozen DY-or-line-end units, and records begin
only at page or editor-marked paragraph starts.  No surface token, PAGE_HOST,
wrapper, family, or visual feature enters the model.

## Frozen scopes

All complete lines in `gdt046_line_frames.tsv` are assigned mechanically:

* `HERBAL_A` = register `HA`;
* `HERBAL_B` = register `HB`;
* `STARS_B` = register `SB`;
* `OTHER_A` = register `OA`;
* `Q13` = register `OB` on pages f75 through f83;
* `OTHER_B` = the remaining register-`OB` pages.

Every page beginning `f84` is rejected before retention.  The earlier limited
public-metadata exposure is disclosed in the active registry; no f84 source or
formal payload is used here.

## Frozen predictions and controls

The following directions are frozen before the six-scope projection is run:

1. q13 has lower Jensen-Shannon divergence from the readable-recipe projected
   role distribution than both Herbal-A and Herbal-B;
2. q13 ranks in the two closest of the six scopes;
3. `STARS_B`, the independently record-rich Recipe/Stars register, is the
   closest other Voynich scope to q13 in projected role-distribution space.

Prediction 1 partly contains the already exposed GDT224 q13-versus-Herbal-B
comparison; its q13-versus-Herbal-A half and the six-scope rank are new.  The
published GDT176 Stars projection informs prediction 3, so this is a frozen
specificity synthesis rather than pristine confirmation.

Report record- and field-weighted distributions, exact-record-size matched
contrasts where capacity exists, physical-folio deletion, and all pairwise
scope distances.  A role distribution is a structural scaffold, not a recipe
identification.

## Decision ceiling

All three directions and at least eight of nine q13 physical-folio deletions
must hold for `Q13_RECIPE_ROLE_SPECIFICITY_PROVISIONAL`.  Otherwise use
`Q13_RECIPE_ROLE_LIKENESS_GENERIC_OR_UNSTABLE`.

Even a pass establishes only that q13 resembles a practical-record role
architecture at coarse position/length resolution.  It assigns no field an
ingredient, tool, action, object, word, language, plaintext, or translation.
