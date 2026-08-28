# GDT613 method

## Question

Can an exact GDT609 FST34 implementation recover natural planted plaintext and
all 42 primitive/merge cards once every parameter is directly observable?

## Inputs

GDT608 supplies the directed 98-unit/64-merge tree. GDT609 supplies the model
JSON. A hash-pinned Latin reference is partitioned before truth generation.
GDT612 supplies only seven archived keys for a labelled post-run bridge rescore;
it supplies neither a target result nor a success threshold.

## Method

GDT612 mixed a real-language model, a destroyed-language discriminator and a
reference-word candidate inventory. Its objective ranks planted truth below
every fitted pseudokey, while its generator omits four primitives and one
override from train. Longer search cannot repair either defect.

GDT613 therefore uses natural Latin plaintext but no plaintext alignment, word
list, candidate word, destroyed-LM subtraction, lexicon bonus or Voynich target
data during fitting. The preparer parses the bound GDT609 `model_v1.json` and
compiles the capacity/grammar consumed by the decoder. Connector, wholeform,
context and null transitions remain behaviorally distinct. All 64 GDT608
merges compose in directed order; eight synthetic truth cards are separate paid
exceptions, at most four wholeforms, with no independent qok-family whole card.

Each truth world carries fixed output-length cards. Search mutates characters
directly over the normalized Latin alphabet; it never selects reference words.
Moves exchange complete role/length cards, mutate one output character, or
move/mutate a paid merge card. Output length is not a free move.

The primary term is real-reference character cross-entropy of the complete
decoded chunk stream, including boundaries. There is no real-minus-destroyed
term and no dictionary reward. FST violations, connector edge/only use and
override description length are separately reported in one additive bit scale.
An independent reference block supplies a confirmation score never optimized.
Destroyed references are separate matched fits, never a subtracted reward.

## Decision rule and claim ceiling

The oracle gate scores truth, every declared one-move mutation, old GDT612 keys
where comparable and deterministic near/far decoys. Every truth parameter must
be exercised in train and held. If truth does not outrank alternatives on both
fit and confirmation blocks, the objective is non-identifying and recovery
stops.

Only then may multiple blind starts recover the exact behavioral truth class:
primitive role+output, merge-card location/type+output and held plaintext.
This experiment may select or reject a synthetic generator, exact-FST
implementation, objective and optimizer. It cannot assign a Voynich unit, word,
sound, language, plaintext or meaning. A later target experiment is allowed
only after the synthetic gates pass without repair from held results.
