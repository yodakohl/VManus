# V63 R1 — lehrbare Slotgrammatik ohne Totalparse

Status: kreative Werkstattedition; keine wissenschaftliche Entzifferung, kein Lexemnachweis.

## Entscheidung

Eine kleine Grammatik ist **als Anker- und Registerverfahren lehrbar**, aber nicht als vollständige Sprache. Sie besteht aus genau sieben Templates. Ein Template darf nur durch ein ausgewähltes exaktes Merkwort oder einen ausdrücklich freigegebenen Formaloperator beginnen. OWNER, ACTIVE, TARGET und PREVIOUS füllen danach ausschließlich anonyme Slots; ein Registerzustand darf niemals selbst ein Template erzeugen.

Von 381 Ereignissen tragen 126 einen V63-Anker: 85 exakte Merkwortvorkommen und 41 Formaloperatoren. Damit werden 64/116 Aussagen und 74/135 Felder wenigstens einmal verankert; 52 Aussagen und 61 Felder bleiben vollständig `EXEMPLAR_ONLY`. 255 Ereignisse bleiben unlizenzierter Exemplarrest. Selbst die 12 Aussagen und 14 Felder, deren sämtliche Ereignisse Anker sind, gelten ausdrücklich **nicht** als Totalparse: Referenten, Werte, Wortfolge und lokale Prosa bleiben außerhalb der Grammatik.

## Gefrorenes Inventar

| Template | Instanzen | Aussagen | Felder |
|---|---:|---:|---:|
| `PARAMETER_ASSIGNMENT` | 29 | 23 | 26 |
| `TARGET_ASSIGNMENT` | 16 | 14 | 15 |
| `RELATION_LINK` | 19 | 13 | 16 |
| `STATE_CHECK_GATE` | 11 | 10 | 11 |
| `ACTION` | 17 | 15 | 15 |
| `TERMINAL_ACTION` | 16 | 16 | 16 |
| `SELECTION_REFERENCE` | 18 | 15 | 16 |

Die vollständigen Operator-, Slot-, Fehler- und Lehrregeln stehen in `V63_R1_TEMPLATE_INVENTORY.tsv`. Die Zuordnung ist absichtlich eng:

- `MASS?` und `SET(ARG_AIIN)` → Parameterzuweisung.
- `ZIEL?` und `SET(ARG_AL)` → Zielzuweisung.
- `FRAME_O(LINK)` → Relationsverknüpfung.
- `BEREIT?`, `KLAR?` → Zustandsprüfung/Sperre.
- `ANWENDEN?`, `TEMPERIEREN?` → Handlung.
- `SPÜLEN?`, `ABLASSEN?` → terminale Handlung.
- `ANSATZ?`, `VORIGES?`, `ANTEIL?` und `MARK` → Auswahl/Verweis.

Andere SET-, LINK-, FRAME- oder Schlussformen, der bloße sichtbare Kartenkörper und der strikte Prompt `VORGABEPARAMETER?` sind in V63 keine selbständigen Anker. Insbesondere wird die Oberfläche `daiin` nicht wie die exakte Karte `MASS?` behandelt. `MARK` bleibt formales Markieren eines opaken Arguments; seine Einordnung unter Auswahl/Verweis benennt weder Referent noch Wortart.

## Ausführbare Schreib- und Leseregel

1. V61-`statement_id` statt physischer Zeile aufschlagen; eine Zeile beendet keine Aussage automatisch.
2. Ereignisse in veröffentlichter Reihenfolge lesen und ausschließlich in der exakten V60-Spalte oder in der engen Formal-Allowlist nach einem Anker suchen.
3. Ohne Anker `EXEMPLAR_ONLY` schreiben und stoppen. Register dürfen diesen Stopp nicht umgehen.
4. Bei einem Anker das zugehörige der sieben Templates öffnen. Mehrere Anker bleiben als geordnete Folge erhalten; sie werden nicht zu einem neuen Satzwert verschmolzen.
5. OWNER/ACTIVE/TARGET/PREVIOUS aus dem V62-Vorzustand einsetzen. Ein Nachzustand darf nur als markierter `POST_FALLBACK` dienen, weil V62 keine Ereignisordnung innerhalb einer Aussage beweist.
6. Fehlende Pflichtrolle als `UNRESOLVED` notieren. Ein Pflanzen-, Stoff-, Körper-, Gefäß- oder Stationswort darf nur aus dem lokalen Exemplar kommen und bleibt dort.
7. Den V62-Übergang unverändert ausführen und ins Verlaufsbuch schreiben. Kein Kartenanker erhält dadurch eine stille Objektbedeutung.
8. Formale Feldschließung lautlos ausführen. Sie ist weder Satzzeichen noch Bedeutung von `SPÜLEN?`/`ABLASSEN?`.

## Drei vollständige Rücklesetests

### H2-S001 / F003

Die Ankerfolge enthält `BEREIT? → ANSATZ? → MASS?`. Aus dem anfangs leeren Recordzustand liefert der veröffentlichte V62-Übergang OWNER=H2:O01 und ACTIVE=H2:I001. Der Lehrling schreibt daher abstrakt: `CHECK BEREIT? ON H2:I001; SELECT H2:I001 BY ANSATZ?; SET MASS? FOR H2:I001; VALUE=UNRESOLVED`. Erst danach darf er die V61-Werkstattklausel als lokale Exemplarlesung danebenstellen. Widerspruch: Die Ereignisreihenfolge der Registereinführung innerhalb der Aussage ist nicht beobachtet; ACTIVE ist hier ausdrücklich ein `POST_FALLBACK`.

### B1-S004 / F026

Vor der Aussage stehen ACTIVE=B1:I002 und PREVIOUS=B1:I001. Der formale Anker `FRAME_O(LINK)` erlaubt genau `LINK B1:I002 TO B1:I001`; er erlaubt weder die Benennung beider Posten noch eine konkrete räumliche oder medizinische Relation. Der V62-Zustand bleibt unverändert. Widerspruch: PREVIOUS hat mehrere plausible lokale Referentenklassen; die anonyme Kante ist ausführbar, die Sachrelation nicht bestimmt.

### B3-S003 / F073

Vor dem Feld stehen OWNER=B3:O01, ACTIVE=B3:I001 und TARGET=B3:T001. Der exakte Anker `ABLASSEN?` erlaubt `DO ABLASSEN? ON B3:I001; TARGET=B3:T001`; die formale Schließung wird getrennt und lautlos ausgeführt. Widerspruch: Alle acht `ABLASSEN?`- und alle acht `SPÜLEN?`-Vorkommen fallen mit zwei Schlussfamilien zusammen. `END_A/END_B` bleibt daher ein gleichwertiger technischer Rivale.

`V63_R1_EXECUTABLE_EXAMPLES.tsv` führt für alle elf exakten und alle vier formalen Ankerklassen je ein vollständiges Bindungs-, Ausführungs- und Updatebeispiel mit strikt abgetrennter lokaler Exemplarlesung.

## Abdeckung nach Record

| Record | verankerte Aussagen | verankerte Felder |
|---|---:|---:|
| B1 | 12/21 | 13/24 |
| B2 | 8/22 | 10/26 |
| B3 | 20/34 | 21/38 |
| B4 | 8/16 | 11/20 |
| B5 | 1/3 | 2/5 |
| B6 | 1/1 | 2/2 |
| H1 | 2/2 | 2/2 |
| H2 | 3/3 | 3/3 |
| H3 | 3/4 | 3/4 |
| H4 | 3/4 | 3/4 |
| H5 | 3/6 | 4/7 |

Die 116- und 135-Zeilen-Karten veröffentlichen jeden Nullfall als `EXEMPLAR_ONLY`; es gibt keine erzwungene Restkategorie und keine semantische Ableitung aus sichtbaren Komponenten.

## Stärkste Widersprüche

1. **Abdeckung:** Mehr als die Hälfte der Ereignisse und 52/116 Aussagen besitzen keinen lizenzierten Anker. Die Grammatik ist ein Skelett, keine vollständige Quellsyntax.
2. **Registerzirkularität:** Viele V62-IDs wurden in der kreativen Edition mithilfe lokaler Exemplare eingeführt. Darum dürfen sie Slots füllen, aber nie ein Template oder einen Kartenwert begründen.
3. **Relationslücke:** Zehn von 19 `FRAME_O(LINK)`-Ankern haben im Aussage-Vorzustand weder PREVIOUS noch TARGET als zweiten Endpunkt. Ein späterer Nachzustand beweist die Ereignisordnung nicht.
4. **Ziellücke:** Zwei von 16 Zielzuweisungsankern enden mit TARGET=UNSET; alle anderen Ziele bleiben anonyme, teils überschriebene IDs.
5. **Terminalkonfundierung:** Die 16 terminalen Merkwörter sind vollständig mit Schlussformen konfundiert. Eine reine Renderer-/Formularlesung bleibt stark.
6. **Quelltextlücke:** Kein Template liefert Zahl, Einheit, Instrument, Material, Körperteil, Station oder Ergebnis. Diese Angaben stammen weiterhin nur aus den gekennzeichneten lokalen Exemplaren.

## Typische Lehrlingsfehler und Reparaturen

- **Fehler:** gleich aussehende Oberflächen oder Teilformen übernehmen den Merkwert. **Reparatur:** nur die exakte Joint-Tuple-Zeile im ausgewählten Ledger nachschlagen.
- **Fehler:** ein getragenes ACTIVE erzeugt automatisch eine Handlung. **Reparatur:** ohne exakten/formalen Anker `EXEMPLAR_ONLY`.
- **Fehler:** H2:I001 als Pflanze, Flüssigkeit oder Person aussprechen. **Reparatur:** ID anonym zurücklesen; Sachwort nur in der getrennten Exemplarspalte.
- **Fehler:** `MASS?` mit einer lokal geratenen Menge füllen. **Reparatur:** `VALUE=UNRESOLVED` belassen.
- **Fehler:** `MARK` als Zustand oder bestimmtes Pronomen lesen. **Reparatur:** nur das opake Formalargument markieren.
- **Fehler:** `SPÜLEN?` oder `ABLASSEN?` aus jedem Feldschluss ableiten. **Reparatur:** terminales Template nur bei der exakten Karte; Schlussoperation separat.
- **Fehler:** den restlichen deutschen Satz aus einem Anker generieren. **Reparatur:** unlizenzierte Ereignisse und lokale Ergänzungen sichtbar als Exemplarrest führen.

## Schluss

V63 verbessert V62 als **unterrichtbares Kontrollskelett**: sieben Templates, ein enger Triggercheck, vier anonyme Merkregister und ein verpflichtender `UNRESOLVED`-Ausgang. Es verbessert V59 nicht zu einer Übersetzung. Der stärkste Gesamtrivale bleibt ein illustriertes Formular-/Musterbuch, in dem SET/LINK/MARK und die beiden Schlussfamilien Produktionszeichen sind und die deutschen Prozesssätze nur moderne Exemplare.

Validierung: siehe `V63_R1_VALIDATION.json`; die reproduzierbare Erzeugung steht in `V63_R1_BUILD_SLOT_GRAMMAR.py`, der unabhängige Prüfer in `V63_R1_VALIDATE_SLOT_GRAMMAR.py`.
