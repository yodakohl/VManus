# V15 R3 — Bio-Wertregister statt Stationsalphabet

Status: unabhängige explorative R3-Arbeitshypothese; keine Übersetzung und
kein kanonischer GDT-Nachweis.

## Ergebnis

Die vier führenden Schlussfamilien kodieren auf den drei festen Bio-Seiten am
ehesten **latente Antworten eines Anwendungs-/Konfigurationsregisters**, nicht
die sichtbaren Figuren, Becken, Leitungen oder Endstationen selbst:

```text
Bild/Absatz/Stempel liefert:  AKTIVES OBJEKT + FRAGE/SLOT
Wertkarte liefert:           KATEGORIALE ANTWORT
DY liefert:                  COMMIT
```

Die Bilder können die stillen Operanden und die Art des Formulars liefern.
Der exakte Schlusswert sagt aber wahrscheinlich, *wie* der jeweilige Slot
belegt ist: etwa Grundmodus, markierter Anwendungsmodus, Arbeits-/Ergebnislage
oder Halte-/Trägerlage. Das ist konkreter als „irgendein Wert“, ohne aus der
Zeichenform ein Wort zu machen.

Konfidenzen:

| These | Konfidenz |
|---|---:|
| gemeinsamer `EXACT_VALUE + COMMIT`-Mechanismus | .91 |
| latente Zustands-/Prozess-/Anwendungsslots | .69 |
| vier direkte sichtbare Stationsnamen | .24 |
| bloße generische Schreibkadenz/Stempelantworten ohne Sachwert | .39 |
| gewöhnliche abgekürzte Fachwörter am Zellenende | .43 |

## Versiegelte sichtbasierte Rollenkarte

Vor der Familienfreigabe wurden nur die 38 neutralen occurrence IDs, Seite,
Locus, Absatz/Record, Feldordinal, offizielles Bild und Seitenlayout benutzt.
Die Rollenkarte enthielt keine Oberfläche, Tuple-ID oder Familienbezeichnung.

- Freeze-Datei:
  `CANDIDATE_V15_R3_VISUAL_ROLE_FREEZE.tsv`
- Freeze-Zeit: `2026-08-21T19:09:21+02:00`
- SHA-256:
  `ebba6a572e0bb282c789834d887f25f680e52af1c59827c096e543e2654dcbc6`
- 38/38 Vorkommen, eindeutige IDs `R3O01`–`R3O38`
- Bildquellen: offizielle Yale-IIIF-Canvases `1006221`, `1006222`, `1006224`
- Bild-SHA-256 bei der Prüfung: f81v `5065b133...`; f82r
  `81bd1aa1...`; f83r `3d5b04d7...`

Die Karte war bewusst konservativ. Die Zeichnungen gingen der Schrift voraus,
die Prosa fließt um sie herum, und es gibt bei den Zielzeilen keine eindeutigen
Leiterlinien. Deshalb wurde meist der ganze Absatz einer Bildzone zugeordnet,
nicht nachträglich jeder attraktive Einzelwert einer Figur.

| eingefrorene Rolle | n | HIGH | MEDIUM | LOW |
|---|---:|---:|---:|---:|
| `GENERAL_CONFIGURATION_OR_PAGE_OWNER` | 11 | 0 | 0 | 11 |
| `FIGURE_OR_BODY` | 11 | 0 | 7 | 4 |
| `JUNCTION_OR_INTERMEDIATE_STATION` | 8 | 0 | 8 | 0 |
| `VESSEL_POOL_OR_CONTAINER` | 4 | 0 | 4 | 0 |
| `CONDUIT_PATH_OR_FLOW` | 4 | 0 | 4 | 0 |

`TERMINAL_OUTLET_OR_ENDPOINT` und `VISUALLY_UNOWNED` erhielten keine
Zielposition. Das ist kein Umverteilen nach Reveal: Bei keinem Zielabsatz war
ein einzelner Auslass besser begründet als die breitere Apparaturzone; die
f81v- und f83r-R03-Blöcke bekamen die ausdrücklich erlaubte allgemeine
Seitenbesitzerrolle mit LOW statt einer erfundenen lokalen Station.
Als Sensitivitätsgrenze kann man sämtliche elf LOW-`GENERAL`-Fälle geschlossen
in `VISUALLY_UNOWNED` umbenennen: Dann ändert sich nur der Zeilenname der
späteren 5/1/5/0-Tabelle, keine Familienzählung, MI oder Schlussfolgerung. Die
visuell attraktiveren vier engen Rollen werden dadurch nicht stärker.

## Familien-Reveal und vollständige Buchführung

Der Post-Reveal-Join steht in
`CANDIDATE_V15_R3_VALUE_ROLE_JOIN.tsv`. Er enthält dieselben 38 IDs samt
Feldlänge, eingefrorener Rolle, Familie und formaler Oberfläche. Die Zählung
ist exakt `VAL-S=12`, `VAL-QE=10`, `VAL-Q=8`, `VAL-L=8`.

| sichtbare Rolle | VAL-S | VAL-QE | VAL-Q | VAL-L | n |
|---|---:|---:|---:|---:|---:|
| General/Page owner | 5 | 1 | 5 | 0 | 11 |
| Figure/body | 2 | 3 | 1 | 5 | 11 |
| Junction/intermediate | 3 | 3 | 2 | 0 | 8 |
| Vessel/pool/container | 0 | 3 | 0 | 1 | 4 |
| Conduit/path/flow | 2 | 0 | 0 | 2 | 4 |
| **gesamt** | **12** | **10** | **8** | **8** | **38** |

Es gibt attraktive Tendenzen: `VAL-QE` häuft sich im Beckenblock, `VAL-L` bei
Figur/Leitung, `VAL-Q` in allgemeinen Konfigurationen. Aber keine davon ist
ein sichtbares Namensschild. Schon im selben Rollenblock stehen mehrere Werte:
f83r-R02/FIGURE enthält alle vier Familien, f83r-R04/JUNCTION drei und
f83r-R03/GENERAL drei. Ein Wert kann daher nicht schlicht „FIGUR“, „BECKEN“
oder „LEITUNG“ heißen.

## Kontrollen

Ich verglich die Familienidentität mit den eingefrorenen Rollen und den schon
vorhandenen Formularmerkmalen. Mutual information (MI) ist hier nur eine
deskriptive Klein-N-Zahl; die Permutation mischt die vier Familienhäufigkeiten
20.000-mal.

| Prädiktor | MI (bit) | globale Permutations-p | In-sample Mehrheits-Treffer |
|---|---:|---:|---:|
| sichtbare Rolle | .551 | .0097 | 18/38 |
| Seite | .335 | .0130 | 16/38 |
| Feldordinal | .312 | .4626 | 17/38 |
| Feldlänge | .277 | .7098 | 16/38 |
| Seite×Absatz („copied stencil“-Proxy) | .770 | .0994 | 21/38 |

Der schöne globale Rollenwert ist **nicht unabhängig**: Rollen wurden
absatzweise eingefroren und die Familien sind seiten-/absatzlokal. Nach
Permutation nur innerhalb derselben Seite fällt der Rollenwert auf `p=.1003`;
innerhalb eines Absatzes gibt es praktisch keine Rollenbeweglichkeit. Ein
Leave-one-occurrence-out-Mehrheitsdecoder erreicht mit Rolle nur `8/38`, mit
Seite×Absatz `14/38` (globale Mehrheitsbasis `12/38`). Damit gewinnt sichtbare
Rolle nicht gegen den Stempel-/Absatzrivalen. Feldlänge und Ordinal erklären
die Auswahl ebenfalls nicht.

Die äußere Wrapperklasse ist sogar deterministisch mit dem Wertdeck verwoben:
`Q` trägt alle 10 `VAL-QE` und 8 `VAL-Q`, `L` alle 8 `VAL-L`, und die
`S/CH/T`-Realisierungen alle 12 `VAL-S` (MI `1.509` bit). Das ist jedoch kein
unabhängiger Sachkontrollwert, sondern Teil der exakten Kartenidentität. Es
zeigt: Der Schreiber erkennt die Wertklasse an der ganzen Karte; das Bild
ersetzt sie nicht.

## Konkrete, vorläufige Werttaxonomie

Ich behalte vier in einer Werkstatt lehrbare Arbeitsglossen. Sie sind
Kontextklassen, keine englischen Lexeme:

| Familie | ausführbare Arbeitsglosse | Konfidenz | Grund / Grenze |
|---|---|---:|---|
| `VAL-Q` | `BASE_CONFIGURATION` — Grundmodus/gewöhnliche Einstellung | .46 | konzentriert in allgemeinen und Junction-Blöcken; wiederholt sich in benachbarten Slots, aber fehlt f82r |
| `VAL-QE` | `MARKED_APPLICATION` — angewandter/gefüllter markierter Modus | .51 | stark auf f82r und im Beckenblock; f82r.27 wiederholt ihn; kein Stoff oder Badname folgt |
| `VAL-S` | `ACTIVE_OR_RESULT_STATE` — gesetzte Arbeits-/Ergebnislage | .49 | breiteste Familie, häufiger Ende befüllter Felder und in mehreren Apparaturzonen; zu mobil für ein sichtbares Objekt |
| `VAL-L` | `HELD_OR_CARRIED_STATE` — gehaltene/gebundene Trägerlage | .47 | singletonreich, Figur/Leitung/Becken statt allgemeiner Konfiguration; nicht exklusiv genug für „Leitung“ oder „Auslass“ |

Die engste gemeinsame Taxonomie lautet somit:

```text
Q/QE = zwei verwandte Konfigurations- oder Anwendungsmodi
S    = gesetzte Arbeits-/Ergebnislage
L    = gehaltene/gebundene Trägerlage
```

Diese Bedeutungen dürfen explorativ stehen bleiben. Sie werden erst verworfen,
wenn weitere feste Vorkommen einer Glosse klar widersprechen oder ein kleineres
Modell die Wiederholungen, Singleton-Zellen und Verteilungen besser erklärt.

## Ausführbarer Encoder und Decoder

### Encoder

```text
1. Wähle aus Bild und Absatzstempel das aktive Objekt H.
2. Öffne den nächsten im Stempel erwarteten Slot K.
3. Falls K qualifiziert wird, schreibe die bekannten Qualifikationskarten.
4. Wähle genau eine Antwort aus {Q, QE, S, L} oder dem übrigen lokalen Deck.
5. Schreibe die exakte Ganzkarte in einer lokal lizenzierten Oberfläche.
6. Hänge DY als COMMIT an und gehe zum nächsten Slot.
7. Brauchen zwei Slots dieselbe Antwort, kopiere dieselbe Wertkarte erneut;
   verwende kein bloßes Ditto, sofern der Stempel die Wiederholung ausschreibt.
```

### Decoder

```text
1. Segmentiere die physische Zeile in Felder.
2. Markiere ein Feld mit finalem attached DY als committed.
3. Lies die vollständige exakte Schlusskarte, nicht nur DY oder den Wrapper.
4. Schlage {Q, QE, S, L, OTHER} im lokalen Bio-Deck nach.
5. Kombiniere den Wert mit dem aus Bild/Absatz geerbten Slot K.
6. Gib bei unbekanntem K aus: "K = VALUE"; erfinde keinen Stoff, Körperteil,
   Betrag, Weg oder Stationsnamen.
```

Der Decoder scheitert bewusst, wenn man nur ein Bildobjekt oder nur den
Wrapper kennt. Er kann den fehlenden Slotnamen derzeit nicht rekonstruieren.

## f82r.27: sieben Zellen

```text
Feld:       1 | 2     | 3  | 4 | 5 | 6  | 7
Karten:     1 | 2     | 1  | 1 | 1 | 1  | 1
Werte:      A | B+b   | QE | D | E | QE | F
Bildrolle:  VESSEL_POOL_OR_CONTAINER für alle sieben Slots (MEDIUM)
```

Die Zellen 3 und 6 besitzen damit **vergleichbare breite sichtbare Rollen**,
aber nicht zwei unabhängig lokalisierte gleiche Stationen: Die Gleichheit
entsteht innerhalb desselben Absatzes über dem gemeinsamen Becken. Die
brauchbarste Lesung ist: zwei verschiedene, vom Stempel vorgegebene Slots
erhalten denselben markierten Anwendungsmodus `QE`. Das kann etwa zwei
Teilnehmer-, Phasen- oder Anschlusspositionen parallel konfigurieren; es beweist
weder dieselbe Flüssigkeit noch dieselbe Körperstelle.

## Drei fortlaufende Registerlesungen

Diese Lesungen sind Werkstatt-Rücklesungen, kein Plaintext.

### f81v, Zeilen 17–18

> Für die allgemeine Konfiguration des großen gemeinsamen Beckens: beende eine
> qualifizierte Zelle mit Arbeits-/Ergebnislage `S`. In der nächsten Zeile
> verbinde die zwei lokalen Angaben unter dem aktiven Bezug und bestätige
> wieder `S`; setze anschließend für zwei aufeinanderfolgende geerbte Slots
> zweimal den Grundmodus `Q`. Der Rest der Zeile bleibt offen.

Die Wiederholung `Q,Q` spricht für zwei gleiche Antworten, nicht für zwei
sichtbare gleichnamige Stationen.

### f82r, Zeile 27

> Im Stempel des unteren Beckenrecords bestätige A; bestätige B mit seiner
> Qualifikation b; setze für den dritten Slot den markierten Anwendungsmodus
> `QE`; bestätige D und E; setze im sechsten Slot erneut exakt `QE`; bestätige
> zuletzt F. Alle sieben Zellen sind geschlossen.

### f83r, Zeilen 25–28

> Im Junction-/Kopplungsrecord setze zuerst `QE`. Im nächsten Feld folgen zwei
> lokale Angaben und der Grundmodus `Q`. Danach endet eine längere
> Konfigurationszelle in `S`; die nächste Zeile bestätigt erneut `QE`. In der
> folgenden Zelle erscheint nochmals `Q`; anschließend wird ein weiterer Slot
> mit `S` bestätigt und die Zeile läuft in einen offenen Rest aus.

Gerade dieser Record zeigt im selben sichtbaren Junction-Rahmen `QE`, `Q` und
`S`. Die Werte unterscheiden daher latente Antworten innerhalb einer
Apparatur, nicht drei gezeichnete Objektklassen.

## Stärkster Rivale und Scheiterfälle

Der stärkste Rivale ist ein **kopierter Formular-/Kadenzstempel mit gewöhnlich
abgekürzten Schlusswörtern**. Danach sind Q/QE/S/L häufige fachsprachliche
Wörter oder Modellantworten, die wegen Absatzvorlage und verfügbarer Zeilenbreite
wiederkehren; DY markiert nur eine normale Endform. Dieser Rivale erklärt die
starke Seite×Absatz-Bindung und gewinnt derzeit gegen eine direkte visuelle
Stationskarte.

Das Registermodell bleibt dennoch nützlich, weil es die 16 Ein-Karten-Zellen,
exakte Wiederholungen und die gemeinsame COMMIT-Schicht mit einer ausführbaren
Regel erklärt. Es scheitert oder muss enger werden, wenn:

1. dieselbe Familie auf festen Seiten systematisch gegensätzliche
   Zustands-/Anwendungswerte tragen muss;
2. Wiederholungen vollständig durch kopierte Zeilenstempel vorhergesagt werden
   und keine Slotauswahl übrig bleibt;
3. eine Familie als gewöhnliches Satzschlusswort in offenen, nichtzelligen
   Bio-Prosaumgebungen dominiert;
4. ein sichtbar eindeutig eigener Stationssatz zeigt, dass unterschiedliche
   Familien immer nur verschiedene gezeichnete Stationen benennen.

## Feste Vorhersagen innerhalb der drei Seiten

1. Weitere Auswertung derselben Absätze soll **mehrere Familien innerhalb einer
   sichtbaren Rolle**, aber stabilere Auswahl an wiederkehrenden Stempelstellen
   finden.
2. `VAL-Q` und `VAL-QE` sollen sich als verwandte, aber austauschbare
   Modusantworten verhalten; eine starre Rangfolge oder binäre Skala wird nicht
   erwartet.
3. `VAL-L` soll in geerbten oder ein-kartigen Slots überproportional bleiben,
   ohne ausschließlich an Leitungen oder Körper gebunden zu sein.
4. `VAL-S` soll weiter häufiger ein bereits befülltes Feld abschließen als
   `VAL-L/QE`; es darf aber auch als vollständige Singleton-Antwort stehen.
5. Bei einer neuen, unabhängig eindeutig segmentierten Doppelstation auf den
   festen Seiten wäre gleicher Wert in beiden Slots Unterstützung für
   parallele Konfiguration; verschiedene Werte wären mit Zustandsbelegung
   ebenfalls vereinbar, aber gegen einen direkten Stationsnamen.

## Seal und Evidenzgrenze

Verwendet wurden ausschließlich f81v, f82r und f83r, ihre drei offiziellen
Bilder sowie schon erlaubte f84-freie Layout-/Formaldaten. f84 und f84r blieben
versiegelt. ZL3b/IT2a/RF1b wurden als alternative Lesungen eines Manuskripts,
nicht als Replikationen behandelt. Keine Zeichenform erhielt über Klang,
Buchstabenähnlichkeit, OCR oder automatisches Bildlabel eine Bedeutung.
