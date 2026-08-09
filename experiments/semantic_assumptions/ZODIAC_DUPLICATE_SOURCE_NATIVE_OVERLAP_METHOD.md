# Source-native overlap across duplicated zodiac signs

## Question

Do the two public-icon-identified Aries pages (`f70v1`, `f71r`) and the two
Taurus pages (`f71v`, `f72r1`) share any complete source-native subword
material that is absent from the other zodiac pages?

This is distinct from the archived terminal `r/s` suffix audit. It uses the
lossless source-native STA layer, scans complete page text, and does not use
the unavailable formal parser.

## Inputs and scope

- The corrected public page table supplies zodiac identities from the
  illustration-description field only. The contradictory f73v tentative field
  is ignored; f73v is Sagittarius.
- ZL3b, IT2a, and RF1b are alternate readings, not replications.
- Every zero-alternative source group on all 12 zodiac pages is included. No
  nearest-object, label-to-figure, clockwise day, or millimetric ownership is
  inferred.

## Frozen feature views

Within each complete source group and reading, enumerate contiguous:

- STA-family n-grams of lengths 2, 3, 4, and 5;
- exact STA-member-code n-grams of lengths 1, 2, and 3;
- complete STA-family group surfaces.

For each view, compare the three possible perfect matchings of the four
15-item half-sign pages using multiset weighted Jaccard, summing the two pair
scores. The public Aries-plus-Taurus matching is fixed before manuscript
features are opened.

A candidate sign-specific feature must occur on both pages of Aries or both
pages of Taurus in every reading, and occur on none of the other ten zodiac
pages in any reading. Report its page/reading counts, source roles, and exact
source-group witnesses. Do not select a spelling after inspection.

## Decision and ceiling

The layout-preserving matching null has only three assignments, so its minimum
attainable one-sided probability is `1/3`. This pass is descriptive regardless
of rank. A surviving feature is only a same-sign page-specific subword
candidate requiring new independent evidence; it is not ARIES, TAURUS, a sign
name, a month, a day, a word, a lexeme, plaintext, or translation. Zero
candidates closes this exact recurrence route without retuning n-gram lengths,
readings, pages, roles, or absence rules.
