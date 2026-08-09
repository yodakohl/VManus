# Explicit berry / no-fruit Herbal contrast freeze

## Exposure and scope

The user proposed separating Herbal pages with berries from pages without
berries before the active reset. No valid active experiment or result for the
current human-labelled panel exists in the compact claim registry. This new
route is **exploratory and source-exposed**: the source labels and page IDs are
known, but no current-transcription feature score has been computed when this
freeze is written.

Only literal human assertions in the current voynich.nu/Gheuens-Rapaport page
atlas are admitted:

- positive: exact phrase `α: berries that have no added circles`;
- negative: exact phrase `α: no fruits or flowers`.

Silence, missing tags, ambiguous “flowers or berries,” possible plant names,
AI plant identifications, OCR, and automated/neural vision are excluded. The
expected panel is eight positive and seven negative physical pages. All must
be section H, Currier A, hand 1 in every manual reading. Alternate readings
are one manuscript and are synchronized, never counted as replications.

## Text and feature universe

Use only `CONFIRMED_PROSE` rows on the fifteen pages in the current
pre-grounding interlinear. Literal tokens and parsed root tokens have separate
denominators. The score-blind feature inventory contains:

- exact literal tokens;
- proper literal prefixes, suffixes, and strictly internal substrings of
  lengths 2, 3, and 4;
- exact parsed-root tuples, root atoms, root tuple prefixes/suffixes, and
  adjacent root bigrams.

Every feature must exist in all three readings, hit at least eight tokens and
four physical pages in each reading, and proper literal pieces must occur in
at least four distinct complete token types in each reading. Features are
fixed before the source-positive assignment is scored.

## Nuisance controls and exact statistic

For each edition, page, and feature, count tokens containing the feature at
least once. Condition exact expected counts on complete token length (literal
character length or parsed-root atom count), divide residuals by the page's
matching token denominator, then project out a score-blind intercept and linear
folio-number trend. Raw token-membership rates with the same folio projection
are a mandatory sensitivity.

Enumerate all `C(15,8) = 6,435` eight-page assignments. For every feature and
reading, standardize the positive-minus-negative mean by its exact assignment
standard deviation. A feature's score is the better of the positive and
negative directions, using the **minimum** standardized effect over ZL3b,
IT2a, and RF1b; reading disagreement therefore scores zero. The family null is
the maximum feature score at each synchronized assignment. Tails are inclusive
and no permutation-order tie break is allowed.

## Frozen candidate gates

A provisional page-field candidate requires all of:

1. primary familywise exact `p <= .05`;
2. raw-rate sensitivity familywise exact `p <= .10`;
3. the same direction in all readings and both views;
4. minimum absolute primary reading effect at least `.015`;
5. raw presence on at least four pages of the enriched source class in every
   reading;
6. the primary direction survives deletion of every one of the fifteen pages
   in every reading.

The control run must reconstruct the source panel and feature universe without
computing the source-positive target assignment. It must pass unique-planted,
reading-disagreement, linear-folio, constant, exact-enumeration, deterministic,
and artifact-binding controls before one target invocation.

## Claim ceiling

Even a pass nominates only a recurrent text pattern associated with this
explicit human berry/no-fruit page panel. It cannot establish that the author
mentions berries, identify a noun or negation, translate the pattern, identify
a plant or language, or supply plaintext. A failure closes only this fixed
page-level morphology score; it does not turn unannotated pages into negatives.
