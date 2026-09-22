# GDT1036 — ein ganzer Anschlussabsatz erfüllt die festen Abdeckungsgrenzen

**Genau f4r.1–4 qualifiziert sich in beiden vollständigen Lesarten.** Der
Absatz hat jeweils31Rohgruppen. ZL verwendet17bereits gebundene Positionen
mit14verschiedenen festen Formen, IT18Positionen mit15Formen. Neu wären
13ZL- beziehungsweise12IT-Formen. Die tatsächliche gemeinsame Hypothese ist
noch zu entwickeln; dieser Befund bestätigt keine ihrer Bedeutungen.

Öffentliche Registrierung vor dem Lauf: `59502dd35c513bd67e9ffd955a6aa495a5a0b591`.
Alle1.349vollständigen GDT928-Absätze wurden mit unverändertem65+15-Inventar
gezählt. Beide Ausgangsblätter21/32 wurden vollständig ausgeschlossen. Alle
anderen Texte waren bereits Projektexposition; keine neue unabhängige Reserve
entstand. Die beiden Lesarten sind keine unabhängigen Manuskriptzeugen.

| Umfang | Ergebnis |
|---|---:|
| Vollständige ZL-/IT-Absätze |659/690|
| Physische Blätter im bestehenden Paket |90|
| Absatzgruppen nach exakter ganzer Lokusliste |749|
| Gruppen mit beiden vollständigen Lesarten |600|
| Einseitige Gruppen mit abweichender/fehlender Gegenabgrenzung |149|
| Wegen ursprünglichem Blatt ausgeschlossene Absatzzeilen |16|
| Einzellesarten mit allen Abdeckungsgrenzen |4|
| Paare mit allen Grenzen in beiden Lesarten |1|

Die folgende Tabelle enthält **alle vier einzeln qualifizierenden Lesarten**
und den jeweiligen ganzen Gegenabsatz. Kein ungünstiger Nachbar wurde entfernt.

| Ganzer Absatz | ZL feste Positionen/gesamt | IT feste Positionen/gesamt | Ergebnis |
|---|---:|---:|---|
| f4r.1–4 |17/31|18/31|einziger ausgewählter Anschluss|
| f10v.4–7 |16/32|14/29|IT unter der vorab festen Hälfte|
| f47r.1–5 |13/29|15/30|ZL unter der vorab festen Hälfte|

Alle31Positionen des ausgewählten Absatzes und ihre Gegenlesarten bleiben
[SELECTED.json](artifacts/SELECTED.json) gebunden; unbekannte Formen sind
UNKNOWN und haben keine ergänzte Bedeutung. Beide ausgewählten ganzen Absätze
haben mindestens eine als unsicher markierte Zeile. Wie **vor** dem Lauf
registriert, werden diese Flags berichtet, nicht zum Aussortieren einzelner
Gruppen benutzt. Es gibt keine behauptete paläographische Bestätigung.

[COUNTS.csv](artifacts/COUNTS.csv) und [ROWS.json](artifacts/ROWS.json) bewahren
sämtliche1.349Zeilen, alle zutreffenden Abweisgründe, Rohgruppen, genaue
Quell-IDs und Unsicherheitsflags. [PAIRS.json](artifacts/PAIRS.json) enthält
sämtliche749Paargruppen einschließlich einseitiger Gruppen.
[RANKED.json](artifacts/RANKED.json) enthält die vollständige qualifizierende
Rangliste. Der genaue Bruch17/31 entscheidet hier nicht zwischen mehreren
Kandidaten: nur einer besteht überhaupt alle Grenzen.

Vollständig im Inventar liegen die vier ursprünglichen Lesarten sowie der
zweigruppige IT-Absatz f28v.6. Letzterer erfüllt weder Mindestlänge, Mindestzahl
fester Formen noch Mindestzahl fester Operationen; er wird nicht unterschlagen
oder als zusätzliche ganze Prozesslesung ausgegeben. In diesem Versuch findet
überhaupt keine Grammatik- oder Zustandsausführung statt.

## Entscheidung und Bedeutungsgrenze

**ONE_COMPLETE_EXTENSION_TARGET.** Als nächster Entwicklungsschritt wird genau
der gesamte ausgewählte Absatz versucht, mit sämtlichen alten Werten fest.
Ein Fehlschlag erlaubt keinen Wechsel zu f10v oder f47r und keine Lockerung
im selben Durchgang. Die vollständige Fortsetzung muss ihre Ergänzungen und
Argumentbindungen offenlegen. Unbekannte Wörter sind fehlende Abdeckung,
keine schon beobachteten semantischen Widersprüche.

RAW514s ursprüngliche Karte bleibt bytegleich. Vor dem Zensus wurde ausdrücklich
abweichend festgelegt, die Zeilenflags zu berichten, statt vollständig sichere
Zeilen zur Voraussetzung zu machen. Ihre19Produktionen sind ein dort erhaltener
Zählfehler; die Ausgangsvorlage hat18. GDT1036 prüft nur deren unverändertes
Inventar, keine der offenen V1- oder neu entwickelten V2-Nachbedingungen.
GDT994s anderes47-Werte-Transportresultat bleibt unverändert.

Die Auswahl bevorzugt den Wortbestand der beiden Entwicklungsabsätze. Auch ein
inhaltlich falsches Wörterbuch kann diese Abdeckung erzielen. Deshalb sind dies
keine Bedeutungswahrscheinlichkeiten, kein Signifikanzresultat und keine
bestätigten Übersetzungen. Unabhängige Bedeutungsprüfkapazität0; bestätigte Wörter0.
f84/f84r, f116v und die Reserven blieben geschlossen; keine Bilder geöffnet.

## Reproduktion und Aufwand

[VALIDATION.json](artifacts/VALIDATION.json): unabhängige Rekonstruktion aller
1.349Zeilen,749Gruppen, exakten rationalen Rangfolge, vollständiger Auswahl,
CSV und10Lockbindungen PASS. Der Validator hat den Primärcode weder gelesen
noch importiert.27Primär- und24unabhängige synthetische Prüfungen gingen voraus.
Das bestätigt Berechnung und eingefrorene Auswahl, nicht historischen Inhalt.

Beginn12:53UTC, Ausführung und Validierung13:08UTC, Ergebnisabschluss13:11UTC.
Das25-Minuten-Budget bis13:18UTC schließt Veröffentlichung ein.

```sh
python experiments/yolo/gdt1036_powder_frozen_lexicon_capacity/src/run.py --execute
python experiments/yolo/gdt1036_powder_frozen_lexicon_capacity/src/validate.py --execute
```
