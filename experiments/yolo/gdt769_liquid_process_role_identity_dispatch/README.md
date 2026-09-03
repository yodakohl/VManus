# GDT769 — liquid process role identity dispatch

Status: `PASS`. All 17 builder artifacts are present; 26,743 independent checks and byte-identical replay of all 17 outputs pass.

GDT769 asks which structural roles best fit five exact complete forms and then supplies conservative, context-sensitive German reader defaults. It does not derive meanings from EVA letters or substrings and does not claim a decipherment.

## Current provisional answer

| Target | Role/default now carried forward | What remains open |
| --- | --- | --- |
| `ol` | R05 field relation by specificity tiebreak: `und/mit`, or `von/aus` in an amount attachment; `C1_LOCAL_FRAME__C0_ROLE_TIEBREAK` | equally passing R01 preparation and R03 product/result roles; all concrete liquid identities |
| `otar` | R05 transition by specificity tiebreak: `dann/anschließend/weiter`; `C1_LOCAL_FRAME__C0_ROLE_TIEBREAK` | equally passing R01 nominal role; `bis` is the primary identity rival |
| `pcheey` | R04 neutral bounded preparation/form-II field; the only unique role winner; dry evidence is zero | exact form or substance identity |
| `ols` | R04 measure/dose/final-portion field by specificity tiebreak: `Maß-/Produktposten` | equally passing R01 substance/preparation role; identity of the measured preparation or product |
| `ckhy` | global role open; final process context `mischen/verrühren`, medial content context `Mischung/Kompositum` | global R01 versus R02 and every specific mixture identity; not R05 |

The renderer deliberately separates structural role from word identity. Every German phrase above is replaceable. There are zero confirmed lexemes and zero confirmed plaintext clauses.

`ol`, `ols`, and `otar` are not evidence wins: their displayed roles are `SPECIFICITY_DISPATCH_PRIORITY_AMONG_EQUAL_GATE_SCORES`. The line reader also incorporates two leak repairs: `sain` is rendered `zwei Drachmen` as a fused value form with C0 unit identity, and `chekar` is only the local C0 placeholder `Zwischenzubereitung` rather than a composed hot/dry fraction.

## Read in this order

- [REPORT.md](REPORT.md) gives the provisional decision, counterevidence, scoring corrections, historical architecture comparison, and all twelve complete-line reader outcomes.
- [METHOD.md](METHOD.md) defines the experiment and evidence boundaries.
- [PREREGISTRATION.md](PREREGISTRATION.md) fixes gates, controls, and failure outputs.
- [TARGET_5_ROLE_IDENTITY_SPECS.tsv](src/TARGET_5_ROLE_IDENTITY_SPECS.tsv) contains the five target hypotheses.
- [ROLE_5_MODEL_SPECS.tsv](src/ROLE_5_MODEL_SPECS.tsv) defines R01–R05, including the corrected same-occurrence R03 gate and the discriminative R05 gate.
- [HISTORICAL_SOURCE_REGISTRY.tsv](src/HISTORICAL_SOURCE_REGISTRY.tsv) and [HISTORICAL_RELATOR_ANALOGUES.tsv](src/HISTORICAL_RELATOR_ANALOGUES.tsv) provide architecture-only historical controls.
- [LINE_READER_DEFAULT_SPECS.tsv](src/LINE_READER_DEFAULT_SPECS.tsv) contains the twelve complete working readers.
- [artifacts/README.md](artifacts/README.md) lists the outputs expected from the runner.

## Reproduction status

The manifest reserves these commands:

```bash
python3 experiments/yolo/gdt769_liquid_process_role_identity_dispatch/src/run.py
python3 experiments/yolo/gdt769_liquid_process_role_identity_dispatch/src/validate.py
```

The output set contains the observed builder result and an independent passing validation. The report remains a reproducible working theory rather than a confirmed translation. No new pages, images, or transcriptions are admitted; `f84` and `f84r` remain forbidden.
