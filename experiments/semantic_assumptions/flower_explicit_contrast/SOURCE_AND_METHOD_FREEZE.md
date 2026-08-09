# FLOWER001 explicit side-view-flower/no-reproductive-structure freeze

## Exposure and source panel

This is a prospective, source-exposed successor to BERRY001. BERRY001 found
no passing recurrent morphology and its thresholds, feature scores, and
near-miss are not reused to select this panel. The new independent human
predicate is the exact Gheuens/Rapaport phrase
`α: flower(s) seen from the side`. Its explicit opposite is the already
defined phrase `α: no fruits or flowers`. Silence is never a negative.

The source atlas contains 19 flower-positive and seven explicit-negative
Herbal pages, with no overlap. The first source-only control build exposed
that an ordinary page match would count the recto and verso of one folio as
separate units. It was rejected before any target feature was extracted. The
corrected prospective rule admits only one page per folio, excludes a positive
page on any negative folio, and selects the lexically first page ID when two
positive pages share a folio. Two remaining distinct-folio positive pages were
then assigned to every negative page by minimum total absolute folio-number
distance, without inspecting any Voynich string. The corrected source-only
solution is frozen as these seven triplets:

| explicit negative | flower positive 1 | flower positive 2 |
|---|---|---|
| f3r | f2r | f4v |
| f7r | f10v | f11v |
| f8r | f17r | f19r |
| f25v | f24v | f27r |
| f42r | f32r | f38r |
| f47r | f29v | f44r |
| f52v | f49r | f54r |

The total absolute folio distance is 72. Three positive pages are excluded by
the one-page-per-folio rule (f2v, f8v, and f32v), and two by the target-blind
proximity match (f87r and f90v2). The
frozen triplets, not any claim of a unique matching, define the experiment.
Every admitted page must be section H, Currier A, hand 1 in all three manual
readings. OCR, automated vision, AI plant identities, colour guesses, and
tentative plant names are excluded.

## Text representation

Use only `CONFIRMED_PROSE` loci. Reuse BERRY001's frozen current-grammar
feature builder exactly: exact literal tokens; proper within-token literal
prefixes, suffixes, and internal pieces of length 2--4; parsed-root tuples,
atoms, tuple boundaries, and adjacent root bigrams. Features must occur in all
three alternate readings, at least eight token instances and four pages per
reading; proper literal pieces need four complete containing token types.

Token membership is conditioned on complete token length, divided by the
matching page token denominator, and projected away from an intercept and
linear folio number. Raw membership rates with the same projection are the
mandatory sensitivity. ZL3b, IT2a, and RF1b are alternate readings of one
manuscript, not independent samples.

## Exact blocked inference

Within each triplet exactly one page carries the explicit negative source
predicate. Enumerate all `3^7 = 2,187` choices of one negative page per
triplet. For each feature and reading, contrast the mean of the other two
pages against the selected negative, average equally over the seven blocks,
and standardize over the exact orbit. The robust two-sided score is the
minimum same-direction standardized effect across all readings; disagreement
therefore scores zero. The family null is the maximum over every eligible
feature at each synchronized assignment. All tails are inclusive.

Anonymous controls must verify the exact orbit, a unique synthetic planted
assignment, a three-way top-tie fixture, alternate-reading disagreement,
block-constant cancellation, rejection of a one-block-driven signal, input
bindings, determinism, and absence of a target artifact. A nonimporting
implementation must reconstruct the complete control package before one
target invocation.

## Frozen candidate gates

Because this is a second source-exposed botanical page-field experiment, a
candidate must pass all of:

1. adjusted exact familywise `p <= .025`;
2. raw-rate exact familywise `p <= .05`;
3. the same direction in all readings and both views;
4. minimum absolute adjusted reading effect at least `.015`;
5. presence on at least four enriched-class pages in every reading;
6. the adjusted direction survives deletion of every one of the seven blocks
   in every reading;
7. at least five of seven individual blocks have the candidate direction in
   every adjusted reading.

No gate, block, page, feature family, nuisance term, or direction may change
after target exposure.

## Claim ceiling

Even a pass is only a recurrent page-field pattern associated with this
specific contrast between side-view-flower drawings and explicitly
fruit/flower-free drawings. It cannot establish FLOWER, FRUIT, NO, a plant
name, a word class, a language, plaintext, or translation. Failure closes
only this fixed blocked morphology test.
