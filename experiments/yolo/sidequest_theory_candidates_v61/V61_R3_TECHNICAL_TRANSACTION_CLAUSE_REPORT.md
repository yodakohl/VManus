# V61 R3: technische Transaction-/Clause-Map der elf Prosa-Records

## Ergebnis

Die kleinste ausführbare Segmentierung erzeugt aus den 135 kanonischen Feldern **98 technische Source-Statement-Hypothesen**. Davon enden 90 an einem vorhandenen formalen Commit; acht bleiben am jeweiligen Recordende bewusst offen. 31 Statements umfassen mehrere physische Loci. Die 46 Locusgrenzen innerhalb eines Records teilen sich in 37 Fortsetzungen und 9 Resets.

Das ist keine Identifikation von 98 natürlichsprachlichen Sätzen oder Plaintext-Klauseln. „Statement“ bezeichnet hier allein eine ausführbare Transaktion der Sidequest-Schicht: vom Start eines aktiven Arbeitszustands bis zum vorhandenen `TERMINAL`-Commit oder bis zu einem ausdrücklich ungelösten Recordende.

## Deterministische Transaktionsregel

```text
IDLE
  -> lade sichtbaren Record-/Bild-Owner und lokale Exemplarargumente
  -> ACTIVE(statement)

ACTIVE + Feld(OPEN)
  -> führe lokale Feldexpansion aus
  -> halte Ergebnis und Slots aktiv
  -> weise das nächste Feld demselben Statement zu,
     auch wenn ein physischer Locuswechsel dazwischenliegt

ACTIVE + Feld(TERMINAL)
  -> führe lokale Feldexpansion aus
  -> COMMIT(statement)
  -> das nächste Feld beginnt eine neue Transaktion

ACTIVE + RECORD_END
  -> OPEN_DEFERRED_AT_RECORD_END
  -> kein stiller Commit und kein Carry in den nächsten Record
```

Die elf ausgewählten V60-Ganzkarten werden nur über ihre exakte opake `joint_tuple_id` als Slots eingetragen. `MASS?` ist ein Parameterslot; `ANWENDEN?`, `SPÜLEN?`, `TEMPERIEREN?`, `ABLASSEN?` sind Operationsslots; `BEREIT?`, `KLAR?` Zustandslots; `VORIGES?`, `ZIEL?` Relationsslots; `ANSATZ?`, `ANTEIL?` Eingabeslots. Das ist nur eine Sortierung der bereits ausgewählten Merkwörter, keine neue Kartenbedeutung. Unbekannte Karten bleiben opak. Weder Oberfläche, `PAGE_HOST`, Stringteil noch Komponente vererbt einen Wert.

Die vollständigen ausführbaren Lesungen stammen aus den kanonischen lokalen Feldexpansionen. Sie werden als Record-Füller geladen und nicht aus Kartenwörtern zusammengesetzt. `CLOSE` wird ausgeführt, aber nicht gesprochen.

## Vollständige Abdeckung

| Record | Ereignisse | Felder | Statements | committed | offen am Ende | lociübergreifende Statements | Locusgrenzen: weiter/reset |
|---|---:|---:|---:|---:|---:|---:|---:|
| H1 | 14 | 2 | 1 | 0 | 1 | 1 | 1 / 0 |
| H2 | 24 | 3 | 1 | 0 | 1 | 1 | 2 / 0 |
| H3 | 17 | 4 | 2 | 1 | 1 | 1 | 2 / 0 |
| H4 | 18 | 4 | 4 | 3 | 1 | 0 | 0 / 1 |
| H5 | 27 | 7 | 2 | 1 | 1 | 2 | 5 / 1 |
| B1 | 66 | 24 | 18 | 17 | 1 | 6 | 6 / 0 |
| B2 | 62 | 26 | 19 | 19 | 0 | 7 | 7 / 0 |
| B3 | 86 | 38 | 31 | 31 | 0 | 7 | 7 / 2 |
| B4 | 47 | 20 | 16 | 16 | 0 | 4 | 4 / 5 |
| B5 | 11 | 5 | 3 | 2 | 1 | 1 | 2 / 0 |
| B6 | 9 | 2 | 1 | 0 | 1 | 1 | 1 / 0 |
| **Summe** | **381** | **135** | **98** | **90** | **8** | **31** | **37 / 9** |

Die Statementlängen sind klein: 67 bestehen aus einem Feld, 26 aus zwei, vier aus drei und eines aus vier Feldern. Mehrfeld-Statements sind in diesem Datensatz zugleich lociübergreifend. Das typische Bio-Muster ist daher nicht „eine Zeile = ein Satz“, sondern: mehrere committed Parallelzellen, danach eine offene Schlusszelle, deren Transaktion am Kopf des nächsten Locus abgeschlossen wird.

## Drucktest f82r.3 → f82r.4

Die hervorgehobene Grenze gehört zu `S033 = F050|F051` und wird als Fortsetzung klassifiziert:

```text
f82r.3 / F050 OPEN:
  zweiten Lauf fortführen -> durch Tuch -> durch verbundene Läufe
  -> nächsten abgemessenen Posten beginnen

ACTIVE_STATE_CARRY

f82r.4 / F051 TERMINAL:
  nächsten abgemessenen Posten beginnen -> gleiche Einstellung
  -> breites Gefäß -> abziehen -> COMMIT
```

Der gleiche exakte formale `SET(<ARG_AIIN>)`-Tuple steht als letztes Setup von F050 und erstes Setup von F051. In der gewählten Lesung ist das eine resumptive Wiederaufnahme des offenen Slots über den physischen Locuswechsel. Der stärkste Rival ist hier besonders konkret: Die Wiederholung könnte ein neuer Zeilenheader sein; dann müsste F050 jedoch einen nicht geschriebenen Commit erhalten und F051 eine neue Transaktion beginnen. Die Map behält deshalb die Fortsetzung, markiert aber den Wiederholungsbefund statt ihn als Bedeutungsbeweis zu zählen. Keine der elf semantischen Mnemonikkarten ist für diese Entscheidung nötig; der Fall ist formal.

## Drucktest f83r

f83r enthält 21 innere Locusgrenzen: 14 Fortsetzungen und 7 Resets. Gerade dieses Mischbild verhindert eine pauschale Zeilenregel.

- B3 setzt an sieben Grenzen fort. Nach `f83r.15→16` und `f83r.22→24` resetet es, weil F095 beziehungsweise F107 bereits terminal commitet.
- B4 setzt an `25→26`, `35→37`, `39→41` und `41→44` fort. Es resetet an `26→27`, `27→28`, `28→35`, `37→38` und `38→39`.
- B5 trägt sein letztes Statement über `47→48→49`; B6 trägt sein einziges Statement über `52→54`. Beide enden ohne geschriebenen Commit und bleiben daher offen.

Die vielfachen terminalen Einzelzellen in B3/B4 werden als parallele Kleintransaktionen behandelt. Der stärkste Gegenvorschlag ist eine große fortlaufende Prozessprosa, in der `CLOSE` nur ein internes Zwischenhäkchen wäre. Das spart Statementstarts, bezahlt aber sieben explizite f83r-Commitzeichen, die es von Grenzen zu Binnenmarken umdeuten muss.

## Rivalen und Scheitern des Modells

Der stärkste globale Rival ist `PHYSICAL_LOCUS_RESET`: Jede der 37 offenen Locusgrenzen würde als Satzende gelesen. Dafür braucht er 37 stille Commits und zerreißt unter anderem H2, B2 und die langen offenen B5/B6-Ketten. Der gegenteilige Rival `MACROPROCESS_MERGE` verbindet auch die neun committed Grenzen; dafür muss er vorhandene `CLOSE`-Ereignisse zu bloßen Checkpoints herabstufen.

Die closure-gesteuerte Map gewinnt als ausführbare Registerregel, weil sie weder stille Zwischen-Commits noch ignorierte formale Commits benötigt. Sie scheitert als linguistische Entzifferung: Die lokale Prosa ist exemplarisch, acht Records enden mit offenem Zustand, und die Grenzen könnten historisch auch Rubrik-, Kopier- oder Layoutfunktionen tragen. Insbesondere beweist eine technisch konsistente Transaktion keine Syntax und keine medizinische Bedeutung.

## Artefakte

- `V61_R3_PHYSICAL_LOCUS_BOUNDARIES.tsv`: sämtliche 46 inneren Locusgrenzen, Zustandstransition und stärkster Segmentierungsrivale.
- `V61_R3_98_TRANSACTION_STATEMENTS.tsv`: Inputs, Parameter-/Operations-/Zustands-/Relationsslots, Output, Carry, Vollablesung und Rival für jedes Statement.
- `V61_R3_135_FIELD_ASSIGNMENT.tsv`: eindeutige Zuordnung jedes Feldes mit Vor-/Nachzustand.
- `V61_R3_BUILD_TRANSACTION_CLAUSE_MAP.py`: deterministischer Builder.
- `V61_R3_VALIDATE_TRANSACTION_CLAUSE_MAP.py` und `V61_R3_VALIDATION.json`: reproduzierbare Counts, Invarianten, Scope- und Hashprüfung.

Reproduktion im V61-Verzeichnis:

```bash
python3 V61_R3_BUILD_TRANSACTION_CLAUSE_MAP.py
python3 V61_R3_VALIDATE_TRANSACTION_CLAUSE_MAP.py
```
