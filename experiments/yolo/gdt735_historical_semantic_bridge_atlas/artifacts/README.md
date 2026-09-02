# GDT735 generated artifacts

This directory contains generated compact results. Human-authored source decks
and model specifications live under `../src/` and are inputs, not generated
evidence summaries.

## Generated files

- `OPAQUE_96_HEAD_BODY_GRID.tsv` — balanced 96-cell target grid with EVA
  provenance separated from opaque `H1–H4`; literal and initial credit zero.
- `HEAD_FIELD_24_PERMUTATION_DIAGNOSTIC.tsv` — all 24 assignments, two OCR
  frequency distances/ranks, structural tie size 24, identification credit 0.
- `HISTORICAL_ENTRY_ATLAS.tsv` — 17 observations with evidence tier, channel,
  and Voynich mapping credit 0.
- `HISTORICAL_SOURCE_ARCHITECTURE_MATRIX.tsv` — per-source slot and channel
  summary, including the direct same-source bridge flag.
- `HISTORICAL_SLOT_CENSUS.tsv` — slot counts by rows, sources, and channel.
- `BRIDGE_MODEL_COMPARISON.tsv` — M01–M08 dispositions. M01 is ineligible;
  M02 is nonidentifying; M04/M06 are architecture selections only.
- `SEMANTIC_BRIDGE_ROLE_DICTIONARY.tsv` — broad role seeds and rivals, with
  literal, initial, and component-export credit zero.
- `BRIDGE_DECISION_REGISTER.tsv` — compact decisions and evidence.
- `RESULT.json` — counts, dispositions, claims, status, and hashes.

The human-facing generated `REPORT.md` is one directory above.

## Source/generated boundary

Inputs under `../src/` are the 22-row source registry, 17-row observation deck,
28-row OCR control deck, eight model specs, sixteen role seeds, and the runner
and validator entry points. OCR counts are weak descriptive controls, not
relations, and no generated file may turn them into a Voynich mapping.

## Reproduce and invariants

```bash
python3 experiments/yolo/gdt735_historical_semantic_bridge_atlas/src/run.py
python3 experiments/yolo/gdt735_historical_semantic_bridge_atlas/src/validate.py
```

Expected target invariants are 96 cells, 24 bodies, 24 cells per opaque head,
1,166 occurrences, and 875 exact-reader occurrences. Historical deck
invariants are 22/17/28. The 24 assignments remain structurally tied. All
lexeme, glyph, EVA-letter/initial, relation, and component-export claims remain
zero.

## Claim ceiling

The artifacts support only a two-channel historical architecture prior and a
mixed whole-plus-bound-field working model. They do not supply an actual
four-head code, plaintext, plant or ingredient identity, unit, EVA letter
value, sound, or translation.
