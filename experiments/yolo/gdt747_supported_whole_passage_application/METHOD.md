# GDT747 method

## Question

Werden bereits vorhandene Zeilen und mehrzeilige Blöcke konkret informativer,
wenn ausschließlich der Schnitt aus GDT746s Formfamilien- und unabhängigen
Top-5-Verteilungsachsen eingesetzt wird? Erzeugen unmittelbare bekannte
Ganzwörter zusätzliche lokale Unterstützung oder einen sichtbaren Kontrast?

## Inputs

Zwölf GDT746-Kandidaten besitzen S2/S3-Verteilungsstatus; sie haben 64
Vorkommen auf 62 Zeilen und 40 bereits erlaubten Seiten. GDT734 liefert den
kompakten Zellcache, GDT743 occurrence-spezifische ganze Zielkarten und GDT739
die Achsenextraktion. Der Guard materialisiert weiterhin nur die 179 erlaubten
Seiten vor jeder Token-/Alternativleser-Abfrage; `f84/f84r` bleiben gesperrt.

## Method

`src/PASSAGE_SAFE_VALUES.tsv` enthält für jedes der zwölf Ganzwörter genau den
Schnitt `form_and_top5_axis_agreement` aus GDT746. Elf Formen besitzen einen
solchen Kern; `chtl` hat keinen und bleibt trotz zwei Vorkommen offen. Zusätze
aus der direkten Formfamilie erscheinen sprachlich nur als „wahrscheinlich“
oder als benannter Rivale.

Die 62 Kandidatenzeilen werden vollständig und positionsgetreu gerendert. Die
Hierarchie ist:

1. GDT746-Form-/Verteilungsschnitt am exakten Kandidatenwort;
2. GDT743s occurrence-spezifische vollständige Zielkarte;
3. sichere W2/W3-Ganzwortkarte aus GDT734;
4. bekannte, aber schwächere Ganzwortkarte sichtbar in eckigen Klammern;
5. offen oder ausdrücklich zurückgehalten.

Eine GDT734-Karte ist nur sichtbar, wenn sie bekannt, komponentenfrei,
kompositionsfrei und achsentragend ist. Alte konkrete Identitäten für Pulver,
Samen/Saat, Wurzel, Holz, Blatt/Kraut/Pflanze, Wasser, Wein, Öl, Salz, Pfund,
Handvoll oder eine spezifische Gewichtseinheit werden zurückgehalten. Wörter
wie „Arbeitsgut“ erhalten keine Sichtbarkeit.

Für jedes der 64 Kandidatenvorkommen werden die vollständigen bekannten W2/W3-
Ganzwörter in Abstand eins oder zwei geprüft. Eine Kandidatenachse ist lokal
gestützt, wenn sie in deren ganzer Karte vorkommt. Zwei verschiedene bekannte
Wörter ergeben L2; tragen sie denselben Kern, aber einen heißen/kalten oder
trockenen/feuchten Kontrast, ergibt dies L3. Der initiale EVA-Buchstabe spielt
dabei keine Rolle.

Sechs vorab auf dem vollständigen Kandidateninventar gewählte Blöcke decken
den einzigen Zwei-Kandidaten-Satz, vier enge Mehrzeilengruppen und einen
Wiederholungskontrollfall ab. Ihre manuelle Karte bewertet Fachregistertyp und
Informationsgewinn, nicht natürlichsprachliche Glätte.

## Decision rule and claim ceiling

L3 darf einen Achsenwert passage-lokal verstärken; wiederkehrendes L2 darf eine
Ganzwortkarte als passagegestützt markieren. L1 bleibt örtliche Unterstützung.
L0 ändert den GDT746-Wert nicht. Vollständige Zeilen dürfen als Sachregister,
Liste oder Tabelle beschrieben werden, aber nicht ohne Syntaxbeleg in flüssige
Anweisungen umgeschrieben werden.

GDT747 bestätigt kein Lexem, keinen Klartext, keinen EVA-Zeichen-/Teilstringwert,
keine konkrete Pflanze, Flüssigkeit, Substanz, Krankheit, Heilung, Person,
Gefäß- oder Maßeinheit und keine ungesehene Form.
