# GDT444 — Ein sichtbarer Slot trennt die Handlungen

## Ergebnis

Die 44 roten direkten Handlungspaare sind keine Verbote gegen dieselben beiden
Handlungen in einer längeren Karte. Sobald ein sichtbarer Fokus dazwischen
steht, gehen 471/484 Mikroketten durch:

- 460 grün;
- 11 gelb;
- 13 rot.

Jedes rote Direktpaar besitzt mindestens zehn lesbare Fokus-Trenner. Bei 31
Paaren funktionieren alle elf; bei 13 Paaren funktionieren zehn von elf.
Kein direktes Paar wird dadurch grün oder gelb.

## Beispiel

```text
CHD+K       -> STOP: PAIR:CHD>K
CHD+Y+K     -> grün: CHD<-Y; keine direkte Paarberührung
```

Die zweite Form heißt nicht, dass `CHD>K` plötzlich erlaubt wäre. `Y` macht
zwei getrennte Pakete sichtbar: der laufende Posten gehört zur linken
Bearbeitung, danach folgt die rechte Gabe.

## Die elf Trenner

| Fokus | Grün | Gelb | Stop |
|---|---:|---:|---:|
| `AIIN` | 44 | 0 | 0 |
| `AIN` | 44 | 0 | 0 |
| `AIR` | 43 | 1 | 0 |
| `AL` | 44 | 0 | 0 |
| `AR` | 44 | 0 | 0 |
| `E` | 44 | 0 | 0 |
| `EE` | 39 | 5 | 0 |
| `EEE` | 26 | 5 | 13 |
| `L` | 44 | 0 | 0 |
| `OR` | 44 | 0 | 0 |
| `Y` | 44 | 0 | 0 |

Die elf gelben Zellen sind keine neuen Ausnahmen:

- fünfmal `R<-EE`;
- fünfmal `S<-EEE`;
- einmal `R<-AIR` in `R+AIR+R`.

Die dreizehn roten Zellen sind ebenso vollständig erklärt: `EEE` bindet bei
Gleichstand links, und die linke Handlung ist in acht Fällen `CHD`, in fünf
Fällen `R`. Damit entstehen genau die beiden alten Lücken `CHD<-EEE` und
`R<-EEE`, nicht dreizehn neue Probleme.

## Reale Vorkommen

Der Mechanismus ist nicht nur eine synthetische Möglichkeit. Die laufende
26-Seiten-Ausgabe enthält bereits:

- 28 exakte Dreier-Vorkommen;
- 27 vollständige Rezepte;
- 18 verschiedene Paar×Fokus-Muster;
- 16 der 44 roten direkten Paare;
- 13 Seiten.

Alle 28 Dreiertripel sind über seitenübergreifende Fokusanschlüsse grün. Die
häufigsten getrennten roten Paare sind `SH>S` (5), `S>S` (4) und `CHD>K` (3).
Das ist direkte Werkstattpraxis für die Regel „rote Nachbarschaft, lesbare
Slotkette“.

## Lehrregel

```text
A+B rot       -> nicht zusammenziehen
A+F+B sichtbar -> F mit dem alten Selector binden und beide Handlungen getrennt lesen
EEE nach CHD/R -> weiterhin stoppen
```

Damit wird das Stop-Deck präziser statt lockerer: Es verbietet nur die
ungestützte direkte Verschmelzung, nicht jede längere Sequenz derselben Köpfe.

## Nächster Schritt

GDT441–GDT444 bilden jetzt gemeinsam eine vollständige Aufnahmeentscheidung:
exakter Schlüssel, alte Faktoren, Kontextrettung, sichtbare Slottrennung oder
benannter Stop. Als nächstes sollte daraus ein einziges kurzes Intake-Protokoll
und eine ausführbare Zertifikatszeile pro neuer sichtbarer Karte gebaut werden,
damit die nächsten Seiten ohne nachträgliche Umdeutung durchlaufen können.
