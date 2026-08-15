# GDT121 — Q20 OPEN prediction of BODY extent

Status: `EXPLORATORY_YOLO_FIXED_MODEL_FAMILY`

## Question

GDT115 localizes a transferable OPEN-to-BODY compiler-profile channel, but its
nuisance baseline was already told the BODY line/group/member counts.  GDT121
asks whether the OPEN also predicts that structural extent on an unseen
physical folio.

The five BODY targets are line count, group count, source-member count, groups
per line, and members per group.  They are record-shape measurements, not
numbers encoded by individual signs and not semantic quantities.

## Held-folio design

Reuse the 170 clean Q20 records on eight physical folios and hold out one
physical folio at a time.  The adversarial nuisance baseline knows page side,
within-page record ordinal, records on page, OPEN group/member counts, and the
leave-one-record-out mean BODY extent of the other records on that page.

At fixed ridge 1000 compare five OPEN additions:

1. wrapper proportions (`OPEN_WRAPPER7`);
2. full compiler proportions (`OPEN_COMPILER12`);
3. PAGE_HOST edge/length profile (`OPEN_EDGE29`);
4. raw OPEN character trigrams in 32 fixed SHA bins;
5. PAGE_HOST-only character trigrams in the same bins.

Score held standardized squared-error reduction as Gaussian pseudo-bits.  In
each held folio, permute complete OPEN feature vectors within page and exact
OPEN-member-count strata.  BODY, nuisance, record shapes, and the OPEN multiset
remain fixed.  Use 4,096 shared worlds and max-five correction.

ZL3b is primary; IT2a/RF1b are alternate-reading sensitivities, not independent
samples.  A useful lead requires positive selector-paid compiler gain, max-five
p at most .05, at least six of eight positive folios, positive direction in all
readings, and compiler gain above both string controls.

f84r is excluded before retention and is not opened, queried, joined, scored,
targeted, assigned, or predicted.  No number value, heading, recipe, semantic
role, word, morpheme, POS, sound, language, plaintext, meaning, or translation
is inferred.
