# Artifacts

The builder writes the complete reproducible GDT641 release:

- `TARGET_DECISION_DECK.tsv`: the two frozen targets, rivals and decisions.
- `FORM_FAMILY_ATLAS.tsv`: observed TCH/E/OL/OR and CHE/CHO sister cells.
- `COMPONENT_BINDING_AUDIT.tsv`: visible component trace and source for each
  target.
- `ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv`: all seven target occurrences.
- `SEQUENTIAL_DECISION_LEDGER.tsv` and `ROUND_COVERAGE_COUNTS.tsv`: immutable
  before/after state per promotion.
- `ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv`: the exact-only V18 additions.
- `NEWLY_COMPLETED_LINES.tsv`: literal and smoothed readings of f15r.12 and
  f37v.8.
- `V18_EXACT_TOKEN_GLOSSARY.tsv`, `WORKING_DICTIONARY_V18.tsv` and the full V18
  coverage/complete/one-hole editions.
- `RESULT.json` and `VALIDATION.json`: hashes, counts, guards and independent
  replay status.

The full 4,128-line coverage tables are retained because the release validator
byte-replays them and because downstream experiments consume them as the V18
prefix.
