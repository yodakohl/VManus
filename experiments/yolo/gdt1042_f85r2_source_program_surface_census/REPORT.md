# GDT1042 — gemeinsame Formen, keine gebundene Jahreszeitenlesung

**COMPLETE_DESCRIPTIVE_CENSUS_NO_MEANING_BINDING.** Die vier räumlichen
Textblöcke teilen mehrere Gesamtformen. Die Wiederholungen liefern jedoch
keine Wortbedeutung und keine in allen drei Lesungen wiederkehrende Zweier-
oder Dreierfolge. Das ist ein vollständiges lokales Inventar, kein neuer
Nachweis der astrologisch-medizinischen Deutung.

Die [registrierte Methode](METHOD.md) wurde vor der aktuellen Abfrage
hashgebunden. Die Seite war bereits Projektdatenmaterial. Alle 473
transkribierten Gruppen der drei alternativen Lesungen wurden über den
Selektor-Guard erfasst; davon gehören 108/107/109 zu den festgelegten Absätzen.
Die übrigen 48/50/51 Gruppen aus .1 und .24 sind vollständig separat enthalten.
Keine Bildöffnung, Reservenutzung, neue Zerlegung oder übernommene Wortglosse.

| Räumlicher Block | Zeilen | Gruppen ZL / IT / RF | Verschiedene Gesamtformen ZL / IT / RF |
|---|---|---|---|
| Nord | 2–6 | 19 / 19 / 19 | 18 / 18 / 18 |
| Ost | 7–11 | 27 / 27 / 27 | 27 / 27 / 27 |
| Süd | 12–17 | 26 / 26 / 26 | 24 / 24 / 24 |
| West | 18–23 | 36 / 35 / 37 | 29 / 30 / 32 |

Alle sechs Absatzpaare, ohne Auswahl oder Rangfolge:

| Paar | Gemeinsame vollständige Formen in ZL3b | Unterschiede IT2a / RF1b |
|---|---|---|
| N–E | aiin, daiin | dieselben |
| N–S | aiin, or | dieselben |
| N–W | aiin, chol, or | dieselben |
| E–S | aiin, oteey | dieselben |
| E–W | aiin, ol | dieselben |
| S–W | aiin, ain, chedy, or, qodaiin, shedy | IT: qodain statt qodaiin; RF: `{ch'}edy` statt shedy |

`aiin` ist in jeder Lesung die einzige identische Gesamtform in allen vier
Blöcken. Das macht sie nicht zu JAHR, JAHRESZEIT, MENSCH oder einer anderen
Übersetzung. Der Süd-West-Vergleich hat sechs gemeinsame Formen; daraus folgt
ohne Längen-/Häufigkeitskontrolle weder eine besonders enge semantische
Verbindung noch ein Herbst-Winter-Paar. Die Blockbezeichnungen sind räumlich.

Die einzige wiederholte Zweierfolge ist `or aiin`: ZL dreimal (.2, .20, .22),
RF zweimal (.2, .22), IT ohne Wiederholung. ZL markiert zwei dieser Abstände
als unsicher. In IT steht .20 `ar aiin`, und .22 hat `or aiinog`. Es wurde
nichts zusammengeführt oder korrigiert, um eine gemeinsame Konstruktion zu
erzeugen. Wiederholte Dreierfolgen: null in jeder Lesung.

Die vollständige Tabelle der Ein-Edit-Nachbarn enthält 45/43/32 Paare. Sie
prüft alle 3240/3570/2701 Paare der dafür geeigneten verschiedenen
Buchstabenformen. Markierte Gruppen bleiben im Gesamtinventar, sind aber
aus dieser einen Zusatzanalyse ausgeschlossen: 4/1/14 verschiedene Formen,
4/1/15 Vorkommen. Ein Edit in einer Transkription ist weder ein Lautwechsel
noch ein nachgewiesenes Morphem. Der bereits bekannte produktive Wortbau
wird dadurch nicht erneut als neue Entdeckung beansprucht.

Alle 72 Zeileninstanzen enthalten ihre erste und letzte Gruppe samt
Abstandsmarkierungen. Die fünf Nord- und Ost- sowie sechs Süd- und Westzeilen
werden nicht zu Reimpaaren oder einer umlaufenden Leseordnung umgedeutet.
Die Absatzanfänge sind in allen drei Lesungen `sain`, `pchedeey`, `otchs`,
`okees` (N/E/S/W). Die Endgruppen sind N `roseer`/`sosees`/`sosees`, E
`chok{co}m`/`chokcod`/`chot{co}g`, S `ain` und W `sheoly`.
Auch die vollständigen Randgruppen liefern somit keine identische
wiederkehrende Viererbeschriftung; eine abstraktere Konstruktion ist damit
nicht ausgeschlossen.
Ohne physisch identifizierte Konstruktion lässt sich keine konkrete
Monats-, Alters- oder Humorenbezeichnung zuordnen.

## Vollständige prüfbare Daten

- [Alle Gruppen und Positionen](artifacts/native_groups.tsv), einschließlich .1/.24.
- [Blockgrößen](artifacts/block_counts.tsv) und [alle gemeinsamen Formen mit Belegen](artifacts/block_intersections.tsv).
- [Alle wiederholten Formen](artifacts/repeated_forms.tsv) und [Zweier-/Dreierfolgen mit Abstandssignaturen](artifacts/repeated_ngrams.tsv).
- [Alle Ein-Edit-Paare mit Vorkommen](artifacts/literal_edit1_pairs.tsv).
- [Jeder Zeilenanfang und jedes Zeilenende](artifacts/line_first_last.tsv).
- [Maschinenlesbarer Befund](artifacts/RESULT.json) und [unabhängige Rekonstruktion](artifacts/VALIDATION.json).

Ausführen: `python3 experiments/yolo/gdt1042_f85r2_source_program_surface_census/src/run.py`,
anschließend `python3 experiments/yolo/gdt1042_f85r2_source_program_surface_census/src/validate.py`.
Die Quellprojektion hat SHA256
`489c3960116c88f76de39187eef3d2f9d3dd68d3c2e514f54abe7a2294d185e9`.
Die unabhängige Prüfung rekonstruiert Tabellen, nicht Handschriftenbedeutungen.

## Entscheidung

Die im [Quellenvergleich](../../../research_registry/proposals/laufenberg_f85r2_20260926/REPORT.md)
präzisierte Bildtradition bleibt eine Arbeitshypothese. Das Textinventar liefert
konkrete Vergleichsstellen, **bestätigt aber keine der saisonalen oder
medizinischen Bedeutungen**. Keine Signifikanzbehauptung und kein positiver
Test einer Suchfamilie. GDT884, F85B001 und der alte Absatzordnungs-Stopp werden
nicht wiederholt oder umgedeutet. Unabhängige Bestätigungskapazität hier: null,
denn nur ein bereits exponiertes physisches Blatt. Bestätigt übersetzte Wörter: null.
