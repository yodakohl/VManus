# GDT446 — Identität und Ausführung getrennt

GDT446 korrigiert die zu grobe Katalogpriorität aus GDT445. Ein exakter
Schlüssel identifiziert eine Karte; ausgeführt werden darf sie nur, wenn ihre
sichtbaren Faktoren und ihr eingehender Zustand ebenfalls durchgehen.

```bash
python3 experiments/yolo/gdt446_identity_execution_intake_split/src/run.py
python3 experiments/yolo/gdt446_identity_execution_intake_split/src/validate.py
```

Einzelprüfung:

```bash
python3 experiments/yolo/gdt446_identity_execution_intake_split/src/intake_certificate_v2.py \
  --recipe AIR+DY --incoming-action CH --scope-incoming-action NONE
```

Primärbericht: `REPORT.md`.
