# Artifacts

- `Q_44_OUTER_MICROFIELD_AUDIT.tsv`: every fixed q/base contact, both clipped
  outward fields, anchors, raw candidates, complete-field decisions and safe
  renderer flags.
- `CONTROL_42_OUTER_MICROFIELD_AUDIT.tsv`: identical audit for every direct
  contact in the fixed non-q control universe.
- `SIDE_ROLE_GROUP_COMPARISON.tsv`: compact 44-versus-42 comparison.
- `Q_PAIR_TYPE_ROLE_CENSUS.tsv`: twelve q/base pair-type summaries.
- `OKEEY_13_LOCAL_CARRIER_REVIEW.tsv`: all thirteen `qokeey/okeey` contacts and
  the disposition of the ten GDT751 carrier cards.
- `GDT752_Q_BASE_MICROFIELD_READER.md`: compact human reader.
- `GDT752_GDT388_SIDE_ROLE_EDGE_PACKET.tsv` and
  `GDT752_GDT388_EDGE_INTAKE.json`: executable relation-readiness record. The
  sole symmetric complete case is intentionally invalid/not score-ready after
  formal semantic access.
- `RESULT.json`: machine summary and claim boundary.
- `VALIDATION.json`: independent invariants and byte replay certificate.

The complete 44- and 42-row tables are retained because negative and censored
contacts are necessary to reproduce the directional comparison and prevent
later cherry-picking of the lone q lead.
