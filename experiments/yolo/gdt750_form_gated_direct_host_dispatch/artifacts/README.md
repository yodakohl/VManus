# GDT750 artifacts

- `RULE_VARIANT_CALIBRATION.tsv`: all six rules on 1,134 known occurrences.
- `KNOWN_1134_OCCURRENCE_CALIBRATION.tsv`: occurrence-level TP/FP evidence.
- `FORM_17_PRIOR_DECK.tsv`: complete-surface distance-one/two votes for the
  fixed target deck.
- `TARGET_1684_HOST_DISPATCH_AUDIT.tsv`: every target position, including
  discovery and reader-agreement flags and silent alternatives.
- `ACTIVE_OCCURRENCE_CARDS.tsv`: the nineteen licensed outside cards.
- `ACTIVE_HOST_CONTACTS.tsv`: the exact host supporting each active card.
- `FORM_17_DISPATCH_PROFILE.tsv`: compact decisions for all seventeen forms.
- `GDT750_FORM_GATED_HOST_READER.md`: readable active passages and calibration.
- `GDT750_GDT388_HOST_EDGE_PACKET.tsv` and
  `GDT750_GDT388_EDGE_INTAKE.json`: executable relation intake; it is invalid
  only because formal access is deliberately unsealed.
- `RESULT.json`: machine-readable scope, calibration and form profiles.
- `ROUTE_FEASIBILITY.json`: reproducible post-result comparison of three
  successor routes; this is navigation rather than primary score evidence.
- `VALIDATION.json`: invariant, edge-gate and byte-replay certificate.

The two large occurrence tables are retained because they expose every
negative position, discovery exclusion and calibration prediction needed to
reproduce the narrow zero-false-positive result.
