# GDT182 — f57 decoder multiplicity report

Status: **LOCAL_F57_DECODER_DESCRIPTIVE_NOT_ABOVE_FEATURE_MULTIPLICITY**.

## Outcome

The f57 two-register decoder remains an elegant local description, but its
perfect 8/8 fit is not confirmation-like once the available shallow feature
search is counted.

Across predicates that are literal and stable through every expansion of all
three alternate readings:

| register | stable predicates | effective masks | complete 2×2 mask pairs |
|---|---:|---:|---:|
| N1 | 57 | 10 | 3 |
| D1 | 42 | 9 | 2 |

The GDT179 choices are genuine complete decoder pairs:

- N1: `START2:ot` (`1001`) plus `END1:y` (`0101`);
- D1: `HAS2:ok` (`0110`) plus `END1:y` (`0101`).

But they are not the only complete pairs.  N1 can also be partitioned by the
`al/dal` mask, and D1 can be partitioned by an `r/ar` mask.  A complete grid is
therefore partly a consequence of searching flexible predicates on four
exposed labels.

## Shared-axis result

Seven literal predicate names are nonconstant in both registers.  Only the
two aliases `END1:y` and `HAS1:y` have the same four-position mask (`0101`) in
both.

That is the attractive part of GDT179: terminal `y` really is the sole simple
literal shared axis under this feature family.  It is nevertheless weak after
selection.  Permuting the four D1 labels over the four fixed positions gives:

| diagnostic | matching worlds / 24 | exact tail |
|---|---:|---:|
| any searched common literal obtains the same mask | 10 / 24 | 0.4167 |
| `END1:y` specifically obtains the same mask | 4 / 24 | 0.1667 |

The first row is the honest search-adjusted diagnostic because `y` was chosen
after the registers were exposed.  The second is descriptive only.  Neither
supports a confirmed semantic coordinate.

## Consequence for the translation theory

This does not show that the W.73 phase or the f57 four-quality interpretation
is false.  The visual-historical scaffold still organizes the page, and the
register-conditioned coordinates remain an economical way to write it down.
What changes is evidential force:

- the labels are not decoded words;
- terminal `y` is not established as a quality morpheme;
- `starts-ot` and `contains-ok` are not established as Fire/Water operators;
- the f77 5/5 relation fit inherits an exposed state assignment and is not an
  independent semantic replication.

Accordingly, GDT181 remains the leading **generative** hybrid-compiler theory,
but its local f57/f77 semantic fragment must be called a descriptive candidate
rather than a provisional translation result.

## What remains useful

The audit sharpens the next target.  A fresh same-system diagram must be
predicted before its strings are inspected.  Merely finding another perfect
2×2 partition after seeing four labels is insufficient.  The decisive evidence
would be transfer of a frozen predicate and register reference, or a readable
homolog that fixes the values independently.

No new target, image-derived state, prose string, or f84r material was used.
