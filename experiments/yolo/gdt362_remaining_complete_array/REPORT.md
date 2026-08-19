# GDT362 remaining complete-array report

Status: **FROZEN_DIRECTION_CONTRADICTED**.

## Outcome

The exhaustive remaining complete array in the current human-source census did
not reproduce the GDT360/GDT361 first-group `AQ`/CONTACT direction.

| visual state | AQ | non-AQ | total |
|---|---:|---:|---:|
| CONTACT | 0 | 3 | 3 |
| CLEAR_GAP | 1 | 4 | 5 |
| UNCERTAIN | 0 | 1 | 1 |

The frozen statistic is CONTACT AQ prevalence minus CLEAR_GAP AQ prevalence:

`0/3 - 1/5 = -0.20`.

The exact one-sided within-array permutation tail is `56/56 = 1.0`. The sole
AQ row is `f101v2.10` / canonical formal locus `f101v.10`, and it was called
CLEAR_GAP before its family `AQAB` was exposed. The three CONTACT rows begin
`ACACAB`, `BAQABB`, and `BABACA`; the internal `AQ` in `BAQABB` does not satisfy
the frozen first-group-prefix predicate.

## Chronology and correction

The nine-locus unit and AQ direction were frozen in commit `f5c8a1e` before
target image review or formal query. The first image check showed that f101v is
a two-canvas foldout, not a complete single canvas. That source-layout defect
was disclosed and corrected in commit `c3eb43b` before the continuation canvas
was displayed. The complete visual calls—3 CONTACT, 5 CLEAR_GAP, and one
fold-damage UNCERTAIN—were then frozen and published in commit `90a69bc` before
any target family was queried.

The visual atlas uses the legacy physical-page locus names `f101v2.10-.18`;
the current source-native tables use `f101v.10-.18`. The published human
crosswalk verifies that alias. Seven rows have exact family consensus. `.13`
and `.14` lack exact full-family consensus because their readings/segmentation
differ, but the first-group AQ predicate is non-AQ in all three readings, so no
row is dropped from the frozen test. The predicate is reading-stable on all
nine rows; `AQ` and `AQA` have identical masks on this panel.

## What this changes

GDT360 selected AQ after a broad existing-annotation search. GDT361 supplied a
directionally positive but very weak new-folio result (`1/3` CONTACT versus
`0/2` GAP; exact `p=.60`). GDT362 was the last complete unused-folio array
available under the source-only census and reverses that direction. Combining
all three descriptively still gives `6/14` CONTACT versus `3/25` GAP, but that
aggregate is dominated by the postselected GDT360 discovery panel and is not a
prospective confirmation.

The current AQ/contact acquisition route is therefore closed. No alternative
prefix, substring, family, visual recoding, or exclusion was searched after
the contradiction. Reopening would require genuinely new provenance-clean
arrays and a separately frozen question, not another selection from this
exposed panel.

## Limitations

- The visual calls come from one AI direct observer; no independent human or
  second blind review is claimed.
- `.13` remains UNCERTAIN because the label lies at the damaged fold and across
  two photographs.
- CONTACT is literal visible stroke contact, not ownership or semantics.
- ZL3b, IT2a, and RF1b are alternate readings of one manuscript, not three
  replications.

## Claim ceiling

GDT362 establishes only that the frozen AQ/contact direction failed on this
complete held visual array. It does not invalidate AQ as a formal family and
does not assign contact, plant, object, word, morpheme, part of speech, sound,
language, plaintext, meaning, or translation. No f84 material was accessed.
