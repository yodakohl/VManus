# GDT403 — Vierseiten-Eingabeblatt

GDT403 macht den GDT402-Parser praktisch benutzbar. Es enthält vier noch
unbelegte Seitenslots, ein festes Ereignisschema, alle erlaubten Parserachsen
und eindeutige Grün-/Gelb-/Rot-Entscheidungen.

Es werden keine neuen Manuskriptseiten, Oberflächen oder Bedeutungen geladen.
Die Vorlage wartet auf die vier Seiten, die der Benutzer als Nächstes freigibt.

Ausführen:

```bash
python3 experiments/yolo/gdt403_four_page_factorized_admission_worksheet/src/run.py
python3 experiments/yolo/gdt403_four_page_factorized_admission_worksheet/src/validate.py
```

Der praktische Einstieg ist `FOUR_PAGE_ADMISSION_WORKSHEET.md`; der kompakte
Befund steht in `REPORT.md`.
