# GDT338 renderer-invariant formal equivalence report

Status: **NO_STABLE_RENDERER_INVARIANT_EQUIVALENCE**.

## Prospective panel

The frozen outer panel contains 25 fields / 32 groups on 17 held physical folios, representing 9 exact normalized classes in 3 registers. Every held rendered surface was absent from training; every normalized class had at least two training surfaces on at least two training folios. No raw glyph, separate PAGE_HOST feature, substring, semantic annotation, or external source was used; PAGE_HOST remains opaque inside the exact joint ID.

## Unseen-surface wrapper transfer

The best noncandidate wrapper baseline is **JOINT_NO_RULE**. `JOINT_TWO_RULE` changes held codelength by +2.384 bits relative to that baseline (-0.201 after the fixed log2(6) selector), with 4/17 positive folio folds and 2/3 positive registers. Its fixed-prediction max-two diagnostic p is 1.000000.

Exact wrapper-sequence top-1 is 5/25 for the candidate versus 4/25 for the best baseline. Exact rendered-surface lookup has 0/25 coverage by construction.

## Normalized-object recovery from placement

The frozen GDT336 placement correction changes held tuple codelength by +7.977 bits (+6.977 after the one-bit selector), with 10/17 positive folio folds and 2/3 positive registers. Exact normalized-field top-1 is 15/25 versus 9/25; max-two diagnostic p is 0.326498.

The genuinely multi-group sensitivity contains seven two-group fields. Its wrapper gain is +1.322 bits and its placement gain is +2.536 bits. This small subset is reported as a sensitivity, not upgraded into sequence-level evidence.

## Interpretation

The decision gates are mechanical. A failure means that the executable grammar does not justify a new equivalence relation beyond exact opaque joint-tuple identity under the tested renderer/placement marginalization. A pass would still establish only formal predictive exchangeability, never semantic or linguistic identity.

## Claim ceiling

Opaque exact-joint renderer normalization only. No different tuple sequence, word, morpheme, PAGE_HOST function, semantic role, meaning, sound, language, plaintext, translation, diagram phase, or external correspondence is inferred. f84 was not opened, parsed, retained, joined, or scored.
