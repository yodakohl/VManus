# GDT610 exploratory contract: consensus-coupled carrier decoder

Frozen before any target held-text decoding.

## Scope and bindings

- Input: published GDT606 boundary-aware 98-unit sequence artifact, SHA-256
  `3ee0841e211314b72719acbbf79ed3a6dc7bfc3c157734f54dbdac92ac458fdf`.
- Only the 68 training folios choose target mappings. The 23 held folios are
  decoded after all categories, candidates, hyperparameters, and mappings are
  frozen.
- No sealed target and no GDT459--GDT599 workshop output is an input.
- Reference texts and their hashes are hard-bound in the source.

## Decoder fixed in advance

1. Assign exactly 42 letter, 4 doubled-letter, 34 syllable, 7 null, and 11
   whole-word carrier categories deterministically from training-ciphertext
   frequency, boundary, standalone, and context-entropy features. Categories
   never move during language fitting. Whole-word anchors are ranked by
   standalone fraction plus a boundary term; frequency has only a tiny
   *negative* tie-break and therefore cannot create a W bucket.
2. Form six deterministic leave-one-folio-block-out views. Each view has a
   different frequency-based candidate rotation but the same fixed categories.
3. Optimize each view by deterministic coordinate ascent. After warm-up, every
   proposal includes an explicit reward for agreement with the modal output of
   the other five views. Thus carrier agreement is inside the objective.
   The language term is character 4-gram typicality plus a reference word-length
   distribution only. There is no dictionary-membership or word-frequency
   bonus. Every non-null codebook output additionally pays the explicit
   two-part MDL spelling cost `(1 + output_length) * log2(27)` bits once per
   view; a W candidate therefore pays for every output character.
4. Choose the consensus weight only on a planted-key synthetic mixed-codebook
   control with the same 98 labels and exact target chunk-length sequence.
   Control categories are supplied (the control tests output/key recovery
   conditional on the anchor-first allocation). Synthetic labels are
   frequency-rank relabeled (descending control occurrence count to descending
   frozen training-corpus occurrence count) before decoding; label names carry
   no oracle information, while this makes the control match both chunk and
   rank-frequency form. Evaluate weights
   `0, 0.03, 0.10, 0.30, 1.00`; zero is the uncoupled diagnostic only. Among
   positive weights select the maximum of the unweighted sum of held plaintext
   character accuracy, held occurrence-weighted key accuracy, type key
   accuracy, and exact-map stability; ties go to the smaller weight.
5. Apply that weight unchanged to Latin, Old Italian, and Middle High German.

## Evidence rule

A target fragment is concrete only if at least four characters long, arises at
the same held locus from the same contiguous source-unit span, and all six
coupled views give the identical unit-to-output assignments across that span.
A dictionary match alone is insufficient. We report the uncoupled baseline,
synthetic oracle recovery, all mappings, and every held decode so forced but
wrong consensus remains visible.

Two earlier implementation smoke tests were stopped during their first target
fit without inspecting or retaining target metrics: the first control did not
match rank-frequency form; the second still gave lexicon membership a direct
score bonus. This contract governs the final run. The scratch copy used during
computation differed from the published input only in the inert JSON schema
label; the inventory, metadata and complete train/held payload are
byte-identical after removing that label. GDT610 binds the canonical published
hash above.
