# GDT590 — fokussierte Körper-/Stationsentscheidung im Bad

Status: `PASS_FOUR_BATH_FORKS_BODY_DEFAULT__52_OF_92_CLEAN_BODY__40_BLOCKED_STATION__FOUR_READER_PATCHES`

Alle vier in GDT589 verbliebenen Y+AIIN-Badgabeln lesen im Gesamtmodell zuerst
`Körper`; `Stationsansatz` bleibt an jeder Stelle sichtbar. Das 92-Host-Bild
lautet danach 52 blockerfreie Körperhosts gegen 40 durch Relation, Form oder
Adresse geblockte Stationshosts. Exakt vier von 1.243 Slots und vier von 793
Aussagen ändern sich.

Der manuelle Bildpass ist absichtlich separat: nur E2637 neigt bildlich leicht
zu Körper, E2404, E2652 und E3182 eher zu Station/Apparat. Alle vier Ziele sind
Prosa ohne Wort-Figur-Zeiger. Die 4/4-Arbeitsentscheidung stammt daher aus
vollständigem Host und Satzfolge, nicht aus einem Bildlabel.

- `REPORT.md` erklärt Ergebnis und Grenzen.
- `METHOD.md` beschreibt Hostregel, Replay und Bildpass.
- `artifacts/GDT590_FOUR_BATH_READER.md` zeigt die vier vollständigen Passagen.

```bash
python3 experiments/yolo/gdt590_focused_bath_body_station_adjudication/src/run.py
python3 experiments/yolo/gdt590_focused_bath_body_station_adjudication/src/validate.py
```
