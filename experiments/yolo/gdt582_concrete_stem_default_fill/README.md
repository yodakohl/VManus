# GDT582 — concrete stem default fill

Status: `PASS_15889_COMPLETE_DEFAULTS__13593_PRODUCTIVE_FUNCTION_SLOTS__109_LEARNED_CONTENT_SLOTS__42_CORE_STEMS__181_REGISTER_CELLS__80_CLASS_NAME_TYPES__4026_ALIAS_DEFAULTS__5122_EVENTS__793_STATEMENTS__744_LOCAL_CARDS__25_EVENT_SENSE_CHECKS__20_COMPLETE_PASSAGE_CHECKS__ZERO_EMPTY_DEFAULTS`

GDT582 ist der erste vollständige konkrete Bedeutungsdurchgang auf der in
GDT581 polierten Grammatik. Jeder der 15.889 geschriebenen Slots erhält einen
nichtleeren, austauschbaren Default. Die ausgewählte Arbeitstheorie ist eine
Mischung aus 42 produktiven GDT581-`slot_value`-Klassen, 181
Klasse×Register-Ausformulierungen, 80 gelernten Klasse×Namenskern-Karten und
zwei ownergebundenen `LOCAL_X`-Bedeutungen. Diese 42 Klassen sind analytische
Normalisierungen; nicht jede ist ein direkt beobachtetes Manuskriptwort oder
ein bewiesener Wortstamm.

Der entscheidende Gewinn ist Komposition innerhalb der bereits von GDT581
segmentierten Occurrences: 13.593/13.702 Inhalts-Slots werden aus kurzen
wiederkehrenden Klassen gelesen; nur 109 bleiben gelernt. Wasser,
Wein, Öl, Salz, Wurzel, Blatt, Blüte, Samen, Krankheit und Heilmittel liegen
damit an konkreten Namens- oder Owner-Slots, ohne `Y`, `O`, `AIIN`, `CHD` oder
einen anderen häufigen Stamm auf allen fünf Registern zu überladen.

Ausführen:

```bash
python3 experiments/yolo/gdt582_concrete_stem_default_fill/src/run.py
python3 experiments/yolo/gdt582_concrete_stem_default_fill/src/validate.py
```

Das Ergebnis steht in [REPORT.md](REPORT.md), das Verfahren in
[METHOD.md](METHOD.md), das vollständige Arbeitswörterbuch in den TSV-Artefakten
und die komplette Dreißig-Seiten-Ausgabe in
`artifacts/GDT582_CONCRETE_DEFAULT_THIRTY_PAGE_EDITION.md`.

Alle deutschen Werte sind explorative Hausdefaults. Sie sind konkret genug,
um ganze Passagen zu lesen, dürfen aber jederzeit durch einen besseren
kompositionellen Wert ersetzt werden.
