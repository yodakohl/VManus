# V58 R1 — stärkster vollständiger nichtmedizinischer Rivale

Status: kreative Gegenedition der zehn festen Sidequest-Seiten aus Sicht eines
Werkstattlehrmeisters um 1420. Sie ist weder Entzifferung noch semantischer
Beweis.

## Urteil

Der stärkste nichtmedizinische Rivale ist ein
**illustriertes technisches Auftrags- und Lehrmusterbuch als offenes
Miszellaneum**:

```text
Garten-/Materialproben       5 Herbal-Records
Badehaus-/Wasserwerksformen  6 Biological-Records
Kalender-/Diagrammvorlagen   3 Astrodiagramme
```

Der gemeinsame Zweck ist nicht ein erfundener Garten→Wasser→Kalender-Ablauf.
Eine Schreiber-/Zeichnerwerkstatt bewahrt darin vollständige Muster für drei
Arten bebilderter praktischer Aufträge. Gemeinsam sind Kartenökologie,
Feldform, Exemplarbenutzung, Renderer und Korrektur; die Inhalte bleiben drei
lokale Fachmappen. Damit erklärt das Modell ausdrücklich ein Miszellaneum.

Arbeitsurteil:

`ILLUSTRATED_TECHNICAL_COMMISSION_EXEMPLAR_MISCELLANY`

Es ist der beste Gegner der medizinischen Zweckthese, überholt sie im
qualitativen 100-Punkte-Vergleich aber knapp **nicht**: 82 zu 84. Der Abstand
ist kleiner als die Unsicherheit der kreativen Ausgaben. V59 sollte daher die
exemplarbasierte Architektur als zweckneutral behandeln und Medizin nur als
führende lokale Inhaltsfüllung, nicht als Kartenbedeutung.

## Vollständige Gegenedition

`V58_R1_COMPLETE_NONMEDICAL_READINGS.tsv` gibt allen fünf Herbal-Records, allen
sechs Biological-Records und allen drei Astrodiagrammen eine konkrete
nichtmedizinische Prozessfolge. Sie übernimmt die bestehenden vollständigen
Record- beziehungsweise Diagrammgrenzen ohne Auslassung oder Neusegmentierung:

- Herbal: 20 Felder/100 Ereignisse;
- Biological: 115 Felder/281 Ereignisse;
- Astro: 142 Loci/395 Gruppen;
- gesamt: 10 Seiten, 14 Einheiten und 776 sichtbare Gruppen.

Die flüssigen Gegenlesungen sind Ganzrecord-Defaults. Kein Stoff, Werkzeug,
Wasserlauf, Arbeitsschritt oder Kalenderwert wird dadurch zum Kartenlexem.

## Erlernbarer Werkstattablauf

1. **Auftragsmappe wählen.** `BOTANISCHE_MATERIALPROBE`,
   `WASSERWERKSFORMULAR` oder `KALENDERDIAGRAMM`; keine Karte wechselt frei
   zwischen den drei Fachmappen.
2. **Bild/Geometrie zuerst kopieren.** Pflanze, Becken-/Figurenumfeld oder
   Diagrammlage liefert nur die stille Adresse.
3. **Vollständiges lokales Muster auflegen.** Einer von elf Prosa-Records oder
   eines von drei Diagrammblättern bestimmt seltene Karten, Reihenfolge und
   Oberfläche.
4. **Kleinen Kontrollstreifen einsetzen.** Vorgabeparameter aufrufen,
   Standardslot setzen, Relationsslot setzen und aktiven Arbeitsstand
   verknüpfen. Nur diese vier Regeln sind streng übertragbar.
5. **Lokale Sachprosa am Rand halten.** Gartenlos, Farbmuster, Zisterne,
   Filter, Sternstation oder Arbeitstag sind Meisterexpansionen, keine Werte
   sichtbarer Fragmente.
6. **Felder setzen.** `FIELD := NONCLOSE* TERMINAL?`; Schluss höchstens einmal
   und nur feldfinal. Physische Zeile bleibt Reflow.
7. **Aus demselben Deck rendern.** Exakte Ganzkarte, belegte Position,
   Wrapper, JOIN/SPACE und Handform werden nicht aus Bedeutungsfragmenten neu
   erzeugt.
8. **Korrektor rückliest formal.** Er prüft Bildadresse, Kartenidentität,
   Reihenfolge, Wiederholung, Schluss und Lage. Inhaltlich darf er nur den
   bezeichneten vollständigen Musterbogen aufsagen.

Dieser Ablauf ist für alle zehn Seiten derselbe. Er produziert keine elfte
Seite und keinen fachübergreifenden Sachindex.

## Druck auf das Wörterbuch

| Schicht | feste Abdeckung | nichtmedizinische Behandlung |
|---|---:|---|
| Tier A | 45/381 Ereignisse in 35/135 Feldern | vier formale Kontrollen unverändert behalten |
| gemeinsame exakte Brücke | 17 Typen, 136 Ereignisse | elf Karten/zehn Promptklassen; 96/136 Ereignisse nur mit exponierter Mnemonik |
| Tier-B-Merkwörter | `MASS?`, `VERWENDEN?`, `BEREIT?`, `BEREITUNG?`, `AN?`, `KLAR?`, `ZUVOR?`, `TEIL?` | als domänenneutrale Rezitationshilfen möglich, niemals Sachnomen |
| lokaler Schwanz | 162/173 Prosa-Kartentypen außerhalb des elfteiligen Decks | aus Recordmuster kopieren; keine neue Universalbedeutung |
| opake Prosa | 236/381 Ereignisse | sichtbar bewahren und bei atomarer Rücklesung `UNKNOWN` sagen |
| Bio-lokale Mnemonics | `WARM?`, `SPÜLEN?`, `ABLASSEN?` | passen zu Wasserwerk, bleiben aber `LOCAL_ONLY`; Schluss liefert keine Tätigkeit |
| Astro | 395/395 Gruppen | drei lokale ZL3b-Namensräume; keine Prosa-Kartenwerte importieren |

Der Rivale fügt **null neue universelle Kartenwerte** hinzu. Sein Vorteil ist
deshalb keine bessere Übersetzung, sondern geringerer Dictionary-Druck. Seine
kompletten Garten-, Wasserwerks- und Kalendertexte entstehen ebenso wie die
medizinischen Texte erst auf Recordebene.

## Stille Annahmen

1. Die vier Pflanzenbilder sind Garten-/Werkstoffproben und keine Heilpflanzen.
2. Die fünf Herbal-Records handeln von Herkunft, Ernte, Sortierung,
   Extraktion, Materialprobe und Lagerung; keine dieser Funktionen ist direkt
   im Bild identifiziert.
3. Die Biological-Figuren sind Badegäste, Bediener oder Maßstabsfiguren, nicht
   Patienten; die gezeichneten Läufe bilden reale oder exemplarische
   Wasserwerksfunktionen ab.
4. Wärme, Klären, Filtern, Spülen und Ablassen gehören zu Haus-/Badebetrieb,
   nicht zu Therapie. Diese Entscheidung liegt im Ganzrecord, nicht in der
   Karte.
5. Die drei Kreisblätter sind Kalenderzeichner-/Lookup-Muster. Ein
   Arbeitskalender ist möglich, aber kein Kalenderwert ist extern verankert.
6. Die Werkstatt oder ein späterer Besitzer hat drei Fachmappen wegen ihrer
   gemeinsamen Herstellungsweise zusammengebunden. Es gibt keinen sichtbaren
   Sachverweis zwischen ihnen.
7. Die konkreten Materialverwendungen — Farbstoff, Beize, Leimung, Duftstoff
   oder Faserprobe — sind austauschbare lokale Defaults und dürfen nicht in
   die Kartenglossen zurückfließen.

## Stärkste Widersprüche

- Die Herbal-Bilder und die historische Abiss-Parallele besitzen eine stärkere
  medizinische Quellenanalogie als eine nachgewiesene Färbe-/Materialkunde.
- Für Gartenbeet, Färberprobe, Leimung, Werkstoffprüfung oder Lagerklasse gibt
  es keinen unabhängig bezeichneten Referenten.
- Nackte Figuren in Becken passen ausgezeichnet zu gewöhnlichem Badebetrieb,
  aber ihre Dichte und Nähe zu Anwendungen passt ebenso gut oder besser zu
  therapeutischer Badeliteratur. Ein reiner Rohrplan erklärt sie nicht.
- Die gezeichneten Biological-Läufe sind nicht als maßstäbliche Hydraulik
  bestätigt; ein technischer Wasserwerksbetrieb wird auf Recordebene geraten.
- Sieben, zwölf und achtundzwanzig sind kalender-/astronomisch gewöhnlich,
  doch keine Gruppe benennt Tag, Monat, Planet, Stern oder Arbeit.
- Zwischen den beiden 28er-Seiten bleiben 0/28 Gleichpositionstreffer, null
  Vollformtreffer im 28×28-Raster sowie fehlender Start und fehlende Richtung.
  Der Rivale darf deshalb ebenfalls keinen Kalender-Join bauen.
- Ein Musterbuch kann fast jede opake Sequenz „als Exemplar“ bewahren. Diese
  Erklärung ist formal stark, aber semantisch schwach und teilweise
  unfalsifizierbar.
- Teure, inhaltlich reiche Bilder sind schwerer als bloße Schreibübungen zu
  erklären. Der Rivale braucht professionelle Auftragsmuster, nicht
  belanglose Lehrlingskritzeleien.

## Direkter Punktvergleich

Die sechs bereits verwendeten qualitativen Kriterien bleiben unverändert;
Punkte sind Modellvergleich, keine Wahrscheinlichkeit. Details stehen in
`V58_R1_DIRECT_COMPARISON.tsv`.

| Kriterium | max. | technisches Miszellaneum | iatromedizinisches WHAT/HOW/WHEN |
|---|---:|---:|---:|
| Erklärung exakter Evidenz | 25 | 23 | 21 |
| Abdeckung dreier Register | 20 | 19 | 18 |
| Lehrbarkeit | 15 | 15 | 13 |
| historische Plausibilität | 15 | 10 | 14 |
| semantischer Hebel | 15 | 7 | 11 |
| unterscheidende Vorhersagen | 10 | 8 | 7 |
| **gesamt** | **100** | **82** | **84** |

Der Rivale gewinnt Formökonomie, ehrliche Modultrennung und Lehrbarkeit. Die
medizinische Theorie gewinnt bei Bild-/Gattungsanalogie und der Kohärenz von
Pflanze, Bad/Anwendung und astrologischer Praxis. Beide verlieren am selben
Punkt: Es gibt keine sichtbare direkte Verknüpfung der drei Module.

## Unterscheidende Prüfungen

- **Für den Rivalen:** Nach Kontrolle von Seite und Stencil sollten seltene
  Karten und Terminalfamilien stärker mit Kopiermuster/Renderer als mit
  unabhängig sichtbaren Patienten-, Pflanzen- oder Tätigkeitsrollen gehen.
- **Für Medizin:** Eine extern bezeichnete wiederholte Karte müsste dieselbe
  Behandlung, Körperstelle, Zubereitung oder Indikation über verschiedene
  Records tragen und stärker sein als Stencilidentität.
- **Herbal-Scheide:** Ein lesbares paralleles Quellenblatt müsste überwiegend
  Material-/Gartenoperationen statt Heilanwendung besitzen oder umgekehrt.
- **Bio-Scheide:** Figurenunabhängige Auslässe stützen Wasserwerk; stabile
  figur-/körpergebundene Rollen nach Seitenkontrolle stützen Therapie.
- **Astro-Scheide:** Ein extern verankerter Arbeits-/Erntekalender stützt den
  Rivalen; eine Behandlungs-/Körperregel stützt WHAT/HOW/WHEN. Gleiche
  Kardinalität allein entscheidet nichts.

## Schluss

Der nichtmedizinische Rivale erklärt die **Herstellung** der zehn Seiten
mindestens ebenso gut wie die iatromedizinische Theorie. Er erklärt ihren
konkreten **Inhalt** schlechter und gewinnt den Gesamtvergleich deshalb nicht.
Die robuste V58-Korrektur lautet:

```text
Architektur: zweckneutrales illustriertes Exemplarsystem
führender Inhalt: iatromedizinische Arbeitsfüllung
stärkster Rivale: technisches Garten-/Wasser-/Kalender-Miszellaneum
direkter Sachjoin: in beiden Modellen nicht lizenziert
```
