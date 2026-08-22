# V59 R3 — finale technische und reproduzierbare Edition

Status: vollständige kreative Zehn-Seiten-Edition, keine Entzifferung. Bestätigte
Lexeme und Klartextsätze bleiben jeweils null.

## Endurteil

`DOMAIN_NEUTRAL_EXEMPLAR_FORM_ARCHITECTURE_WITH_IATROMEDICAL_NARROW_CONTENT_LEAD`

Die robuste Schicht ist ein bildgebundenes, exemplarabhängiges
Formular-/Nachschlagesystem mit kleinem Kontrollkern und großem lokalem
Kartenschwanz. Die iatromedizinische WHAT/HOW/WHEN-Lesung bleibt der knappe
inhaltliche Default. Pflanzenrohstoff + Bade-/Waschhaus + Arbeitsalmanach bleibt
die vollständige nichtmedizinische Gegenedition. Keine der beiden
Inhaltsschichten ist Kartenbedeutung.

## Release

| Artefakt | Datenzeilen | Funktion |
|---|---:|---|
| `V59_R3_FINAL_173_CARD_DICTIONARY.tsv` | 173 | eine Zeile je opaker exakter Prosa-ID |
| `V59_R3_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv` | 381 | vollständige Prosaereignisse mit Feldzuordnung |
| `V59_R3_FINAL_135_FIELD_EDITION.tsv` | 135 | ausführbare Feldpartition und lokale Expansion |
| `V59_R3_FINAL_395_ASTRO_GROUPS.tsv` | 395 | ausschließlich seitenlokale Astro-Gruppen und Adressen |
| `V59_R3_FINAL_776_EVENT_LEDGER.tsv` | 776 | normalisierte Vereinigung von 381 Prosa- und 395 Astrozeilen |
| `V59_R3_FINAL_14_RECORD_DIAGRAM_READINGS.tsv` | 14 | fünf Herbal-, sechs Bio- und drei Astro-Gesamtlesungen |
| `V59_R3_VALIDATION.json` | — | Checks und SHA-256-Werte aller sechs Datentabellen |

Das 776er-Ledger verweist über `unit_reading_ref` auf die 14 vollständigen
Texte. Dadurch bleiben alle Records/Diagramme vollständig, ohne dieselben
langen Paraphrasen in jeder Ereigniszeile zu vervielfachen.

## Verbindlicher Schichtenvertrag

1. **Exakte Identität:** `joint_tuple_id` beziehungsweise die lokale
   Astro-Vorkommens-ID bleibt opak und ist kein Wort.
2. **Form:** `page_host_coordinate`, `formal_formula`, Feldposition und
   Abschluss sind Analyse-/Rendererkoordinaten. `CLOSE` ist nur Feldschluss.
3. **Atomare Auswahl:** V50 liefert die formalen Operationen SETZEN,
   MARKIEREN und VERKNÜPFEN sowie die schwachen Mnemonics AN?, BEREITUNG? und
   TEIL?. V51 liefert acht behaltene Ganzkartenmnemonics. Alles andere heißt
   `UNKNOWN_EXEMPLAR`.
4. **V56-Kontext:** Nur 45 Ereignisse tragen einen der vier strengen
   Kontextprompts; darunter gilt `daiin` nur als oberflächenlizenzierter
   Vorgabeparameter. Das globale AIIN-Kartenmnemonic bleibt überall MASS?.
5. **Keine Vererbung:** Ein Ganzkartenmnemonic geht nie auf sichtbare
   Komponenten, RIGHT-Klassen oder ähnliche Oberflächen über. Der Validator
   erzwingt genau ein globales Defaultmnemonic je exakter Prosa-ID.
6. **Lokale Vollständigkeit:** V49-Ereignis-/Feldexpansionen bleiben als
   kreative Exemplarinhalte erhalten; V53/V54 liefern die ausgewählten
   vollständigen Recordtexte. V58 liefert parallel den nichtmedizinischen
   Rivalen.
7. **Astro separat:** Die 395 V22-Gruppen werden nur deshalb übernommen, weil
   V55 diese vollständige Ledgerausgabe ausdrücklich fortführt. Ihre
   Mnemonics sind `ASTRO_LOCAL_ONLY`; keine V50/V51/V56-Prosaangabe wird
   importiert.

Eine physische Zeile ist in jeder Tabelle ausdrücklich `line_is_sentence=NO`.
Alle f68r1-/f69v-Zeilen tragen `direct_f68_f69_join=NONE`.

## Deterministische Override-Reihenfolge

```text
V49 exact ID + formal formula + complete local expansion
  → V50 selected host operation / weak host mnemonic
  → V51 selected recurrent whole-card mnemonic
  → V56 exact-card reinforcement or exact context prompt
  → otherwise UNKNOWN_EXEMPLAR
  → join selected V53/V54/V55 unit default
  → join parallel selected V58 rival
```

Widersprechende Mnemonics lassen den Builder abbrechen. Ein formaler Prompt
ersetzt kein Ganzkartenmnemonic: So kann `FRAME_O(LINK)` als Steueroperation
auftreten, ohne dem umgebenden Karteninhalt ein Objekt oder eine
Verbindungsart zu geben.

## Validierte Bilanz

- 173 eindeutige Prosa-Karten-IDs;
- 381 Prosaereignisse in 135 Feldern;
- 90 geschlossene und 45 offene Felder, jeder Schluss höchstens einmal und
  nur feldfinal;
- 145 ausgewählte atomare/formale Ereignisse und 236
  `UNKNOWN_EXEMPLAR`-Ereignisse;
- 45 strenge V56-Prompt-Ereignisse in 35 Feldern;
- 52 Felder ohne benannten Anker und 17 vollständig benannte Felder;
- 395 Astrogruppen an 142 Loci;
- 776 eindeutige Gesamtledgerzeilen;
- 14 vollständige Einheiten mit Aggregaten 20/100 Herbal, 115/281 Bio und
  142/395 Astro;
- kein Prosa-Mnemonic in Astro und kein direkter f68r1↔f69v-Join.

## Reproduktion

Vom V59-Verzeichnis aus:

```bash
python3 V59_R3_BUILD_FINAL_RELEASE.py
python3 V59_R3_VALIDATE_FINAL_RELEASE.py
```

Der Builder liest nur die ausgewählten V49–V56-Basistabellen, die ausgewählten
V53–V55 Unit-Texte und das durch V55 weiterlizenzierte ausgewählte V22-Ledger.
Die V58-Gegenlesungen sind als exakt ausgewählte Ein-Satz-Defaults im Builder
eingefroren. Der Validator schreibt reproduzierbare SHA-256-Werte in
`V59_R3_VALIDATION.json`.

## Technische Schlussfolgerung

Die Edition ist vollständig, weil jede opake Einzelzeile auf eine lokale
Expansion und einen vollständigen Unit-Text verweist. Sie ist konservativ,
weil diese Vollständigkeit nie nach unten als Wortbedeutung zurückgeschrieben
wird. Der formale Apparat entscheidet zwischen Medizin und Betrieb nicht; die
Medizin behält ihren knappen Vorsprung ausschließlich als historische und
bildgestützte Recordexpansion.

Es wurden keine neuen Seiten oder Daten eingeführt und kein Commit oder Push
ausgeführt.
