# GDT547 — auch die letzten 24 Formen haben sichtbare Bausteine

Status: `PASS_24_ATOM_FACTOR_CARDS_VISIBLE__21_OLD_DECK_COVERS__3_SPECIAL_ROUTES`

## Ergebnis

Die 24 schwächsten Prosakarten sind nicht länger bloß „aus bekannten Faktoren
zusammengesetzt“. Jede besitzt jetzt eine buchstabengetreue sichtbare Spur,
eine vollständige Komponentenbedeutung, die bekannte Kontextlesung und den
genauen Punkt, an dem ihre Stützung endet.

21/24 Oberflächen werden vollständig durch das alte GDT519-Rendererlexikon
abgedeckt. Es existieren 44 exakte Pfade. Bei 16 Karten genügt die kanonische
Schreibform jedes Atoms, etwa:

```text
shddy = sh→SH | d→D_ADDR | dy→DY
        Halten; hier; abschließen.

keeol = k→K | ee→EE | ol→OL
        Geben; auf Grad II; fortsetzen.
```

Fünf Karten verwenden ein altes gelerntes Kurzstück:

- `chcpheor`: `chcph→CH+CH+P | e→E | or→OR`;
- `cphaiin`: `cph→CH+P | aiin→AIIN`;
- `pdaiin`: `p→P | daiin→AIIN`;
- `qotedal`: `qot→OT | e→E | dal→AL`;
- `tocpheey`: `t→T | o→O | cph→CH+P | ee→EE | y→Y`.

Das ist genau die gesuchte Mischform aus atomaren Fachkürzeln und gelernten
kurzen Ganzstücken. Keine dieser fünf Karten braucht eine lange, eigene
Ganzwortbedeutung.

## Die drei begrenzten Sonderwege

`chedaiir` zerfällt sichtbar in `ched→CHD | aiir→IIN+R`. Der aktuelle
Chunk-Atlas weist `aiir` 17/20-mal (85%) `IIN+R` zu; `AIIN+R` bleibt als
3/20-Rivale sichtbar. Die bekannte Gesamtkarte entscheidet hier.

`faiis` liest `f→LOCAL_CHAR_F | aiis→IIN+S`. `aiis` ist ausdrücklich kein
globales Wortstück: Nach `f` oder `qo` trägt es in zwei vollständigen Karten
`IIN+S`; nach `s` trägt es in zwei Karten `A_ADDR+IIN+S`. Diese
Präfixabhängigkeit erklärt zugleich, warum `faiis` und das revidierte `saiis`
nicht dieselbe innere Rezeptfolge brauchen.

`qef` liest `q→NULL_Q | e→E | f→LOCAL_CHAR_F`. Das ist kein freies Löschen:
Die sechs anderen q-Karten desselben Satzes sind 6/6 nichttragend, und der
alte sichtbare q-null-Kanal steht bei 75/84. Die Arbeitslesung bleibt „Auf
Grad I; hier.“

## Wo die Karten noch wirklich schwach sind

Von 52 direkten Atompaaren kommen 40 innerhalb alter vollständiger Karten vor.
Zwölf Übergänge auf neun Karten sind neu. Der aktuelle Faktorleser verarbeitet
im beobachteten Kontext 20 Karten grün und `shtchy` gelb; dort ist `SH>T` nur
lokal belegt.

Seine drei Stopps sind verschieden:

- `axor` und `chxar` enthalten `LOCAL_X`, das im älteren GDT446-Deck
  noch fehlt, aber im späteren f66r-Overlay ausdrücklich vereinheitlicht ist;
- `shso=SH+S+O` verlangt das neue direkte Aktionspaar `SH>S`.

`shso` bleibt deshalb der einzige rohe beobachtete Paar-Default dieser
24er-Gruppe. Er wird vollständig gelesen („Halten und wählen; zur
Ausführung.“), aber nicht als bereits alte produktive Paarregel ausgegeben.

## Praktischer Aufruf und nächster Griff

```bash
python3 experiments/yolo/gdt547_atomic_factor_visible_reader/src/read_atomic.py \
  --surface shso
```

Alle 38 Prüfungen bestehen. Damit besitzen jetzt alle 145 Prosazieloberflächen
eine vollständige Lesung und eine konkrete Stützstufe: 11 exakte Altträger,
29 alte Kachelkompositionen, 81 Fragment-Reader-Karten und 24 sichtbare
Atom/Faktor-Karten.

Als Nächstes sollte diese vierstufige Staffel in einen einzigen
145-Oberflächen-Reader kompiliert werden. Danach kann man gezielt nur die
wenigen echten Defaults—vor allem `shso`, die zwölf Fragmentreste und die zehn
schwächeren Vollkacheln—verbessern, statt die ganze Übersetzung wieder
umzudeuten.

Keine Seite, Rezeptkarte oder Wurzelbedeutung wurde geändert. Die deutschen
Sätze bleiben die beste aktuelle Arbeitsübersetzung, kein bewiesener Klartext.
