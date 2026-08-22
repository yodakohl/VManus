# V78 R3 — kontinuierliche Prosarecords aus Sicht des technischen Registerschreibers

Status: unabhängige kreative Werkstattrekonstruktion auf den festgelegten zehn
Seiten; **keine Übersetzung, kein GDT-Ergebnis und keine Entzifferung**.

## Ergebnis

Die mechanische Ausgabe ist vollständig: 381/381 Events stehen genau einmal in
exakter Kartenreihenfolge, gehören genau einem der 116 Sätze und genau einem der
elf Prosarecords an. Die vollständigen eventgebundenen und flüssigen Recordtexte
stehen in `V78_R3_11_RECORD_CONTINUITY.tsv`; die 381 Einzelbindungen stehen in
`V78_R3_381_EVENT_CONTINUITY.tsv`.

V77 wird ohne Ausnahme angewandt:

- `dcda95c81a5460feb191` erscheint 19/19-mal ausschließlich als `ET?`;
- `b5fcea1eaed06b2f2291` erscheint 9/9-mal ausschließlich als `PER?`;
- `2f1c5e56e8f0ff459065` erscheint 20/20-mal als
  `[FORMAL_PARAMETER_CHANNEL; KEIN_WORT]`;
- `308e8ea2d5d190c498e8` erscheint 6/6-mal als
  `[FORMAL_RELATION_SLOT_CHANNEL; KEIN_WORT]`;
- die übrigen zwanzig V77-Zielkarten bleiben `EXEMPLAR_VALUE_UNKNOWN`;
- die 149 nicht in V77 auditierten Karten erhalten ebenfalls kein Wort, sondern
  `[EXEMPLARWERT UNBEKANNT; NICHT V77-ZIEL]` auf Statusebene.

Damit besitzen nur 28/381 Ereignisse überhaupt eine portable, stets
fragezeichenpflichtige Wortschicht. 143 Ereignisse gehören zu den zwanzig
auditierten unbekannten Zielkarten, 184 zu nicht auditierten Karten und 26 zu
den zwei formalen Nichtwortkanälen. Jede konkrete Sachhandlung bleibt davon
getrennt in einer Klammer der Form
`[MASTER-EXEMPLAR; KEINE WORTBEDEUTUNG: …]`.

## Ausführbare Leserregel

Für jedes Ereignis wird ohne Rückgriff auf Kartenbestandteile in dieser
Reihenfolge gelesen:

1. Drucke die ungeteilte Identität als
   `E###=[OPAQUE_EXACT_CARD:<joint_tuple_id>]`.
2. Schlage ausschließlich die komplette Identität in der eingefrorenen
   V77-Tabelle nach.
3. Drucke genau `ET?`, `PER?`, einen der zwei ausdrücklich nichtlexikalischen
   Formalkanäle oder `[EXEMPLARWERT UNBEKANNT]`.
4. Hänge die ausgewählte V73-/V74-Sachhandlung in eckigen
   `MASTER-EXEMPLAR`-Klammern an. Sie ist kein Kartenwert.
5. Ordne das Event seinem V72-Satz zu. Ein Feld- oder physischer Zeilenwechsel
   beendet den Satz nur dann, wenn die eingefrorene Satzgliedschaft endet.
6. Bei einer sichtbaren Bio-Besitzerlücke lösche Stoff, Ziel und Richtung, auch
   wenn der editorische Satz weiterläuft.

Die Regel benutzt weder Kartenbestandteile noch Lautwerte, Schreibungssimilarität
oder verborgene Koordinaten. Die alte Mnemonikschicht `MASS?`, `ANWENDEN?`,
`BEREIT?`, `ANSATZ?`, `ZIEL?`, `KLAR?`, `VORIGES?`, `ANTEIL?`,
`TEMPERIEREN?`, `SPÜLEN?`, `ABLASSEN?` wird nirgends als Wörterbuch gelesen.
Dass in einer Klammer etwa „Maß“, „Spülen“ oder „Ansatz“ steht, ist allein eine
occurrence-gebundene Ausschreibung des angenommenen Masterexemplars.

## Satz- und Zeilenkontinuität

Die Ausgabe bestätigt die für diese Werkstatttheorie wichtige Korrektur, dass
eine Aussage nicht mit einer physischen Zeile enden muss:

- 18/116 Sätze überschreiten mindestens eine Feldgrenze;
- dieselben 18 überschreiten mindestens eine physische Zeilengrenze;
- insgesamt liegen 19 Feld- und 19 Zeilenübergänge innerhalb eines Satzes vor,
  weil `B5-S003` zwei Übergänge enthält;
- 98 Sätze bleiben innerhalb eines Feldes beziehungsweise einer physischen
  Zeile.

Die vollständigen Übergänge sind:

```text
H5-S001
B1-S002 B1-S003 B1-S018
B2-S004 B2-S005 B2-S012 B2-S016
B3-S016 B3-S021 B3-S026 B3-S030
B4-S003 B4-S011 B4-S015 B4-S016
B5-S003
B6-S001
```

Zehn sichtbare Bio-Besitzerwechsel erzwingen einen Reset. Sechs fallen auf
einen neuen Satzbeginn. Vier schneiden tatsächlich durch einen bereits
laufenden Satz und werden deshalb ausdrücklich gedruckt:

| Reset-Event | Satz | technische Wirkung |
|---:|---|---|
| 203 | `B2-S012` | ungelöste Mittelstation → unteres Mehrfigurenfeld; Stoff, Ziel, Richtung löschen |
| 264 | `B3-S016` | rechte Randstation → eigentümerloser Zwischenbereich; Stoff, Ziel, Richtung löschen |
| 291 | `B3-S026` | Zwischenbereich → gekoppeltes Hauptbogenpaar; Stoff, Ziel, Richtung löschen |
| 356 | `B4-S015` | Hauptbogenpaar → linke offene Fransenstation; Stoff, Ziel, Richtung löschen |

Das sind reale lokale Kontinuitätsbrüche der Bildbindung. Sie dürfen nicht durch
eine unsichtbare Leitung oder einen globalen Prozess repariert werden.

## Elf vollständige Recordausgaben

Die Recordtabelle enthält für jede der folgenden Einheiten die vollständige
opaque Kartenfolge, die Wort-/Nichtwortschicht, eine E###-gebundene lückenlose
Ausschreibung und den flüssigen Recordtext:

| Record | Events | Felder | Sätze | feldübergreifende Sätze | ET? | PER? | technische Gegenlesung |
|---|---:|---:|---:|---:|---:|---:|---|
| H1 | 14 | 2 | 2 | 0 | 1 | 0 | Wurzelprobe säubern, wässrig ausziehen, Prüfportion buchen, Rest lagern |
| H2 | 24 | 3 | 3 | 0 | 2 | 0 | zwei Erntefraktionen pressen, vergleichen und als Materiallose konservieren |
| H3 | 17 | 4 | 4 | 0 | 0 | 0 | Blüten-/Blattfraktionen extrahieren, klären und als Referenzproben lagern |
| H4 | 18 | 4 | 4 | 0 | 0 | 1 | zwei Blattlose mazerieren, waschen, vergleichen und lagern |
| H5 | 27 | 7 | 6 | 1 | 0 | 0 | Frischprobe, Trockenlos und schwachen Auszug getrennt führen |
| B1 | 66 | 24 | 21 | 3 | 9 | 1 | ein lokales Bade-/Waschhaus-Regimen ohne globalen Kreislauf buchen |
| B2 | 62 | 26 | 22 | 4 | 0 | 3 | fünf getrennte Stationsposten mit vier harten Besitzerresets führen |
| B3 | 86 | 38 | 34 | 4 | 1 | 4 | Randstationen, Zwischenbereich und Hauptbogenpaar getrennt buchen |
| B4 | 47 | 20 | 16 | 4 | 2 | 0 | Hauptbogenpaar und zwei voneinander getrennte Endstationen führen |
| B5 | 11 | 5 | 3 | 1 | 2 | 0 | linken offenen Endposten als eigenen Kurzartikel buchen |
| B6 | 9 | 2 | 1 | 1 | 2 | 0 | rechten S-Lauf-/Mehrarm-Endposten als eigenen Artikel buchen |

Für Herbal ist der Prozessrival jeweils das nichtmedizinische
Pflanzenmaterial-Los aus V73. Für Biological ist er das örtliche
Badehaus-/Waschhaus-Betriebsregister aus V74. Der durchgehende Notationsrival
ist ein bildgebundener Muster- oder Stationsatlas: die Karten markieren
Einträge, Verknüpfungen, lokale Parameterstellen und Abschlüsse, während die
Sachwörter nur im verlorenen beziehungsweise angenommenen Masterexemplar
stehen.

## Lokale Grammatikbruch- und Druckstellen

### `ET?`

Alle 19 Vorkommen sind nichtterminal. 15/19 liegen innerhalb eines Feldes,
17/19 innerhalb eines Satzes und 17/19 innerhalb einer physischen Zeile. Vier
stehen am Feldanfang (`E121`, `E295`, `E343`, `E370`); davon beginnen zwei auch
einen Satz (`E121`, `E295`) und zwei eine physische Zeile (`E343`, `E370`).
Keines dieser vier Vorkommen macht `ET?` unmöglich, aber sie verhindern die
engere Behauptung „immer medialer Konnektor“.

Die wiederholten Linkformen in `F004` und `F022` bleiben die beste positive
Lesestütze. Der formal sparsamere Rivale ist jedoch
`FORMAL_INTRA_FIELD_LINK_OR_SLOT_FILLER`. `ET?` gewinnt gegen diesen Rivalen
nicht; es bleibt lediglich der von V77 vorgeschriebene kreative Arbeitswert.

### `PER?`

Sieben von neun Vorkommen beginnen ein Feld, sechs beginnen einen Satz, keines
schließt ein Feld. `E180` und `E219` liegen innerhalb ihres Feldes und sind die
beiden expliziten lokalen Druckstellen. Der stärkste Rival ist daher genau
`FORMAL_ENTRY_OR_RESET_MARK`, nicht ein belegter lateinischer oder deutscher
Wortwert. Auch `PER?` bleibt nur fragezeichenpflichtiger Arbeitswert.

### Formalkanäle und unbekannte Karten

Die zwei Nichtwortkarten verursachen 26 Stellen, an denen eine flüssige
Sachhandlung ausschließlich durch das Masterexemplar geliefert wird. Der
Parameterkanal steht 6/20-mal am Feldanfang, der Relationskanal 2/6-mal; beide
sind niemals terminal und werden formal am besten als innerer Link oder
Slotfüller gegengelesen.

Für alle 173 Karten steht in `V78_R3_CONFLICTS.tsv` ein eigener
Link-/Entry-/Close-Rivale. Die rein formale Verteilung lautet:

| stärkster Positionsrival | Karten |
|---|---:|
| intra-field link / slot filler | 89 |
| entry / reset mark | 46 |
| close / commit mark | 27 |
| polypositionale Mischform | 11 |

Nur 17/173 Karten kommen sowohl in Herbal als auch Biological vor. 107 sind
Bio-only und 49 Herbal-only. Diese Registerverteilung macht eine portable
Wortlesung bei den meisten Karten weder prüfbar noch nötig.

## Technisches Urteil

Die elf Recordtexte sind als Werkstattausgabe mechanisch ausführbar: ein
Schreiber kann die opaque Folge abschreiben, die zwei fraglichen kleinen Wörter
und zwei Nichtwortkanäle stets gleich behandeln, Sätze über Zeilen weiterführen
und an sichtbaren Bio-Lücken zurücksetzen. Die konkrete Sachlektüre ist dagegen
fast vollständig exemplarabhängig. Das Verfahren rekonstruiert daher eine
mögliche Benutzung eines Code- und Musterbuchs, nicht dessen verlorenen Inhalt.

`ET?` und `PER?` überstehen diese Runde ohne unmittelbare Unmöglichkeit, aber
beide werden durch einfachere formale Link-/Entry-Lesungen vollständig
konkurrenziert. V78 R3 fügt **null** neue Karten, Wörter, Laute oder Bedeutungen
hinzu.

## Artefakte und Reproduktion

- `build_v78_r3_continuous_records.py`
- `V78_R3_381_EVENT_CONTINUITY.tsv`
- `V78_R3_116_STATEMENT_CONTINUITY.tsv`
- `V78_R3_11_RECORD_CONTINUITY.tsv`
- `V78_R3_CONFLICTS.tsv`
- `V78_R3_BUILD_SUMMARY.json`
- `validate_v78_r3_continuous_records.py`
- `V78_R3_VALIDATION.json`

Die Ausgabe bleibt auf f10r, f11r, f55v, f56r, f81v, f82r und f83r innerhalb
des festen Zehnseitenpanels. Astro wird in V78 nicht als Prosa gelesen. f84 und
f84r wurden nicht geöffnet.
