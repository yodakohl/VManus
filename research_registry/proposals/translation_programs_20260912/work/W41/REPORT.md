# W41 — Arbeitsübergabe und anschließender Materialzugriff

**Eine neue lokale Arbeitslesung ist formulierbar: „Übergib Flüssigkeit A an Bearbeiter B; B arbeitet weiter; B erwärmt A.“** Sie entsteht auf f83r.6–8 nur unter der alten T0-Regel, nach der das erste Material das Hauptthema bleibt. Der neue Ganzwortkandidat ist `qoky ≈ der genannte Empfänger arbeitet weiter`. Er ist nicht als Wortübersetzung ausgewählt: Beim ebenfalls alten L1-Bezug auf das zuletzt genannte Material entsteht an derselben Erwärmung ein Zugriffskonflikt. Vier weitere qoky haben keinen genannten Empfänger.

Alle sieben Records /51Zeilen/341Gruppen wurden in sechs Fassungen ausgeführt. [DECISION.md](DECISION.md) und [SPEC.json](SPEC.json) wurden vor der Rechnung geschrieben. IDEA000182, Quelle ausschließlich die bereits exponierte P12-f83r-Projektion. P12, P07, P10, S02 und W40 bleiben unverändert; keine neue Seite und kein reservierter Text geöffnet.

## Konkrete Vorhersagen der sechs Kandidaten

V behält P12s Gefäß- und Einfülllesung. H0 liest qokaiin als empfangenden Bearbeiter B und qokeedy als Übergabe des Materials an B; der ergänzte Anfangsakteur A0 arbeitet weiter. H1 ergänzt für **alle sieben qoky** die Rollenbehauptung „B arbeitet weiter“. Diese ändert den Akteur, aber übergibt selbst kein Material. In V/H0 bleibt qoky ungelesen. Erwärmen verlangt in H0/H1 den Bearbeitungszugriff des aktuellen Akteurs; eine Übergabe überträgt ihn an B. Gemeinsamer Zugriff oder eine ungeschriebene Rückgabe sind nicht zugelassen. Dies sind gewählte Annahmen, keine historisch erkannte Eigentumsordnung.

| Kandidat | Feste Vorhersage | Folgen an sämtlichen 20 Handlungen | Konflikte / offene Verpflichtungen | Übergabe→qoky→Erwärmung |
|---|---|---|---|---|
| L1/V | Letztes Material, Gefäß, ein ergänzter Handelnder. | 14 mit Patient/erforderlichem Empfänger, 6 unvollständig. | Kein Personenzugriff getestet; alle 7 qoky offen. | Nicht modelliert. |
| T0/V | Erstes Material bleibt Thema; sonst V. | Ebenfalls 14/6, teilweise andere Patienten. | Gleichfalls kein Personenzugriffstest; 7 qoky offen. | Nicht modelliert. |
| L1/H0 | Übergabe an Bearbeiter B; A0 bleibt Handelnder. | 8 anfängliche Zugriffsanforderungen, 6 spätere Übereinstimmungen, 6 ungebunden. | Kein Zugriffskonflikt, aber 7 qoky und Vorgeschichte bleiben offen. | Kein Akteursmarker gelesen. |
| T0/H0 | Dasselbe mit fortbestehendem Hauptmaterial. | 5 Anfangsanforderungen, 7 Übereinstimmungen, 2 Konflikte, 6 ungebunden. | f83r.8:5 und .16:5: A0 soll bereits an B übergebenes A bearbeiten. | Kein Akteursmarker gelesen. |
| L1/H1 | Nach jedem qoky arbeitet der genannte B; letztes Material. | 4 Anfangsanforderungen, 3 Übereinstimmungen, 1 Konflikt, 12 ungebunden. | .8:5 verlangt C bei B, Zugriff liegt noch bei A0. Vier Marker ohne Empfänger; neun Handlungen ohne Akteur. | Kein vollständiger Anschluss. |
| T0/H1 | Derselbe Marker; Hauptmaterial bleibt A. | 2 Anfangsanforderungen, 5 Übereinstimmungen, 1 Konflikt, 12 ungebunden. | .16:5 bleibt Zugriffskonflikt; dieselben vier fehlenden Empfänger/neun fehlenden Akteure. | Ein lokaler Anschluss auf .6–8 mit drei abhängigen Markernennungen. |

Anfangsanforderungen sind keine bestätigten Zugriffsrechte: Das unbekannte Anfangskonto wird so festgelegt, wie die erste Handlung es benötigt. Die Zahlen über fehlende Rollen überlappen. Alle Modelle behalten die alten drei fehlenden Patienten und vier fehlenden Übergabe-/Gefäßempfänger; vier ungebundene Marker sind zusätzliche Markerfälle, nicht vier weitere alte Handlungen. Die fehlenden Akteure werden nach diesen Markern fortgeführt, statt kostenlos A0 wieder einzusetzen. Nach Fehlern bleibt das Zugriffskonto unverändert; spätere Fälle tragen `prior_problem` und sind nicht unabhängige Widerlegungen.

[Alle Kandidaten](CANDIDATES.tsv), [alle 162 Ereigniszeilen mit vollständigem Vorher-/Nachherkonto](EVENTS.tsv), [alle 2046 wortweisen Ausrichtungen](ALIGNMENT.tsv). Eine Fassung ohne Zugriffskonto gewinnt nicht dadurch, dass sie keine Zugriffskonflikte zählen kann.

## Die positive lokale Folge und ihr direkter Gegentest

1. f83r.6:7 `qokeedy`: A0 übergibt das gebundene Material A an B. Beide Referenzmodelle binden hier A.
2. .6:8 `lchedy`: Material C wird genannt. T0 behält A als Thema, L1 wechselt den Patienten zu C. Die Nennung allein übergibt C nicht.
3. .6:9 `qoky`: H1 setzt B als handelnde Person. .7:4 und .8:4 nennen dieselbe Rolle erneut, ohne eine neue Übergabe oder einen weiteren Akteur einzuführen.
4. .8:5 `chedy`: T0 verlangt, dass B das ihm übergebene A erwärmt. Das Konto erlaubt es. L1 verlangt stattdessen C, dessen notwendiger Zugriff seit der früheren C-Erwärmung .4:2 bei A0 liegt. Das Konto meldet ACCESS_CONFLICT.

Der vollständige Zwischenabschnitt zwischen Übergabe und späterer Erwärmung lautet:

```text
lchedy qoky solshed lsheedy qeeedy qoky o qol rsheedy qokedy qoteedy qoteedy pchedal otedy shecthedchy qoky
```

Das sind 16 Gruppen, davon **zwölf ungelesen** in diesem Versuch. P15s Aspekt-/Wiederholungswerte und S02s Entnahmen werden nicht hineingelesen. Die angenommene geschlossene Zugriffsgeschichte beweist nicht, dass dort keine weiteren realen Übergaben beschrieben werden.

[CHAINS.tsv](CHAINS.tsv) nennt sämtliche drei Markerzeugen .6:9/.7:4/.8:4 zwischen derselben Übergabe und derselben späteren Handlung. **Drei Markerzeugen sind nur ein Übergabe-/Handlungspaar**, nicht drei erfolgreiche unabhängige Folgen. Der erste Builder führte nur den letzten Marker in der Kettentabelle; vor Abschluss wurde die Ausgabe auf alle drei bereits geprüften Marker erweitert. Wortwerte, Konten und Erfolgsbedingungen änderten sich nicht. Die abschließende getrennte Prüfung enumeriert alle Markerzeugen.

## Alle sieben qoky und der verbleibende Gegenfall

| qoky | Geschriebener Empfänger vorher? | Konsequenz H1 in beiden Bezugsmodellen |
|---|---|---|
| f83r.6:9 | B vorhanden | A0→B; kein Materialtransfer durch den Marker. |
| f83r.7:4 | B vorhanden | B arbeitet weiter; dieselbe Rollenbehauptung. |
| f83r.8:4 | B vorhanden | B arbeitet weiter; nächste Erwärmung unterscheidet L1/T0. |
| f83r.20:8 | Kein B in P3 | Empfänger fehlt; Akteur danach ungeklärt. |
| f83r.26:3 | Kein B in P4 | Empfänger fehlt; Akteur danach ungeklärt. |
| f83r.30:4 | Weiter kein B in P4 | Weiter ungeklärt; kein neuer Akteur ergänzt. |
| f83r.36:6 | Kein B in P5 | Empfänger fehlt; Akteur danach ungeklärt. |

**Der zweite Record widerspricht der vollständigen T0/H1-Arbeitsfolge:** .14:2 übergibt A an B, anschließend fehlt jedes qoky. Auf .16:5 soll weiterhin A0 dasselbe A erwärmen. Die neue Markerlesung erklärt diesen Fall nicht. Eine Rückgabe, gemeinsame Arbeit oder andere Wortbedeutung könnte einen anderen Vertrag ergeben, wird hier nicht ergänzt. L1 bindet dort C und vermeidet diesen speziellen Konflikt, hat dafür den anderen Konflikt auf .8:5. Keine stellenweise Mischung von L1 und T0 wurde gewählt.

## Entscheidung und verbleibende Mehrdeutigkeit

**Den lokalen T0/H1-Entwurf als bedingte Arbeitslesung dokumentieren; qoky nicht global als Arbeitsübernahme übersetzen.** Kein Kandidat wird durch Fehlerzählung ausgewählt. T0/H1 erklärt einen Rollenanschluss, lässt aber den Gegenfall und vier ungebundene Marker stehen. L1/H0 bleibt ohne Zugriffskonflikt, dafür ohne jede Erklärung von qoky. Gefäß-/Orts- und andere Personenfassungen sind dadurch nicht entschieden. Gleiches Materialwort könnte zudem verschiedene Portionen bezeichnen (P12 FRESH); W41 setzt ausdrücklich nur REUSE an.

H1 besitzt 57 Positionen mit Bedeutungsannahmen und 284 ungelesene Gruppen; V/H0 behalten 50/291. Diese sieben zusätzlich formulierten Positionen sind ein **Hypothesenzuwachs, keine sieben Übersetzungen**. B ist eine Arbeitsrolle, keine identifizierte Person. Das gesamte Blatt bleibt weit von einer plausiblen vollständigen Lesung entfernt. Kein sofortiger Folgeversuch zur Reparatur der Empfänger- oder Akteursbindung ausgewählt.

[VALIDATION.json](VALIDATION.json): PASS. Getrennter Code rekonstruiert sämtliche alten L1-/T0-Patienten-/Empfängerbindungen aus dem Rohtext, prüft jeden der 162 Ereignisübergänge und alle 2046 Ausrichtungszeilen sowie sämtliche positiven Markerzeugen. Gleicher Bearbeiter, keine unabhängige Bedeutungsprüfung. Unabhängige Bestätigungskapazität für jeden Kandidaten **0**; alle Belege stammen aus dem exponierten f83r. Keine Signifikanz, bestätigten Wort-/Pflanzennamen oder scorefähige GDT388-Relation. f84/f84r und alle Reserveseiten blieben geschlossen.

```sh
python research_registry/proposals/translation_programs_20260912/work/W41/build.py
python research_registry/proposals/translation_programs_20260912/work/W41/validate.py
```

Repository-Prüfung: W41-Validator und Ideenregistry PASS. Die globale Prüfung behält die acht bekannten Altfehler (sieben ungebundene GDT600-Dateien, veralteter Experimentindex); keine dieser Dateien verändert. Der separate Datenschutz-/Umfangsscan prüft ausschließlich den exakten zur Veröffentlichung vorgemerkten Dateistand und ersetzt diese globale Prüfung nicht.
