# GDT212 — readable bath illustration/text grounding calibration

## Question

In a readable illustrated medieval bath book, which broad textual information
roles are actually recoverable from the accompanying pictures?  This calibrates
what q13 geometry can and cannot plausibly ground before any further Voynich
host is interpreted.

## Sources and mapping

The visual source is the Morgan Library's public human catalogue for MS G.74,
*De balneis Puteolanis*, Italy, ca. 1400.  The official page descriptions name
the depicted bath and describe visible scene elements.  Thirty-two catalogue
pages map by bath title and sequence to the 32 readable bath entries frozen in
GDT211.  Morgan fol. 32r is a non-bath page; fols. 33r–34r contain three
additional baths absent from the ALIM sequence and are excluded; fol. 34v maps
to GDT211 entry 33, *De Cruce*.

Every mapping, catalogue URL, folio, normalized flag, and short neutral evidence
summary is frozen in `gdt212_morgan_visual_role_inventory.tsv`.  The
normalization is a post-hoc exploratory human-catalogue normalization, not a
blinded annotation and not direct image evidence.  The four images previously
opened in GDT210 add no independent sample.

## Visual variables

The Morgan prose is reduced to five visible, nonsemantic categories:

- `ACCESS_OR_SETTING`: explicit cave, hillside, exterior source, stairs,
  approach/departure, tent, or other access/setting organization;
- `NON_GENERIC_WATER_SYSTEM`: explicit stream, fountain, well, spring, lake,
  sea, underground water, or flowing water beyond the generic bathing pool;
- `SPECIFIC_USE_ACTION`: an action beyond simply being in a bath, such as
  drinking, collecting, pouring, washing, testing, digging, undressing,
  pointing, or descending;
- `BODY_CONDITION_CUE`: bed/reclining, a named body-directed gesture, patch, or
  other explicit bodily-condition cue;
- `BED_OR_DEPARTURE_NARRATIVE`: a bed/reclining or approach/departure episode.

These categories state geometry/action only.  They do not assert illness,
treatment success, or iconographic meaning.

## Readable text roles

The role-presence flags are taken unchanged from the external GDT211 freeze:
`LOCATION_ACCESS`, `HYDRAULIC_PHYSICAL`, `INDICATION`,
`PROCEDURE_CAUTION`, and `OUTCOME_TESTIMONY`.  Identity and indication occur in
all 32 records, so identity has no binary recovery test and indication is
reported only as a visibility-capacity contrast.

Four predeclared directional pairs are scored:

1. `ACCESS_OR_SETTING -> LOCATION_ACCESS`;
2. `NON_GENERIC_WATER_SYSTEM -> HYDRAULIC_PHYSICAL`;
3. `SPECIFIC_USE_ACTION -> PROCEDURE_CAUTION`;
4. `BED_OR_DEPARTURE_NARRATIVE -> OUTCOME_TESTIMONY`.

For each pair report its 2x2 table, risk difference, smoothed odds ratio,
one-sided Fisher exact probability in the predicted positive direction, and a
leave-one-entry-out one-feature Bernoulli-naive-Bayes log-loss diagnostic.
The latter may exploit a reversed relationship and therefore cannot override a
negative directional effect.  Bonferroni adjustment covers the four pairs.

## Decision

- A role is `VISUALLY_GROUNDED_LEAD` only for positive risk difference and
  adjusted `p <= .05`.
- Positive direction without adjusted support is `WEAK_VISUAL_GROUNDING`.
- Zero or reversed direction is `NOT_VISUALLY_GROUNDED`.
- Constant text roles are `UNSCORABLE_CONSTANT_ROLE`.

The overall result is descriptive calibration.  It cannot translate Voynich
text and cannot transfer a role to a q13 label without separate ownership and
formal evidence.

## Seal

No Voynich target is scored.  No f84 source, row, image, annotation, or formal
payload is accessed.
