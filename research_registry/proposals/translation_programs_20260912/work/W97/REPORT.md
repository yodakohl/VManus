# W97 — der feste Generationenentwurf scheitert an Selbstbezügen

**Alle vier festgelegten Varianten sind widersprüchlich.** Geprüft wurde eine neue, begrenzte Ausführung der IDEA000195: qokedy und qokeedy sollten gemeinsam einen Generationenschritt beziehungsweise gleiche Generation ausdrücken. Der ganze f83r-Arbeitsumfang wurde ausgeführt, ohne die geparkten Mengen- und Rezeptlesungen fortzuschreiben.

Dies ist kein allgemeiner Ausschluss einer Abstammungsdarstellung. Die gewählten Teilnehmer und ihre Identität sind Hypothesen. Auch die Fehlerform ist bekannt: P27 hatte unter anderer Grammatik Selbstbezüge gefunden. W97 liefert keinen neuen allgemeinen Nachweis dieses Problems; insbesondere die qokeedy-Stelle auf .14:2 war bereits im P27-Bericht als Selbstbezug beschrieben. Die beabsichtigte zusätzliche Kopplung entscheidet die vier Modelle nicht erst — sie scheitern schon vorher an einzelnen Identitätsforderungen.

## Fester Vertrag und vollständige Anwendung

Nur qokaiin=A, shedy=B und lchedy=C sind angenommene Personenbezeichnungen. Innerhalb eines Records bezeichnet dieselbe Form dieselbe Person; die Identitäten werden an Recordgrenzen zurückgesetzt. Keine Form wird als echter Personenname bestätigt. Linker Teilnehmer ist die letzte ausdrückliche Nennung eines dieser Wörter; rechts steht die erste solche Nennung vor dem nächsten qokedy/qokeedy oder Recordende. Keine Ergebnisfortführung aus P27, kein chedy-Relationswert.

Ein STEP verlangt g(rechts)−g(links)=+1 oder −1. EQUAL verlangt null. EQUAL bedeutet ausdrücklich nur gleiche Generation, nicht Geschwister oder Ehe: Selbstgleichheit ist erlaubt. Beide Zuordnungen der zwei Operatoren und beide STEP-Richtungen waren vorher festgelegt. Die zwei Richtungen bleiben durch Spiegelung aller Generationen symmetrisch; ihre Übereinstimmung ist keine Wiederholungsbestätigung.

Alle sieben vorhandenen f83r-Records umfassen 51 Zeilen und 341 Gruppen. Es gibt 13 qokedy- und sechs qokeedy-Stellen. Acht besitzen unter der kleinen Grammatik beide Teilnehmer; acht keinen rechten, zwei keinen linken und eine keinen der beiden. Die letzten drei Records ohne diese Operatoren bleiben vollständig mit enthalten. [EDGES.tsv](EDGES.tsv) dokumentiert alle 19 Stellen mit beiden Bezugsloci und sämtlichen Zwischenwörtern. [READING.md](READING.md) und [ALIGNMENT.tsv](ALIGNMENT.tsv) bewahren den gesamten Text.

## Alle acht gebundenen Beziehungen

| Record | Stelle | Form | Angenommene Beziehung |
|---|---|---|---|
| P1 | .4:3 | qokedy | A → B |
| P1 | .6:7 | qokeedy | A → C |
| P2 | .11:6 | qokedy | A → C |
| P2 | .12:8 | qokedy | C → B |
| P2 | .14:2 | qokeedy | B → B |
| P3 | .22:3 | qokeedy | C → B |
| P3 | .23:5 | qokedy | B → B |
| P4 | .28:4 | qokedy | B → B |

Unter qokedy=STEP(+1) und qokeedy=EQUAL würde P1 konkret verlangen: A und C auf derselben Generation, B eine Generation jünger. P2 würde A → C → B über zwei Generationen führen. Das sind nachvollziehbare kombinierte Konsequenzen des hypothetischen Registers, keine beobachteten Familienbeziehungen. Die Gegenfassung vertauscht, welche Teilbeziehung einen Generationenabstand verlangt.

## Entscheidung für jede Variante

| STEP | EQUAL | Richtung | Gebundene STEP-Stellen | Widersprüche |
|---|---|---:|---:|---|
| qokedy | qokeedy | +1 | 5 | .23:5, .28:4 |
| qokedy | qokeedy | −1 | 5 | .23:5, .28:4 |
| qokeedy | qokedy | +1 | 3 | .14:2 |
| qokeedy | qokedy | −1 | 3 | .14:2 |

Jede genannte Stelle verlangt g(B)−g(B)=±1, also 0=±1. Es gibt drei verschiedene widersprechende Stellen, keine sechs unabhängigen Gegenbeweise. Keine Widerspruchszertifikate benötigen beide Operatorarten gemeinsam. [CONTRADICTIONS.json](CONTRADICTIONS.json) enthält alle sechs richtungsabhängigen Zertifikate einschließlich Vorzeichen und Quellstellen; [MODELS.json](MODELS.json) alle vier Entscheidungen.

Die linke Bindung reicht stellenweise über viele ungelesene Gruppen und frühere Operatoren zurück, während die rechte Suche am nächsten Operator stoppt. Das ist genau die registrierte Asymmetrie, keine erkannte mittelalterliche Syntax. Beispielsweise führt .22:3 seinen linken Teilnehmer aus .19:11 fort. Der Selbstbezug .23:5 verbindet zwei shedy-Nennungen auf .23:4 und .24:6. Es sind verschiedene Schriftpositionen, die unser Modell gleichsetzt. Eine tatsächliche Personengleichheit oder ein Personenwechsel ist nicht gelesen.

## Entscheidung und Grenzen

**Diesen festen Generationenentwurf stoppen.** Keine neue Person pro Selbstbezug, keine neue Operatorbedeutung und keine Änderung des Bezugsfensters. Der allgemeinere genealogische Vorschlag bleibt außerhalb dieses konkreten Vertrags ungetestet. Aus dem Scheitern folgt weder eine Pflanzenlesung noch Bedeutungslosigkeit des Textes.

Der erhoffte Mehrwert gekoppelter Beziehungen wurde als konkrete Vorhersage ausgearbeitet, aber nicht unabhängig bestätigt. Es ist kein übersetztes Verwandtschaftswort und kein sinnvoll lesbares Gesamtregister entstanden. Ein weiterer Generationenlauf mit derselben kleinen Teilnehmerliste wäre nicht gerechtfertigt. Kein Folgeexperiment ausgewählt.

[DECISION.md](DECISION.md) wurde vor Ausführung geschrieben; alle f83r-Inhalte waren schon aus früheren Projektversuchen bekannt. [SOURCE.json](SOURCE.json) bindet Vorgänger und Protokoll. Die erneute TSV-Projektion erfolgte mit dem Selektorwächter ausschließlich für f83r und ist bytegleich zum W92-Paket. Keine neue Seite, Abbildung, Quelle, Reserveprüfung oder Kontaktaufnahme. f84/f84r blieben geschlossen. Keine Signifikanz oder unabhängige Bedeutungsbestätigung.

Reproduktion: `python3 research_registry/proposals/translation_programs_20260912/work/W97/run.py`. Die Zertifikatprüfung summiert die ursprünglichen Kanten unabhängig von der Potentialsuche und bestätigt den von null verschiedenen Kreisrest bei aufgehobenen Teilnehmerkoeffizienten. Beide Routinen stammen von root; keine unabhängige semantische Prüfung. Dies ist ein hypothetisches Modell, kein scorefähiges GDT388-Relationspaket.
