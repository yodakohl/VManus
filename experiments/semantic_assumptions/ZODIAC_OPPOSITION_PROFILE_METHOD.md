# ZODIAC_OPPOSITION_PROFILE — frozen source-native design

Date frozen: 2026-08-10, before computing any whole-profile opposition score.

## Question

Do the complete circular-text profiles align with the externally known
opposition relation of the public zodiac emblems?  The four fully visible
opposition pairs are:

- Pisces--Virgo;
- Aries--Libra;
- Taurus--Scorpio;
- Gemini--Sagittarius.

Cancer--Capricorn and Leo--Aquarius are excluded because the latter sign pages
are missing.  Aries combines its two 15-figure pages, as does Taurus.  Each
other sign contributes its single 30-figure page.  Sign identities come only
from the corrected public voynich.nu illustration descriptions; tentative
identifications are not used.

## Frozen target representation

- score IVTFF `C` circular loci only;
- use all zero-alternative source-native STA groups;
- score ZL3b, IT2a, and RF1b separately;
- use eight fixed views: family n-grams 2--5, exact member n-grams 1--3, and
  complete family-group surfaces;
- aggregate all pages of one sign before comparison;
- pair similarity is deterministic weighted Jaccard.

For each reading/view, standardize all 28 pair similarities across the eight
sign profiles with population mean and standard deviation.  A matching score
is the mean standardized similarity over its four pairs and eight views.  The
primary statistic is the weakest of the three reading scores.  Enumerate all
105 perfect matchings exactly; ties use a 1e-15 tolerance.

## Controls and gates

Before the target run, the scorer must:

1. recover a distributed four-pair plant at unique rank 1;
2. reject a constant null as ineligible;
3. reject a one-pair plant by the pair-support gate;
4. reject a plant whose third reading favors a different matching;
5. preserve results under positive affine transformation of each
   reading/view matrix and under simultaneous sign relabeling.

Target confirmation requires all of:

- exact p <= .05 in the complete `C` profile;
- positive matching score in every reading;
- at least three of four opposition-pair contributions positive in every
  reading;
- the same p, reading-direction, and support gates after removing every group
  whose family surface ends in `BABA`;
- after deleting each opposition pair, the remaining three-pair matching ranks
  at most 2 of 15 in the weakest reading, with every reading score positive.

The `BABA` deletion was frozen because the route was motivated by the observed
`okeodaly`/`sheodaly`/`okeedaly` family.  It cannot be used as positive evidence.
Label-role (`L`) profiles are a diagnostic sensitivity only and cannot rescue
a failed circular-text result.

## Claim ceiling

A pass would establish only aggregate source-native profile alignment with the
known zodiac opposition relation.  It would not identify a specific sign,
opposition word, sign name, month, day, astrological doctrine, language, sound,
plaintext, or translation.  Failure closes this fixed whole-profile route;
individual pairs, views, readings, groups, and spellings may not be mined.
