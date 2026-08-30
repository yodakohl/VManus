# GDT669 artifacts

The directory is the deterministic V46 output of `src/run.py`. The main run
and a fresh temporary-directory replay were byte-identical.

Key files:

- `RESULT.json`: status, hashes, coverage, dictionary arithmetic, architecture,
  guards, manual-passage counts, and the next frontier.
- `TARGET_DECISION_DECK.tsv` and `ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv`: the 37
  ordered cards, meanings, compositions, rivals, counts, and card types.
- `ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv`: all 165 target occurrences with reader
  evidence and V45/V46 readings.
- `READER_VARIANT_AUDIT.tsv`: aligned ZL3b/IT2a/RF1b boundary evidence,
  including the two alias wholes and short-form merges.
- `FRONTIER_37_COMPLETIONS.tsv`: closure of every source-frontier row.
- `MANUAL_PASSAGE_AUDIT.tsv`: twenty source-exact manual workshop readings kept
  separate from the automatic renderer.
- `V46_WORKING_TOKEN_GLOSSARY.tsv` and `WORKING_DICTIONARY_V46.tsv`: 1,387
  glossary surfaces and 2,071 dictionary entries.
- `ALL_LINE_CONCRETE_COVERAGE_V46.tsv`, `COMPLETE_PASSAGES_V46.tsv`, and
  `ONE_UNKNOWN_PASSAGES_V46.tsv`: full guarded-panel coverage products.
- `NEWLY_EXPOSED_ONE_HOLE_LINES.tsv` and
  `NEXT_FRONTIER_FULL_PANEL_COUNTS.tsv`: the next 28-row/28-form frontier.
- `STEM_MODEL_V46.tsv`: the 56-role sheet, including scoped `OY_PREP_BASE` and
  `OKY_HOT_PREP_BASE`.
- `VALIDATION.json`: the independent 5,425-check guarded source, hash, replay,
  scope, and privacy validation.

Compact totals: 165 target positions; 23,997 known and 8,342 unknown token
positions; 1,191 complete multi-token lines; 170 one-hole lines; 35 productive
cards, two learned aliases, and twelve local rendering cards.
