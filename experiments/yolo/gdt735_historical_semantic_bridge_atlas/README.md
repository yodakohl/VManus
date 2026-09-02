# GDT735 — historical semantic bridge atlas

GDT735 compares late-medieval pharmaceutical record architectures with the
current working reader without treating modern EVA transcription labels as
medieval letters. The selected historical prior has two separate channels:

- **descriptive:** learned lemma, optional part or substance form,
  quality/state, and degree;
- **prescriptive:** command, ingredient or preparation, amount, unit, and
  process/result.

This is architectural evidence, not decipherment. The inherited target grid
has 96 unique forms over 24 complete bodies, balanced 24 times under each
opaque head `H1–H4`. EVA provenance is stored separately and receives zero
letter, phonetic, Latin-initial, relation, or semantic-identification credit.

All 24 assignments of `PULVIS`, `SEMEN`, `RADIX`, and `LIGNUM` to `H1–H4` tie
on target structure. Two deliberately weak OCR frequency controls do not break
that tie: the rejected EVA-initial mnemonic ranks 20/24 in each source and the
best assignment changes by source. No actual four-head code is found.

The historical decks contain 22 deduplicated sources, 17 compact observations
(nine descriptive, six prescriptive, two mixed-reference), and 28 OCR
field-count rows. Wellcome MS.542 is the strongest direct bridge because the
same manuscript contains both descriptive drug/part/quality/degree entries and
prescriptive commands with counted units. It maps no Voynich form.

## Model dispositions

| Model | Disposition |
| --- | --- |
| M01 EVA initialism | rejected, nonselectable negative control |
| M02 all 24 permutations | nonidentifying label diagnostic |
| M03 whole + quality | directly attested descriptive submodel |
| M04 two-record hybrid | selected historical content prior |
| M05 value ladder | retained; value dimension unresolved |
| M06 mixed abbreviation FST | selected general architecture |
| M07 atomic wholes | retained learned-name fallback |
| M08 H4 liquor/extract | unresolved opaque-role diagnostic |

## Reproduce

From the repository root:

```bash
python3 experiments/yolo/gdt735_historical_semantic_bridge_atlas/src/run.py
python3 experiments/yolo/gdt735_historical_semantic_bridge_atlas/src/validate.py
```

The first command regenerates the compact artifacts, `REPORT.md`, and
`RESULT.json`; the second is the manifest-declared independent validation
entry point. Source specifications are under `src/`; generated outputs are
under `artifacts/`.

## Claim ceiling

`TWO_CHANNEL_PHARMACEUTICAL_ARCHITECTURE_ATTESTED; MIXED_WHOLE_PLUS_BOUND_FIELD_MODEL_SELECTED; FOUR_HEAD_SEMANTICS_UNIDENTIFIED; EVA_INITIALISM_REJECTED; ZERO_LEXEME_OR_GLYPH_IDENTIFICATIONS; NO_NEW_PAGE`.
