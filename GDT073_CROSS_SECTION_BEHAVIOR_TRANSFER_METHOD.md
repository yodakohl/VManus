# GDT073 — cross-section PAGE_HOST behavior transfer

Status: **YOLO postselected transfer audit**

Test whether the fixed GDT068 `SELF+NEIGHBOR` PAGE_HOST behavior profile without
position transfers an archived external axis into a completely different
manuscript section.  Restrict the test family to the three axes that had mixed
capacity in at least two sections in GDT070: `REL_ENCLOSURE`,
`REL_EXPLICIT_ATTACHMENT`, and `REL_ARRAY_OR_GROUP`.

For each target section, rebuild every PAGE_HOST behavior profile using source
events from other sections only.  Retain a target locus only when each of its
hosts occurs on at least two physical folios outside the target section.  Train
the low-capacity five-neighbour predictor only on annotated loci in other
sections.  Compare raw-character trigrams, PAGE_HOST-character trigrams, and
the fixed behavior profile against the identical nuisance predictor.  The
nuisance coordinates are annotation kind, unit, group count, and annotation
certainty; section, Currier, hand, folio, locus, and literal family identity are
not predictors.

Require each target cell and its cross-section training pool to contain at
least ten observations, at least three positives and negatives, and at least
two positive and negative physical folios.  Report every eligible cell and
target folio.  This is an archived-axis, postselected stress test, not
independent semantic validation.  It assigns no role or meaning.  f84r is
excluded before source events or annotations are retained.
