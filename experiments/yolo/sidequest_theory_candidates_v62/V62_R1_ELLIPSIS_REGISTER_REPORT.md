# V62 R1 — ausführbare Ellipsis- und Registerspur

Status: vollständige kreative Werkstattspur für die 116 ausgewählten
Quellaussagen, keine Entzifferung und keine neue Kartenbedeutung.

## Endentscheidung

Vier getrennte stille Register genügen, um die V61-Aussagen ohne wiederholte
deutsche Subjekte und Objekte ausführbar zu halten:

```text
PICTURE_OWNER                OWNER_H1
ACTIVE_PREPARATION_OR_ITEM   ITEM_H1_001
TARGET_OR_STATION            TARGET_H1_001
PREVIOUS_ITEM_REFERENCE      ITEM_H1_000
```

Die Beispiele zeigen nur das ID-Schema. Tatsächliche Werte sind ausschließlich
recordlokale anonyme IDs oder `UNSET`; ungelöste Werte heißen etwa
`UNRESOLVED_ITEM_B2_002`. Kein ID enthält Pflanze, Flüssigkeit, Körper,
Apparat, Gefäß oder irgendeinen Kartenstring.

Das ausgewählte Mnemonic kann anzeigen, dass ein Slot gebraucht wird.
`ZIEL?` liefert aber kein Ziel, `VORIGES?` keinen Antezedenten und `ANSATZ?`
keinen Stoff. Der anonyme Wert kommt nur aus dem Recordzustand und dem bereits
publizierten Exemplar; fehlt beides, bleibt er `UNRESOLVED_*`.

## Gesamtbilanz

Die Spur prüft 116 Statements × 4 Register = 464 mögliche Rollenslots. 369
sind für die konkrete Werkstattklausel erforderlich, 95 nicht erforderlich:

| Register | erforderlich | explizit | geerbt | ungelöst | nicht erforderlich |
|---|---:|---:|---:|---:|---:|
| `PICTURE_OWNER` | 116 | 11 | 105 | 0 | 0 |
| `ACTIVE_PREPARATION_OR_ITEM` | 116 | 78 | 27 | 11 | 0 |
| `TARGET_OR_STATION` | 92 | 62 | 16 | 14 | 24 |
| `PREVIOUS_ITEM_REFERENCE` | 45 | 37 | 4 | 4 | 71 |
| **gesamt** | **369** | **188** | **152** | **29** | **95** |

„Explizit“ heißt: Die ausgewählte kreative Klausel fordert den Slot offen an.
Es heißt nicht, dass das Manuskript den anonymen Referenten entschlüsselt.
„Geerbt“ heißt: Die Klausel benötigt die Rolle, nennt sie aber nicht erneut;
der Eingabestatus liefert sie. „Ungelöst“ heißt: Die Rolle wird benötigt, doch
es gibt am Eintritt weder einen belastbaren Registerwert noch einen konkreten
Exemplarreferenten.

Die Evidenz der 369 erforderlichen Slots bleibt getrennt:

- 85 `SELECTED_MNEMONIC+EXEMPLAR_ONLY`;
- 266 `EXEMPLAR_ONLY`;
- 8 `BOUNDARY`;
- 10 `BOUNDARY+EXEMPLAR_ONLY`.

Diese Zählung ist keine 1:1-Abbildung der 85 Kartenereignisse: Mehrere Karten
können denselben Statementslot stützen, und ein Handlungsmnemonic kann zugleich
aktiven Gegenstand und Zielbedarf anzeigen. Es liefert dennoch niemals den ID.

## Exekutiver Algorithmus

### Recordinitialisierung

Vor Statement 1 bindet der Meister genau einen sichtbaren Besitzer:

```text
PICTURE_OWNER              := OWNER_<RECORD>
ACTIVE_PREPARATION_OR_ITEM := UNSET
TARGET_OR_STATION          := UNSET
PREVIOUS_ITEM_REFERENCE    := UNSET
```

Damit wird der Owner elfmal eingeführt und danach 105-mal getragen. Er darf
weder zwischen Records geteilt noch aus einem Kartenwert erzeugt werden.

### Statementschritt

Für jedes Statement wird in dieser Reihenfolge gearbeitet:

1. Den vollständigen Eingabestatus aus der vorherigen Tracezeile kopieren.
2. `required_roles` aus der ausgewählten Klausel bestimmen. Die deutschen
   Cuewörter gehören nur zur Exemplarspur.
3. Bei `RESUME_ACTIVE_ITEM` den aktiven ID unverändert wiederaufnehmen.
4. Bei `START_NEW_CLAUSE` oder `NEXT_PARALLEL_CELL` einen neuen `ITEM_*` nur
   dann setzen, wenn das Exemplar einen neuen Gegenstand offen einführt;
   andernfalls `UNRESOLVED_ITEM_*` setzen.
5. Bei offen genanntem Ziel einen neuen konservativen `TARGET_*` setzen. Ohne
   genanntes Ziel einen vorhandenen Ziel-ID tragen oder einen
   `UNRESOLVED_TARGET_*` erzeugen. Die konservative Neunummerierung behauptet
   keine Gleichheit zweier Becken oder Körperstellen.
6. Wenn ACTIVE resettiert wird, den alten ACTIVE-ID still als PREVIOUS
   archivieren. Bei `VORIGES?` oder einer lokalen Rückverweisform zuerst dieses
   Register, dann den Eingangs-ACTIVE und zuletzt einen bereits im selben
   Statement eingeführten ACTIVE prüfen.
7. Für jeden benötigten Slot `EXPLICIT`, `INHERITED` oder `UNRESOLVED`
   eintragen; für unbenutzte Slots `NOT_REQUIRED`.
8. Alle vier Ausgabewerte als `exact_next_register_state` festschreiben. Diese
   vier Werte sind die einzige zulässige Eingabe des nächsten Statements.

### Rücklesen

Der Korrektor nimmt `exact_next_register_state`, geht eine Zeile zurück und
prüft für jedes Register `input → operation → next`. Danach prüft er die
Carry-Kante, die V61-Grenzklasse, das unveränderte Kurzskelett und zuletzt die
konkrete Exemplarprosa. Kann ein benötigter ID nicht rückwärts erreicht werden,
muss der Slot ungelöst werden; freie Nacherzählung ist keine Reparatur.

## Was tatsächlich eingeführt, getragen, wiederaufgenommen und resettiert wird

- `PICTURE_OWNER`: 11 Initialisierungen, 105 Carries.
- `ACTIVE_PREPARATION_OR_ITEM`: 8 explizite und 3 ungelöste Erstwerte;
  61 Carries/Reassertions, 8 Resumes sowie 36 explizite, ungelöste oder
  auflösende Resets.
- `TARGET_OR_STATION`: 9 explizite und 5 ungelöste Erstwerte; 33
  Carries/ungenutzte Carries, 1 Resume, 60 explizite oder ungelöste Resets und
  8 UNSET-Operationen.
- `PREVIOUS_ITEM_REFERENCE`: 41 explizite Referenznutzungen, 4 Resumes, 17
  ACTIVE-Archive, 43 ungenutzte Carries und 11 anfängliche UNSET-Zustände.

`V62_R1_REGISTER_CARRY_EDGES.tsv` publiziert 435 konkrete Zustandskanten. Dazu
gehören 11 Owner-Initialisierungen, 144 tatsächlich geerbte Carries, 11
Resumes, 21 ACTIVE→PREVIOUS-Verweise/Archive sowie Kanten, die einen
Eingangswert vor einem Reset sichtbar bewahren. Keine Kante kreuzt einen
Record.

## Elf Recordzustände

`V62_R1_11_RECORD_INITIAL_FINAL_REGISTERS.tsv` zeigt für jeden Record den
identischen Initialtyp und den tatsächlich erreichten Endstatus. Wesentliche
Lehrpunkte:

- H1 endet mit `ITEM_H1_001`, einem ungelösten Ziel und einem Rückverweis auf
  denselben anonymen Item-ID; die Wurzel-/Arzneilesung bleibt außerhalb des ID.
- H2–H5 benötigen mehrere lokale Item-IDs, weil Parallelzellen neue Teile oder
  Chargen eröffnen; diese Trennung ist konservativ und revidierbar.
- B1–B4 besitzen die meisten Zielresets. Das bewahrt die Rivalität
  Körperstelle ↔ Becken/Lauf, statt beides still gleichzusetzen.
- B5 beginnt mit ungelöstem ACTIVE und TARGET; erst die spätere Maß-/Zielklausel
  liefert normale IDs. Sein PREVIOUS kann deshalb selbst auf einen ungelösten
  früheren Item-ID zeigen.
- B6 ist eine einzige zweizeilige V61-Aussage: Owner, Item und Ziel werden im
  selben Statement eingeführt; der interne Rückverweis bleibt auf den anonymen
  Item-ID beschränkt.

## Markante ungelöste Fälle

29 benötigte Rollen in 27 Statements bleiben ungelöst:

- H1-S001 fordert für Waschen/Trinken ein Ziel, ohne eine eindeutige
  Zielstation zu initialisieren.
- H3-S004 und H4-S003 starten Parallel-/Neuklauseln mit zielbedürftiger
  Anwendung, aber ohne stabilen Ziel-ID.
- B1-S001, B2-S001 und B5-S001 beginnen mit einer Operation am Apparat, ohne
  dass ein aktiver Stoff oder Gegenstand bereits gebunden ist.
- B1-S007/B1-S015, B3-S024 und B4-S008 resetten auf eine Parallelzelle, deren
  aktiver Gegenstand nicht offen genannt wird.
- B2-S011 folgt auf die einzige `UNRESOLVED`-Grenze von V61; sein Ziel bleibt
  ebenfalls ungelöst, obwohl eine aktive Badeportion neu angesetzt wird.
- B5-S003 verlangt einen Rückverweis, doch sein gespeicherter Vorgänger ist
  selbst `UNRESOLVED_ITEM_B5_001`.

Die Reparaturregel lautet nie „errate Wasser/Person/Becken“, sondern: ID als
`UNRESOLVED_*` schreiben, Klausel weiter kopieren und erst bei einem späteren
expliziten Exemplarhinweis einen neuen normalen ID setzen.

## Typische Lehrlingsfehler

1. `ZIEL? = TARGET_B2_004` als Kartenübersetzung behandeln. Richtig: Die Karte
   verlangt höchstens einen Zielslot; der ID stammt aus diesem Recordlauf.
2. `VORIGES?` automatisch auf den unmittelbar vorherigen deutschen Satz
   beziehen. Richtig: PREVIOUS-Register nachschlagen; Zeilen- und Satznähe
   entscheiden nicht.
3. Bei `RESUME` einen neuen Item-ID erzeugen. Richtig: Eingangs-ACTIVE tragen,
   außer die Spur ist bereits ungelöst.
4. Bei `PARALLEL` alle Register löschen. Richtig: Owner bleibt; der alte ACTIVE
   wird vor einem Reset als PREVIOUS archiviert.
5. Zwei gleiche Wörter wie „Becken“ automatisch demselben TARGET-ID zuordnen.
   Richtig: explizite Ziele konservativ neu nummerieren, bis V63 eine
   ausführbare Gleichheitsregel liefern sollte.
6. Einen `UNRESOLVED_*`-ID nachträglich in einen normalen ID umbenennen.
   Richtig: nur ein späterer expliziter Schritt darf resetten; Geschichte bleibt
   im Carry-Edge-Ledger sichtbar.

## Stärkste Widersprüche und Rivale

1. 266/369 erforderliche Slots beruhen ausschließlich auf der kreativen
   deutschen Exemplarprosa; das Registermodell ist damit nicht unabhängig
   semantisch bestätigt.
2. 29 Slots bleiben trotz flüssiger Gesamtlektüre ungelöst. Flüssigkeit ist
   folglich kein Nachweis vollständiger Referenz.
3. Die konservativen 53 expliziten TARGET-Resets können echte wiederkehrende
   Stationen übertrennen. Der Gegenfehler — ein einziges Becken oder Körperziel
   durch den ganzen Record — wäre ebenso unbelegt.
4. ACTIVE wird 36-mal resettiert oder aufgelöst; manche dieser Fälle könnten
   Zustandsänderungen desselben Gegenstands statt neue Items sein.
5. PREVIOUS speichert gelegentlich einen ungelösten ID. Das System ist
   ausführbar, aber nicht ontologisch vollständig.
6. Ein sparsamer Zweiregister-Rivale `OWNER + ACTIVE` könnte TARGET und PREVIOUS
   jeweils aus der lokalen Prosa neu berechnen. Er braucht weniger Gedächtnis,
   kann aber `RESUME`, `ZIEL?` und `VORIGES?` nicht kontrolliert rücklesen und
   verwischt die Apparatur-/Körperrivalität.

## Artefakte und Validierung

- `V62_R1_116_STATEMENT_REGISTER_TRACE.tsv`: vollständiges vierfaches
  input→operation→next-Ledger mit Rollenbedarf, Evidenz und Klauseltext;
- `V62_R1_11_RECORD_INITIAL_FINAL_REGISTERS.tsv`: Initial-/Finalzustände und
  Slotcounts je Record;
- `V62_R1_REGISTER_CARRY_EDGES.tsv`: alle 435 recordlokalen Carry-, Resume-,
  Archiv- und Resetkanten;
- `V62_R1_BUILD_REGISTER_TRACE.py` und `V62_R1_VALIDATION.json`:
  reproduzierbare Zustandsmaschine und Prüfprotokoll.

Validierung: `PASS` für 11 Records, 116 Statements, vier Register, 464
potenzielle Slots, 369 benötigte Slots und 435 Kanten. Alle V61-Skeletons und
Klauseltexte bleiben bytegleich; jeder Folgezustand stimmt exakt mit dem
nächsten Eingang überein; alle IDs sind anonym, recordlokal und seitenbegrenzt.
