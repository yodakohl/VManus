# W81 — Zwei Materialien mit wechselndem Zustand?

Die konkrete Gegenüberstellung „Pflanzenpulver plus Flüssigkeit“ ergibt unter dem festen Bezugsvertrag **keinen tragfähigen globalen Sieger**. Beide Materialwörter erhalten trockene und feuchte Zustände. Das ist ein Ergebnis der angenommenen Bedeutungen und Bindungen, keine entschlüsselte Stoffeigenschaft.

Geprüft wurde die vollständige deduplizierte Vereinigung aus W80 und W78: 82 Absatztranskriptionen, 4572 Gruppen, alle 51 R1-Eigenschaftspositionen. 14 davon binden nach der eingefrorenen Letztmaterialregel otchy oder qoteey. Alle stehen in QUALITIES.tsv, alle vollständigen Absätze in PARAGRAPHS.json. ZL/IT sind alternative Transkriptionen, keine unabhängigen Zeugen. Keine neuen oder reservierten Seiten.

| Trägerhypothese | Eigenschaft im R1-Entwurf | Stellen, jeweils ZL/IT |
|---|---|---|
| otchy = T | chol = getrocknet | f19v.3, unmittelbar |
| otchy = T | shol = feucht | f44r.7, Träger auf .6 |
| qoteey = U | chol = getrocknet | f56v.3 zweimal; f79r.5; f112v.41 |
| qoteey = U | shol = feucht | f100r.15 |

Die wiederholten chol auf f56v sind keine unabhängigen Bestätigungen. Bei U ist keine der Eigenschaftsbindungen unmittelbar: f56v von .2 nach .3, f100r von .14 nach .15, f112v von .39 nach .41 und f79r von .2 nach .5. Dazwischen stehen ungelöste Wörter, die selbst Träger sein könnten. Die vollständigen Absätze machen diese Unsicherheit prüfbar; sie wird nicht nachträglich durch neue Wortwerte beseitigt.

## Konkrete Gegenlesungen

| Kandidat | f19v unter W79-Massenannahme | f44r | Prüfung |
|---|---|---|---|
| PL: T Pflanzenpulver, U aktuell flüssige Zubereitung | getrocknetes Pflanzenpulver, Masse C; gleiche Masse Flüssigkeit zugeben | Pulver zu U (ZL) bzw. chor (IT); später Pulver feucht | 8 Lesepositionen an 3 Loci schreiben der aktuell flüssigen U-Zubereitung getrocknet zu |
| LP: T aktuell flüssige Zubereitung, U Pflanzenpulver | getrocknete Flüssigkeit, Masse C; gleiche Masse Pulver zugeben | Flüssigkeit zu U (ZL) bzw. chor (IT); später feucht | 2 Lesepositionen an 1 Locus schreiben der aktuell flüssigen T-Zubereitung getrocknet zu |

Dies sind bedingte Teilparaphrasen; sämtliche nicht glossierten Wörter bleiben offen. Unter dem vorab definierten PHYSICAL_STATE-Modell widersprechen beide Kandidaten ihrer eigenen Festlegung „aktuell flüssig“. Ein trocknungsfähiger Ausgangsstoff, dessen Name nach der Trocknung erhalten bleibt, ist ausdrücklich eine andere Hypothese und durch diesen Vergleich nicht widerlegt. Pulver feucht zu nennen wurde nicht als Widerspruch gewertet.

Unter der vorab beibehaltenen HUMORAL_QUALITY-Alternative unterscheiden diese Befunde die beiden Stoffzuweisungen überhaupt nicht. Der Versuch entscheidet nicht zwischen den Qualitätsdeutungen. Die Ungleichheit 8:2 ist kein Rang oder Signifikanzmaß; verschiedene Trägerhäufigkeiten und abhängige Wiederholungen werden nicht als Evidenzgewicht ausgegeben.

## Was daraus folgt

Die konkretere vorläufige Lesung lautet: **zwei noch unbestimmte, möglicherweise trocken oder feucht vorliegende Zubereitungsmaterialien werden mit Mengenangaben kombiniert**. Auf f19v wäre T getrocknet und U würde in gleicher Masse zugesetzt; auf f44r wäre T später feucht. Das verbindet bekannte lokale Konsequenzen, beweist jedoch weder einen Zustandswechsel derselben Portion noch eine Pulver-, Wasser-, Öl- oder Saftidentität. Für U liefern die neu ausgewerteten Bezugsfolgen ebenfalls beide Zustände, jedoch ausschließlich mit ungesicherter Fernbindung.

GDT768 lässt chor als Blüten-/Fruchtteil richtungsunentschieden. GDT717 setzt einen ersetzbaren otchy-Zustands-/Stufenkern; GDT634 setzt qoteey als Kaltform II. Keine dieser primären Arbeiten bestätigt eine Stoffidentität; ihre anderen Lexika werden nicht eingemischt. char bleibt von chor getrennt. Die drei Operationsrollen-Kollisionen aus W80 bleiben ungelöst und verhindern weiterhin eine vollständige Rezeptlesung.

**Nächste konkrete Aufgabe:** die unbekannten Formen zwischen U und chol/shol in den vier hier vollständig dokumentierten Absätzen gemeinsam lesen, insbesondere den kurzen Übergang `qoteey cthar / ochey chol chol` auf f56v. Erst dann kann beurteilt werden, ob die Eigenschaften U oder einem noch unerkannten neuen Träger gelten. Keine automatische lokale Bindungsreparatur oder Stoffnamenergänzung.

## Reproduktion und Grenzen

DECISION.md vor der neuen Auswertung; run.py erzeugt Vollumfang, Bindungstabelle und beide Kandidaten aus hashgebundenen alten Artefakten. validate.py prüft die Bindungen über rückwärtige Suche unabhängig von der vorwärts laufenden Implementierung. Quellen bereits exponiert, keine unabhängige Bedeutungsbestätigung, keine Signifikanz. f84/f84r geschlossen. Der Ideenproduzent fand keine zusätzliche neue Karte und änderte keine Dateien. Globale bekannte GDT600-Bindungsschulden bleiben unverändert.
