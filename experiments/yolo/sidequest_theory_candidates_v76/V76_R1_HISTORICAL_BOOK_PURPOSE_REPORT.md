# V76 R1 — Wettbewerb zweier Buchzwecke um 1420

## Auswahl

Die stärkste zusammenhängende Arbeitstheorie ist ein **bildgeführtes Praxis-, Bade- und himmlisches Wahlkompendium für eine kleine Heil-/Haus-/Badewerkstatt**:

```text
unbenannte Bildpflanze
  → occurrence-gebundener Stoff-/Zubereitungsartikel
  → lokale Bade-, Wasch-, Auflage- oder Apparatekonfiguration
  → getrennt konsultierte Himmels-/Kalenderbedingung
```

Diese Folge ist eine thematische Buchklammer, kein nachgewiesener Ausführungsalgorithmus. Es gibt keinen sichtbaren Pointer von einem Herbal-Artikel zu einer Biological-Station oder einem Astro-Locus. Der Benutzer wählt vielmehr in drei getrennten Quellenlagen Material, örtliche Anwendungskonfiguration und gegebenenfalls einen himmlischen/kalendarischen Beratungsrahmen.

Der stärkste **wirklich andere** Rivale ist ein **Naturalia-Kosmographie-Muster- und Merkbuch einer Schreib-/Bildwerkstatt**. Darin sind die Pflanzen Bildexemplare mit Materialnotizen, die Biological-Seiten Figuren-/Gefäß-/Band- und Apparatevarianten, und die Astro-Seiten astronomisch-kosmographische Lehr- oder Kopierdiagramme. Sein Hauptnutzer ist nicht der Behandler, sondern der Schreiber, Zeichner oder Schüler, der Formen, Besitzer und lokale Legenden reproduziert.

Der eingefrorene kreative Score ist knapp: Lead 96/108, Rivale 92/108. Das ist keine Statistik und verwirft den Rivalen nicht. Der Lead gewinnt nur, weil er die konkreten V73–V75-Arbeitslesungen besser zu einer praktischen Dreiteilung verbindet; der Rivale erklärt Bildpriorität, fehlende Crosspointer und heterogene Quellen mindestens ebenso gut.

## Unveränderter R1-Hintergrund

1. Du bildest mehrere Schreiber aus, die dasselbe praktische Buch zuverlässig fortsetzen müssen.
2. Du denkst in vorzeigbaren Exemplaren, häufigen Ganzkarten, einfachen Regeln und prüfbaren Abschreibeschritten.
3. Du fragst bei jeder Theorie, wie ein Lehrling sie lernt, ausführt, korrigiert und an eine zweite Hand weitergibt.
4. Du bevorzugst keine Sprache oder Bedeutung, sondern den kleinsten praktisch lehrbaren Produktionsablauf.
5. Du lieferst eine konkrete Schreibanweisung, eine Rücklesung und die Fehler, die ein echter Lehrling machen würde.

## Vollständige Bindung statt Neuübersetzung

V76 übersetzt keine der 776 Gruppen neu. Die 14 Einheiten werden durch Dateipfad, Einheitselektor und SHA-256 an die zentral ausgewählten V73–V75-Detailausgaben gebunden:

| Einheit | Seite | Gruppen | ausgewählte Bindung | Lead-Rolle | Rivalen-Rolle |
|---|---|---:|---|---|---|
| H1 | f10r | 14 | V73 Herbal-Record | erster Pflanzenmaterial-/Zubereitungsartikel | Pflanzenexemplar/Materialprozess |
| H2 | f10r | 24 | V73 Herbal-Record | zweiter Fraktions-/Zubereitungsartikel | Pflanzenexemplar/Materialprozess |
| H3 | f11r | 17 | V73 Herbal-Record | Blüten-/Blatt-Auszugartikel | Pflanzenexemplar/Materialprozess |
| H4 | f55v | 18 | V73 Herbal-Record | Blatt-/Wasch-/Auflageartikel | Pflanzenexemplar/Materialprozess |
| H5 | f56r | 27 | V73 Herbal-Record | Frisch-/Trockenpflanzenartikel | Pflanzenexemplar/Materialprozess |
| B1 | f81v | 66 | V74 Stationsrecord | gemeinsames lokales Bade-/Waschfeld | Figurenpool-/Stationsmuster |
| B2 | f82r | 62 | V74 Stationsrecord | fünf getrennte Bade-/Apparatestationen | Badehaus-/Apparatevarianten |
| B3 | f83r | 86 | V74 Stationsrecord | Randstationen, Lücke, Hauptpaar | Gefäß-/Bogen-/Figurenmuster |
| B4 | f83r | 47 | V74 Stationsrecord | Hauptpaar plus zwei getrennte Endposten | lokale Apparate-/Bildvarianten |
| B5 | f83r | 11 | V74 Stationsrecord | linker eigenständiger Nachtrag | linker Musterposten |
| B6 | f83r | 9 | V74 Stationsrecord | rechter eigenständiger Nachtrag | rechter Musterposten |
| A1 | f67r2 | 190 | V75 Instrument | zwei getrennte Himmelsräder | astronomisches Lehr-/Kopierdiagramm |
| A2 | f68r1 | 65 | V75 Instrument | mehrpaneeliger Sternatlas | mehrere unabhängige Stern-/Gesichtsfelder |
| A3 | f69v | 140 | V75 Instrument | drei getrennte Räder, 28 Plätze nur links | drei Formal-/Kalender-/Kosmographieräder |
| **Summe** | **10 Seiten** | **776** | **100 + 281 + 395** |  |  |

Die vollständige maschinenlesbare Zweckbindung steht in `V76_R1_14_UNIT_PURPOSE_MATRIX.tsv`. Sie enthält keine Oberfläche und keine zeilenweise deutsche Neudeutung.

## Lead: Praxis-, Bade- und Wahlkompendium

### Praktischer Gebrauch

Das Buch dient einem unterrichteten Praktiker, Bad-/Heilgehilfen oder Nutzer eines gelehrten Haushalts beziehungsweise Infirmariums. Es ist kein autonomes Lesebuch. Der Benutzer kennt die Bildbesitzer und hat Zugang zu einem ausgeschriebenen oder mündlich vermittelten Masterexemplar.

- Im Herbal-Teil findet er unter einer unbenannten Ganzpflanze einen lokalen Stoff-/Zubereitungsartikel.
- Im Biological-Teil wählt er eine örtliche Bade-, Wasch-, Auflage- oder Apparatekonfiguration; jede Bildlücke löscht Stoff, Ziel und Richtung.
- Im Astro-Teil konsultiert er genau ein lokales Rad, Paneel oder Sternfeld als möglichen Zeit-, Zustands- oder Wahlrahmen; kein Wert wandert zwischen Instrumenten.

Das ist keine moderne Datenbank. Es ist ein bildadressiertes Arbeitsbuch: Der Bildort liefert das ausgesparte Subjekt oder die Nachschlageadresse, während seltene occurrence-Werte aus der Werkstattvorlage kommen.

### Kompilation und Quellenfolge

Am einfachsten ist keine einzige Urfassung, sondern die Zusammenführung dreier bereits verschieden organisierter Vorlagenhefte:

1. ein Herbal-/Receptarium-Heft mit Ganzpflanzenartikeln;
2. ein balneologisches oder lokales Stationsheft mit Figuren, Becken und Apparatformen;
3. ein astronomisch-kalendarisches Tafelheft mit mehreren lokalen Instrumenten.

Die konzeptuelle Reihenfolge `Material → Anwendung → Bedingung` erklärt die Koexistenz, aber nicht zwingend die physische Binde- oder Entstehungsreihenfolge des ganzen Manuskripts. Aus den zehn Seiten lässt sich diese nicht rekonstruieren. Die fehlenden Crosspointer sprechen dafür, dass die drei Quellenlagen thematisch zusammengestellt und nicht als ein einziges integriertes Verfahren neu geschrieben wurden.

### Bild zuerst, Text danach

Der Meister oder Zeichner disponiert zuerst Ganzpflanze, Stationskonturen beziehungsweise Rad/Panellayout. Danach setzt der Schreiber den Text in die verfügbaren Restflächen und bindet jede Folge an den kleinsten sichtbaren Besitzer. Diese Produktionsfolge erklärt unregelmäßigen Reflow und lokale Textformen, beweist aber den medizinischen Zweck nicht: Auch der Rivale benutzt sie.

### Mehrere Schreiber

Mehrere Hände müssen nicht dasselbe Klartextlexikon teilen. Jeder lernt eine lokale Abschnittsschablone:

- Herbal: Ganzpflanzenbesitzer + Artikelabfolge;
- Biological: kleinste Station + Kontakt-/Resetregel;
- Astro: Instrumentnamensraum + lokales Etikett + Orientierungsverbot.

Ein Korrektor prüft Bildbesitzer, Gruppenfolge, Abschluss und Reset. Damit ist Arbeitsteilung plausibel, ohne die Hände als Arzt, Bademeister oder Astronom identifizieren zu müssen.

### Masterexemplar

Das Masterexemplar ist unter dem Lead keine elegante Entzifferung, sondern die größte methodische Kostenstelle. Es liefert Pflanzenanteil, Medium, Anwendung, Stationshandlung oder Himmelswert, die aus der sichtbaren Form nicht rückgewonnen werden können. Dadurch wird das Buch für Eingeweihte praktisch, für Außenstehende aber semantisch unterbestimmt. Das Modell darf diese Abhängigkeit nicht als Beweis verwenden.

### Was ein Lehrling lernt

1. Abschnitt und Bildbesitzer ausrufen.
2. Die komplette opake Folge ohne Wortzerlegung kopieren.
3. Den occurrence-Wert nur aus dem richtigen lokalen Exemplar einsetzen.
4. Am Pflanzenrecord, an der Biological-Bildlücke und am Astro-Rad/Panellwechsel jedes lokale Register zurücksetzen.
5. Niemals aus gleicher Form einen gleichen deutschen Wert erzwingen.
6. Niemals eine konkrete Arbeitsphrase als Wörterbuchwort lehren.

## Rivale: Naturalia-Kosmographie-Muster- und Merkbuch

### Praktischer Gebrauch

Der Rivale ist ebenfalls praktisch, aber anders: Er dient dem Kopieren, Lehren, Wiedererkennen und Variieren bildlicher sowie diagrammatischer Formen. Sein Benutzer ist ein Schreiber, Zeichner oder Schüler einer gelehrten Werkstatt.

- Die Herbal-Seiten liefern vier Pflanzenmodelle und lokale Material-/Kopiernotizen.
- Die Biological-Seiten liefern Figuren-, Gefäß-, Bogen-, Band- und Apparatekonfigurationen als lokale Musterstationen.
- Die Astro-Seiten liefern Räder, Sternfelder, Zentren und Ringlegenden als Kosmographie-/Astronomie-Merkbilder.

Der Rivale muss weder Patient, Krankheit, Arznei noch günstige Behandlung behaupten. Er ist darum weniger belastet durch die vielen unbebilderten V73/V74-Nomen. Dafür erklärt er die überraschend konkreten occurrence-gebundenen Arbeitsabfolgen nur als exemplarische Lernfüllungen und besitzt eine schwächere inhaltliche Klammer.

### Kompilation und Nutzer

Die drei Quellenbestände werden nach Bildgattung gesammelt: Naturalia, Körper-/Apparatfiguren und Kosmographie. Bilder werden zuerst angelegt, lokale Legenden danach eingepasst; verschiedene Spezialisten kopieren je ihren Formenbestand. Das Masterexemplar ist eine Bild-/Legenden-Vorlage, nicht notwendig ein medizinisches Klartextbuch.

Warum die Sektionen koexistieren: Sie bilden einen gelehrten visuellen Repertoriumsbogen von Pflanze über verkörperte oder apparative Naturprozesse bis zum Himmel. Diese Klammer ist breit, aber für mittelalterliche Miscellanea und Werkstattbücher einfacher als eine erfundene direkte Behandlungskette.

### Was ein Lehrling lernt

Er zeigt Typ, Besitzer und Variante, kopiert die vollständige lokale Legende und kann ein Blatt reproduzieren, ohne dessen externe Referenten sicher zu benennen. Das erklärt die Übertragbarkeit zwischen Händen besonders gut. Es lässt aber offen, warum einige Abschnitte so stark wie Gebrauchs- und Stationsartikel organisiert sind.

## Direkter Vergleich

| Kriterium | Gewicht | Lead | Rivale | Urteil |
|---|---:|---:|---:|---|
| Fit zu V73–V75 | 3 | 4 | 3 | Lead übernimmt die konkreten Inhaltseditionen direkt |
| praktische Kohärenz | 3 | 4 | 2 | Material–Anwendung–Bedingung ist die engere Klammer |
| Bild-zuerst-Produktion | 3 | 3 | 4 | Musterbuch erklärt Bildpriorität am unmittelbarsten |
| mehrere Schreiber | 2 | 4 | 4 | lokale Schablonen passen zu beiden |
| Masterexemplar | 3 | 4 | 4 | beide brauchen eine externe lokale Vorlage |
| Nutzer um 1420 | 2 | 3 | 3 | beide Werkstattmilieus sind möglich |
| Koexistenz der Sektionen | 3 | 4 | 3 | Lead enger; Rivale breiter |
| fehlende Crosspointer | 3 | 3 | 4 | Miscellaneum erwartet Unverbundenheit eher |
| Codebuchgrenze | 3 | 4 | 4 | beide benötigen null portable Glossen |
| Widerspruchslast | 2 | 2 | 3 | Lead ergänzt mehr ungesehene Inhalte |
| **Gewichtete Summe** | **27** | **96/108** | **92/108** | **Lead knapp; Rivale bleibt live** |

Die Punktwerte sind nur eine festgehaltene kreative Vergleichsdisziplin. Sie sind weder Wahrscheinlichkeit noch historische Evidenz.

## Zentrale Widersprüche

Der vollständige Ledger enthält 16 Einträge. Die entscheidenden sind:

- 71/100 Herbal-Ereignisse und 191/281 Biological-Ereignisse erhalten ihren konkreten Inhalt nur aus dem angenommenen Exemplar.
- Keine Pflanzenart, Dosis, Indikation oder Himmelsbezeichnung ist identifiziert.
- Biological besitzt keinen globalen Stoff- oder Flussplan; 32 Ereignisse bleiben an ungelösten Besitzern.
- f67r2 ist keine 7×12-Matrix, f68r1 kein einziges Zentrum-plus-28-Rad, f69v keine gemeinsame geordnete 28-Regelfolge.
- Start, Richtung, Rotation, f68↔f69-Key und Crosssection-Pointer fehlen.
- Bild-zuerst erklärt die Herstellung, nicht den Zweck.
- Mehrere Hände erklären Arbeitsteilung, nicht automatisch Wissensrollen.
- Das verlorene Masterexemplar kann zu viel aufnehmen; seine hohe Erklärungskapazität bleibt eine offene Kostenstelle.
- Die vollständige 776-Gruppen-Bindung ist keine neue Inhaltsbestätigung.

## Harte Codebuch- und Wörterbuchgrenze

Für V76 wurde keine gewünschte historische Wortliste gesucht. Es liegt keine einzige qualifizierende Codebuch-/Nomenclator-Attestation vor. Daher gilt für jede geerbte kleine Karten- oder Formalglosse:

`PROVISIONAL_UNATTESTED_MNEMONIC_OR_FORMAL_LABEL_NOT_WORD`

Occurrence-gebundene Wörter wie Pflanzenteil, Bad, Wärme, Auflage, Stern, Sektor oder Bedingung dürfen die kreative V73–V75-Quellwelt beschreiben. Sie werden dadurch nicht zu Voynich-Wörterbuchwörtern. Bestätigte portable Wörter, Stämme, Laute, Sprachwerte und Klartextklauseln bleiben null.

## Werkstatturteil

Für eine kleine Schreibwerkstatt um 1420 ist der Lead knapp am einfachsten lehrbar: Drei spezialisierte Vorlagenhefte werden bildgeführt zusammengetragen; ein Praktiker oder Gehilfe schlägt unter Bildbesitzern Material-, Stations- und Himmelsbedingungen nach; jeder Schreiber lernt nur die lokale Produktionsschablone. Der Rivale bleibt jedoch beinahe gleich stark, weil er genau dieselbe Produktion ohne die große medizinische Exemplarfüllung erklärt.

Die sicherste gemeinsame Aussage beider Modelle ist deshalb kleiner als ihr Zweckstreit:

> Ein bildgeführtes, aus mehreren lokalen Vorlagentraditionen kompiliertes Werk konnte von mehreren Schreibern über sichtbare Besitzer, vollständige opake Folgen und ein Masterexemplar zuverlässig fortgesetzt werden.

Ob die gespeicherten occurrence-Werte reale Therapie, Badehausbetrieb, astronomische Konsultation oder vor allem Werkstattgedächtnis waren, bleibt offen.

## Artefakte und Prüfung

- `V76_R1_14_UNIT_PURPOSE_MATRIX.tsv` — 14 Einheiten, 776 gebundene Gruppen
- `V76_R1_PRODUCTION_WORKFLOW.tsv` — 12 Produktions- und Lehrschritte
- `V76_R1_COMPETITION_SCORECARD.tsv` — 10 feste Kriterien plus Summe
- `V76_R1_CONTRADICTION_LEDGER.tsv` — 16 offene, begrenzte oder harte Widersprüche
- `V76_R1_build_book_purpose_competition.py` — deterministischer Builder
- `V76_R1_validate_book_purpose_competition.py` — Bindungs-, Scope- und Codebuchvalidator
- `V76_R1_BUILD_SUMMARY.json` — Buildzählung
- `V76_R1_VALIDATION.json` — `PASS`

Der Validator prüft die exakten 14 IDs, zehn Seiten, 100+281+395=776 Detailbindungen, Quellhashes, alle Workflow- und Scorezeilen, den genuinely-different Rivalen, die 16 Widersprüche, null Codebuchattestationen und die vollständige Abwesenheit einer Wörterbuchpromotion.
