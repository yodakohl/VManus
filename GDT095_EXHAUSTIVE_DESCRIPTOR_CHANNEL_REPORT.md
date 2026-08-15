# GDT095 — exhaustive plant-description channel

## Outcome

**EXHAUSTIVE_DESCRIPTOR_CHANNEL_NO_SELECTOR_PAID_HPR2_REPRESENTATION_AFTER_ZERO_OVERLAP_CORRECTION**

This exploratory pass takes every one of the 19 frequency-eligible
normalized human-description tokens on the complete 83-locus strict
pharmaceutical plant-label panel.  It does not select `DARK_LEAF` or any other
attractive phrase. Exact-feature representations now use only neighbors with
positive overlap and otherwise back off to the held-folio prevalence code.
This correction removes a prior lexicographic zero-overlap tie artifact.

The best representation is HOST_WRAPPER_JOINT at only
+1.605 aggregate bits and on 2/5 folios; its selector-paid
gain is -1.717. No representation pays the
ten-way selection cost.

PAGE_HOST character trigrams alone score -47.257 bits and
WRAPPER alone scores -245.395. The exhaustive external
channel therefore does not localize positive information to PAGE_HOST, its
compiler marginals, or their exact conjunctions.

A disclosed post-hoc decomposition gives PAGE_HOST×WRAPPER
+3.230 bits on four location terms (`base`, `edge`,
`ground`, `level`) and -1.625 on the other fifteen
tokens. Neither rescues the aggregate channel. PAGE_HOST remains useful for
the narrow GDT089 lead, but the exhaustive vocabulary does not support it as a
general appearance-bearing layer. The split was inspected after vocabulary
exposure and is not confirmatory.
f84r was absent before the model and was not opened, retained, queried, joined,
scored, or targeted.
