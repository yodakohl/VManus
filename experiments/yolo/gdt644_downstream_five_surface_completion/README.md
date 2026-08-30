# GDT644 — five downstream surface completions

GDT644 consumes the five one-hole lines exposed by GDT643 and adds five
concrete exact-surface cards to the working reader:

- `otal = Ansatz aus kaltem Rohstoff, Form I`;
- `cthol = CTH-Drogenstoff; im Kräuterbuch Blatt- oder Krautdroge`;
- `chokchy = Trockenansatz: heiß-trockene Grundform`;
- `qotchod = kalt-trockene Zubereitung, fertig gebunden`;
- `ytchor = kalt-trockene Portion dieser Droge`.

The five cards cover 195 token positions, complete five lines and expose
fifteen new single-hole lines. V21 contains 298 dictionary rows, 251 exact
glossary surfaces and 10,230 rendered token positions.

Run:

```bash
python3 experiments/yolo/gdt644_downstream_five_surface_completion/src/run.py
python3 experiments/yolo/gdt644_downstream_five_surface_completion/src/validate.py
```

The full evidence, translations, qualifications and next frontier are in
`REPORT.md`. The values are replaceable practical working readings, not a
phonetic decipherment or a claimed final solution.
