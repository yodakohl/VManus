# GDT1153 — frühere Wiederholung bestimmt die Fortsetzung nicht allein

**STRICT_PRIOR_CONTINUATION_CHOICE_REFUTED.** Der registrierte Test ist tatsächlich ausgeführt: alle13 unveränderten ZL-Kontexte aus GDT926, ihre26 Stellen und dieselben Stellen in den beiden alternativen Transkriptionen. Die geprüfte Regel wählt diejenige von zwei Fortsetzungen, die allein schon vorher im vollständigen Absatz vorkam. Sie scheitert in ZL und IT. Das widerlegt diese feste Auswahlregel, nicht Referenz, Anaphern, jede Wiederholungswirkung oder eine Wortbedeutung.

Die [vollständige Tabelle](CANDIDATE_TABLE.md) enthält alle78 Leser/Stellen-Einträge einschließlich Enthaltungen und unprüfbarer Fälle. [Ganze Kontexte](WHOLE_CONTEXTS.md) erhalten alle ursprünglichen Gruppen und Unsicherheiten; [CASES.json](artifacts/CASES.json) zusätzlich sämtliche früheren Fundstellen, Gruppen-IDs, Abstände und Vorhersagen. Niemand wurde nach einem günstigen Ergebnis ausgewählt.

| Lesung | Ursprüngliche Stellen | Regel trifft | Regel widersprochen | Keine Auswahl: beide/keine vorher | Unprüfbar |
|---|---:|---:|---:|---:|---:|
|ZL3b|26|0|1|5 (alle keine)|20|
|IT2a|26|4|5|16 (alle keine)|1|
|RF1b|26|0|0|0|26|

Die26 primären Stellen liegen auf16 physischen Blättern. ZL/IT umfassen jeweils22 verschiedene vollständige markierte Absätze; mehrere Fälle teilen Absätze und sind nicht unabhängige Stichproben. ZLs20 sowie ITs ein unprüfbarer Fall enthalten Unsicherheit im früheren Textbereich. Ein nicht gelesener früherer Ausdruck wird nicht als abwesend gezählt. RF hat20 nicht eindeutig/sicher rekonstruierte ganze Hostzeilen und6 passende Stellen ohne vollständige Absatzgrenzen. Fehlende Prüfbarkeit wird nicht als Gegenbeispiel gezählt. Die9 IT-Auswahlen liegen auf8 Blättern; ZLs einzelne Auswahl ist derselbe f103v-Fall wie in IT.

## Alle tatsächlich entscheidbaren Vorhersagen

| Lesung / Stelle | Zuvor vorhandene Form: Anzahl | Konkurrent zuvor | Vorhersage | Tatsächlich | Ergebnis |
|---|---|---:|---|---|---|
|ZL f103v.6|qokeedy:1|qokam:0|qokeedy|qokam|Widerspruch|
|IT f19r.10|chor:3|ykchor:0|chor|ykchor|Widerspruch|
|IT f75v.47|qokedy:2|qokeedy:0|qokedy|qokeedy|Widerspruch|
|IT f81v.18|qokedy:2|qokeedy:0|qokedy|qokedy|vereinbar|
|IT f86v5.32|chey:1|ykair:0|chey|chey|vereinbar|
|IT f83r.6|lchedy:1|lol:0|lchedy|lchedy|vereinbar|
|IT f77v.36|lchedy:1|shecthedy:0|lchedy|lchedy|vereinbar|
|IT f83r.23|lchedy:1|shecthedy:0|lchedy|shecthedy|Widerspruch|
|IT f103v.6|qokeedy:1|qokam:0|qokeedy|qokam|Widerspruch|
|IT f108v.46|lchedy:2|ral:0|lchedy|ral|Widerspruch|

## Konkrete Konsequenz für eine Lesung

Zwei Vergleiche veranschaulichen den Befund besonders klar, ohne neue Fälle hinzuzunehmen:

- Nach exakt `ol shedy qokedy` folgt auf f75v.47 `qokeedy`, auf f81v.18 `qokedy`. IT hat in beiden vorherigen Absatzbereichen genau2 `qokedy` und0 `qokeedy`.
- Nach exakt `qokal shedy qokedy` folgt auf f77v.36 `lchedy`, auf f83r.23 `shecthedy`. IT hat zuvor jeweils1 `lchedy` und0 `shecthedy`.

Derselbe gemeinsame Kontext und dieselben beiden Wiederholungszahlen reichen hier also nicht für eine deterministische Fortsetzungswahl. Das ist eine beschreibende Folgerung aus den registrierten Fallzeilen, kein zusätzlich getesteter oder statistisch bevorzugter Mechanismus. Andere frühere Wörter, Abstände und Absatzpositionen unterscheiden sich weiterhin. Sie dürfen nicht nachträglich passend gewichtet werden, um diesen Test zu retten.

Eine künftige Lesung kann weiterhin frühere Gegenstände aufgreifen oder neue einführen. Sie muss jedoch erklären, weshalb in diesen konkreten gleichen Kontexten trotz gleicher Wiederholungszahlen verschiedene Formen folgen. Ein bloßes „dieses Wort kam schon vor, also wird derselbe Gegenstand genannt“ genügt nicht. Die Beobachtung entscheidet weder, welches Wort einen Gegenstand bezeichnet, noch ob irgendeine Form ein Pronomen ist.

## Abgrenzung und Entscheidung

IDEA198s allgemeine Frage nach Wiederholung und Fortsetzungswahl bleibt breiter als diese strenge Regel. Ihr f21r/f32v-Beispiel wurde nicht als weiterer günstiger Fall ergänzt. GDT926/927/928 bleiben unverändert. Die frühere Ablehnung eines großen Vorhersagemodells bleibt sinnvoll; jetzt wurde ein kleiner logischer Falsifikator vorab festgelegt und vollständig ausgeführt. Ein einzelner bestimmter Gegenfall genügt gegen die ausnahmslose Regel; replizierte Fortsetzungszweige wären hingegen für eine belastbare allgemeine Präferenz oder Bedeutungswahl nötig und fehlen weiterhin.

**Entscheidung:** diese feste Prioritätsregel schließen; keine Nachbesserung durch jüngstes Auftreten, neue Wortteile, kürzere Kontexte oder veränderte Absatzgrenzen. Die vier vereinbaren IT-Fälle bleiben erhalten, liefern aber keinen eigenständigen Vorteil gegenüber Worthäufigkeit, Themenbindung oder Formeln. Kein Vergleich der gesamten vorausgegangenen Forschungssuche gegen eine Gegenkontrolle, keine Signifikanz- oder Bedeutungsbehauptung. Alle Daten waren exponiert; unabhängige Bedeutungsbestätigung0, übersetzte Wörter0. f84/f84r, f116v und Reserven blieben geschlossen.

## Reproduktion

[Registrierung](PREREGISTRATION.md) und PREREG_LOCK.json binden die Regel und Quellen vor dem neuen Lauf. Verwendet werden nur vorhandene915-Projektionen,926s festes Kandidateninventar und unveränderte927-Quellen-/Absatzfunktionen. Die Registrierung wurde lokal vor dem Zugriff auf die neuen Fallauswertungen eingefroren; sie wurde nicht vor dem Lauf öffentlich gepusht. Bekannte Vorexposition der alten Berichte ist offengelegt.

`python experiments/yolo/gdt1153_prior_continuation_choice/src/run.py` reproduziert alle Tabellen und ganzen Kontexte. Bei der Ausgabeprüfung wurde ausschließlich ein irreführendes, fallbezogenes seed-Feld aus dem deduplizierten Absatzobjekt entfernt; alle Fallzeilen und Ergebniszahlen blieben identisch. Die spätere Markdown-Kontextausgabe ist eine lesbare Wiedergabe derselben JSON-Absätze, keine zusätzliche Datenauswahl.

Unabhängige Rekonstruktion:18/18 Prüfungen PASS; alle78 Fallzeilen, Quellen, Absatzgrenzen, früheren Gruppen-IDs/Abstände, Unsicherheiten und Vorhersagen stimmen überein. Siehe artifacts/VALIDATION.json und artifacts/VALIDATION.md. Diese Prüfung bestätigt die Fallberechnung, keine historische Bedeutung.
