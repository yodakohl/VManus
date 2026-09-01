# GDT728 — V99R2 inherited unit-term dispatch

Status:
`PASS_V99R2_60_INHERITED_UNIT_TERMS__55_PORTION_1_TEIL_1_MASS_3_WERT_0_HOLD__293_OCCURRENCES__61X2_DOSE_TOKENS_REMOVED_FROM_SEMANTIC_FIELDS__324_ACTIVE_V99_BYTE_STABLE__SCORES_EVIDENCE_SCOPE_EXPORT_UNCHANGED__ZERO_COMPONENT_CREDIT__ALL_H0_NONE`

GDT728 ersetzt die 60 geerbten globalen Dosisformulierungen nicht blind,
sondern über eine explizite Ganzworttabelle. Das Ergebnis sind 55
Portionslesungen, ein relativer Teil, ein Maß und drei offene Wertstufen. Die
60 Formen decken 293 beobachtete Vorkommen ab.

Das kanonische Komplettwörterbuch steht in
`artifacts/V99R2_COMPLETE_WORD_CONFIDENCE.tsv`. Jede seiner 1.586 Zeilen
behält Score, Confidence, positive Evidenz und Gegenbeleg. Die 324 aktiven
V99-Zeilen und der vollständige 51-Zeilen-Reader werden nicht verändert.

Reproduktion:

```bash
python3 experiments/yolo/gdt728_v99r2_inherited_unit_term_dispatch/src/run.py
python3 experiments/yolo/gdt728_v99r2_inherited_unit_term_dispatch/src/validate.py
```
