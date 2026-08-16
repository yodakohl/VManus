# GDT163 — held-base one-glyph substitution context transfer

Status: `METHOD_AND_ANALYSIS_FAMILY_FROZEN_BEFORE_SCORING`

## Question

GDT162 found 933 Hamming-one edges among 241 short HPR2 `PAGE_HOST`
identities.  Exact host identity was much more predictive of outer compiler
context than neighbor backoff, but the neighbors still transferred context and
shared substitution-direction effects above position-preserving nulls.

GDT163 asks the causal follow-up: does one *specific* directed substitution

`(host length, position, source HPR2 character -> target HPR2 character)`

learn a context-change vector on unrelated base identities and predict the
direction of change on an unseen base identity?  A genuine productive internal
operator should transfer beyond the exact host pair.  Ordinary lexical
neighborhood similarity need not.

This remains an exploratory formal test.  “Operator” means a predictive
surface relation only; it is not a morpheme, sound change, grammatical
category, or semantic operation.

## Sources and seal

Voynich rows come only from the frozen `gdt062_right_family_inventory.tsv`.
The published HPR2 `page_host` is not refit.  Every row whose page or locus
begins `f84` is rejected before retention.  The actual source contains zero
f84r rows; no f84r row, image, transcription, or formal payload is opened,
queried, retained, joined, or scored.

Historical controls are the five frozen surface-only corpora in
`gdt159_diplomatic_corpora.json.gz`.  No expansion, lemma, translation,
phoneme map, or Voynich-specific parser is applied.

## Directed substitutions and held base families

Primary Voynich hosts have exactly two or three frozen HPR2 display
characters.  Equal-length pairs differing at one position define an edge.
Direction is frozen by Unicode code-point order at the differing position, so
every unordered edge appears once and the reverse is not counted as a second
sample.  The operation key is `(length, position, source, target)`.  The base
family is the remaining string with that position replaced by `*`.

An HPR2 cell is `(operation, base family, section, hand)`.  Both endpoint hosts
must occur at least twice in that exact section×hand cell.  An operation must
have at least four eligible base-family cells to enter transfer scoring.
Weights are `min(20, min(source occurrences, target occurrences))`.

For each cell, encode the source-to-target delta in six *separate* outer HPR2
blocks:

- wrapper;
- inner-D;
- O/OT/local frame;
- right-family renderer;
- DY closure;
- B3 closure.

Each block is a Jeffreys-smoothed categorical distribution.  The candidate
host string never includes any of these outer fields.

## Primary held tests

For each test cell predict its delta from a weighted mean of cells carrying the
same operation while excluding its complete base family.  Score:

- `HELD_BASE`: exclude the base family;
- `HELD_BASE_AND_SECTION`: also exclude the target section;
- `HELD_BASE_AND_HAND`: also exclude the target hand.

At least three training cells and two training base families are required for
each prediction.  Report weighted fractional MSE gain over a zero-delta
baseline, mean cosine, positive-dot direction rate, coverage, and the number of
sections/hands/base families represented.

Two baselines remain separate:

1. `POSITION_ONLY`: same length and position but a different glyph pair,
   excluding the target base family;
2. `EXACT_PAIR_OTHER_STRATA`: the same exact host pair in other section×hand
   cells.  This is an exact-identity baseline and is never mixed into the
   substitution learner.

Operation-specific scores are post-ranked.  MaxT is taken over every eligible
operation in each null world.

## Identical language-agnostic comparator endpoint

GDT159 has no HPR2 wrappers, so manufacturing them would be an invalid
comparison.  A second local-sequence context is therefore computed identically
for Voynich and every historical control:

- contiguous previous-form length class: missing, 1, 2, 3, or 4+;
- contiguous next-form length class: missing, 1, 2, 3, or 4+;
- occurrence-position quartile within the source unit.

Voynich units are physical loci with exact group indices.  Historical units
use frozen `unit_id` and `occurrence_index`; previous/next context is admitted
only when the sampled occurrence index differs by exactly one.  Missing sampled
neighbors remain `MISSING` rather than being treated as document boundaries.

For each corpus, aggregate these context blocks by exact 2–3-character form,
build the same directed Hamming-one operations, and run the same leave-base
learner and `POSITION_ONLY` baseline.  Forms and both endpoints must recur at
least twice; operations require four edges.  Historical fold IDs are provenance
strata, not replications.

The HPR2 and generic context vectors have different dimensions and are never
pooled.  Their dimensionless MSE gain, cosine, direction rate, and null rank are
compared.

## Nulls

Use 1,024 deterministic position-preserving worlds per corpus.  Every original
host/form identity, its occurrences, context vector, length, and each
position's character multiset remain fixed.  Characters are independently
shuffled across type identities at each length and position.  The shuffle
changes which identities form Hamming-one edges and which edges share a
substitution key, thereby destroying only the observed substitution pairing.

Generated labels may collide; identities remain separate and collisions are
reported.  For each world rerun eligibility, held-base prediction, the
position-only baseline, and the best-operation search.  Report inclusive local
and maxT p-values.  No discovery gate automatically terminates the YOLO atlas.

## Decisions

- `PRODUCTIVE_INTERNAL_SUBSTITUTION_TRANSFER_INTERESTING` requires positive
  Voynich held-base MSE gain/cosine/direction, positive held-section and
  held-hand gains, position-preserving maxT p<=.05 for at least one operation,
  and a generic-context gain above every powered GDT159 control.
- `SUBSTITUTION_TRANSFER_NOT_ABOVE_HISTORICAL_CONTROLS` applies when transfer is
  positive but matched historical systems equal or exceed it.
- `LOCAL_OR_REGISTER_CONDITIONED_SUBSTITUTION_ONLY` applies when held-base is
  positive but section or hand exclusion is not.
- `NO_PRODUCTIVE_SUBSTITUTION_SIGNAL` applies when held-base transfer is not
  positive.

These labels describe a surface-generative relation, not linguistic
morphology.

## Claim ceiling

At most GDT163 can support a recurrent one-character host relation that
predicts changes in formal outer or local-sequence context on unrelated host
bases.  It cannot establish a grapheme, phoneme, morpheme, word, POS, language,
semantic role, meaning, plaintext, or translation.
