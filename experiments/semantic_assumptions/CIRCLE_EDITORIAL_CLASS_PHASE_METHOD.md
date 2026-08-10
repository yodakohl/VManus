# CIRCLE_EDITORIAL_CLASS_PHASE — frozen public-class design

Date frozen: 2026-08-10, before computing a manuscript profile/class score.

## Question

Do complete source-native circular-text profiles align with the public human
catalogue's interleaved `astronomical` versus `cosmological` page classes on
f67 and f68?

This is not a zodiac-dictionary or object-label test.  The target panel is the
ten f67/f68 page panels for which the corrected public catalogue uses exactly
one of those two general-description classes:

- f67: f67r1, f67r2, f67v1 astronomical; f67v2 cosmological;
- f68: f68r1, f68r2, f68r3, f68v2 astronomical; f68v1, f68v3 cosmological.

## Frozen representation and statistic

- only IVTFF `C` circular loci;
- all zero-alternative source-native STA groups;
- ZL3b, IT2a, and RF1b scored separately;
- eight complete page-profile views: family n-grams 2--5, exact-member n-grams
  1--3, and whole family-group surfaces;
- weighted Jaccard between page profiles;
- within each folio and reading/view, population-standardize every page-pair
  similarity;
- folio effect = mean same-class z similarity minus mean different-class z
  similarity;
- reading score = equal mean over the two folios and eight views;
- primary score = the weakest of the three reading scores.

The exact null independently rotates the complete public class vector around
the ordered page panels of f67 and f68.  It therefore contains exactly 4 x 6 =
24 phase assignments and preserves each folio's class counts, run structure,
spacing, and page order.  Ties use tolerance 1e-15.

## Controls and confirmation gates

Before the target, the scorer must:

1. enumerate exactly 24 unique phase assignments;
2. recover a distributed two-folio class plant at unique rank 1;
3. reject a one-folio plant through the both-folio gate;
4. reject third-reading disagreement;
5. reject a pure within-folio ordinal-distance profile;
6. preserve score/rank under simultaneous class complementation and positive
   affine transformations of every reading/view matrix.

Target confirmation requires all of:

- unique inclusive rank 1 of 24 (exact p=1/24);
- positive score in every alternate reading;
- positive f67 and f68 contribution in every alternate reading;
- after deleting each of the eight views in turn, rank at most 2/24 and every
  reading and folio contribution remains positive.

No view, page, folio, reading, feature, group, or spelling may be selected
after the result.

## Claim ceiling

A pass establishes only that complete circular-text profiles align with the
public editorial astronomical/cosmological distinction at the correct phase
on f67/f68, beyond arbitrary cyclic placement of the unchanged class pattern.
It does not prove that the author used those categories; identify a sun, moon,
star, planet, sphere, zodiac sign, or diagram object; name a register; assign a
word, sound, language, plaintext, or translation.  Failure closes this fixed
panel and representation.
