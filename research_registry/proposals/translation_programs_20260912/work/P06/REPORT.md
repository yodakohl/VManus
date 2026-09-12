# P06 — Trennen und Wiedervereinigen mit Bestandskonto

Die feste Lesung liefert einen konkreten lokalen Rücklauf auf f83r.27–28: Ein Gemisch wird in zwei Portionen getrennt; genau diese beiden Portionen werden anschließend gemeinsam wieder vereinigt. Die symbolische Massenbilanz schließt, ohne einen Verlust oder eine Ersatzportion zu ergänzen. Das ist eine explizite Hypothese auf bereits exponiertem Text, keine identifizierte Stoffoperation.

Alle sieben f83r-Records mit 341 Gruppen wurden in C (verbundener Bestand) und I (unabhängige Versuche) ausgeführt. Sechs ganze Wortannahmen betreffen 50 Positionen; 291 bleiben offen. Von allen 19 Operationsstellen sind in beiden Fassungen sechs vollständig ausführbar: zwei Trennungen und vier Vereinigungen. Dreizehn bleiben unvollständig. Der lokale Rücklauf ist keine ganze Kapitelübersetzung.

## Konkrete Lesung und Bilanz

| Schriftstelle | Hypothese C | Symbolische Folge |
|---|---|---|
| shedy .26:5 | vorhandenes Gemisch | Masse m>0 |
| qokeedy .27:3 | trenne in zwei Portionen | m=m1+m2 |
| shckhedy .27:4 | erste Fraktionsportion | m1>0 |
| shckhedy .27:5 | zweite Portion derselben Fraktionsklasse | m2>0 |
| qokedy .28:4 | vereinige diese beiden Portionen | m3=m1+m2 |
| shedy .28:5 | neues Gemisch | m3=m |

[Schema und unabhängige Gegenlesung](SCHEMA.md), [Rücklaufkonto](CYCLES.tsv). Die zwei getrennten Portionen werden durch den gesetzten Trennvertrag und zwei Ergebnispositionen eingeführt. Die Wiederholung shckhedy allein übersetzt weder eine Zahl noch zwei Arbeitsgänge. „Zwei verschiedene Portionen“ ist nicht „zwei verschiedene Stoffe“. Das Endprodukt hat im Modell dieselbe Masse, aber keine bewiesene chemische Zusammensetzung.

Zwischen den beiden Fraktionsnennungen und der Vereinigung bleiben saiin cheeky sheey offen; auch dain chedy vor der Trennung wird nicht in einen passenden Befehl umgedeutet. Die motivierende Folge wurde vor dem Lauf gesehen und in DECISION.md benannt. Ihr Erfolg ist kein blinder Vorhersagetreffer.

## Fester Vertrag für sämtliche Vorkommen

Dingkarten: shedy Gemisch, lchedy Rückstand, qokeey Flüssigkeit, shckhedy Fraktion. Qokeedy trennt die letzte linke Materialportion in die ersten zwei rechts genannten Materialien vor der nächsten Operation. Qokedy vereinigt die letzten zwei links genannten Materialpositionen zum ersten rechten Material. Kein unbekanntes Zwischenwort wird entfernt; es bleibt in den vollständigen Lesern offen.

C behandelt normale Wiederaufnahme derselben Form als Verweis auf die zuletzt erzeugte verfügbare Portion. Ein verbrauchter Bestand wird nicht kostenlos ersetzt. Erfolgreiche Ergebnisse erzeugen neue IDs an den geschriebenen Ergebnispositionen; daher können zwei shckhedy-Ergebnisse verschieden sein, ohne die Identitätsregel je Einzelfall zu wechseln. Jede erste nicht durch eine erfolgreiche Operation erklärte Materialklasse wird als zusätzliche externe Anfangsmenge ausgewiesen. Dies ist eine Inhaltsannahme, kein entdeckter Zufluss.

I benutzt dieselben schriftlichen Argumente und dieselben Operationen, aber jede Operation ist ein eigener Versuch mit frischen Eingabemengen. Daher gibt es in I keinen beweisbaren Identitätsübergang von den zwei Split-Ergebnissen zu den zwei Merge-Eingaben. Beide Einzelbilanzen können stimmen, ohne einen Kreislauf zu bilden. Die Modelle unterscheiden sich in der Stoffidentität, nicht in einer günstigeren Argumentauswahl.

## Alle sechs ausführbaren Operationen

| Record / Stelle | C-Lesung | Spätere Verwendung |
|---|---|---|
| P1 .4:3 | Gemisch und Rückstand vereinigen | neues Gemisch bleibt im Bestand |
| P2 .12:8 | Gemisch und Rückstand vereinigen | Ergebnis ist Eingabe der Trennung .14:2 |
| P2 .14:2 | dieses Gemisch in Gemischportion und Rückstand teilen | beide Ergebnisse bleiben getrennt; keine spätere Vereinigung im Record |
| P3 .23:5 | Flüssigkeit und Gemisch vereinigen | neues Gemisch bleibt im Bestand |
| P4 .27:3 | Gemisch in zwei Fraktionsportionen teilen | beide gehen in .28:4 ein |
| P4 .28:4 | beide Fraktionsportionen vereinigen | neues Gemisch; weitere Trennung .30:3 bleibt ohne Ergebnisse |

Die P2-Folge ist Vereinigung→Trennung. Eine gleiche Masse der nachfolgenden Portionen belegt nicht die Rückgewinnung genau der ursprünglichen chemischen Bestandteile. In P4 ist zusätzlich Flüssigkeit aus .25:3 im Bestand, die im Rücklauf nicht verbraucht wird. Sie verschwindet nicht aus der Gesamtbilanz.

## Dreizehn unvollständige Stellen bleiben stehen

P1: .6:7 hat nur eine statt zwei Ergebnisnennungen; .7:8 kein Ergebnis, dazu verweist eine linke Position auf bereits verbrauchten Rückstand. P2: .9:3 und .11:6 fehlen Eingaben; .13:7 fehlt ein Ergebnis und ein alter Rückstandsbezug ist verbraucht. P3: .20:4, .20:7, .21:2 und .21:8 besitzen keine rechte Ergebnisnennung vor der nächsten Operation; .22:3 hat nur eine statt zwei. P4: .25:1 fehlen Eingabe und ein zweites Ergebnis, .25:4 fehlt eine zweite Eingabe, .30:3 fehlen die Ergebnisse. P5/Q1/Q2 haben keine der zwei angesetzten Operationsformen, bleiben aber vollständig im Reader und Nomenkonto enthalten.

[Alle 19 schriftlichen Argumentmengen](BINDINGS.tsv), [C-Ereignisse einschließlich Verbrauchsfehlern](EVENTS_C.tsv), [I-Ereignisse](EVENTS_I.tsv), [alle Materialnennungen C](MENTIONS_C.tsv). Keine fehlgeschlagene Operation produziert im zertifizierten Bestandskonto ein Ergebnis. Das beweist keine stoffliche Unmöglichkeit der ungelesenen Passage; es markiert die Grenze dieser festen Lesung.

## Vollständiger Bestand und Grenzen

C führt zwölf angenommene externe Anfangsportionen über alle Records: P1 drei, P2 zwei, P3 drei, P4 zwei, P5 zwei. Q1/Q2 haben keine gewählten Materialnennungen. Der positive Zahlenzeuge setzt jede Anfangsportion auf eins, halbiert bei Trennung und summiert bei Vereinigung. Der verbliebene Gesamtbestand bleibt in jedem Record exakt gleich der eingeführten Masse. Diese Zahlen sind frei gewählt und keine Übersetzung. [Bestände C](BALANCES_C.tsv).

I führt für seine sechs vollständigen Einzelversuche zehn frische Eingabeportionen. Diese Zahl ist mit den zwölf C-Anfangsportionen nicht als Sparsamkeitsvergleich verwendbar: C zählt auch das ganze nicht operierte Nomeninventar, I hier nur die erfolgreichen Versuchseingaben. [Getrennte Versuchsbilanzen](BALANCES_I.tsv). Keine Fassung erhält daraus einen Bedeutungsbonus.

Vollständige Leser: F83_P1_C.md bis F83_Q2_C.md sowie gleichnamige I-Dateien; [C-Ausrichtung](ALIGNMENT_C.tsv), [I-Ausrichtung](ALIGNMENT_I.tsv), [Abdeckung](COVERAGE.tsv). GDT790 liefert die grobe Einzel-/Koppelgliederung, GDT890 belässt andere Bildgrenzen offen und GDT891 betrifft eine externe Funktionsdeutung. Keine Bildpfeile, Flussrichtungen oder ungeschriebenen Verbindungen zwischen Records werden ergänzt. Der untere Bildzusammenhang beweist keine gemeinsame Stoffportion von P4 und P5.

## Entscheidung

Den lokalen Split-/Reunion-Kandidaten als konkret bilanzierte Hypothese aufbewahren. Er ist stärker ausgearbeitet als eine bloße passende Doppelung: zwei Ergebnispositionen, ihre spätere gemeinsame Verwendung und sämtliche Bestandsfolgen sind benannt. Die Wortwerte, die Zweiteilungsgrammatik und vor allem die Portionenidentität sind jedoch gesetzt. I zeigt, dass dieselben schriftlichen Rollen auch unabhängige Behandlungen zulassen. C wird deshalb nicht als Übersetzung ausgewählt. Dreizehn Operationslücken und 291 offene Gruppen verhindern eine nahezu vollständige Lesung oder Reservetestfreigabe.

Keine unabhängige Bedeutungsprüfung, Signifikanzbehauptung oder scorefähige GDT388-Relationsevidenz. Keine bestätigten Stoffe, Pflanzennamen oder chemischen Vorgänge. Keine neuen Seiten, Bilder oder Kontakte; f84/f84r geschlossen. Originalversuche unverändert.

Reproduktion aus Repositorywurzel: `python3 research_registry/proposals/translation_programs_20260912/work/P06/build.py`, danach entsprechend `validate.py`. SOURCE.json bindet die alte begrenzte Projektion und die vor dem Lauf geschriebene DECISION.md. Ein separater Validator spielt alle Argumente und das vollständige rationale Bestandskonto nach; er prüft Modellkonsistenz, keine historische oder semantische Wahrheit.

Nächster Auswahlkandidat: P20, Fachzeichen und grammatische Schrift, mit Primärprüfung vor Ausführung. Das vorgeschlagene qoky-Beispiel für P23 wurde wegen seiner direkten P26-Überschneidung nicht als nächster Ansatz übernommen.
