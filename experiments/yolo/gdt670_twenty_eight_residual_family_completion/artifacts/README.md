# GDT670 artifacts

The artifact set is generated deterministically by `src/run.py`; `RESULT.json` records SHA-256 hashes for all builder inputs and generated outputs.

## Primary results

- `RESULT.json` — status, dimensions, hashes, architecture, coverage, and claim boundary.
- `FRONTIER_28_COMPLETIONS.tsv` — one completed source-frontier row per target form.
- `TARGET_DECISION_DECK.tsv` and `ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv` — final card decisions.
- `ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv` — all 91 target positions.
- `FAMILY_COMPOSITION_ATLAS.tsv` and `CARD_ARCHITECTURE_SUMMARY.tsv` — family and 25-composed/3-learned summaries.
- `READER_VARIANT_AUDIT.tsv` and `CONTEXT_RENDERING_CARDS.tsv` — reader evidence, including local `ka ar → karar`.

## V47 register and coverage

- `V47_WORKING_TOKEN_GLOSSARY.tsv` and `WORKING_DICTIONARY_V47.tsv` — 1,415 glossary surfaces and 2,100 dictionary entries.
- `ALL_LINE_CONCRETE_COVERAGE_V47.tsv` — all 4,128 physical lines.
- `COMPLETE_PASSAGES_V47.tsv` — 1,223 complete multi-token lines.
- `ONE_UNKNOWN_PASSAGES_V47.tsv` — 154 one-unknown lines.
- `ROUND_COVERAGE_COUNTS.tsv`, `NEWLY_COMPLETED_LINES.tsv`, `NEWLY_EXPOSED_ONE_HOLE_LINES.tsv`, and `NEXT_FRONTIER_FULL_PANEL_COUNTS.tsv` — V46→V47 changes and the next frontier.

## Render and passage audits

- `TARGET_LINE_TRANSLATIONS.tsv` — deterministic affected-line renderings.
- `MANUAL_PASSAGE_AUDIT.tsv` — 20 corrected manual workshop readings, separate from automatic renderings.
- `INHERITED_OL_RENDER_REVISIONS.tsv` and `INHERITED_SOL_RENDER_REVISIONS.tsv` — inherited specifications, not new GDT670 revisions.
- `STEM_MODEL_V47.tsv` — unchanged 56-role model.
- `PAGE_ALLOWLIST.tsv` — exact 179-page safe panel.

All meanings are exploratory working defaults, not confirmed plaintext.
