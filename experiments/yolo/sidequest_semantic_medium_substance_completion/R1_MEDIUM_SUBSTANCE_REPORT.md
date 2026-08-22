# R1 — Stoff- und Flüssigkeitsabschluss aus Sicht eines Apotheker-Schreibers um 1420

## Ergebnis in einem Satz

Die beste knappe Werkstattordnung ist keine universelle Flüssigkeitssilbe, sondern eine kleine gelernte Stofftafel: **AIR = LAUFFLÜSSIGKEIT**, **CHEO = AUSZUG**, **OR = ZUBEREITUNG**, daneben getrennte Ganzkarten für **WEINSUD, KLARAUSZUG, SPÜLFLÜSSIGKEIT, BADZUSATZ, TRANK, BRUSTTRANK, WARMAUSGUSS, FRISCHWASSER, WARMWASSER** und **BADWASSER**. Eine Öl- oder Honigkarte lässt sich auf diesen Seiten nicht invariant setzen.

Das ist eine ausdrücklich kreative Sidequest-Arbeitstheorie, keine Entzifferungsbehauptung. Alle Bedeutungen sind kurze Werkstattdefaults; Besitzer, Bild und Nachbarn dürfen nur die lokale Handlung ergänzen.

## Arbeitsbereich

- Ausgangspunkt: aktive ausgewählte Anwendungsausgabe.
- Gelesene Textseiten: ausschließlich f10r, f11r, f55v, f56r, f81v, f82r und f83r.
- Keine neue Seite, keine neue Transkription und keine Astro-Uminterpretation.
- f84 und f84r blieben vollständig versiegelt.
- Exakte Kartenidentität hat Vorrang: dieselbe joint tuple erhält denselben Stoffkern.
- Satzhandlungen sind keine Stammwerte. `SCHOAL` heißt daher nicht mehr „in Wein kochen“, sondern kurz `WEINSUD`; Kochen/Bereiten ist die lokale Satzhandlung.

## Die geschlossene Stofftafel

| Karte/Komponente | Default | Ereignisse | Entscheidung |
|---|---:|---:|---|
| AIR in `chair, kair, okair, schedair, dairydy` | LAUFFLÜSSIGKEIT | 5 | produktiver gemeinsamer Stoffkern |
| CHEO in `chokcheo, cheoar` | AUSZUG | 2 | produktiver gemeinsamer Stoffkern |
| OR und OR-Komposita | ZUBEREITUNG | 13 | aktive Lesung bestätigt; nicht Öl |
| `dshedy` | FRISCHWASSER; SCHLUSS | 1 | gelernte Ganzkarte |
| `rsheal` | WARMWASSER | 1 | gelernte Ganzkarte |
| `shecthy` | BADWASSER | 1 | gelernte Ganzkarte, stärkster lokaler Wert |
| `schoal` | WEINSUD | 1 | gelernte Ganzkarte |
| `dl` | BADZUSATZ | 2 | wiederkehrende Ganzkarte |
| `cheey|shey` | KLARAUSZUG | 4 | aktive Lesung bestätigt |
| `tshey` | SPÜLFLÜSSIGKEIT | 1 | aktive Lesung bestätigt |
| `kchy` | TRANK | 1 | Satzverb aus Kartenwert entfernt |
| `kchoar` | BRUSTTRANK | 1 | aktive Ganzkarte bestätigt |
| `skar` | WARMAUSGUSS | 1 | kurze Ganzkarte statt Satzglosse |
| `cho|sho` | PFLANZENSTOFF | 4 | identische Karte vereinheitlicht |
| Öl | keine Karte | 0 | nicht erzwingen |
| Honig | keine Karte | 0 | frühere Lesung verworfen |

Die vollständige Aufstellung aller 23 Zielkarten mit sämtlichen Event-IDs, Aussagen und Seiten steht in `R1_MEDIUM_SUBSTANCE_PARADIGM.tsv`. Die Komponentenregeln und Grenzen stehen in `R1_MEDIUM_SUBSTANCE_COMPONENTS.tsv`.

## 1. AIR: nicht „Wasser“, sondern LAUFFLÜSSIGKEIT

Der gemeinsame Wert muss in fünf sehr verschiedenen Hüllen gleich bleiben:

| Event | Form | Seite | kurze Komposition | konkrete Lesung |
|---|---|---|---|---|
| E006 | `chair` | f10r | CH + AIR | Laufflüssigkeitszulauf |
| E103 | `kair` | f81v | K + AIR | Laufflüssigkeit |
| E260 | `okair` | f83r | OK + AIR | Laufflüssigkeit starten |
| E300 | `schedair` | f83r | S + CHED + AIR | Laufflüssigkeit führen |
| E351 | `dairydy` | f83r | D + AIR + Y + DY | Laufflüssigkeit abschließen |

`WASSER` wäre zu eng: Die Vorkommen liegen an Wurzelzubereitung, Becken, Lauf, Führung und Schluss. `FLÜSSIGKEIT` wäre zu breit: Das wiederkehrende Verhalten ist gerade der im Gang befindliche Lauf. `LAUFFLÜSSIGKEIT` ist deshalb der kürzeste Kern, der alle fünf Kompositionen überlebt.

## 2. CHEO: AUSZUG, nicht unbestimmte „Trägerflüssigkeit“

| Event | Form | Seite | Komposition | Lesung |
|---|---|---|---|---|
| E065 | `cheoar` | f55v | CHEO + AR | Auszug daraus entnehmen |
| E092 | `chokcheo` | f56r | OK + CHEO | Auszug zugeben |

Der Stoffkern ist in beiden Fällen schlicht `AUSZUG`. Das erste Umfeld nimmt ihn aus einem Vorrat, das zweite gibt ihn in den laufenden Posten. Damit ist CHEO konkreter als „Medium“, ohne behaupten zu müssen, beide Ereignisse bezeichneten dieselbe Flüssigkeit.

`CHEO` und `SHEY` werden nicht zusammengelegt:

- CHEO = der entnommene oder zugegebene Auszug;
- SHEY = das klare Ergebnis nach Auswringen, Ruhen und Nachseihen.

Die Unterscheidung entspricht dem Werkstattablauf **Auszug einsetzen → trennen → Klarauszug erhalten**, nicht zwei synonymen Wörterbuchkarten.

## 3. OR bleibt ZUBEREITUNG

Die 13 Ereignisse bilden die bereits aktive kleine Kompositionstafel:

- `OR` = Zubereitung;
- `CHO+OR` = Pflanzenzubereitung;
- `OL+OR` = vorige Zubereitung;
- `OT+OR` = nächste Zubereitung;
- `OR+AIN` = Portion der Zubereitung.

Das ist stärker als die verführerische Lesung `OR = Öl`: Öl erklärt weder „vorige/nächste“ noch die Portion noch die nackte wiederkehrende Prozessposition. OR ist ein benannter Ansatz beziehungsweise eine Zubereitung, kein einzelnes Ingrediens.

## 4. Wasser ist eine gelernte Dreierkarte, kein künstlicher Stamm

Auf den festen Seiten gibt es drei lokale Wassernamen, aber keinen belastbaren sichtbaren gemeinsamen Wasserstamm:

1. `dshedy` in B2-S007: **FRISCHWASSER; SCHLUSS** — „Frischwasser zugeben; Schluss.“
2. `rsheal` in B2-S017: **WARMWASSER** — „Warmwasser eingießen; an der zweiten Öffnung wiederholen und schließen.“
3. `shecthy` in B3-S021: **BADWASSER** — in einer Folge aus Maß, Arbeitsstelle, Ruhe-/Absetzstelle und anschließendem Umsetzen.

`SHECTHY = BADWASSER` ist bewusst konkreter als das frühere doppelte „warmes Wasser“. Der umgebende Stations- und Ruheablauf passt zu einem angesetzten Bad. Es bleibt eine gelernte Ganzkarte: Aus `SH`, `CTH` oder `Y` wird kein globales Wasserzeichen gemacht.

Stärkster Rivale für SHECTHY ist `ANGESetzTES WASSER`. Sollte ein späteres Vorkommen ohne Badbesitzer erscheinen, wäre dies der erste Ersatzkandidat. Auf den gegenwärtigen Seiten macht `BADWASSER` jedoch den B3-Ablauf am knappsten lesbar.

## 5. Wein, Sud, Badzusatz und Ausguss

### SCHOAL = WEINSUD

Die einzige Karte liegt genau in der H3-Trennkette:

> Pflanzenstoff → **Weinsud** → auswringen → vorgeschriebene Standzeit → nachseihen → Klarauszug → abkühlen/schließen.

`WEINSUD` ist eine plausible gelernte Rezeptkarte. Das frühere „in Wein kochen“ war als Einzelwortwert zu lang und vermischte Stoff mit Tätigkeit. Weder `O`, `OL` noch `AL` werden dadurch zu Weinbestandteilen.

### DL = BADZUSATZ

`dl` steht zweimal im f81v-Badzyklus und behält beide Male denselben Stoffwert. Das genügt für eine wiederkehrende Ganzkarte, nicht für eine produktive Abkürzung `D` oder `L`.

### SKAR = WARMAUSGUSS

Die terminale Folge B4-S016 lautet jetzt knapp:

> weitere Portion zugeben → Stelle → **Warmausguss** → ruhen/absetzen; Schluss.

`Warmausguss` verbindet Stoffzustand und Werkstattgebrauch in einem zeitgemäß plausiblen Nomenklatorwort, ohne einen freien SK- oder AR-Stoffstamm zu erfinden.

## 6. Die Honigkorrektur

Die größte konkrete Revision ist negativ. Die exakte Karte `2cc054357a929df85f64` hat vier Ereignisse und die Oberflächen `cho|sho`:

| Event | bisherige Kontextlesung | jetzt invariantes Kartenmaterial |
|---|---|---|
| E075 | ganzes Kraut sammeln | Pflanzenstoff |
| E078 | klebrige Blätter zerstoßen | Pflanzenstoff |
| E088 | Stiele trocknen | Pflanzenstoff |
| E094 | „Honig zugeben“ | Pflanzenstoff zugeben |

Eine Karte kann in derselben Ausgabe nicht dreimal Pflanze und einmal Honig heißen, nur weil Honig in einem Brustmittel gut passen würde. Deshalb fällt die Honigkarte weg. Honig bleibt historisch hoch plausibel, aber auf diesen Seiten lexikalisch **unlokalisiert**.

Die revidierte H5-S005-Lesung lautet daher:

> Pflanzenstoff zugeben → laufenden Posten einsetzen → als Brusttrank geben → bei trockenem Husten gebrauchen.

Das ist weniger dekorativ als „Honig“, aber kompositionell sauberer.

## 7. Warum auch Öl unlokalisiert bleibt

- `OL` ist in der aktiven Grammatik eine häufige Weiter-/Vorigenkarte und bildet mit OR „mit der vorigen Zubereitung“.
- `OR` ist durch die vollständige Zubereitungstafel gebunden.
- `SCHOAL` kann als Ganzkarte Weinsud heißen, ohne `O/OL/AL` zu Ingredienzien zu machen.
- Keine andere Zielkarte wiederholt sich so, dass `ÖL` invariant und nützlicher als ihr aktueller Werkstattwert wäre.

Öl ist deshalb ein erwartbares mittelalterliches Ingrediens, aber kein gefundenes Voynich-Wort dieser Arbeitsausgabe.

## Historische Werkstattähnlichkeit, ca. 1370–1450

Die Vergleichsbasis ist die moderne Edition der *Medieval Welsh Medical Texts*. Sie ediert die vier frühesten medizinischen Sammlungen, die laut Einleitung aus dem späten 14. Jahrhundert stammen und eng in die europäische Rezepttradition gehören. Damit ist sie zeitlich und praktisch nah genug, um Abläufe zu vergleichen, nicht um Voynich-Karten zu benennen. [Editionsüberblick](https://www.ncbi.nlm.nih.gov/books/NBK558253/)

Die Rezepte zeigen genau die Werkstattunterscheidungen, die die neue kleine Stofftafel plausibel machen:

- Kräuter werden in Weißwein bis zur Reduktion gekocht, ausgepresst, erneut erhitzt und in einem sauberen Gefäß aufbewahrt;
- Kräuteressenz wird in Wasser überführt und mit Honig kombiniert;
- Arznei wird durch feines Leinentuch gepresst beziehungsweise geseiht und anschließend verwahrt;
- warmes Wasser wird zu zerstoßenem Material gegeben, danach wird durch Leinen gepresst und ein Pflaster bereitet;
- Olivenöl, Honig, Fette und Wachs werden als ausdrücklich getrennte Ingredienzien gekocht und durch Leinen geseiht;
- Wein, Honig und Kräuter werden zu einem Trank gekocht oder vor dem Verwahren geseiht;
- Bäder, Waschflüssigkeit und Lauge erscheinen als eigene Anwendungsmedien.

Diese Beispiele stehen unter anderem in Buch 5, besonders den Rezepten 5/2, 5/13, 5/16, 5/24, 5/26, 5/43–46, 5/52 und 5/56. [Primärtext und Übersetzung](https://www.ncbi.nlm.nih.gov/books/NBK558238/)

Die historische Parallele unterstützt also die **Form** des Modells: eine Mischung aus kurzen Fachkarten für Wasserarten, Weinansatz, Öl, Honig, Trank, Badzusatz sowie wiederkehrenden Arbeitsverben. Sie beweist nicht, dass eine bestimmte Voynich-Karte eines dieser Wörter bedeutet. Gerade weil Öl und Honig in realen Rezepten eigene Stoffe sind, sollten sie nicht aus `OL`, `OR` oder einem einmal bequem wirkenden `sho` erzwungen werden.

## Konkrete Passageübersetzungen

### H3 — f11r, vollständiger Record

1. Nimm im ersten Frühjahr Blüten und junge Blätter der unbenannten Pflanze. Bereite daraus einen **Weinsud**; wringe ihn aus, lass ihn die vorgeschriebene Zeit stehen, seihe nach und nimm den **Klarauszug**. Lass ihn abkühlen; damit endet der erste Posten.
2. Behalte einen Teil der frischen Blüten für eine zweite Arznei zurück.
3. Nimm vom vorigen Posten; gib den laufenden Posten als **Trank** in vorgeschriebenem Maß.
4. Nimm die zurückbehaltenen Blüten und arbeite mit dem vorigen Arbeitsgut weiter, bis der Posten gebrauchsfertig ist.

Diese Lesung hat nun eine klare Materialfolge: `PFLANZENSTOFF → WEINSUD → KLARAUSZUG → TRANK`.

### H5 — f56r, vollständiger Record

1. Pflanzenzubereitung; Pflanzenstoff zu Beginn der Blüte; vorgeschriebenes Maß; Pflanzenstoff; als Auflage auflegen; dann die nächste Zubereitung an der Stelle einsetzen.
2. Vom vorigen Posten nehmen; die bezeichnete Stelle waschen; den laufenden Posten auftragen und schließen.
3. Vom übrigen Kraut die blühenden Stiele nehmen; Pflanzenstoff grob zerreiben; den Posten erneut in Arbeit nehmen.
4. Den laufenden Posten einsetzen, **Auszug** zugeben und abseihen.
5. Pflanzenstoff zugeben; den Posten einsetzen; als **Brusttrank** geben und bei trockenem Husten gebrauchen.
6. Den nächsten Posten wählen; je Gabe das vorgeschriebene Maß.

Die frühere Honigbehauptung ist entfernt; die Passage bleibt als Pflanzenstoff–Auszug–Trank-Kette lesbar.

### B2/B3/B4 — Wasser- und Laufstellen

- B2-S007: „**Frischwasser** zugeben; Schluss.“
- B2-S017: „**Warmwasser** eingießen; an der zweiten Öffnung wiederholen und schließen.“
- B3-S014: „**Laufflüssigkeit** starten; länger ruhen oder absetzen; Schluss.“
- B3-S021: „Auf das Maß einstellen; gebrauchsfertig; Stelle; laufender Posten; Maß; Ruhe-/Absetzstelle; **Badwasser**; Posten; Stelle; gebrauchsfertig; lokal umsetzen; Schluss.“
- B3-S030: „Posten einsetzen; Maß; **Laufflüssigkeit führen**; danach erneut umsetzen; Schluss.“
- B4-S014: „Zubereitung; laufender Posten; über der bezeichneten Stelle; **Laufflüssigkeit abschließen**.“
- B4-S016: „Weitere Portion zugeben; Stelle; **Warmausguss**; ruhen oder absetzen; Schluss.“

## Gegenbeispiele und harte Grenzen

| Versuch | Gegenbeispiel | Konsequenz |
|---|---|---|
| `sho = Honig` | dieselbe exakte Karte ist auch `cho` und bezeichnet in drei weiteren Ereignissen Pflanzenstoff | verwerfen |
| `OL = Öl` | OL trägt den aktiven Vorigen-/Weiterwert und bildet regulär OL+OR | verwerfen |
| `OR = Öl` | nacktes OR, CHO+OR, OL+OR, OT+OR und OR+AIN verlangen Zubereitung | verwerfen |
| `AIR = Wasser` | fünf Ereignisse beschreiben einen laufenden Stoff in Pflanze, Becken und Leitung | zu eng; Laufflüssigkeit behalten |
| `SHEY = jede Flüssigkeit` | SHEY steht gerade am klaren Ende der Trennfolge | zu breit; Klarauszug behalten |
| `CHEO = SHEY` | CHEO wird entnommen/zugegeben, SHEY folgt auf Nachseihen | getrennte Prozessstufen behalten |
| `SCHOAL` produktiv zerlegen | nur ein Ereignis | Ganzkarte Weinsud; keine Teilstämme exportieren |
| gemeinsamer Wasserstamm | drei Wasserkarten teilen keine belastbare exakte Komposition | gelernte Dreierkarte behalten |

## Technisches Ergebnis

- `R1_173_MEDIUM_SUBSTANCE_DICTIONARY.tsv`: 173 Karten, keine leeren Defaults.
- `R1_381_MEDIUM_SUBSTANCE_INTERLINEAR.tsv`: 381 Ereignisse.
- `R1_116_MEDIUM_SUBSTANCE_SENTENCES.tsv`: 116 Aussagen.
- `R1_11_MEDIUM_SUBSTANCE_RECORDS.md`: 11 vollständige Records.
- 15 Karten, 19 Ereignisse und 17 Aussagen wurden gezielt revidiert.
- `R1_MEDIUM_SUBSTANCE_COMPONENTS.tsv`: 13 Komponenten-/Grenzzeilen.
- `R1_MEDIUM_SUBSTANCE_PARADIGM.tsv`: 23 Zielkarten mit allen Vorkommen.
- `R1_VALIDATION.json`: PASS, 35 Prüfungen.

Builder und Validator sind `R1_BUILD_MEDIUM_SUBSTANCE.py` und `R1_VALIDATE_MEDIUM_SUBSTANCE.py`. Es wurden weder Route noch Ledger geändert und nichts committed oder gepusht.
