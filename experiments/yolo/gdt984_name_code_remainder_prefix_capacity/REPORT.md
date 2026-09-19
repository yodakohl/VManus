# GDT984 — 730 weitere Kombinationen ausgeschlossen, kein Name ausgewählt

**PREFIX_PROJECTION_WEAK.** Von 8.986 noch offenen Namens-/Seitenkombinationen
bestehen 8.256 die neue notwendige Bedingung, also **91,8763 %**. 730 scheitern.
Die vorher festgelegte 90-%-Grenze greift: Diese Projektion wird nicht schrittweise
weiter ausgebaut. Es gibt weiterhin keinen vollständigen gemeinsamen Code und
kein ausgewähltes oder bestätigtes Pflanzenwort.

## Was diesmal tatsächlich vorausgesagt wurde

Der unveränderte GDT963-Entwurf verlangt einen gemeinsamen präfixfreien Code für
vier vollständige Dioskurides-Abschnitte auf vier verschiedenen physischen Blättern.
GDT976s zwei Namenscodes waren bisher nur mit freien Zwischenräumen verglichen.
Jetzt muss **jeder einzelne übrige Quellausdruck** eine nichtleere Zeichenfolge
besitzen, die mit keinem der beiden Namenscodes im Präfixverhältnis steht.
Alle 613 Quellpositionen bleiben erhalten: sechs exakte Namenpositionen und
607 übrige Positionen, einschließlich aller 255 einmaligen Atome.

Kein neuer Name, Lautwert, Wortabstand, Quellalias oder Decoder wurde eingesetzt.
Das ist eine notwendige Folge des alten Schreibvertrags. Wiederholte andere
Atome dürfen in dieser ausdrücklich gelockerten Prüfung noch unterschiedliche
Werte erhalten; ihre gemeinsamen Bedeutungen wurden nicht gelesen. Im Gegensatz
zu GDT978 dürfen auch einmalige Werte nicht mit einem der Namen kollidieren.
Die beiden Projektionen prüfen verschiedene notwendige Bedingungen; keine wird
als Ersatz für den vollständigen Code ausgegeben.

## Alle Kandidaten und Ergebnisse

[CASE_PREDICTIONS.tsv](artifacts/CASE_PREDICTIONS.tsv) nennt sämtliche 8.990
ursprünglichen Kandidaten mit ihren unveränderten konkreten Codes, zwei festen
Seiten und dem alten Status. Die Bedeutung jedes der 613 erwarteten Slots steht
in [SOURCE_PREDICTIONS.json](artifacts/SOURCE_PREDICTIONS.json). Die Regeln und
Eingaben wurden öffentlich vor der Ausführung in `8fafb29c0` registriert; die
Tabellen wurden vor der Zielanpassung geschrieben.

| Tatsächlich geprüfte Folge | Kandidaten | Konsequenz |
|---|---:|---|
| I.1 lässt keine passende vollständige Zerlegung zu | 352 | diese Namens-/Seitenkombination ausgeschlossen |
| I.1 besteht, IV.20 lässt keine passende Zerlegung zu | 318 | diese Kombination ausgeschlossen |
| Beide festen Seiten bestehen, aber keine Ergänzung auf vier verschiedenen Blättern | 60 | diese Kombination ausgeschlossen |
| Vollständige Zerlegungen unter der gelockerten Bedingung auf vier Blättern | 8.256 | nur partielle Kandidaten |
| Bereits in GDT977 ausgeschlossen | 4 | unverändert übernommen, kein neuer GDT984-Erfolg |
| Unentschiedene neue Rechnungen | 0 | keine Zeitüberschreitung oder verlorenen Fälle |

[CANDIDATE_TABLE.tsv](artifacts/CANDIDATE_TABLE.tsv) berichtet jeden einzelnen
Fall, einschließlich der Zahl möglicher Vier-Blatt-Ergänzungen.
[NAME_CLASS_TABLE.tsv](artifacts/NAME_CLASS_TABLE.tsv) gruppiert die festen
geordneten Codepaare. Von 1.318 vorher noch aktiven Klassen bleiben 1.207;
111 werden neu ausgeschlossen. Zwei weitere Klassen waren schon ausgeschlossen.

| Hypothetischer Name | Vorher mögliche Zeichenfolgen | Verbleibend | Neu vollständig entfallene Werte |
|---|---:|---:|---|
| IRIS | 52 | 52 | keine |
| XIPHION | 138 | 136 | kshedy, pchey |

Diese Strings sind unter dem ursprünglichen Vertrag Codewerte, die sogar
über geschriebene Gruppen hinweg reichen dürfen. Weder ein ganzer Voynich-Ausdruck
noch ein Name ist damit übersetzt. Gleiche Codepaare mit mehreren möglichen Seiten
bleiben in diesem Test mehrdeutig; wechselnde Transkriptionen liefern keine
unabhängigen Manuskripte.

## Ein konkreter Widerspruch

Kandidat 65 setzt auf f17v `IRIS=pch` und `XIPHION=o`. Der vollständige Zieltext
beginnt `pchodolchorfchyopy...`, die feste Quelle beginnt `IRIS, ILLYRIA, LEAF, ...`.
Nach `pch` muss der nächste Quellausdruck ILLYRIA beginnen. Dort steht aber `o`:
Jeder nichtleere Code für ILLYRIA würde mit dem vollständigen XIPHION-Code anfangen.
Das verbietet der vorausgesetzte präfixfreie Code. Kein längerer Wortabschnitt
kann diesen konkreten Präfixkonflikt beseitigen.

Dieser anschauliche Fall wurde erst nach der Gesamtauswertung als Illustration
gewählt. Er bestimmt weder die Kandidatenmenge noch die Entscheidung. Sämtliche
441.530 lokalen Klassen-/Rollen-/Seitenfolgen sind in
[LOCAL_RESULTS.json.gz](artifacts/LOCAL_RESULTS.json.gz) erhalten: 274.528 negative
und 167.002 positive lokale Zerlegungen. Diese Zahlen sind keine ebenso vielen
unabhängigen Lesungen oder Bedeutungsbeweise.

## Was die positiven Fälle noch nicht leisten

[CLASS_RESULTS.json.gz](artifacts/CLASS_RESULTS.json.gz) erhält alle passenden
Seiten je Rolle und Klasse. [BOUNDARY_WITNESSES.json.gz](artifacts/BOUNDARY_WITNESSES.json.gz)
zeigt für jede der 1.207 überlebenden Klassen ein vollständiges Vierseitenbeispiel,
mit genau einer Grenze je Quellatom und ohne ausgelassene Zielzeichen.

**Keines dieser 1.207 gespeicherten Beispiele ist schon ein gemeinsames Wörterbuch:**
In jedem erhalten wiederholte Nicht-Namenatome unterschiedliche Zeichenfolgen.
Das wurde nach dem Ergebnis eigens am vollständigen Inhalt der gespeicherten
Beispiele geprüft, siehe [INTERPRETATION_AUDIT.json](artifacts/INTERPRETATION_AUDIT.json).
Es ist eine Grenze dieser Existenzzeugen, keine Widerlegung anderer möglicher
vollständiger Codes. Die gemeinsame Bedeutung der übrigen Wörter bleibt gerade
jene offene Verpflichtung, die eine echte Lesung erfüllen müsste.

Die ursprünglichen GDT963- und GDT978-UNKNOWNs werden weder in PASS noch in FAIL
umbenannt. GDT976s ursprüngliche Menge und GDT977s vier Ausschlüsse bleiben bytegleich.
Die neuen 730 Ausschlüsse betreffen nur den übernommenen wörtlichen Gesamtcode.
Unklare Transkriptionen und andere Schreibmodelle werden nicht mitverworfen.

## Prüfung, Datenabgrenzung und Entscheidung

Die genaue Berechnung nutzt erreichbare Zeichengrenzen. Ein anderer Prüfer im
Code verwendet explizite endliche Grenzmengen als Bitmengen und konstruiert eigene
positive Zerlegungen. Er importiert weder Runner noch dessen Modell. Alle 441.530
lokalen Folgen, alle 8.990 Tabellenzeilen, alle 1.320 Klassenzeilen und sämtliche
vollständigen Beispielgrenzen stimmen: **PASS**, keine ungelöste Klasse. Gleicher
Autor; unabhängige Berechnung ist keine unabhängige Bedeutungsprüfung.

Vor Zielzugriff wurden beide Implementierungen gegen vollständiges Aufzählen
kleiner synthetischer Texte geprüft. Die Hauptrechnung dauerte 15,889 Sekunden
mit 32 Arbeitern, die vollständige Gegenprüfung 9,857 Sekunden. Vorbereitung,
Quellenprüfung, Beweis und Veröffentlichung benötigen zusätzliche Arbeitszeit;
Rechenzeit oder Testanzahl werden nicht als Entzifferungsgewinn ausgegeben.

Alle verwendeten Seiten waren bereits exponiert. Die unveränderten IT-Domänen
umfassen 33/101/101/100 Rollen-Seiten; die früheren ZL/RF-Kapazitätsgrenzen und
254 unklaren ursprünglichen Seitenrahmen bleiben bestehen. Keine neue Bild- oder
Textzulassung, keine Reserveöffnung, f84/f84r/f116v geschlossen, keine Kontakte.
Unabhängige Bestätigungskapazität **0**. Keine Suchgegenkontrolle, deshalb keine
Signifikanzbehauptung. Kein semantisch bewerteter GDT388-Relationsbeleg.

**Weiterer Forschungsentscheid:** Die Namensprojektion bleibt zu mehrdeutig für
eine Auswahl. Keine weitere kleine Zusatzbedingung und kein automatischer längerer
Solverlauf. Der nächste aktive Gegenstand wird eine zusammenhängende explorative
Inhaltslesung mit einer anderen überprüfbaren Folge; neue RAW-Entwürfe sind
Vorschläge, keine bereits zugelassenen Versuche. Der Zehnstundenauftrag läuft
weiter; dieser Teilversuch allein erfüllt ihn nicht.

Der Teilblock begann mit Auswahlprüfung um 23:23 UTC am 19. September; Rechnung
und vollständige Gegenprüfung waren vor 23:45 UTC beendet. Der inklusive
Vorbereitungs-/Veröffentlichungscheckpoint ist 00:23 UTC am 20. September.
Der ganze Nutzerblock begann 23:05:26 UTC und endet frühestens 09:05:26 UTC.
