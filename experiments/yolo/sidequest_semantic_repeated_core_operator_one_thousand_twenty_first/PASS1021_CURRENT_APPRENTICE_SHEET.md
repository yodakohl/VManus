# Lehrmeistertafel der Werkstatt

> **Sieh zuerst den Besitzer. Lies dann die längste bekannte Form, öffne ihre
> Kerne von links nach rechts, ergänze den örtlichen Kanal und setze zuletzt
> Grad, Stufe und Schluss. Ein Zeilenende beendet den Gang nicht.**

## Der gewöhnliche Gang

`BILD / GEFÄSS / STATION / RAD → [BEGINN oder FOLGE] → [POSTEN · WERT · ANTEIL · EINHEIT] → HANDLUNG → [AUSGANG · VERBINDUNG · LAUF · ZIELORT] → [GRAD oder STUFE] → [SCHLUSS]`

Nicht jede Stelle muss gefüllt sein. Das Bild oder Register nennt den Besitzer
stumm. Unbekannte Bild-, Stoff- und Ringnamen werden als ganze Kennung aus dem
Exemplar kopiert.

## Die neunzehn tragbaren Kerne

| Handlungsköpfe | Arbeitsinhalt | Folge und Beziehung |
|---|---|---|
| `OK` SETZEN<br>`CH` NEHMEN<br>`SH` HALTEN<br>`K` GEBEN<br>`S` WÄHLEN<br>`T` EINSTELLEN<br>`CHD` UMSETZEN<br>`R` MARKIEREN<br>`P` EINSETZEN | `Y` AKTIVER POSTEN<br>`AIIN` WERT<br>`AIN` ANTEIL<br>`OR` EINHEIT | `OL` FORTSETZEN<br>`OT` DANACH<br>`AR` AUSGANG<br>`AL` ZIELORT<br>`L` VERBINDUNG<br>`AIR` LAUF |

**Bindung:** Der sichtbare Besitzer füllt den Kern örtlich aus. `AIN` bleibt
ANTEIL, auch wenn das Bild daraus Pflanzenanteil, Stationsanteil, Sektor oder
Zutatenanteil macht. Ebenso bleiben `AIIN=WERT` und `OR=EINHEIT`. `AR` und
`AL` nennen die beiden Orte; `L` und `AIR` geben weder Wasser noch Richtung
hinzu. `Y` hält den aktiven Posten fest und ist kein Schluss.

## Die acht Steuerzeichen

| Zeichen | Wert | Zeichen | Wert |
|---|---|---|---|
| `E` | GRAD I | `EE` | GRAD II |
| `EEE` | GRAD III | lizenziertes `DY` | SCHLUSS |
| `O` | AUSFÜHRUNG | `CARRIER_Q` | BEGINNMARKER |
| `IIN` | STUFE | `DA` | ZWEITE STUFE |

Grad I/II/III bleibt dieselbe Reihe; erst die Handlung macht daraus örtlich
eine kurze, stärkere, weitere oder vollständige Ausführung. Nur eine gelernte
Schlussform oder eine sichtbare Besitzergrenze schließt den Gang.

## Vier örtliche Kanäle für neunzehn Zeichen

| Kanal | Zeichen | Lehrregel |
|---|---|---|
| **HIER** | `D_ADDR AM_ADDR A_ADDR S_ADDR LOCAL_CHAR_F D_LABEL S_LABEL M_LOCAL Z_ADDR` | Nimm die bezeichnete örtliche Stelle; kein eigenes Wort für Teil, innen, außen, Mitte oder Rand. |
| **VARIANTE** | `G_LABEL LOCAL_CHAR_G LOCAL_CHAR_I LOCAL_CHAR_B LOCAL_CHAR_J LOCAL_CHAR_Z` | Nimm die im Exemplar markierte Variante; keine allgemeine Zahl, Farbe, Prüfung oder Richtung. |
| **KLASSE** | `HO` vorn, `AN` hinten | Nimm die örtliche Klasse; kein fester Stoff- oder Pflanzenname. |
| **VORBEZUG** | `OS RESUME_CARD` | Nimm den vorausgesetzten Besitzer oder Gang wieder auf. |

## Zehn Formen, die geöffnet werden

| Eingeschobene Form | Öffnung | Gewöhnliche Form | Öffnung |
|---|---|---|---|
| `CTH = C<T>H` | `CH + T` | `CHEO` | `CH + E + O` |
| `CKH = C<K>H` | `CH + K` | `CHK` | `CH + K` |
| `CPH = C<P>H` | `CH + P` | `SHED` | `SH + E` |
| `CFH = C<F>H` | `CH + LOCAL_CHAR_F` | `LSH` | `L + SH` |
|  |  | `SOLK` | `OL + K` |
|  |  | `LD` | `L + D_ADDR` |

**CHK gegen CKH:** `CHK` ist die lineare Folge `CH|K`; sie eröffnet gewöhnlich
einen Gang und nimmt rechts Grad, Posten oder Adresse an. `CKH` ist das
eingeschobene Paket `C<K>H`; es sitzt häufig in einem äußeren `O`-, `SH`-,
`CH`- oder `L`-Rahmen. Beide tragen **NEHMEN + GEBEN**. Die Verpackung ändert
die Stellung, nicht die Kernsumme.

## Elfte Regel: zwei gleiche Kerne

```text
PAKETGRENZE:  X + X + Z  = äußeres X [inneres X [Z]]
FREI:         X + X      = mehrere X bei Dingen / X nochmals bei Handlungen
```

An einer geöffneten Paketgrenze gehören die zwei Kerne zu zwei benachbarten
Besitzerebenen. Frei stehende Doppelkerne werden beide gleichrangig gelesen.
Der zweite Kern wird nie als bloßes Ditto gelöscht und erhält kein neues Wort.

## So wird gelesen

1. Besitzer und sichtbare Grenze bestimmen; nicht am Zeilenende abbrechen.
2. Die längste bekannte Grafik greifen; erst danach die zehn Formen öffnen.
3. Kerne links nach rechts lesen; `OT` führt weiter, `OL` setzt denselben Gang fort.
4. `HIER`, `VARIANTE`, `KLASSE` oder `VORBEZUG` aus dem Exemplar ergänzen.
5. Grad und Stufe an die laufende Handlung binden; lizenziertes `DY` schließt.

## So wird geschrieben

1. Den Bild-, Gefäß-, Stations- oder Radbesitzer wählen.
2. Beginn oder Folge setzen; dann Posten, Wert, Anteil oder Einheit nennen.
3. Handlung und nötige Beziehung setzen; örtliche Kennungen ganz kopieren.
4. Grad oder Stufe zufügen und nur bei wirklichem Ende eine Schlussform nehmen.
5. Eine häufige Form darf als Ganzkarte geschrieben werden; beim Lesen behält
   sie stets dieselbe Kernsumme.

**Hin und zurück:**

`CARRIER_Q | OK + AIN | AL | E | DY`

`BEGINNMARKER | ANTEIL SETZEN | ZIELORT | GRAD I | SCHLUSS`

Zum Schreiben dieselben Plätze in derselben Folge setzen; der sichtbare
Besitzer entscheidet, welcher Anteil und welcher Zielort gemeint sind.

## Vier schon festgelegte neue Zusammensetzungen

| Form | Öffnung | erste Lesung |
|---|---|---|
| `chain` | `CH + AIN` | ANTEIL NEHMEN |
| `pain` | `P + AIN` | ANTEIL EINSETZEN |
| `paiin` | `P + AIIN` | WERT EINSETZEN |
| `lair` | `L + AIR` | VERBINDUNG IM LAUF |

> **Merksatz:** Der Kern bleibt kurz. Das Bild macht ihn anschaulich. Die
> örtliche Kennung wird kopiert. Grad und Schluss stehen für sich.
