# GDT143 — nested relation-pair prediction

## Outcome

**NESTED_RELATION_PAIR_STRUCTURE_TRANSFERS_WITHIN_EXPOSED_POOL**

With each relation held out in turn, the PAGE_HOST-character-trigram model ranks the true target at 1, 2, 3, 1, 1 of five: mean reciprocal rank 0.767, 3/5 top-one, local exact MRR p=0.0167. The all-four model yields ranks 1, 3, 1, 1, 2, MRR 0.767, and 3/5 top-one. Repeating the complete nested fit for every one of 120 mappings gives a shared maximum-over-18 p=0.0250.

The controls are informative: raw-character and compiler models produce zero top-one folds; naively combining exact PAGE_HOST and PAGE_HOST trigrams also produces zero, while the all-four ridge learns to downweight the misleading channels in four-relation training. This is genuine label holdout within the panel, but it remains conditional on five already exposed targets and therefore is not a fresh corpus holdout or manuscript-wide retrieval test.

Only published f84-free GDT140 artifacts were used; no source or image was opened. No botanical truth, plant/component identity, semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation follows.
