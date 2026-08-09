# DIRECTIONPLACEMENT001 source and method freeze

Date: 2026-08-09

## Claim and source ceiling

Test whether reusable formal morphology is associated with labels that the
human source explicitly describes east versus west of a nearby illustrated
object. The source establishes geometric placement only. It does not establish
ownership, and the labels are not assumed to say EAST or WEST.

The admitted source is the validated 57-locus horizontal panel from
`DIRECTIONPLACEMENT001` capacity. OCR, automated/neural vision, image
measurement, AI plant identity, and inferred geometric ownership are banned.
ZL3b, IT2a, and RF1b are alternate readings of one manuscript.

## Source-order-balanced exact pairs

Within each frozen exact page/code/object stratum, sort EAST and WEST loci by
natural locus order. Retain every member of the smaller class. Select the same
number from the larger class at evenly spaced inclusive ranks; for a one-item
minority use the lower median. Pair the selected lists in rank order. This is
source-only and cannot inspect a Voynich string.

The rule yields 16 pairs / 32 loci on six physical folios. Pair sides are
assigned A/B by the published SHA-256 ordering key
`DIRECTIONPLACEMENT001|pair_id|source_locus`; the masked pair file contains no
direction class. Controls may read only that masked file and the interlinear.
The observed direction binding is forbidden until one separately authorized
target invocation.

## Frozen representation

For each locus and reading, preserve space-delimited tokens and build three
separate formal domains.

- LIT: exact complete tokens and proper within-token prefixes, suffixes, and
  infixes of lengths 2--4.
- ROOT: exact parsed root tuples, first/last atoms, atoms, and adjacent atom
  bigrams.
- ROLE: exact formal role paths, first/last roles, roles, and adjacent role
  bigrams.

Structural ROOT/ROLE features remain formal categories, never English words or
parts of speech. A feature must occur in all readings, at least four token
instances and four physical folios per reading. Proper literal fragments must
occur in at least three distinct complete containing token types per reading.
It must also have nonzero within-pair variation and nonzero exact-orbit scale
in every reading and both views; a constant or unreadable feature is excluded
without reference to the observed direction.

Each locus has two frozen views. RAW is the fraction of domain tokens carrying
the feature. LENGTH_ADJUSTED subtracts the source-blind expected count given
complete token length (literal character count or ROOT/ROLE atom count), then
divides by domain-token count. This preserves whitespace while preventing a
generic long-label effect from masquerading as morphology.

## Exact paired inference

Enumerate every one of the `2^16 = 65,536` synchronized A/B swaps. Within each
physical folio average its pair differences, then average the six folios
equally. Standardize each feature over the exact orbit. The robust two-sided
score is the same-direction minimum standardized effect across ZL/IT/RF; an
alternate-reading sign disagreement scores zero. At each assignment, the
family null is the maximum over all frozen features. All tails are inclusive.

## Mandatory prescore controls

Before target access, controls and a nonimporting validator must reconstruct
the exact input bindings, 32-locus/96-row contract, feature list and matrices,
all 65,536 swaps, folio equal weighting, two-sided complement tie, inclusive
tails, reading-disagreement collapse, pair-constant cancellation,
length-only cancellation, a cross-context planted signal, rejection of a
one-folio signal, duplicate/missing/side-drift row guards, determinism, and
absence of a target artifact. The control artifact must state that no observed
direction assignment was extracted.

## Frozen target gates

A candidate must pass all of:

1. LENGTH_ADJUSTED exact familywise `p <= .025`;
2. RAW exact familywise `p <= .05`;
3. one common direction in every reading and both views;
4. minimum absolute adjusted and raw effect at least `.10`;
5. enriched-side presence on at least four of six folios in every reading;
6. the adjusted feature has the same nonzero direction on at least five of six
   individual folios in every reading;
7. both non-pharmaceutical folios (f68 and f88) have that same nonzero
   adjusted direction in every reading;
8. the adjusted direction survives deletion of every physical folio in every
   reading;
9. every one-folio-deletion adjusted familywise tail is `p <= .05`.

No feature, threshold, pair, nuisance adjustment, direction, or gate may
change after target access.

## Interpretation

Failure closes only this fixed placement-association test. Even a pass would
show recurrent morphology associated with described horizontal placement; it
could reflect layout or scribal practice. It would not alone establish an
EAST/WEST word, ownership, a lexeme, plaintext, language, or translation.
