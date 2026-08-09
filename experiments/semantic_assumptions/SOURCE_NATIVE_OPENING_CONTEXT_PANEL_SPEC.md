# Source-native `NONE` versus `DA` context panel

Status: **FROZEN_TARGET_MASKED_PANEL**

The score-blind opening-operation audit selected `NONE__DA`. This builder shall
retain only the 53 exact family remainders for which both states occur on at
least two physical folios. It may derive operation assignments solely to select
rows and produce label quotas; it must not attach an operation label to any
stored row or compute an operation-to-context association.

For each retained group, store an anonymous unit ID, anonymous exact-remainder
ID, physical folio, section, Currier, editorial kind, exact group count, and
exclusive locus role `SINGLE/FIRST/MIDDLE/LAST`. Store immediate external
context only as:

- left: `START`, the last family of the exactly adjacent strict group, or
  `AMBIGUOUS` if that source group is not strict;
- right: `END`, the first family of the exactly adjacent strict group, or
  `AMBIGUOUS` if that source group is not strict.

A separate quota table may store only `(anonymous remainder, folio,
NONE_count, DA_count)`. It may not identify which rows carry either state.
Report row/base/folio counts, label totals, mixed-quota strata and movable rows,
context categories, and per-register capacity. Stop before calibration if fewer
than 500 rows, 40 remainders, 50 folios, 20 mixed quota strata, or 200 movable
rows remain.

This panel authorizes target-free synthetic calibration only. It contains no
English gloss and cannot establish detachment, wordhood, prefix function,
syntax, sound, language, cipher operation, meaning, plaintext, or translation.
