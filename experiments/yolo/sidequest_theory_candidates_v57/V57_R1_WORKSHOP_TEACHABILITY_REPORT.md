# V57 R1 — Lehrmanual für die Zehn-Seiten-Werkstatt

Status: unabhängiger Lehrbarkeitstest aus der Rolle eines Werkstattlehrmeisters
um 1420. Das Folgende ist ein ausführbares Modell für Abschrift und begrenzte
Rekomposition der zehn Sidequest-Seiten, keine Entzifferung und kein Beweis
ihres historischen Zwecks.

## Urteil

Mehrere Schreiber könnten das sichtbare System zuverlässig fortführen, **wenn**
die Werkstatt nicht ein großes Wörterbuch, sondern vier getrennte Lehrmittel
besitzt:

1. einen kleinen gemeinsamen Kontrollstreifen;
2. elf vollständige Prosa-Recordmuster mit ihren seltenen Karten;
3. drei voneinander getrennte Astro-Musterblätter;
4. einen Korrekturbogen für Feldschluss, Kartenposition und lokale Oberfläche.

Lehrbar ist vor allem die Form. Die konkrete deutsche Quellenprosa ist nur aus
Bild und Recordmuster wiederzugewinnen. Wer das Musterblatt wegnimmt, erhält
keine Pflanze, kein Wasser, keinen Körperteil und keine Stationsregel aus den
Karten allein. Genau diese Grenze ist Teil des Lehrplans.

## Geprüfter Bestand

| Register | Seiten | Einheiten | Felder/Loci | sichtbare Gruppen | offene/geschlossene Felder | ausgewählte Anker/opaque Ereignisse |
|---|---:|---:|---:|---:|---:|---:|
| Herbal | 4 | 5 Records | 20 Felder | 100 | 15/5 | 32/68 |
| Biological | 3 | 6 Records | 115 Felder | 281 | 30/85 | 113/168 |
| Astro | 3 | 3 Diagramme | 142 Loci | 395 | nicht anwendbar | nicht anwendbar |
| **gesamt** | **10** | **11 Records + 3 Diagramme** | **135 Prosa-Felder + 142 Astro-Loci** | **776** | **45/90** | **145/236** |

Die zehn Seiten sind ausschließlich `f10r`, `f11r`, `f55v`, `f56r`, `f81v`,
`f82r`, `f83r`, `f67r2`, `f68r1` und `f69v`. Die Seitendecks stehen vollständig
in `V57_R1_LOCAL_EXEMPLAR_DECKS.tsv`.

## Vier Arten von Wissen

| Zeichen | Was der Lehrling damit tun darf | Beispiel |
|---|---|---|
| `P` produktiv | Eine Regel innerhalb bereits belegter Register-, Feld- und Positionslizenzen anwenden. | `FIELD := NONCLOSE* TERMINAL?` |
| `M` memoriert | Eine exakte Karte, Formel, Sequenz oder Oberfläche als unzerlegtes Muster kopieren. | `Y–AIIN–Y`; seltene Recordkarten |
| `B` bildgeliefert | Einen stillen Besitzer oder eine lokale Sachklasse aus dem Bild einsetzen. | Bildpflanze; Becken-/Figuren-/Röhrenumfeld |
| `D` Default | Eine kreative deutsche Recordlesung nur zusammen mit ihrem festen Musterbogen aufsagen. | Wurzelwasser; Bad-/Irrigationsgang; Mondstationsregel |

`P` ist die einzige echte Generativität. `M`, `B` und `D` dürfen im Kopf des
Schreibers zusammenkommen, werden aber beim Korrigieren wieder getrennt.

## Curriculum in acht Lektionen

| Lektion | Meisterstück | Auswendig | Produktiv | Bestehensprobe |
|---:|---|---|---|---|
| 1 | Bild zuerst, Schrift danach | zehn Seiten und ihre 14 Einheiten | sichtbaren Besitzer als stillen Recordparameter führen | Kein Bildwort wird einer Karte zugeschrieben. |
| 2 | Exakte Karten erkennen | Kernformen und Wrappergleichheiten | gleiche exakte Karte trotz lokaler Oberfläche wiedererkennen | `AIIN/DAIIN/SAIIN/CHAIIN/TAIIN`, freie Y-Formen und `CHOL/OL` werden nicht als fünf, sechs oder zwei Lexeme gezählt. |
| 3 | Kontrollstreifen | vier Tier-A-Regeln; acht exponierte Tier-B-Merkwörter | nur die vier strengen Konstruktionen in belegten Slots benutzen | Ein stilles Objekt wird nie in ein Merkwort eingebaut. |
| 4 | Feld und Schluss | lokale Terminalkarten und Positionslisten | offene und geschlossene Felder korrekt bilden | Jeder Schluss steht einmal und nur am Feldende; Zeile und Satz werden nicht gleichgesetzt. |
| 5 | Herbal-Muster | fünf Recordfolgen, 20 Felder, seltene Karten | gemeinsamen Kontrollstreifen in Herbal-Slots einsetzen | 15 offene und 5 geschlossene Felder bleiben erhalten. |
| 6 | Biological-Muster | sechs Recordfolgen, 115 Felder, lokale Zellstencils | kurze Zellen, Wiederholung und aktive Verknüpfung formal führen | 30 offene und 85 geschlossene Felder bleiben erhalten. |
| 7 | Oberfläche und Korrektur | seiten-/handlokale Allomorphe | nur eine bereits belegte Oberfläche an einer belegten Position wählen | Kein Wrapper erhält eine Übersetzung; keine neue Tuple wird erfunden. |
| 8 | Astro-Sonderkurs und Rücklese | drei komplette Diagrammdecks | Geometrie, Inventargröße und exakte Wiederholung reproduzieren | Keine Prosa-Glosse und keine direkte `f68r1`↔`f69v`-Zuordnung wird importiert. |

Die kleine Werkstatt braucht drei Rollen: Der Meister bezeichnet Bildbesitzer
und Muster; der Schreiber setzt beziehungsweise kopiert Karten; der Korrektor
liest rückwärts nur Kartenidentität, Feldform, Position, Wiederholung und
Bildadresse. Erst danach darf der Meister die lokale Defaultprosa nennen.

## Kernkarten und Kontrollstreifen

### Tier A: vier ausführbare gemeinsame Regeln

| sichtbare/formale Einheit | Werkstattprompt | Modus | Lizenz |
|---|---|---|---|
| exaktes `daiin` | `VORGABEPARAMETER?` | `M`, schwach `P` | nur an belegten Herbal-/Bio-Positionen; die Art des Parameters bleibt lokal |
| `SET(<ARG_AIIN>)` | `STANDARDSLOT SETZEN` | `P` | formale Konstruktion; RIGHT erbt nicht `MASS` |
| `SET(<ARG_AL>)` | `LOKALEN RELATIONSSLOT SETZEN` | `P` | formale Konstruktion; RIGHT erbt nicht `AN` |
| `FRAME_O(LINK)` | `AKTIVEN ARBEITSSTAND VERKNÜPFEN` | `P` | nur mit belegter Rahmen- und Positionsform |

Diese Schicht deckt 45/381 Prosaereignisse in 35/135 Feldern. Nur
`VORGABEPARAMETER?` ist überhaupt eine Quellenphrase; die übrigen drei sind
Steuerregeln.

### Tier B: portable, aber memorierte Merkwörter

| exakte ausgewählte Karte | einziges Merkwort | Lehrstatus |
|---|---|---|
| `AIIN` | `MASS?` | `M`; konkretes Maß/Grad/Dauer bleibt im Record |
| `OKY` | `VERWENDEN?` | `M`; kein stilles Mittel oder Ziel |
| `CTHY` | `BEREIT?` | `M` |
| `OR` | `BEREITUNG?` | `M` |
| `AL` | `AN?` | `M`; nicht auf RIGHT übertragen |
| `EY` | `KLAR?` | `M` |
| `OLOR` | `ZUVOR?` | `M` |
| `CHEY` | `TEIL?` | `M`; keine bestimmte Pflanzen- oder Körperpartie |

Zusammen mit `SET` und `LINK` bilden elf gemeinsame exakte Brückenkarten zehn
Promptklassen und erklären 96/136 Brückenereignisse. Sie sind ein
Rezitationsvokabular, kein produktives gemeinsames medizinisches Lexikon. Die
einzigen registerübergreifenden kurzen Folgen `ZUVOR?|LINK` und
`VERWENDEN?|MASS?` werden parataktisch gelernt, nicht als Sätze.

### Nur lokale beziehungsweise zurückgezogene Karten

- `OK = SETZEN`, `L = VERKNÜPFEN` sind nur innerhalb der obigen formalen
  Konstruktionen produktiv; `OT = MARKIEREN` bleibt eine lokale formale
  Gedächtnishilfe.
- `LCHE = ABLASSEN?`, `OKE = SPÜLEN?` und `OKEEY = WARM?` bleiben
  Biological-lokale Defaults. Besonders terminales `LCHE` darf im
  Korrekturdurchgang nur als Schlussform behandelt werden.
- `E` und `CKHY` bleiben `UNKNOWN`; terminal gebundenes `oldy` erhält keine
  Quellenphrase.
- Die einzige längere gemeinsame Formel `Y–AIIN–Y` wird als eine exakte
  Ganzform memoriert. Ihre beiden Kontexte lizenzieren weder gleiche Menge noch
  symmetrische Operanden.

## Schreibgang

1. **Bildadresse festlegen (`B`).** Das vorhandene Bild wird zuerst kopiert.
   Es bezeichnet den Recordbesitzer, schreibt aber kein Nomen in eine Karte.
2. **Seitendeck wählen (`M`).** Einer der elf Prosa-Records oder eines der drei
   Astro-Blätter wird geöffnet. Ein freier Wechsel zwischen Decks ist verboten.
3. **Quellengerüst markieren.** Nur Tier-A-Kontrollen werden produktiv gesetzt;
   Tier-B-Merkwörter bleiben Fragezeichen. Alle lokalen Sachwörter stehen am
   Rand des Musterbogens, nicht im Kartenwert.
4. **Opaque Folge kopieren (`M`).** Unbekannte Karten bleiben sichtbar und
   unbekannt. Sie dürfen weder ausgelassen noch mit plausibler Prosa gefüllt
   werden.
5. **Feld bilden (`P`).** `FIELD := NONCLOSE* TERMINAL?`. Ein Feld kann offen
   bleiben oder genau eine lizenzierte Terminalkarte am Ende tragen.
6. **Position prüfen (`P`).** Jede Karte bleibt in einer für sie belegten
   `FIRST`, `MIDDLE`, `LAST` oder `ONLY`-Position. Fehlt eine Lizenz, wird nicht
   geschrieben, sondern ein vollständiges lokales Muster kopiert.
7. **Oberfläche rendern (`M/P`).** Wrapper und Handform kommen aus demselben
   Seitendeck. Physischer Zeilenanfang begünstigt `s`, eine Stelle nach
   angehängtem DY begünstigt `q`; beides sind Kopiertendenzen, keine
   übersetzten Vorsilben und keine freie Erzeugungsregel.
8. **Zeilen setzen.** Eine physische Zeile enthält ein oder mehrere Felder.
   Wiederkehrende `4O`, `5O`, `1C|3C|1C|4O` und `2C|4O` sind Formstencils,
   keine Quellenphrasen.
9. **Rücklesen.** Zuerst werden exakte Karten, Schlussmuster und Bildadresse
   genannt. Die flüssige Defaultprosa darf nur mit sichtbar danebenliegendem
   Recordmuster ergänzt werden.

## Bildargumente

- **Herbal:** Das Bild macht einen bebilderten Simplex-/Materia-medica-Record
  plausibel und liefert einen stillen Pflanzenbesitzer. Skabiosenähnliche
  Wurzel, kleine Schattenpflanze, Breitblatt und Feuchtlandpflanze sind lokale
  Bilddefaults beziehungsweise Rivalen, keine Kartenübersetzungen.
- **Biological:** Figuren, Becken, Rohre und offene Ausläufe stützen eine
  gemischte Bad-/Irrigations- und Apparatewerkstatt. Viele Labels liegen aber
  nur nahe bei Figuren oder Formen; kein sichtbarer Gegenstand ist dadurch das
  Lexem einer Nachbarkarte.
- **Astro:** Kreisgeometrie, Zentrum und radiale Lage sind Teil der Adresse.
  Sie stützen Auswahltafel, räumlichen Katalog und Regelkreis, liefern aber
  weder Planeten-/Mondstationsnamen noch eine Verbindung zu einer Prosakarte.

## Astro-Sonderkurs

Die drei Blätter werden in getrennten Mappen gelernt:

1. `f67r2`: 74 Loci/190 Gruppen. Der Lehrling kopiert ein 7er-, ein 12er-, ein
   weiteres 12er-, ein 8er- und ein Rubrikinventar. `7×12` ist eine
   Konfigurationsidee, keine ausgeschriebene Vollmatrix. Planeten/Zodiak sind
   nur der historische Default des Meisters.
2. `f68r1`: 37 Loci/65 Gruppen. Zentrum, drei Anker, 28 räumliche Stationen und
   Zentrallegende werden positionsgetreu kopiert. Es gibt keinen sichtbaren
   Autorenstart und keine nachgewiesene Laufrichtung.
3. `f69v`: 31 Loci/140 Gruppen. 107 Kreistextgruppen und 33 Gruppen in 28
   radialen Regeln werden getrennt gehalten. Das exakte `okeod` an den
   Positionen 11, 15 und 24 behält dieselbe lokale Regel; `LONG/SHORT` ist
   keine Polarität.

Die gleiche Zahl 28 erlaubt im Unterricht den Hinweis auf eine gemeinsame
Gattung, aber keinen Index-Join: 0/28 Vollformtreffer bei gleicher moderner
Position und 0 Vollformtreffer über alle 28×28 Vergleiche. Ein Lehrling, der
Station *n* von `f68r1` automatisch mit Regel *n* von `f69v` verbindet, fällt
durch.

## Typische Lehrlingsfehler und Reparaturen

| Fehler | Diagnose | Reparaturregel |
|---|---|---|
| Zeile wird als Satz gelesen. | Layout wird zu Syntax. | Terminals suchen, Felder neu schneiden, Zeilenumbruch zuletzt behandeln. |
| Schluss wird als „ablassen“, „fertig“ oder Satzpunkt gesprochen. | Semantik kommt aus `CLOSE`. | Schlusswort streichen; nur `C` notieren. |
| Ein ganzes Wort wird in sichtbare Teilformen zerlegt. | Substring-/Host-Mining. | Exakte Karte beziehungsweise Joint-Tuple aus dem Deck holen und unzerlegt lesen. |
| `s` oder `q` erhält ein Lexem. | Renderer wird Wörterbuch. | Exakte Identität kollabieren; lokale Oberfläche aus demselben Deck zurückkopieren. |
| `MASS?` wird als „Maß Wasser“ gelernt. | Stilles Objekt steckt im Kartenwort. | Nur `MASS?`; „Wasser“ an Bild-/Recordrand verschieben. |
| `WARM?`, `SPÜLEN?` oder `ABLASSEN?` wandert ins Herbal-Deck. | Bio-Default wird universalisiert. | `LOCAL_ONLY` markieren und gemeinsame Tier-A-Regel benutzen. |
| Opaque Karte wird aus dem flüssigen Artikel ergänzt. | Defaultprosa überschreibt Evidenz. | Karte exakt kopieren, Rücklesung `UNKNOWN`; Prosa separat behalten. |
| Karte wechselt frei zwischen Anfang, Mitte und Ende. | Positionslizenz fehlt. | Belegte Position nachschlagen; sonst vollständiges Feldmuster kopieren. |
| Wiederholtes `qokeedy` wird als benannte Behandlung gelesen. | Gleichheit wird überinterpretiert. | Nur „dieselbe exakte Kategorie zweimal“ behalten. |
| `qokaiin` über `f82r.3→.4` wird allgemeines `RESUME`. | einmaliger Carry wird Grammatik. | Als lokale memorierte Ausnahme markieren; Dittographie bleibt Rivale. |
| `f68r1[n]` wird mit `f69v[n]` verbunden. | bloße 28er-Gleichheit wird Join. | Decks trennen; fehlenden sichtbaren Start, Richtung und Vollformtreffer aufsagen. |
| `LONG/SHORT` wird gut/schlecht. | Layoutlänge wird Bedeutung. | `okeod` 11/15/24 vergleichen; Polarität streichen. |

## Rückleseprüfung

Sechs konkrete Prüfungen stehen in `V57_R1_ROUNDTRIP_TESTS.tsv`. Bestanden
werden sie in zwei getrennten Spalten:

- `FORM_PASS`: Kartenidentität, Reihenfolge, Wiederholung, Bildadresse,
  Feldzahl/-schluss oder Diagrammgeometrie kommen zurück.
- `SEM_EXEMPLAR_ONLY`: Die konkrete Quellenprosa kommt nur zurück, solange das
  lokale Recordmuster vorliegt. Ohne dieses Muster muss der Lehrling
  `UNKNOWN` oder mehrere lokale Rivalen sagen.

Das ist kein Mangel der Prüfung, sondern ihr wichtigstes Korrektiv. Ein
scheinbar besserer semantischer Rücklauf, der Wasser, Pflanze, Bad, Rohr oder
Mondstation aus einer Karte allein erzeugt, ist ein Durchfallen.

## Stärkster Widerspruch und Schluss

Der stärkste Widerspruch gegen ein produktives Schreib-/Lesesystem lautet:
236/381 Prosaereignisse sind unter der ausgewählten Schicht opak, es gibt keine
gemeinsame vollständige Herbal-/Biological-Feldfolge, und Astro besitzt drei
lokale Namensräume ohne sichtbaren Join. Ein Schreiber kann deshalb die
flüssigen V53-/V54-/V55-Texte nicht aus einem kleinen Kartenlexikon neu
erzeugen. Er kann sie nur mit vollständigen Exemplaren bewahren.

Das Werkstattmodell besteht diesen Drucktest in der engeren Form
`SMALL_PRODUCTIVE_CONTROL_GRAMMAR_PLUS_LARGE_MEMORIZED_EXEMPLAR_LAYER`. Es ist
als Abschrift-, Muster- und Korrektursystem konkret lehrbar; seine
Quellenexpansion bleibt kreativ, registerlokal und semantisch unbeweisend.
