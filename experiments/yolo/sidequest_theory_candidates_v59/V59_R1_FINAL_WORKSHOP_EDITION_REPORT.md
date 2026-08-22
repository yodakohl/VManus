# V59 R1 — finale Zehn-Seiten-Werkstattedition

Status: vollständige kreative Endausgabe des Sidequests, keine Entzifferung.
Bestätigte Lexeme und bestätigte Klartextklauseln bleiben jeweils null.

## Endurteil

```text
ROBUSTE ARCHITEKTUR
  zweckneutrale, bildadressierte Exact-Card-/Exemplarmaschine

FÜHRENDER LOKALER INHALTSDEFAULT
  iatromedizinisches WHAT/HOW/WHEN
  = Pflanzenzubereitung | Bad/Irrigation mit Apparat | Astro-/Regimenanhang

STÄRKSTER VOLLSTÄNDIGER RIVALE
  technisches Miszellaneum
  = Pflanzenrohstoff | Bade-/Waschhausbetrieb | Arbeitsalmanach

NICHT LIZENZIERT
  Sachbedeutung aus Host-Substring, phrase-sized stem gloss,
  Semantik aus CLOSE/RIGHT/Wrapper oder direkter 28er-Seitenjoin
```

Im V58-R1-Vergleich behält der iatromedizinische Inhalt den knappen Vorsprung
84:82. Diese Wertung betrifft nur kreative Inhaltskohärenz. Das sichtbare
Schreibsystem selbst bleibt domänenneutral.

## Vollständige Ausgabe

Der Builder `V59_R1_BUILD_FINAL_EDITION.py` übernimmt die Vollbestände
mechanisch und lässt keine Zeile von Hand aus:

- 173 Exact-Card-Defaults: `V59_R1_FINAL_173_CARD_DICTIONARY.tsv`;
- 381 Prosaereignisse: `V59_R1_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv`;
- 135 Felder: `V59_R1_FINAL_135_FIELD_EDITION.tsv`;
- 395 Astrogruppen: `V59_R1_FINAL_395_ASTRO_GROUP_EDITION.tsv`;
- 776 sichtbare Einheiten gemeinsam: `V59_R1_FINAL_776_VISIBLE_UNIT_EDITION.tsv`;
- 5 Herbal- + 6 Bio- + 3 Diagrammtexte:
  `V59_R1_FINAL_14_RECORD_DIAGRAM_TEXTS.tsv`.

V49 liefert Karten, Ereignisse und Felder; V43 bestätigt dieselben 173
deutschen kreativen Kartendefaults; V22 liefert die 395 Astrogruppen. Die
aktuellen Ganztexte stammen aus V53–V55, der Rivale aus V58, die Lehr- und
Bindungsregeln aus V50–V57. Quell- und Ausgabe-Hashes stehen in
`V59_R1_VALIDATION.json`.

## Die fünf strikt getrennten Ebenen

| Ebene | Inhalt | Darf nicht werden |
|---|---|---|
| `FORMAL_VALUE` | Exact-Tuple, SET/MARK/LINK, Rahmen, Position, OPEN/TERMINAL oder Astro-Locus | gesprochenes Quellenwort |
| `ATOMIC_OR_WHOLE_CARD_MNEMONIC` | ein exaktes, kurzes Fragezeichen-Merkwort | produktiver Stamm oder Substringregel |
| `LOCAL_IATROMEDICAL_EXPANSION` | vollständiger Ereignis-, Feld-, Record- oder Diagrammdefault | Beleg für den Kartenwert |
| `NONMEDICAL_RIVAL` | gleichrangige lokale technische Gegenexpansion | zweites Kartenwörterbuch |
| `UNKNOWN_EXEMPLAR_STATUS` | explizite Grenze und Kopierpflicht | still ergänzte plausible Prosa |

Die ausgegebenen Formelbäume ersetzen jede Hostkoordinate durch
`OPAQUE_PAYLOAD`; die Exact-Tuple-ID bewahrt dennoch die Identität. Damit wird
kein Hostname als Bedeutungsschlüssel benutzt.

## Finaler kleiner Lehrbestand

### Vier strenge Kontrollen

```text
daiin                    VORGABEPARAMETER?
SET(<ARG_AIIN>)          STANDARDSLOT SETZEN
SET(<ARG_AL>)            LOKALEN RELATIONSSLOT SETZEN
FRAME_O(LINK)            AKTIVEN ARBEITSSTAND VERKNÜPFEN
```

Sie decken 45/381 Ereignisse in 35/135 Feldern. RIGHT-Klassen erben weder
`MASS?` noch `AN?`.

### Exakt gebundene Mnemonics

```text
portabel:   MASS?  VERWENDEN?  BEREIT?  BEREITUNG?
            AN?    KLAR?       ZUVOR?   TEIL?
Bio-lokal:  WARM?  SPÜLEN?     ABLASSEN?
sonst:      UNKNOWN
```

`SPÜLEN?` und `ABLASSEN?` bleiben schlusskonfundiert. `CKHY` und `E` bleiben
unbekannt. `Y–AIIN–Y` wird in seinen zwei Vorkommen als exakte Ganzform
memoriert; Gleichmaß, Dyade und Referenz bleiben unentschieden.

Die Bindung erfolgt ausschließlich über Exact-Tuple-IDs. Deshalb sinkt die
alte V52-Deckung von 145 auf 142/381: drei nichtportable AL-/OR-/CHEY-
Hostvorkommen erhalten in V59 kein Merkwort mehr. Insgesamt gelten:

- 57 Ereignisse mit domänenneutraler formaler SET/MARK/LINK-Operation;
- 85 Ereignisse mit exakter Mnemonik, davon 62 portabel und 23 Bio-lokal;
- 142 Ereignisse in der disjunkten Vereinigung dieser beiden Schichten;
- 239 Ereignisse `UNKNOWN/EXEMPLAR`;
- 82/135 Felder mit mindestens einem strikten Anker, 53 ohne Anker und nur
  17 vollständig annotierte Felder.

## Feld-, Renderer- und Astroregeln

```text
FIELD := NONCLOSE* TERMINAL?
```

Alle 90 Schlüsse stehen genau einmal und feldfinal; 45 Felder bleiben offen.
Eine physische Zeile ist Reflow, kein Satz. CLOSE wird nicht gesprochen. Eine
Karte darf nur in belegter FIRST/MIDDLE/LAST/ONLY-Position und nur in einer
bereits lizenzierten Oberfläche erscheinen. `s` am Zeilenanfang und `q` nach
DY bleiben Renderertendenzen ohne Wortwert.

Astro besitzt 395/395 lokale Defaults, aber kein Prosakartenlexikon:

- `f67r2`: 74 Loci/190 Gruppen, 7×12-Konfigurations- und Auswahltafel;
- `f68r1`: 37 Loci/65 Gruppen, Zentrum + 28 räumliche Stationen;
- `f69v`: 31 Loci/140 Gruppen, geordnete 28 lokale Regeln.

Zwischen den beiden 28er-Inventaren bleiben 0/28 Gleichpositionstreffer, null
Vollformtreffer im 28×28-Raster, kein gemeinsamer Start und keine gemeinsame
Richtung. Die drei radialen `okeod`-Einträge behalten sowohl im medizinischen
als auch im nichtmedizinischen Default denselben Wert; ein weiteres sichtbares
`okeod` innerhalb der Kreisprosa ist ein anderer lokaler Slot.

## Schreibunterricht

1. Bild oder Diagramm zuerst kopieren und nur als stillen Besitzer binden.
2. Eines der 14 vollständigen Exemplare wählen; keine lokale Karte aus einem
   anderen Deck erraten.
3. Exact-Tuple bestimmen, dann den formalen Wert lesen; sichtbare Teilform und
   ähnliche Oberfläche sind kein Schlüssel.
4. Nur bei exakt freigegebener ID das Einwort-Merkwort mit Fragezeichen
   aufsagen; sonst `UNKNOWN`.
5. Karten in belegter Position einsetzen und das Feld nach
   `NONCLOSE* TERMINAL?` schließen oder offenlassen.
6. Oberfläche, JOIN/SPACE und Zeilenreset aus demselben Hand-/Seitendeck
   kopieren.
7. Erst danach den iatromedizinischen **oder** den technischen Ganzdefault aus
   dem bezeichneten Exemplar expandieren; nie aus den Atomen zusammensetzen.
8. Der Korrektor liest rückwärts: Bildadresse → Oberfläche → Exact-Tuple →
   Position → Feldschluss → Mnemonik/UNKNOWN → getrennten Ganzdefault.

Ein Lehrling fällt durch, wenn er Zeile=Satz setzt, CLOSE übersetzt, ein
Bildnomen in die Karte steckt, eine lokale Bio-Mnemonik ins Herbal überträgt,
ein unbekanntes Ereignis aus flüssiger Prosa ergänzt oder die beiden
28er-Blätter indexgleich verbindet.

## Vierzehn Endtexte

Die vollständige Texttabelle bewahrt folgende Einheiten ohne semantischen
Kurzschluss:

- Herbal: `H1–H5`, 20 Felder/100 Ereignisse;
- Biological: `B1–B6`, 115 Felder/281 Ereignisse;
- Astro: `A1–A3`, 142 Loci/395 Gruppen.

Jede Zeile enthält formale Rolle, Mnemonikschicht, vollständigen
iatromedizinischen Text, vollständigen nichtmedizinischen Rivalen,
Exemplarstatus, Hauptwiderspruch und Lehrregel.

## Stärkste Widersprüche

1. 239/381 Prosaereignisse besitzen unter der strengsten Schicht keine
   atomare oder formale Quellenlesung; die Ganztexte sind meisterseitige
   Expansionen.
2. 53/135 Felder haben keinen strikten Anker, obwohl beide Inhaltsmodelle sie
   flüssig ausfüllen. Fluency ist daher kein Entzifferungsbeleg.
3. Kein ausgewählter Wert benennt Pflanze, Wasser, Wein, Frau, Körper,
   Krankheit, Becken, Rohr, Gefäß, Stern oder Richtung.
4. Das technische Miszellaneum trägt fast dieselbe Algebra. Formale Passung
   diagnostiziert keine Medizin.
5. Die iatromedizinische Theorie besitzt die bessere Bild- und
   Gattungsanalogie, aber keinen sichtbaren WHAT→HOW→WHEN-Sachzeiger.
6. Alle 395 Astroinhalte sind lokale Exemplarwerte ohne extern verankerten
   Namen oder Regelinhalt.

## Validierung und Schluss

Die Validierung ist `PASS`: 173/381/135/395/776/14, zehn Seiten, 11
Prosa-Records, drei Diagramme, 45 offene und 90 geschlossene Felder. Sie prüft
vollständige Ebenen, identische V43/V49-Kartenwerte, V49/V22-Prosaidentität,
exakte Feldpartition, erlaubte Seiten, Einwort-Mnemonics, Astrotrennung und den
fehlenden 28er-Join.

Das finale R1-Modell lautet:

`DOMAIN_NEUTRAL_EXEMPLAR_MACHINE_WITH_IATROMEDICAL_NARROW_CONTENT_LEAD_AND_COMPLETE_NONMEDICAL_CONTROL`

Es ist als beaufsichtigtes Kopier-, Formular- und Rücklesesystem lehrbar. Es
ist kein autonomer semantischer Codec und keine wissenschaftliche Übersetzung.
