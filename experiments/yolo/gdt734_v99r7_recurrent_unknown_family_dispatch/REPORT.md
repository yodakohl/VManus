# GDT734 — V99R7 recurrent unknown-family dispatch

Status: `PASS_V99R7_71_ACTIVE_WHOLE_EXPORT_REPAIRS_305_CELLS__20_UNIQUE_SPLIT_EXACT_WHOLES_226_CELLS__531_CHANGED_CELLS__7989_TO_7458_UNKNOWNS__5107_TO_5016_FORMS__15_NEW_COMPLETE_LINES__9_COMPOSITIONAL_5_ROLE_CONSTRAINED_6_LEARNED__28_EDITORIAL_AUDITS_26_REVISED__1606_CONFIDENCE_EVIDENCE_ROWS__19_ROLE_MATRIX__ZERO_COMPONENT_EXPORT__NO_NEW_PAGE`

## Ergebnis

Der erste, rein technische Pass findet einen reproduzierbaren
V99R6/V99R7-Projektionsfehler: 71 aktive Ganzwortlesungen
waren als `ACTIVE_WORKING_DEFAULT` und bedingungslos exportierbar markiert,
blieben in GDT733 aber an 305 identischen Cache-Stellen `?`, weil dessen
Projektionsfilter nur die ältere `GLOBAL_V48_DEFAULT`-Schicht einsammelte.
V99R7 repariert alle 305 Stellen. `dchey` und `olkar` bleiben als die beiden
bewusst kontext- beziehungsweise spangebundenen Ausnahmen draußen.

Davon getrennt prüft der zweite, explorative Pass 20 häufige Restformen an 226
Stellen und gibt jeder einen konkreten Ganzwortdefault. Jede besitzt genau eine
Zweiteilung unter den derzeit konkreten V99R4-Lesartenkombinationen; das ist
keine Behauptung einer sprachlich eindeutigen Segmentierung. Der manuelle
Gegencheck trennt neun kompositionell gestützte,
fünf rollenbeschränkte und sechs nur als gelernte Ganzwörter lesbare Formen.
Eine eindeutige Trennstelle zählt ausdrücklich nicht automatisch als
semantischer Beleg. Die neue Tranche spricht unter anderem trockenes Pulver,
Drogenholz, Blütenfraktion, Ansatz, Trocknen, Kühlen, Einweichen und Abmessen
aus. Kein Kandidat mit mehreren Zerlegungen wird übernommen.

Damit sinkt die Zahl der `[surface:?]`-Marker in diesem festen Cache von 7.989
auf **7.458** Zellen und von 5.107 auf **5.016** Formen.
Diese Abdeckungsmetrik misst keine Übersetzungswahrheit. Insgesamt
ändern sich 531 Zellen auf 472 Zeilen; die Zahl vollständig
lesbarer Cache-Zeilen steigt von 1413 auf
1428 (+15).

## Praktischer Renderer

28 der formal exportierbaren aktiven Ganzwörter wurden zusätzlich redaktionell
geprüft. 26 erhalten eine kürzere gesprochene
Fassung, ohne Score, Evidenz oder gespeicherten semantischen Kern umzuschreiben.
So wird etwa `Mischgut` zu `Mischung`, `heißen Auszug bereiten` zu `Ansatz
erhitzen`, und occurrence-lokale Patienten verschwinden aus portablen Kernen.
`os=Zubereitung` und `dold=abmessen und abschließen` bleiben sichtbar offen,
statt mit erfundenem Stoff oder Patienten aufgefüllt zu werden.

Diese gesprochene Fassung gilt für die 305 zuvor ausgelassenen
Ganzwortprojektionen. Bereits vorhandene exakte V99-Kontexte und gebundene
Spans behalten als höhere Präzedenz ihre positionsgebundene Realisierung; die
abweichende Ausgabe derselben Oberfläche ist damit explizit lokal und kein
zweiter stiller globaler Default.

## Wortstamm- und Codebuchmodell

Innerhalb des aktuellen Arbeitswörterbuchs ist die ausgewählte 19-Formen-
Kreuzmatrix mit Rollen konsistenter als mit universellen Wörtern:
`-ol` verhält sich als Stoff-/Materialrolle, `-or` als Portion, `-aiin/-ain`
als Index III/II und `-ar` als Anteil I. `cth`, `p` und `s` sind dabei
exakte-Ganzwort-Arbeitsköpfe für Pflanzendroge, Pulver und Samen; kein freier
Kopfwert wird exportiert. `olk` bleibt gebunden, `olkol` begrenzt die
`-ol`-Regel und `-dy` wird nicht als portable Rolle freigegeben. Der nächste
historische Architekturvergleich ist ein Apothekerbuch-Mikroeintrag aus
gelerntem Drogenwort, kurzem Qualitätsrahmen und separatem Mengen-/Gradslot.
Diese Parallelen bestätigen weder eine Form noch eine Bedeutung: Sie erhalten
exakt null Relations- und Zeichenwertkredit.

## Confidence und Evidenz

Das vollständige V99R7-Wörterbuch enthält 1.606 Lesarten für 1.602 Formen.
Jede Zeile trägt Arbeitsbedeutung, Score, Confidence, positive Evidenz,
Gegenbeleg, Scope und Exportrecht. Die 20 neuen Formen liegen bewusst nur in
W1/W2. Ihre Scores werden aus dem schwächeren Teilwert, einem begrenzten
Wiederholungsbonus und einem expliziten Routenabzug berechnet. Wiederholung und
Score sind ausschließlich interne Arbeitsmodell-Rangwerte, keine semantische
oder historische Bestätigung. Die Teilwerte werden nicht frei exportiert. Die
ganze Form darf im
bereits zugelassenen Cache als explorativer Default laufen.

## Grenze

Dies ist ein konkreter explorativer Arbeitsrenderer, kein bestätigter Klartext. Die
3.971 singletonlastigen Restformen, konkrete Pflanzenarten, Krankheiten,
Heilungen, historische Einheiten und die mehrdeutigen Spitzenformen
`qokeody`, `okeody`, `qokeor`, `chdaiin`, `ory` bleiben offen. Keine neue
Seite, kein Bild, keine Transkription, kein `f84` und kein `f84r` wurde benutzt.
