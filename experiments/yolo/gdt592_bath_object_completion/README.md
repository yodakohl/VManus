# GDT592 — vollständige Badegut-Arbeitslesung

Status: `PASS_254_BATH_ACTION_OBJECTS__149_OBJECTLESS_PLUS_5_FILL_ONLY_PATCHED__53_BODY__81_STATION__107_BATH_OBJECT__9_UNIT__4_PORTION__13_LOCAL_HANDOFFS__11_EPISODE_CARRIES__132_STATEMENTS__2_GDT569_DIVERGENCES_RETAINED`

Alle 254 `SH_BIO_BATHE`-Handlungen besitzen jetzt ein ausgesprochenes
Arbeitsobjekt. Die zunächst angenommenen 24 Badeepisode-Carries zerfallen nach
vollständiger Sichtprüfung in 13 nähere schriftliche Objektübergaben und nur
elf kurze Episode-Carries. Das neutrale Restobjekt heißt lesbar `Badegut` bzw.
`das zu badende Gut`; AIIN bleibt getrennt davon `Badfüllung`.

Ausführen:

```bash
python3 experiments/yolo/gdt592_bath_object_completion/src/run.py
python3 experiments/yolo/gdt592_bath_object_completion/src/validate.py
```

Siehe `METHOD.md`, `REPORT.md`, den vollständigen Leser unter `artifacts/` und
`experiment.json`.
