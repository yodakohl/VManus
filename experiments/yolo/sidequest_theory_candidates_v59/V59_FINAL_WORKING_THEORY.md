# V59 — finale Arbeitstheorie nach zehn Verbesserungsrunden

Status: kanonische Endfassung des kreativen Zehn-Seiten-Sidequests. Keine
wissenschaftliche Entzifferung.

## Ergebnis in einem Satz

Die zehn Seiten lassen sich am sparsamsten als **bildadressiertes,
exemplarabhängiges Werkstattregister mit kleiner formaler Kontrollgrammatik,
wenigen memorierten Ganzkarten und großem lokalem Kartenschwanz** schreiben;
iatromedizinische Pflanzen-, Bad-/Irrigations- und Astroinhalte bilden die
knapp führende vollständige Arbeitslesung, aber dieselbe Maschine trägt fast
ebenso gut ein technisches Pflanzenrohstoff-/Badehaus-/Almanachregister.

## Kanonische Datenfassung

R1s V59-Ausgabe ist die ausgewählte Datenrelease:

| Datei | Inhalt | Zeilen |
|---|---|---:|
| `V59_R1_FINAL_173_CARD_DICTIONARY.tsv` | alle exakten Prosa-Karten | 173 |
| `V59_R1_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv` | alle Prosaereignisse | 381 |
| `V59_R1_FINAL_135_FIELD_EDITION.tsv` | alle Prosa-Felder | 135 |
| `V59_R1_FINAL_395_ASTRO_GROUP_EDITION.tsv` | alle Astrogruppen | 395 |
| `V59_R1_FINAL_776_VISIBLE_UNIT_EDITION.tsv` | gemeinsame Gesamtledger | 776 |
| `V59_R1_FINAL_14_RECORD_DIAGRAM_TEXTS.tsv` | 11 Records + 3 Diagramme | 14 |

`V59_R1_BUILD_FINAL_EDITION.py` erzeugt diese Tabellen reproduzierbar;
`V59_R1_VALIDATION.json` bindet Quellen- und Ausgabehashes. Die kompakte
Lesefassung steht in `V59_FINAL_TEN_PAGE_READING.md`, das aktive Kurzlexikon in
`V59_FINAL_QUICK_DICTIONARY.tsv`.

## Warum R1 statt der drei anderen Vollausgaben

R2 und R3 behalten V50s PAGE_HOST-weite schwache AL-/OR-/CHEY-Leads und
annotieren deshalb 145/381 Ereignisse. R1 bindet Mnemonics nur an die in V56
exakt ausgewählten Joint-Tuple-Identitäten. Drei nichtportable Vorkommen fallen
zurück auf `UNKNOWN/EXEMPLAR`:

```text
R2/R3: 145 annotiert + 236 unbekannt
R1:    142 annotiert + 239 unbekannt
```

Die strengere Fassung gewinnt, weil die atomare Einheit des Sidequests das
exakte GDT327-Joint-Tuple ist und PAGE_HOST keine etablierte semantische
Einheit darstellt. Diese letzte Korrektur verhindert, dass die zuvor
zurückgewiesene Stammsemantik durch die Hintertür wiederkehrt.

## Das Schreibsystem

### 1. Stiller Besitzer

Das Bild oder Diagramm wird zuerst angelegt. Es liefert den Artikelbesitzer
oder die räumliche Adresse, ohne dass Pflanzenname, Becken, Körper, Rohr,
Planet oder Sternstation ausgeschrieben sein müssen.

### 2. Feldgrammatik

```text
FIELD := NONCLOSE* TERMINAL?
```

Alle 90 formalen Schlüsse stehen einmal und feldfinal; 45 Felder bleiben
offen. Eine physische Zeile ist Reflow und darf eine Aussage fortsetzen.
`CLOSE` wird nicht als Wort gesprochen.

### 3. Kleine Kontrollschicht

Der strengste registerübergreifende Kern lautet:

```text
daiin                    -> VORGABEPARAMETER?
SET(<ARG_AIIN>)          -> STANDARDSLOT SETZEN
SET(<ARG_AL>)            -> LOKALEN RELATIONSSLOT SETZEN
FRAME_O(LINK)            -> AKTIVEN ARBEITSSTAND VERKNÜPFEN
```

Er deckt 45/381 Ereignisse in 35/135 Feldern. Weitere SET/MARK/LINK-Formen
erhöhen die rein formale Deckung auf 57 Ereignisse, ohne Quellenwörter zu
liefern.

### 4. Memorierte Ganzkarten

Acht gemeinsame exakte Karten tragen die exponierten Mnemonics `MASS?`,
`VERWENDEN?`, `BEREIT?`, `BEREITUNG?`, `AN?`, `KLAR?`, `ZUVOR?` und `TEIL?`.
Drei Bio-lokale Karten tragen `WARM?`, `SPÜLEN?` und `ABLASSEN?`; die letzten
beiden sind mit Feldschluss konfundiert. Zusammen betreffen diese elf Karten
85 Ereignisse.

Formale und mnemonic Schicht überlappen; ihre disjunkte Vereinigung umfasst
142/381 Ereignisse. 239/381 bleiben `UNKNOWN/EXEMPLAR`.

### 5. Lokale Exemplardecks

162/173 exakte Prosa-Kartentypen besitzen kein gemeinsames kurzes Mnemonic.
Der Schreiber kopiert sie aus einem der elf Recordmuster. Die drei Kreisblätter
bilden eigene Positionsdecks mit 395 lokalen Gruppen. Ein Meister kann trotzdem
jede Stelle in eine konkrete Quellenphrase expandieren, solange Record, Bild
und Exemplar vorliegen.

### 6. Renderer

Wrapper, q/s, JOIN/SPACE, Positionsform und Zeilenreset werden aus einem
lizenzierten lokalen Muster gewählt. Sie tragen keine eigene Übersetzung.
RIGHT-, FRAME-, INNER-D-, DY- und B3-Koordinaten erben niemals das Mnemonic
einer vollständigen Karte.

## Wozu das Buch in der ausgewählten Welt dient

### Herbal = WHAT

Fünf bebilderte Simplex-/Materia-medica-Artikel notieren Auswahl,
Zubereitungsstand, Maß, Verbindung, Gebrauch und Folgeansatz. Die konkreten
Pflanzenwetten reichen von einer skabiosen-/Teufelsabbiss-nahen Wurzel über
Veilchen/Doldenpflanze und Allium/Wegerich bis zur riskanten Sonnentau-Lesung.

### Biological = HOW

Sechs Records notieren kurze Arbeitszellen für temperieren, mischen, stehen,
klären, filtern, ablassen, nachfüllen und weitergeben. Figuren halten
therapeutisches Baden und Anwendung offen; menschenfreie Ausläufe erzwingen
zugleich eine echte Apparateschicht. „Frauenheilkunde“ oder ein bestimmtes
Organ wird nicht eingesetzt.

### Astro = WHEN

- f67r2: 7×12-Konfigurations-/Auswahltafel;
- f68r1: Zentrum plus 28 räumliche Stationen;
- f69v: geordnete 28 lokale Regeln.

Iatromathematik, Mondstationen und Regimenpraxis sind die historische
Defaultfamilie. Die Seiten besitzen jedoch keinen nachgewiesenen gemeinsamen
Start, Lauf oder 28er-Schlüssel.

## Der gleichwertige Gegenversuch

Die formale Maschine kann auch folgendes Buch tragen:

```text
Herbal -> Pflanzenrohstoffe und technische Auszüge
Bio    -> Bade-/Waschhaus- oder Wasserwerksbetrieb
Astro  -> allgemeiner Arbeits-/Wahlalmanach
```

Dieser Rivale erklärt die Apparateschicht besser, braucht aber fünf
unbelegte Pflanzenendprodukte und einen unbelegten Arbeitskalender. In allen
vier unabhängigen V58-Rubriken verliert er knapp gegen die medizinische
Inhaltskohärenz. Deshalb gilt:

`ARCHITEKTUR DOMÄNENNEUTRAL; MEDIZIN NUR FÜHRENDER INHALTSDEFAULT`.

## Was die zehn Runden verbessert haben

| Runde | bleibende Korrektur |
|---|---|
| V50 | E=BIS zurückgezogen; nur drei formale Operationen und drei schwache Hostleads |
| V51 | komplexe Kartenparaphrasen auf elf kurze Ganzkartenmnemonics reduziert; CKHY zurückgezogen |
| V52 | Feldform von Satzbedeutung getrennt; 236 Ereignisse explizit opak |
| V53 | fünf komplette Herbal-Artikel mit Bildrivalen und ungestützten Nomen |
| V54 | sechs komplette Bio-Prozesse als Therapie plus reale Apparateschicht |
| V55 | drei unabhängige Astro-Instrumente; f68↔f69-Join verworfen |
| V56 | kleiner gemeinsamer Kontrollkern statt universellem medizinischem Lexikon |
| V57 | mehrere Schreiber lernen Regeln plus Exemplare, nicht 173 freie Wörter |
| V58 | nichtmedizinischer Vollrivale beweist die Domänenneutralität der Algebra |
| V59 | letzte PAGE_HOST-Semantik entfernt; alle 776 Defaults in getrennten Ebenen konsolidiert |

## Bedeutung von „vollständig“

Jede sichtbare Gruppe besitzt:

1. opake Identität;
2. formale Rolle;
3. exaktes Mnemonic oder `UNKNOWN`;
4. konkrete lokale Ereignis-/Slotexpansion;
5. Verweis auf einen vollständigen Record-/Diagrammtext;
6. einen technischen Gegeninhalt.

Damit ist die kreative Edition vollständig. Bestätigte historische Lexeme,
Klartextsätze, Sprache, Lautwerte und referentielle Bedeutungen bleiben
dennoch **null**.

## Schluss

Der Sidequest ist auf diesen zehn Seiten ausgeschöpft. Weitere Verbesserung
würde jetzt neue Seiten, eine unabhängige externe Referenz oder eine neue
methodische Prüfung brauchen. Nach der Anweisung wird weder automatisch eine
weitere Runde noch ein wissenschaftlicher Voynich-Score gestartet.

`f84` und `f84r` blieben durchgehend versiegelt.
