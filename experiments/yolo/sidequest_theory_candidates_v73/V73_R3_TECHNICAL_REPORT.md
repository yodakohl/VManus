# V73 R3 — nichtmedizinische Herbal-Drittedition

Status: kreative Zehnseiten-Werkstattedition, keine Entzifferung oder Übersetzung.

## Ergebnis

Die Edition belegt alle **100 Herbal-Ereignisse**, **20 Felder**, **19 Aussagen** und **5 Records** ohne Leerstelle. Sie liest die fünf Records als Pflanzenmaterial-Buchungen für Probenahme, Vorbereitung, Nassauszug, Fraktionsvergleich und Lagerung. Von den 100 Ereignissen sind 29 durch eine eingefrorene Karte/Formalklasse teilweise typisiert; 71 bleiben reine Exemplarwerte.

Jedes Bild besitzt weiterhin nur einen Ganzpflanzenartikel. Weder Texttasche noch Blatt, Wurzel oder Kopf wird zum eigenen Bildbesitzer. Wasser ist in mehreren Arbeitsdefaults ausdrücklich zugelassen, aber ebenso ausdrücklich **nicht abgebildet**.

## Unveränderter technischer Rollenstand

1. Die Gegenlesung denkt in Werkstattlisten, Abrechnungen, Maßen, Kalendern und Rezeptparametern.
2. Karten dienen als Adressen, Verweise, Slots, Abhängigkeiten und Abschlusszeichen.
3. Das Verfahren muss um 1420 handschriftlich ausführbar bleiben.
4. Seitenlayout, Renderer und gespeicherter Exemplarwert bleiben getrennt.
5. Eine brauchbare Lesung braucht eine ausführbare Regel, Beispielbuchungen und sichtbare Scheiterfälle.

## Ausführbare Quellenregel

```text
BEGIN_RECORD(record, WHOLE_PLANT_OWNER)
  ACTIVE = PREVIOUS = TARGET = MEASURE = UNSET
  FOR each frozen event in exact V69 order:
    emit exact tuple ID + opaque formula + known question-mark card/prompt
    obtain the unknown occurrence value from the workshop exemplar
    execute the occurrence-specific plant-work instruction
    update only the licensed local register effect
    CLOSE closes the local field, never proves a physical operation
  END
  clear all registers; no value passes to the next H-record
END_RECORD
```

`SELECT_PREVIOUS` therefore means previous **within the current record only**. `LINK_ACTIVE` joins bookkeeping state, not an invisible pictured pipe. A known card still receives a concrete source argument from the exemplar; an unknown event receives both its typed value and its concrete action there.

## Die fünf vollständigen Artikel

### H1 — Erste Nassprobe und Trockenreserve der f10r-Ganzpflanze

Erster Arbeitsartikel zur ganzen f10r-Pflanze. Eröffne ein frisches Los und nimm eine kleine unterirdische Probe. Bürste sie ab, spüle sie einmal, schneide sie klein und bedecke sie in einem Ziehgefäß mit sauberem Wasser. Prüfe einen kleinen Löffel des ersten Auszugs und trage das örtliche Maß ein; breite den unbenutzten Rest getrennt zum Trocknen aus. Fülle einen zweiten Auszugsposten ab, erwärme ihn sanft ohne Sieden, verknüpfe ihn nur innerhalb dieses Records mit dem aktiven nassen Ansatz und gieße ihn ab, sobald sich der örtliche Bereitschaftszustand zeigt.

Ablauf: `SAMPLING_WET_EXTRACTION_STORAGE > GENTLE_HEAT_SETTLE_DECANT`.

Stärkster medizinischer Rivale: Heilkundlicher Wurzel-Auszug mit Dosis und therapeutischem Gebrauch.

Härtester Widerspruch: Nur die ganze Pflanze ist sichtbar; Wurzelwahl, Wasser, Gefäß, Maß und Arbeitszweck sind unbebilderte Exemplarfüllungen.

### H2 — Press-, Wasch- und Fraktionsvergleich der f10r-Ganzpflanze

Zweiter, selbständiger Arbeitsartikel zur selben f10r-Bildpflanze. Beginne ein neues Los und wähle frisches oberirdisches Material. Quetsche und presse eine Handprobe, fange die Flüssigkeit getrennt auf, bemesse sie und behalte den Presskuchen. Wasche den Kuchen mit einer gleichen Wassermenge und stelle die vorige H2-Pressflüssigkeit daneben; beide gehören nur zum recordlokalen Vergleich, nicht zum alten H1-Los. Gib beiden gleiche Prüfmaße und notiere nach dem Stehen die klarere Fraktion. Seihe die Waschcharge, führe Flüssigkeit und Satz getrennt, spüle den Satz einmal nach, gieße die obere Flüssigkeit ab und trockne den verbleibenden Stoff als Referenz.

Ablauf: `FRESH_SAMPLE_PRESS_EXTRACTION > MATCHED_FRACTION_COMPARISON > SECOND_WASH_SETTLE_STORAGE`.

Stärkster medizinischer Rivale: Heilkundliche Presssaftbereitung aus oberirdischen Pflanzenteilen.

Härtester Widerspruch: Die zweite Recordgrenze ist formal, aber Pressen, Fraktionen, Vergleich und Klarheitsbeobachtung sind weder Bild- noch Kartenwerte.

### H3 — Klär-, Tuch- und Warmprobe der f11r-Ganzpflanze

Arbeitsartikel zur ganzen f11r-Pflanze. Nimm eine kleine unterirdische Probe, zerkleinere und presse sie durch ein grobes Tuch und seihe die Flüssigkeit danach durch ein feines. Nimm sie am örtlichen Klarheitszeichen an und lasse sie bedeckt abkühlen; bewahre außerdem eine trockene Kopf- oder Blütenprobe als Referenz auf. Tränke einen sauberen Tuchstreifen mit einem gemessenen Flüssigkeitsanteil und vergleiche ihn auf neutraler Unterlage mit einem trockenen Streifen. Erweiche schließlich eine Blattprobe im warmen Wasserbad, zerstoße sie, nimm sie am Bereitschaftszeichen in den Vergleich und notiere ihre Beschaffenheit.

Ablauf: `DOUBLE_FILTRATION_CLARIFICATION > DRY_REFERENCE_STORAGE > WET_DRY_MATERIAL_COMPARISON > WARM_SOFTENING_TEXTURE_TEST`.

Stärkster medizinischer Rivale: Heilkundlicher geklärter Auszug plus äußerliche Auflage.

Härtester Widerspruch: Tücher, Wasserbad, Prüfunterlage und jahreszeitliche Entnahme sind nicht gezeichnet; selbst KLAR? bleibt nur Fragezeichen-Mnemonic.

### H4 — Parallele Wasserfraktionen der f55v-Ganzpflanze

Arbeitsartikel zur ganzen f55v-Pflanze. Eröffne einen Standardslot, bemesse eine Blattprobe, schneide sie in Streifen und lasse sie bedeckt in Wasser ziehen. Teile die Flüssigkeit gleich; rühre und filtere die erste Fraktion, während die zweite in eigenem Gefäß mit frischem Wasser bei mäßiger Wärme dieselbe Zeit steht. Bemesse beide Fraktionen erneut, setze einen lokalen Vergleichsslot und vereinige gleich große Teilproben. Führe diese Mischung als aktiven H4-Ansatz, lagere den Rest bedeckt und verbrauche die frische Probe zeitnah für eine Materialwäsche. Die groteske Wurzelform liefert dabei keinen eigenen Arbeitsposten.

Ablauf: `MEASURED_WATER_STEEP > FIRST_FRACTION_FILTER_TEST > SECOND_FRACTION_WARM_CONTROL > FRACTION_COMBINATION_AND_STORAGE`.

Stärkster medizinischer Rivale: Heilkundliche Blattabkochung oder Waschung.

Härtester Widerspruch: Die Texttaschen beweisen keine Pflanzenpartien; Wassergefäße und parallele Fraktionen sind vollständig unbebildert.

### H5 — Standort-, Nass- und Trockenvergleich der f56r-Ganzpflanze

Arbeitsartikel zur ganzen f56r-Pflanze. Eröffne ein saisonales Los, schneide und quetsche eine kleine unterirdische Probe, bemesse sie und lasse sie kalt in sauberem Wasser ziehen. Filtere den Auszug, prüfe eine gleiche Kleinmenge auf neutralem Tuch und weise sie einem recordlokalen Musterposten zu. Nimm ein zweites Los von einem feuchteren oder schattigeren Standort, prüfe denselben Anteil und trockne seinen Rückstand offen. Trenne außerdem einen reifen Kopf als Trockenmuster, löse feines Material auf ein Tuch aus und lagere es im Schatten. Stelle dem frischen Ansatz eine trockene Kontrollprobe gegenüber. Befeuchte einen weiteren bezeichneten Posten, vermenge ihn zur frischen Materialprobe und gebrauche ihn sofort; schließe mit dem abgemessenen hellen oder geöffneten Kopfteil.

Ablauf: `SEASONAL_SAMPLE_MEASURE > COLD_WATER_EXTRACTION_TEST > SITE_LOT_COMPARISON > HEAD_SAMPLE_DRY_STORAGE > FRESH_VERSUS_DRY_CONTROL > WET_BINDING_MATERIAL_TEST > DESIGNATED_PART_END_MEASURE`.

Stärkster medizinischer Rivale: Heilkundliche saisonale Sammlung, Auflage und Dosis.

Härtester Widerspruch: Mehrere Köpfe beweisen weder Reifestufen noch Samen; Standort, Wasser, Kontrollprobe und Bindemittel sind kreative Quellenargumente.

## Was diese Fassung gewinnt

- Sie gibt jedem der 100 Ereignisse eine kleine, ausführbare Defaultrolle.
- Sie braucht keine Pflanzenart und keine neu erfundene Wortwurzel.
- Sie nutzt Wasser nur dort, wo ein Nassprozess den Record tatsächlich zusammenhängender macht.
- H1/H2 werden trotz gleicher Bildpflanze als getrennte Lose geführt; `VORIGES?` greift nicht über die Recordgrenze.
- f55v-Texttaschen bleiben Restflächen um eine ganze Pflanze und werden nicht zu Blatt-/Wurzelrubriken.

## Was sie nicht gewinnt

Der Großteil der konkreten Handlung ist nicht im Formsystem erkannt: 71 Ereignisse sind vollkommen exemplarabhängig, und auch die 29 typisierten Ereignisse tragen nur Fragezeichen-Mnemonics oder Formalprompts. Kein Bild zeigt Wasser, Gefäß, Tuch, Mörser, Maß, Vergleichsbrett oder Lagerbehälter. Die technische Lesung ist deshalb eine kohärente nichtmedizinische Gegenfüllung derselben offenen Slots, keine bessere historische Übersetzung als der medizinische Rivale.

Keine Karte, kein Stamm, kein Laut, keine Art und kein Klartext wurde neu bestätigt. f84 und f84r wurden nicht geöffnet.
