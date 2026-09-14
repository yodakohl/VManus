# GDT931 — Reproduktion

Die [Präregistrierung](PREREGISTRATION.md) ist das maßgebliche Protokoll.
Die lokale, bereits abgegrenzte Quelle wird direkt aus GDT930 wiederverwendet;
kein neuer Zugriff auf eine gemischte Tabelle und keine neue Bildöffnung.
Alle Quelldateien, nominalen Annahmen und drei neuen Wortvorschläge sind in
PREREG_LOCK.json gebunden. Quellen mit f84/f84r bleiben ausgeschlossen.

```sh
python experiments/yolo/gdt931_shedy_concrete_reading_contrast/src/run.py
python experiments/yolo/gdt931_shedy_concrete_reading_contrast/src/validate.py
```

run.py führt eine feste Ganzwortzuweisung, die vollständige Konkordanz und
beide unmittelbaren Bezugsrichtungen aus. Keine Anpassung, Suche oder OCR.
validate.py implementiert Abdeckung, Werte und Nachbarn separat und prüft
zusätzlich einen bytegleichen Replay. ROOT schrieb beide; die Prüfung ist
keine unabhängige semantische Begutachtung. Der Bericht enthält die manuelle
Bedeutungsgegenbilanz und die RF-Varianten ohne nachträgliche Gleichsetzung.

[ALIGNMENT](artifacts/ALIGNMENT.tsv) erhält jede Gruppe und alle Quelltrenner;
[SHEDY_CASES](artifacts/SHEDY_CASES.tsv) jede Zielstelle samt ganzer Zeile;
[ATTACHMENTS](artifacts/ATTACHMENTS.tsv) jeden Kandidatenanschluss beider
Richtungen. Diese Anschlüsse sind keine score-ready Relationsevidenz.
