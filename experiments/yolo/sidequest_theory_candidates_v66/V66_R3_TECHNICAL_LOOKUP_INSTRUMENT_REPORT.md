# V66 R3 — ausführbare technische Nachschlageinstrument-Edition

## Ergebnis

Die drei Astro-Seiten lassen sich vollständig als **drei getrennte, nichtsemantische Nachschlageinstrumente** ausgeben. Die Edition deckt alle **395 sichtbaren ZL3b-Gruppen in 142 Loci** ab: f67r2 190/74, f68r1 65/37 und f69v 140/31. Jede Gruppe hat eine seitenlokale Adresse, eine Diagrammrolle und eine konkrete technische Defaultfunktion. Die sichtbare Zeichenfolge bleibt dabei nur ein opaker Merker; sie erhält keinen Wortwert.

Das stärkste nichtmedizinische Modell ist ein generisches Kalender-/Arbeitsplanregister. Es ist als Instrument ausführbar und kostet im festgelegten Beschreibungsmaß 50 Annahmepunkte gegenüber 137 für die medizinische Wahltafel. Das ist **kein Entzifferungsergebnis**: Die medizinische Lesung bleibt für f67r2 und f68r1 historisch-iconographisch stärker, während die Arbeitsplanlesung dort nur weniger externe Namen einsetzen muss. Auf f69v kosten beide Konkurrenten gleich viel kreative Regelprosa.

## Strikter Schichtenvertrag

1. **Sichtbare Gruppe:** Die 395 Oberflächen werden vollständig und unverändert projiziert.
2. **Lokale Adresse:** Nur A1-, A2- oder A3-interne IDs; keine gemeinsame Seiten-ID und kein Prosa-Tuple.
3. **Formale Rolle:** Auswahl-, Kopf-, Zentrum-, Stations-, Regel- oder Legendenfunktion.
4. **Technischer Default:** Ein ausführbarer lokaler Gebrauchssatz, ausdrücklich `LOCAL_FUNCTION_EXEMPLAR_NOT_WORD_MEANING`.
5. **Vergleich:** Die medizinische Wahltafel steht in einer separaten Vergleichsspalte und vererbt nichts an den technischen Default.

Weder ein Kartenteil noch eine bloße Formähnlichkeit erzeugt Inhalt. f68r1 und f69v werden nicht verbunden. Die Negativprüfung findet **0/28 gleiche Vollformen am selben redaktionellen Index und 0 Vollformüberschneidungen über alle 28×28 Paare**.

## Die drei Instrumente

| Instrument | Sichtbare Abdeckung | Ausführbarer technischer Gebrauch | stärkster Widerspruch |
|---|---:|---|---|
| A1, f67r2 | 190 Gruppen / 74 Loci | Sieben Reihenmerker, zwölf Spaltenmerker, zwölf getrennte Hilfsmerker und acht Bedingungsmerker adressieren einen virtuellen 7×12-Arbeitsauftrag; 35 übrige Loci sind lokale Anweisungsblöcke. | Keine vollständige 7×12-Zellmatrix und keine benannten Achsen sind sichtbar; die 84 Zellen sind daher ausdrücklich virtuell. |
| A2, f68r1 | 65 / 37 | Der sichtbare Mittelpunkt ist der opake Katalogbesitzer; 28 gezeichnete Loci sind primäre zweidimensionale Ortsadressen. Sieben Kopf- und ein Legendenlocus bleiben lokale Bedienbestandteile. | Die 28er-Form passt besser zu einem historischen Mondstationskatalog; Start, Richtung und Stationsnamen fehlen aber. |
| A3, f69v | 140 / 31 | Drei Kopf-Loci setzen den Konsultationsmodus; die 28 folgenden Quell-Loci liefern je genau eine lokale Arbeitsregel. Gleiche ganze Einträge erhalten dieselbe Regel. | Sämtliche konkreten Arbeitsregeln sind Exemplare, nicht aus den Zeichen erschlossene Werte; `LONG/SHORT` trägt keine Polarität. |

Für A3 bleibt insbesondere das ganze sichtbare `okeod` in den redaktionellen Regeln 11, 15 und 24 gleich und erhält dreimal denselben technischen Default. Das ist eine Gleichheitsbedingung an den ganzen Eintrag, keine Segmentierung.

## Ausführbare Lookup-Regeln

```text
A1(row R01..R07, column C01..C12, condition K01..K08, optional X01..X12)
  -> validiere lokale Schlüssel
  -> bilde A1:Rxx:Cyy
  -> lies einen der 84 virtuellen Arbeitsaufträge
  -> hänge K und optional X getrennt an
  -> gib Arbeitscode plus sichtbare Quell-Loci zurück

A2(drawn_locus f68r1.9..f68r1.36 | CENTER)
  -> validiere den gezeichneten Quellort
  -> gib seitenlokale Adresse plus opakes Label zurück
  -> verwerfe bloße Nummern ohne deklarierte Redaktionsvariante
  -> verwerfe jeden f69-Regelabruf

A3(source_locus f69v.4..f69v.31, optional rotation/sense)
  -> validiere den Quellort
  -> lies genau seine lokale Arbeitsregel und den opaken ganzen Eintrag
  -> behandle LONG/SHORT nicht als Wert
  -> verwerfe jeden f68-Stationsschlüssel
```

Die Prozessgraphen sind damit:

```text
A1: ROW_KEY + COLUMN_KEY + CONDITION_KEY -> VIRTUAL_CELL -> WORK_ORDER
A2: DRAWN_2D_LOCUS -> PAGE_LOCAL_ADDRESS -> OPAQUE_CATALOGUE_ENTRY
A3: HEADER_MODE -> SOURCE_RULE_LOCUS -> LOCAL_RULE -> EXECUTE_OR_WITHHOLD
```

## Orientierung und rotationsäquivalente Varianten

Keine moderne Nummer ist ein behaupteter Handschriftenanfang. Die Ausgabe bewahrt immer den Quell-Locus und behandelt Nummern nur als Auditkoordinaten.

- A1: 7 Reihenverschiebungen × 12 Spaltenverschiebungen = **84** Varianten der Rotationsgruppe C7×C12. Die gezeichnete Achsennachbarschaft bleibt erhalten; Spiegelungen sind keine Rotationen und werden nicht als zusätzliche Textwerte eingeführt.
- A2: 28 zyklische Startverschiebungen × zwei Aufzählungsrichtungen = **56** Varianten. Der gezeichnete zweidimensionale Locus bleibt der einzige Defaultschlüssel.
- A3: 28 Startverschiebungen × zwei Leserichtungen = **56** Varianten. Der f69-Quell-Locus bleibt der einzige Defaultschlüssel.

Insgesamt sind **196** Varianten explizit tabelliert. Keine Variante richtet A2 auf A3 aus.

## Symmetrischer Annahmekostenvergleich

Das feste Prüfmaß gewichtet Struktur=1, Domänenbelegung=2, externen Einzelnamen=1, lokalen Regelinhalt=1, Körper-/Behandlungsbindung=2, Werkstattachse=1, Orientierung=3 und Crosspage-Verbindung=5. Orientierung und Crosspage-Verbindung werden bei beiden Modellen mit null angesetzt. Das Maß ist nur ein reproduzierbarer Beschreibungslängen-Proxy, keine historische Wahrscheinlichkeit.

| Diagramm | generischer Arbeitsplan | medizinische Wahltafel | Kostenurteil | historisches Urteil |
|---|---:|---:|---|---|
| A1 | 11 | 70 | Arbeitsplan | Medizin führt wegen 7/12-Konvention |
| A2 | 7 | 35 | Arbeitsplan | Medizin führt wegen 28er-Stationsform |
| A3 | 32 | 32 | Gleichstand | Medizin führt knapp / Gleichstand |
| **Summe** | **50** | **137** | **Arbeitsplan im Proxy** | **kein Bedeutungsnachweis** |

Der Kostenunterschied A1/A2 entsteht vor allem dadurch, dass das technische Instrument sichtbare Labels opak lassen darf, während eine konkrete medizinische Ausgabe historische Planet-, Tierkreis-, Körper- oder Stationsnamen ergänzen müsste. A3 widerlegt einen billigen technischen Sieg: Beide Modelle müssen 28 nicht sichtbare lokale Inhalte bezahlen.

## Artefakte und Reproduktion

- `V66_R3_395_GROUP_LOOKUP_EDITION.tsv`: vollständige Gruppenprojektion und lokale Funktionslesung.
- `V66_R3_142_LOCUS_FUNCTIONS.tsv`: vollständige Locus-Lesungen.
- `V66_R3_F67_84_VIRTUAL_LOOKUP_CELLS.tsv`: kartesische, ausdrücklich nicht sichtbare Arbeitsadressen.
- `V66_R3_F68_29_ADDRESS_CATALOGUE.tsv`: Zentrum plus 28 räumliche Adressen.
- `V66_R3_F69_28_TECHNICAL_RULES.tsv`: getrennte lokale Regelreihe.
- `V66_R3_196_ROTATION_EQUIVALENCE_VARIANTS.tsv`: alle zugelassenen Redaktionsvarianten.
- `V66_R3_3_LOOKUP_ALGORITHMS.tsv`: Ein-/Ausgaben, Fehlerfälle und Prozessgraphen.
- `V66_R3_3_DIAGRAM_TECHNICAL_EDITION.tsv`: drei vollständige Diagrammlesungen.
- `V66_R3_6_MODEL_ASSUMPTION_COSTS.tsv`: symmetrische Kostenbuchung.
- `V66_R3_BUILD_LOOKUP_INSTRUMENT_EDITION.py` und `V66_R3_VALIDATE_LOOKUP_INSTRUMENT_EDITION.py`: deterministischer Build und Validator.

Ausführen:

```bash
python3 experiments/yolo/sidequest_theory_candidates_v66/V66_R3_BUILD_LOOKUP_INSTRUMENT_EDITION.py
python3 experiments/yolo/sidequest_theory_candidates_v66/V66_R3_VALIDATE_LOOKUP_INSTRUMENT_EDITION.py
```

Der Validator selektiert die drei erlaubten Seiten über den geschützten TSV-Zugriff, prüft 3/395/142 sowie alle Teiltabellen, die vollständige Quellprojektion, lokale IDs, Gleichheit wiederholter Ganzformen, die 0/0-Crosspage-Negativprobe, Annahmekosten und einen byte-identischen Neubau.
