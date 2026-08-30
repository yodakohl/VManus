# GDT655 — DAL/AL measured-material completion

Status: `PASS_18_ANCHORED_PLUS_1_PREDICTED_DAL_AL_SURFACES__V32`

GDT655 liest AL als Rohstoffklasse und DAL als abgemessene Rohstoffmenge. 18
Karten sind reader-verankert, DAIIL ist eine ausdrücklich reader-instabile
Kompositionsvorhersage; ORAL wird aus dem direkten OR|AL-Split revidiert.
Sieben weitere Mehrwortzeilen werden vollständig.

```bash
python3 experiments/yolo/gdt655_dal_al_measured_material_completion/src/run.py
python3 experiments/yolo/gdt655_dal_al_measured_material_completion/src/validate.py
```
