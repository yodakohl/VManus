# GDT727 — V99 six meaning debt dispatch

Status:
`PASS_V99_6_MEANING_DEBTS_DISPATCHED__5_LEXICAL_CORES__13_CONTEXTS__9_LINES__PORTION_FAMILY__4_BOS_PHYSICAL_DISPATCH__3_SHEKY_PATIENTS__479_POSITIONS_ONCE__471_UNITS__ZERO_SCORE_SCOPE_EXPORT_DELTA__ALL_H0_NONE`

GDT727 ersetzt die sechs offenen GDT726-Gruppen durch konkrete Arbeitsdefaults:
`Portion(en)` an sechs Stellen, neutrale Lesungen für `cpheesy` und `tail`, vier
physisch geprüfte BOS-Entscheidungen und drei verschiedene lokale Patienten für
den gleichen `sheky`-Handlungskern.

Die aktuelle Komplettfassung steht in
`artifacts/GDT727_V99_51_LINE_WORKING_READER.md`; das Wörterbuch mit Confidence
und Evidenz für jede Zeile in `artifacts/V99_COMPLETE_WORD_CONFIDENCE.tsv`.

Reproduktion:

```bash
python3 experiments/yolo/gdt727_v99_six_meaning_debt_dispatch/src/run.py
python3 experiments/yolo/gdt727_v99_six_meaning_debt_dispatch/src/validate.py
```
