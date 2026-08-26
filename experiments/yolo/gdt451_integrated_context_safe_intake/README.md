# GDT451 — ein Aufnahmebefehl, eine unverrückbare Reihenfolge

GDT451 verbindet den schnellen historischen Nachbarstatus aus GDT449 mit dem
lokalen Ausführungszertifikat aus GDT446. Der Nachbarstatus darf sortieren und
warnen. Die endgültige Entscheidung stammt immer aus dem gerade sichtbaren
Kontext.

Ausführen:

```bash
python3 experiments/yolo/gdt451_integrated_context_safe_intake/src/intake_command.py \
  --recipe 'D_ADDR+EEE+Y' \
  --incoming-action CHD \
  --scope-incoming-action CHD \
  --next-recipe 'OT+AIIN'
```

Neu bauen und prüfen:

```bash
python3 experiments/yolo/gdt451_integrated_context_safe_intake/src/run.py
python3 experiments/yolo/gdt451_integrated_context_safe_intake/src/validate.py
```

Das Ergebnis ist ein Arbeitswerkzeug für bereits sichtbare Kompositionen, kein
Generator für neue Oberflächen und keine Übersetzung.
