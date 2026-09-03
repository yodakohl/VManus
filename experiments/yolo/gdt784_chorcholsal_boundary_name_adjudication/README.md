# GDT784 — `chorcholsal` boundary/name adjudication

GDT784 keeps the current-reader surface `chorcholsal` intact while testing
whether its recurring `chor`/`chol` material can support a non-exporting
PART+DRY echo.  The practical, deliberately replaceable C0 default is
**`trockene Blütendroge`**; the complete existing span `ol chorcholsal` is
rendered **`Ansatz: trockene Blütendroge`**.  This is a working display, not a
plaintext or lexeme claim.  `sal` remains semantically open.

The decision combines three current fused readings, Stolfi's split target and
thirteen target-free dot controls, the previously bound visual gap audit,
GDT759's 8/7 bidirectional PART+DRY pairs, and the exact P|A|1 slot twin
`cheor ol chockhar` at f100v.20. Five historical witnesses license only the
candidate architecture, never the Voynich spelling or identity.

Reproduce with:

```bash
python3 -B experiments/yolo/gdt784_chorcholsal_boundary_name_adjudication/src/run.py
python3 -B experiments/yolo/gdt784_chorcholsal_boundary_name_adjudication/src/validate.py
./vmanus-exp check-edge-packet experiments/yolo/gdt784_chorcholsal_boundary_name_adjudication/artifacts/GDT784_GDT388_BOUNDARY_PACKET.tsv
```

See `METHOD.md`, `PREREGISTRATION.md`, `REPORT.md`, and `artifacts/RESULT.json`.
