# GDT211 — balneological record-schema bridge

## Question

Does anonymous q13 record organization exhibit the weak opening-versus-body
reuse asymmetry predicted by the independently frozen readable bath-record
schema in `gdt211_source_freeze.json`?

This is not a word-decoding test.  The target variables are exact source-native
formal PAGE_HOST IDs and complete source groups.  No PAGE_HOST receives a
semantic role or gloss.

## Chronology

Commit `4d62597` froze the external source audit, 33-item entry inventory,
role vocabulary, and two target predictions before this scorer was created or
run.  The q13 corpus was historically exposed by earlier experiments, so the
result is a prospective feature test on an exposed corpus, not a pristine
holdout.

## Target and guards

The target is every complete physical line on f75–f83 represented in both
`gdt046_line_frames.tsv` and `gdt062_right_family_inventory.tsv`.  The primary
scope is section B, Currier B, hand 2.  A seven-line section-T spillover is an
explicit sensitivity.  Source rows whose page begins `f84` are rejected before
retention; no f84r row is present, joined, displayed, or scored.

For each line the scorer retains only:

- page, physical folio, section, Currier, hand;
- editorial `paragraph_start`;
- source group count;
- first complete source token;
- its frozen HPR2 PAGE_HOST.

The HPR2 parser is not changed.  Paragraph starts are editorial layout
evidence, not authorial headings or semantic boundaries.

## Frozen statistics

For PAGE_HOST and, as a surface sensitivity, the complete first token:

1. mark an identity recurrent when it occurs on at least two physical folios
   in the scored scope;
2. compute the continuation-minus-paragraph-start recurrent fraction;
3. compute the analogous difference in mean `log2(scope frequency)`.

The primary direction is positive: paragraph starts should be less recurrent.
The two source-freeze predictions are the two verbal directions of this single
contrast and are not counted as independent successes.

## Exact nulls

The binary recurrence endpoint permits an exact combinatorial calculation.
Within each stratum, the observed number of paragraph starts is reassigned over
the observed lines and the hypergeometric distributions are convolved.  Three
nested nulls are reported:

1. physical page only;
2. physical page plus source-group-count bucket (`1–4`, `5–7`, `8–10`, `11+`);
3. physical page plus exact source-group count.

The third is primary because opening and continuation lines differ in length.
Its opportunity count and swappable-line capacity are reported.  No threshold
was tuned after seeing the result.

## Generic-opening controls

The same statistics are run on Currier-B/hand-2 Herbal lines and on the small
Currier-B/hand-2 T/C pool.  These are not genre-matched replications.  They test
whether any q13 lead is merely a generic paragraph-opening effect.

## Decision

- `BALNEOLOGICAL_RECORD_SCHEMA_SPECIFIC_LEAD` requires a positive PAGE_HOST
  effect, exact-count null `p <= .05`, and an effect exceeding Herbal-B/hand-2
  by at least 0.10.
- `BALNEOLOGICAL_RECORD_SCHEMA_COMPATIBLE_BUT_GENERIC_LINE_OPENING_CONFOUND`
  applies when the predicted direction appears but either the strict null or
  specificity gate fails.
- otherwise `BALNEOLOGICAL_RECORD_SCHEMA_NOT_SUPPORTED`.

## Claim ceiling

The result can assess only compatibility of anonymous record architecture with
a readable bath-entry schema.  It cannot identify an identity field, bath,
disease, body part, action, word, morpheme, sound, language, plaintext, or
translation, and it cannot by itself confirm or reject the image-level
therapeutic-bath theory.
