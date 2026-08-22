# V78 R1 — kontinuierliche Arbeitsübersetzung aller elf Prosa-Records

## Ergebnis

Die dritte Arbeitsedition bindet alle 381 ausgewählten Prosaereignisse genau einmal an zwei getrennte Ebenen:

1. eine Literalspur aus exakter Karten-ID und dem einzig erlaubten V77-Status;
2. eine kontinuierliche deutsche Quellenausweitung, in der jedes nicht historisch gebundene konkrete Wort sichtbar als `[EXEMPLAR:…]` steht.

Die elf Records H1–H5 und B1–B6 sind vollständig. Kein physisches Zeilenende wurde automatisch zum Satzende. Die 116 V72-Satzverbände liefern die Satzgrenzen; ihre Zeilen- und Feldübergriffe bleiben ausgewiesen. Zehn sichtbare biologische Besitzerwechsel setzen Stoff, Ziel und Richtung ausdrücklich zurück.

Die maschinelle Validierung ist `PASS`:

- 381/381 Ereignisse in strenger Reihenfolge;
- 19/19 `dcda…` ausschließlich als `ET? = UND?/AUCH?`;
- 9/9 `b5fcea…` ausschließlich als `PER? = DURCH?/GEMÄSS?`;
- 26 Vorkommen der zwei formalen Karten ausschließlich als `[FORMAL; KEIN WORT]`;
- 327 übrige Ereignisse ausschließlich als sichtbare Quellenausweitung;
- 28 vollständige ET/PER-Fitprüfungen;
- elf Record-Konflikte plus 28 lokale ET/PER-Konflikte;
- keine versiegelte Seite geöffnet.

Dies ist eine kreative Arbeitsübersetzung, keine Entzifferung oder bestätigte Übersetzung.

## Feste Werkstattregel

Ein Lehrling erhält zwei übereinanderliegende Spuren.

**Schreibspur**

1. Kopiere jede exakte Karten-ID in der gegebenen Reihenfolge.
2. Lies `dcda95c81a5460feb191` nur als `ET?`; im deutschen Arbeitslauf darf es ausschließlich `UND?` oder `AUCH?` werden.
3. Lies `b5fcea1eaed06b2f2291` nur als `PER?`; im deutschen Arbeitslauf darf es ausschließlich `DURCH?` oder `GEMÄSS?` werden.
4. Schreibe die beiden Karten `2f1c5e56e8f0ff459065` und `308e8ea2d5d190c498e8` nur als `[FORMAL; KEIN WORT]`. Der Lehrling darf ihnen weder Maß, Ziel noch irgendeinen anderen Wortwert geben.
5. Jede andere Karte bleibt in der Literalspur `[EXEMPLARWERT UNBEKANNT]`.

**Rücklesespur**

1. Alles Konkrete aus Bildbesitzer, Mastervorlage oder früherer Arbeitsedition steht vollständig innerhalb `[EXEMPLAR:…]`.
2. Fehlt ein Prädikat, ein Objekt oder ein Rückbezug, steht die Ergänzungsstelle nochmals als `[ELLIPSE:…]` in dieser Exemplarklammer.
3. Ein Satz darf über physische Linien und Felder weiterlaufen, wenn V72 denselben Satzverband trägt.
4. Bei einem sichtbaren Stationswechsel beginnt ein neuer lokaler Besitzer. Stoff, Ziel und Richtung werden nicht vererbt.
5. Erst wird die Literalspur Karten für Karte kontrolliert; erst danach darf die Quellenausweitung flüssig gelesen werden.

Damit kann eine zweite Hand dieselbe Seite fortsetzen, ohne 173 erfundene Wörter lernen zu müssen.

## ET/PER-Druckprobe

### ET?

Alle 19 Vorkommen bleiben in der additiven Kategorie:

- 16 werden `UND?`;
- 3 werden `AUCH?`;
- 10 sind lokal gut brauchbar, 9 angespannt, aber einsinnig;
- kein Vorkommen erhält zusätzlich „fortführen“, „Arbeitsstand“, „danach“, „vorher“ oder einen anderen Kartenwert.

Die klarsten Werkstattbeispiele sind die beiden wiederholten Ketten:

`E26 [EXEMPLAR] – E27 ET? – E28 [EXEMPLAR] – E29 ET? – E30 [FORMAL] – E31 [EXEMPLAR]`

und

`E132 [EXEMPLAR] – E133 ET? – E134 [EXEMPLAR] – E135 ET? – E136 [EXEMPLAR]`.

Sie können als additive Aufzählungen rückgelesen werden. Schwächer sind E370 sowie E376/E378, weil dort ET? an einen absichtlich wortlosen formalen Posten anschließt. Diese Fälle kosten 2/4 und dürfen nicht durch einen Zusatzsinn gerettet werden.

### PER?

Die neun Vorkommen bleiben ausnahmslos bei `DURCH?` oder `GEMÄSS?`:

- 3 werden `DURCH?`;
- 6 werden `GEMÄSS?`;
- 7/9 stehen am Feldanfang;
- E180 steht am Feldende, E219 im Feldinneren;
- E56 sowie das unmittelbar doppelte E180–181 kosten 3/4.

Die notwendigen Komplemente sind nicht Teil von PER?. Sie werden deshalb als `[EXEMPLAR:… [ELLIPSE:lokales Komplement]]` angezeigt. Gerade E180–181 bleibt ein offener Widerspruch: zwei benachbarte PER?-Karten können als `DURCH? … GEMÄSS? …` gelesen werden, aber diese Lösung benötigt zwei ergänzte lokale Bezüge. Die Edition behält die Hypothese explorativ, erklärt den Doppelbeleg jedoch nicht für glatt oder bestätigt.

## Elf Records

| Record | Seite | Events | Felder | Statements | ET/PER | Reparaturkosten |
|---|---|---:|---:|---:|---|---:|
| H1 | f10r | 14 | 2 | 2 | ET 1 / PER 0 | 3 |
| H2 | f10r | 24 | 3 | 3 | ET 2 / PER 0 | 3 |
| H3 | f11r | 17 | 4 | 4 | ET 0 / PER 0 | 3 |
| H4 | f55v | 18 | 4 | 4 | ET 0 / PER 1 | 3 |
| H5 | f56r | 27 | 7 | 6 | ET 0 / PER 0 | 3 |
| B1 | f81v | 66 | 24 | 21 | ET 9 / PER 1 | 3 |
| B2 | f82r | 62 | 26 | 22 | ET 0 / PER 3 | 4 |
| B3 | f83r | 86 | 38 | 34 | ET 1 / PER 4 | 4 |
| B4 | f83r | 47 | 20 | 16 | ET 2 / PER 0 | 3 |
| B5 | f83r | 11 | 5 | 3 | ET 2 / PER 0 | 2 |
| B6 | f83r | 9 | 2 | 1 | ET 2 / PER 0 | 2 |

Die vollständigen Literalspuren und Volltexte stehen in `V78_R1_ELEVEN_RECORDS_CONTINUOUS.md` sowie maschinenlesbar in `V78_R1_11_RECORD_CONTINUOUS.tsv`.

### H1–H5

Die Herbal-Records bleiben Ganzpflanzenartikel. Wurzel, Blätter, Blüten, Wasser, Wein, Öl, Honig, Krankheit, Dosis und Anwendung sind keine Kartenwörter; sie stehen vollständig als Exemplarinhalte. H5-S001 überschreitet wie in V72 ein formales Locus-/Feldende. Die wichtigste Korrektur gegenüber älteren Wörterbüchern ist, dass wiederholte konkrete Handlungen nicht zurück in eine portable Kartenbedeutung gelangen.

### B1–B6

Die Bio-Records bleiben lokale Stationsartikel. Gefäß, Becken, Lauf, Flüssigkeit, Bad, Körperstelle, Wärme, Richtung und Anwendung sind kreative Exemplarinhalte. Der Text darf einen sichtbaren Abstand überschreiten, doch an jedem der zehn Besitzerbrüche wird der lokale Zustand zurückgesetzt. Die Edition behauptet keinen globalen Kreislauf und keine gemeinsame Flussrichtung.

B2 und B3 erhalten Reparaturkosten 4/4, weil ihre V72-Sätze bereits Besitzerwechsel und starke Quellenannahmen überbrücken; das ist kein ET/PER-Scheitern. Innerhalb der Rollenkarten ist PER? in B2 am teuersten. B5 und B6 sind kurz und formal gut kopierbar, aber ihre ET?-Verbindungen liegen teilweise neben wortlosen Markierungen.

## Konflikte und echte Lehrlingsfehler

Die häufigsten Fehler wären:

- ein früheres Mnemonikwort wie MASS, ANWENDEN, BEREIT oder ABLASSEN wieder auf die Karte zu schreiben;
- `[FORMAL; KEIN WORT]` doch als Maß- oder Zielwort zu lesen;
- ET? als „fortführen“ zu retten, sobald UND?/AUCH? grammatisch unbequem wird;
- PER? als beliebiges Satzanfangssignal statt ausschließlich DURCH?/GEMÄSS? zu verwenden;
- ein ergänztes PER-Komplement als Teil des Kartenwertes auszugeben;
- eine nominale Quellellipse unmarkiert zu lassen;
- einen Satz am physischen Zeilenende abzubrechen;
- am Bio-Stationswechsel Stoff, Ziel oder Richtung weiterzutragen;
- Herbal-Inhaltswörter aus Bildähnlichkeit oder historischer Plausibilität zu Wörterbucheinträgen zu machen.

`V78_R1_CONTRADICTIONS.tsv` hält deshalb nicht nur elf allgemeine Record-Gegenargumente fest, sondern auch jeden der 28 lokalen ET/PER-Rivalen und seine Reparaturkosten.

## Interpretation ceiling

V77 liefert für `et` und `per` echte 1414er Codebuchkategorien, nicht die Identität der Voynich-Karten. V78 zeigt lediglich, dass diese zwei minimalen Kategorien ohne Zusatzsinn durch alle 28 festgelegten Stellen geführt werden können, wenn zahlreiche lokale Inhalte explizit aus dem Masterexemplar ergänzt werden. Besonders PER? bleibt wegen E56 und E180–181 fragil.

Es folgen daraus keine bestätigten Kartenwörter, Stämme, Laute, PAGE_HOST-Werte, Sprache, medizinischen Tatsachen oder Übersetzungen. Die Edition öffnet keine weitere Seite und verwendet f84/f84r nicht.

## Dateien

- `V78_R1_381_EVENT_CONTINUOUS_INTERLINEAR.tsv`
- `V78_R1_11_RECORD_CONTINUOUS.tsv`
- `V78_R1_ELEVEN_RECORDS_CONTINUOUS.md`
- `V78_R1_ET_PER_28_FIT.tsv`
- `V78_R1_CONTRADICTIONS.tsv`
- `V78_R1_BUILD_SUMMARY.json`
- `V78_R1_build_continuous_records.py`
- `V78_R1_validate_continuous_records.py`
- `V78_R1_VALIDATION.json`
