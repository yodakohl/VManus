# GDT143 — nested relation-pair prediction

## Question

Can a formal-pair rule learned from four archived Herbal relations rank the
fifth relation's target page, or is GDT140 only a simultaneous five-pair
assignment effect?

This is an exposed, post-hoc internal transfer test.  It uses only the
published f84-free GDT140 5×5×4 similarity cube and all 120 assignment worlds.
No transcription source, image, new relation, or semantic label is opened.

## Exact nested procedure

For every assignment world and each held source relation:

1. hold out all five candidate pairs involving that source page;
2. on the other four source pages, label the world's four assigned pairs one
   and the other sixteen pairs zero;
3. standardize features on those twenty training pairs only;
4. fit ridge least squares with an unpenalized intercept and fixed lambda 1;
5. softmax the five held scores and rank the world's assigned target.

The six fixed feature models are exact PAGE_HOST identity, PAGE_HOST character
trigrams, both PAGE_HOST scores, raw character trigrams, compiler signature,
and all four published similarities.  Report mean reciprocal rank, mean log2
assigned-target probability, and top-one count.  Refit the entire nested
procedure for every one of the 120 assignment worlds.  A shared maximum over
six models times three metrics is the finite-orbit search diagnostic.

This is a prediction in the limited sense that each target relation is absent
from its fold's training labels.  It is not prediction into the full Herbal
corpus: all five candidate target pages and the panel itself were already
exposed.

## Ceiling

Use `NESTED_RELATION_PAIR_STRUCTURE_TRANSFERS_WITHIN_EXPOSED_POOL` only if the
PAGE_HOST-character-trigram and all-four models each achieve at least three of
five top-one targets, mean-reciprocal-rank local p at most .05, and the shared
18-statistic tail is at most .05.  Otherwise use
`NESTED_RELATION_PAIR_STRUCTURE_NOT_SUPPORTED`.

No result establishes botanical truth, a plant/component identity, a semantic
role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or
translation.
