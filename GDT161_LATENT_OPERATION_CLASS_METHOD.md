# GDT161 latent operation-class method

Status: **FROZEN BEFORE LATENT-CLASS SCORING**.

## Question

GDT160 found a large, diffuse LEFT×RIGHT compatibility excess after preserving
operation counts, supports, hosts, token lengths, character frequencies, and
register placement.  GDT161 asks whether that excess is predictively compressible
into a small factorial inventory of anonymous LEFT and RIGHT operation classes.
The alternative is a large collection of local lexical/morphotactic
contingencies that does not transfer to unseen operation pairs.

This is a surface-incidence experiment.  It assigns no glyph value, morpheme,
sound, language, syntax, plaintext, meaning, or semantic gloss.

## Frozen inputs and operation graph

The scorer reconstructs every GDT003 training-fold operation graph from the
already-frozen, f84r-free GDT003 target corpus and the five GDT159 diplomatic
comparators.  Operation discovery, the fourteen support strata, 32-operation
stratum cap, and compatibility thresholds are unchanged.  LEFT is the union of
prefix-add and prefix-replace operations; RIGHT is the union of suffix-add and
suffix-replace operations.  A positive graph cell requires at least three
LEFT×RIGHT host triplets and at least one complete directed square, exactly as
in the calibrated GDT160 graph definition.

Operation strings and glyph identities are forbidden model inputs.  Each
operation is represented only by:

1. an anonymous binary incidence vector over the source hosts on which it has
   an observed edge; and
2. where allowed, its compatibility row or column after the evaluated cells
   have been masked.

Host coordinates are anonymous categories.  Their spellings, lengths,
characters, operation family subtype, and edit strings are never supplied to a
clusterer or predictor.  Opaque hashes are retained only for deterministic
splits, joins, and reproducibility.

## Fixed models

`GLOBAL` predicts the training-cell prevalence.

`HOST_PROFILE_LOGIT` is a fixed ridge-logistic baseline using only five
anonymous incidence summaries: left support, right support, intersection,
Jaccard overlap, and cosine overlap.  It receives no character features.

`DEGREE_LOGIT` is an additional masked-cell baseline using smoothed observed
training row and column rates.  It is ineligible when an operation is wholly
unseen.

`HOST_BLOCK` clusters LEFT and RIGHT operations separately by cosine k-means on
their normalized anonymous host-incidence vectors.  Smoothed compatibility
probabilities are then estimated for every LEFT-class×RIGHT-class block.

`COMPAT_BLOCK` starts from the same host classes and alternates LEFT and RIGHT
assignments using only the unmasked compatibility profile.  It is evaluated
only for masked cells, never as evidence for unseen-operation transfer.

The predeclared class grid is `K = {1,2,4,8,16,32}` independently on each side,
subject to nonempty-class capacity.  All admissible LEFT-K × RIGHT-K
combinations are evaluated.  Training-only two-part MDL chooses the pair:

`Bernoulli block codelength + 0.5*K_LEFT*K_RIGHT*log2(training cells) +
nLEFT*log2(K_LEFT) + nRIGHT*log2(K_RIGHT)`.

K=1 is the no-class model.  No result-dependent K, feature, threshold, or
operation name is added.

## Held-out tests

### Pair-cell test

Every LEFT×RIGHT cell is assigned by opaque-ID hash to one of five outer
partitions.  For each partition, that cell set is hidden before class fitting,
block-rate estimation, degree estimation, and prediction.  All cells receive
one prediction.  This tests completion of unseen pair compatibilities while
allowing the remaining compatibility profiles of both operations.

### Both-operations-unseen test

LEFT and RIGHT operations are independently assigned to five opaque-ID
partitions.  The 25 crossed folds each remove one LEFT partition and one RIGHT
partition completely.  Class prototypes, baseline coefficients, and block
rates use only the remaining operations.  Held operations are assigned to
classes solely by cosine similarity of anonymous host-incidence profiles.
Every pair is evaluated exactly once, with both endpoint operations unseen to
the compatibility model.  `COMPAT_BLOCK` and `DEGREE_LOGIT` are not eligible.

Scores are pooled average precision, log loss in bits/cell, Brier score, top
prevalence-matched precision, fold-direction counts, and selector-paid MDL.
The primary test is whether `HOST_BLOCK` improves held log loss and average
precision over both `GLOBAL` and `HOST_PROFILE_LOGIT` in the
both-operations-unseen evaluation.  Pair-cell `COMPAT_BLOCK` is an upper-bound
diagnostic, not sufficient evidence of a reusable factorial system.

Class compactness is reported as selected K, operations per class, occupied
positive blocks, positive-cell concentration by block, and co-clustering
stability across the pre-existing GDT003 folds.  Opaque operation identity may
be used to compare repeated assignments after fitting, never as a feature.

## Top-20 concentration null

The GDT160 primary right-label switch is rerun for the Voynich target with the
same 1,024 worlds, burn-in, spacing, seed derivation, and exact length blocks.
This time every anonymous pair's eligibility is retained.  Each null world is
treated as a pseudo-observed graph; its pair excess is measured against the
leave-one-world-out mean, positive excesses are ranked, and the fraction in the
top 20 is recorded.  The observed GDT160 graph is evaluated against the same
pair universe and null mean.  The inclusive concentration tail answers whether
the published 0.58% top-20 share is unusually concentrated or unusually
diffuse under the degree-preserving null.  Pair identities remain descriptive.

## Comparator and decision rules

The identical procedure is run on all five GDT159 corpora.  The low-capacity
apothecary corpus may return `INSUFFICIENT_CLASS_CAPACITY`; it is never pooled
to manufacture power.  ZL3b/IT2a/RF1b are not three samples because the frozen
target is the already matched agreement corpus.

Final decision vocabulary:

- `COMPACT_FACTORIAL_OPERATION_CLASSES_SUPPORTED`
- `PAIR_COMPATIBILITY_COMPRESSIBLE_BUT_NOT_NEW_OPERATION_TRANSFERABLE`
- `LATENT_CLASSES_NOT_ABOVE_HOST_DEGREE_BASELINES`
- `DIFFUSE_LEXICAL_MORPHOTACTIC_CONTINGENCIES_FAVORED`
- `INSUFFICIENT_CLASS_CAPACITY`

The strongest decision requires a selected K no larger than 16 on both sides,
positive both-unseen log-loss gain over `HOST_PROFILE_LOGIT`, positive AP gain,
positive direction in at least 9 of 12 Voynich GDT003 folds, and no worse than
half of the pair-cell latent gain surviving the both-unseen test.  Otherwise a
pair-cell-only gain is explicitly local/compressible but nontransferable.

## Seal and claim ceiling

The scorer reads only the frozen GDT003/GDT159 corpus bundles and GDT160
aggregate artifacts.  It does not read a Voynich transcription table or image.
The GDT003 provenance already excludes f84r; every input hash and seal flag is
validated before scoring.

At most, GDT161 can establish predictive compression of a formal
surface-operation incidence graph.  It cannot establish linguistic morphology,
a word boundary, language, sound, plaintext, meaning, semantic role, or
translation.
