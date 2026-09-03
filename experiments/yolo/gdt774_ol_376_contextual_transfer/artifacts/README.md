# GDT774 artifacts

- `OL_376_TRANSFER_ATLAS.tsv`: canonical 376-occurrence automatic/hybrid
  dispatch ledger, including signals, precedence, confidence, calibration,
  repetition, legacy crosswalk, and claim-credit fields.
- `TRANSFER_BRANCH_SUMMARY.tsv`: rule/output counts for both renderers.
- `AMOUNT_17_EDGE_AUDIT.tsv`: all seventeen directed amount edges, including
  the bilateral pair and two line-final exclusions.
- `CALIBRATION_REPLAY_AUDIT.tsv`: automatic 9/15 and hybrid 15/15 replay of the
  fixed GDT773 outputs.
- `DIRECT_SIGNATURE_DIRECTION_SUMMARY.tsv`: right/left process and close
  signatures, state signatures, and the signalless remainder.
- `F15_STATE_BRIDGE_AUDIT.tsv`: all 31 state bridges, transition directions,
  priority overlaps, vetoes, and final outputs.
- `LINE_POSITION_REPEAT_AUDIT.tsv`: position, paragraph, repetition, F14/F15,
  and direct-signature counts against the final dispatch.
- `ADJACENT_OL_PAIR_AUDIT.tsv`: the seven `ol ol` pairs; all fourteen tokens
  remain nominal and signalless.
- `REGISTER_DISPATCH_SUMMARY.tsv`: section and hand splits for position,
  repetition, signal, and automatic/hybrid output.
- `PHYSICAL_FOLIO_TRANSFER_SUMMARY.tsv`: all 61 physical-folio partitions.
- `LEGACY_GRUNDANSATZ_COMPARISON.tsv`: guarded GDT683 inheritance versus the
  automatic and hybrid contextual/fallback split.
- `MANUAL_24_CONTEXT_AUDIT.tsv`: deterministic contrast audit with explicit
  zero independent semantic score credit.
- `GDT774_WORKING_DICTIONARY.tsv`: every selected output with occurrence count,
  confidence, evidence, counterevidence, and scope.
- `RESULT.json`: machine-readable decisions, source hashes, counts, structural
  audit, scope, and claim ceiling.
- `VALIDATION.json`: independent reconstruction, safety checks, and
  byte-identical runner/report replay.

`structural_audit/` contains the separate 20,000-draw analysis:

- `OL_376_STRUCTURAL_POSITION_ATLAS.tsv`;
- `OL_DIRECT_SIGNATURE_DIRECTION_MATRIX.tsv`;
- `OL_EVIDENCE_VENN_DISPATCH.tsv`;
- `OL_SELF_REPEAT_ATLAS.tsv`;
- `OL_NEIGHBOR_SURFACE_SUMMARY.tsv`;
- `OL_REPEATED_NEIGHBOR_FRAMES.tsv`;
- `OL_REGISTER_SUMMARY.tsv`;
- `OL_FOLIO_HOLDOUT.tsv`;
- `OL_POSITION_MATCHED_NULL.tsv`;
- `STRUCTURAL_AUDIT_RESULT.json`.

All German text is a replaceable working renderer. Structural roles are not
translations, and all lexeme/plaintext/component credits remain zero.
