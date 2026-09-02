# GDT735 method

## Question

Can an attested late-medieval pharmaceutical record architecture organize the
current 96-form four-head grid without identifying any EVA label as a
historical letter, Latin initial, sound, or lexeme?

## Inputs

The already admitted GDT635/GDT636 grids and GDT635 head profile yield 96
unique forms on 24 complete shared bodies, balanced as 24 cells under each
opaque head `H1–H4`. They contain 1,166 inherited occurrences, of which 875 are
surface-exact in the alternate-reader accounting.

Human-authored GDT735 inputs are:

- `HISTORICAL_SOURCE_REGISTRY.tsv`: 22 deduplicated sources;
- `HISTORICAL_ENTRY_OBSERVATIONS.tsv`: 17 descriptive, prescriptive, or
  mixed-reference observations;
- `HISTORICAL_FIELD_COUNTS.tsv`: 28 rows in two weak OCR frequency decks;
- `BRIDGE_MODEL_SPECS.tsv`: eight architectures with costs, falsifiers, and
  claim ceilings;
- `SEMANTIC_ROLE_SEEDS.tsv`: sixteen broad distributional seeds, literal
  values unresolved and component-export credit zero.

No new page, image, transcription, `f84`, or `f84r` is used.

## Opaque target construction

The runner replaces the four source labels by `H1–H4`; `H_EVA_P/S/R/L` are
retained only as modern transcription provenance. Every row has unresolved
literal head lexeme, EVA-initial credit 0, and relation credit 0. Inherited
body roles remain working roles, not newly confirmed meanings.

## Twenty-four-way diagnostic

All `4! = 24` assignments of the historical labels `PULVIS`, `SEMEN`, `RADIX`,
and `LIGNUM` to `H1–H4` are enumerated. Every assignment explains the same 96
structural cells, hence tie size 24.

For two OCR slices, total-variation distance compares target head frequencies
with historical word-mention frequencies. OCR mentions are neither entries nor
relations, and the sources were inspected during reconnaissance. The ranks are
therefore only a weak negative control. No rank earns mapping credit.

M01—the former mnemonic `p→pulvis, s→semen, r→radix, l→lignum`—is an invalid
anachronistic initialism and is ineligible for selection regardless of score.
M02 retains all 24 ranks solely as label-compatibility diagnostics.

## Historical atlas and two channels

The 17 observations are joined to the 22-source registry, classified by
evidence tier, and separated into:

- a descriptive channel of lemma/synonym, part or substance form,
  quality/state, and degree;
- a prescriptive channel of command, ingredient/preparation, amount, unit,
  and process/result.

Index and cross-reference fields remain distinct. Wellcome MS.542 is the
direct same-manuscript bridge: it contains descriptive learned-name or named-
part entries with qualities/degrees and prescriptive commands with counted
drops. This attests coexistence of channels, with Voynich mapping credit 0.

The atlas separately checks for an actual interchangeable four-head
one-letter material code. None occurs in the 22-source registry.

## Model dispositions

M01 is rejected as a nonselectable negative control. M02 remains a
nonidentifying 24-way diagnostic. M03 is a directly attested descriptive
submodel. M04 is the selected two-record content prior. M05 retains ordered
values but no fixed dimension. M06 is the selected mixed-whole/bound-field
architecture. M07 remains necessary for memorized names. M08 leaves H4
unresolved among wood, liquor, extract, liquid, weight, and a neutral binder.

Selection means “best historical architecture prior,” never plaintext. All
component-export, relation, EVA-initial, glyph, sound, and lexeme credits stay
zero.

## Generated products and assertions

The runner asserts deck sizes 22/17/28, model/seed sizes 8/16, the balanced
96-cell grid, exactly two OCR datasets, zero historical relation credit, zero
component export, and zero permitted literal lexeme claims. It generates the
compact TSV products documented in `artifacts/README.md`, plus `REPORT.md` and
`RESULT.json`.

Reproduce:

```bash
python3 experiments/yolo/gdt735_historical_semantic_bridge_atlas/src/run.py
python3 experiments/yolo/gdt735_historical_semantic_bridge_atlas/src/validate.py
```

## Decision rule and claim ceiling

Historical evidence may retain only directly observed field architectures
that require no EVA-to-letter mapping. Target head semantics remain
unidentified while the structural 24-way tie persists or a role requires
literal or neighbor import.

Maximum claim:

`TWO_CHANNEL_PHARMACEUTICAL_ARCHITECTURE_ATTESTED; MIXED_WHOLE_PLUS_BOUND_FIELD_MODEL_SELECTED; FOUR_HEAD_SEMANTICS_UNIDENTIFIED; EVA_INITIALISM_REJECTED; ZERO_LEXEME_OR_GLYPH_IDENTIFICATIONS; NO_NEW_PAGE`.
