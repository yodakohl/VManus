# FPR001 ordered-root target-blind calibration

Status: **FROZEN SYNTHETIC ONLY; F37V FORMAL CONTENT FORBIDDEN**.

## Frozen statistic

The fixed query is the five-root sequence `ot+od+e+od+or`. For each complete
parsed word, compute its longest common subsequence (LCS) length with the query.
The page score is the maximum word LCS. A target passes only if:

1. its page score is at least 3 in ZL3b, IT2a, and RF1b;
2. it is the unique highest-scoring page in every reading; and
3. it is the unique highest page after averaging the three reading scores.

Alternate readings are sensitivity surfaces, not replications. The final
inclusive empirical rank is among target plus 94 frozen H/A/hand-1 background
pages. Its attainable passing floor is `1/95=.010526 <= .02`.

The threshold 3 was fixed from target-masked capacity: every background word
has LCS at most 2. No target value may inform it.

## Synthetic worlds

Reconstruct the 94-page background after excluding f37v before formal-field
access. Select pseudo-target pages by sorted-page cyclic index. Synthetic
changes are literal root-word fixtures; their page score is always recomputed
by the frozen LCS function rather than assigned directly.

- 64 `NULL`: unchanged background.
- 8 `FULL_ORDERED`: add the exact query word in all readings (LCS 5).
- 8 `REDUCED_ORDERED`: add `ot+od+e` in all readings (LCS 3).
- 8 `UNORDERED_BAG`: add `e+or+od+od+ot`, the same root multiset as the query
  but a deliberately different order (LCS 2).
- 8 `ONE_EDGE`: add `x+ot+od+x` (LCS 2).
- 8 `CROSS_WORD_SPLIT`: distribute query material over the separate words
  `ot+od`, `e+x`, and `od+or` (maximum within-word LCS 2).
- 8 `ONE_READING`: add `ot+od+e` to only one cyclically selected reading.
- 8 `READING_DISAGREEMENT`: add `ot+od+e` to ZL3b and IT2a but not RF1b.

Required outcomes: zero NULL passes; 8/8 in both ordered-positive families;
zero passes in every adversarial family. Reversing page order must leave all
decisions unchanged. An injective renaming `root -> R:root`, applied to both
query and words, must leave every background and fixture LCS byte-identical.
Any f37v root/surface/match/score access is a hard stop.

## Consequence

A complete pass authorizes a separately committed, frozen, one-shot f37v
target using exactly this statistic. A target pass can establish only
unusually strong anonymous ordered-root composition in the new same-drawing
pair. It does not establish a plant name, component, word, sound, language,
cipher, plaintext, meaning, or translation.
