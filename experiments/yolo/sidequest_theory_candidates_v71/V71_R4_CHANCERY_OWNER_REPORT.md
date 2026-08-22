# V71 R4 — skeptische Bildbesitzerkarte

Status: unabhängige kreative Kanzleilesung, keine Übersetzung.

## Entscheidung

Die Bilder können auf allen 277 verlangten Einheiten einen **Adressrahmen**
bereitstellen, aber nur selten einen exakten referentiellen Ausdruck. Die
sinnvollste Regel für einen Schreiber um 1420 ist:

1. Beginne einen Artikel oder eine Stationszone mit dem lokal sichtbaren
   Bildbesitzer.
2. Trage ihn ohne Wiederholung über folgende Felder weiter.
3. Setze ihn beim Wechsel in eine unverbundene Bildzone neu.
4. Binde einen Text nur dann direkt an ein Objekt, wenn er in dessen gezeichnetem
   Slot liegt; bloße Nähe bleibt `PAGE_OWNER_ONLY`.
5. Kopiere den konkreten seltenen Wert aus dem Exemplar, statt ihn aus dem Bild
   oder aus Kartenbestandteilen zu erraten.

Das ergibt eine vollständige, aber bewusst asymmetrische Karte:

- Herbal und die meisten Bio-Felder besitzen vererbte Artikel-/Zonenbesitzer;
- einzelne Astro-Slots besitzen direkte sichtbare Adressen;
- konkrete Operation, Substanz, Körperteil oder Himmelsname bleibt im
  Exemplar.

## Vollständige Beispielspuren

### Herbal f10r

`F001` initialisiert den sichtbaren Besitzer als die **unbekannte abgebildete
gezähnte blau blühende Pflanze**. `F002` erbt denselben Besitzer. `F003`
beginnt den zweiten recordlokalen Artikelabschnitt unter demselben Seitenbild;
`F004–F005` tragen ihn weiter. Wasser darf als konkrete kreative Quellenfüllung
in einem Feld stehen, ist aber nicht Teil des sichtbaren Besitzers.

### Biological f82r

`F045–F052` gehören zur oberen Figuren-/Zylinderzone. `F053–F056` wechseln zu
lokalen mittleren Geräten. `F057–F061` gehören zur liegenden oder mittleren
Anwendungsstation; `F062–F070` zum unteren gemeinsamen Figurenfeld. Diese vier
Blöcke dürfen nacheinander gelesen werden, aber keine unsichtbare Leitung macht
sie zu einem einzigen Kreislauf.

### Astro f69v

`f69v.1`, `.2` und `.3` werden getrennt dem linken, mittleren und rechten Rad
beziehungsweise dessen Prosafeld zugeordnet. Die 28 singletonartigen Loci
`.4–.31` dürfen als lokale Plätze des ungefähr 28-speichigen linken Rades
gelesen werden. Sie erhalten die anonymen Defaults `left-wheel radial place
01–28`; nicht Tagesname, Mondhaus, Regel oder Laufrichtung.

## Stärkster positiver Gewinn

V70s Bildkorrektur lässt sich als einfache Werkstattpraxis ausführen:
`VISIBLE_OWNER -> INHERITED_OWNER -> LOCAL_EXEMPLAR_VALUE`. Damit kann ein
Schreiber elliptisch bleiben, ohne dass jede Karte selbst einen Gegenstand
benennen muss.

## Stärkster Rivale

Die gleiche Verteilung entsteht, wenn Bilder und Text nur gemeinsam aus einem
Layout-Exemplar kopiert wurden und grammatisch überhaupt kein stiller Besitzer
existiert. Besonders Herbal besitzt keine Leader-Linie von Feld zu Pflanzenteil.
Darum lautet `PAGE_OWNER_ONLY` nicht `REFERENT_PROVEN`.

## Härtester Widerspruch

Bei f82r und f83r fehlt für viele Textinseln die eindeutige lokale Bildbindung.
Die Zonenkarte ist eine lesbare Redaktionsentscheidung, keine wiedergewonnene
Autorenreferenz. Ein einziges Feld kann weiterhin das Bild, den vorherigen Satz
oder einen ungemalten exemplarischen Gegenstand meinen.

Die vollständige Tabelle `V71_R4_OWNER_LEDGER.tsv` enthält 135 Prosa-Felder und
142 Astro-Loci. Es wurde keine Karten-, Stamm-, Wort- oder Lautbedeutung
hinzugefügt; f84 und f84r blieben versiegelt.
