# GDT547 — sichtbarer Reader für 24 Atom/Faktor-Karten

Status: `PASS_24_ATOM_FACTOR_CARDS_VISIBLE__21_OLD_DECK_COVERS__3_SPECIAL_ROUTES`

GDT547 gibt den letzten 24 GDT542-Prosakarten je eine vollständige sichtbare
Kompositionsspur, Kontextlesung und Ausführungsnotiz. 21 Formen werden exakt
vom alten Renderer-Deck gedeckt; drei benutzen eng begrenzte, bereits
vorhandene Sonderkanäle.

```bash
python3 experiments/yolo/gdt547_atomic_factor_visible_reader/src/run.py
python3 experiments/yolo/gdt547_atomic_factor_visible_reader/src/validate.py
python3 experiments/yolo/gdt547_atomic_factor_visible_reader/src/read_atomic.py \
  --surface faiis
```

Siehe `METHOD.md`, `REPORT.md` und `experiment.json`.
