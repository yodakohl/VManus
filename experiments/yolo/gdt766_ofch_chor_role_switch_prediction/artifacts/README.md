# GDT766 artifacts

The builder emits 21 TSV tables plus `RESULT.json`; the validator adds
`VALIDATION.json`. The principal result files are:

- `OFCH_CORE_43_OCCURRENCE_ATLAS.tsv` and
  `OFCH_CORE_25_FORM_PROFILE.tsv`: full exact complete-word census;
- `OFCH_22_MATCHED_GEOMETRY_CONTROL.tsv`: per-target frequency/section control
  pools, with the aggregate in `OFCH_22_MATCHED_CONTROL_SUMMARY.tsv`;
- `CHOR_ROLE_191_OCCURRENCE_ATLAS.tsv`, `CHOR_ROLE_4_PROFILE.tsv` and
  `CHOR_PCHOR_GEOMETRY_CONTRAST.tsv`: complete-word role separation;
- `OFCH_REPRODUCTIVE_4_BRIDGE_ATLAS.tsv` and the GDT388 packet: four
  explicitly non-score-ready same-line contacts;
- `OFCH_25_WORKING_DICTIONARY.tsv`,
  `CHOR_ROLE_4_WORKING_DICTIONARY.tsv` and
  `CONCRETE_WHOLE_CANDIDATE_TOURNAMENT.tsv`: portable, bold and rival whole
  readings with evidence and confidence;
- `FIVE_COMPLETE_LINE_WORKING_READER.tsv`: five lines and all 46 exact tokens;
- `FAMILY_DERIVATION_QUARANTINE.tsv`: removed action, root and head-noun leaks.

Every table is deterministically rebuilt and byte-compared by `src/validate.py`.
