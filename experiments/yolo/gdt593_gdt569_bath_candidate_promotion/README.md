# GDT593 — stabile AIN/OR-Badeobjekte

Status: `PASS_12_STABLE_ROOT_PROMOTIONS__8_AIN_PORTION__4_OR_UNIT__5_ANAPHORIC_SAME_SCOPE__7_RESET_TYPE_DEFAULTS__254_OBJECTS__12_STATEMENTS_CHANGED__93_COLD_DEFAULTS_REMAIN`

GDT593 ersetzt zwölf neutrale `Badegut`-Defaults durch konkretere
Arbeitsobjekte: acht getragene AIN-Werte werden `Anwendungsportion`, vier
getragene OR-Werte `Einheit`—lokal Stationseinheit, nach Reset Badeinheit. Fünf lokale Quellen werden anaphorisch
als dasselbe Objekt formuliert; nach sieben Resets wird nur der bestimmte Typ
gesetzt. Die alte Badegut-Klausel bleibt an jeder Stelle als Rival erhalten.
Y bleibt für den nächsten, aktionsabhängigen Pass offen.

Ausführen:

```bash
python3 experiments/yolo/gdt593_gdt569_bath_candidate_promotion/src/run.py
python3 experiments/yolo/gdt593_gdt569_bath_candidate_promotion/src/validate.py
```

Siehe `METHOD.md`, `REPORT.md`, den vollständigen Leser unter `artifacts/` und
`experiment.json`.
