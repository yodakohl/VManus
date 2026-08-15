# GDT074 — section-excluded enclosure-class transport

Status: **YOLO fixed-predicate transport audit**

Audit the two exact enclosure-associated PAGE_HOST behavior predicates frozen
in GDT072 without retuning:

- `HCLASS_RAIIN_HIGH`: outside-target-section `R=aiin` rate at least 0.25;
- `HCLASS_FO_ACTIVE`: outside-target-section `F=O` rate at least 0.10.

Use only the two sections with GDT073 enclosure capacity, A and Z.  For each
target section, rebuild each host rate from all source events outside that
section and require each host to occur on at least two outside-section physical
folios.  Evaluate the fixed predicate against archived `REL_ENCLOSURE` within
physical-folio×human-unit strata.  Export all feature-positive examples and
counterexamples.  A predicate transports only if its conditional direction is
positive in both sections.  This is a postselected transport audit because the
predicates and archived relation axis arose in GDT069; it does not consume or
confirm the prospective GDT072 tests.  No alternative threshold, relation,
gloss, parser, or target is searched.  f84r is excluded.
