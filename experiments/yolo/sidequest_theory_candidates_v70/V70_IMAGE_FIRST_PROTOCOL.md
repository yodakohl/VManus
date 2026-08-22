# V70 — bildzentrierte Revisionsrunde

Status: vom Benutzer ausdrücklich nach V69 autorisierte einzelne neue
Sidequest-Runde; keine wissenschaftliche Entzifferung.

## Ziel

Die zehn V69-Seiten werden diesmal direkt aus den hochauflösenden
Faksimilebildern beschrieben. Erst wird festgehalten, was sichtbar ist; danach
werden iatromedizinische und praktisch-technische Lesung damit konfrontiert.

## Festes Bildpaket

Nur die zehn Dateien in `V70_IMAGE_MANIFEST.tsv` dürfen geöffnet werden:

- Herbal: f10r, f11r, f55v, f56r;
- Biological: f81v, f82r, f83r;
- Astro: f67r2, f68r1, f69v.

Keine andere Manuskriptseite darf angesehen werden. Insbesondere bleiben f84
und f84r versiegelt. Die Faksimile-JPEGs werden nicht ins Repository kopiert;
Hash und Abmessung binden die tatsächlich betrachteten Bytes.

## Reihenfolge pro Seite

1. **Sichtinventar vor Bedeutung:** Figuren, Pflanzenpartien, Farben,
   Behälter, Röhren, Bögen, Auslässe, Sterne, Kreise, Trennlinien,
   Beschädigungen und leere Flächen neutral aufzählen.
2. **Geometrie:** Welche Dinge berühren oder verbinden sich tatsächlich?
   Welche liegen nur nahe beieinander? Wo endet eine Linie sichtbar?
3. **Produktionsindizien:** Text umgeht Bild, überlagert Kontur, wird von
   Kontur unterbrochen oder nutzt Restflächen. Bild-zuerst bleibt der Default,
   wenn bloße Platzanpassung genügt.
4. **Bildbesitzer:** höchstens sichtbare Besitzerklassen vergeben, etwa
   `WHOLE_PLANT`, `ROOT`, `POOL`, `FIGURE`, `CONDUIT`, `STAR_STATION` oder
   `DIAGRAM_SECTOR`; keine Pflanze, Krankheit oder Operation benennen.
5. **Erst danach Lesungsdruck:** Für jede V69-Inhaltsannahme `SUPPORTS`,
   `COMPATIBLE`, `STRAINS` oder `CONTRADICTS` vergeben und das genaue
   Bilddetail nennen.
6. **Konkrete Revision:** Mindestens eine bisherige Lesung präzisieren,
   zurücknehmen oder durch eine bildnähere Alternative ersetzen.

## Verbotene Abkürzungen

- Keine Textbedeutung aus räumlicher Nähe allein.
- Keine unsichtbare Flüssigkeit, Strömungsrichtung oder Körperöffnung
  ergänzen, wenn Kontur/Farbe sie nicht zeigt.
- Nacktheit beweist Bad/Medizin nicht; Röhren beweisen Wasserwerk nicht;
  Sterne beweisen keine bestimmte astronomische Liste.
- Farbe kann Material, spätere Kolorierung oder reine Unterscheidung sein.
- Text wurde nach den Bildern eingepasst; unregelmäßiger Umbruch ist daher
  zunächst Platzfolge, nicht Semantik.
- Keine automatische Bilderkennung, OCR oder externe Bildklassifikation.
- Keine neue Karten- oder Stammbedeutung allein aus dem Bild.

## Vier unabhängige Perspektiven

- R1 Werkstattlehrmeister: Zeichenablauf, Seiteneinteilung, Kopierbarkeit,
  sichtbare Besitzer und Lehrregeln über alle zehn Seiten.
- R2 historischer Fachschreiber: Herbal/Bio-Ikonographie und zeitnahe
  Vergleichspraxis; Astro nur als Gattungscheck.
- R3 technischer Zeichner: reale versus schematische Verbindungen, Behälter,
  Strömungsoptionen, Diagrammgeometrie und technische Gegenlesung.
- R4 Kanzleikorrektor: unabhängiger Gesamtcensus, Platz-/Reflow-Erklärung,
  Ambiguitäten und abschließende Auswahl.

Keine Rolle liest vor ihrem eigenen Freeze die Ergebnisse einer anderen.

## Geforderte Ausgabe

Jede Rolle liefert:

- eine Zeile pro Seite mit neutralem Sichtinventar;
- eine Tabelle der wichtigsten lokalen Bildobjekte und ihrer tatsächlichen
  Verbindungen;
- eine V69-Annahmenmatrix;
- mindestens eine vollständige, bildrevidierte Passage oder Einheit;
- stärkste positive Lesung, stärksten Rivalen und härtesten Widerspruch.

Die zentrale Auswahl darf eine konkrete Lesung explorativ behalten. Sie muss
nicht bewiesen sein; sie fällt erst, wenn das Bild sie ausschließt oder eine
sichtbar einfachere Alternative sie ersetzt.

## Stopp

V70 ist genau eine Bildrunde. Sie eröffnet keine weitere Runde automatisch.
