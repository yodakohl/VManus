# V65 R2 — historische Biological-Zweitausgabe

**Rolle:** handschriftenkundiger Arzt- und Herbal-Schreiber um 1420.
**Status:** vollständige kreative Quellenedition, keine Entzifferung.
**Umfang:** ausschließlich `f81v`, `f82r`, `f83r`; 6 Records, 115 Felder,
97 reflowte Aussagen und 281 Ereignisse.

## Entscheidung

Die stärkste Gesamtfassung ist:

```text
ILLUSTRIERTES THERAPEUTISCHES BAD-/WASCHARBEITSBLATT
MIT EIGENSTÄNDIGER BECKEN-, FILTER- UND AUSLASSBEDIENUNG
```

Das ist keine reine Frauenheilkunde und kein einheitlicher Patientenbericht.
B2 trägt den stärksten Körper-/Teilbad-Default; B4 lässt sich als äußere
Haut-/Wundwäsche lesen, aber nur mit einem gattungsgestützten Körperbesitzer.
B1 und B3 bleiben zwischen therapeutischem Bad und Badehaus-/Wasserbetrieb
geteilt. B5 und B6 sind innerhalb des medizinischen Blatts technisch
sparsamer als eigenständige Therapien.

Die Gegenfassung „bloßes Wasserwerk“ bleibt stark, gewinnt aber nicht das
ganze Blatt: Figuren und die zeitgenössisch gewöhnliche Verbindung von Bad,
Gesundheit, Waschung und Wundversorgung verlangen zumindest eine ernsthafte
körperbezogene Defaultlesung. Umgekehrt verhindern die menschenfreien
Auslasslabels auf f83r und 191/281 unparsed Ereignisse eine fortlaufende
Frauenkrankheitenprosa.

## Unveränderte Quellschichten

1. **Exakte Karte:** Die elf V60-Werte bleiben unverändert:
   `MASS?`, `ANWENDEN?`, `BEREIT?`, `ANSATZ?`, `ZIEL?`, `KLAR?`,
   `VORIGES?`, `ANTEIL?`, `TEMPERIEREN?`, `SPÜLEN?`, `ABLASSEN?`.
2. **Formal:** `VORGABEPARAMETER?`, `STANDARDSLOT_SETZEN`,
   `AKTIVEN_ARBEITSSTAND_VERKNÜPFEN` und
   `LOKALEN_RELATIONSSLOT_SETZEN` bleiben Prompts ohne Wortbedeutung.
3. **Register:** `OWNER`, `ACTIVE`, `TARGET` und `PREVIOUS` behalten die
   exakten recordlokalen V62-IDs. B6 erbt insbesondere nichts aus B5.
4. **Bild:** Figuren, Becken, Zonen, Bögen, Röhren und Auslässe sind
   seitenweite Argumente. Nähe erzeugt keinen stillen Feldbesitzer.
5. **Historisches Exemplar:** Wasser, Kräuter, Tuch, Patient, Haut, Wunde,
   Teilbad, Temperatur, Dauer, Anzahl und jede nicht geankerte Handlung sind
   ausdrücklich `IMAGE`, `GENRE` oder `EXEMPLAR`, nie Kartenbedeutung.

## Vollständige Deckung

| Record | Felder | Aussagen | Events | V63 erkannt | EXEMPLAR_ONLY | Urteil |
|---|---:|---:|---:|---:|---:|---|
| B1 / f81v | 24 | 21 | 66 | 23 | 43 | Badbereitung = Badehaus unentschieden |
| B2 / f82r | 26 | 22 | 62 | 16 | 46 | schwacher medizinischer Teilbad-Vorsprung |
| B3 / f83r | 38 | 34 | 86 | 29 | 57 | äußere Lavage = Wasserwerk unentschieden |
| B4 / f83r | 20 | 16 | 47 | 15 | 32 | medizinisch nur mit Genre-Körperbesitzer |
| B5 / f83r | 5 | 3 | 11 | 4 | 7 | technischer Hilfsprozess gewinnt |
| B6 / f83r | 2 | 1 | 9 | 3 | 6 | technischer Hilfsprozess gewinnt |
| **Summe** | **115** | **97** | **281** | **90** | **191** | **layered mixed edition** |

V63 auf Bio allein: 56 `UNIQUE_EXACT`, 29 `UNIQUE_FORMAL_ONLY`, fünf
`UNIQUE_CONVERGENT_CHANNELS` und 191 `UNPARSED_EXEMPLAR`. Auf Feldebene sind
14/115 eindeutig, 41 mehrdeutig und 60 unparsed; auf Aussageebene 12/97,
35/97 und 50/97. Die flüssige Ausgabe ist daher überwiegend
Exemplarkomposition, nicht Kartenübersetzung.

## Körper, Bad und Patient versus Apparatur

- **f81v:** Figuren erlauben einen körperbezogenen Seitenrahmen. Keine
  erlaubte Beobachtung weist aber ein B1-Feld sicher einer Patientin zu.
- **f82r:** Figurenpaare und getrennte farbige Zonen machen Badende und
  unterschiedliche Arbeitsbereiche plausibel. Von den im erlaubten
  Bilddossier geprüften Labels sitzt nur eines sicher auf einem
  kreuzförmigen Bauteil; die übrigen sind meist nur nahe bei Figur oder Form.
  Deshalb gewinnt B2 als Teilbad, nicht als bestimmte gynäkologische Kur.
- **f83r:** Zwei Labels liegen in gemischter Nähe von Figur und Röhrenende;
  zwei andere unmittelbar an offenen, mehrstrichigen Auslässen ohne lokale
  Figur. Diese asymmetrische Evidenz erzwingt den selbständigen
  Apparate-Layer und schwächt B3/B4 als reine Patientenprosa.

Weder „Frau“ noch „Patientin“ wird aus einer sichtbaren Karte gelesen. Das
Geschlecht der Figuren ist Bildargument; Gebärmutter, Menstruation, Geburt,
Vagina und innere Körperöffnung werden als Default vollständig
zurückgezogen.

## Sechs durchgängige Prozesse und V54-Reparaturen

### B1 — therapeutische Badeflotte und Beckenbeschickung

Erster Arbeitsort spülen; eine exemplarische Kräuter-Badeflotte ansetzen;
mehrere recordlokale Posten messen und verbinden; temperieren, stehen und
prüfen; eine Portion als äußere Badewaschung verwenden; Arbeitsort/Gefäß
spülen; nachfüllen, absetzen, durch Tuch klären und an die nächste Station
geben.

**V54-Reparatur:** Öl, geschlossener Rücklauf und einzelne Patientin sind
gestrichen. **Gegenbeleg:** 43/66 unparsed, kein lokaler Körperbesitzer.

### B2 — Teilbad, örtliche Waschung und warmer Nachgang

Gefäß reinigen; temperierte Kräuterflotte vorbereiten; Badende in ein
örtliches Teil- oder Sitzbad führen; Flüssigkeit durch Tuch klären, warm
halten, am bezeichneten Bereich gebrauchen und ablassen; zweiten kühleren
oder erneut erwärmten Waschgang ausführen; mit örtlicher Waschung oder warmer
Tuchauflage schließen.

**V54-Reparatur:** Der unparsed „Trank“ wird zur örtlichen Waschung. Innere
Irrigation und anatomische erste/zweite Öffnung werden nicht behauptet.
**Gegenbeleg:** 46/62 unparsed und Bildnähe ist kein Textbesitz.

### B3 — langer warmer Bade- und äußerer Lavagezyklus

Bade-/Waschflotte absetzen, Posten zuteilen und zuführen; nachfüllen,
mischen, temperieren und Körper- oder Beckenbereich benetzen; als äußere
Lavage/Badewaschung gebrauchen; spülen und ablassen; zweite Charge bis zum
örtlichen Prüfzustand führen und den Gang wiederholen.

**V54-Reparatur:** „Irrigation“ bedeutet hier höchstens äußere Lavage. Die
echte innere Instillation bleibt nur historischer Gegenvergleich.
**Gegenbeleg:** 57/86 unparsed und menschenfreie Auslass-Owner.

### B4 — gefilterte warme Haut-/Wundwäsche mit Tuchauflage

Tuch/Auflage in einen exemplarischen Waschzusatz tauchen; ausgewählten
Anteil temperieren und fortführen; eine äußere Haut-/Wundstelle waschen und
das warme Tuch auflegen; Rest seihen; Arbeitsort spülen; verbrauchte
Flüssigkeit ablassen und Schlussportion nachfüllen.

**V54-Reparatur:** Der unscharfe „warme Nachgang“ wird als konkrete äußere
Wäsche plus Auflage ediert. Wunde, Haut, Tuch und Medium bleiben
Gattungsergänzungen. **Gegenbeleg:** 32/47 unparsed; kein Körperwort.

### B5 — zeitlich gehaltener Wärme- und Übergabenachtrag

Recordlokalen Restposten abziehen; einmal erwärmen; für die örtliche Frist
halten; nach örtlichem Maß an die nächste Station führen.

**V54-Reparatur:** Kein neuer Patient und keine Behandlung werden ergänzt.
Der Boiler-/Gefäßnachtrag gewinnt lokal.

### B6 — kalter Filter- und Zielübergabenachtrag

Innerhalb B6 einen ungekochten oder abgekühlten Posten einrichten; durch
Tuch/einfache Öffnung führen; örtlich bemessene Portion an die recordlokale
Zielstation übergeben.

**V54-Reparatur:** Kein Rückgriff auf B5. `PREVIOUS` wird, soweit benötigt,
innerhalb des einzigen B6-Statements eingeführt. Beide Felder bleiben offen.

## Historische Druckprüfung um 1420

Die Vergleiche kalibrieren mögliche Quellmechanismen; sie identifizieren
keine Voynich-Karte.

1. Die Biblioteca Angelica beschreibt ihren spät-13.-jh. *De balneis
   Puteolanis* als illustrierten Text über die therapeutischen Eigenschaften
   konkreter Thermalbäder; die 18 Miniaturen verbinden Menschen,
   Landschaften, Becken und Architektur. Ein Morgan-Exemplar um 1400 zeigt
   nackte Badende in einem Becken. Das ist die stärkste Bildgattungsanalogie,
   aber kein Ablaufzettel für Ventile oder 115 Kleinfelder.
   [Biblioteca Angelica](https://bibliotecaangelica.cultura.gov.it/de-balneis-puteolanis/),
   [Morgan Library MS G.74, ca. 1400](https://ica.themorgan.org/manuscript/page/22/77063)
2. Monica Greens kritische *Trotula*-Edition behandelt das Ensemble als drei
   im Mittelalter zusammengeführte Texte. Ein öffentlich dokumentierter
   Behandlungsabschnitt kombiniert Kräuterwasserbad, Salbung und weitere
   Nachbehandlung. Das stützt B2s Bad-plus-Anwendung und B4s warme Auflage,
   nicht eine bestimmte Diagnose.
   [University of Pennsylvania](https://penntoday.upenn.edu/node/149164),
   [Metropolitan Museum mit Green-Übersetzung](https://www.metmuseum.org/fr/perspectives/trotula-womens-medicine-in-middle-ages)
3. Wellcome MS.549 (1471) vereinigt Regimen, eine Tierkreis-/Badetabelle,
   Rezepte und *De passionibus mulierum*; sein Explicit nennt Waschen mit
   lauwarmem Wasser. Die etwas spätere Handschrift belegt eine reale
   medizinische Sammelökologie, nicht dieselbe Seitengrammatik.
   [Wellcome MS.549](https://wellcomecollection.org/works/qbpnbgj8)
4. Der südwestdeutsche Pal. lat. 1331 vom Anfang des 15. Jahrhunderts enthält
   nebeneinander Frauenkosmetik, zwei *Regimina sanitatis*, Rezeptmaterial und
   Abulcasis’ *Liber servitoris* über Arzneibereitung. Das ist der beste
   zeitnahe Codexvergleich für medizinisch-pharmazeutische Kompilation.
   [UB Heidelberg, Pal. lat. 1331](https://digi.ub.uni-heidelberg.de/diglit/bav_pal_lat_1331)
5. Die 1420–1430 datierte mittelniederländische *Chirurgia magna* Utrecht
   MS.1356 enthält Instrumentenbilder und doppelte lateinisch-volkssprachige
   Überschriften. Sie zeigt, dass Wund- und Instrumentenwissen um 1420
   tatsächlich illustriert und volkssprachig übertragen wurde. Zugleich ist
   sie ein Gegenbeleg: ein Chirurgiebuch benennt Kapitel und Instrumente viel
   expliziter als unsere opake Kurzfeldedition.
   [Universiteitsbibliotheek Utrecht, MS.1356](https://www.uu.nl/en/special-collections/collections/manuscripts/medieval-medical/cyrurgie-by-guy-de-chauliac)
6. Theodorics überlieferte Wundpraxis kennt warme Weinwäsche und anschließende
   einfache Bandage; das macht B4 historisch ausführbar, liefert aber weder
   das Medium noch die Wunde aus den Karten.
   [Historische Studie in PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10532452/)
7. Albucasis’ lateinische Chirurgie war über Jahrhunderte ein europäisches
   Lehrbuch; die urologische Tradition beschreibt reale Flüssigkeitsinstillation
   mittels kleinem Hohlrohr/Spritzeninstrument. Das beweist die technische
   Möglichkeit von Irrigation, widerspricht aber einer unmarkierten
   Übertragung auf die ganze Beckenlandschaft.
   [British Library Add MS 36617](https://searcharchives.bl.uk/catalog/032-002055067),
   [Actas Urológicas Españolas](https://scielo.isciii.es/scielo.php?pid=s0004-06142007000800003&script=sci_arttext)
8. Spätmittelalterliche Badstuben waren gewöhnlich Dampf-/Schwitzbäder mit
   Heizung, kaltem Schlussabspülen und teils Wundbehandlung. Das stärkt die
   Mischform „Bad plus medizinischer Dienst“, nicht einen geschlossenen
   modernen Rohrkreislauf.
   [Kuml 57, DOI 10.7146/kuml.v57i57.24661](https://tidsskrift.dk/kuml/article/view/24661)
9. Mittelalterliche Städte und Klöster besaßen echte gravitationsgespeiste
   Wasseranlagen. Diese historische Technik macht das Wasserwerk zum starken
   formalen Rivalen und verbietet das Argument, Röhren müssten medizinisch
   sein.
   [Roberta Magnusson, Johns Hopkins University Press](https://www.press.jhu.edu/books/title/3007/water-technology-middle-ages)

## Prozess-/Zustandsgraph

Die sechs linearen Quellgraphen besitzen zusammen 25 Knoten und 19
`ORDERED_NEXT_PHASE`-Kanten. Jeder Knoten bewahrt seine vollständigen
Statement-, Feld- und Eventlisten sowie den V62-Eintritts- und Austrittszustand.
Alle 97 Statements liegen genau einmal in einem Knoten. Keine Schleife wurde
aus Wiederholung erzwungen: ein zweiter Waschgang bleibt als `EXEMPLAR_GRAPH`
markiert, weil parallele Zellen derselben Form genügen könnten.

## Urteil

**KEEP — aber nur geschichtet und mit niedriger bis mittlerer Konfidenz.**

Die beste um-1420-Edition ist ein medizinisch gerahmtes Bad-/Waschblatt, das
echte Apparatebedienung einschließt. Sie ist konkreter und historisch sauberer
als V54, weil sie den Körperbesitzer nur dort einsetzt, wo Bild und Gattung ihn
tragen, innere Gynäkologie/Irrigation zurückzieht und B5/B6 als technische
Hilfsrecords stehen lässt. Sie bleibt überwiegend exemplarabhängig:
bestätigte Lexeme und Klartextklauseln bleiben null.

## Artefakte und Validierung

- `V65_R2_281_EVENT_BIO_INTERLINEAR.tsv`
- `V65_R2_115_FIELD_EDITIONS.tsv`
- `V65_R2_97_STATEMENT_EDITIONS.tsv`
- `V65_R2_SIX_RECORD_EDITIONS.tsv`
- `V65_R2_PROCESS_GRAPH_NODES.tsv`
- `V65_R2_PROCESS_GRAPH_EDGES.tsv`
- `V65_R2_UNSUPPORTED_ASSUMPTIONS.tsv`
- `V65_R2_BUILD_BIO_SECOND_EDITION.py`
- `V65_R2_VALIDATION.json`

**Validator: PASS — 6/115/97/281; 90 erkannt, 191 EXEMPLAR_ONLY; exakte
V60-Werte und formale Prompts unverändert; V62-IDs ausschließlich
recordlokal; keine verbotene Seite.**
