# V54 R1 — Biological-Ausgabe als bebildertes Bade- und Irrigationsmusterbuch

Status: vollständige kreative Werkstattausgabe der sechs erlaubten Records auf
`f81v`, `f82r` und `f83r`; keine Entzifferung. `f84` und `f84r` wurden nicht
berührt. Die vorhandene V42-Vollabdeckung dient als Nachweis für alle 115
Felder und 281 Ereignisse; V54 baut keine zweite 115-Zeilen-Kopie, sondern
revidiert die sechs vollständigen Prozessfolgen unter der strengeren
V52-Grammatik.

## Ergebnis

Die kleinste lehrbare Gesamtlesung ist ein **bebildertes Formular- und
Musterbuch für medizinische Bade-, Spül- und Irrigationsgänge**. Das
Formular-/Musterbuch erklärt die vielen kurzen, wiederholbaren Zellen; Bad und
Irrigation liefern die konkrete lokale Defaultausfüllung. Ein gewöhnliches
Badehaus- oder Wasserwerkregister bleibt der stärkste vollständige Rivale.

Diese Auswahl verbindet nicht heimlich drei Ebenen. Sie trennt sie:

```text
exakte Karte        -> nur ausgewähltes V50/V51-Merkwort oder UNBEKANNT
Feldform            -> NONCLOSE* TERMINAL?
sichtbares Bild     -> möglicher Besitzer, Ort oder Stationszeiger
vollständiges Feld  -> lokale, kreative Arbeitsanweisung
ganzer Record       -> geordnete Musterfolge; nicht notwendig ein Patientengang
```

## Vollständigkeit und harte Form

| Record | Felder | Ereignisse | offen | terminal |
|---|---:|---:|---:|---:|
| `f81v_R1` | 24 | 66 | 7 | 17 |
| `f82r_R1` | 26 | 62 | 7 | 19 |
| `f83r_R1` | 38 | 86 | 7 | 31 |
| `f83r_R2` | 20 | 47 | 4 | 16 |
| `f83r_R3` | 5 | 11 | 3 | 2 |
| `f83r_R4` | 2 | 9 | 2 | 0 |
| **gesamt** | **115** | **281** | **30** | **85** |

Aus V52/V53 folgt außerdem für den Biological-Teil: 113/281 Ereignisse tragen
einen ausgewählten Anker, 168/281 bleiben opak. Ein Terminal steht, wenn
vorhanden, genau einmal und zuletzt im Feld. Er wird nicht als „beende“,
„warte“ oder anderes gesprochenes Wort übersetzt. Eine physische Zeile ist
kein Satz.

## Strikte Kartenankerschicht

V54 führt keine neue Kartenbedeutung ein. Zulässig bleiben nur:

```text
OK=SETZEN       OT=MARKIEREN    L=VERKNÜPFEN    AL=AN?
E=UNBEKANNT     OR=BEREITUNG?   CHEY=TEIL?

AIIN=MASS?      EY=KLAR?        OKY=VERWENDEN?  LCHE=ABLASSEN?
OKE=SPÜLEN?     CTHY=BEREIT?    OKEEY=WARM?     CKHY=UNBEKANNT
OLOR=ZUVOR?
```

`LCHE` und `OKE` bleiben terminalkonfundierte Ganzkarten; aus ihrem Schluss
wird keine Semantik gewonnen. RIGHT-Klassen wie `<ARG_AIIN>` erben niemals
`AIIN=MASS?`. Wasser, Öl, Tuch, Person, Körperstelle, Becken, Röhre, Trank und
Auflage gehören ausschließlich zur Bild- oder Ganzfeldexpansion.

## Drei vollständige Modelle im Vergleich

| Modell | Was es gut erklärt | Stärkster Verlust | Urteil |
|---|---|---|---|
| medizinische Bad-/Irrigationswerkstatt | Figuren als Behandelte; warme und kühle Anwendungen; Waschen, Baden, Binden, Trinken und Ableiten als gewöhnlicher Arbeitsvorrat | keine Diagnose und kein Körperteil ist kartenseitig verankert; eine einzige lineare Therapie über 38 Felder ist unglaubwürdig | beste konkrete Inhaltsausfüllung, wenn als Mustersammlung gelesen |
| Badehaus/Wasserwerk | Becken, verbundene Läufe, Füllen, Umlauf, Klären und Ablassen; sehr leicht an mehrere Schreiber übertragbar | Tuch, Auflage, Trank und einzelne Anwendung müssen zu Betriebsvarianten umgedeutet werden; die genaue Buchgattung bleibt unbelegt | stärkster vollständiger Sachrivale |
| Formular-/Musterbuch | 115 kurze Felder, 85 formale Schlüsse, offene Fortsetzungen, Wiederholungen und sehr ungleiche Recordlängen | bestimmt für sich weder Flüssigkeit noch medizinischen Zweck und erklärt die Figuren nur als Owner-Zeiger | beste Architektur, aber kein eigenständiger Sachinhalt |

Die Auswahl ist daher zweistufig: **Musterbuch** ist die Schreibarchitektur;
**medizinische Bäder/Irrigationen** sind die beste kreative Defaultdomäne. Wo
ein Feld ohne Verlust als Wasserwerkschritt lesbar ist, bleibt diese Lesung
gleichrangig markiert.

## Die sechs Recordentscheidungen

### 1. `f81v_R1` — gemeinsamer Warmwasser-Umlauf

- **[BILD] Owner-Rollen:** Figuren im verbundenen Becken-/Laufbild;
  Arbeitsstelle, oberer Zulauf, unterer Sammelraum und Rücklauf sind mögliche
  Stationsbesitzer, keine Wörter.
- **[GANZFELD] Prozess:** Erstspülung; gemessenen Voransatz und Rücklauf im
  unteren Bereich mischen; durch verbundene Läufe führen; warm halten, rühren,
  stehen lassen und bedeckt verwahren; nachfüllen, einmal erwärmen und kühlen;
  erneut spülen; füllen, temperieren, klären und an der markierten Station
  verwenden.
- **Revision:** V42/V49s Öl, Becken und Leitungen bleiben brauchbare lokale
  Defaults, werden aber aus keinem Atom mehr abgeleitet. Die 24 Felder sind
  Stationszellen, nicht 24 Sätze.
- **Stärkster Widerspruch:** Dasselbe Bild kann Patientenbad, Gefäßumlauf oder
  dekorativ gegliederten Raum zeigen.
- **Lehrregel:** Kopiere zuerst die Stationenfolge; sprich nur Kartenanker und
  ergänze Rücklauf oder Medium erst bei der Ganzfeldlesung.

### 2. `f82r_R1` — Einzelplatz mit Wechsel- und Anwendungsvarianten

- **[BILD] Owner-Rollen:** Badende Figur, Teilbecken, zweite Öffnung, breites
  Gefäßfeld und unterer Ablauf als mögliche Bildbesitzer.
- **[GANZFELD] Prozess:** Gefäß/Lauf spülen und Ansatz zurückstellen; Portion
  warm eintauchen; über zweite Öffnung, Tuch und verbundenen Lauf klären;
  abziehen, Wasser oder Medium zugeben und warm halten; weitere Portionen
  eintauchen und unten ablassen; danach Warm-/Kühlspülung sowie die
  Formularoptionen Bad, Trank, Bindung und Schlussmischung.
- **Revision:** Die letzten Zellen werden nicht mehr zwanghaft als ein einziger
  Patientengang verbunden, sondern als geordnete, auswählbare Musterprompts.
- **Stärkster Widerspruch:** Baden, Trinken, Binden und Leitungsarbeit können
  ebenso voneinander unabhängige Bildadressen sein.
- **Lehrregel:** Ein neuer Owner-Zeiger darf die Anwendung wechseln; ein bloßer
  Feldschluss darf es nicht.

### 3. `f83r_R1` — langer Irrigations- und Rücklaufbogen

- **[BILD] Owner-Rollen:** Hauptfigur, obere Zufuhr, unterer Ablauf,
  Auffangbecken und mehrere verbundene Stationen; ihre genaue Zuordnung zu den
  Textfeldern bleibt hypothetisch.
- **[GANZFELD] Prozess:** Absetzen und unten abführen; abmessen und eintauchen;
  mit Warmwasser neu beginnen, spülen, mischen und bedeckt stellen; baden,
  ablassen, füllen und klären; örtlich verwenden, kühlen, erneut spülen und die
  Läufe wechseln; stehen, sanft erhitzen, Rückstand behalten; Person oder
  Arbeitsobjekt ans Becken setzen; dosieren, binden, zweimal spülen, abziehen,
  baden, im breiten Gefäß klären und im unteren Becken ruhen lassen.
- **Revision:** Der 38-Feld-Block ist ein Mastermuster aus wiederholbaren
  Zyklen, keine rekonstruierte 86-Wort-Prosa und keine zwingend lineare
  Einzeltherapie.
- **Stärkster Widerspruch:** Die fünf Arbeitsphasen können tatsächlich mehrere
  Varianten, nicht einen Prozess, darstellen.
- **Lehrregel:** Teile nur an terminalen Feldgrenzen; offene Felder erben den
  aktuellen Bildbesitzer, aber keinen stillen neuen Gegenstand.

### 4. `f83r_R2` — lauwarmer Nachlauf und Filtergang

- **[BILD] Owner-Rollen:** Nachbehandlungsfigur, breites Becken, obere und
  untere Laufstation; Tuch und Auflage sind Kontextdefaults, nicht sicher
  sichtbare Besitzer.
- **[GANZFELD] Prozess:** Temperiert baden, füllen und spülen; zum unteren
  Ablauf rühren; Anteil lauwarm mit dem Voransatz verwenden und stehen lassen;
  binden; zweimal durch Tuch klären; noch warm an der ersten Öffnung spülen;
  sanft erhitzen, im breiten Gefäß zugeben, zweimal waschen, unten ableiten;
  sofort verwenden, oberen Lauf öffnen und Warmwasser nachfüllen.
- **Revision:** `Binden`, `Tuch`, `breites Gefäß` und `Warmwasser` bleiben
  vollständige Felddefaults; keines wird einem unbekannten Atom zugeschlagen.
- **Stärkster Widerspruch:** Dieselbe Folge ist als rein technischer Filter-
  und Transfergang mindestens ebenso glatt.
- **Lehrregel:** Zwei gleiche Filterfelder werden zweimal kopiert; Wiederholung
  darf nicht als ein einziges Wort oder als Schreibfehler verschwinden.

### 5. `f83r_R3` — kurzer Wärme-/Übergabenachtrag

- **[BILD] Owner-Rollen:** Übergabestelle und zweiter Lauf; ein eigener Patient
  oder eigener Ansatz ist nicht sichtbar gesichert.
- **[GANZFELD] Prozess:** Abziehen; einmal erwärmen; ein Intervall halten; mit
  dem Voransatz warm und maßweise zur markierten Stelle führen; am zweiten
  Lauf gleichmäßig weiterrühren.
- **Revision:** V42/V49s Fortsetzungsintuition wird verschärft: die drei offenen
  Schlussfelder erhalten keinen neuen stillen Rezeptbesitzer.
- **Stärkster Widerspruch:** Der Block kann bloß Nachtrag oder Korrektur zu
  `f83r_R2` sein.
- **Lehrregel:** Bei offenem Nachtrag den letzten ausdrücklich sichtbaren Owner
  weiterführen; ohne Bildwechsel keinen neuen erfinden.

### 6. `f83r_R4` — ungekochter Direktgang

- **[BILD] Owner-Rollen:** Figur oder Arbeitsobjekt am Becken, erste Öffnung
  und markierte Zielstation. „Person“ ist nur die engste Bildausfüllung.
- **[GANZFELD] Prozess:** Ohne Kochen am Becken ansetzen und den Voransatz über
  die erste Öffnung führen; eine gemessene aktuelle Portion durch Tuch zur
  markierten Stelle bringen.
- **Revision:** Der kurze Schlussblock bleibt ein offener Zwei-Zellen-Nachtrag;
  V54 fügt weder Diagnose noch gesprochenen Abschluss hinzu.
- **Stärkster Widerspruch:** Figur, Gefäß oder abstrakter Zustand können
  denselben Ownerplatz besetzen.
- **Lehrregel:** Offene Schlussfelder offen lassen; der Schreiber darf keinen
  fehlenden Terminalstrich semantisch ergänzen.

## Rücklese- und Fehlerregel für Lehrlinge

Ein Lehrling liest zuerst Record und Bildstation, dann Feld für Feld. Er nennt
nur die ausgewählten Kartenmerkwörter, markiert opake Karten als unbekannt und
liest eine vorhandene Terminalform ausschließlich als Grenze. Erst danach
spricht er die lokale Werkstattanweisung aus dem vorgezeigten Muster.

Die fünf häufigsten Fehler wären: eine Zeile zum Satz machen; `CLOSE` als Verb
lesen; ein Bildobjekt in eine Karte einschmuggeln; `<ARG_AIIN>` als `MASS`
lesen; mehrere Formularvarianten zu einer einzigen Therapie verkleben. Genau
diese Fehler beseitigt V54 gegenüber V42/V49, ohne deren vollständige
Feldabdeckung aufzugeben.

## Grenze

Die Ausgabe ist ausführbar und lehrbar, aber die Sachwahl bleibt unbestimmt.
Badende, Becken und Läufe favorisieren einen Wasser-/Badekontext; sie beweisen
weder Medizin noch Wasserwerk. 168 von 281 Ereignissen sind atomar opak. Die
flüssigen Prozessfolgen sind deshalb Ganzfeldexpansionen aus Bild, Register und
gewöhnlicher Werkstattpraxis, keine Summe entzifferter Wörter.
