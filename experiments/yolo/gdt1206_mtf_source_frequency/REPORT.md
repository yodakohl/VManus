# GDT1206 — bewegliche Alphabettafel: rücklesbar, Häufigkeitsprobe gescheitert

**MTF_FREQUENCY_SCREEN_FAIL.** Der feste Schreiber erzeugt auf allen vier
Quelltextsammlungen viel zu viele verschiedene Wortformen und zu geringe
Anteile der zehn häufigsten Formen. Beide notwendigen Bedingungen scheitern
gegen jede der drei getrennten Voynich-Zusammenfassungen. Eine andere feste,
eindeutig lesbare Zeichentafel kann diese Wortgleichheiten nicht verändern.

Alle **1.054 vollständigen Rezepte mit 80.931 Wörtern und 333.022 Zeichen**
werden exakt zurückgelesen. Das ist ein positiver Nachweis für Inhaltserhalt
auf den vorhandenen Editionsprojektionen, keine Übersetzung des Manuskripts.

## Was tatsächlich geprüft wurde

Der Schreiber beginnt jedes Rezept mit der Liste a–z. Für jeden Kleinbuchstaben
schreibt er dessen aktuellen Rang und schiebt den Buchstaben nach vorn. Der
Leser führt dieselbe Liste aus dem bereits gelesenen Text. 56 weitere vorab
festgelegte Zeichen bleiben durch eigene Codes erhalten, ohne die Liste zu
verändern. Quellwörter und Rezeptgrenzen bleiben unverändert; keine Wortliste,
Streichung, freie Wahl oder Bedeutungsersetzung.

Geprüft wurde nur der MTF-Teil des zuvor **unausgeführten** GDT1197-Vertrags,
jetzt unter einer eigenen [Vorregistrierung](PREREGISTRATION.md). GDT1197s
historischer Bericht bleibt unverändert. Der andere Entwurf ALT wurde nicht
ausgeführt. Die Quellen und Voynich-Zielwerte waren bereits exponiert.

Der neue Vertrag war am 5. Oktober 2026 um **14:27:22 UTC** samt Quell-, Programm-
und Validatorhashes fixiert, bevor die Codierung und Ergebniszählung begannen.
Vier unveränderte GDT1177-Sammlungen b4/w1/bs1/gr1, je die ersten 8.000 Gruppen;
Rezeptgrenzen bleiben bei Nachbarzählungen getrennt. Alle vollständigen Rezepte
sind zusätzlich codiert und zurückgelesen. Keine neue Handschriftstelle oder
Abbildung, keine Reserve, keine Sprach- oder native Zeichenwertzuweisung.

## Ergebnis

| Quelle | Verschiedene Quellwörter | Verschiedene MTF-Formen | Anteil der zehn häufigsten MTF-Formen | Exakte gleiche Nachbarpaare |
|---|---:|---:|---:|---:|
| b4 | 1.131 | 6.111 | 3,6875 % | 1 / 7.897 |
| w1 | 1.275 | 6.328 | 2,2625 % | 0 / 7.890 |
| bs1 | 1.105 | 6.351 | 5,1000 % | 0 / 7.893 |
| gr1 | 1.199 | 5.997 | 4,9750 % | 1 / 7.896 |

Die drei vorhandenen Voynich-Vergleichsausschnitte mit je 8.000 Gruppen enthalten
**2.451 / 2.530 / 2.500 Formen** für IT2a/RF1b/ZL3b. Die zehn häufigsten Formen
belegen **13,3125 / 12,6000 / 12,8750 %**. Die Leser werden nicht zusammengelegt.

Die unveränderten Toleranzen sind ±0,05 für Typenanteil und Top10-Anteil sowie
±0,01 für exakte Nachbarwiederholung. Jede Quelle scheitert an den ersten beiden
Bedingungen gegen jeden Leser: **24 feste Verletzungen**, keine knappe Grenze.
Alle zwölf Bedingungen zur exakten Nachbarwiederholung liegen formal innerhalb
der alten Toleranz. Diese ist hier so weit, dass auch null Wiederholung besteht;
daraus folgt keine überzeugende Wiedergabe der nativen Wiederholungsstruktur.
Alle 36 Vergleiche einschließlich der vereinbaren Werte bleiben in
[RESULT.json](artifacts/RESULT.json).

## Warum eine neue Zeichentafel den Fehler nicht behebt

Die Ausgabe besteht bisher aus Rangcodeeinheiten, nicht ausgewählten Voynich-
Zeichen. Ein fester eindeutig decodierbarer Träger erhält die Gleichheit und
Ungleichheit ganzer Codefolgen. Deshalb bleiben Anzahl verschiedener Wörter,
Top10-Anteil und exakte Nachbarwiederholung unter jeder solchen Zeichentafel
identisch. Diese notwendige Bedingung prüft eine ganze feste Trägerklasse.

Die Aussage gilt ausdrücklich nicht für zusätzliche zustandsabhängige Träger,
mehrdeutige Codes, andere Quellsprachen, veränderte Wortgrenzen oder andere
Resetregeln. Solche Änderungen werden hier nicht nachgeschoben. Zeichenlänge,
Edit-Distanz, q→o, finales y und Zeichenentropie wurden auf abstrakten Rängen
nicht als Voynich-Maße bewertet. Die illustrative Rohkarten-Palette behält ihre
bekannten q/y-Mängel und wurde nicht als native Zuordnung ausgewählt.

Die Buchstabenliste bewahrt zwar den Inhalt, macht aber die Schreibweise eines
wiederkehrenden Wortes stark von der vorherigen Buchstabenfolge abhängig. In
unseren vier Quellen entsteht erheblich mehr Formenvielfalt als benötigt.
Dies ist ein Befund über diesen **künstlichen Schreiber auf festen Quellen**,
kein neuer statistischer Befund über das gesamte Voynich-Manuskript.

## Auswahlkorrektur: warum keine Platzmessung folgte

Die zunächst verfolgte IDEA000200 unterscheidet geschriebene Restzeichen und
Restgruppen; ihre Rohkarte beansprucht selbst keine freie physische Fläche.
Für f108v.35/.52 ist ein unabhängig vorgegebener rechter Schreibanschlag nicht
gebunden. Das beobachtete letzte Tintenende ist ein Ergebnis der Niederschrift,
kein Nachweis des zuvor verfügbaren Raums. Auch eine genaue Pixelzählung
beantwortet diese Frage daher nicht von selbst.

Die ältere [Primärkorrektur vom 5. September](../../../docs/visual_overview/NEXT_STEP.md)
hatte die Breitenmessung bereits als Hauptpriorität zurückgenommen: eine passende
Breite unterscheidet Inhalt und Schreibkonvention kaum; ein Gegenbefund trifft
nur die enge unmittelbare Platzsparregel. Diese Grenze wird übernommen. Es gab
hier **keine neue Bildmessung und kein negatives Messergebnis**. Die allgemeine
Platzdruckfrage und IDEA200s ursprüngliche beschreibende Kontextfrage bleiben
ungetestet. Eine kausale Erweiterung braucht ein unabhängiges Raummaß und eine
festgelegte Regel, statt den letzten geschriebenen Strich zum Sollrand zu machen.

## Vorgänger, Entscheidung und nächste Auswahl

- GDT001s nativer inverser MTF-Test bleibt gescheitert: sechs Sprachpakete, Ordnung2, physische Zeilenresets. Dieser Vorwärtstest ist kein neuer nativer Schlüsselversuch.
- GDT1202s Schranke für höchstens zwei Ganzwortvarianten bleibt gültig. Die 26!-Alphabetordnung war davon nicht erfasst; mehr mögliche Zustände lösen die Wortverteilung aber nicht automatisch.
- GDT1193s kostspieliger Grundkontroll-Pass sowie GDT1194/1195/1196/1180s jeweilige Fehlschläge bleiben unverändert.
- GDT1204/1205s bedingter chey/chedy-Gegenfall und begrenzte Bildstützung werden weder erklärt noch umgedeutet. Gleiche Nachbarn wählen MTF nicht aus.

**Diesen festen MTF-Quell-/Trägervertrag schließen.** Keine andere Zeichentafel,
neue Toleranz, zusätzliche Resetregel oder weitere Quelle automatisch versuchen.
ALT bleibt unausgeführt. Vor dessen möglicher Auswahl ist IDEA000938s Unterschied
zu prüfen: Jeder Alias hat dort einen festen Quellbuchstabenwert, während MTF-
Ränge ihre Buchstabenwerte wechseln. Ob diese Bindung eine passende Erklärung
wiederkehrender ganzer Teile ermöglicht, ist eine separate Auswahlfrage. Eine
native Teilgrenze, daldy-Deutung oder konkrete Buchstabenzuordnung wird dadurch
nicht angenommen. Kein nächster Versuch ist ausgewählt.

## Prüfung und Reproduktion

```
env PYTHONHASHSEED=0 python3 experiments/yolo/gdt1206_mtf_source_frequency/src/run.py
env PYTHONHASHSEED=0 python3 experiments/yolo/gdt1206_mtf_source_frequency/src/validate.py
```

Beide abgeschlossen. Der separate Validator benutzt Zeitstempel letzter
Verwendungen anstelle der verschobenen Liste und importiert keinen Runner.
Er rekonstruiert sämtliche Rangfolgen, liest nur aus den ausgegebenen Rängen
zurück und prüft erst danach gegen den Quelltext. Alle Rezepte, Wörter,
333.022 Einheiten, Frequenzlisten und 36 Entscheidungen stimmen überein:
[VALIDATION.json](artifacts/VALIDATION.json), **PASS**. Gleicher Autor, keine
unabhängige semantische Bestätigung oder Prüfung menschlicher Praktikabilität.

Vollständige Rangbücher und Stichprobenfrequenzen liegen pro Quelle als kompakte
JSON-Dateien vor. Eingaben sind über REGISTRATION_LOCK.json gebunden. Kein
scorefähiges semantisches Relationspaket und keine native Wortzuweisung.
Lokaler Konstruktions-/Auswahlcheckpoint gemäß Nutzer-Ausnahme; kein Commit,
Push oder öffentliche Veröffentlichung wird behauptet.
