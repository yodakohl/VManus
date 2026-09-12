# P17 — Themenwechsel mit gemeinsamem Geltungsbereich

Die beiden neuen Diskursfassungen N und R sind auf dem gesamten f83r-Prose-Arbeitsblatt ausgeführt. Keine neue Wortbedeutung wurde ergänzt. Sie halten ausdrücklich fest, welche Materialnennungen das Thema ändern und welche Hintergrund bleiben. Die folgenden Unterschiede sind Konsequenzen dieser Annahmen, keine Bestätigung ihrer Richtigkeit.

| Modell | Wechsel | Wechselblöcke mit ≥2 Aussagen | ≥2 andere Bezüge als L1 | ≥2 andere Bezüge als T0 | beides im selben Block |
|---|---:|---:|---:|---:|---:|
| N | 4 | 4 | 2 | 4 | 2 |
| R | 3 | 0 | 0 | 0 | 0 |
| L1 | 11 | 3 | 0 | 1 | 0 |
| T0 | 0 | 0 | 0 | 0 | 0 |

N macht eine erste Materialnennung zum neuen Thema und lässt spätere bekannte Nennungen im Hintergrund. R wechselt erst bei erneuter Nennung des anderen Materials. Die Wiederholung des aktuellen Themas ist in beiden nur Wiederaufnahme. L1 (letztes Material) und T0 (erstes Material) sind die unveränderten P12-Baselines. Ein Block endet am nächsten tatsächlichen Themenwechsel oder an der Recordgrenze. B=Gefäß aktualisiert nur das Ziel. Keine Bildposition und kein unbekanntes Wort liefert einen freien Themenmarker.

Alle vier Fassungen: 341 Gruppen, 50 Positionen mit P12-Hypothesen, 291 offen; 20 Prädikationen. Ein gemeinsames Thema kann fehlende Ziele nicht ersetzen. Die exakten Vollständigkeitszahlen stehen in RESULT.json und an jedem Prädikat.

## Alle Wechselblöcke der neuen Modelle

| Modell | Beginn | Wechsel | Ende vor | sämtliche Aktionen | vollständig | andere Bezüge L1 / T0 |
|---|---|---|---|---|---:|---|
| N | f83r.3:7 | A→C | RECORD_END | f83r.4:2,f83r.4:9,f83r.6:6,f83r.6:7,f83r.8:5 | 5 | 3 / 5 |
| N | f83r.11:9 | A→C | RECORD_END | f83r.14:2,f83r.16:5 | 2 | 1 / 2 |
| N | f83r.19:11 | A→C | RECORD_END | f83r.21:5,f83r.22:3,f83r.22:5,f83r.23:9 | 3 | 1 / 4 |
| N | f83r.37:5 | C→A | RECORD_END | f83r.42:5,f83r.43:3 | 2 | 2 / 2 |
| R | f83r.6:8 | A→C | RECORD_END | f83r.8:5 | 1 | 0 / 1 |
| R | f83r.14:6 | A→C | RECORD_END | f83r.16:5 | 1 | 0 / 1 |
| R | f83r.44:2 | C→A | RECORD_END | NONE | 0 | 0 / 0 |

## Sämtliche Prädikationen im direkten Vergleich

| Ort | Wort | N | R | L1 | T0 | Ziel |
|---|---|---|---|---|---|---|
| f83r.2:10 | chedy | A | A | A | A | NA |
| f83r.4:2 | chedy | C | A | C | A | NA |
| f83r.4:9 | chedy | C | A | A | A | NA |
| f83r.6:6 | chedy | C | A | A | A | NA |
| f83r.6:7 | qokeedy | C | A | A | A | B |
| f83r.8:5 | chedy | C | C | C | A | NA |
| f83r.14:2 | qokeedy | C | A | A | A | B |
| f83r.16:5 | chedy | C | C | C | A | NA |
| f83r.21:5 | chedy | C | A | C | A | NA |
| f83r.22:3 | qokeedy | C | A | C | A | NA |
| f83r.22:5 | chedy | C | A | C | A | NA |
| f83r.23:9 | chedy | C | A | A | A | NA |
| f83r.25:1 | qokeedy | NA | NA | NA | NA | NA |
| f83r.25:5 | chedy | NA | NA | NA | NA | NA |
| f83r.27:2 | chedy | A | A | A | A | NA |
| f83r.27:3 | qokeedy | A | A | A | A | NA |
| f83r.30:3 | qokeedy | A | A | A | A | NA |
| f83r.42:5 | chedy | A | C | C | C | NA |
| f83r.43:3 | chedy | A | C | C | C | NA |
| f83r.49:3 | chedy | NA | NA | NA | NA | NA |

## Konkrete bedingte Lesungsfolge

N eröffnet bei lchedy auf f83r.3:7 das Thema Zusatzstoff. Dadurch heißen .4:9, .6:6 und .6:7 hypothetisch: Erwärme den Zusatzstoff; erwärme ihn; fülle ihn in das genannte Gefäß. L1 und T0 beziehen diese drei Aktionen auf die Flüssigkeit. Das geerbte Verb und das Füllziel bleiben gleich. Die schriftlichen shedy-Wiederholungen auf .4/.5 werden in N Hintergrund, nicht jeweils neue Patienten; genau diese starke Annahme bleibt sichtbar.

Im späteren Record P5 eröffnet shedy auf .37:5 das neue Thema Flüssigkeit. N bindet beide Erwärmungen .42:5/.43:3 an sie, obwohl lchedy auf .41:3 dazwischensteht. R/L1/T0 bleiben dort beim Zusatzstoff. Beide Aktionen sind derselbe angenommene Verbtyp, also keine zwei unabhängigen Bedeutungsbelege. Beide N-Blöcke enden erst mit ihrem Record; eine innere Beendigung durch einen weiteren neuen Materialtyp ist bei nur A/C nach dem zweiten Typ nicht möglich. Diese lexikalisch bedingte Kapazitätsgrenze wurde nicht als entdecktes Satzende ausgegeben.

## Entscheidung und Grenzen

N besitzt zwei Wechselblöcke, die jeweils mindestens zwei Bezüge gegenüber beiden Baselines verändern. R hat keinen Wechsel mit zwei nachfolgenden Prädikationen; seine mehrteiligen Unterschiede entstehen nur durch initiale Themenpersistenz. Für die weitere Ausarbeitung einer echten Wechselregel bietet N damit den konkreteren Arbeitskandidaten, ohne als richtige Übersetzung gewählt zu sein. Ein Wechselblock liefert nur dann eine neue mehrteilige Lesungskonsequenz gegenüber den Baselines, wenn tatsächlich mehrere Bezüge abweichen. Initiale Persistenz, reine Umbenennung und passende Einzelbezüge werden nicht dafür gezählt. Die Tabellen zeigen alle Fälle einschließlich leerer Wechselblöcke; keine nachträgliche Kürzung oder Umverteilung. Keine dieser Zählungen ist ein Test gegen unabhängige richtige Argumente. N/R bleiben deshalb Diskursrivalen; eine kleinere Anzahl Wechsel oder flüssigere deutsche Formulierung wählt kein Modell aus.

A=Flüssigkeit und C=Zusatzstoff können inhaltlich anders heißen, ohne die Themenrechnung zu ändern. Selbst die als Kontrast bezeichnete R-Umschaltung hat keinen gebundenen semantischen Gegensatz. Die fünf geerbten Wortkarten bleiben Annahmen. Die 291 offenen Gruppen könnten Satz-, Themen- oder Gegenstandsgrenzen enthalten; ihre Behandlung als für dieses begrenzte Register wirkungslos ist keine Entzifferung.

P1–P3 dienen der ersten Ausarbeitung; die übrigen vier Records werden unverändert mitgerechnet. Alle waren vorher exponiert, also keine unabhängige Bestätigung. Q1/Q2 werden als eigene Records behandelt, nicht mit einem Bildthema aufgefüllt. Keine Bildlabels oder neuen Seiten geöffnet; f84/f84r bleiben geschlossen. Keine Signifikanz oder score-ready Relationsevidenz.

## Quellen und Reproduktion

GDT790/792/809/220 und P12/P18 bleiben unverändert. Die Diskursregeln sind in DECISION.md vor Ausführung festgelegt; SOURCE.json bindet sie und die begrenzte P12-Projektion. TOPIC_BLOCKS.tsv und MENTIONS.tsv ergeben den vollständigen Themenbaum; PREDICATIONS.tsv listet jedes ergänzte Material und Ziel samt Schriftquelle. READING_N/R/L1/T0.md zeigen sämtliche Zeilen einschließlich aller unübersetzten Gruppen.

`python3 research_registry/proposals/translation_programs_20260912/work/P17/build.py`; `python3 research_registry/proposals/translation_programs_20260912/work/P17/validate.py` aus dem Repository.
