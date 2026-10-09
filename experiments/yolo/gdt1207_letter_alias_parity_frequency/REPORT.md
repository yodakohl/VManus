# GDT1207 — feste Buchstabenwerte und zwei Aliasse: zu viele Wortformen

**ALT_FREQUENCY_SCREEN_FAIL.** Der Entwurf trifft den Anteil häufiger Wörter
innerhalb der unveränderten Toleranzen, erzeugt aber auf allen vier festen
Quelltexten zu viele verschiedene Schreibformen. Jede Typenanteilsbedingung
scheitert gegen jeden der drei getrennten Voynich-Vergleichsausschnitte.
Eine andere feste, eindeutig lesbare Zeichentafel kann diese Wortgleichheiten
nicht verändern. Alle **1.054 Rezepte / 80.931 Wörter / 333.022 Zeichen** bleiben
vollständig rücklesbar; keine native Bedeutung ist gewonnen.

## Fester Entwurf statt wechselnder Buchstabenwerte

Für jeden gewöhnlichen Quellbuchstaben gibt es zwei fest lesbare Schreibwerte.
Der Schreiber wechselt bei jeder Verwendung genau dieses Buchstabens zwischen
seinen beiden Varianten. Andere Buchstaben ändern dessen Zustand nicht. Jedes
Rezept beginnt mit Variante0; Wortzwischenräume setzen nichts zurück.

Das benötigt52gewöhnliche Aliaswerte,56festgelegte Sonderzeichenwerte und26Ticks
für den Schreiber. Zur reinen Buchstabenrückgewinnung genügt die feste Tabelle;
für die Prüfung der kanonischen Wahl führt auch der Leser die Ticks mit.
Die möglichen2^26Gesamtzustände sind keine zwei Ganzwortvarianten: Bei anderer
Vorgeschichte kann dasselbe ganze Quellwort mehr als zwei Formen erhalten.
GDT1202s engere Zwei-Ganzwortvarianten-Schranke entscheidet dies daher nicht.

Nur der vorher ungetestete ALT-Teil von GDT1197 wurde ausgeführt. GDT1206s MTF
hat dagegen wechselnde Buchstabenwerte und bleibt gescheitert. Die alten
Berichte behalten ihren damaligen Status; beide früher offenen1197Arme haben
jetzt getrennte spätere Entscheidungen in1206und1207.

## Die Wiederholungsbedingung

Die Modellannahmen werden vor einem Zahlentest am bekannten Wortbau geprüft.
Ein vollständiger Codeblock kann **genau gleich zweimal unmittelbar erscheinen**,
wenn jeder gewöhnliche Quellbuchstabe darin gerade oft vorkommt. Dann stellt
der erste Block alle seine Ticks wieder her. Sonderzeichen ändern keinen Tick.

Ein rein künstliches Beispiel; A0/A1 und B0/B1 sind Aliasnamen, keine Voynichwerte:

| Quellblock dreimal geschrieben | Erste Form | Zweite Form | Dritte Form |
|---|---|---|---|
| abb | A0 B0 B1 | A1 B0 B1 | A0 B0 B1 |
| abba | A0 B0 B1 A1 | A0 B0 B1 A1 | A0 B0 B1 A1 |

Erste und dritte Form sind immer gleich; erste und zweite nur bei gerade vielen
Vorkommen jedes gewöhnlichen Buchstabens. Eine ungerade **Gesamtlänge** genügt
nicht als Widerspruch: aÄa enthält zwei gewöhnliche a und ein tickneutrales Ä.

GDT1200 hält sowohl die ganze Form `ol` als auch die ganze Form `olol` fest.
Unter **einem gemeinsamen nichtlöschenden, eindeutig decodierbaren Träger und
einem Quellwort pro Gruppe** ist die Decodierung von olol erzwungen zweimal
dieselbe Codeeinheitenfolge wie bei ol. Das gilt auch ohne Präfixfreiheit.
Es erzwingt für den hinter ol liegenden Quellblock die genannte gerade Häufigkeit.
Es beweist weder, dass o/l einzelne Buchstaben sind, noch zwei Quellwörter oder
eine Bedeutung. Ein Quellblock mit geraden Häufigkeiten ist möglich: **kein
nativer Gegenbeweis** gegen ALT allein aus dieser Doppelung.

Bei B Bdy oder BBdy sind zusätzlich vollständige gültige Codestrings B UND dy
sowie kein Reset zwischen den Kopien nötig. Ein beliebiger wiederholter innerer
Glyphenteil oder ein nur gültiger Präfix erlaubt diese Folgerung nicht. Die
abweichenden Lesergrenzen und1201s inhaltsgleiche Mehrfachgruppierungen bleiben.
[Methodischer Beweis](METHOD.md), keine neue native Zählung oder Schlüsselbindung.

## Fester Quelltest

Registrierung am5.Oktober2026 um **14:46:37UTC**, vor der Codierung und Zählung,
mit Hashbindung von Quellen, Vertrag, Runner und Validator. Unveränderte1177-
Editionsprojektionen b4,w1,bs1,gr1; je erste8000Gruppen in Quellreihenfolge,
Rezeptgrenzen bei Nachbarpaaren erhalten. Alle vollständigen Rezepte dienen der
Rückleseprüfung. Derselbe feste1174-Zielbestand und dieselben Toleranzen wie1197
und1206; keine neue Quelle, Handschriftstelle, Bildöffnung oder Reserve.

| Quelle | Verschiedene Aliasformen /8.000 | Anteil der zehn häufigsten | Exakte gleiche Nachbarpaare |
|---|---:|---:|---:|
| b4 |3.444|11,7000 %|0 /7.897|
| w1 |3.586|11,1750 %|0 /7.890|
| bs1 |3.489|12,4125 %|0 /7.893|
| gr1 |3.209|12,8625 %|0 /7.896|

Die getrennten nativen Ausschnitte haben IT2a2.451, RF1b2.530 und ZL3b2.500Formen
je8.000Gruppen. Ihre unveränderten oberen Typengrenzen liegen bei2.851/2.930/2.900.
**Alle zwölf Typenbedingungen scheitern.** Keine Grenzanpassung folgt.

Alle zwölf Top10-Bedingungen bestehen unter ±0,05. Das ist gegenüber1206ein
qualifizierter positiver Kontrollbefund, kein ausgewählter Voynich-Schreiber.
Die zwölf Bedingungen zur exakten Nachbarwiederholung bestehen formal ebenfalls:
die alte ±0,01-Toleranz lässt null zu. Tatsächlich gibt es in allen vier
Stichproben null exakte Wiederholungen. Dies bleibt sichtbar und wird nicht als
gelungene Erklärung nativer Wortwiederholungen dargestellt. Die feste gemeinsame
Entscheidung ist trotz der vereinbaren Werte FAIL. Alle36Vergleiche stehen in
[RESULT.json](artifacts/RESULT.json).

## Konsequenz und Grenzen

Der regelhafte Buchstabenwechsel erhält feste Teilwerte auf ausgerichteten
Codeeinheiten. Er verteilt unsere wiederkehrenden Quellwörter trotzdem auf mehr
Schreibformen als zugelassen. Ein fester eindeutig lesbarer Träger erhält die
vollständige Wortgleichheitspartition und kann den Typenfehler nicht korrigieren.
Dies ist eine bedingte Ablehnung des **genauen Quellen-/Reset-/Carriervertrags**,
keine allgemeine Widerlegung von Schreibvarianten, Abkürzung oder natürlicher
Sprache. Glyphenlänge, Edit-Distanz, q-o/finales y und Zeichenentropie wurden auf
abstrakten Aliaswerten nicht geprüft; die Rohpalette behält ihre bekannten Mängel.

52Aliaswerte werden weder zum nativen Alphabet noch zu Bedeutungen erklärt.
Die durchgehende Quellrückgewinnung gilt für vorhandene Editionsprojektionen,
nicht für ursprüngliche Manuskriptorthographie. Gleicher Autor und bekannte
Quellen; keine unabhängige historische oder semantische Bestätigung.

Den festen Entwurf schließen. Keine nachträgliche Wahl einzelner wechselnder
Buchstaben, Zusatzresets, neue Quelle oder abgeschwächte Toleranz.1206,1202,
1196/1180und die gescheiterten nativen931/928-Bindungen behalten ihre Grenzen.
1204/1205s Nachbarkontrast wird nicht mit einem neuen d-Wert gefüllt.

Vor der nächsten Konstruktion ist die gemeinsame **Quell- und Gruppierungsannahme**
gezielt zu prüfen: Welche Schlüsse beruhen auf diesen vier Editionsprojektionen
und auf einem Quellwort pro geschriebener Gruppe? Die1176–1178/1196/1203-
Gruppierungsentscheidungen bleiben bindend. Kein anderer Text, Wortbegriff oder
Schreiber ist hier schon ausgewählt; kein automatischer dritter Gedächtnisversuch.

## Reproduktion und Prüfung

```
env PYTHONHASHSEED=0 python3 experiments/yolo/gdt1207_letter_alias_parity_frequency/src/run.py
env PYTHONHASHSEED=0 python3 experiments/yolo/gdt1207_letter_alias_parity_frequency/src/validate.py
```

Der Runner benutzt einen26-Bit-Zustand, die separate Prüfung unabhängige
Vorkommenszähler je Buchstabe. Sie importiert keinen Runner, liest die Ausgabe
ohne Quellhilfe zurück und vergleicht erst anschließend. Alle1.054Rezepte,
80.931Wörter,333.022Einheiten, Frequenzlisten und36Entscheidungen stimmen überein.
Paritätsbeispiele und absichtlich falsche Aliasfolge sind geprüft; verschiedene
Quellwörter werden durch die festen Werte nicht zu derselben Einheitenganzform
zusammengeführt. [VALIDATION.json](artifacts/VALIDATION.json): **PASS**.
Das ist Software-/Quellentreue, keine Validierung einer nativen Lesung.

Alle vollständigen Aliasbücher und Stichprobenfrequenzen sind pro Quelle als
kompakte JSON-Dateien erhalten. Lokaler Konstruktions-/Auswahlcheckpoint gemäß
Nutzer-Ausnahme; kein Commit, Push oder öffentliche Publikation behauptet.
