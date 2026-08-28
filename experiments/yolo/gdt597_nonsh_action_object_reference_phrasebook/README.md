# GDT597 — Nicht-SH-Objekt- und Referenzphrasebook

Status: `PASS_396_NONSH_ACTION_OBJECTS__219_WRITTEN__77_LEFT__4_RIGHT__96_DEFAULT__0_UNFILLED`

GDT597 gibt allen 396 laufenden `T/CHD/S`-Aktionen auf den sechs bereits
geöffneten Badseiten einen konkreten Arbeitsgegenstand. 219 Aktionen lesen ihr
vollständig geschriebenes GDT589-Packet. Von den 177 trägerlosen Aktionen
übernehmen 77 eine kompatible linke Quelle, vier teilen ein rechtes Komplement
im selben Ereignis und 96 benutzen ein aktionsinternes oder regelgebundenes
Defaultobjekt.

Der Leser führt Teilnehmer und Parameter getrennt. OT und DY schneiden den
Bezug ab; OL erhält ihn. Eine `Stationsbedingung` oder ein `Stationsmaß` kann
daher zwischen zwei Teilnehmern stehen, ohne selbst zum Patienten zu werden.
Vier sichtbare Scopeentscheidungen verhindern zugleich zu weite Forttragung:
Neuansatz, verbrauchte Portion, nur intern umgeleiteter Strom und zwei
aufeinanderfolgende Maßparameter.

Die vollständige Leseschicht steht in
`artifacts/gdt597_396_nonsh_action_object_replay.tsv`, die 17 schwierigen
Werkstatturteile in `artifacts/gdt597_17_manual_workshop_decisions.tsv` und die
kompakte Grammatik in
`artifacts/GDT597_NONSH_OBJECT_REFERENCE_PHRASEBOOK.md`.

```bash
python3 experiments/yolo/gdt597_nonsh_action_object_reference_phrasebook/src/run.py
python3 experiments/yolo/gdt597_nonsh_action_object_reference_phrasebook/src/validate.py
```
