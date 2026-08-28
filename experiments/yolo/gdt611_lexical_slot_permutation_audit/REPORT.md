# GDT611 lexical-slot permutation audit

## Entscheidung

**`NO_STABLE_LEXICAL_OR_FAMILY_SLOT__FORMAL_FRAME_RELATIONS_ONLY`**

Die gezielte Suche liefert keinen konkreten Schlüssel für `WASSER`, `WEIN`,
`OEL`, `SALZ`, `WURZEL`, `BLATT`, `BLUETE`, `SAMEN`, `REIBEN`,
`KOCHEN/ERWAERMEN`, `TROCKNEN`, `EINWEICHEN`, `GEFAESS`, `BAD`,
`KRANKHEIT`, `FRAU` oder `HEILUNG`. Null von 17 Default-Zuweisungen besteht
den Lexem-Gate; auch null von vier Bedeutungsfamilien besteht den vorab
festgelegten held-Folio-, exakten Frame-, Section-Null- und Restart-Gate.

Der Lauf findet dennoch drei konkrete formale Austauschspuren:

1. `Cor`, `T+ol` und `Ty` wiederholen mehrere identische äußere Frames in train
   und held, besonders mit `daN` links oder rechts.
2. `qokaI` und `qol` wiederholen acht identische lokale Frames. Ihre
   Section-Verteilung transportiert jedoch nicht: viele train-Zeugen liegen in
   `B`, die held-Zeugen überwiegend in `S`.
3. `ok+eol` und `qok+eol` bilden das sauberste innere Paradigma:
   `0/2:*+eol` trägt train `33/26` und held `10/11` Ereignisse.

Diese Relationen stützen “austauschbare Form im selben lokalen Slot”. Sie
stützen keine der verlangten Bedeutungen gegenüber ihren Alternativen. Der
exakte Default `ok+eol=BAD`, `qok+eol=KRANKHEIT` ist beispielsweise
score-identisch zu `ok+eol=KRANKHEIT`, `qok+eol=BAD` und zu jeder weiteren
Umbenennung innerhalb der Record-/Entity-Familie.

## Begrenzter Umfang

Verwendet wurden ausschließlich die veröffentlichten f84/f84r-freien
GDT605/GDT606-Artefakte und die formalen GDT608-Rollen. Es wurde keine neue
Transkription abgefragt, keine Seite oder Abbildung geöffnet und kein
Workshop-Wert gelesen.

| Eingabe | SHA-256 |
|---|---|
| `guarded_rows.tsv` | `d6674f3d54edc49590c884b5d703cb032b966c1abd4da6338093795ce1f31ef9` |
| `unit_sequences.json` | `3ee0841e211314b72719acbbf79ed3a6dc7bfc3c157734f54dbdac92ac458fdf` |
| GDT608 `stable_stem_role_summary.tsv` | `4c385f59520e4b9ebc9c75274eb1ff8a28efc340b12ccad29754e085d866012b` |
| GDT608 `merge_tree.tsv` | `2098c71be9da13b483cf2561e06412276d8c60aa32e72520e8877f8f5d53090a` |
| Preregistration | `631e3ed1cf3be99279da54cb4b9df0ebddbd9919260789ad15c02fa7853b4462` |

Der Strom umfasst 4,165 guarded Zeilen, 20,336 train- und 9,838 held-Chunks
auf unveränderten 68/23 physischen Folios. Alle page- und physical-folio-Felder
wurden auf `f84*` geprüft; Treffer: null.

Der Route-Check traf vor allem die geschlossene Familie
`LEXICAL_GLOSSES_FROM_FORMAL_ROLES` sowie nichtkanonische Workshop-Routen. Die
Workshop-Bedeutungen wurden nicht geöffnet. Die geschlossene Warnung ist direkt
einschlägig: formale Träger und Richtungen besitzen ohne unabhängigen Anker
keine Wortbedeutung.

## Was genau getestet wurde

Ein Träger ist eine vollständige Hard-Chunk-Sequenz der finalen GDT605-Units,
zum Beispiel `qok+eol`. Ein Träger musste train mindestens 12-mal, held
mindestens 6-mal und auf mindestens 4/2 physischen Folios auftreten. Das ergibt
200 zulässige Träger.

Lokale Austauschbelege sind strikt exakt:

- internes Ein-Unit-Maskenframe, etwa `0/2:*+eol`;
- identischer vorheriger Chunk auf derselben physischen Zeile;
- identischer folgender Chunk;
- identisches zweiseitiges Nachbarframe.

Ein held-Frame zählt nur, wenn dasselbe Trägerpaar bereits in train dasselbe
exakte Frame teilt. Held-only Ähnlichkeit ist kein Transferbeleg.

GDT608 wird nur syntaktisch verwendet:

- `q`, `qo`, `qok`, `qol`, `qot`: formale linke Entry-Familie;
- `y`, `dy`, `aN` und ihre registrierten rechten Kinder: formale
  Closure-Familien;
- `k`, `lk`, `ok`, `olk`, `yk`: formale nonterminale `k`-Familie.

Diese Mengen erhalten keine Bedeutung und keine POS-Bezeichnung. Die
Operationskandidaten werden nur durch Zeilenanfang plus Entry-Profil gewählt.

Die 975 stärksten train-Kanten perkolieren über alle 200 zulässigen Träger zu
einer einzigen Komponente. Das ist selbst ein negativer Befund: einseitige
lokale Nachbarwiederholung ist zu breit, um semantische Inseln zu isolieren.
Die konkreten Paarframes bleiben auswertbar, die Komponentenzugehörigkeit aber
ist kein Bedeutungsbeleg.

## Vollständiger Mini-Wörterbuch-Kandidat

Die Bedeutungsnamen sind reproduzierbare Defaults: innerhalb jeder
train-only gewählten Familie werden sie nach absteigender train-Frequenz
vergeben. Fragezeichen sind obligatorisch. `Score` ist für Section-Familien ein
Carrier-versus-Rest Log-Odds-Kontrast und für Operationen der eingefrorene
formale Entry-/Zeilenanfang-Z-Score. `p held` stammt aus 1,000
physical-folio-erhaltenden Section-Permutationen; für Operationen ist er nicht
anwendbar. `Frames` zählt exakt wiederverwendete held-Frames mit einem anderen
ausgewählten Familienmitglied.

| Default | Träger | train/held n | Ziel | Score train→held | p held | Frames | Restart | Urteil |
|---|---|---:|---|---:|---:|---:|---:|---|
| `REIBEN?` | `qot+Cy` | 50/11 | formal Entry | 4.246→2.729 | — | 0 | .335 | Default-only |
| `KOCHEN_ERWAERMEN?` | `t+Cedy` | 22/9 | formal Entry | 4.500→4.439 | — | 0 | .640 | Default-only |
| `TROCKNEN?` | `qo+aN` | 12/9 | formal Entry | 4.200→2.863 | — | 0 | .500 | Default-only |
| `EINWEICHEN?` | `y+CEy` | 12/11 | formal Entry | 4.918→5.309 | — | 0 | .705 | Default-only |
| `WURZEL?` | `Cor` | 137/40 | `H` | 2.459→1.588 | .373 | 5 | .145 | Default-only |
| `BLATT?` | `Ty` | 75/16 | `H` | 4.218→2.803 | .386 | 3 | .980 | Default-only |
| `BLUETE?` | `T+ol` | 35/15 | `H` | 3.444→2.159 | .614 | 4 | .780 | Default-only |
| `SAMEN?` | `ot+Col` | 17/8 | `H` | 3.862→2.229 | .193 | 0 | .960 | Default-only |
| `WASSER?` | `qokaI` | 198/74 | `P|B` | 2.075→**-0.554** | .534 | 11 | .180 | held sign reversal |
| `WEIN?` | `qol` | 72/28 | `P|B` | 2.957→1.643 | .407 | 8 | .965 | Default-only |
| `OEL?` | `ol+Cedy` | 26/13 | `P|B` | 2.286→0.676 | .645 | 0 | .475 | Default-only |
| `SALZ?` | `Se+Ky` | 20/11 | `P|B` | 2.924→0.255 | .707 | 3 | .785 | Default-only |
| `GEFAESS?` | `s+ol` | 36/6 | `B` | 1.717→1.775 | .402 | 0 | .145 | Default-only |
| `BAD?` | `ok+eol` | 33/10 | `P` | 3.222→0.990 | .444 | 1 | .705 | Default-only |
| `KRANKHEIT?` | `qok+eol` | 26/11 | `P` | 3.189→1.953 | **.0539** | 1 | .845 | engster Nichtbesteher |
| `FRAU?` | `Ce+Ty` | 16/8 | `B` | 2.183→0.238 | .841 | 0 | .075 | Default-only |
| `HEILUNG?` | `K+ey` | 16/7 | `P` | 2.797→1.370 | .433 | 0 | .535 | Default-only |

Keine Zeile besteht den vollständigen Familien-Gate. `qok+eol` ist der engste
Nichtbesteher: positives train/held `P`-Profil, zwei held-Zielfolios, Restart
.845 und das robuste `*+eol`-Frame, aber der vorab verlangte held-Nullwert liegt
bei `.053946`, nicht bei höchstens `.05`. Selbst ein knappes Bestehen hätte nur
eine `P`-kompatible Formfamilie geliefert, nicht das Wort `KRANKHEIT`.

Die maschinenlesbare vollständige Tabelle steht in
`mini_dictionary_candidates.tsv`; dort sind Section-Zählungen, Foliozahlen,
formale Shape-Flags, gematchte Kontrollen und alle benannten Alternativen
enthalten.

## Familienentscheidungen

| Familie | ausgewählt | Mitglieder bestanden | held Frame-Paare | Gate |
|---|---:|---:|---:|---|
| Operation | 4 | 0 | 0 | FAIL |
| Pflanzenteil | 4 | 0 | 3 | FAIL |
| Flüssigkeit/Material | 4 | 0 | 2 | FAIL |
| Record/Entity | 5 | 0 | 1 | FAIL |

### Operationen

Alle vier Träger haben im held-Strom positive formale Scores. Keiner kehrt aber
in mindestens 75% der 200 train-Folio-Bootstraps wieder; die Raten liegen bei
.335, .640, .500 und .705. Vor allem teilen die vier Kandidaten **null**
identische train→held Frames. Damit stützt die GDT608-Schablone lediglich
Entry-/Zeilenanfangsform, nicht `reiben` gegenüber `erwärmen`, `trocknen` oder
`einweichen`.

### Pflanzenteile

Alle vier train- und held-Kontraste zeigen positiv nach `H`. Konkrete
Frame-Wiederholungen existieren:

| Paar | exaktes Frame | train Zeugen | held Zeugen | Beispiel-Loci |
|---|---|---:|---:|---|
| `Cor ↔ T+ol` | links `daN` | 5/4 | 1/3 | train `f19v.10`/`f22r.3`; held `f30v.4`/`f28v.8` |
| `Cor ↔ T+ol` | rechts `daN` | 6/3 | 2/3 | train `f19r.12`/`f37v.11`; held `f23r.2`/`f18r.12` |
| `Cor ↔ Ty` | links `daN` | 5/10 | 1/1 | train `f19v.10`/`f11r.5`; held `f30v.4`/`f45v.2` |

Die held Section-Nullwerte bleiben trotzdem `.193` bis `.614`; die
Konzentration sitzt auf zu wenigen beziehungsweise nicht frei austauschbaren
physischen Folios. Selbst wenn `H` konventionell als pflanzenillustrierte
Section gelesen wird, besitzt kein Bild `Cor`, `Ty`, `T+ol` oder `ot+Col` als
Textlabel. Noch grundlegender: `WURZEL`, `BLATT`, `BLUETE` und `SAMEN` sagen im
vorliegenden Strom exakt dieselben Observablen voraus. Die vier Namen sind
untereinander permutation-symmetrisch.

### Flüssigkeiten und Materialien

Der stärkste lokale Austausch ist `qokaI ↔ qol` mit acht exakt gleichen
train→held Frames. Das ist kein Flüssigkeitsschlüssel, weil die Section-Richtung
driftet:

| Frame | train `qokaI`/`qol` | held `qokaI`/`qol` | konkrete Loci |
|---|---:|---:|---|
| links `Cey` | 6/3 | 2/3 | train `f79r.18`/`f104v.4`; held `f111v.31`/`f111v.32` |
| rechts `Cedy` | 9/10 | 4/4 | train `f75r.16`/`f104v.4`; held `f103r.13`/`f111v.32` |
| rechts `ol` | 8/1 | 2/2 | train `f75v.44`/`f75v.40`; held `f103v.37`/`f81r.22` |

`qokaI` hat train die Section-Zählung
`B:150,C:1,H:7,P:0,S:32,T:8`, held dagegen
`B:3,C:0,H:0,P:1,S:70,T:0`. Sein `P|B`-Score kehrt von `+2.075` auf
`-0.554` um; nach Ausschluss gemischter Section-Folios lautet der held-Wert
`-0.609`. Ein lokales Austauschparadigma ist also real, aber nicht an die
angezielte Section-Klasse gebunden. `WASSER`, `WEIN`, `OEL` und `SALZ` bleiben
vollständig vertauschbar.

### Gefäß, Bad, Krankheit, Frau, Heilung

Das sauberste innere Frame des ganzen Kandidatensatzes ist:

```text
0/2:*+eol
train: ok+eol=33, qok+eol=26
held:  ok+eol=10, qok+eol=11
train loci: f100r.25 / f100r.14  (beide P)
held loci:  f103r.10 / f103r.11  (beide S)
```

Damit ist die Ersetzung des ersten Elements vor `eol` belastbar. Der Wechsel
von `P`-train zu `S`-held verhindert eine einfache Section-Bedeutung; außerdem
liefert das Frame keine Beobachtung, die `BAD` von `KRANKHEIT`, `GEFAESS`,
`FRAU` oder `HEILUNG` unterscheidet. `Ce+Ty=FRAU?` ist ein besonders klares
Gegenbeispiel: train liegen 12/16 Ereignisse in `B`, held aber 8/8 in `S`;
Restart `.075`, held Section-Null `p=.841`, null Familienframes.

## Bildtyp- und Section-Grenze

Die erlaubten Artefakte enthalten Section-Codes, Hand, Currier-Code, Locus und
Folio, aber keine unabhängig besitzende Objektannotation für eine konkrete
Textsequenz. Deshalb bleiben `H`, `B`, `P`, `S`, `T`, `C` in den Scores opaque.

Auch bei der konventionellen Bildtyp-Lesart “H≈Herbal, B≈Figuren/Balneologie,
P≈Pharma” folgt nur eine schwache Kompatibilitätsfrage:

- `H` kann Pflanzenteil, Pflanzenname, Handlung, Material oder Beschreibung
  nicht unterscheiden;
- `B` kann Wasser, Bad, Frau, Krankheit, Heilung oder Gefäß nicht
  unterscheiden und besitzt im held-Split nur ein physisches Folio;
- `P` besitzt im held-Split zwei Folios und trennt Gefäß, Zutat, Krankheit und
  Handlung ebenfalls nicht.

Vier Folios tragen im guarded Strom mehr als einen Section-Code (`f66`, `f76`,
`f86`, held `f85`). Der primäre Section-Null schließt sie aus und berechnet
Beobachtung und 1,000 Permutationen auf 65/22 einheitlichen Folios neu. Der
dominant-Section-Lauf bleibt nur Diagnose. Diese Korrektur und der exakte
Frame-Reuse-Fix sind in `DEVIATIONS.md` festgehalten.

Kein held Section-Test erreicht `p<=.05`. Der kleinste Wert ist
`qok+eol`, `p=.053946`; alle Pflanzenteilwerte liegen bei `.193` bis `.614`,
alle Flüssigkeits-/Materialwerte bei `.407` bis `.707`.

## Gematchte Kontrollen

Jeder der 17 Defaults wurde mit dem nächsthäufigen zulässigen Träger gleicher
Sequenzlänge und gleicher q/y/k-Shape gematcht.

| Endpunkt | Kandidaten | Kontrollen | Kandidat besser |
|---|---:|---:|---:|
| held Frame-Token-Coverage | .4362 | .4169 | 7/17 Paare |
| train→held Section-JS, Bits (kleiner besser) | .2564 | .2218 | 7/17 Paare |

Die ausgewählten Kandidaten besitzen damit keinen besonderen
Wiederholungs-/Stabilitätsvorteil gegenüber bloß gleich häufigen, gleich
geformten Trägern. Die kleine mittlere Frame-Coverage-Differenz von `.0193`
kehrt auf Paarbasis sogar um: nur 7/17 Kandidaten gewinnen. Ihre
Section-Drift ist im Mittel größer, nicht kleiner.

## Exakte Permutations-Null

Für jede Familie wurden Original-, zyklische und umgekehrte Benennung
ausgeführt. Section-/Formalziel, Frameziel und kompletter
Likelihood-Signaturhash bleiben jeweils byte-identisch; Delta immer
`0.000000000`.

Die vier Familien besitzen zusammen

```text
4! × 4! × 4! × 5! = 1,658,880
```

exakt gleich bewertete Wörterbücher. Das ist keine Optimierungsschwäche,
sondern Nichtidentifizierbarkeit: Ohne eine beobachtete, unabhängig benannte
Wasser-, Blatt-, Frauen- oder Krankheitsreferenz enthält der interne Strom
keine Variable, an der die konkreten Namen hängen könnten.

## Konkreter held-Absatz

Die Absatzwahl war deterministisch: erst maximale Zahl von Dictionary-Hits,
dann unterschiedliche Träger, dann Zeilenzahl, dann Absatz-ID. Gewählt wurde
`f111v:p1`, Section `S`, mit 25 vollständigen Zeilen und 18 Hits:

- `qokaI` = `[WASSER?]` 14-mal;
- `qok+eol` = `[KRANKHEIT?]` zweimal;
- `qol` = `[WEIN?]` einmal;
- `Se+Ky` = `[SALZ?]` einmal.

Drei konkrete Zeilen:

```text
f111v.8
EVA: sho otchey cheol kechy chcthey okain ol l keey qokain checkhy chedar am
Units: So | ot+Cey | Ce+olk+e+Cy | C+T+ey | ok+aI | ol | lk+Ey |
       qokaI | Ce+Ky | Ce+dar+am
Default: ... | [WASSER?] | ...

f111v.21
EVA: sair air ain qol rar ain cheey lkeey lkain cheokain sheo qo qokain chear alam
Units/Default: s+air | air | aI | [WEIN?] | r+ar | aI | CEy | lk+Ey |
               lk+aI | Ce+ok+aI | Se+o | qo | [WASSER?] | Ce+ar | al+am

f111v.23
EVA: qokaiin sheckhy qokar chalkain chckhedy lcheol okaiin qokain cheol daiin lam
Units/Default: qokaN | [SALZ?] | qok+ar | C+al+k+aI | C+K+edy | l+Ceol |
               okaN | [WASSER?] | Ceol | daN | l+am
```

Dieser Absatz ist kein positiver “Rezept”-Beleg. Er ist das stärkste
Gegenbeispiel gegen eine flüssige Lesung von `qokaI`: Der Träger wurde wegen
train `P|B` gewählt, erscheint held aber 70-mal in `S` und dominiert gerade
dort den bestgedeckten Absatz. Ersetzt man `[WASSER?]` zyklisch durch
`[WEIN?]`, `[OEL?]` oder `[SALZ?]`, bleiben alle Scores unverändert.

Der vollständige Absatz mit jeder guarded EVA-Zeile und jeder Unit-Sequenz
steht in `HELD_PARAGRAPH.md` und `held_paragraph_witness.tsv`.

## Konkrete Gegenbeispiele

| Default | gehaltenes Gegenlocus | Grund |
|---|---|---|
| `WASSER?=qokaI` | `f103r.13`, `S` | `P|B`-Vorzeichen kehrt um; Restart .180 |
| `FRAU?=Ce+Ty` | `f103r.18`, `S` | train B-Schwerpunkt, held vollständig S; p=.841 |
| `SAMEN?=ot+Col` | `f1r.8`, `T` | positives H-Profil, aber null exakt wiederverwendete Familienframes |
| `REIBEN?=qot+Cy` | `f103r.26`, `S` | null Operationsframes; Restart .335 |
| `KRANKHEIT?=qok+eol` | `f103r.11`, `S` | starkes `*+eol`-Formparadigma, aber keine Krankheitsbeobachtung und p=.0539 |

`counterexamples.tsv` enthält für alle 17 Defaults das konkrete held-Locus,
die ganze EVA-Zeile, den nächstliegenden Austauschträger und dessen exakt
wiederverwendete Frames.

## Schluss

Die konkrete Antwort auf die verlangte Konkurrenzfrage lautet:

- `Cor/T+ol/Ty` werden gegenüber beliebigen seltenen Trägern als wiederkehrende
  H-gewichtete **Formen in gemeinsamen daN-Frames** gestützt; keine von ihnen
  wird als Wurzel, Blatt, Blüte oder Samen gestützt.
- `qokaI/qol` werden als lokal austauschbare **Formen** gestützt; die
  train→held Section-Umkehr widerspricht Wasser/Wein/Öl/Salz als stabiler
  Klasse.
- `ok+eol/qok+eol` werden stark als **inneres `*+eol`-Paradigma** gestützt;
  Bad/Krankheit/Gefäß/Frau/Heilung bleiben gleichwertige Namen.
- Für Reiben/Erwärmen/Trocknen/Einweichen besteht nicht einmal ein stabiles
  gemeinsames held-Frame-Paradigma.

Ein echter nächster Semantiktest müsste eine dieser bereits eingefrorenen
Paarrelationen gegen einen extern und unabhängig besitzenden Wiederholungsanker
prüfen, etwa eine vor der Stringanalyse nominierte, mehrfach beschriftete
Objekt-/Pflanzenteilrelation auf mehreren held Folios. Die internen
GDT605/GDT606-Daten allein können die 1,658,880 gleichwertigen Benennungen nicht
auswählen.

## Reproduzierbarkeit

- `PREREGISTRATION.md`: Auswahl, Nulls und Gates vor dem Lauf.
- `DEVIATIONS.md`: zwei guarded Implementierungskorrekturen.
- `analyze.py`: vollständige Rekonstruktion und Auswertung.
- `mini_dictionary_candidates.tsv`: alle 17 Defaults und Gegenalternativen.
- `transferred_frame_witnesses.tsv`: jedes exakte train→held Frame samt Loci.
- `family_summary.tsv`, `selected_family_pairs.tsv`: Familiengates.
- `section_nulls.tsv`: 1,000-fache einheitliche-Folio-Nulls.
- `bootstrap_stability.tsv`: 200 train-Folio-Restarts.
- `matched_frequency_controls.tsv`: Frequenz-/Shape-Kontrollen.
- `label_permutation_witness.tsv`: identische Benennungsscores.
- `HELD_PARAGRAPH.md`, `held_paragraph_witness.tsv`: vollständiger Absatz.
- `counterexamples.tsv`: alle konkreten held-Gegenbeispiele.
- `RESULT.json`, `ARTIFACT_MANIFEST.tsv`: kompakte Entscheidung und Hashes.
- `validate.py`, `VALIDATION.json`: unabhängige Rekonstruktion; **PASS 94/94**.
