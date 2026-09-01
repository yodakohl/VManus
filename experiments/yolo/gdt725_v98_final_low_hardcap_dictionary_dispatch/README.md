# GDT725 — V98 final low-hardcap dictionary dispatch

Status: `PASS_V98_16_FINAL_LOW_HARDCAP_READINGS_AUDITED__21_POSITIONS__9_CORE_OR_STRUCTURAL_REPAIRS_PLUS_7_RETAINED__5_STRUCTURAL_READINGS_SEPARATED__4_ACTION_WHOLES_RETAINED__72_EVIDENCE_BINDINGS__0_UNAUDITED_HARDCAP__NO_COMPONENT_EXPORT_NO_SCORE_CREDIT__ALL_H0_NONE`

GDT725 prüft die letzten sechzehn bislang nur geerbten oder strukturell
gedeckelten Wörterbuchlesarten. V98 hält Wörterbuchdefault, lokale Ausgabe und
Strukturmarke getrennt. Eine nachgeschaltete Rendererprüfung führt zwei bereits
gebundene Spannen je einmal aus und repariert eine an GDT686 gebundene
Companion-Zeile, ohne Wörterbuchkern oder Score zu verändern. Die vollständige Fassung steht in
`artifacts/V98_COMPLETE_WORD_CONFIDENCE.tsv`; die kompakte Entscheidungstabelle
in `artifacts/V98_16_FINAL_HARDCAP_DECISIONS.tsv`.

Reproduktion:

```bash
python3 experiments/yolo/gdt725_v98_final_low_hardcap_dictionary_dispatch/src/run.py
python3 experiments/yolo/gdt725_v98_final_low_hardcap_dictionary_dispatch/src/validate.py
```
