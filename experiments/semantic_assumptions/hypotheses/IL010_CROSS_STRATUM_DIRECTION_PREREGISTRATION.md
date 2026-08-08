# IL010 — cross-stratum direction-specific adjacency increment

Registered: 2026-08-06, after IL009 confirmed cross-stratum aggregate adjacency
on all three axes and after one disclosed bucket-2 training-only feasibility
run, but before any bucket-1 or bucket-0 directional-increment score.

## Question and distinct invariant

IL009's source-excluded adjacency tables retain physical `DC` and `CD`
orientations, but an orientation-aware table can succeed merely because the
same unordered D-C pairs recur on both sides. IL010 asks whether orientation-
specific pair affinities add held information beyond an otherwise identical
pair table pooled across `DC` and `CD`.

The three frozen axes remain `CURRIER`, `SECTION`, and `HAND`. Every source
model excludes all training pages sharing the target page's value on that
axis. No exact root pair or axis subset is selected.

Archived line-order, exact-transition, and substitution-class reports establish
ordering elsewhere, but do not test this cross-stratum orientation increment
under IL006's exact page/form/position/entry null.

## Models and score

- Manual ZL3b is primary; IT2a/RF1b are alternate readings only.
- Roots, D/C split, page buckets, physical edges, metadata, smoothing constants,
  and eligibility are inherited unchanged from IL006/IL009.
- The oriented model is the source-excluded IL009/IL006 table with separate
  `DC` and `CD` conditionals.
- The collapsed model pools D-C pair counts across `DC` and `CD`, while keeping
  the same orientation-specific C-root marginal. Thus it retains unordered
  pair affinity and root-side propensity but removes pair-specific orientation.
- An edge score is oriented log-likelihood ratio minus collapsed log-likelihood
  ratio. A page score is its unweighted edge mean.
- Buckets 2--4 train; bucket 1 validates; fixed bucket 0 decides once.
- No OCR, automated vision, image evidence, embeddings, dictionary, plaintext,
  word guess, or gloss is permitted.

## Exact null and family

The exact IL006/IL009 within-page null is unchanged: D and C labels permute
separately only among positions with the same partition, exact
Currier/section/hand stratum, complete root-free form shell, five-bin
horizontal position, and paragraph-opening state. Page vocabulary, root-free
sequence, forms, positions, entry state, and edge orientations remain fixed.

One deterministic shuffle is the reserved negative; 2,048 following shuffles
estimate the null. A joint max-z conditional-randomization family and shared-
page max-z sign-flip family cover all three axes. Conservative family p is the
larger. Report page-bootstrap intervals.

## Disclosed training-only feasibility

Models trained on buckets 3--4 and evaluated on bucket 2. Every axis used
23/30 pages (76.7%), retained source exclusion, normalization, and integrity,
and had a clean reserved negative. Development-only directional residuals:

- `CURRIER`: -0.00495 bit/edge, 39.1% positive, family p=0.8897;
- `SECTION`: +0.01350 bit/edge, 65.2% positive, family p=0.1135;
- `HAND`: +0.00957 bit/edge, 56.5% positive, family p=0.2840.

Greedy 10%-swap plants added +0.08500, +0.06963, and +0.07630 bit/edge
respectively on every page, with joint sign-family p=0.000005. These are
development values only; all three axes remain frozen.

## Validation gates

Bucket 1 is evaluated twice. All gates must pass before bucket 0:

1. every axis has at least 20 evaluated pages and at least 70% coverage;
2. oriented and collapsed probability tables are finite and normalized, and
   every target value is absent from its source pages;
3. repeated outputs are identical and all cell margins, edge counts, and
   root-free sequences remain intact;
4. on every axis the 10%-swap plant adds at least +0.02 bit/edge, improves at
   least 80% of pages, and has joint sign-family p<=0.01;
5. no reserved-negative axis reaches +0.005 bit/edge, 55% positive pages, and
   conservative family p<=0.01 simultaneously.

Gate failure stops before bucket 0 and closes only this instrument.

## Held rule and interpretation

A ZL axis confirms only with residual >=+0.005 bit/edge, >=55% positive pages,
conservative family p<=0.05, and >=70% coverage. IT2a and RF1b must each reuse
at least 70% of that axis's frozen ZL pages and have the same positive mean
direction; their p-values are not combined.

- axis pass: direction-specific D-C partner choice transfers across that
  excluded metadata boundary beyond unordered pair affinity and root-side
  propensity;
- no pass: IL009's shared relation is not upgraded to direction-specific pair
  transfer at this resolution; prior line ordering remains intact.

Physical left/right order is not thereby proven to be spoken reading order.
No outcome identifies phrase structure, dependency labels, POS, language,
sound, morphology, root meaning, or plaintext.

## Stop rule

One validation and one final are allowed. Reopening requires new permitted data
or a genuinely different invariant, not another pooling rule, smoothing value,
direction encoding, root partition, split, threshold, axis subset, or pair list.
