# GDT003 nested held-folio replication method

Status: `FROZEN_BEFORE_NESTED_TARGET_SCORING`

Date: 2026-08-14

Branch: `yolo/gdt002-visual-grammar-constraints`

## Question and ceiling

This replication asks whether a formal transformation algebra learned anew on
training folios predicts exact source-group forms on a completely unseen
physical folio better than strong string-statistical baselines. It assigns no
morpheme, grammatical category, language, sound, meaning, plaintext, or
translation.

The earlier GDT003 transformation list is not supplied to an outer fold. The
named `q-` plus right-edge `-dy/-dal/-dar` family is a preregistered reporting
subgroup because the user named it before this replication; it receives no
special inclusion rule.

## Corpus and firewall

The corpus contains one physical source group only when ZL3b, IT2a, and RF1b
have the same nearest-basic-EVA display and source-group topology. The three
editions are alternate readings of one manuscript, not replications. f84r is
discarded by a routing-field guard before any formal fields are retained,
joined, or scored. Cleaner-created fragments are not added as boundaries.

Every outer fold removes one complete physical folio before transformation
discovery, operation selection, pair selection, character-model fitting, and
whole-group frequency fitting. A prediction is eligible only when its exact
target type is absent from training.

## Training-only transformation discovery

The fixed target-blind edit grammar is:

- add 1--3 characters at the left edge;
- add 1--3 characters at the right edge;
- replace a 1--2-character left edge with a 1--2-character left edge while
  retaining a nonempty common remainder;
- replace a 2--3-character right edge with a 2--3-character right edge while
  retaining a nonempty common remainder.

Replacement directions are canonicalized lexicographically to prevent inverse
duplicates. The actual added/replaced strings are inferred only from exact
training type pairs. A rule needs at least five exact training type edges and
support on at least three training physical folios.

To bound flexibility without privileging earlier Voynich strings, rules are
stratified by edit family and old/new edge lengths. Within each stratum, retain
the best 32 by exact edge count, then physical occurrence support, then rule
identifier. There are at most 448 retained rules per fold. This selector was
frozen before nested target scoring.

## Training-only algebra and predictions

For each retained operation pair and training host `X`, construct `A(X)`,
`B(X)`, `A(B(X))`, and `B(A(X))`. Only commuting pairs with the first three
cells present contribute. A pair is frozen for prediction when training has at
least three three-cell hosts and at least one complete rectangle.

For a training three-cell host whose common fourth form is absent from
training, the fold emits that exact fourth form as a prediction. Multiple
derivations of the same target are deduplicated by the training-only paradigm
score

`log2((complete + 0.5)/(triplets + 1)) + log2(1 + min(edgeA,edgeB))/20`.

No held-folio string, label, count, success, or rank enters discovery or
tie-breaking.

## Baselines and evaluation

All models rank the identical frozen candidate targets in each fold:

- paradigm completion score;
- character order-2 KT;
- character order-4 KT;
- visible whole-group frequency of the three known cells;
- nearest edit distance to the three known cells.

The GDT001 context mixer is recorded as non-comparable because it has no
isolated missing-group API independent of its canonical serialized context.

Report exact correct predictions, precision, coverage of held novel types,
average precision, AUC, and top-1/top-5 hits. A deterministic 4,096-world
within-folio label permutation preserves each fold's candidate count and
positive count and tests the paradigm AP advantage over the best string
baseline. Report the same metrics for the preregistered subgroup consisting of
training-discovered prepend-`q` combined with a training-discovered right-edge
add/replace involving `dy`, `dal`, or `dar`.

## Decision

- `PRODUCTIVE COMPOSITION SUPPORTED` requires at least five exact held-folio
  hits, paradigm AP at least 0.02 above every string baseline, permutation
  p<=0.05, and positive advantage in the named q/right-edge subgroup.
- `LIMITED/LOCAL COMPOSITION ONLY` requires exact held-folio hits and positive
  paradigm advantage that misses at least one confirmation gate.
- `NOT DISTINGUISHABLE FROM STRING STATISTICS` applies when exact held-folio
  hits exist but paradigm ranking does not beat the best string baseline.
- `PRODUCTIVE COMPOSITION FALSIFIED` applies when the nested discovery emits no
  correct unseen-folio completion or cannot recover a reusable algebra.

All readings were public before computational masking. A correct prediction is
model-hidden cross-validation, not newly acquired manuscript evidence.
