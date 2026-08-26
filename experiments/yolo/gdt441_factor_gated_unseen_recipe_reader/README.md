# GDT441 — Leser für neue Kombinationen bekannter Kerne

Status: `ALL_PAGE_PRIVATE_RECIPES_CONDITIONALLY_READABLE__NOT_OCCURRENCE_PREDICTION`

Der Leser versucht zuerst den exakten 1.563-Rezept-Katalog. Fehlt der Schlüssel,
liest er eine **bereits sichtbare** neue Kombination, sofern ihre Scope-Kanten,
benachbarten Handlungspaare und ihr Schluss bereits lizenziert sind.

```bash
python3 experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/src/factor_gate_stream_read.py \
  --input INPUT.tsv --output READINGS.tsv
```

Die Eingabe braucht die Spalten `event_id`, `statement_id`, `physical_page`,
`register`, `owner_de`, `surface` und `component_recipe` in physischer Folge.
Der Leser erzeugt keine Oberfläche und sagt nicht voraus, dass eine Kombination
vorkommen wird. Sie muss zuerst sichtbar vorliegen.

Der kompakte Befund steht in [REPORT.md](REPORT.md), die Regeln in
[METHOD.md](METHOD.md).
