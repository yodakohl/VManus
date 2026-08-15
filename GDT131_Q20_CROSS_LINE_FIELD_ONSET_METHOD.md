# GDT131 — Q20 cross-line field-onset transfer

Status: `EXPLORATORY_YOLO_FIXED_FOUR_MODEL_FAMILY`

## Question

GDT114–GDT117 established a transferable relation between the compiler
profile of a star record's first physical line (`OPEN`) and the aggregate
compiler profile of its later lines (`BODY`).  GDT118 did not localize that
relation cleanly to the whole first BODY line.  This experiment asks a more
discrete question: does the **final field of OPEN** predict the
onset and closure architecture of the **first field of BODY line 1**, beyond
the aggregate OPEN compiler profile?

OPEN and BODY are human-catalogued physical record positions, not headings or
recipes.  A field is a source-native sequence ending at DY, with the remaining
line-final sequence retained as an open field.

## Frozen panel and target

Reuse the 170 Q20 records on eight physical folios and the complete field atlas
published by GDT127.  ZL3b is primary; IT2a and RF1b are alternate readings of
the same object.  The first-BODY-field target is a 22-cell factored vector:

- first group wrapper (including `NONE`);
- first group O/OT frame (including `NONE`);
- first group RIGHT-family presence, inner-D, DY and B3 states;
- field group-count bin `1/2/3/4+`;
- closure state `DY/B3/OPEN`.

This is a discrete construction fingerprint.  It is not a semantic class.
Exact full first-field surface and exact compiler-template prediction are
retained as sparse diagnostics, not promoted to the primary endpoint: 168/170
ZL surfaces and 150/170 ZL templates are distinct.

## Held-folio models

Hold out one physical folio at a time.  The adversarial nuisance baseline sees
record extent/OPEN length, page side and record ordinal, and the final OPEN
field's group count plus total PAGE_HOST and raw character lengths.  It sees no
target architecture from the held folio.
The fixed reference model additionally sees the aggregate 12-cell OPEN
compiler profile.  Four additions are compared against that reference:

1. `LAST_COMPILER12` — final-OPEN-field compiler rates plus field length;
2. `LAST_ORDERED_CELL_HASH32` — ordered compiler-cell bigrams;
3. `LAST_HOST_CHAR3_HASH32` — PAGE_HOST character trigrams;
4. `LAST_RAW_CHAR3_HASH32` — complete source-group character trigrams.

All hashes are SHA-256 modulo 32.  Ridge 1000 is inherited from GDT116 and is
not tuned.  Pseudo-bits are reductions in standardized Gaussian squared error,
consistent with GDT114–GDT125.  Exact architecture top-1/top-3 predictions are
training-only nearest prototype diagnostics.

## Control and decision

Use 4,096 shared worlds per reading.  Within each held page and exact
OPEN-member-count stratum, permute only the added final-field representation;
the target, nuisance, aggregate OPEN profile, page ecology and lengths remain
fixed in the regression.  Report local and max-four p-values.  This is a
model-adjusted coarse-stratum diagnostic, not an exact conditional
final-field-length permutation: only 33 ZL records remain swappable after also
matching final-field group count, four after PAGE_HOST character length, and
two after raw character length.  The corresponding RF counts are 29, zero and
zero.  The current panel cannot supply a powered exact opportunity-matched
permutation.

A supported cross-line field rule requires positive selector-paid gain,
positive gain on at least six of eight ZL folios, positive gain in all three
readings, max-four p at most .05, and performance above both string controls.
Otherwise retain any directional lead as exploratory and report its fold,
reading, sparsity and baseline dependence.

The exact formula endpoint is expected to be harsh.  Failure there rejects a
simple codeword-to-codeword dictionary only; it does not erase the aggregate
GDT115/GDT117 compiler linkage.

f84r is rejected by literal page/locus guard before records are retained.  It
is not opened, queried, joined, scored, targeted, or assigned a prediction.
No heading, recipe, role, gloss, word, morpheme, POS, sound, language,
plaintext, meaning, or translation is assigned.
