# P26 — Ein Verfahrensname mit zwei Parametern

Der erste Durchgang liefert eine konkrete, begrenzte Verfahrenslesung: „Material erhitzen und in ein Gefäß überführen“, später mit einem anderen Material wiederholt. Alle sieben qoky-Vorkommen wurden berücksichtigt: eine mögliche Definition, sechs zwingende Aufrufe. Drei Aufrufe haben beide Parameter; drei nicht. Eine spätere Zustandsaussage bekommt nur durch die Expansion einen Erzeuger. Das ist ein bedingter Erklärungsgewinn gegenüber dem Ergebnisnomen, keine Identifikation von qoky.

Alle 341 Gruppen der sieben f83r-Records sind in beiden Fassungen enthalten. Sieben ganze Wortannahmen betreffen 70 Positionen; 271 bleiben offen. P26 ist deshalb ein partieller erster Durchgang, keine vollständige Kapitelübersetzung. Die ursprüngliche P26-Proposaldatei und frühere Versuche bleiben unverändert.

## Definition und vollständiges Aufrufkonto

[Verfahrenskarte](PROCEDURE.md): qokaiin=Material A, shedy=Material B, lchedy=Gefäß, chedy=erhitze, qokeedy=überführe, qokedy=ist vorbereitet. M liest qoky als Verfahrensnamen; N als „Ansatz“. Alle Werte sind frei gesetzte Hypothesen. Gleiche Materialform bedeutet innerhalb eines Records dasselbe Objekt; neue Records beginnen ohne Kontext.

| qoky-Stelle | Geschriebene Parameter | Anfang und vollständige Expansion M | Ergebnis / Problem |
|---|---|---|---|
| .6:9 | A .6:5; Gefäß .6:8 | Vorangehendes .6:6 Erhitzen und .6:7 Überführen wird als Definition gelesen | Bereits erzeugtes Ergebnis; nachgestellte Namensgebung zusätzlich angenommen |
| .7:4 | A .6:5; Gefäß .6:8 | Erhitze A; überführe A in G | Vollständig, aber bereits vorbereitete Portion erneut bearbeitet |
| .8:4 | A .6:5; Gefäß .6:8 | Erhitze A; überführe A in G | Vollständig, zweite Wiederbearbeitung; nächste explizite Erhitzung .8:5 beginnt erneut |
| .20:8 | B .19:9; Gefäß .19:11 | Erhitze B; überführe B in G | Vollständiger Aufruf mit anderem Material; vorher kein erzeugter Vorbereitungszustand |
| .26:3 | weder Material noch Gefäß | Erhitze ?; überführe ? in ? | Zwei fehlende Parameter, kein fertiges Ergebnis |
| .30:4 | B .28:5; kein Gefäß | Erhitze B; überführe B in ? | Ein fehlender Parameter; vorher erhitzt, keine Überführung erzeugt |
| .36:6 | kein Material; Gefäß .34:2 | Erhitze ?; überführe ? in G | Ein fehlender Parameter, kein fertiges Ergebnis |

Die N-Gegenfassung nennt an allen sieben Stellen einen „Ansatz aus X in G“ mit denselben linken Bezügen und denselben nominalen Bezugslücken. Sie führt dort keine Handlung aus. [Alle Aufrufe M](CALLS_M.tsv), [alle Nennungen N](CALLS_N.tsv) enthalten exakte Anfangs-/Endzustände. Niemandem wird stillschweigend eine neue Portion zugewiesen.

## Welche Folge tatsächlich verschieden erklärt wird

Auf f83r.20:8 steht der angenommene Aufruf mit Material B, danach auf .21:2 qokedy. M kann die Zustandsaussage „B ist vorbereitet“ an die zwei expandierten Schritte anbinden. N kann dies unter denselben sonstigen Regeln nicht. Die offene Gruppe saiin folgt dem Aufruf, solkeedy steht vor der Zustandsaussage; deren mögliche Bedeutung ist nicht kontrolliert. Dieser Zusammenhang ist daher bedingt, nicht blind vorhergesagt.

Von allen 13 qokedy-Aussagen haben in M zwei einen vollständigen Erzeuger, in N eine. Die gemeinsame Stelle .7:8 hat in N schon die ausgeschriebene Überführung .6:7 als Erklärung; der erneute Aufruf bringt dort keinen zusätzlichen Erklärungserfolg. Elf weitere Aussagen sind in beiden Fassungen ungestützt, zwei davon haben nicht einmal einen Materialbezug. Insbesondere .20:4 und .20:7 behaupten denselben Vorbereitungszustand schon VOR dem neuen Aufruf. Der neue Ablauf erklärt also keineswegs den ganzen Absatz. Nach der späteren Erhitzung .21:5 fehlt für .21:8 erneut die vorausgesetzte Überführung. Keine dieser ungestützten Aussagen ist automatisch ein logischer Widerspruch; sie bleibt eine nicht gedeckte Voraussetzung der Lesung.

[Alle 13 Zustandsvergleiche](ALL_STATE_COMPARISONS.tsv) und alle 20 expliziten Handlungen in [M](EVENTS_M.tsv) beziehungsweise [N](EVENTS_N.tsv). Von den expliziten Handlungen haben in beiden Fassungen 13 vollständige Rollen. Die übrigen sieben werden weder gelöscht noch durch den Verfahrensnamen repariert.

## Ganze Arbeitsseite

- P1: drei frühe Erhitzungen, nur eine vollständig gebundene ausgeschriebene Überführung und drei qoky-Stellen einschließlich Definition. Wiederbearbeitung und nachgestellte Benennung bleiben Kosten.
- P2: kein qoky. Seine vier Zustandsaussagen erhalten durch P26 keine neue Erklärung; der anfängliche Zustand hat keinen Materialbezug. Das Verfahren wird nicht heimlich ergänzt.
- P3: ein vollständiger Aufruf mit Material B; eine zusätzliche Zustandsanbindung, aber frühere und spätere Vorbereitungsbehauptungen bleiben ungestützt.
- P4: zwei unvollständige Aufrufe; das als Gefäß gesetzte lchedy fehlt im gesamten Record. Kein Gefäß aus P3 geliehen.
- P5: der Aufruf steht vor der ersten gewählten Materialnennung des Records. Das spätere shedy wird nicht rückwirkend zum Parameter gemacht.
- Q1: eine angenommene Erhitzung ohne Material; kein Aufruf.
- Q2: alle 16 Gruppen offen; kein Aufruf und keine ergänzte Definition.

Die [kurze M-Lesung](READING_M.md), [vollständig expandierte M-Lesung](EXPANDED_M.md), [N-Gegenlesung](READING_N.md) und ALIGNMENT-Tabellen erhalten sämtliche Gruppen. „Vollständig expandiert“ bedeutet alle angesetzten Aufrufe ausgeschrieben, nicht alle Wörter übersetzt. [Abdeckung je Record](COVERAGE.tsv).

## Entscheidung, Vorwissen und Grenzen

M als konkrete Arbeitshypothese aufbewahren: Es gibt eine unveränderte Zweischrittkarte, drei gebundene Aufrufe und einen nachvollziehbaren Materialwechsel mit nachfolgendem Zustandsbezug. M wird nicht gegenüber N als Übersetzung ausgewählt: Der einzige zusätzliche Erzeuger folgt aus unseren angesetzten Verfahrens- und Zustandswerten; er ist keine unabhängige Bedeutungsprüfung. Zudem fehlen die Parameter bei der Hälfte der Aufrufe, die Definitionssyntax ist erfunden, und die wiederholte Überführung derselben Portion in dasselbe Gefäß ist ungeklärt. Keine Reserveprüfung bei 271 offenen Gruppen.

Primär gelesen: GDT441/448 (alte Faktor-/Kontextleser), GDT904 (festes Vinidarius-Modell), GDT817 (anderer Transformationssatz mit Transferproblemen). Keiner bestätigt diese Werte. Die Registry zeigt außerdem frühere qoky/saiin-Deutungen und Verfahrensmakros; der Bericht des älteren Pass500 fasst fünf Makros in acht Prozessprimitive. P26 beansprucht deshalb keine historische Erstidee. Es prüft eine einzelne ganze Form mit genau zwei schriftlich motivierten Schritten und sämtlichen Aufrufen im festgelegten Paket. Ältere Zählungen aus anderen Paketen werden nicht auf unsere sieben ZL3b-Stellen übertragen.

P12/P15/P07 und die aktuelle Sichtung haben das gesamte Material bereits exponiert. Keine unabhängige Bestätigungskapazität innerhalb dieses Durchgangs; keine Signifikanzbehauptung, keine bestätigten Stoffe, Gefäße oder Wortbedeutungen. Keine neuen Bilder, Seiten, Kontakte oder Reservetests. f84/f84r bleiben geschlossen. HERB4 und f77r/f82r sind hier nicht textuell ausgeführt.

Reproduktion aus Repositorywurzel: `python3 research_registry/proposals/translation_programs_20260912/work/P26/build.py`, danach entsprechend `validate.py`. SOURCE.json bindet die vor dem Lauf geschriebene DECISION.md und die alte begrenzte Quellprojektion per Hash. Lokale Validierung prüft Vollständigkeit und feste Modellkonsequenzen, keine Bedeutungswahrheit. Nächster Auswahlkandidat: P16, Bedingungen und Ausnahmen; Primärprüfung vor Ausführung erforderlich.
