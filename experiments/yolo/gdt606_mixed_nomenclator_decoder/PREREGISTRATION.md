# GDT606 exploratory attack contract

GDT606 applies one fixed historical-capacity mixed-codebook family to the
GDT605 98-unit inventory. The 68/23 physical-folio split, separator treatment,
64 train-only merges, three reference languages, candidate-generation rules,
category capacities and restart seeds are fixed in source.

The primary capacity is 42 letter/homophone signs, four doubled-letter signs,
34 two-/three-letter signs, seven nulls and eleven whole-word signs. Two
capacity sensitivities use 36/4/40/7/11 and 46/4/30/7/11. Each sums to 98.
Six primary real-model starts, four matched character-order-destroyed starts
and three starts for each sensitivity are retained for each language.

A language can only become a reading candidate when its held text is more
typical under the real model, real keys dominate destroyed-reference keys,
minimum held-weighted category and exact-output agreement reach 70% and 50%,
and consensus words occur on at least three held folios. Apparent words are
also audited against their exact source-unit carriers. Failing outputs remain
search diagnostics, never translations.

The first implementation contained a process-hash-order bug in seeded
initialization. GDT606 sorts all units before every seeded shuffle. The final
artifact set was reproduced in two independent full executions after that
correction.
