# Artifacts

- `V87_COMPLETE_WORD_CONFIDENCE.tsv`: canonical 1,582-surface,
  1,586-reading dictionary with score, level, positive evidence,
  counterevidence and historical status on every row.
- `V87_324_ACTIVE_LEXICAL_READINGS.tsv`: active compact cores, local
  realizations, decompositions, confidence and export scopes.
- `V87_479_CONTEXT_REALIZATIONS.tsv`: all admitted positions, including the
  occurrence-local LEFT/RIGHT boundary decision and one-shot rendering.
- `V87_18_BOUND_C1_CORE_CONTEXT_DELTA.tsv`: the eighteen old/new cores,
  contexts, scores, evidence, counterevidence and open slots.
- `V87_109_HELD_READING_AUDIT.tsv`: cumulative queue with eighteen V87
  revisions and 91 readings left for later repair.
- `V87_7_FAMILY_EVIDENCE.tsv`: only the seven existing family rules used in
  this tranche.
- `V87_2_BOUND_SPAN_RENDERER.tsv`: inherited G683 span plus the new local
  G678 f7r.2 `keo r` one-shot span.
- `V87_1_BOUNDARY_DELTA.tsv`: full evidence and counterevidence for that one
  newly executable boundary decision.
- `V87_18_PRIMARY_EVIDENCE_BINDINGS.tsv`: one exact pre-GDT714 source row per
  target, including bound decomposition, counts, reader fields and the family
  IDs actually allowed to contribute score.
- `V87_2_ONE_SHOT_RENDER_DIRECTIVES.tsv`: the two consumer actions: P288 emits
  the span once and P289 emits nothing; both source contexts are consumed.
- `V87_8_F7R2_RENDERED_UNITS.tsv`: the actual eight-unit f7r.2 output after
  consuming the nine source positions through that span.
- `RESULT.json` and `VALIDATION.json`: compact distributions and the
  deterministic replay certificate.
