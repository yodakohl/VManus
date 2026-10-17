# Die14er-Tabelle lässt sich nicht bloß mit exklusiven neuen Codes ergänzen

**Bedingter Ausschluss einer Vervollständigungsart, keine Übersetzung und kein
Ausschluss von Deutsch.** Die rohe14er-Idee bleibt unbestätigt. Neu ist eine
notwendige Folge ihrer schon festgelegten Wortpositionsregeln.

Im [ursprünglichen Vorschlag](GERMAN14_RAW_TABLE_20261017.json) steht a für ein
nichtfinales Quell-e. Ein finales e erzeugt dagegen y. Das ist eine angenommene
Schreibregel, keine erkannte Voynichbedeutung.

Wir prüfen jetzt ausdrücklich die zusätzliche Bedingung, dass der **vollständige
Code a keinem anderen Quellursprung** gegeben wird. Ebenso bleiben k bei N und
l bei S reserviert. Ein Ursprung darf weiterhin mehrere positionsabhängige
Schreibungen haben; geteilte einzelne Striche in in/iin sind erlaubt.
Zusätzliche Buchstaben, Fälle und beliebig lange Codes bleiben möglich, solange
sie nicht leer sind. Die vorhandenen Regeln, das greedy ei und die Gleichsetzung
von vollständiger Gruppe und Quellwort bleiben fest. Neue Makros und unsichtbare
Buchstaben fallen außerhalb dieses Teilmodells. Diese Exklusivität war keine
ursprüngliche Anforderung der rohen14er-Idee.

## Der kurze Gegenbeweis

Eine ganze Ausgabegruppe aus nur a kann bei nichtleeren Ausgaben nur einen
Quelltoken enthalten. Der einzige erlaubte Ursprung für diesen Code ist E.
In einem vollständigen Quellwort aus diesem einen Token ist E aber final.
Nach der festen Regel müsste deshalb y entstehen. **a ist so nicht erzeugbar.**
Weder ein größerer Zeichenvorrat noch längere zusätzliche Codes beheben das.
Der Beweis verlangt weder Präfixfreiheit noch freie eindeutige Decodierbarkeit
noch ein bestimmtes Wörterbuch oder eine bestimmte Sprache.

Für das ganze k gilt dasselbe mit N: Ein finales N schreibt in. Für l liefert
das eingefrorene Programm bei einem einzelnen S wegen seiner Initialpriorität
q. Diese letzte Priorität ist eine zusätzliche Festlegung des Programms; sie
wurde durch die14längeren Vergleichswörter nicht selbst geprüft.

## Die benötigten Belege sind bereits vorhanden

Nachgeschlagen wurden die alten GDT1233-Panels: reine P-Prosa, bestimmte Lücken
auf beiden Seiten, unveränderte Rohform und genau eine Zerlegung in Arbeitseinheiten.
Kein neuer Bildentscheid und keine unabhängige Bestätigung der Wortgrenzen.

| Vollständige strenge Gruppe | IT2a | ZL3b | RF1b |
|---|---:|---:|---:|
| a | 1 | 1 | 2 |
| k | 0 | 1 | 2 |
| l | 36 | 35 | 69 |

Der gemeinsame a-Beleg liegt bei f89v1.19/G002. Das sind drei Lesungen desselben
physischen Ortes, keine drei unabhängigen Bestätigungen. Die a-Aussage bleibt
an diesen seltenen Beleg gebunden. l ist viel häufiger, trägt aber nur den
stärkeren Vertrag mit der festgelegten Einzel-S-Priorität. Ein geänderter
Einzel-S-Fall würde den a-Gegenbeweis nicht entfernen.

Die erste k-Stelle unterscheidet sich: ZL f95v1.10/G004, RF f95v1.9/G004;
IT hat hier im strengen Bestand keinen alleinstehenden k-Beleg. Es wird kein
Leser gewählt, um einen fehlenden Beleg zu ergänzen. Sämtliche gefundenen
Quellzeilen, eigene Leserzählungen und Dateihashes stehen im
[Ergebnis](GERMAN14_COMPLETION_RESULT_20261017.json).

## Was ausdrücklich weiter möglich ist

Ein anderer Ursprung X könnte ebenfalls a schreiben. Das verletzt die hier
geprüfte Exklusivität, muss aber keine Mehrdeutigkeit ganzer Wörter erzeugen.
Beispiel: X schreibt a, EE schreibt ay. In dem festgelegten Quellwortschatz
{X,EE} sind beide Wörter eindeutig rücklesbar. Auch zusammen mit allen14alten
Vergleichswörtern bleiben in diesem kleinen Quellbeispiel alle16Ausgaben
verschieden. Das ist nur ein Quellengegenmodell, keine deutsche Lesung.

Ebenso könnten leere Ausgaben, andere Gruppengrenzen oder geänderte Grundregeln
die Folgerung vermeiden. Für keinen dieser Wege wird eine native Berechtigung
behauptet. Besonders darf man aus diesem Beweis nicht „jeder eindeutig lesbare
Code scheitert“ ableiten: Kontexte können wiederverwendete Codes unterscheiden.

## Arbeitsentscheidung

Keine reine Alphabetvervollständigung beginnen, die diese Codes exklusiv
reserviert und alle anderen Annahmen erhält. Genau diese unbegrenzt große
Zusatzcodefamilie scheitert unter den alten vollständigen Gruppen bereits.
Die allgemeinere rohe14er-Tabelle bleibt inconclusive: Codewiederverwendung,
Syntax, historische Quelle und die übrigen Formen sind nicht erklärt.
Es wird kein Alias, Dialektwechsel, Null-e oder anderes Ersatzsystem ausgewählt.

GDT1233/1353 belegen unter ihren eigenen Verträgen Code-Mitgliedschaften.
Hier wird eine andere Folge gezogen: Ein bereits vorgeschlagener Quellursprung
hat an einer vorhandenen ganzen Gruppe keine zulässige Positionslizenz.
Es ist ein dokumentarisches Korollar mit alten Belegen, kein neuer globaler
Singletonversuch, Decoderlauf oder Manuskriptbefund.

Ein separater Agent prüfte die Logik und Gegenmodelle; ein anderer zählte den
alten Cache unabhängig. Der kleine [Begleitcode](GERMAN14_COMPLETION_BOUND_20261017.py)
reproduziert die gespeicherten Belege und Annahmengegenmodelle; seine Ausführung
bestätigt keine Paläographie oder Bedeutung. Die ursprüngliche Tabelle und alle
früheren Entscheidungen bleiben unverändert.0übersetzte Wörter.
Arbeitsbudget12:49:49–13:14:49UTC einschließlich Veröffentlichung.
