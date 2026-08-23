# Sidequest: Variantenbuch der gelernten Ganzkarten

## Was diese Runde verbessert

Das vorige Lehrlingsblatt reduzierte 22 exakte Ganzkarten auf sechzehn
Bedeutungskoepfe. Offen blieb aber die Schreiberfrage: Wenn etwa GEFAESS,
KUEHLEN oder WASCHEN gemeint ist, welche sichtbare Karte wird genommen?

Die Antwort ist einfacher als erwartet:

```text
9 Kopfwoerter  -> genau eine exakte Form
5 Kopfwoerter  -> kleine sachliche Variantenmenues
2 Kopfwoerter  -> gleiche exakte Karte, nur lokale Handform
```

Damit braucht der Lehrling neben den sechzehn Bedeutungen nur sieben echte
Auswahlregeln. Alle 28 Ganzkartenvorkommen sind damit wieder in ihre
vollstaendigen 116 Arbeitsaussagen eingesetzt.

## Die fuenf sachlichen Menues

### GEFAESS

- `os`: Mischgefaess fuer frischen Pflanzenstoff mit folgendem
  Fluessigkeitszulauf;
- `oykchor`: Zubereitungsgefaess fuer einen bereits fortgefuehrten Ansatz;
- `ly`: Auffang- oder Haltegefaess einer Biological-Station.

Der gemeinsame Kopf bleibt GEFAESS. Die Arbeitsaufgabe waehlt die Unterart.

### KUEHLEN

- `tchody`: den eben gewonnenen Klarauszug als Fertigprodukt kaltstellen;
- `ody`: eine bereits bestimmte Portion abkuehlen.

Die Unterscheidung liegt damit nicht in zwei beliebigen Synonymen, sondern im
Status des gekuehlten Postens: Fertigprodukt gegen Portion.

### PFLANZENTEIL

- `dchey`: Wurzel;
- `sh`: Staengel.

Hier liefert die Zeichnung den Selektor. Die Textkarte muss den Pflanzennamen
nicht wiederholen.

### WASCHEN

- `rshedy`: eigenstaendiger vollstaendiger Waschgang;
- `lkedy`: Nachwaschen nach einer laengeren Bearbeitungsfolge.

### TRENNEN

- `cfhy`: grob trennen oder auswringen, bevor der Posten steht;
- `cphy`: nach der Standzeit fein trennen oder nachseihen, unmittelbar vor dem
  Klarauszug.

Die beiden Karten bilden nun eine klare zeitliche Folge statt zweier
unverbundener Spezialwoerter.

## Zwei reine Handvarianten

`cheey|shey` ist eine einzige exakte KLARLAUF-Karte. In H3 und B4 erscheint
`shey`, in B2 `cheey`. Die Bedeutung wird nicht veraendert; der Schreiber
kopiert die lokale Form.

Dasselbe gilt fuer `dchol|schol` = VORIGES. H3 verwendet `dchol`, H5 `schol`.
Das ist eine Werkstatt-/Exemplarentscheidung, kein zweiter semantischer Wert.

## Neun direkte Eintraege

Bei den restlichen Kopfwoertern gibt es keine Auswahl:

| Kopfwort | Karte |
|---|---|
| ZUSATZ | `dl` |
| ROH | `qekey` |
| TUCH | `dain` |
| SCHWENKEN | `sshkchdy` |
| AUFTRAGEN | `cheeckhody` |
| FUELLEN | `ytey` |
| FRISCHWASSER | `dshedy` |
| TEILEN | `ches` |
| BEFESTIGEN | `qokylddy` |

## Konkreter Schreibablauf

Der Werkstattschreiber kann nun vorwaerts arbeiten:

1. Bildbesitzer und Arbeitsanweisung bestimmen den Bedeutungskoepf.
2. Bei neun Koepfen wird sofort die einzige Karte geschrieben.
3. Bei fuenf Menues waehlen Gegenstand, Prozessstufe oder Ziel die Unterkarte.
4. Bei KLARLAUF und VORIGES wird nur die lokale Oberflaeche kopiert.
5. Danach werden die produktiven `P`- und gebundenen `p`-Karten ergaenzt.
6. Der gesamte Satz wird rueckgelesen; ein Zeilenwechsel beendet ihn nicht.

Beispiel H3-S001:

```text
... cfhy -> STANDZEIT -> cphy -> shey -> tchody
    grob                  fein    Klarlauf  Fertigprodukt kaltstellen
```

Diese Folge ist jetzt nicht mehr nur eine freie deutsche Uebersetzung. Sie
liefert eine konkrete Schreibentscheidung: grob vor der Standzeit, fein danach,
lokale Klarlauf-Handform, anschliessend die Kuehlkarte fuer das Fertigprodukt.

## Neue Arbeitsbasis

Das gemischte System sieht nun so aus:

```text
produktive Fachkuerzel
+ gebundene lokale Traeger
+ neun direkte Ganzkartenkoepfe
+ fuenf kleine sachliche Variantenmenues
+ zwei lokale Oberflaechenregeln
+ Bildbesitzer
```

Das ist einfacher zu lehren als ein flaches Nomenklatorbuch. Die sichtbare
Variation hat drei getrennte Ursachen: Bedeutung, fachliche Unterart und
Schreiberoberflaeche. Sie werden nicht mehr miteinander vermischt.

## Artefakte

- `VARIANT_SELECTOR_LEAF.md`: das kurze Variantenblatt;
- `WHOLE_16_VARIANT_RULES.tsv`: alle sechzehn Auswahlregeln;
- `WHOLE_28_VARIANT_OCCURRENCES.tsv`: jede reale Ganzkartenstelle mit Kontext;
- `ENCODER_116_STATEMENTS.tsv`: vollstaendige Vorwaerts-Schreibtafel;
- `VARIANT_7_DRILLS.tsv`: die sieben Kontrastuebungen;
- Builder, Validator und maschinenlesbare Zusammenfassungen.

Die Runde bleibt auf den festen Prosaseiten. Die Astro-Tabellen wurden nicht
veraendert; die versiegelten Seiten wurden nicht benutzt.
