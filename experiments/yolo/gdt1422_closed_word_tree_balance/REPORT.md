# GDT1422 — ein fertiger Baum pro Wort scheitert an drei alten Formen

**CLOSED_WORD_FIXED_ARITY_EXCLUDED.** Die vorhandenen ganzen Formen `ol`,
`oldy` und `ololdy` können nicht sämtlich genau einen geschlossenen Ausdruck
bilden, wenn jede Arbeitseinheit immer dieselbe feste Anzahl von Eingaben
verlangt. Der zusätzliche Schluss verwendet alte Belege; kein neues Wort,
keine neue Handschriftenbeobachtung und keine Übersetzung wurden gewonnen.

## Die einfache Bauprobe

Angenommen, `ol` ist bereits ein fertiger Ausdruck und `oldy` ebenfalls.
Dann schreibt `ololdy` genau beide unverändert hintereinander. Das ergibt
zwei fertige Ausdrücke. Ein einzelner Ausdruck bräuchte eine zusätzliche
Verknüpfung oder eine andere der unten ausdrücklich ausgeschlossenen Regeln.
Dieses Argument setzt keine Bedeutung für OL, D oder Y voraus.

Genauer hat ein endlicher Baum einen Verbindungspfeil weniger als Knoten.
Die Summe von **1 minus Eingabezahl** über alle Knoten ist deshalb1.
OL und OLDY müssten jeweils1 beitragen, ihre Verkettung OLOLDY also2.
Gleichzeitig verlangt das Modell für OLOLDY wieder1: Widerspruch.
Der Zählervektor-Nachweis in RESULT erhält alle Zeichen; die Linearkombination
−OL−OLDY+OLOLDY ergibt links0 und rechts−1. Die Traversierungsrichtung ist
für diese notwendige Bedingung gleichgültig. Ein Parser oder Zeichenschlüssel
ist nicht erforderlich.

## Die tatsächlich verwendeten Belege

| Alternative Lesung | OL | OLDY | OLOLDY |
|---|---:|---:|---:|
| ZL3b |455|25|2|
| IT2a |456|24|2|
| RF1b |469|18|2|

Dies sind unveränderte GDT1200-Ganzformprofile, keine neu gezählten Wörter.
Beide OLOLDY-Stellen, f23r.1 und f34r.1, haben in jeder Lesung bestimmte
Außengrenzen. Die ursprünglichen Gruppen-IDs und vollständigen Belegdatensätze
stehen in [RESULT.json](artifacts/RESULT.json). Das sind **zwei Stellen einer
Handschrift mit alternativen Lesungen**, keine sechs unabhängigen Belege.
Die DAL-Trennungsfrage wird nicht benötigt. Dasselbe eingebettete OL müsste
nur dieselbe **Operatorstelligkeit** tragen; eine gemeinsame konkrete
Wortbedeutung wurde weder angenommen noch erschlossen.

## Exakter Ausschluss und erhaltene Alternativen

Geschlossen wird nur: jede ganze Gruppe genau ein expliziter endlicher Baum;
feste Stelligkeit je unveränderter Arbeitseinheit; einheitliche Prefix- oder
Postfixdarstellung; keine impliziten Knoten, äußeren Argumente oder
kontextabhängigen Umdeutungen. Die Segmentierung muss die OL|OLDY-Verkettung
erhalten. Die vier wörtlichen Arbeitszeichen o,l,d,y sind kein bewiesenes
Ursprungsalphabet. Ein anders segmentierter Code wäre ein anderer Vertrag.

Das schließt weder gewöhnliche Sprache noch Syntaxbäume allgemein aus.
Eine Folge von Befehlen kann beispielsweise durch Ausführung nacheinander
zusammengesetzt werden, ohne diesen Einbaumvertrag zu erfüllen. Offene
Ausdrücke über Wortgrenzen, variable Listenlänge, implizite Verknüpfung oder
wechselnde Zeichenrollen sind ebenfalls nicht widerlegt. Keine Alternative
wird dadurch bestätigt oder automatisch als Reparatur ausgewählt.

IP080s vorhandener Oktober6-Schluss betraf dagegen **Absatz=Baum,
Ganzwort=Knoten** und IT-Absatzränder. Dieser neue **Wort=Baum,
Arbeitseinheit=Knoten**-Schluss braucht keine Absatzflags.1200s Familien,
1201s transparente Komposition,1391s enger Stoppvertrag und1401s
Adressfehler bleiben unverändert. Die Baumidentität und allgemeine
Verkettungsidee sind keine neuen mathematischen Entdeckungen.

## Entscheidung und Prüfung

Keinen Parser für diesen geschlossenen Einzelwortvertrag bauen. Weitere
Ausdruckslesungen müssen ihre wirkliche Gruppierung und Argumentaufnahme
benennen; die fehlende Wortbedeutung wird nicht durch eine neue Operatorrolle
ersetzt. Der größere Übersetzungsweg bleibt offen, bestätigte Lexeme0.

Quellen und erwarteter Widerspruch waren vor Auswahl bekannt. Der
[Vertrag](PREREGISTRATION.md) ist daher eine offengelegte deduktive Anwendung,
keine blinde Vorhersage. Lock am2026-10-17T06:43:25UTC vor ausführbarem Replay.
Ein getrennt arbeitender Agent bestätigte Beweis und Vorgängerabgrenzung und
schrieb den Validator ohne Primärimport. Er rekonstruiert Profile und beide
Außengrenzen pro Leser, prüft das symbolische Zertifikat sowie kleine gültige
und ungültige Ausdrucksbeispiele. [PASS](artifacts/VALIDATION.json) bestätigt
Quellenbindung und Schluss **unter Annahmen**, keine native Grammatik.

Keine neuen Bilder, Rohtranskriptionen, externen Quellen oder Reserven;
f84/f84r bleiben versiegelt. Keine semantische Relation bewertet. Der
inklusive Auswahl-bis-Publikation-Block ist06:35–07:05UTC begrenzt;
die tatsächliche Veröffentlichung wird im bestehenden aktiven Stand erfasst.
Reproduktion: die beiden Befehle aus experiment.json in einer frischen Kopie
ohne RESULT/VALIDATION ausführen, LOCK und alte Eingaben erhalten.
