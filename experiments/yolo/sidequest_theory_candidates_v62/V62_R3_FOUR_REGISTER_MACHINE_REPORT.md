# V62 R3: deterministische Vierregistermaschine

## Entscheidung

Die vollständige ausgewählte V61-Lesung mit 116 Source-Statements lässt sich als kleine Registermaschine ausführen, wenn vier voneinander getrennte recordlokale Werte geführt werden:

```text
OWNER                    <RECORD>:O01
ACTIVE_ITEM/PREPARATION  <RECORD>:I001...
TARGET/STATION           <RECORD>:T001...
PREVIOUS_ITEM            Zeiger auf <RECORD>:Ixxx
```

Unter dem veröffentlichten Rekonstruktionskriterium reicht kein kleineres persistentes Registerset für alle Statements. Der Befund ist trotzdem keine Entzifferung: Die IDs sind nur anonyme Buchhaltungsmarken; konkrete Pflanzen, Flüssigkeiten, Körperstellen und Gefäße stammen aus den bereits ausgewählten V61-Recordexpandierungen.

## Ausführbare Regel

| Beobachtung | OWNER | ACTIVE_ITEM/PREPARATION | TARGET/STATION | PREVIOUS_ITEM |
|---|---|---|---|---|
| `RECORD_START` | `INTRODUCE O01` | `INTRODUCE I001` | `RESET` | `RESET` |
| `WITHIN_LOCUS_FIELD_BOUNDARY` | `CARRY` | `CARRY` | `CARRY` | `CARRY` |
| `RESUME_ACTIVE_ITEM` | `CARRY` | `RESUME` | `CARRY` | `CARRY` |
| `NEXT_PARALLEL_CELL` oder `START_NEW_CLAUSE` | `CARRY` | altes Active nach Previous, dann `INTRODUCE` neues Item | `RESET` | `INTRODUCE` verdrängtes Active |
| `UNRESOLVED` | `CARRY` | `CARRY` | `CARRY` | `CARRY`; Ambiguitätsflag behalten |
| Recordende | kein Carry über die Recordgrenze | kein Carry über die Recordgrenze | kein Carry über die Recordgrenze | kein Carry über die Recordgrenze |

V60 darf diese Struktur nur über die elf bereits ausgewählten Ganzkarten anstoßen:

- `ANSATZ?` bestätigt oder resumiert die aktive Vorbereitung; `ANTEIL?` führt einen abgeleiteten aktiven Posten ein.
- `VORIGES?` resumiert den depth-one `PREVIOUS_ITEM`-Zeiger.
- `ZIEL?` führt den anonymen Zielslot ein oder resumiert ihn.
- `MASS?`, `ANWENDEN?`, `BEREIT?`, `KLAR?`, `TEMPERIEREN?`, `SPÜLEN?` und `ABLASSEN?` werden als bereits lizenzierte Parameter-, Aktions- oder Zustands-Trigger protokolliert; sie erhalten hier keine neue Bedeutung.

Lokale V61-Phrasen dürfen einen anonymen Ziel- oder Vorwert füllen. Diese Füller sind im Übergangsledger ausdrücklich als `LOCAL_*` markiert und vererben sich niemals auf eine Karte. Jede Transition veröffentlicht Pre-State, beobachtete Trigger, fehlende Slots, vier Operationen, vollständigen Operationspfad, Post-State und Rückwärtsstatus.

## Vollständigkeit und stille Slots

Die 116 Übergänge decken alle 135 Felder und 381 Prosaereignisse der ausgewählten Statement-Schicht. Die fehlenden Rollen auf Statementebene sind häufig:

| Register | in der Statementform nicht explizit | benötigt als persistenter stiller Wert |
|---|---:|---:|
| OWNER | 105 | 105 |
| ACTIVE_ITEM/PREPARATION | 108 | 83 |
| TARGET/STATION | 24 | 9 |
| PREVIOUS_ITEM | 19 | 19 |

Die Differenz zwischen „nicht explizit“ und „persistent benötigt“ ist wichtig. Ein lokaler V61-Füller kann beispielsweise ein neues Gefäß im selben Statement sichtbar einführen; dafür fehlt zwar eine Kartenmarkierung, aber kein Carry aus dem Vorzustand.

## Bezahlter Vergleich mit weniger Registern

Für 0, 1, 2 und zusätzlich 3 Register wurden sämtliche Teilmengen der vier Register exhaustiv geprüft. Gewinner maximieren zuerst die Zahl vollständig generierbarer Statements und minimieren danach die Zahl fehlender stiller Slotinstanzen.

| Registerzahl | stärkster Rivale | vollständig | scheitert | Abdeckung |
|---:|---|---:|---:|---:|
| 0 | kein persistenter Zustand | 9 | 107 | 7,76 % |
| 1 | OWNER | 27 | 89 | 23,28 % |
| 2 | OWNER + ACTIVE_ITEM/PREPARATION | 88 | 28 | 75,86 % |
| 3 | OWNER + ACTIVE_ITEM/PREPARATION + PREVIOUS_ITEM | 107 | 9 | 92,24 % |
| 4 | vollständige Maschine | 116 | 0 | 100 % |

Der Zweiregisterrivale ist der stärkste wirklich kleine Gegenentwurf: sichtbaren Recordbesitzer halten und nur den aktuellen Posten fortschreiben. Er verliert genau dort, wo eine frühere Charge oder eine getrennte Station wiedergewonnen werden muss. Der Dreiregisterrivale fügt den Vorposten hinzu, scheitert aber an neun target-sensitiven Statements ohne hinreichenden aktuellen Zieltrigger. Man könnte diese neun Ziele jedes Mal neu aus dem Bild lesen; dann ist das Bild jedoch ein externer fünfter Speicher und kein registerloser Ersatz.

## Konkrete Buchungen

`H2-S002` startet mit `O=H2:O01, A=H2:I001, T=UNSET, P=UNSET`. Die exakten Trigger `ANSATZ? | VORIGES? | MASS?` verlangen einen Vorwert, identifizieren ihn aber nicht. Die Maschine führt daher anonym `H2:I002` als vorherigen Posten ein, resumiert ihn nach Active und legt `H2:I001` in Previous zurück. Das ist ausführbar, aber aus dem Post-State allein nicht semantisch eindeutig.

`H5-S001` ist ein sauberer positiver Fall: Recordstart führt `H5:O01` und `H5:I001` ein; `ZIEL?` plus lokaler markierter Ziel-Füller setzt `H5:T001`. Der Übergang ist auch aus dem Post-State rückwärts eindeutig, solange die anonymen IDs und der Operationstyp bekannt sind.

`B1-S002` zeigt die Kapazitätsgrenze. Das Statement enthält `ZIEL?`, `VORIGES?`, zwei `MASS?` sowie mehrere lokale Stationen. Vier Register führen die Schritte aus, aber ein einziger Target-Slot behält nur die letzte Station und der Previous-Slot nur einen der zwei Anteile. Der Operationspfad bleibt vollständig; der nackte Post-State ist verlustbehaftet.

`B2-S011` übernimmt die eine ausgewählte `UNRESOLVED`-Grenze. Die Maschine entscheidet deterministisch für `CARRY` aller Register, behauptet aber nicht, dass Reset oder Resume widerlegt seien.

## Rückwärtslesung und Fehleraudit

Mit dem vollständigen Transition-Log sind 116/116 Übergänge rückwärts nachvollziehbar, weil Pre-State und jede Operation erhalten bleiben. Aus dem Post-State allein sind nur 47/116 rückwärts eindeutig; 69/116 haben mindestens einen überschriebenen oder nicht eindeutig identifizierten Wert.

Der Audit enthält 122 Fehler-/Druckzeilen. Davon sind 73 protokollierbare Informationsverluste, die ein Transition-Log auffängt: 41 Zielüberschreibungen, 16 Previous-Überschreibungen und 16 Zielresets. 49 Zeilen markieren irreduzible kreative Ambiguitäten in 33 Statements:

- 19 Fälle unterscheiden Vorbereitung, Posten, Lauf, Rest oder Einstellung als Vorreferent nicht sicher.
- 9 Statements nennen mehrere Ziele oder Stationen, obwohl nur ein Target-Slot vorhanden ist.
- 8 Records enden mit einem offenen Zustand statt einem geschriebenen Commit.
- 6 Zwei-Anteil-Konstruktionen legen die ACTIVE/PREVIOUS-Reihenfolge nicht fest.
- 4 Vorreferenzen benötigen eine anonym eingeführte, nicht eindeutig beobachtete Identität.
- je ein Fall betrifft einen vollständig inferierten Zielslot, einen wiederholten Active-Trigger und die ungelöste V61-Grenze.

Die Maschine ist somit **lehrbar und ausführbar als Registerprotokoll**, aber nicht selbstgenügsam als Übersetzung. Sie benötigt lokale Exemplarfüllung, und vier einzelne Register reichen nicht aus, um Mehrzielsequenzen oder tiefe Referenzketten verlustfrei im bloßen Endzustand zu speichern.

## Artefakte und Reproduktion

- `V62_R3_116_STATE_TRANSITIONS.tsv`: vollständige Zustandsmaschine über alle Statements.
- `V62_R3_REGISTER_INVENTORY.tsv`: vier Register, Regeln, Operationszählungen und Notwendigkeitszeugen.
- `V62_R3_IRREDUCIBLE_ERROR_AUDIT.tsv`: vollständiger Fehler-, Verlust- und Ambiguitätsaudit.
- `V62_R3_REDUCED_REGISTER_MODELS.tsv`: exhaustive Gewinner für 0–4 Register.
- `V62_R3_BUILD_FOUR_REGISTER_MACHINE.py`: deterministischer Builder.
- `V62_R3_VALIDATE_FOUR_REGISTER_MACHINE.py` und `V62_R3_VALIDATION.json`: Counts, Zustandsketten-, Scope-, Modell- und Hashprüfung.

```bash
python3 V62_R3_BUILD_FOUR_REGISTER_MACHINE.py
python3 V62_R3_VALIDATE_FOUR_REGISTER_MACHINE.py
```
