# GDT1031: feste Synonym-Verkürzung nicht entscheidbar

**Ergebnis: NO_CAPACITY.** Der registrierte Versuch wurde ausgeführt und unabhängig
nachgerechnet. Keine Transkription erreicht alle vorab gesetzten Mindestmengen;
deshalb wurden weder Modellgewinne noch Nullwelten berechnet. Das ist weder eine
Bestätigung noch eine Widerlegung der sechs vermuteten Bedeutungsgruppen.

Die öffentliche Vorregistrierung ist Commit `d91ff65c8`. Anschließend wurden
unveränderte Programme und alle gebundenen Eingaben verwendet. Die Vorbereitung
begann um 09:59:12 UTC; Ausführung und unabhängige Prüfung waren vor 10:22 UTC
abgeschlossen. Budget einschließlich Veröffentlichung: bis 10:34:12 UTC.

## Vorhersagen und vollständige Auswertung

Für jede Familie war vorab dieselbe feste probabilistische Folge vorhergesagt:
Bei späterem Auftreten derselben vermuteten Bedeutung im vollständigen Absatz
werden kürzere ASCII-Transkriptionsformen bevorzugt, mit β = ln(3). Zwei ansonsten
gleiche Positionen mit maximalem Rang-/Längenabstand hätten 3:1 Gewicht für
lang→kurz. Dies sind weder gemessene Glyphenlängen noch bestätigte Synonyme.
Absatz, Familie, Zeilenrand, vorheriges `dy` und eigenes `dy` bleiben konstant.

| Vermutete Gruppe | Alle festen Formen (Länge) | IT2a mobile Blöcke / Positionen / Blätter | Familien-Mindestmenge erreicht | ZL3b mobile Blöcke |
|---|---|---:|---|---:|
| IS | qoky (4), r (1) | 5 / 10 / 5 | ja | 0 |
| LENTIL | qokain (6), okedy (5) | 0 / 0 / 0 | nein | 0 |
| NOURISHMENT | saiiin (6), san (3) | 0 / 0 / 0 | nein | 0 |
| NOT | sshey (5), sol (3), oltydy (6), or (2) | 3 / 7 / 3 | nein | 0 |
| LETTUCE | char (4), cheey (5) | 8 / 17 / 8 | ja | 0 |
| CURRENT_GREEKS | ysheeyqorar (11), y (1) | 0 / 0 / 0 | nein | 0 |

LENTIL war schon vor Datenöffnung unter dem eigenen-dy-Kontrollmerkmal analytisch
unbeweglich. Die Gruppe blieb ausdrücklich im Plan; sie wurde nicht ersetzt.
Die IT2a-Werte sind der gesamte passende Bestand, keine Auswahl günstiger Stellen.
Alle 841 Vorkommen mit ihren tatsächlichen Formen, Absätzen, Zeilen, Rängen und
Kontextmerkmalen stehen in [OCCURRENCES.json](artifacts/OCCURRENCES.json); alle
667 nichtleeren Blöcke einschließlich der unbeweglichen in
[BLOCKS.json](artifacts/BLOCKS.json). Diese Tabellen enthalten keine reparierten
Wörter. Die kompakte [Kandidatentabelle](artifacts/CANDIDATES.csv) nennt jede feste
Vorhersage und den Entscheid für alle drei Transkriptionen.

| Transkription | Ganze Absätze | Entwicklungsblatt ausgeschlossen | Quellenunsicher, ganzer Absatz | Literal | Mobile Absätze | Mobile Blöcke / Positionen / Blätter | Ausreichende Familien |
|---|---:|---:|---:|---:|---:|---:|---:|
| ZL3b | 659 | 22 | 607 | 30 | 0 | 0 / 0 / 0 | 0 |
| IT2a | 690 | 23 | 166 | 501 | 13 | 16 / 34 / 12 | 2 |
| RF1b | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |

Von den 30 literalen ZL-Absätzen enthalten 14 keine Familienform, 16 nur
unbewegliche Belege. Von den 501 literalen IT-Absätzen enthalten 176 keine
Familienform, 312 nur unbewegliche Belege und 13 mobile Belege. Die Scope-Tabelle
bewahrt alle 1349 Absätze einschließlich Ausschlüssen. Insgesamt enthält der
Quellvertrag 31238 ZL- und 30728 IT-Gruppen; dies sind **keine** Nenner unabhängiger
Bedeutungsbelege. Die starke Asymmetrie der literalen Abdeckung folgt dem
vorhandenen zeilenweisen `anchor_eligible`-Status und der vorab strikten
Ganzabsatzregel, nicht einem nachträglichen Texturteil.

Der Gate verlangte je Transkription mindestens 20 mobile Blöcke, 40 Positionen,
fünf physische Blätter und drei Familien mit jeweils mindestens vier Blöcken auf
drei Blättern. IT verfehlt Blöcke, Positionen und Familien; ZL verfehlt alle.
RF besitzt keinen Absatzvertrag. Deshalb bleiben sämtliche beobachteten
Modellgewinne **null/unberechnet**, nicht null Bit: keine Likelihoods, keine
p-Werte, keine Richtungsentscheidung, kein als bestätigt gezählter Kandidat.
Eine bestätigte gemeinsame Spur hätte außerdem ZL und IT bestehen müssen.

## Datenabgrenzung und verbleibende Mehrdeutigkeit

Die Entwicklungsblätter 76 und 80 wurden vollständig, auf allen Seiten,
ausgeschlossen. Die übrigen Absätze stammen ausschließlich aus dem bereits
projektweit exponierten GDT928-Paket. Dieser Blattabstand macht daraus keinen
historisch blinden Holdout. RAW507 hatte zusätzlich 15 Absätze desselben Pakets
für eine andere Frage inspiziert; auch diese Exposition wird nicht aufgehoben.
Quellenunsichere Absätze wurden vollständig ausgeschieden, ohne ihre Wörter
für die Auswertung zu lesen. f84/f84r und f116v wurden nicht geöffnet; keine neue
Quelle, Abbildung, Reserve oder Transkriptionsregel kam hinzu.

Die Lesarten ZL/IT/RF beschreiben dasselbe Manuskript und sind keine unabhängigen
Handschriften. Selbst ein positiver Ausgang hätte nur dieses bedingte
Schreibgesetz unterstützt: semantisch opake Klassen mit denselben Mitgliedern
machen identische Vorhersagen. IS, LENTIL, LETTUCE usw. bleiben alle geratene
Bezeichnungen. Ein negatives Gesetz hätte die Synonymdeutung ohne zusätzliche
Schreiberannahme ebenfalls nicht allgemein widerlegt. Unabhängige
Bedeutungsbestätigungskapazität: **0**; bestätigte Wörter: **0**.

## Prüfung und Entscheidung

Der unabhängige [Validator](src/validate.py) rekonstruiert sämtliche Scope-,
Vorkommens-, Block- und Kapazitätstabellen direkt aus den gebundenen Eingaben,
ohne den Hauptlauf zu importieren. Er bestätigt alle acht Lockdateien und den
korrekten Verzicht auf Scores: [VALIDATION.json](artifacts/VALIDATION.json), PASS.
Die beiden unterschiedlichen Partitionsfunktions-Implementierungen und der
feste Nullablauf sind synthetisch vorgeprüft; sie wurden mangels Kapazität
**nicht** auf Manuskriptscores ausgeführt. PASS ist hier Reproduktionsprüfung,
keine positive Manuskriptlesung.

**Die unveränderte Route endet als nicht entscheidbar.** Kein Absenken der
Schwellen, Weglassen der dy-Kontrolle, Ersetzen unproduktiver Familien oder
nachträgliches Scoren einzelner günstiger Gruppen. Ein neuer Versuch bräuchte
einen eigenständig begründeten neuen Vorhersagevertrag oder neue zulässige
Belege; der vorhandene Kapazitätsbefund allein legitimiert keine Reparatur.
Die gesamte historische Ideensuche wurde nicht als Gegenkontrolle simuliert;
es wird keinerlei Signifikanz der Gesamtsuche behauptet.

Reproduktion:

```sh
python experiments/yolo/gdt1031_synonym_recurrence_shortening/src/run.py
python experiments/yolo/gdt1031_synonym_recurrence_shortening/src/validate.py --execute
```
