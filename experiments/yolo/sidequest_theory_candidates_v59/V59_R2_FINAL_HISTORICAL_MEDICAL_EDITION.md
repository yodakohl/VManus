# V59 R2 — finale historisch-medizinische Zehn-Seiten-Edition

Status: vollständige kreative Quelltextedition, keine Entzifferung. Bestätigte
Lexeme: **0**. Bestätigte Klartextklauseln: **0**.

## Endurteil

Die historisch plausibelste Gesamtlesung bleibt ein **bebildertes
iatromedizinisches Werkstatt- und Nachschlagebuch**:

```text
Herbal = WHAT: fünf bildadressierte Simplex- und Bereitungsartikel
Bio    = HOW:  sechs Bad-, Irrigations- und Apparateprozesse
Astro  = WHEN: drei selbständige Konfigurations-/Regimeninstrumente
```

Das ist der führende **Inhaltsdefault**, nicht die Bedeutung der Schrift. Die
robuste Architektur bleibt domänenneutral: ein kleiner Kontrollkern, wenige
memorierte Ganzkarten, `FIELD := NONCLOSE* TERMINAL?`, bildgelieferte Besitzer,
registerlokale Exemplardecks und Positions-/Rendererregeln. Ein Bade-/Waschhaus-
Hausbuch mit Pflanzenrohstoffen und unabhängigem Arbeitsalmanach ist für alle
14 Einheiten vollständig formulierbar, verliert historisch aber knapp gegen
die medizinische Fassung. In R2s vorab definierter V58-Rubrik lautete das
Ergebnis `86:80`.

## Editionsregel

Die Endausgabe liest nicht Karte für Karte in einen deutschen Satz um. Sie
bewahrt fünf Ebenen:

```text
sichtbare Gruppe / exakte Karte
  -> formale Steuerung oder schwaches Ganzkartenmnemonic, falls ausgewählt
  -> sonst UNKNOWN_EXEMPLAR_TAIL
  + stiller Besitzer aus Bild, Diagrammlage und Record
  + lokale Quellenexpansion des ganzen Feldes/Records
  -> flüssiger iatromedizinischer Default
```

Die letzte Zeile ist eine Edition des **angenommenen Quelltexts**. Sie ist
nicht die Summe entzifferter Kartenwörter. Ein physischer Zeilenwechsel ist
kein Satzende; `CLOSE` ist kein gesprochenes „fertig“, „spülen“ oder
„ablassen“.

## Kompaktes Endwörterbuch

`V59_R2_FINAL_DICTIONARY.tsv` enthält alle 173 exakten Prosa-Kartentypen und
trennt die verlangten Ebenen in eigenen Spalten:

| ausgewählte Ebene | Kartentypen | Ereignisse | Inhalt |
|---|---:|---:|---|
| `FORMAL_CONTROL` | 13 | 57 | `OK=SETZEN`, `OT=MARKIEREN`, `L=VERKNUEPFEN` in ihren lizenzierten Formeln |
| `WEAK_HOST_MNEMONIC` | 6 | 22 | `AL=AN?`, `OR=BEREITUNG?`, `CHEY=TEIL?` |
| `EXACT_CARD_MNEMONIC` | 8 | 66 | acht unteilbare, exponierte Ganzkartenwerte |
| `UNKNOWN_EXEMPLAR_TAIL` | 146 | 236 | lokal zu kopierende Karte ohne ausgewählte atomare Bedeutung |
| **gesamt** | **173** | **381** | jede Karte und jedes Ereignis erhalten Status plus lokalen Default |

Die acht behaltenen Ganzkartenmnemonics sind:

```text
AIIN  MASS?          EY     KLAR?          OKY   VERWENDEN?
LCHE  ABLASSEN?      OKE    SPUELEN?       CTHY  BEREIT?
OKEEY WARM?          OLOR   ZUVOR?
```

`LCHE` und `OKE` bleiben mit dem formalen Schluss konfundiert; `EY` beruht nur
auf zwei von vier Rollen; `OLOR` hat nur zwei Ereignisse. `E` und `CKHY` sind
zurückgezogen und liegen im unbekannten Exemplarschwanz. Sichtbare Teilformen
werden nicht produktiv zerlegt.

V56s strengere Schicht wird zusätzlich pro Ereignis ausgewiesen:

```text
exaktes sichtbares daiin -> VORGABEPARAMETER?
SET(<ARG_AIIN>)          -> STANDARDSLOT_SETZEN
SET(<ARG_AL>)            -> LOKALEN_RELATIONSSLOT_SETZEN
FRAME_O(LINK)            -> AKTIVEN_ARBEITSSTAND_VERKNUEPFEN
```

Sie deckt exakt `45/381` Ereignisse in `35/135` Feldern. Ein RIGHT-Argument
erbt dabei weder `MASS?` noch `AN?`.

## Die vierzehn Quelltexte

Die vollständige Tabelle
`V59_R2_FOURTEEN_UNIT_SOURCE_EDITION.tsv` gibt für jede Einheit das
literal-formale Gerüst, die flüssige medizinische Fassung, den stärksten
nichtmedizinischen Rivalen, den historischen Mechanismus und eine exakte Liste
der im flüssigen Default verwendeten, aber als Kartenwerte unbestätigten
Nomen. Auch ein Fragezeichen-Mnemonic wie `MASS?` macht das Quellnomen nicht
zu einem bestätigten Wort. Kurzfassung:

### Herbal

- **H1 f10r_R1:** Wurzelzubereitung einer skabiosen-/Teufelsabbiss-nahen
  Pflanze; Wasserarznei, Maß, Vorrat und warmer Folgegebrauch. Rivale:
  technischer Wurzelzusatz für Wasch-/Farbbetrieb.
- **H2 f10r_R2:** obere Pflanzenteile als Saft/Sud, mit Vorzubereitung und Öl
  verbunden, äußerlich verwahrt. Rivale: zweite technische Extraktionscharge.
- **H3 f11r_R1:** Veilchen als Leitbild; Wein-/Wasserauszug, Tuchklärung und
  warme Auflage. Rivale: Duft-/Farbprobe.
- **H4 f55v_R1:** breitblättriges Allium/Wegerich; Auszug/Waschung und warme
  Auflage. Rivale: Blattflotte und weicher Zurichtungsrest.
- **H5 f56r_R1:** sonnentaunahe Feuchtlandpflanze; kleine Auszugsmenge,
  Teiltrennung und riskante Brust-/Hustenanwendung. Rivale: klebriger
  technischer Rohstoff. Dies bleibt die schwächste medizinische Artikelwette.

Herbal umfasst `20` Felder/`100` Ereignisse, davon nur `32` ausgewählte
Anker und `68` unbekannte Karten. Pflanzenart, Organ, Wasser, Wein, Öl, Honig,
Krankheit und Körperziel werden deshalb in der Einheitentabelle als Bild- oder
Quellenannahmen geführt, nie als Kartenwerte.

### Biological

- **B1 f81v:** gemeinsames Grundbad und Becken-/Laufansatz; Rivale:
  Bade-/Waschhaus-Hauptkreislauf.
- **B2 f82r:** individualisierte Bad-/Wasch-/Auflagestation; Rivale:
  nichtmedizinisches Einzelbecken mit Badgast oder Bediener.
- **B3 f83r_R1:** langer Irrigations-, Filter-, Ablass- und Stationszyklus;
  Rivale: Mehrbeckenbetrieb ohne Patientensemantik.
- **B4 f83r_R2:** warmer Nachgang mit Spülung, Filtration und Neuansatz;
  Rivale: reine Anlagenpflege.
- **B5 f83r_R3:** kurzer Wärme-/Halt-/Übergabenachtrag; der technische Rivale
  ist nahezu gleich stark.
- **B6 f83r_R4:** kalter offener Filtergang; der technische Rivale ist ebenfalls
  nahezu gleich stark.

Bio umfasst `115` Felder/`281` Ereignisse: `85` terminale und `30` offene
Zellen, `113` ausgewählte Anker und `168` unbekannte Ereignisse. Nackte Figuren
halten Behandlung und Baden offen; menschenfreie Ausläufe erzwingen eine echte
Apparateschicht. Keine Karte bezeichnet Frau, Gebärmutter, Krankheit, Wasser,
Rohr, Becken oder Körperöffnung.

### Astro

- **A1 f67r2:** 7-/12-/weitere Inventare werden medizinisch als Planeten-,
  Tierkreis-/Körpersektor- und Bedingungsselector gelesen. Rivale: allgemeiner
  Arbeits-/Wahlkalender. Die Seite ist keine vollständige 7×12-Matrix.
- **A2 f68r1:** Zentrum plus 28 räumliche Mond-/Sternstationen; Lage ist
  Identität, Start und Richtung fehlen. Rivale: neutraler Sternmerkkatalog.
- **A3 f69v:** drei Rubriken plus 28 lokale Regimen-/Wahlregeln. Rivale:
  Arbeits-, Ruhe-, Beschaffungs- oder Sperralmanach. LONG/SHORT ist nur Layout;
  die wiederholte Vollregel `okeod` behält an 11/15/24 denselben Default.

Astro umfasst `142` Loci/`395` Gruppen (`190+65+140`). Jede Gruppe behält im
V22-basierten Ledger einen konkreten lokalen Quelldefault, trägt in V59 aber
den Status `UNKNOWN_LOCAL_EXEMPLAR_LABEL`. Kein Prosa-Kartenwert wird
importiert. Zwischen f68r1 und f69v gibt es weiterhin weder sichtbaren Start
noch Richtung noch exakte Vollformpaarung noch lizenzierten Index.

## Historische Kalibrierung

Die Gattung ist um 1420 möglich, ohne einen direkten Donor zu liefern:

- [British Library Add MS 29301](https://searcharchives.bl.uk/catalog/032-002020783)
  (ca. 1420–30) verbindet illustrierte Chirurgie, Arzneipflanzen, Herbal,
  Rezepte und Zodiac Man. Das ist der stärkste zeitnahe Beleg für die
  medizinisch-naturkundliche Inhaltsökologie.
- [British Library Harley MS 1736](https://searcharchives.bl.uk/catalog/040-002047567)
  (1446 mit Nachträgen) verbindet Chirurgie, Wässer/Distillation, Rezepte,
  medizinische Astrologie, sieben Planeten und Tierkreistafeln.
- [Wellcome Collection MS.8515](https://wellcomecollection.org/works/w9nkm98w)
  ist ein um 1425 angelegtes Kalender-, Astronomie- und Astrologiehandbuch mit
  medizinischer Astrologie und späteren Rezeptnachträgen. Es stützt den
  selbständigen Astroanhang stärker als einen direkten Seitenjoin.
- Spätmittelalterliche praktische Miszellaneen konnten Kalender, Prognostik,
  Handwerk und Rezepte in einem benutzten Codex vereinen. Das hält den
  nichtmedizinischen Rivalen offen. [Armstrong, *Here Is a Good Boke to
  Lerne*](https://www.cambridge.org/core/journals/journal-of-british-studies/article/here-is-a-good-boke-to-lerne-practical-books-the-coming-of-the-press-and-the-search-for-knowledge-ca-14001560/8217EBC4F6CE53F1084709587B7C2E12).
- Technische Pflanzenextraktion ist kein moderner Notbehelf: ein Rezept in
  Oxford, Bodleian Library, MS Rawlinson C.506 (ca. 1400–1450) beschreibt die
  Gewinnung und Verarbeitung von Efeugummi. Das stützt lediglich den
  Werkstattmechanismus des Rivalen, nicht eine der Bildpflanzen. [Ali 2018,
  *Colourants made from aphids and ivy gum*](https://www.nature.com/articles/s40494-018-0204-3).

Diese Vergleiche belegen Manuskript- und Verfahrensökologie. Sie belegen weder
Sprache noch Kartenwerte, Pflanzenidentitäten, einzelne Therapien oder eine
Voynich-spezifische Kürzungspraxis.

## Vollständige Maschinenedition

- `V59_R2_FINAL_DICTIONARY.tsv`: 173/173 Prosa-Kartentypen.
- `V59_R2_381_EVENT_INTERLINEAR.tsv`: 381/381 sichtbare Prosaereignisse mit
  formalem/atomarem Status, Bildbesitzer und lokalem Quelldefault.
- `V59_R2_135_FIELD_EDITION.tsv`: 135/135 Felder mit exakter Oberfläche,
  Formalfolge, V50/V51-Ankerfolge, V52-Klasse und kreativer Feldexpansion.
- `V59_R2_395_ASTRO_GROUP_LEDGER.tsv`: 395/395 sichtbare Astrogruppen mit
  Positionsbesitzer, lokalem Default und explizit unbekanntem Gruppenstatus.
- `V59_R2_BUILD_FINAL_EDITION.py`: reproduzierbare mechanische Ableitung aus
  den publizierten V49- und V22-Vollledgern über selector-first guarded access.

Die V52-Feldpartition wird exakt reproduziert:

```text
Q1_OPEN_OPAQUE       8 Felder / 16 Ereignisse
Q2_TERMINAL_OPAQUE  44 Felder / 57 Ereignisse
Q3_HOST_FRAME       33 Felder / 107 Ereignisse
Q4_WHOLE_CARD       26 Felder / 72 Ereignisse
Q5_MIXED_PARATACTIC 24 Felder / 129 Ereignisse
```

Damit besitzt jede der `381+395=776` sichtbaren Gruppen einen Default und
einen Status, ohne dass eine kurze Karte einen Satzwert erhält.

## Editionsgrenze

Die flüssige Fassung ist meisterseitige Expansion. Ohne Bild, Register und
lokales Exemplar rekonstruiert der ausgewählte Kern weder Wurzel/Wasser/Wein,
noch Patient/Bad/Rohr, noch Planet/Mondhaus/Regel. `236/381` Prosaevents und
inhaltlich `395/395` Astrogruppen bleiben unbekannter Exemplarschwanz. Genau
darum lautet die Schlussformel:

`IATROMEDICAL_SOURCE_DEFAULT__DOMAIN_NEUTRAL_FORMAL_MACHINE__NO_DECIPHERMENT`

Es wurden keine neuen Voynich-Seiten, keine V59-Geschwisterdateien und weder
`f84` noch `f84r` benutzt. Kein Commit oder Push wurde ausgeführt.
