# GDT517 — Aus Oberflächen wird jetzt wirklich ein ausführbares Rezept

## Ergebnis

Der bisher fehlende Zwischenschritt ist gebaut. Wir müssen bei einer neuen
Voynich-Form nicht mehr zuerst von Hand ein Rezept hinschreiben: Der Compiler
kann die sichtbare Zeichenfolge selbst in gelernte Ganzstücke und Reststücke
zerlegen, mehrere Rezepte ausgeben und sofort einen Arbeitsdefault wählen.

Der harte Rücklauf benutzt nur die älteren 26 Seiten und behandelt die 159
GDT515-Formen als neue Oberflächen:

| Modell | kachelbar | aktuelles Rezept erzeugt | Rang 1 | Top 5 |
|---|---:|---:|---:|---:|
| nur alte Einatom-Ganzformen | 45 | 36 | 22 | 36 |
| alle alten Ganzrezepte | 107 | 91 | 69 | 91 |
| plus direkte Reststücke | 155 | 153 | 104 | 147 |
| plus iterative Reststückschließung | **159** | **159** | **117** | **157** |

Damit ist nicht jede Rangfolge richtig. Aber keine der 159 Formen bleibt mehr
ohne Default, und das später gewählte GDT516-Rezept fehlt in keinem einzigen
Kandidatenraum. Nur `aiicthy` (Rang 6) und `dalcheeeky` (Rang 56) liegen tiefer
als Rang 5.

## Was tatsächlich gelernt wurde

Aus 1.558 alten laufenden Oberflächen entstehen 4.403 verwendbare sichtbare
Stücke mit 5.555 Rezeptmöglichkeiten. Einige besonders klare Beispiele:

| sichtbares Stück | Default | Unterstützung | Anteil |
|---|---|---:|---:|
| `q` | `CARRIER_Q` | 147/150 | 98,0 % |
| `i` | `LOCAL_CHAR_I` | 47/56 | 83,9 % |
| `eee` | `EEE` | 58/61 | 95,1 % |
| `dy` | `DY` | 491/847 | 58,0 % |

Gerade `dy` zeigt, warum Alternativen nötig sind: `D_ADDR+Y` hält 175 Kontakte,
`Y` weitere 152. Der Compiler darf daraus keinen immer gleichen Wortstamm
machen. `c` und `x` sind die andere Art von Ausnahme: ihre lokalen Lesungen
gelten nur im f66r-Lokalregister. Ein allgemeiner Prose-Aufruf liest `c` weiter
als `CH`; ein Aufruf mit `--page f66r --domain LOCAL_RECORD` erhält `LOCAL_C`.

## Die 42 Rang-1-Abweichungen

40 der 42 abweichenden Defaults enthalten das aktuelle Rezept bereits unter
den ersten fünf. Sie bilden keine beliebige Fehlerwolke, sondern einige
wiederkehrende Entscheidungen:

- ein langes altes Ganzstück verschluckt eine heute sichtbar getrennte
  Komponente, etwa `cheod: CH+E+O` statt `CH+E+O+D_ADDR`;
- `dy`, `…dy` und `…y` konkurrieren als Schluss, lokale Adresse plus Posten oder
  bloßer Posten;
- alte Oberflächenkarten tragen eine kürzere Rezeptanalyse als die neu
  bevorzugte sichtbare Komposition;
- seltene Formen konkurrieren zwischen `CH`, `SH` und `CHD` oder zwischen
  `K+E` und `OK`.

Das ist jetzt handhabbar: Der Atlas nennt für jede Form Rang, Top-5-Rezepte und
die genaue Stückkette. Für die bereits geöffneten 30 Seiten gewinnt ohnehin
die exakte Ereigniskarte. Der nächste sinnvolle Angriff ist ein
Nachbarschafts-/Rollen-Reranker für diese 42 Fälle, nicht eine erneute globale
Umdeutung des Wörterbuchs.

## Vollständige 30-Seiten-Basis

Nach dem Rücklauf wird der Compiler mit allen 5.122 laufenden Ereignissen neu
gebaut. Diese enthalten 1.711 verschiedene laufende Oberflächen, weiterhin
jeweils mit genau einem aktuellen Rezept. Das Zukunftsmodell umfasst 4.783
Stückformen und 5.999 Rezeptmöglichkeiten.

Daneben steht jetzt eine exakte Ausgabe für alle **5.866** Gruppen:

- 5.122 laufende Karten;
- 183 vollständig ausgearbeitete GDT473-Lokalpakete;
- 510 vollständig ausgearbeitete GDT513-Lokalkarten;
- 51 neue ausgewählte Lokalkarten.

Die 183+510 Karten ersetzen die alten pauschalen `LOCAL_ADDRESS`-Marker. Ein
gelernter Pflanzen-, Sternstellen- oder Besitzername bleibt ein lokales
Ganzpaket; seine sichtbare Funktionsschale wird separat gespeichert. Der
kompakte Oberflächenindex hat 2.243 Rezeptoptionen. Im Prosebereich besitzt
jede Oberfläche genau ein Rezept. Nur neun lokale Oberflächen-/Domänenpaare
haben je zwei endliche Möglichkeiten: `cheody`, `d`, `doly`, `l`, `o`,
`okeal`, `okealar`, `r` und `s`.

## Der Textstrom läuft ohne falsche Labelstopps

Der alte Live-Leser ergab auf den 546 ausgewählten Prosekarten:

- 539 grüne Lesungen;
- eine alte gelbe Lesung (`shtchy`);
- sechs Stopps.

Die sechs Stopps waren drei Adressabschlüsse ohne aktiven Handlungskopf,
`axor/chxar` mit dem lokalen `x`, und die neue direkte Aktionsfolge `SH>S` in
`shso`. Rollenbewusst ergibt sich:

- drei `READ_ROLE_CONTAINER`;
- zwei `READ_LOCAL_SHELL`;
- ein zusätzliches endliches `READ_AMBER` für `shso`;
- **null verbleibende Stopps**.

Die fünf Rollencontainer/-schalen verändern den Handlungszustand nicht. Die
Freigabe von `shso` gilt nur für diese direkt beobachtete Karte und macht aus
`SH>S` keine unbegrenzte globale Regel.

## Praktischer Aufruf

```bash
python3 experiments/yolo/gdt517_thirty_page_surface_recipe_intake_compiler/src/intake_surface.py \
  --surface aiicthy --page f31r --top 5

python3 experiments/yolo/gdt517_thirty_page_surface_recipe_intake_compiler/src/intake_surface.py \
  --surface c --page f66r --domain LOCAL_RECORD
```

Die Auswahlreihenfolge ist immer: exaktes Ereignis, bekannte
Oberflächen-/Rollenoption, dann Compiler-Rang 1. Das ist die neue Arbeitsbasis,
nicht der Nachweis eines historischen Wortes oder einer Klartextsprache.
