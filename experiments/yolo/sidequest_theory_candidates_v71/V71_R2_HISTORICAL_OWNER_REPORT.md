# V71 R2 — historische Bild-zu-Text-Eigentümerkarte

Status: **explorative Sidequest-Arbeitstheorie; keine Entzifferung und kein
Wörterbuch**.

## Unveränderter R2-Hintergrund

1. Du kennst zeitgenössische Herbarien, Materia medica, Rezeptbücher, Abkürzungen und kompilierte Sammelhandschriften.
2. Du vergleichst Namen, Beschreibungen, Qualitäten, Habitate, Zubereitungen, Anwendungen und Rezeptfortsetzungen.
3. Du unterscheidest überlieferte Textpraxis von modernen Tabellen-, Datenbank- oder Übersetzungsannahmen.
4. Du darfst historische Quellen recherchieren, aber niemals Voynich-Formen über Klang oder Buchstabenähnlichkeit zuordnen.
5. Du lieferst die historisch plausibelste Quelltextstruktur samt Gegenbelegen und eng begrenzter Pseudoübersetzung.

## Ergebnis

Die 135 V69-Prosefelder und 142 eindeutigen Astro-Loci sind vollständig auf
den **kleinsten noch bildlich vertretbaren Eigentümer** zurückgesetzt. Die
277-Zeilen-Karte enthält 84 `DIRECT_VISIBLE`, 111 `INHERITED_VISIBLE`, 35
`PAGE_OWNER_ONLY` und 47 `UNRESOLVED`. Sie deckt alle 381 Proseereignisse und
alle 395 Astrogruppen ab.

Der Hauptbefund ist nicht ein neues Bedeutungslexikon, sondern eine
Eigentümerkorrektur:

```text
Herbal:  Feld -> Ganzpflanzenartikel, nicht automatisch Pflanzenteil/Operation
Bio:     Feld -> lokale sichtbare Station/Assembly, nicht seitenweiter Kreislauf
Astro:   Locus -> lokaler Ring-/Stern-/Rosettenplatz, nicht importierter Tabellenwert
```

Dabei bezeichnet „Eigentümer“ nur das Bildobjekt, dessen Artikel, Vignette oder
lokale Adresse den Text am sparsamsten rahmt. Es ist weder Referent noch
Wortbedeutung.

## Eigentümerstatus

- `DIRECT_VISIBLE`: Der Locus sitzt an einem einzelnen sichtbaren Träger, etwa
  einem lokalen Sternplatz oder Rosettenspeichenplatz. Das vergibt keinen
  Namen.
- `INHERITED_VISIBLE`: Der Text liegt in einer klar begrenzten Bildstation und
  erbt sie, besitzt aber keine Leader-Linie zu einem Einzelteil.
- `PAGE_OWNER_ONLY`: Nur das ganze Seitenbild oder der ganze Pflanzenartikel
  ist vertretbar.
- `UNRESOLVED`: Mindestens zwei sichtbare lokale Eigentümer bleiben gleich
  möglich; Nähe wird nicht als Entscheidung benutzt.

Die konkrete Vollkarte steht in `V71_R2_OWNER_LEDGER.tsv`; die 27 gebündelten
Änderungsfamilien stehen in `V71_R2_REVISIONS.tsv`.

## Gearbeitete Herbal-Spur

### f10r: F001 und die Wasserfrage

```text
F001 / H1 / f10r.2 / 10 Quellereignisse
    -> PAGE_OWNER_ONLY
    -> WHOLE_BROAD_TOOTHED_RADIAL_FLOWERED_HERB
    -> stiller Quelldefault: derselbe illustrierte Pflanzenartikel
    -> stärkster Rivale: spezieller Blüten-/Blatt-/Untergrundteil-Abschnitt
```

Die Achse verbindet Blätter, Blütenkopf, obere Terminalform und rote
Untergrundschwellungen. Kein Gefäß, Mensch, Werkzeug und **kein Wasser** berührt
die Pflanze. Historisch kann ein Herbalartikel selbstverständlich eine
wässrige Zubereitung enthalten, obwohl sie nicht abgebildet ist. Deshalb darf
„Wasser als unbebildertes Rezeptargument“ offenbleiben; weder ein rotes Organ
noch ein Feld wird dadurch zu WASSER. Genau dieselbe Eigentümerregel gilt für
F002–F005.

### f55v: vier Taschen, ein Artikel

F010–F013 liegen in vier durch Stamm und Blattmasse erzeugten Schreibtaschen.
Der Stamm ist aber ununterbrochen mit Spray, Blattmasse und groteskem
Wurzelkörper verbunden. Alle vier Felder erhalten daher
`PAGE_OWNER_ONLY -> WHOLE_BROAD_LEAF_PANICLED_PLANT_WITH_MNEMONIC_ROOT`.
Die attraktive Rivalin „eine Tasche je Blatt/Blüte/Wurzel/Tier“ bleibt im
Ledger stehen, verliert aber gegen die einfachere Bild-zuerst-Produktion.

Das entspricht der Gattung illustrierter Simples: Egerton MS 747 stellt große
Pflanzenbilder direkt in Textartikel; der Carrara-Codex Egerton MS 2020 zeigt
nahe 1400 eine Werkstatttradition differenzierter Pflanzenartikel. Diese
Vergleiche tragen Artikelstruktur, keine Pflanzenidentifikation.

## Gearbeitete Bio-Spur

### f82r: B2 wird wirklich in Vignetten geteilt

Die V69-Einheit B2 ist bildlich nicht eine Anlage. Die Feldspur lautet jetzt:

| Felder | Locus | kleinster Eigentümer | Status |
|---|---:|---|---|
| F045–F052 | .2–.4 | obere Doppelbogen-/Lochzylinder-/Figurenstation | `INHERITED_VISIBLE` |
| F053–F056 | .7 | lokales vierarmiges Kreuzstück an Querlinie | `INHERITED_VISIBLE` |
| F057–F058 | .19 | liegende Figur im trichterfüßigen Gefäß | `INHERITED_VISIBLE` |
| F059–F061 | .23 | Übergang zwischen Liegegefäß und unterem Becken | `UNRESOLVED` |
| F062–F070 | .26–.27 | untere grüne Figurenfassung mit vertikalen Enden | `INHERITED_VISIBLE` |

Der konkrete stille Default ist stets „die lokale Vignette ist aktueller
Artikel-/Stationsbesitzer“. Nicht still ergänzt werden dürfen Flüssigkeit,
Flussrichtung, Behandlung, Patient oder ein moderner geschlossener Kreislauf.

Die Badehandschriften Morgan MS G.74, BnF Latin 8161 und Angelica MS 1474
machen nackte Benutzergruppen in Becken und illustrierte Bäderregimen um diese
Zeit zu einer einfachen Gattungsoption. Taccolas *De ingeneis* (BSB Clm 197 II)
macht zugleich eine hydraulische Apparateschicht zeitgemäß. Gerade die
Konkurrenz dieser beiden historischen Mechanismen verlangt lokale Besitzer
statt einer erzwungenen Medizin- oder Technikübersetzung.

### f83r: Konnektivität bleibt, der große Kreislauf fällt

```text
F071–F098 (.3–.16)  -> linke Randfolge kleiner Figurenstationen
F099–F108 (.20–.24) -> linkes verbundenes Gefäß/Bogen/blaues-Kanal-Assembly
F109–F119 (.25–.28) -> UNRESOLVED zwischen den zwei unteren Assemblies
F120–F135 (.35–.54) -> rechtes Schalen/S-Rohr/blauer-Endknoten-Assembly
```

Die linke und rechte untere Konfiguration besitzen je echte lokale Konturen.
Zwischen ihnen fehlt aber jede Kontur. V71 behält daher lokale Verbindung,
verwirft Quelle, Senke, Richtung und ein seitenweites Rücklaufschema. Das ist
eine historische Manuskriptpraxis, die ein Schreiber um 1420 leicht lernen
konnte: Bildstation wählen, ihren Artikel/Abschnitt schreiben, stilles Objekt
aus der lokalen Station fortführen.

## Gearbeitete Astro-Spur

### f67r2: 7 und 12 bleiben Forminventare, nicht Namen

Die zwei Räder werden nicht wieder zu einer 7×12-Matrix zusammengedrückt.

- Loci .1–.12 besitzen je nur einen lokalen radialen Sektor-/Adressplatz
  (`DIRECT_VISIBLE`).
- Die sieben verstreuten Schlüssel-Loci .15/.22/.28/.31/.34/.37/.47 bleiben
  lediglich eine **siebenstellige Formkandidatur** (`INHERITED_VISIBLE`); alle
  Planetennamen und die Kreuzproduktannahme fallen.
- .52–.63 besitzen je einen äußeren Platz des rechten Rosettenrades; die alten
  Häusernamen fallen.
- .64–.71 erben nur das rote Außenband.
- .72–.74 besitzen nur die beiden Räder als Seitenkontext.
- Bei den übrigen .13–.51-Loci fehlt im erlaubten Freeze die sichere
  Quelllocus-zu-Rad-Seite-Zuordnung; sie sind ausdrücklich `UNRESOLVED`.

Or 5591 belegt als historischer Vergleich Urteile der sieben Planeten in zwölf
Zeichen. Das zeigt die Zeitgemäßheit der Relation, nicht ihre Anwesenheit oder
Benennung auf f67r2. Eine sichtbare Ringstelle darf daher bestehen, ohne zum
Planeten, Zeichen, Körperteil oder Tabellenwert zu werden.

### f68r1: der stärkste direkte Astro-Besitz

Die 28 Loci .9–.36 sind jeweils als lokale Sternstation oder kleiner
Sterncluster adressierbar (`DIRECT_VISIBLE`, Konfidenz 0.84). Beibehalten wird
nur diese räumliche Adressierung. Eingeführte Picatrix-Namen, Operationen,
Startpunkt und Route fallen. Loci .1–.7 gehören nur zum mehrteiligen Atlas;
.8 bleibt unter fünf Gesichtmedaillons ungelöst; .37 gehört lokal zum rechten
kreisförmigen Sternfeld.

### f69v: 28 sichtbare Plätze, keine 28 übersetzten Regeln

Loci .4–.31 werden auf die ungefähr 28 keulenendigen lokalen Plätze der linken
Rosette gebucht. Das ist die kleinste direkte Zuordnung und bewahrt den realen
Formbefund. Sie erzeugt **keine** Reihenfolge, keine günstige/ungünstige
Polarität und keine Bade-, Kräuter- oder Eingriffsregel. Die drei langen
Loci .1–.3 haben nur die drei getrennten Rosetten samt rechtem Prosablock als
Seitenbesitzer.

Add MS 25435 belegt 28 siderische Mondsegmente und ein I–XXVIII-Rad;
Add MS 82946 belegt die zeitnahe Nachbarschaft von Mondtafeln,
astrologischem Rad und medizinischen Figuren. Diese Quellen machen eine
28er-Radgattung möglich. Sie machen die Voynich-Plätze weder zu Mondhäusern
noch zu medizinischen Anweisungen.

## Historische Quellen (Gattungskalibrierung, keine Identifikation)

1. British Library, [Egerton MS 747](https://searcharchives.bl.uk/catalog/032-001983805), *Tractatus de herbis*, ca. 1280–1350.
2. British Library, [Egerton MS 2020](https://searcharchives.bl.uk/catalog/032-001982947), Carrara-Herbal, ca. 1390–1404.
3. Morgan Library, [MS G.74, f.23r](https://ica.themorgan.org/manuscript/page/22/77063), *De balneis Puteolanis*, ca. 1400.
4. Biblissima/BnF, [Latin 8161, f.23](https://portail.biblissima.fr/en/ark:/43093/ifdata38fe2523aff0ab85012f88057adb9c6897a121d1), Bad-/Beckenszene.
5. Biblioteca Angelica, [MS 1474](https://bibliotecaangelica.cultura.gov.it/de-balneis-puteolanis/), *De balneis Puteolanis*.
6. BSB/Biblissima, [Clm 197 II](https://iiif.biblissima.fr/collections/manifest/8c98cf397390b92a940c9651dfb9fbfa0546de5c), Taccola, *De ingeneis*, ca. 1427–1441.
7. British Library, [Add MS 82946](https://searcharchives.bl.uk/catalog/032-000200122), 1409–1431, Mondtafeln/astrologisches Rad/Zodiac Man.
8. British Library, [Add MS 25435](https://searcharchives.bl.uk/catalog/032-002029758), ca. 1345–1355, 28 siderische Segmente und Rad.
9. British Library, [Or 5591](https://searcharchives.bl.uk/catalog/040-003955407), ältere 7×12-Planet/Zeichen-Tradition, Abschrift 1462–1463.

## Reproduzierbarkeit und Grenze

`build_v71_r2_owner_ledger.py` erzeugt Ledger, Revisionsfamilien und
Build-Zusammenfassung deterministisch nur aus den zwei eingefrorenen
V69-Ledgern. `validate_v71_r2.py` bestätigt 277 eindeutige Einheiten, 381/395
Quellgruppen, die vier zulässigen Statusklassen und ausschließlich die zehn
festen Seiten. Keine Oberfläche, Kartenbedeutung, Stammdeutung oder
Klangähnlichkeit geht in die Zuordnung ein. Andere Manuskriptseiten,
Geschwister-V71 und versiegelte Daten wurden nicht geöffnet.

Die Obergrenze lautet:

> Ein Textfeld kann einen sichtbaren Artikel-, Stations- oder Adressbesitzer
> haben, ohne dass auch nur ein einziges seiner Schriftgebilde übersetzt ist.

