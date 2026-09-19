# GDT983 — qoqokeey bleibt ein isolierter Expansionskandidat

**NO_CONTEXT_SUPPORT.** Die feste Familie `qoqo` plus mindestens ein weiteres
Kleinbuchstabenzeichen besitzt in den zugelassenen P-Zeilen nur eine Gesamtform:
`qoqokeey`, an genau der bereits bekannten Stelle f75v.39. Die Wiederholung des
Anfangs ist damit in diesem Bestand keine belegte produktive Formfamilie.
Das ist keine allgemeine Widerlegung bedeutungstragender Reduplikation.

Die drei vorher registrierten Vorhersagen bleiben verschieden und unentschieden:

| Kandidat | Vorhergesagte Expansion | ZL / IT / RF Rohvorkommen des Kandidaten | ZL / IT / RF Expansionen in geeigneten vollständigen Absatzzeilen | Passende Kontexte |
|---|---|---|---|---|
| DUP | qokeey qokeey | 1 / 1 / 1 | 3 / 11 / 0 | 0 |
| ECHO | qo qokeey | 1 / 1 / 1 | 0 / 1 / 0 | 0 |
| SINGLE | qokeey | 1 / 1 / 1 | 124 / 257 / 0 | 0 |

[Die vollständige Kandidatentabelle](artifacts/CANDIDATE_TABLE.tsv) enthält alle
neun Kombinationen von Kandidat und Transkription. Die Nullspalte für RF bedeutet
hier fehlende vollständige Absatzabdeckung, nicht Abwesenheit der Schreibungen.
Die Vorkommen sind Lesungen derselben Handschrift, keine unabhängigen Replikate.

## Warum keine Expansion ausgewählt wird

Der registrierte Vergleich verlangt einen tatsächlichen unmittelbaren Nachbarn
auf beiden Seiten, auf derselben unverändert geeigneten Zeile. Für die einzige
Kurzform gibt es **null geeignete Vergleichspositionen**: IT f75v.39 steht am
Zeilenanfang; in ZL ist die gesamte Zeile zusätzlich wegen einer bereits bekannten
unsicheren kleinen Leerstelle bei qol/sheedy ungeeignet. RF bietet in GDT928 keine
eigenständigen vollständigen Absätze. Die Nulltreffer sind deshalb keine beobachteten
Bedeutungswidersprüche. Der Test hat keine Kapazität, die drei Bedeutungsmechanismen
zu unterscheiden. Schon das Fehlen einer zweiten Kurzform verhindert die vorab
verlangte familienübergreifende Übertragung.

Die Doppelung selbst ist realer überlieferter Wortlaut. Unter der festen
Absatz-/Zeilenregel sind die ZL-Vorkommen f103r.53, f108v.46 und f75v.45; IT enthält
zusätzlich f103r.46, f103r.48, f103v.1, f107v.44, f108r.6, f108v.40, f111r.20 und
f112v.16. Einige dieser Expansionen stehen am Rand und haben deshalb selbst keine
zwei Vergleichsnachbarn. Alle werden erhalten, nicht nur passende Einzelstellen.

Eine nützliche Grenze zeigt die bereits exponierte ganze Zeile f108r.6, im
Wortlaut aller drei Transkriptionen:

```
ol cheol qo qokeey qokeey qokeedy sheoky otedy qotey qokchey chdar aiin y
```

Hier überlappen `qo qokeey` und `qokeey qokeey` tatsächlich. Ihr gemeinsames
Vorkommen kann keine der beiden Analysen von qoqokeey auswählen. Insbesondere
darf der ECHO-Treffer nicht als exklusiver Beleg gegen DUP ausgegeben werden.
Die Stelle war bereits in GDT863 als einer der unmittelbaren qo-Echos enthalten;
sie wird hier nicht als neu entdeckte Handschriftenstelle ausgegeben.

## Umfang, Widersprüche und verbleibende Bedeutungen

Der Rohdurchgang umfasst 3.768 ZL-, 3.767 IT- und 3.768 RF-P-Zeilen. Er bewahrt
233 Kandidaten-/Wiederholungspositionen in 213 vollständigen Quellzeilen:
ZL 1 Kurzform + 78 genaue qo-Wortdoublets + 6 getrennte qo-Echos;
IT 1 + 76 + 6; RF 1 + 59 + 5. Diese Rohinventare sind nicht nachträglich als
strenge Kontexttreffer gewertet. Unsichere Zeichen und Abstände stehen vollständig
in [SOURCE_LINES.json](artifacts/SOURCE_LINES.json).

Der eigentliche Vergleich nutzt alle 659 ZL- und 690 IT-Absätze aus GDT928.
Zwei Kurzformpositionen, 396 geeignete Expansionspositionen und sämtliche
vorhergesagten Verknüpfungen wurden ausgewertet. Keine Verknüpfung erfüllt die
festen Flankenbedingungen. [PREDICTIONS.json](artifacts/PREDICTIONS.json),
[COMPRESSED_OCCURRENCES.json](artifacts/COMPRESSED_OCCURRENCES.json) und
[EXPANSION_OCCURRENCES.json](artifacts/EXPANSION_OCCURRENCES.json) machen die
Vorhersage und die tatsächliche fehlende Vergleichskapazität getrennt sichtbar.

- DUP könnte Wiederholung einer Handlung, Betonung, Mehrzahl oder Wiederaufnahme
  eines Nomens ausdrücken. Die Schreibungsannahme wählt keines davon.
- ECHO könnte eine getrennte Konstruktion oder einen Schreibansatz abbilden;
  ein Fehler oder Neustart wird nicht als historische Tatsache behauptet.
- SINGLE könnte gleiche Bedeutung bei graphischer Zusatzwiederholung zulassen;
  keine Transkription wird dafür korrigiert oder gekürzt.
- Auch keine dieser drei Möglichkeiten kann zutreffen. Die Ergebnisse rechtfertigen
  weder qoqokeey=bereite aus GDT982 noch qokeey=Feuer oder Erwärmen aus alten Entwürfen.

**Entscheidung:** Keine Expansion bevorzugen, keinen Wiederholungsmarker übersetzen.
Die Abkürzungsroute wird ohne neue konkrete Inhaltsunterscheidung nicht verbreitert.
GDT910s ursprünglicher Nicht-Wiederkehrbefund bleibt erhalten; dies ist ein gesonderter
Test der festgelegten Familie in später bereits zugelassenem Material. GDT982s
fünf vollständige hypothetische Zeilenfassungen bleiben unverändert.

## Reproduktion und Fortsetzung

Öffentliche Registrierung: `1b68f6a39`, vor der ersten Ausführung. Die Regeln und
alle Quellen sind in PREREG_LOCK.json gebunden. Der separat geschriebene Validator
importiert den Runner nicht und rekonstruiert das vollständige Rohinventar, alle
Vorhersagen, Absatzpositionen, Verknüpfungen und Tabellenfelder: PASS. Gleicher Autor;
Softwareprüfung ist keine unabhängige Bedeutungsprüfung. Keine neue semantisch
gewertete Relationskante; aus Nullverknüpfungen entsteht kein GDT388-Nachweis.

Unabhängige Bestätigungskapazität: **0**. Keine geeignete Gegenkontrolle der gesamten
historischen Suche, deshalb keine Signifikanzbehauptung. Kein bestätigtes Wort.
Alle Daten waren im Projekt exponiert; keine Reserve, f84/f84r oder f116v geöffnet,
kein neues Bild, keine Kontakte. Abwechselnde Transkriptionen schaffen keinen Holdout.

Vorbereitung begann 23:05:26 UTC am 19. September 2026; Protokoll, Durchführung und
Validierung waren um 23:20 UTC abgeschlossen, innerhalb des 35-Minuten-Budgets.
Das ist ein kurzer abgeschlossener Teilversuch im mindestens zehnstündigen
Nutzerauftrag (frühestes Blockende 20. September 09:05:26 UTC), keine Behauptung
zehn bereits geleisteter Stunden. Der nächste Auswahlgegenstand ist eine tatsächlich
inhaltliche Beziehung aus dem parallel ergänzten RAW-Vorrat; vor Auswahl sind deren
genaue Vorgänger und Konsequenzen zu prüfen. Kein weiterer identischer Mustersuchlauf.
