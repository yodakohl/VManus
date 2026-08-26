# GDT448 — Nachbarkarten im echten Kontext

GDT448 setzt die begrenzten GDT447-Nachbarn probeweise in die tatsächlich
belegten Zustände ihrer jeweiligen Quellkarte. Damit wird sichtbar, was ein
neutraler Einzelkartentest übersieht und was der echte Aussagescope verbietet.

```bash
python3 experiments/yolo/gdt448_context_conditioned_neighbor_replay/src/run.py
python3 experiments/yolo/gdt448_context_conditioned_neighbor_replay/src/validate.py
```

Primärbericht: `REPORT.md`.
