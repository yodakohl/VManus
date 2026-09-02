# Artifacts

- `MATCHED_11_PAIR_CONTROL_DECK.tsv`: target plus five q/base and five non-q
  pairs selected without semantic or role outcomes.
- `TARGET_AND_CONTROL_OCCURRENCE_FIELDS.tsv`: all 803 target-centred fields,
  including negative and censored cases.
- `SURFACE_22_ROLE_CENSUS.tsv`: complete-field role counts for every surface.
- `PAIR_11_ROLE_COMPARISON.tsv`: identical directional test for all eleven
  pairs.
- `INHERITED_ROLE_PROVENANCE_AUDIT.tsv`: exact GDT664/GDT666 source cards and
  the current renderer disposition.
- `QOKEOL_OKEOL_75_OCCURRENCE_READER.tsv`: every target occurrence with old
  prose, corrected whole default and separately labelled external context.
- `GDT753_QOKEOL_OKEOL_ROLE_READER.md`: compact human result.
- `RESULT.json`: machine scope, gate, provenance and renderer correction.
- `VALIDATION.json`: invariant and byte-replay certificate.

The full 803-row table is retained because the negative and radius-censored
fields are necessary to reproduce the comparison and prevent selecting only
the attractive f99v.22 lead.
