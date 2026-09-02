# Artifacts

- `A3_17_TARGETS.tsv`: fixed GDT745 candidate deck.
- `SURFACE_63_OCCURRENCE_FEATURES.tsv`: all 1,523 selected cached occurrences
  with section, line, flanks and closure features.
- `CALIBRATION_782_CANDIDATE_KNOWN_SCORES.tsv`: every candidate against every
  known comparison whole; needed to audit ranks and non-direct alternatives.
- `PAIR_52_DISTRIBUTION_SCORES.tsv`: the selected edit-distance-one relations.
- `CANDIDATE_17_DISTRIBUTION_CENSUS.tsv`: consolidated meanings, evidence and
  counterevidence.
- `GDT746_WHOLE_DISTRIBUTION_READER.md`: human-readable complete card set.
- `GDT746_GDT388_*`: executable relation intake and its expected invalid result.
- `RESULT.json`, `VALIDATION.json`: compact machine summaries.

The 1,523-row occurrence file and 782-row calibration matrix are retained
because they are the minimal auditable source of the reported pair ranks and
the section-removed sensitivity.
