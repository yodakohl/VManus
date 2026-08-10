# ZODIAC_DUPLICATE_CROSSROLE — frozen cross-page C/L design

Date frozen: 2026-08-10, before computing any C-to-L manuscript similarity.

## New invariant

The prior duplicated-zodiac audit merged all IVTFF roles into a page bag and
had only three matchings among four half-sign pages.  This successor is
different:

- it uses all twelve public zodiac page panels;
- it keeps circular (`C`) and label (`L`) material separate;
- it forbids same-page comparisons;
- for each page pair it symmetrically averages `C(page 1)`--`L(page 2)` and
  `C(page 2)`--`L(page 1)`;
- it asks whether the two public duplicated-sign pairs, Aries
  f70v1--f71r and Taurus f71v--f72r1, are jointly exceptional among every
  choice of two disjoint page pairs.

There are exactly 1,485 such two-pair matchings.  Sign identities come only
from the corrected public illustration descriptions.  Tentative identities,
nymph proximity, day order, ring position, and object attributes are excluded.

## Representation and score

- zero-alternative source-native STA groups only;
- ZL3b, IT2a, and RF1b separately;
- eight views: family n-grams 2--5, exact member n-grams 1--3, and whole
  family-group surfaces;
- deterministic weighted Jaccard;
- within every reading/view, population-standardize the 66 cross-role page-pair
  similarities;
- matching score is the mean z similarity of its two pairs over all views;
- primary score is the weakest reading score;
- exact inclusive one-sided orbit with 1e-15 tie tolerance.

The complete test is repeated after deleting every source group whose family
surface ends in `BABA`.  This deletion is mandatory because `okeodaly` and
related `BABA` families motivated the route; they cannot confirm it by
themselves.

## Controls and gates

Before target access, the scorer must enumerate exactly 1,485 unique matchings,
recover a distributed two-pair plant uniquely at rank 1, and reject constant,
one-pair, one-page-hub, and third-reading-disagreement worlds.  Positive affine
transformations and simultaneous page relabeling must preserve the decision.

Confirmation requires, for both FULL and NO_BABA:

- exact joint p <= .01;
- positive matching score in all three readings;
- both Aries and Taurus pair contributions positive in every reading;
- each individual pair is in the inclusive top 10% of all 66 page pairs in
  every reading;
- deleting any one of the eight views leaves joint p <= .05, every reading
  positive, and both pair contributions positive.

No reading, role direction, view, page, sign pair, group, family, member, or
spelling may be selected after the result.

## Claim ceiling

A pass establishes only a transferable source-native cross-role field across
the two duplicated public sign relations.  It would make a sign-level shared
component more plausible, but would not identify which form carries it or
establish a sign name, month, day, degree, person, star, barrel, word, morpheme,
sound, language, plaintext, or translation.  Failure closes this fixed
cross-role representation.
