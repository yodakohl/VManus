# V66 R2 — historische Astro-/Iatromathematik-Zweitausgabe

## Urteil

**KEEP, aber als drei selbständige Instrumente ohne sichtbaren Seitenjoin.**

```text
f67r2 = 7 Planeten × 12 Zeichen/Körperbezirke
         + lokales zweites 12er-Inventar
         + 8 Wahlbedingungen

f68r1 = Zentrum + 28 räumliche Mondhausadressen

f69v  = unabhängige Folge aus 28 medizinischen Wahlregeln

f68r1 ↔ f69v = NONE
```

Das ist eine vollständige kreative Quellenausgabe, keine Entzifferung. Alle
395 ZL3b-Gruppen erhalten einen konkreten Default, doch stets als Fragment
eines **locusgebundenen lokalen Exemplars**. Kein Gruppenbild erhält ein Wort,
keine Lautung und keinen registerübergreifenden Kartenwert. Planet-, Zeichen-,
Haus- und Mondstationsnamen sind ausdrücklich externe Editionslabels.

## Vollständige Ausgabe

| Blatt | Loci | Gruppen | gewähltes System | Confidence |
|---|---:|---:|---|---:|
| f67r2 | 74 | 190 | 7 Planeten × 12 Zeichen/Körpersektoren, ergänzt um 12 Häuser und 8 Wahlchecks | .46 |
| f68r1 | 37 | 65 | räumlicher Mondhauskatalog: Zentrum + 28 Stellen | .40 |
| f69v | 31 | 140 | 3 Rubriken + 28 unabhängige medizinische Wahlregeln | .36 |
| **gesamt** | **142** | **395** | vollständig | — |

Die vollständigen Ebenen sind:

- `V66_R2_395_GROUP_ASTRO_INTERLINEAR.tsv`: jede sichtbare Gruppe in
  unveränderter Reihenfolge, mit lokalem Textfragment und explizitem
  `KEINE KARTENGLOSSE`;
- `V66_R2_142_LOCUS_EDITIONS.tsv`: vollständiger Quelltext jedes Locus;
- `V66_R2_THREE_DIAGRAM_EDITIONS.tsv`: lesbare Gesamtedition der drei Blätter;
- `V66_R2_HISTORICAL_SOURCES.tsv`: acht historische Vergleichsquellen mit
  Reichweite und Gegenbeleg.

## f67r2 — planetarisch-zodiakaler Wahlrahmen

Die stärkste vollständige Lesung ist keine ausgeschriebene 7×12-Matrix,
sondern ein **mehrstufiger Selektor**. Der Benutzer bestimmt Tages- oder
Stundenherrn, den Mond im Tierkreiszeichen und den diesem Zeichen zugeordneten
Körperbezirk. Danach rahmt er die Frage mit dem zweiten Zwölferinventar und
prüft acht Wahlbedingungen: insbesondere Saturn, Mars, Sonnenverbrennung,
Trennung von einem Übeltäter und Verbindung mit einem Wohltäter. Das Ergebnis
erlaubt, mildert oder verschiebt einen Eingriff, dessen Diagnose, Arznei und
Dosis aus einem anderen Rezept oder aus dem Fall stammen.

Als lokale Vergleichsfolge setzt die Ausgabe die sieben Planeten in der
Reihenfolge Saturn, Jupiter, Mars, Sonne, Venus, Merkur, Mond und die zwölf
Zeichen Widder bis Fische mit der Kopf-bis-Fuß-*melothesia*. Das zweite
Zwölferinventar wird kreativ als Häuserreihe gelesen; Haus I bezeichnet den
Kranken, VI die Krankheit, VII Arzt/Gegenpartei und X Behandlung/Meister. Diese
Namen sind keine Lesung der Oberflächen.

Das passt zur realen Werkstattpraxis auffallend gut. Wellcome MS.8515, um 1425,
enthält die sieben bekannten Planeten und anschließend Medizin nach
Tierkreiszeichen und Humores in einem praktischen Tabellenhandbuch
([Wellcome MS.8515](https://wellcomecollection.org/works/w9nkm98w)). Ein
englischer Faltalmanach von 1415–20 verband Planetenstunden, Mondstand,
Zodiakmann und die Wahl medizinischer Eingriffe
([Wellcome folding almanac](https://wellcomecollection.org/stories/the-enigma-of-the-medieval-folding-almanac)).
Michael von Rhodos zeigt wenige Jahre später denselben Körperveto-Mechanismus:
man soll am vom Mondzeichen beherrschten Glied nicht zur Ader lassen
([Michael of Rhodes, p. 103b](https://brunelleschi.imss.fi.it/michaelofrhodes/manuscript/page_103b.html)).

**Stärkster Gegenbeleg:** Das Blatt zeigt weder eine vollständige 7×12-Tabelle
noch identifizierte Planeten-, Zeichen- oder Körperzeichen. Die zusätzlichen
12 und 8 Plätze können unabhängige Lehrlisten sein. Die konkrete Verrechnung
ist daher eine Quelledition, kein vom Bild erzwungener Algorithmus.

## f68r1 — Zentrum und 28 räumliche Mondhäuser

Das Zentrum ist im Default der Mond als Katalogbesitzer; f68r1.9–36 sind 28
räumlich verschiedene Stellen. Für eine vollständig lesbare Ausgabe setzt der
Herausgeber **nur konventionell** `S01=f68r1.9` und zählt in
Transkriptionsreihenfolge bis S28. Die Namen Alnat, Albatain … Arexe sowie die
kurzen Operationsklassen stammen aus dem lateinischen *Picatrix*-Vergleich.
Sie sind sämtlich als `EXTERNAL_LOCAL_EXEMPLAR_LABEL_NOT_VOYNICH_READING`
markiert.

Der lateinische *Picatrix* nennt explizit 28 Mondhäuser, ihre Tierkreisgrade
und lokale Wirkungen; Haus I erlaubt unter anderem Arzneieinnahme, Häuser XIV,
XXII, XXIII und XXVII Heilung. Derselbe Text zeigt aber auch die entscheidende
Grenze: die meisten Wirkungen betreffen Reise, Bau, Handel, Krieg,
Beziehungen, Saat oder Magie
([Warburg, *Picatrix: The Latin Version*](https://commons.warburg.sas.ac.uk/downloads/8g84mm241)).
Ein Manuskript des 15. Jahrhunderts bei der Society of Antiquaries überliefert
28 Mondhausoperationen zusammen mit sieben Planetensiegeln
([SAL MSS/0039/01](https://collections.sal.org.uk/mss.0039.01)).

**Stärkster Gegenbeleg:** 28 macht Mondhäuser plausibel, aber nicht medizinisch.
Der reale *Picatrix*-Vergleich ist überwiegend nichtmedizinisch. Im Voynich-
Blatt fehlen außerdem ein autorensichtbarer Start, eine Laufrichtung und jeder
extern verankerte Name.

## f69v — unabhängige 28er-Regelfolge

Die drei großen Kreistextloci werden als Rubrik, Gebrauchsanweisung und
Vorsichtsregel gelesen. f69v.4–31 enthalten 28 lokale Wahlregeln: Bad,
Waschung, Salbung, Ruhe, kleineres Maß, Aderlassverbot, Seihen oder
Zurückhalten. Die V22-Regeln bleiben als kreative Ausgangsbasis erhalten, aber
ihre Ontologie ist verschärft: Jede Regel ist eine **ganze lokale
Exemplarregel**, nie die Bedeutung ihrer ein oder zwei sichtbaren Gruppen.

Das wiederholte vollständige `okeod` steht an den modernen Stellen 11, 15 und
24 und bedeutet in allen drei lokalen Ausgaben „Die Stelle ist für ein Bad
günstig“. Damit bleibt LONG/SHORT reine Schreibraum- oder Templatevariation;
es trägt keine Polarität.

Eine 28er-Folge passt historisch besser zu Mondhäusern oder einer daraus
abgeleiteten Wahlregel als zu gewöhnlichen Mondtagen. Ein spätmittelalterliches
Brugger Kollektivlunarium ordnet seine Prognosen über **30** Tage und behandelt
unter anderem Krankheit, Arbeitsbeginn und gelegentlich Aderlass
([Braekman/DBNL](https://www.dbnl.org/tekst/_ver016197701_01/_ver016197701_01_0009.php)).
Darum lautet der V66-Default `28_MANSION_OR_RULE_SEQUENCE`, nicht schlicht
„28 Mondtage“.

**Stärkster Gegenbeleg:** Keine der konkreten medizinischen Regeln ist extern
an eine ZL3b-Oberfläche gebunden. Ein magisches Mondhaus-Operationsbuch, ein
Arbeitsalmanach oder eine Kopierfolge kann dieselbe 28er-Architektur tragen.

## Die direkte f68↔f69-Frage

**Entscheidung: `NONE`.**

- f68 hat 28 räumliche Adressen, aber keinen bewiesenen Start und keine
  bewiesene Richtung;
- f69 hat 28 transkribierte Regelstellen, aber ebenfalls keinen gesicherten
  autorenseitigen Nullpunkt;
- V55 fand weder 28 gleichindexige Treffer noch überhaupt einen exakten
  Vollflächen-Treffer zwischen beiden 28er-Inventaren;
- gleiche Kardinalität und gemeinsame historische Gattung ersetzen keinen
  sichtbaren Schlüssel.

Ein geschulter Benutzer könnte zwei konventionelle, außerhalb der Seiten
gelernte Reihenfolgen kennen. V66 bildet beide vollständig ab, behauptet aber
keinen paarweisen Lookup-Pfad.

## Quellenkritisches Schlussurteil

Die historische Druckprobe stärkt die **Quellengattung** stärker als die
einzelnen Inhalte. Ein Arzt oder Almanachkompilator um 1420 konnte Planet,
Tierkreis, Körperbezirk, Mondstand und Wahlzeit in kompakten Tabellen
verbinden. Ebenso konnte er 28 Mondhäuser als Namens- oder Operationskatalog
abschreiben. Nicht belegt sind die gewählte Startposition, Rotation, konkrete
Namen, medizinischen Einzelregeln oder eine Verbindung zu den Prosa-Seiten.

Der stärkste integrierte R2-Default bleibt deshalb:

```text
THREE_LOCAL_IATROMATHEMATICAL_LOOKUP_INSTRUMENTS
WITH_EXTERNAL_EXEMPLAR_LABELS
AND_WITHOUT_VISIBLE_CROSSPAGE_KEY
```

## Validierung und Scope

`V66_R2_VALIDATION.json` meldet **PASS** über alle Gates:

- 3/3 erlaubte Seiten;
- 142/142 Loci (`74 + 37 + 31`);
- 395/395 Gruppen (`190 + 65 + 140`);
- 28/28 räumliche f68-Stellen;
- 28/28 f69-Regeln;
- 0 portable Astro-Kartenglossen;
- 0 f68↔f69-Identitätsbehauptungen;
- Start-/Richtungsunsicherheit in jeder Locuszeile sichtbar;
- `okeod` an 11/15/24 regelidentisch.

Die gemischte V22-Quelle wurde ausschließlich über `./vmanus-exp query-tsv`
mit drei einzeln angegebenen Allow-Werten, ausgewählten Spalten und
`--forbid-prefix f84` materialisiert. Keine neue Voynich-Seite und kein
V66-Geschwisterartefakt wurde geöffnet. `f84` und `f84r` blieben versiegelt.
