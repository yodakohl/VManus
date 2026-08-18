# GDT305 — prospective low-support field-entry transfer

## Purpose and chronology

GDT304 froze four formal predictions after a disclosed post-hoc endpoint
decomposition.  GDT305 tests those predictions on exact forms whose positional
outcomes were not scored by GDT303 or GDT304.

Pair selection is score-blind.  The freezer may read only form identity,
`PAGE_HOST`, the six renderer fields, event support, physical folio, and line
group count.  It must not read group position, HPR2 field position, record
ordinal, or any close flag.  The frozen pair table is committed before the
scorer is run.

This is prospective relative to GDT303/GDT304, but not pristine manuscript
evidence: the source corpus and parser existed before the prediction, and the
minimum-support threshold was chosen after a score-blind capacity audit.

## Frozen panel

Eligible observations are f84-free `VOYNICH_REFERENCE` events on physical
lines with at least two groups.  A candidate pair must:

1. have the same exact `PAGE_HOST`;
2. differ in exactly one of `wrapper`, `local_frame`, `inner_d`,
   `right_family`, `dy_closure`, and `b3`;
3. instantiate exactly one frozen direction: `NONE->q`, `ch->s`, or `d->s`
   in `wrapper`;
4. give each exact surface at least two events on at least two physical
   folios; and
5. use two exact surfaces absent from every published GDT303 pair row.

All qualifying pairs are retained.  No position-derived filtering is allowed.

## Frozen endpoints and decisions

For each exact form, compute event proportions for:

- HPR2 `FIELD_FIRST` and `FIELD_LAST`;
- physical `LINE_FIRST` and `LINE_LAST` as parser-independent anchors;
- `RECORD_ORDINAL_1`.

Compute target-minus-source deltas, average multiple pairs equally within an
opaque host, then average hosts equally within an operation.

The four predictions are evaluated literally:

- P1 passes iff `NONE->q` has positive mean `FIELD_FIRST` and negative mean
  `FIELD_LAST`;
- P2 passes iff `ch->s` has positive mean `FIELD_FIRST`;
- P3 passes iff `d->s` has positive mean `FIELD_FIRST`;
- P4 passes iff the absolute mean `RECORD_ORDINAL_1` delta is below 0.10 for
  all three operations.

Operation-local directional sign-flip p-values are diagnostics, not gates.
The two-host `ch->s` panel has descriptive capacity only.  Classify the joint
result as `ALL_FROZEN_DIRECTIONS_TRANSFER`, `MIXED_FROZEN_DIRECTIONS`, or
`FROZEN_DIRECTIONS_FAIL` from the four Boolean predictions without repair.

## Claim ceiling

At most this supports a probabilistic formal field-entry renderer on rare but
cross-folio exact forms.  It does not establish a linguistic morpheme,
grammatical category, part of speech, discourse meaning, sound, language,
plaintext, or translation.  No f84 row may be opened, parsed, retained,
joined, or scored.
