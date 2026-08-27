# GDT514 — Zweite Vierseitenauswahl und Besitzerkarte

Status: `PASS_SELECTION_AND_OWNER_MAP_READY`

GDT514 rekonstruiert die 200 erlaubten physischen Seiten ausschließlich über
die geschützte Seitenspalte, zieht aus den 174 noch ungelesenen Seiten genau
einmal vier Kandidaten und hält danach deren sichtbare Besitzergrenzen fest:

`f31r | f66r | f20v | f4r`

Voynich-Textinhalte der vier Seiten bleiben in diesem Experiment geschlossen.

Ausführen:

```bash
python3 experiments/yolo/gdt514_second_random_four_page_selection_owner_map/src/run.py
python3 experiments/yolo/gdt514_second_random_four_page_selection_owner_map/src/validate.py
```

Siehe `REPORT.md`, `METHOD.md` und `artifacts/README.md`.
