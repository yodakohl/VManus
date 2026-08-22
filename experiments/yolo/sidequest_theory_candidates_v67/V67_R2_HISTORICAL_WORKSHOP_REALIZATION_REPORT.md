# V67 R2 — Historischer Lehrbarkeits- und Werkstattentwurf um 1420

Status: **kreative historische Arbeitsedition, keine Entzifferung und keine
Lautzuweisung**. Geprüft wurden ausschließlich die feste Zehnseitenbasis und
die ausgewählten V60–V66-Schichten. `f84` und `f84r` wurden weder gelesen noch
verwendet.

## Urteil

Die stärkste Realisierung ist ein **zweistufiges Hybridverfahren**:

```text
gewöhnliche lateinische oder volkssprachliche Fachquelle
→ bild- und registergestützte Ellipse
→ Quellpaket in fester Registerreihenfolge
→ 11 gelernte Ganzkarten + 4 nichtlexikalische Formalprompts
→ exakt kopierter, semantisch exemplarabhängiger Rest
→ Herbal-Artikel | Bio-Arbeitszellen | Astro-Nachschlagetafel
→ graphische Reinschrift und physischer Reflow
```

Das Verfahren ist um 1420 **als kleine Werkstattpraxis lernbar**, sofern die
Schreiber bereits normale Rezept- und Tabellenliteracy besitzen und ein
Masterexemplar samt Codeblatt vorliegt. Es ist **nicht semantisch autonom**:
Geht dieses Exemplar verloren, lassen sich Pflanze, Medium, Leiden, Körperteil,
Gefäß, Planet, Zeichen, Mondstation und lokale Regel nicht aus den kurzen
Karten zurückgewinnen. Diese Abhängigkeit ist zugleich der stärkste Gegenbeleg.

## Wettbewerb der drei Quellstile

Die vollständige Wertung steht in
`V67_R2_SOURCE_ORDER_AND_MODEL_COMPETITION.tsv`.

1. **Lateinisches Formular** gewinnt als normierende Vorstufe. `Recipe`,
   Mengenformeln, knappe Imperative und Abschlussformeln sind gut abkürzbar.
   Wellcome MS.683 zeigt eine lateinische Rezeptsammlung mit zwei Haupthänden,
   zeitgenössischen Zusätzen und formelhaften Rezeptstrukturen
   ([Katalog](https://wellcomecollection.org/works/w6ne7k4t)). Es erklärt aber
   weder den großen seltenen Herbal-Rest noch die geschlossenen Bio-Zellen
   allein.
2. **Volkssprachlicher Imperativ** gewinnt für das Vorschreiben oder mündliche
   Unterweisen von Herbal-Artikeln: nehmen → bearbeiten → Medium zugeben →
   anwenden. Die Untersuchung von Rawlinson C.299 beschreibt gerade die Folge
   Leiden → Stoffe → Zubereitung → Anwendung in einer großen
   fünfzehntjahrhundertlichen Rezeptsammlung
   ([Studie](https://www.cambridge.org/core/journals/medical-history/article/evidence-for-the-continued-use-of-medieval-medical-prescriptions-in-the-sixteenth-century-a-fifteenthcentury-remedy-book-and-its-later-owner/95663D54A46819495D78EE9BF7FC88EA)).
   Sichtbar wäre diese Sprache jedoch zu ausführlich; eine zweite
   Kompilationsstufe bleibt nötig.
3. **Reine Tabellennotation** gewinnt als unmittelbare Form der Bio- und
   Astro-Reinschrift. Sie trägt Position, Registerzustand und lokale
   Nachschlageadresse, aber nicht selbständig die konkreten Fachnomen. Ein
   praktischer Kalender um 1425 und ein medizinisches Faltalmanach von
   1415–1420 belegen den zeitnahen Gebrauch medizinisch-astronomischer
   Nachschlageinstrumente
   ([MS.8515](https://wellcomecollection.org/works/w9nkm98w),
   [Faltalmanach](https://wellcomecollection.org/stories/the-enigma-of-the-medieval-folding-almanac)).

Keine Einzelform gewinnt alle Register. Das Hybrid ist keine Behauptung, dass
ein solches Voynich-Codebuch historisch belegt sei; es ist die knappste
Werkstattrekonstruktion, die alle drei festen Quellformen ohne neue
Kartenbedeutungen tragen kann.

## Quellreihenfolge je Register

- **Herbal:** Bildbesitzer/Rubrik → Pflanzenteil und Maß → Bearbeitung und
  Medium → Zustand → Gebrauch am Ziel → Verwahrung oder Variante. Der
  Bildbesitzer darf stumm bleiben. Das illustrierte lateinische Herbal Egerton
  MS 747 ist ein Gattungsvergleich für Bild plus Artikel, nicht für das
  Kartensystem
  ([British Library](https://searcharchives.bl.uk/catalog/032-001983805)).
- **Biological:** sichtbare Station/Besitzer → aktive Charge → Menge →
  Relation/Ziel → temperieren, prüfen oder gebrauchen → ablassen/lokal
  schließen → nächste parallele Zelle. Frau, Bad, Patient und Körperteil werden
  nur bei Bild- oder Exemplarlizenz eingesetzt; sonst bleibt der Ablauf ein
  Gefäß-, Leitungs- oder Wasserarbeitsgang. Illustrierte therapeutische Bäder
  um 1400 liefern eine reale Bildgattungsanalogie, entscheiden aber diese
  Alternative nicht
  ([Morgan MS G.74](https://ica.themorgan.org/manuscript/page/22/77063)).
- **Astro:** extern gewählte Zeitfrage → räumliche Adresse → lokaler
  Exemplareintrag → extern bekannte Handlung erlauben, mildern oder
  verschieben. A1 ist ein 7/12-Rahmen mit zweitem Zwölferinventar und acht
  Prüfbedingungen; A2 ein Zentrum-plus-28-Raumkatalog; A3 eine unabhängige
  28er-Regelfolge. A2 und A3 erhalten **keine** direkte Identität. Die
  lateinische *Picatrix*-Tradition ist nur Vergleich für operationstragende
  Mondstationslisten
  ([Warburg-Ausgabe](https://commons.warburg.sas.ac.uk/downloads/8g84mm241)).

## Codebuch, Genealogie und Kompilator

Das minimale Codebuch hat vier getrennte Lagen:

1. ein gemeinsames Blatt mit den elf unveränderten V60-Merkwerten `MASS?`,
   `ANWENDEN?`, `BEREIT?`, `ANSATZ?`, `ZIEL?`, `KLAR?`, `VORIGES?`,
   `ANTEIL?`, `TEMPERIEREN?`, `SPÜLEN?`, `ABLASSEN?`;
2. vier Formalprompts für Standard-, Relations-, Aktiv-/Verknüpfungs- und
   Vorgabeplatz, ausdrücklich **ohne Wortwert**;
3. je ein Registerblatt für Herbal, Bio und Astro;
4. einen lokalen Exemplarrand für seltene Ganzkarten sowie ein graphisches
   Blatt für Wrapper, Allographen, Schließer und Feldumbruch.

Die plausible Genealogie lautet `E0` gewöhnliche Fachquellen → `E1`
normalisierte elliptische Quellklauseln → `E2` autorisiertes Kartenexemplar →
registerweise Arbeitskopien. Eine neue seltene Karte darf ein Kopist nur aus
`E2` übernehmen; eine neue allgemeine Bedeutung erfordert gleichzeitig eine
Änderung von Masterexemplar und Codeblatt. Damit werden mehrere Hände möglich,
ohne dass jede die ganze medizinische Prosa neu erfinden darf.

Der Kompilator setzt zuerst Record und Register zurück, bindet nötigenfalls den
stillen Bildbesitzer, ordnet die gewöhnliche Klausel, führt die vier
recordlokalen Register `OWNER`, `ACTIVE`, `TARGET`, `PREVIOUS`, ersetzt nur
exakte lizenzierte Karten, setzt Formalprompts, kopiert den übrigen Rest
unzerlegt und übergibt erst dann an den Layoutschreiber. Die Typologie
mittelalterlicher medizinischer Abkürzungen — Kontraktion, Suspension,
hochgestellte Buchstaben, Brevigraphen und Sonderzeichen — macht eine solche
Ausbildung kategorial plausibel, liefert aber **keine** Voynich-Lautung
([Jones](https://reunido.uniovi.es/index.php/SELIM/article/download/13301/12036/28090)).

## Ausbildung und Übergabe

Ein bereits literater Gehilfe lernt in dieser Reihenfolge: gewöhnliche
Rezeptformeln; normale Abbreviatur; die 15 gemeinsamen Deck-/Formalwerte;
drei Registerblätter; beaufsichtigtes Kompilieren; rückwärtiges Prüfen gegen
`E2`. **Sechs bis zwölf Wochen** sind eine rein editorische Aufwandsschätzung,
kein Manuskriptbefund. Ohne `E2` wird der Gehilfe niemals unabhängig, weil der
lokale Rest absichtlich exemplarabhängig bleibt.

Übergaben erfolgen vorzugsweise an Recordgrenzen mit Reset aller vier
Register. Bei einer Übergabe mitten im Record werden Besitzer, aktiver Posten,
Ziel, Voriges-Referent, Registertemplate und Position im lokalen Rest
mitgegeben. Eine Kantenwiederholung wie `qokaiin` zwischen f82r.3 und f82r.4
ist dann ein Catchword-/Kopiermechanismus derselben Klausel, keine zweite
Anweisung und keine neue Bedeutung. Wellcome MS.550 ist ein naher
Gattungsvergleich für eine illustrierte, rubricierte, mehrsprachige und von
mehreren Händen geschriebene medizinisch-astrologische Sammelhandschrift
([Katalog](https://wellcomecollection.org/works/htndqk24)).

## Bidirektionale Belastungsproben

`V67_R2_FULL_TRACES.tsv` enthält den vollständigen H4-Record (18 Ereignisse),
die lange B2-Folge (62 Ereignisse) und je eine vollständige Gebrauchsanweisung
für A1–A3 (190/65/140 Gruppen).

- **H4, Quelle → Karte:** ein flüssiger Blatt-/Wein-/Auszug-/Umschlagartikel
  wird in vier Quellpakete zerlegt. Nur `MASS?`, `ANSATZ?`, ein Standard- und
  ein Zielprompt werden kurz lizenziert; Bärlauch, Wein, Honig, Wunde und jede
  konkrete Bearbeitung bleiben `IMAGE/GENRE/EXEMPLAR`.
  **Karte → Quelle:** Reihenfolge und Registercarry lassen sich wiedergeben,
  die konkreten Nomen und 11 unlizenzierte Ereignisse nicht. Genau diese
  asymmetrische Rücklesung verhindert eine Scheindekodierung.
- **B2, Quelle → Karte:** ein mehrphasiger Teilbad- oder Leitungsprozess wird
  als Charge → Ziel → Temperieren/Prüfen/Anwenden → Ablassen → nächste Zelle
  kompiliert. **Karte → Quelle:** die sechs Phasen und der f82-Kantencarry sind
  rekonstruierbar, nicht aber Patientin, Wasser, Tuch, Becken oder Öffnung.
  Der stärkste Rival ist ein geschlossener Badehaus-/Wasserwerkzyklus.
- **A1–A3, Quelle → Karte:** ein extern bekanntes Zeit- oder
  Mondstationsinventar wird in räumliche Ganzloci kopiert. **Karte → Quelle:**
  nur die Nachschlageprozedur und Locusgrenzen sind rücklesbar. Sämtliche
  Planeten-, Zeichen-, Körper-, Stations- und Operationsnamen bleiben lokale
  Editionswerte; Start und Drehrichtung bleiben unbewiesen.

## Stärkster Gegenvergleich und Schluss

Der stärkste nichtkodische Gegenvergleich ist ein **gewöhnliches
mehrsprachiges Fachmiszellaneum mit starkem Layout und unbekannter Sprache**:
Herbal-Prosa, ein Badehaus-/Wasserwerkdiagramm und astronomische Tabellen
könnten unabhängig nebeneinander kopiert worden sein. Eine ungefähr
zeitgleiche medizinische Sammelhandschrift verbindet tatsächlich Chirurgie,
Pflanzen, Rezepte und Zodiac Man
([BL Add MS 29301](https://searcharchives.bl.uk/catalog/032-002020783)); das
beweist aber weder ein gemeinsames Deck noch diese zehnseitige Einheit.

Darum lautet das Endurteil: **historisch lehrbar unter erhaltenem
Masterexemplar, textintern nicht bewiesen**. Das Hybridmodell erklärt die
gemeinsamen kurzen Karten und die drei verschiedenen Layoutregister besser als
einer der drei reinen Quellstile. Sein Preis ist hoch und offen ausgewiesen:
11 Karten bleiben Fragezeichen, vier Prompts bleiben nichtlexikalisch, der
größte Teil der Prosa bleibt `EXEMPLAR_ONLY`, und alle 395 Astrogruppen bleiben
lokale Nachschlageeinträge ohne Laut- oder Wortzuweisung.

## Artefakte und Abdeckung

- `V67_R2_WORKSHOP_MANUAL.tsv`: 30 kontrollierte Codebuch-, Genealogie-,
  Compiler-, Ausbildungs-, Übergabe- und Prüfschritte.
- `V67_R2_SOURCE_ORDER_AND_MODEL_COMPETITION.tsv`: 3 Quellstile × 3 Register
  plus gewähltes Hybridmodell.
- `V67_R2_FULL_TRACES.tsv`: 13 vollständige Tracezeilen; H4 = 18, B2 = 62,
  A1/A2/A3 = 190/65/140 Gruppen.
- `V67_R2_HISTORICAL_COMPARATORS.tsv`: 11 echte Vergleichsquellen mit
  Reichweitengrenzen.
- Die feste Vollabdeckung wird unverändert aus V64/V65/V66 referenziert:
  Herbal 5 Records/100 Ereignisse, Bio 6 Records/281 Ereignisse, zusammen 381
  Prosaereignisse; Astro 3 Diagramme/142 Loci/395 Gruppen.
