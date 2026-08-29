# GDT639 — sichtbare Felder in strikten Restlöchern reparieren

Status: `PASS_8_EXACT_COMPONENT_REPAIRS__9_NEW_COMPLETE_LINES__16_HELD_DEFAULTS`

GDT639 gibt allen 24 strikten V15-Lochoberflächen einen konkreten
Arbeitsdefault. Acht vollständig komponentengebundene Oberflächen bestehen
den Umlauf über alle 332 Vorkommen und werden V16-Einträge. Sechzehn weitere
Defaults bleiben mit einer benannten offenen Feld- oder Skopusfrage außerhalb
des Wörterbuchs.

V16 besitzt 280 Wörterbuchzeilen und deckt 39 Mehrwortzeilen vollständig;
28 davon sind leserstabil und scope-sauber. Neun Zeilen werden neu geschlossen.

Ausführen:

```bash
python3 experiments/yolo/gdt639_strict_hole_component_repair/src/run.py
python3 experiments/yolo/gdt639_strict_hole_component_repair/src/validate.py
```

Der vollständige Befund steht in `REPORT.md`.
