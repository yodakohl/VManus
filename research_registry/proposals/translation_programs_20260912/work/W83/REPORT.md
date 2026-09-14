# W83 — shey als Handlung oder Eigenschaft

**Die Eigenschaftslesung ersetzt mehrere falsche Verbargumente durch fehlende Eigenschaftsträger; sie löst die Ausgangsprobleme nicht.** Auf f8v liefert der Vergleich aber zwei ausdrücklich verschiedene Aussagen über unterschiedliche Portionsnennungen.

Drei vollständige Fassungen wurden auf exakt denselben 112 W82-Absatztranskriptionen ausgearbeitet: V `shey=erwärmen`, H `shey=warm`, F `shey=feucht`. Gemeinsames Gerüst ist ausschließlich der hypothetische W82-C-Entwurf mit cthar=Krautportion; er wird dadurch nicht ausgewählt. Alle übrigen Wörter und Regeln bleiben gleich. Pro Fassung 7059 Gruppen und 441 Eigenschafts-, Mengen- und Operationspositionen; alle 66 shey-Positionen stehen in SHEY.tsv, alle vollständigen Fassungen in READING.md/ALIGNMENT.tsv. Dies ist kein globaler shey-Zensus, sondern der vollständige vorhandene W82-Absatzumfang.

## Aussagen an den entscheidenden Stellen

| Stelle | V: erwärmen, unmittelbar folgende Eingabe | H/F: warm/feucht, letzte vorherige Materialnennung |
|---|---|---|
| f8v.7 ZL/IT `shey cthar` | erwärme die folgende Krautportion auf .7 | die Krautportion von .4 ist warm/feucht; danach neue cthar-Nennung auf .7 |
| f116r.38 ZL `shey okaiin` | erwärme die folgende Zubereitung okaiin auf .38 | die Krautportion cthar von .35 ist warm/feucht |
| f15r.1 ZL/IT `shey daiin` | Mengenwert als Eingabe: falsche bekannte Rolle | kein vorheriger bekannter Materialträger |
| f116r.32 ZL/IT `shey ol` | „auch“ als Eingabe: falsche bekannte Rolle | kein vorheriger bekannter Materialträger |
| f77r.10 ZL/IT `shey qotaiin` | „abseihen“ als Eingabe: falsche bekannte Rolle | kein vorheriger bekannter Materialträger |
| f103r.26 IT `qotchy shey` | „zugeben“ erhält „erwärmen“ als Material | „zugeben“ erhält „warm/feucht“ als Material: weiterhin falsche Rolle |

IT liest auf f116r.38 dagegen `shey okain`: okain bleibt unbekannt. Die H/F-Bindung an cthar .35 bleibt auch dort bestehen; okain wird nicht mit okaiin vereinheitlicht.

Auf f8v.4 wird cthar genannt; .5 enthält chol chol, .6 Mengenwerte, .7 schließlich shey cthar. Die Fassung H/F kann somit lokal eine trockene und später warme/feuchte *frühere* Portionsnennung darstellen. Ein tatsächlicher Zustandswechsel wird daraus nicht abgeleitet: weder zeitliche Satzfolge noch Gegenstandsidentität noch Wirkung einer Handlung ist bewiesen. Die neue Nennung auf .7 wird nicht still mit .4 identifiziert. GDT625 hatte genau diese Verwechslung von Teilkontrast und Prozess bereits als Problem behandelt; seine älteren Wortwerte liefern keine unabhängige Lösung.

Die vollständigen Gegenbeispielabsätze beginnen auf f15r mit `tshor shey ...`, auf f116r.31 mit zahlreichen ungelösten Wörtern. Diese könnten Träger enthalten, sind im festen Glossar aber unbekannt. Das fehlende Subjekt wird ausdrücklich nicht durch einen imaginären Absatzgegenstand ergänzt.

## Vollständige Ergebnisse

| Modell | shey als Handlung/Eigenschaft | Ergebnis für alle 66 Positionen |
|---|---|---|
| V | Handlung | 3 angenommene Materialeingaben, 56 unbekannte Eingaben, 6 falsche bekannte Rollen, 1 fehlende Eingabe |
| H | Eigenschaft warm | 34 an vorheriges Material gebunden, 32 ohne bekannten Träger |
| F | Eigenschaft feucht | dieselben 34 Bindungen und 32 Lücken |

V hat über alle 114 Operationen 91 unbekannte, 7 als Material angenommene, 7 falsche und 9 fehlende Eingaben. H/F haben nur noch 48 Operationen: 35 unbekannte, 4 angenommene Materialien, 1 falsche und 8 fehlende Eingaben. Die Verringerung von sieben auf einen Rollenfehler beruht auf der Entfernung der 66 shey-Verpflichtungen, nicht auf sechs gelösten Übersetzungsproblemen. Gerade die sechs falschen shey-Eingaben werden zu sechs trägerlosen Eigenschaften.

H und F sind in **allen Bezügen dieses Tests identisch**. Der Wechsel warm↔feucht ist ein bloßer Bedeutungsersatz ohne hier geprüften unabhängigen Unterschied. Es wird weder H noch F aus Bindungszahlen gewählt. Ebenso wenig sind 34 Eigenschaftsbindungen und drei nominale Verbeingaben vergleichbare Erfolgsquoten; unterschiedliche Regeln erzeugen sie.

## Entscheidung

Die lokale Hypothese „Krautportion erwärmen“ bleibt möglich, aber ihr festes Grammatikmodell trägt nicht durch den Umfang. Die Alternative „Krautportion warm/feucht“ ist konkret ausgearbeitet und verändert die Bezugsrichtung; sie ist keine erfolgreiche Reparatur der problematischen Stellen. **Keine Auswahl eines shey-Wertes, keine bestätigte Wortübersetzung, kein vollständiger Rezepttext.**

Der nächste sinnvolle Versuch müsste den bisher fehlenden Absatzgegenstand ausdrücklich aus geschriebenen Formen gewinnen, statt weitere bekannte Wörter von Hand zu Substantiven umzubenennen. Der kurze Anfang `tshor shey tchaly shy chtols shey daiin` auf f15r ist dafür der konkrete Fall: eine gemeinsame Lesung der ganzen Eröffnungszeile muss beide shey-Nennungen und den Mengenwert erklären. Vor einem neuen Vertrag ist die vorhandene Arbeit zu tshor/Absatzköpfen primär zu prüfen. Eine implizite Subjektregel oder Vorwärtsbindung wird hier nicht nachträglich eingeführt.

## Prüfung und Abgrenzung

DECISION.md vor Erstellung der neuen Fassungen; motivierende Absätze bereits exponiert. run.py reproduziert alle Gruppen und Ereignisse; validate.py prüft V gegen die unveränderte W82-C-Tabelle und H/F mittels separater rückwärtiger Materialsuche. SOURCE_HASHES.json bindet die Eingaben. Lokaler Validator PASS. Keine neuen Bilder, Seiten, Kontakte oder externen Quellen; f84/f84r und Reserven geschlossen. Keine Signifikanz. Ideenproduzent fand nur bestehende verwandte Vorschläge, keine neue Karte. Die bekannten sieben globalen GDT600-Dateibindungsfehler bleiben unverändert.
