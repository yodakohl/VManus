# GDT111 — DY/PAGE_HOST transition test

## Question

Does a within-line DY boundary separate a transferable PAGE_HOST slot, and do
the PAGE_HOSTs on the two sides form a predictive transition beyond the
post-boundary host alone?

This is source-only formal inference. It does not assign a function or meaning
to DY or any host.

## Population

Use every source-index-consecutive within-line group boundary in the
15,592-group, f84r-free GDT062 HPR2 inventory. Some physical lines contain a
group excluded from the strict source panel; no boundary is bridged across
such a gap. The binary target is whether the preceding group carries DY
closure. Line-final groups have no boundary and are absent.
Leave one complete physical folio out for every prediction.

## Models

All models contain the same low-capacity nuisance features: register, boundary
position quartile, line-length bucket, and active previous/next compiler state
excluding DY itself. Compare:

1. nuisance only;
2. next raw-form character trigrams;
3. next PAGE_HOST character trigrams;
4. previous PAGE_HOST character trigrams;
5. next compiler state only;
6. next plus previous PAGE_HOST trigrams;
7. next PAGE_HOST plus ordered previous-final→next-final edge pair;
8. next plus previous PAGE_HOST and the edge pair;
9. next PAGE_HOST final character only;
10. previous PAGE_HOST final character only.

The multinomial naive-Bayes classifier uses fixed additive smoothing 32. All
ten tried models are retained. Report held codelength, average precision,
positive/negative-class savings, physical-folio directions, and register
contributions.

The key comparisons are:

- next PAGE_HOST versus nuisance: post-DY slot separation;
- next PAGE_HOST versus next raw string: HPR2 abstraction value;
- previous PAGE_HOST versus nuisance: host-specific DY licensing;
- next+previous PAGE_HOST versus previous PAGE_HOST: post-slot value after
  controlling that licensing;
- full edge-pair model versus additive next+previous PAGE_HOST: ordered
  boundary interaction.

A large previous-host effect by itself is only renderer licensing. A positive
next-host increment after that control supports a post-DY slot; an additional
ordered edge-pair increment supports a transition interaction.

## Existing-result boundary

GDT020 already established that a coarse record-state projection changes after
DY. GDT111 does not count that as new evidence; it asks whether the finer HPR2
PAGE_HOST representation generalizes and whether ordered pre/post dependence
survives.

## Holdout and claim ceiling

f84r is absent from the source inventory and is not opened, parsed, retained,
queried, joined, scored, or targeted. No semantic role, gloss, word, morpheme,
POS, sound, language, plaintext, meaning, or translation is assigned.
