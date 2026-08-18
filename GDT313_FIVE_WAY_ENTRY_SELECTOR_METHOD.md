# GDT313 — five-way entry-state selector

## Frozen question

GDT311 transfers binary source/target choice, and GDT312 compresses the common
`s` target into a line-entry rule.  Do `s` and `q` occupy distinct external
entry regimes when compared inside the *same* opaque host/renderer opportunity?

Intersect the frozen GDT303 `ch->s`, `d->s`, and `NONE->q` exact cells by
opaque PAGE_HOST plus every non-wrapper renderer coordinate.  Exactly two
cells survive (`l` and `or`); each has all five exact choices
`{NONE,ch,d,s,q}`.  Use every occurrence of those ten surfaces once.  Reuse
the deterministic GDT311 folio split.  The frozen panel has 273 training and
203 test events.

Fit ridge-10 multinomial models:

1. exact-cell prior;
2. cell plus physical line start;
3. cell plus preceding physical-group DY;
4. cell plus both entry coordinates.

Predictions are learned on training folios only.  The primary exact held null
permutes five-way labels inside `cell × register` on the test folios for 8,192
worlds and max-three correction.

Call `FIVE_WAY_ENTRY_STATE_SELECTOR_TRANSFERS` only if the two-coordinate
model has positive raw and null-centered held log-loss gain, max-three p at
most .05, the training coefficient and held cell/register-matched delta for
`s × LINE_START` are positive, and the corresponding `q × PREV_DY` values are
positive.

## Claim ceiling

At most this establishes a stochastic formal selector among five known exact
surface choices in two opaque cells.  It does not predict another cell or
identify a morpheme, category, meaning, sound, language, plaintext, or
translation.  No f84 row may be opened, parsed, retained, joined, or scored.
