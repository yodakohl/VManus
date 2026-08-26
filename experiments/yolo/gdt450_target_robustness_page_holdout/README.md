# GDT450 — Seiten-Holdout des Zielrobustheitsdecks

GDT450 lernt die grobe Zielentscheidung ohne jeweils eine physische Seite und
prüft sie auf deren synthetischen Nachbarproben. Der Live-Zertifizierer bleibt
unverändert die letzte Instanz.

```bash
python3 experiments/yolo/gdt450_target_robustness_page_holdout/src/run.py
python3 experiments/yolo/gdt450_target_robustness_page_holdout/src/validate.py
```

Primärbericht: `REPORT.md`.
