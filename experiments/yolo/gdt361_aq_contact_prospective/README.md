# GDT361 — prospective AQ/contact array

GDT361 takes the single postselected GDT360 CONTACT/GAP lead and tests its
direction on one newly reviewed source-described array on physical folio f102.
The experiment preserves a published canvas correction, freezes direct visual
calls before the six scored family rows are revealed, and reports the weak
prospective outcome without assigning a meaning.

Run and validate:

```bash
python3 experiments/yolo/gdt361_aq_contact_prospective/src/freeze.py
python3 experiments/yolo/gdt361_aq_contact_prospective/src/validate_freeze.py
python3 experiments/yolo/gdt361_aq_contact_prospective/src/freeze_visual.py
python3 experiments/yolo/gdt361_aq_contact_prospective/src/validate_visual.py
python3 experiments/yolo/gdt361_aq_contact_prospective/src/run.py
python3 experiments/yolo/gdt361_aq_contact_prospective/src/validate.py
```

The first four commands document historical freeze stages and should not be
interpreted as recreating their chronology. The final scorer uses guarded
locus selection and rejects all f84 material before parsing.
