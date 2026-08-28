# GDT594 — Y-Badevorkommen vervollständigen

Status: `PASS_49_Y_OCCURRENCE_COMPLETIONS__17_LOCAL_STATION__2_LOCAL_FLOW__1_LOCAL_BODY__29_RESET_BODY_FIRST__20_ANAPHORIC__29_DEFINITE__254_OBJECTS__49_STATEMENTS_CHANGED__44_COLD_DEFAULTS_REMAIN`

GDT594 konkretisiert die 49 nach GDT593 noch neutralen Badeobjekte mit
getragenem `Y`: im selben Objektsegment als 17 Stationsansätze, 2 Ströme und
1 Körper; nach 2 echten post-donor Readerresets oder 27 Satzresets als
29 körpernahe SH-Bad-Defaults.
Das ist eine vollständige Vorkommensedition und kein globaler Eintrag
`Y = Körper/Station/Strom`.

Ausführen:

```bash
python3 experiments/yolo/gdt594_gdt569_y_bath_occurrence_completion/src/run.py
python3 experiments/yolo/gdt594_gdt569_y_bath_occurrence_completion/src/validate.py
```

Die Methode steht in `METHOD.md`, das Ergebnis in `REPORT.md`, der vollständige
Leser in `artifacts/GDT594_Y_COMPLETED_BATH_READER.md`.
