# V49 R2 — historisch begrenzte atomare Glossen

## Ergebnis in einem Satz

Die V48-Stammglossen werden nicht nur gekürzt, sondern nach ihrem Typ
bereinigt: **fünf schwache Einwort-Hostkandidaten, neun atomisierte
Ganzkartenlabels und für den Rest `UNBEKANNT`**. Besonders entscheidend sind:

```text
CHOR = UNBEKANNT
CHO  = UNBEKANNT; nicht PFLANZE
CHEY = ANTEIL?       (schwacher Kandidat)
OK   = ITEM?         (stärkster Formelkandidat)
OR   = ANSATZ?       (vorläufiger Inhaltskandidat)
AL   = ZU?           (schwacher Relationskandidat)
E    = BIS?          (schwacher Gatterkandidat)
OT   = UNBEKANNT
L    = UNBEKANNT
AIIN = MASS?         (Ganzkarte, kein Stamm)
EY   = FERTIG?       (Ganzkarte, kein Stamm)
```

Das Fragezeichen ist epistemisch; es gehört nicht zur maschinellen Glosse.
Keine Form wird einer historischen Sprache oder Lautung zugewiesen.

## Historische Größenordnung

Der bisherige Fehler bestand darin, die vollständige moderne
Kontextparaphrase einer Karte als Bedeutung ihres PAGE_HOSTs zu behandeln.
Historische Vergleichspraxis erlaubt ein deutlich engeres, aber nicht völlig
starres Spektrum:

1. Die CoReMA-Editionsrichtlinien modellieren Abbreviaturen als graphische
   Kürzung plus Expansion; ihr Minimalbeispiel expandiert ein gekürztes
   `Item`. Sie unterscheiden zudem Abbreviaturzeichen, Brevigraphen und
   Kontraktionen. Das normale Editionsziel ist also eine Wortform oder ein
   Teil einer Wortform, nicht eine aus dem Rezeptkontext erfundene
   Ereignisbeschreibung.  
   Quelle: [CoReMA, Editorial Decisions](https://gams.uni-graz.at/o%3Acorema.editorialdec).

2. Cappellis *Lexicon abbreviaturarum* ist ausdrücklich nach Abbreviatur und
   **whole word** durchsuchbar. Das bestätigt die lexikalische
   Nachschlagepraxis, beweist aber keine bestimmte Voynich-Sprache.  
   Quelle: [Cappelli digitale](https://www.litterae.eu/cappelli/en.php).

3. Spätmittelalterliche praktische Handschriften können eigene technische
   Zeichen verwenden. Für das Ashmole-Miszellan beschreibt eine historische
   Studie apothekarische Zeichen, die einzelne Gewichte wie Skrupel oder
   Drachme vertreten. Der Bodleian-Katalog zu Trinity College MS 9 verzeichnet
   entsprechend Folgen aus `Recipe`, Gewichtssymbol und Zahl. Ein Zeichen kann
   also sehr wohl eine technische Einheit tragen.  
   Quellen: [Journal of British Studies](https://www.cambridge.org/core/journals/journal-of-british-studies/article/here-is-a-good-boke-to-lerne-practical-books-the-coming-of-the-press-and-the-search-for-knowledge-ca-14001560/8217EBC4F6CE53F1084709587B7C2E12/share/a024150fe1501e59df5b45628147fdd3df550196),
   [Bodleian medieval manuscript catalogue, Trinity College MS 9](https://medieval.bodleian.ox.ac.uk/pdfs/trinity/MS_9.pdf).

4. Ein fast zeitgleicher medizinisch-alchemistischer Codex von 1443 schreibt
   Rezeptanweisungen als Abfolge von `Recipe`, Stoffen, Verknüpfungen und
   Handlungsformen; ein norditalienisches Receptarium aus der Mitte des 15.
   Jahrhunderts zeigt dieselbe getrennte Rezeptstruktur. Das ist mit kurzen
   Wort-, Formel- und Einheitensiglen vereinbar, aber kein Vorbild dafür, einen
   Host als „Pflanzenmaterial zeitgebunden beschaffen“ zu glossieren.  
   Quellen: [Wellcome MS, 1443](https://wellcomecollection.org/works/nkqqy37b),
   [Wellcome MS.683](https://wellcomecollection.org/works/w6ne7k4t).

5. Komplexere Kurzschriftsysteme sind historisch real: das British-Library-
   *Lexicon Tironianum* beschreibt eine mittelalterliche Variante mit rund
   4.000 Zeichen. Das erlaubt prinzipiell gelernte Ganzzeichen, aber nicht die
   freie Wahl einer jeweils anderen Kontextparaphrase.  
   Quelle: [British Library, Add MS 21164](https://searcharchives.bl.uk/catalog/032-002091538).

Die Regel „höchstens ein Wort/Operator“ ist daher **eine konservative
Sidequest-Inferenzregel**, kein behauptetes universales Gesetz mittelalterlicher
Schrift. Ein längeres festes Formelsiglum wäre historisch möglich, müsste aber
als dieselbe feste Expansion über seine Belege hinweg motiviert sein.

## Einzelentscheidungen

### `CHOR` und `CHO`

`CHOR` ist im GDT327-Modell ein eigener PAGE_HOST. Die sichtbare Zeichenfolge
darf nicht ohne neue Evidenz als `CHO + R` gelesen werden. `CHO` selbst besitzt
zwei Karten, deren bisherige lokale Lesungen „Waldort“ und „Abkühlen“ lauten.
Damit ist `CHO = Pflanze` ausgeschlossen.

Die zwei `CHOR`-Karten wurden beide in bereits spekulativen Herbal-Sätzen mit
Sammeln verbunden:

```text
qotchor / otchor  → lokal „vor der Blüte gesammelt“
chochor           → lokal „im Frühjahr sammeln“
```

Diese Übereinstimmung ist kein unabhängiger Beleg, weil gerade aus diesen
Sätzen die V48-Glosse abstrahiert wurde. `SAMMELN?` wäre zwar die einzig
zulässige atomare Kurzfassung, wird in R2 aber **nicht** als Stammwert
übernommen. Endstatus: `UNBEKANNT / WHOLE_CARD_ONLY`.

### `CHEY`

V48 vermengte vier Beiträge: Auswahl + Materialklasse + Teil + Aufnahme. Nach
Abzug der stillen Bild- und Handlungsargumente bleibt höchstens:

```text
CHEY = ANTEIL?
```

Das passt zu den drei lokalen Lesungen auf f10r, f56r und f83r, stammt aber
weiterhin aus ihnen. Daher schwacher atomarer Kandidat, keine identifizierte
Vokabel und keine Lizenz für sichtbares `-ey`.

### `OK`

`OK` ist mit fünf Karten und 24 Ereignissen die beste echte Kombinationsserie.
`ARBEITSPOSTEN AKTIVIEREN` ist dennoch eine moderne Zwei-Komponenten-
Beschreibung. Historisch plausibler ist ein kurzer Eintragsmarker:

```text
OK = ITEM?
```

`ITEM` meint hier die anonyme Formularfunktion „weiterer Eintrag“, nicht die
Behauptung, dass der Quelltext Latein sei oder die Zeichen `ok` die Laute von
*item* codieren. Ein alternatives `NIMM` wäre semantisch enger und erklärt die
Eintragsposition schlechter.

### `OR`

`BEREITETES ERGEBNIS/ARBEITSMEDIUM` vereint zwei Kategorien. Die kleinste
brauchbare Werkstattglosse ist:

```text
OR = ANSATZ?
```

Sie kann Material während und nach der Bereitung bezeichnen. Die Evidenz bleibt
schwach: zwei Karten, acht Ereignisse, ohne extern identifizierten Stoff.

### `AL` und `E`

Beide komplexen Glossen lassen sich ohne stilles Objekt atomisieren:

```text
AL = ZU?
E  = BIS?
```

`ZU` trägt nur eine gerichtete Relation, nicht Zielart oder Parallelstation.
`BIS` trägt nur das Gatter, nicht Handlung, Zustand oder Zeitspanne. Beide sind
schwache Funktionskandidaten; die früheren semantischen Transferexperimente
haben keinen solchen Voynich-Wert bewiesen.

### `OT` und `L`

Für `OT` wechseln die lokalen Lesungen zwischen Dauer, Ort, Quelle und Weg.
Für `L` wechseln sie zwischen Öl, Abziehen, Kochen, Ablauf und Fortsetzung.
Das lässt sich nicht ehrlich auf jeweils ein Wort reduzieren. Beide gehen auf
`UNBEKANNT` zurück. Die Parserzustände `FRAME-O` und `FRAME-OT` bleiben als
formale Koordinaten sichtbar, aber bedeutungslos.

### `AIIN` und `EY`

Beide besitzen im festen Panel jeweils nur eine exakte Kartenart. Sie sind
deshalb keine Wortstämme:

```text
AIIN = MASS?     [Ganzkarte]
EY   = FERTIG?   [Ganzkarte]
```

`MASS` ist durch historische technische Einheitensiglen als Typ plausibel,
nicht durch einen identifizierten Voynich-Wert. `FERTIG` ist die kürzeste
gemeinsame Endzustandslesung; `KLAR`, `FLÜSSIGKEIT` und „läuft ab“ gehören
ausdrücklich nur zur lokalen f11r-Paraphrase.

### Übrige wiederkehrende Ganzkarten

Auch die sieben übrigen V48-Kartenlabels werden lediglich auf ein Wort
reduziert. Sie werden dadurch **nicht** zu Stämmen:

| Ganzkarte | atomisierte lokale Arbeitshilfe | Status |
|---|---|---|
| `OKY` | `NUTZE?` | schwache Ganzkarte |
| `LCHE` | `ABLASS?` | schwache Ganzkarte |
| `OKE` | `SPÜLE?` | schwache Ganzkarte |
| `CTHY` | `BEREIT?` | schwache Ganzkarte |
| `OKEEY` | `LAUWARM?` | schwache Ganzkarte |
| `CKHY` | `VERBINDUNG?` | schwache Ganzkarte |
| `OLOR` | `REST?` | schwache Ganzkarte |

Diese Labels sind nur kürzere Nachfolger der lokalen V48-Paraphrasen. Sie
besitzen keine unabhängige historische Identifikation und lizenzieren keine
Zerlegung ihrer sichtbaren Zeichenfolgen.

## Vollständige Revision

Die Neufassung hält zwei Ebenen auseinander:

```text
r2_atomic_literal_German        = wiederverwendbarer Einwort-Kandidat oder UNBEKANNT
local_creative_expansion_German = weiterhin lesbare, seitenlokale Werkstattparaphrase
```

Die lokale Paraphrase darf kein Beleg für den atomaren Wert sein. Die formalen
Koordinaten werden nur noch als `FORMAL-O`, `FORMAL-OT`, `FORMAL-D`, `R-*`,
`SCHLUSS` und `SONDERSCHLUSS` ausgegeben; ihre alten deutschen Satzfragmente
sind entfernt.

Artefakte:

- `V49_R2_HISTORICAL_ATOMIC_CANDIDATES.tsv`;
- `V49_R2_HISTORICAL_ATOMIC_173_CARD_DICTIONARY.tsv`;
- `V49_R2_HISTORICAL_ATOMIC_381_EVENT_INTERLINEAR.tsv`;
- `V49_R2_HISTORICAL_ATOMIC_135_FIELD_TRANSLATION.tsv`;
- `V49_R2_VALIDATION.json`.

Validiert sind 173 Karten, 381 Ereignisse und 135 Felder. 151 Karten bleiben
auf Hostebene unbekannt. `f84` und `f84r` wurden nicht geöffnet.
