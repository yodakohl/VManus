# GDT197 — global competition among the perfect f57/f77 decoders

## Question

GDT182 showed that three different shallow predicate pairs perfectly partition
the exposed four labels in the f57 N1 register.  GDT179/GDT180 selected
terminal `y` plus initial `ot`, but the local fit did not distinguish that pair
from terminal `y` plus `al`, or `al` plus initial `ot`.

GDT197 asks whether the selected pair is privileged by manuscript-wide record
ordering.  A genuine reusable state coordinate should organize unseen physical
line sequences at least as well as the alternative predicates that happened to
fit the same four labels.

This is a formal decoder competition.  The display names HOT/MOIST/COLD/DRY
are not used in scoring and are not propagated to prose.

## Frozen candidate family

Exactly the three complete N1 mask pairs in `gdt182_decoder_pairs.tsv` are
tested:

1. `AL_Y`: contains `al` × terminal `y`;
2. `AL_OT`: contains `al` × starts `ot`;
3. `Y_OT`: terminal `y` × starts `ot` — the GDT179/GDT180 selection.

Each pair maps every retained source group to one of four anonymous bit states.
No substring, threshold, orientation, or alternate decoder is added.

## Corpus and holdout

Use the frozen HPR2 inventory only to obtain physical locus, folio, section,
group order, group count, and display surface.  Reject every `f84*` row before
retention.  Keep only complete strict all-reading-stable physical lines, so
adjacency is never manufactured across missing groups.

For each candidate, train a Dirichlet-1/2 four-state unigram and line-reset
first-order Markov model while holding out one complete physical folio.  Score
the held lines and sum over folds.  The primary statistic is held
`UNIGRAM_BITS - MARKOV_BITS`.

## Order null and selection control

Generate 4,096 deterministic worlds that independently permute the group order
inside every retained physical line while preserving every line's state
multiset and length.  The held-folio models remain trained on true training
order.  Report:

- local inclusive tail for each candidate;
- standardized observed order z;
- max-three tail across the complete frozen decoder family;
- section contributions and leave-one-folio contributions.

The selected `Y_OT` decoder wins only if it has the largest observed z, its
max-three p is at most .05, and its held gain is positive after every folio
deletion.  Otherwise its global sequence behavior does not disambiguate the
local semantic scaffold.

## Claim ceiling

A win would support only a reusable anonymous two-bit record coordinate.  A
loss weakens the selected `ot` axis but does not invalidate HPR2, terminal `y`
as a formal feature, or a page-local f57/f77 description.  No bit is a quality,
word, morpheme, sound, language, plaintext, meaning, or translation.  `f84r`
and all other `f84*` rows are excluded before retention and scoring.
