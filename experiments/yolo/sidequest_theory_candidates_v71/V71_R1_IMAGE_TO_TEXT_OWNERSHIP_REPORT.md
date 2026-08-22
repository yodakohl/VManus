# V71 R1 — vollständige Bild-zu-Text-Besitzerkarte

Rolle: Lehrmeister einer Schreibwerkstatt um 1420. Status: kreative,
zehnseitige Arbeitstheorie; keine Entzifferung, Übersetzung oder
manuskriptweite Behauptung.

## Ergebnis

Alle 135 Prosa-Felder und alle 142 eindeutigen Astro-Loci besitzen nun genau
eine Werkstattentscheidung. Der vollständige maschinenlesbare Bestand steht in
`V71_R1_OWNER_LEDGER.tsv`:

| Abschnitt | Einheiten | `DIRECT_VISIBLE` | `INHERITED_VISIBLE` | `PAGE_OWNER_ONLY` | `UNRESOLVED` |
|---|---:|---:|---:|---:|---:|
| Herbal | 20 | 9 | 9 | 1 | 1 |
| Biological | 115 | 7 | 98 | 3 | 7 |
| Astro | 142 | 71 | 39 | 31 | 1 |
| Gesamt | 277 | 87 | 146 | 35 | 9 |

Damit werden 381/381 Prosaereignisse und 395/395 Astrogruppen erreicht. Die
32 Revisionen sind in `V71_R1_REVISIONS.tsv` zusammengefasst; kein formaler
Feld-, Karten-, Locus- oder Gruppenidentifikator wurde geändert.

## Die kleinste lehrbare Besitzerregel

Der Meister lehrt nicht, ein Bild zu „übersetzen“. Er lehrt eine feste
Reihenfolge, mit der ein Schreiber ein ausgelassenes sichtbares Argument
einsetzt:

1. **Am Feld- oder Locusbeginn zuerst nach direktem Besitz suchen.** Liegt der
   Text in einem einzelnen Bildteil, einer gebundenen Szene, einem Sternplatz,
   Ring oder Sektor, wird genau dieses kleinste Objekt eingesetzt:
   `DIRECT_VISIBLE`.
2. **Ohne neuen sichtbaren Besitzer den letzten Besitzer im selben Record oder
   Diagramm forttragen.** Das ist `INHERITED_VISIBLE`. Der Übertrag endet
   zwingend an einer Record-, Seiten- oder Diagrammgrenze.
3. **Wenn eine Seite nur einen tragenden Bildbesitzer hat, ihn als schwächeren
   Default nehmen.** Das ist `PAGE_OWNER_ONLY`: etwa der gemeinsame f81v-Pool
   oder die gepaarten f67-Räder. Dieser Status darf keine einzelne Figur,
   Leitung oder Richtung erfinden.
4. **Bei mehreren gleich möglichen lokalen Besitzern nicht raten.** Das ist
   `UNRESOLVED`. Der Schreiber kopiert dann den Wert aus dem Masterexemplar.
   Genau so werden die B5/B6-Nachträge auf f83r und der mehrdeutige
   Gesichtsmittelpunkt von f68r1 behandelt.

Die Rücklesung läuft rückwärts:

```text
sichtbare Gruppe
  -> exakte Feld- oder Locus-ID
  -> Besitzstatus im Ledger
  -> kleinster Bildbesitzer oder recordlokaler Vorbesitzer
  -> konkrete stille Besitzerklasse
  -> opaker Karten-/Exemplarwert bleibt unverändert
```

Das Bild füllt also nur die Besitzerstelle. Es liefert weder Verb, Substanz,
Temperatur noch Kartenwert.

## Schreibanweisung für einen Lehrling

### Herbal

Zeichne zuerst die ganze Pflanze. Eröffne jeden Record mit dem kleinsten
sichtbaren Teil, den das Masterexemplar vorgibt: Wurzelstock, offener Kopf,
geschlossene Knospe, Blütenkopfmenge, Blattmasse oder Seitenkopfgruppe. Trage
diesen Teil bis zu einem neuen Bildteil- oder Recordwechsel fort. Ist nur die
Pflanze als Ganzes sicher, schreibe `WHOLE_PLANT`; erfinde keine Art.

### Biological

Ziehe um jede wirklich zusammenhängende Figur-Gefäß-Gruppe gedanklich einen
Besitzerrahmen. Ein Bogen, der zwei Gefäße wirklich berührt, bildet einen
lokalen Besitzer. Zwei gleichfarbige, aber unverbundene Szenen bleiben getrennt.
Blau oder Grün sagt weder Wasser noch Richtung. Bei f81v trägt der gemeinsame
zweireihige Einschluss den ganzen Record. Bei f82r wechseln die Besitzer mit
den vier lokalen Szenen. Bei f83r dürfen nur der Bogenverbund, der linke
Abwärtskanal und der rechte S-Kanal samt Endkörper direkt fortgetragen werden.

### Astro

Jede Kreisfigur ist ein eigener Namensraum. Ringtext gehört seinem Ring,
Sektortext seinem Sektor und ein lokales Sternlabel der Sternstelle an seiner
Quellposition. Ein Rad darf weder seinen Start noch seinen Wert an das nächste
vererben. f69v besitzt einen separaten Prosablock, zwei lokale Ringtexte und
28 anonyme Stellen ausschließlich am linken Speichenrad. Das ist eine
Platzinventur, keine Folge von 28 gelesenen Regeln.

## Vollständige Spur 1 — Herbal H2 (`f10r`, F003–F005)

Der Record beginnt neu; H1s Wurzelbesitzer darf nicht über die Recordgrenze
mitkommen.

| Feld | Status | eingesetzter Besitzer | konkrete Rücklesung | stärkster Rivale |
|---|---|---|---|---|
| F003 / `f10r.6` | `DIRECT_VISIBLE` | `PLANT_10_OPEN_HEAD_AND_UPPER_LEAF_TIER` | „Nimm den sichtbaren offenen Kopf samt oberem Blattbereich als aktuellen H2-Posten; das Verfahren bleibt im Exemplar.“ | ganze Pflanze |
| F004 / `f10r.8` | `DIRECT_VISIBLE` | `PLANT_10_CLOSED_BUD_OR_UPPER_TIP` | „Eröffne als Gegenposten die geschlossene Knospe beziehungsweise obere Spitze.“ | wieder der offene Kopf |
| F005 / `f10r.9` | `INHERITED_VISIBLE` | `PLANT_10_TWO_HEAD_STAGE_SET` | „Führe beide recordlokal gesetzten sichtbaren Kopf- oder Stufenposten gemeinsam weiter; Produkt und Mischung sind unbekannt.“ | ganze Pflanze ohne Teilunterscheidung |

V69 muss hier die enge Pflanzennennung und die Salbenoperationen ändern. Die
bildsparsame Zweiteilung offener Kopf versus geschlossene Knospe darf bleiben.

## Vollständige Spur 2 — Biological B2 (`f82r`, F045–F070)

Die 26 Felder werden nicht mehr zu einer einzigen Filter-Abfluss-Maschine
verbunden. Die Spur deckt jede B2-Zeile ab:

| Locus | Felder | Statusfolge | lokaler Besitzer | stiller Default |
|---|---|---|---|---|
| `f82r.2` | F045–F048 | `DIRECT`, danach 3× `INHERITED` | obere paarige Bogen-/Zylindergruppe | aktueller Schritt gilt nur dieser verbundenen oberen Anordnung |
| `f82r.3` | F049–F050 | 2× `INHERITED` | obere paarige Bogen-/Zylindergruppe | gleiche obere Szene; die Zeilengrenze eröffnet keinen neuen Apparat |
| `f82r.4` | F051–F052 | 2× `INHERITED` | obere paarige Bogen-/Zylindergruppe | Fortsetzung derselben Szene, ohne Fließrichtung |
| `f82r.7` | F053–F056 | `DIRECT`, danach 3× `INHERITED` | mittlere linke Hand-/Gerätestation mit Wellensträngen | nur sichtbarer Handkontakt und Strangverlauf zählen |
| `f82r.19` | F057–F058 | `DIRECT`, danach `INHERITED` | liegende Figur im Trichtergefäß | lokaler Figuren-Gefäß-Posten ohne Verbindung zum oberen Zylinder |
| `f82r.23` | F059–F061 | `DIRECT`, danach 2× `INHERITED` | unterer unregelmäßiger Figurenpool | gemeinsame untere Einfassung als Besitzer |
| `f82r.26` | F062–F063 | 2× `INHERITED` | unterer unregelmäßiger Figurenpool | derselbe untere Besitzer wird fortgetragen |
| `f82r.27` | F064–F070 | 7× `INHERITED` | unterer unregelmäßiger Figurenpool | Abschlussfolge innerhalb des unteren Feldes; keine Rückleitung nach oben |

Der stärkste Rivale jedes lokalen Besitzers ist die ganze Seite als
Stationsatlas. Er ist schwächer, weil er die sichtbaren Unterbrechungen nicht
nutzt, aber stärker als V69s erfundene globale Rohrleitung.

## Vollständige Spur 3 — Astro `f69v`, alle 31 Loci

Die ersten drei Loci besitzen drei verschiedene sichtbare Textorte:

| Locus | Besitzer | Rücklesung |
|---|---|---|
| `f69v.1` | `F69_UPPER_RIGHT_PROSE_BLOCK` | Prosahinweis für die Drei-Räder-Tafel; genaue Reichweite unbekannt |
| `f69v.2` | `F69_MIDDLE_LOBED_DIAGRAM_RING_TEXT` | opaker Ringtext des mittleren Lappenrades |
| `f69v.3` | `F69_RIGHT_FACE_PETAL_DIAGRAM_RING_TEXT` | opaker Ringtext des rechten Gesicht-Blatt-Rades |

Die restlichen 28 Loci bilden vollständig die lokale Platzinventur des linken
Speichenrades:

```text
f69v.4  -> F69_LEFT_SPOKE_RADIAL_PLACE_01
f69v.5  -> F69_LEFT_SPOKE_RADIAL_PLACE_02
f69v.6  -> F69_LEFT_SPOKE_RADIAL_PLACE_03
f69v.7  -> F69_LEFT_SPOKE_RADIAL_PLACE_04
f69v.8  -> F69_LEFT_SPOKE_RADIAL_PLACE_05
f69v.9  -> F69_LEFT_SPOKE_RADIAL_PLACE_06
f69v.10 -> F69_LEFT_SPOKE_RADIAL_PLACE_07
f69v.11 -> F69_LEFT_SPOKE_RADIAL_PLACE_08
f69v.12 -> F69_LEFT_SPOKE_RADIAL_PLACE_09
f69v.13 -> F69_LEFT_SPOKE_RADIAL_PLACE_10
f69v.14 -> F69_LEFT_SPOKE_RADIAL_PLACE_11
f69v.15 -> F69_LEFT_SPOKE_RADIAL_PLACE_12
f69v.16 -> F69_LEFT_SPOKE_RADIAL_PLACE_13
f69v.17 -> F69_LEFT_SPOKE_RADIAL_PLACE_14
f69v.18 -> F69_LEFT_SPOKE_RADIAL_PLACE_15
f69v.19 -> F69_LEFT_SPOKE_RADIAL_PLACE_16
f69v.20 -> F69_LEFT_SPOKE_RADIAL_PLACE_17
f69v.21 -> F69_LEFT_SPOKE_RADIAL_PLACE_18
f69v.22 -> F69_LEFT_SPOKE_RADIAL_PLACE_19
f69v.23 -> F69_LEFT_SPOKE_RADIAL_PLACE_20
f69v.24 -> F69_LEFT_SPOKE_RADIAL_PLACE_21
f69v.25 -> F69_LEFT_SPOKE_RADIAL_PLACE_22
f69v.26 -> F69_LEFT_SPOKE_RADIAL_PLACE_23
f69v.27 -> F69_LEFT_SPOKE_RADIAL_PLACE_24
f69v.28 -> F69_LEFT_SPOKE_RADIAL_PLACE_25
f69v.29 -> F69_LEFT_SPOKE_RADIAL_PLACE_26
f69v.30 -> F69_LEFT_SPOKE_RADIAL_PLACE_27
f69v.31 -> F69_LEFT_SPOKE_RADIAL_PLACE_28
```

Jede Zeile liest nur: „Nimm den opaken Eintrag an diesem lokalen radialen
Platz.“ Keine Zeile liest Bad, Aderlass, Salbung, Arbeitsschritt oder
günstig/ungünstig. Start und Umlaufsinn bleiben unbekannt.

## Die neun ungelösten Besitzer

`UNRESOLVED` ist hier eine Werkstattanweisung, kein Versagen ohne Ersatz:

- F013: Das Masterexemplar muss bei PLANT_55 zwischen Blattmasse, oberer Krone
  oder beidem wählen.
- F129–F133: Für B5 ist unter den lokalen f83r-Figurengefäßen kein eigener
  sichtbarer „Übergabebecken“-Besitzer auswählbar.
- F134–F135: Für B6 ist kein sichtbares „Kaltbecken mit Filter“ auswählbar.
- `f68r1.8`: Die Seite besitzt mehrere Gesichtsmittelpunkte; ein einzelner
  Mondbesitzer ist nicht sichtbar.

In allen neun Fällen lautet der konkrete Default
`EXEMPLAR_VALUE_UNKNOWN_AT_VISIBLE_OWNER_SLOT`: Der Lehrling kopiert den
Besitzerhinweis aus dem Exemplar und darf keine Szene nach Ähnlichkeit wählen.

## Was V69 ändern muss

Die formale V69-Ausgabe bleibt byte- und ID-seitig unangetastet. Ihre kreativen
Besitzerglossen müssen jedoch in allen 277 Einheiten neu gebunden werden,
weil V71 absichtlich eine vollständige Besitzeredition liefert. Die größten
inhaltlichen Reparaturen sind:

- enge Pflanzenarten und bildlich nicht sichtbare Medien werden auf anonyme
  Teile zurückgesetzt;
- f81v erhält einen gemeinsamen Pool statt eines Umlaufnetzes;
- f82r und f83r werden in reale lokale Verbindungen zerlegt;
- f67r2 wird ein Paar lokaler Räder statt einer sichtbaren 7×12-Matrix;
- f68r1 wird ein Multipanel-Atlas statt eines Ein-Zentrum-Katalogs;
- f69v erhält drei getrennte Radnamensräume und nur links eine lokale
  28-Platz-Inventur.

## Typische Lehrlingsfehler und Korrektur

1. **Besitzer über Recordgrenzen tragen:** H1-Wurzel in H2 übernehmen.
   Korrektur: Register am Recordanfang löschen.
2. **Farbe als Fließpfeil lesen:** Blau von einer Bio-Szene in die nächste
   verlängern. Korrektur: nur echte Linienberührung kopieren.
3. **Eine Seite zu einer Maschine machen:** f82r oder f83r global verbinden.
   Korrektur: Besitzerrahmen um jede lokale Kontaktgruppe.
4. **Mehrere Zentren verschmelzen:** f68r1 einen einzigen Mond geben.
   Korrektur: Panelgrenze und Quellposition bewahren.
5. **Radplätze in Sätze verwandeln:** die 28 linken f69-Stellen linear lesen.
   Korrektur: Platz-ID, nicht Lesereihenfolge, abschreiben.
6. **Bildteil in Kartenbedeutung verwandeln:** einem häufigen Zeichen
   „Wurzel“, „Wasser“ oder „Stern“ geben. Korrektur: sichtbarer Besitzer und
   opake Karte bleiben zwei getrennte Spalten.

## Reproduzierbarkeit und Grenze

`V71_R1_build_owner_map.py` erzeugt Ledger, Revisionsliste und
`V71_R1_VALIDATION.json` aus genau den gefrorenen V69-Quellen neu. Alle Gates
stehen auf `PASS`. Keine andere Seite, kein aktiver Geschwisterbericht und
kein versiegeltes Material wurde benutzt; `f84` und `f84r` blieben vollständig
ungeöffnet.

Das Ergebnis etabliert nur eine vollständige kreative
**Bildbesitzer-Defaultschicht**. Es etabliert kein Wort, keinen Stamm, keine
Pflanzenart, keine Flüssigkeit, keine Himmelsbezeichnung und keine Operation.
