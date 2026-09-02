# GDT755 artifacts

- `TOP24_448_OCCURRENCE_FIELDS.tsv`: all reader-exact target positions and independently anchored radius-five fields, with suspect GDT754 neighbour axes excluded.
- `TOP24_CHANNEL_CENSUS.tsv`: placement, section and complete-field channel profile for every target whole.
- `EXACT_FORM_INITIAL_POSITION_COMPARATOR.tsv`: all 373 reader-exact surfaces with at least ten occurrences ranked by line-initial rate, without semantic features.
- `TOP24_CANDIDATE_RANKING.tsv`: three historical candidates per target with role, channel, layout, date, content-axis, evidence and counterevidence diagnostics.
- `TOP24_WORKING_GLOSS_UPDATE.tsv`: one selected concise German candidate, confidence, evidence and two rivals per complete form.
- `CONCRETE_VOCABULARY_SLOT_AUDIT.tsv`: explicit slot inventory for water, wine, oil, salt, plant parts, processes, person, disease, vessel and preparation concepts.
- `TOP24_448_CANDIDATE_RENDERER.tsv`: occurrence-level candidate render plus an EVA-preserving hybrid line.
- `GDT755_HISTORICAL_REGISTER_READER.md`: compact human table, principal changes, slot audit and sixteen hybrid examples.
- `RESULT.json`: machine-readable scope, confidence counts, strongest lead, controls and claim boundary.
- `VALIDATION.json`: invariant and byte-identical replay certificate.

The 448-row occurrence and renderer tables are retained because the reader must be able to verify that every candidate is attached only to an enumerated reader-exact complete form and that all 172 suspect compound meanings were excluded from external-field anchoring.
