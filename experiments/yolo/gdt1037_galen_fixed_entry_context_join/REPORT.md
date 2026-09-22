# GDT1037 — feste Galen-Werte mit Zeilen- und Vorgängerkontext

**REFUTED_FIXED_CONTEXT_JOIN**, auch auf den als literal markierten Quellzeilen.
Der eingefrorene Kontext trennt die widersprechenden Bedeutungen der beiden
vollständigen Galen-Lesefamilien nicht. Es wurden keine Wortwerte verändert.

## Vertrag und tatsächlich geprüfte Daten

[Präregistrierung](PREREGISTRATION.md), [Methode](METHOD.md) und beide Programme
waren vor der Ausführung mit 17 Datei-Hashes öffentlich gebunden: Commit
`ad09becb84f0587cb4d734df6b4960c2f971618f`, bestätigt 14:14:10 UTC.
Die vier ganzen Entwicklungsabsätze umfassen 183 ZL3b-Positionen:
f107v.45–49 und f111r.44–47 (A:95), f76v.37–41 und f80v.19–22 (B:88).
67 A-Werte und 59 B-Werte ergeben 113 Formen, darunter 13 gemeinsame Formen.
Die vorangehende vollständige Denotationsprüfung hält bei allen 13 unterschiedliche
feste Bedeutungen fest; ein bloßer Unterschied englischer Etiketten genügt nicht.

Geprüft wird die notwendige Bedingung einer Funktion D(Form,Kontext).
LINE_START bedeutet erste Rohgruppe derselben physischen Zeile. Sonst wählt die
unmittelbar vorherige Rohgruppe mit dem exakten ASCII-Ende `dy` PREV_DY; alle
anderen Positionen sind OTHER. Unsichere Vorgänger werden weder übersprungen
noch normalisiert. Dies ist ein neuer wörtlicher Kontextselektor, keine identische
Wiederholung des GDT318-Parsers und kein Bedeutungsbeweis aus dessen Formstatistik.

Alle 113 Formen × drei Zustände werden in beiden Panels gespeichert (678 Zellen),
auch leere und nur einseitig besetzte Zellen. Das zweite Panel behält ausschließlich
Positionen aus Quellzeilen mit literal-Flag True: 65 Positionen, A40/B25.
Die gesamten 183 Rohpositionen bleiben in SCOPE.json erhalten.

## Vollständige gemeinsame Vorhersage-/Beobachtungstabelle

Eine Zelle mit mindestens einer A- und einer B-Position verletzt die verlangte
Trennung der festen Bedeutungen. Zahlen sind A/B-Häufigkeiten; * markiert solche
Kollisionen. Im Literal-Panel hat keine gemeinsame Form LINE_START-Positionen.

| Form | Fester A-Wert | Fester B-Wert | RAW Start | RAW nach dy | RAW sonst | LITERAL nach dy | LITERAL sonst |
|---|---|---|---:|---:|---:|---:|---:|
| aiin | WATER | VEGETABLE | 0/0 | 0/0 | 3/4* | 0/0 | 2/1* |
| al | IN | LITTLE | 0/0 | 0/0 | 4/1* | 0/0 | 3/0 |
| chedy | THAT_WATER | EFFECT | 0/0 | 0/1 | 3/2* | 0/1 | 3/1* |
| cheey | EVACUATION | LETTUCE | 0/0 | 0/0 | 2/1* | 0/0 | 0/1 |
| chey | LIQUID | OF | 0/0 | 1/1* | 4/2* | 0/0 | 1/1* |
| daiin | BECAUSE | GOOD_JUICED | 0/0 | 0/0 | 1/2* | 0/0 | 0/1 |
| dal | WHEN | THIS_FOOD | 0/0 | 1/0 | 0/1 | 1/0 | 0/1 |
| or | COLD | NOT | 0/0 | 0/0 | 1/1* | 0/0 | 0/1 |
| qokeedy | AS_POSSIBLE | MORE | 0/0 | 0/1 | 1/0 | 0/0 | 0/0 |
| qokey | FULLY | UNNATURALLY | 0/0 | 1/0 | 2/1* | 0/0 | 0/0 |
| qoky | NO | IS | 0/0 | 1/1* | 1/2* | 0/0 | 0/0 |
| shedy | DISCARD | CABBAGE | 0/0 | 0/1 | 1/5* | 0/0 | 1/2* |
| y | FOR | CURRENT_GREEKS | 2/0 | 0/0 | 2/1* | 0/0 | 0/0 |

Die vollständigen Denotationen stehen in [ENTRIES.json](artifacts/ENTRIES.json),
alle Zellbelege einschließlich Nullen in
[SHARED_CONTEXT_CELLS.json](artifacts/SHARED_CONTEXT_CELLS.json) und
[ALL_CONTEXT_CELLS.json](artifacts/ALL_CONTEXT_CELLS.json).

RAW_EXACT ergibt **13 Kollisionszellen bei 11 Formen**, insgesamt 48 kartesische
A×B-Zeugenpaare. Das sind keine 48 unabhängigen Beobachtungen. LITERAL_LINES
behält **vier Kollisionszellen bei vier Formen und acht Zeugenpaare**:

| Form | A-Positionen | B-Positionen | gemeinsamer Zustand |
|---|---|---|---|
| aiin | f107v.45 G009; f107v.46 G002 | f76v.41 G008 | OTHER |
| chedy | f107v.46 G006; f111r.47 G007/G009 | f76v.41 G003 | OTHER |
| chey | f107v.46 G003 | f80v.22 G004 | OTHER |
| shedy | f107v.45 G006 | f76v.41 G009; f80v.22 G007 | OTHER |

Schon jedes dieser widersprechenden festen Wertepaare kann nicht durch dieselbe
Funktion desselben Wortes und dieses Kontextes realisiert werden. `dal` und
`qokeedy` sind im Rohpanel zwar getrennt; dies bestätigt ihre Bedeutungen nicht.
Insbesondere hat qokeedy im Literal-Panel überhaupt keine Position.

## Entscheidung und Grenzen

Die konkrete Verbindung der beiden vollständigen Lesungen über diesen festen
Kontext ist geschlossen. Keine automatische Suche nach weiteren Kontextmerkmalen,
keine neue Wortzuweisung, kein Austausch der Quellabsätze. GDT1034/1035 bleiben
unverändert: Dort war die Frage eines neu zugewiesenen gemeinsamen Codes anders;
hier bleiben alle ursprünglichen Denotationen fest.

Das Ergebnis verwirft weder jede der beiden getrennten Lesefamilien noch beliebige
kontextabhängige Bedeutungssysteme. GDT311/318s positives Strukturwissen bleibt
bestehen. Eine Wiederaufnahme benötigt einen sachlich begründeten, vorab vollständig
festgelegten anderen Mechanismus mit einer anderen prüfbaren Konsequenz.

Alle vier Absätze und ihre Lesungsentwürfe waren bereits exponiert. Dies war eine
registrierte Prüfung neuer Konsequenzen an bekannten Daten, keine unabhängige
Bestätigung. Keine Bild- oder Reservedaten geöffnet; f84/f84r und f116v geschlossen.
Unabhängige Bedeutungsprüfkapazität 0, bestätigte Wörter 0. Keine Signifikanzbehauptung.

## Reproduktion und Prüfung

[RESULT.json](artifacts/RESULT.json) enthält beide Entscheidungen;
[COLLISIONS.json](artifacts/COLLISIONS.json) sämtliche widersprechenden Belegpaare.
Der unabhängige Validator rekonstruierte alle sechs Ergebnisartefakte und prüfte
alle 17 Lockbindungen. [VALIDATION.json](artifacts/VALIDATION.json): PASS.
Er hat den Primärcode weder gelesen noch importiert. Die Prüfung bestätigt die
Berechnung, nicht die frei angesetzten Wortbedeutungen.

```sh
python experiments/yolo/gdt1037_galen_fixed_entry_context_join/src/run.py --execute
python experiments/yolo/gdt1037_galen_fixed_entry_context_join/src/validate.py --execute
```

Gesamtbudget einschließlich Vorbereitung und Veröffentlichung: 14:04–14:34 UTC.
Ausführung und unabhängige Prüfung abgeschlossen; Ergebnisbericht 14:30 UTC.
