# V60 R3: technischer Drucktest der elf exakten Ganzkarten

## Ergebnis

Der streng ID-gebundene Drucktest ist **ausführbar, aber explorativ**. Allen elf Zielkarten kann ein kurzer technischer Default zugewiesen werden, ohne eine sichtbare Kartenschreibung zu zerlegen. Die 85 kanonischen Vorkommen sind einzeln auditiert. Der Test rechtfertigt keine Entzifferung: Besonders `OLOR` und `OTCHEY` bleiben wegen jeweils nur zwei Belegen schwach; `OKE` und `LCHE` sind in sämtlichen 16 Belegen mit formalem `CLOSE` konfundiert.

Die revidierte strikte Edition enthält genau 173 Kartentypen und 381 Prosaereignisse. Nur die elf vorab festgelegten exakten Joint-Tuple-IDs erhalten einen technischen Default (85 Ereignisse). Die anderen 162 Kartentypen beziehungsweise 296 Ereignisse bleiben `UNKNOWN_EXEMPLAR`.

## Bindungsvertrag

1. Schlüssel ist ausschließlich die vollständige, opake `joint_tuple_id`.
2. Oberflächenformen dienen nur der Anzeige. Weder `PAGE_HOST`, Stringähnlichkeit noch Teilkarten oder Komponenten vererben einen Wert.
3. Der technische Default ist ein knapper Arbeitsbefehl, Parameter, Zustand oder Relationsslot. Lokale iatromedizinische und nichtmedizinische Expansionen bleiben getrennte Record-Füller.
4. `formal_formula_opaque`, `FORMAL_VALUE`, `strict_control_prompt` und `terminal_status` bleiben unverändert. Ein physischer Zeilenanfang ist kein Satzanfang.
5. Nachbarn, Feldstellung und `CLOSE` dürfen einen Kandidaten belasten, erzeugen aber keine Bedeutung.

## Entscheidungen

| Karte | n | Technischer Default | Zwei Rivalen | Quellklasse / Zustandswirkung | Stärkster Widerspruch | Konfidenz |
|---|---:|---|---|---|---|---:|
| AIIN | 20 | `SOLLWERT?` | `MASS?`, `DAUER?` | Parameterreferenz; setze den aktiven Slot auf einen vorgeschriebenen Referenzwert | Keine Skala oder Einheit; fünf Feldenden lassen den regierten Slot still | 0,74 |
| OKY | 10 | `AUSFÜHREN?` | `VERWENDEN?`, `BUCHEN?` | Aktion; führe den aktiven Posten aus und schalte den Arbeitszustand weiter | Ein Ein-Karten-Feld muss Aktion und Objekt erben | 0,58 |
| CTHY | 7 | `FREIGABE?` | `BEREIT?`, `HALTEN?` | Zustands-Gate; markiere bereit und erlaube den Folgeschritt | Sechs von sieben Belegen sind medial und könnten bloßer Verbinder sein | 0,61 |
| OR | 7 | `ANSATZ?` | `BEREITUNG?`, `CHARGE?` | aktive Charge; setze den vorbereiteten Arbeitsansatz | Zwei identische direkt benachbarte Belege belasten eine echte Chargenlesung | 0,60 |
| AL | 10 | `ZIEL?` | `AN?`, `STATION?` | Zielrelation; setze lokales oder bildgegebenes Routenziel | Ein Ein-Karten-Feld und mehrere Initialbelege besitzen keinen offenen Routenoperanden | 0,50 |
| EY | 4 | `KLARLAUF?` | `KLAR?`, `FILTERN?` | Zustandsschwelle; markiere erreichten Klarlauf | Positionswechsel lässt Zustand gegen lokale Aktion unentschieden | 0,49 |
| OLOR | 2 | `VORLAUF?` | `ZUVOR?`, `RÜCKLAUF?` | Vorchargenrelation; nimm vorherigen Lauf als Linkquelle | Beide Belege berühren eine exakte LINK-Karte; n=2 | 0,48 |
| OTCHEY | 2 | `POSTEN?` | `TEIL?`, `ABSCHNITT?` | Selektor; setze markierten Posten oder Abschnitt aktiv | Verschiedene sichtbare Owner und mögliche vollständige Erklärung durch den formalen Rahmen; n=2 | 0,40 |
| OKEEY | 7 | `TEMPERIEREN?` | `WARMHALTEN?`, `NACHFÜLLEN?` | Temperaturkontrolle; setze Arbeitsband | Keine Skala oder unabhängige Wärmereferenz; nur Bio-Belege | 0,69 |
| OKE | 8 | `SPÜLEN?` | `REINIGEN?`, `UMWÄLZEN?` | Spülaktion; markiere gespült, dann formaler Commit | Alle acht Belege sind terminal; Semantik ist nicht von `CLOSE` isolierbar | 0,46 |
| LCHE | 8 | `ABFÜHREN?` | `ABLASSEN?`, `AUSGEBEN?` | Abflussaktion; route aktive Charge zum lokalen Ausgang, dann Commit | Alle acht Belege sind terminal, fünf davon Ein-Karten-Felder | 0,51 |

Damit werden gegenüber V59 R1 `OKE = SPÜLEN?` beibehalten und zehn Werte technisch präzisiert oder verbreitert. Die wichtigsten funktionalen Revisionen sind `MASS? → SOLLWERT?`, `VERWENDEN? → AUSFÜHREN?`, `BEREIT? → FREIGABE?`, `AN? → ZIEL?` und `WARM? → TEMPERIEREN?`.

## Vorkommensdruck

Die Auditklassifikation ergibt 57/85 Vorkommen, die mit Default plus lokalem Füller vereinbar sind. Weitere 16/85 sind ausdrücklich `CLOSE_CONFOUNDED_NOT_DISPROVED`; 4/85 lassen Zustand gegen Aktion offen; je 2/85 tragen Druck durch identische Nachbarschaft, LINK-Nachbarschaft oder formalen Rahmen; je ein Ein-Karten-Feld belastet den geerbten Aktions- beziehungsweise Zielslot. „Vereinbar“ ist dabei kein positiver Bedeutungsbeweis, sondern nur das Ausbleiben eines positions- oder nachbarschaftsbedingten Widerspruchs.

`AIIN` ist als formaler Parameterwert plausibler als als konkrete Maßeinheit: Der Wert bleibt bei FIRST/MIDDLE/LAST-Wechsel stabil, doch seine Dimension muss lokal geliefert werden. Analog ist `AL` besser als formaler Zielslot denn als inhaltlich benannte Station. `OKE` und `LCHE` dürfen dagegen nicht als unabhängige semantische Erfolge gewertet werden, solange kein nichtterminaler Beleg vorliegt.

## Artefakte und Reproduktion

- `V60_R3_11_CARD_TECHNICAL_DECISIONS.tsv`: elf Gewinner, je zwei Rivalen, Quellklasse, Zustandswirkung, Belegstatistik und Widerspruch.
- `V60_R3_85_OCCURRENCE_AUDIT.tsv`: jedes der 85 Vorkommen mit Stellung, Nachbarn, `CLOSE`, lokalen Expansionen und Belastungscode.
- `V60_R3_REVISED_STRICT_173_CARD_DICTIONARY.tsv`: vollständige revidierte Kartentyp-Edition.
- `V60_R3_REVISED_STRICT_381_EVENT_INTERLINEAR.tsv`: vollständige revidierte Ereignis-Edition.
- `V60_R3_VALIDATION.json`: Counts, Invarianten und SHA-256-Lineage.

Aus dem V60-Verzeichnis reproduzieren:

```bash
python3 V60_R3_BUILD_TECHNICAL_MNEMONIC_REVISION.py
python3 V60_R3_VALIDATE_TECHNICAL_MNEMONIC_REVISION.py
```

Der Validator besteht alle Gates: `11/85/173/381`, exakte ID-Bindung, verbotene Komponentenvererbung, unveränderte formale Schicht, vollständige Auditdeckung, genau zwei konkrete Rivalen pro Zielkarte und `162/296 UNKNOWN_EXEMPLAR` außerhalb des Zielsets.
