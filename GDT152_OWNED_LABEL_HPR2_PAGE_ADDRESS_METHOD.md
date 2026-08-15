# GDT152 — owned pharmaceutical-label HPR2 page address

## Question and novelty

Can the current HPR2 PAGE_HOST representation recover the five externally
fixed Herbal↔pharmaceutical relations whose pharmaceutical inscriptions have
singular or provisional local ownership?

The old source-root route stopped or failed under a different parser. GDT152
does not reopen that parser: it applies the later HPR2 layer stripping to a
published five-label query slice and compares the resulting anonymous query to
complete Herbal PAGE_HOST bags. The panel and targets are fully exposed, so
this is a post-hoc mechanism test, not confirmation.

## Fixed panel

The five relations are unchanged:

- f89v2.6 → f48v;
- f102r2.21 → f18v;
- f102r2.22 → f23r;
- f102v1.17 → f19r;
- f102r1.2 → f37v.

The query TSV preserves ZL3b, IT2a, and RF1b separately. `token` is the
published nearest-basic display form used by HPR2 and is explicitly lossy;
`family_surface` is the source-native consensus-family view. The readings are
sensitivities, never replications.

## Exact test

For each reading, construct a 5×5 query-to-target matrix under five fixed
representations:

1. exact PAGE_HOST identity;
2. PAGE_HOST character trigrams;
3. raw display-token character trigrams;
4. source-family character trigrams;
5. HPR2 compiler signature.

Similarity is weighted Jaccard between the one-label query and each complete
target-page bag. Enumerate all 5! = 120 target assignments. Report the true
assignment score/rank/tail, row ranks, and a shared maximum-over-15
representation×reading score control.

## Ceiling

This can test only whether the fixed locally owned labels behave like HPR2
addresses for their paired Herbal page. Failure does not prove that labels or
PAGE_HOSTs lack content. No plant/component identity, semantic role, gloss,
word, morpheme, POS, sound, language, plaintext, meaning, or translation is
assigned. f84r is absent from the query and target panel.
