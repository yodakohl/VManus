# GDT224 — readable-recipe role instrument transfer to q13

## Question

Does q13 record architecture look more like the coarse role organization of
real medieval recipes than same-hand Herbal-B records do, when the external
instrument is frozen and no Voynich source identity is used?

GDT176 learned a five-class position/length classifier on 22,394 editor-tagged
units from 1,136 recipes in six held collections.  Its externally selected
`POSITION_LENGTH` model recovered OPERATION and INGREDIENT strongly, CLOSER
partially, and failed to separate TOOL or OPENER.  GDT224 reuses that model
unchanged.  Exported labels are therefore restricted to:

- `INSTRUCTION_CLAUSE_LIKE` from OPERATION;
- `SHORT_ARGUMENT_LIKE` from INGREDIENT or TOOL;
- `RECORD_CLOSER_LIKE` from CLOSER; and
- `UNRESOLVED_EDGE_CLASS` from OPENER.

These are structural role likenesses, not Voynich semantics.

## Frozen target and control

The q13 target is every complete line on f75–f83 with register `OB`, hand 2:
240 lines, 18 pages, nine physical folios.  The control is every complete
Herbal-B/hand-2 line in the same frozen line frame: 61 lines, 19 pages, ten
folios.  All f84 pages are rejected before retention.

A mechanical record begins at the first available line on each page and at
every later line marked `paragraph_start`.  This gives 33 q13 and 22 Herbal-B
records.  Paragraph marks are editorial layout evidence, not semantic
headings.  Within each physical line, a field ends after any group with the
frozen GDT016 `dy_closure=1`; the line end closes the remaining field.  Fields
never cross lines.  The CoReMA feature vector is exactly relative field
position, squared position, `log2(1+field group count)`, and
`log2(1+record field count)`.

The model is refit only on the already public GDT176 external role units using
the published deterministic optimizer.  q13 and Herbal rows affect neither
features, coefficients, scaling, nor class definitions.

## Frozen comparisons

Before q13 field roles are generated, three directional diagnostics are fixed:

1. q13 should have a higher folio-balanced fraction of records containing both
   an instruction-clause-like and a short-argument-like field than Herbal-B;
2. q13 should have a higher folio-balanced final-field closer-like rate;
3. q13's aggregate projected four-class distribution should have lower
   Jensen–Shannon divergence from the externally predicted CoReMA distribution
   than Herbal-B's.

Each difference is also reported only within exact record-field-count strata
shared by target and control, with record weights inverse to stratum size.
Whole-folio leave-one-out direction and 4,096 fixed section-label permutations
provide diagnostics; the two registers are not exchangeable biological
replicates, so p-values remain exploratory.  No host identity, token character,
wrapper, family, drawing, or visual annotation enters the classifier.

## Decision

`Q13_RECIPE_ROLE_ARCHITECTURE_PROVISIONAL` requires all three raw directions,
at least two of three exact-size-controlled directions, and at least eight of
nine q13 leave-one-folio aggregate directions.  Otherwise the result is
`Q13_RECIPE_ROLE_ARCHITECTURE_WEAK_OR_GENERIC` or
`Q13_RECIPE_ROLE_ARCHITECTURE_NOT_SUPPORTED`.

## Claim ceiling

At most this may identify a coarse q13 procedure/argument/closer-like record
scaffold learned from readable recipes.  It cannot distinguish an ingredient
from a tool, identify a specific action or object, assign a source group to a
role, or establish a word, language, plaintext, or translation.  No f84
artifact is accessed.
