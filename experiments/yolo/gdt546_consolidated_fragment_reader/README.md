# GDT546 — konsolidierter Fragment-Reader

Status: `PASS_81_CARD_FRAGMENT_READER__4_DUAL_BRIDGES__12_EXPLICIT_DEFAULTS`

GDT546 kompiliert die 81 Fragment-plus-Atom-Karten aus GDT543 mit den vier
Sekundärbrücken aus GDT545 zu einem einzigen exakt oberflächenindizierten
Reader. Hauptanker, Erweiterungen, sichtbare Kürzel, Andockkanten, Kontext und
deutsche Arbeitslesung erscheinen gemeinsam. Unbekannte Oberflächen stoppen.

```bash
python3 experiments/yolo/gdt546_consolidated_fragment_reader/src/run.py
python3 experiments/yolo/gdt546_consolidated_fragment_reader/src/validate.py
python3 experiments/yolo/gdt546_consolidated_fragment_reader/src/read_fragment.py \
  --surface chepakeo
```

Siehe `METHOD.md`, `REPORT.md` und `experiment.json`.
