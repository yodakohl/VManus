# GDT632 — das CTH-Raster erhält eine innere Ordnung

## Ergebnis

Die Formen sind nicht länger als lose Ganzwörter zu behandeln. Die
beste Arbeitsanalyse lautet:

```text
ch/sh + e? + [o? + cth + Rest]
```

Die deutsche Arbeitslesung ist entsprechend:

| Form | Parse | konkrete Arbeitslesung |
|---|---|---|
| `chcthy` | `ch+[cth+y]` | trockenes CTH-Material; im Herbal trockenes Blatt-/Krautmaterial |
| `shcthy` | `sh+[cth+y]` | feuchtes CTH-Material; im Herbal feuchtes Blatt-/Krautmaterial |
| `checthy` | `ch+e+[cth+y]` | trockenes CTH-Material der E-Reihe |
| `shecthy` | `sh+e+[cth+y]` | feuchtes CTH-Material der E-Reihe |
| `chocthy` | `ch+[o+cth+y]` | trockenes CTH-Material der O-Reihe |
| `shocthy` | `sh+[o+cth+y]` | feuchtes CTH-Material der O-Reihe |
| `cheocthy` | `ch+e+[o+cth+y]` | trockenes CTH-Material der EO-Reihe |
| `sheocthy` | `sh+e+[o+cth+y]` | feuchtes CTH-Material der EO-Reihe |

„E-/O-Reihe“ ist dabei eine sichtbare Strukturangabe, kein deutsches
Ersatzwort. In flüssiger Arbeitsübersetzung bleiben `e` und `o` vorerst stumm;
im Parse gehen sie nie verloren.

## Das vollständige 2×4-Raster

Alle acht erwarteten Zellen sind real belegt:

| Qualitätskern | Zwischenklasse | Token | Typen | dreifach exakt |
|---|---|---:|---:|---:|
| `ch` | `∅` | 118 | 20 | 102 |
| `ch` | `e` | 34 | 6 | 31 |
| `ch` | `o` | 23 | 4 | 19 |
| `ch` | `eo` | 6 | 3 | 6 |
| `sh` | `∅` | 36 | 5 | 33 |
| `sh` | `e` | 21 | 4 | 20 |
| `sh` | `o` | 13 | 4 | 13 |
| `sh` | `eo` | 4 | 2 | 3 |

Das sind 255 fusionierte Vorkommen, 48 Oberflächentypen und 104 Seiten. 251
Vorkommen besitzen einen bereits in GDT625 publizierten nackten CTH-Rest.
Der häufigste Rest `y` allein erscheint in allen acht Zellen:

```text
CH: 75 / 26 / 17 / 4
SH: 29 / 18 / 10 / 3
     ∅    e    o    eo
```

Auch die Qualitätsopposition wiederholt sich statt nur bei `cthy` aufzutreten.
Gleiche `ch/sh`-Restpaare gibt es fünfmal in der direkten Reihe, dreimal unter
`e`, dreimal unter `o` und einmal unter `eo`. Das Ganzwortmodell müsste dieses
selbe Raster für jede Oberfläche neu lernen.

## Warum die Hierarchie nicht einfach `ch/sh + e/o + CTH` lautet

Außerhalb des Qualitätsrasters stehen folgende nackte Köpfe:

| Kopfklasse | Token | Typen | Seiten |
|---|---:|---:|---:|
| `cth+R` | 408 | 69 | 125 |
| `ecth+R` | 0 | 0 | 0 |
| `octh+R` | 32 | 16 | 27 |
| `eocth+R` | 0 | 0 | 0 |

Damit verhalten sich `e` und `o` verschieden. `o` kann mit CTH einen
selbständigen inneren Kopf bilden; `e` ist nur nach `ch/sh` belegt. Die 46
fusionierten O-/EO-Token in dreizehn Oberflächentypen reduzieren sich
vollständig auf sechs bereits vorkommende innere Köpfe:

```text
octham  octhedy  octhey  octhody  octhol  octhy
```

Die Abdeckung ist 46/46. Nur drei der 46 Vorkommen teilen allerdings die Seite
mit ihrem nackten Kopf. Das ist deshalb ein global produktives Typenparadigma,
keine Behauptung, der Schreiber habe auf jeder Seite eine ausgeschriebene
Legende danebengesetzt.

Auch die Reihenfolge ist gerichtet: `ch/sh+eo+cth` erscheint zehnmal in fünf
Typen, `ch/sh+oe+cth` kein einziges Mal. Nacktes `ecth`, `eocth` und `oecth`
sowie getrenntes `e | cth` und `eo | cth` bleiben in jeder der drei Lesungen
leer. Nacktes `octh` ist dagegen in allen drei Lesungen sichtbar; zusätzlich
gibt es fünf leserspezifisch getrennte `o | cth`-Realisierungen.

## Schreibgrenze und innere Analyse sind zwei Ebenen

Die beobachteten internen Wortgrenzen schneiden so:

```text
[ch / che / cho / cheo] | cth+Rest
[sh / she / sho / sheo] | cth+Rest
```

Fünf eindeutige Leserwechsel und sieben in allen Lesungen getrennte Spans
ergeben zwölf konservative `linke Shell | CTH`-Grenzen. Dazu kommt die direkte
Brücke `sh | cthey ↔ shcthey`. f21r.7 zeigt eine dreizehnte linke Shellgrenze;
dort überlappt aber der rechte Rand mit einem längeren Ziel und wird deshalb
nur in der inklusiven Population verwendet.

Die Gegenrichtung fehlt vollständig: Es gibt weder `ch/sh | e/o/eo+cthR`
noch `ch/sh | e/o/eo | cthR` in irgendeiner Leserzeile. Orthographisch gehört
`o` somit zum linken Block, obwohl die nackte Kopfserie morphologisch
`o+cth+R` verlangt. Ein `cheo | cthy` wird daher nicht widersprüchlich, sondern
zweistufig gelesen:

```text
sichtbar:       cheo | cthy
Arbeitsanalyse: ch + e + [octhy]
```

Auch die äußeren Grenzen sind beweglich: Vier dreifach normalisierte Spans und
ein paarweiser Span zeigen etwa `y | checthy ↔ ychecthy`,
`sshol | shecthy ↔ ssholshecthy` und `chcthy | dain ↔ chcthydain`.

## Vier sauber getrennte Vorkommenspopulationen

Getrennte Lesungen werden nicht heimlich als fusionierte Wörter gezählt:

| Population | Vorkommen | Oberflächentypen | Inhalt |
|---|---:|---:|---|
| fusionierte ZL3b-Formen | 255 | 48 | exaktes Ausgangsraster |
| plus all-reader-getrennt | 262 | 51 | sieben in allen Lesungen getrennte Ausdrücke |
| konservativ grenznormalisiert | 265 | 52 | plus drei eindeutige ZL3b-split/anderer-Leser-fused Spans |
| inklusive linke Grenze | 266 | 53 | plus f21r.7 mit überlappendem rechten Rand |

Drei der sieben all-reader-getrennten Ausdrücke haben noch keine fusionierte
Oberfläche und sind echte Kompositionsvorhersagen:

```text
she | cthol   -> shecthol
sho | cthos   -> shocthos
sheo | cthody -> sheocthody
```

Sie sind bereits als getrennte Ausdrücke lesbar. Das Experiment behauptet
nicht, dass ihre fusionierte Schreibung zwingend auf einer späteren Seite
auftreten muss.

## Die schärfste neue Vorhersage: `octheey`

Nach Einbezug aller konservativen und der einen inklusiven Wortgrenze tragen
die O-/EO-Zellen 55 Vorkommen in siebzehn Oberflächentypen. 54 Vorkommen und
sechzehn Typen treffen einen nackten O-CTH-Kopf. Die acht belegten Köpfe sind:

```text
octham  octhedy  octhey  octhody  octhol  octhor  octhos  octhy
```

Die einzige Lücke entsteht aus f114v.33:

```text
cheo | ctheey  ↔  cheoctheey
```

Das geordnete Modell verlangt hier konkret `octheey`. Diese Form ist im
aktuellen erlaubten Typendeck nicht belegt. Sie ist damit die nächste
prüfbare Kopfvorhersage, nicht eine nachträglich erfundene Bedeutung.

## Konkrete Lesungen, die das Raster bereits trägt

Das Raster erweitert die GDT631-Lesung tatsächlich auf neue Zellen:

| Stelle | Oberfläche | Arbeitsübersetzung |
|---|---|---|
| f20v.10 | `chocthy chol daiin` | trockenes Blatt-/Krautmaterial der O-Reihe: trocken, Grad III |
| f80r.42 | `checthy qokain` | trockenes CTH-Material der E-Reihe: heiß im qo-Rahmen, Grad II |
| f80r.16 | `qokain shecthy` | feuchtes CTH-Material der E-Reihe: heiß im qo-Rahmen, Grad II |
| f80r.18 | `shecthy qokain` | dieselbe E-Zelle in umgekehrter Oberflächenreihenfolge |
| f85r1.21 | `okaiin cheocthey` | trockene EO-CTH-Materialform, Rest `ey` offen: heiß im o-Rahmen, Grad III |
| f107v.4 | `qokain shocthy otaiin` | feuchte O-CTH-Materialform zwischen heiß Grad II und kalt Grad III |

Neun Mikroklammern wiederholen sich; insgesamt werden 49 konkrete lokale
Klauseln ausgegeben. Die Klammern lesen Materialzustand und Qualitätsgrad,
nicht einen erfundenen langen Arbeitsablauf.

Die Qualitätskontakte begrenzen zugleich die Sicherheit. Von 97 Kontakten bis
Distanz drei sind 55 unmittelbar; sieben folgen derselben Trocken-/Feuchtachse,
einer steht ihr entgegen und 89 liegen auf der orthogonalen Heiß-/Kaltachse.
Unmittelbare Unterstützung derselben Achse liegt in `CH-∅` dreimal, `CH-O`
einmal und `SH-∅` einmal vor. Für die E- und EO-Zellen gibt es noch keinen
solchen Direktkontakt. Deshalb wird trocken/feucht dort kompositionell geerbt,
nicht neu bewiesen.

Ein reales Warnbeispiel bleibt f25r.4: `shocthy ytchey` stellt die feuchte
O-Kandidatenform direkt neben eine kalt-trockene Qualitätsform. Das kann eine
zweite technische Zelle sein; es darf nicht stillschweigend als Bestätigung
gezählt werden.

## Register statt vier Synonyme

Die Zwischenklassen sind stark verteilt. In Sektion B stehen fusioniert 29
E-, aber keine O- oder EO-Token; im Herbal stehen fünf E-, 25 O- und zwei
EO-Token. Currier A trägt `E:2, O:28`, Currier B dagegen `E:53, O:8`.

Trotzdem sind die Klassen keine deterministischen Seiten- oder Handschriften-
Ersatzformen. 36 Seiten enthalten fusioniert mindestens zwei Klassen, vier
mindestens drei; mit den sieben all-reader-getrennten Spans sind es 38 und vier.
Die inklusive linke Grenzpopulation erhöht die erste Zahl auf 39. Auf einer
Seite stehen E und O gemeinsam. In dieser größten Population verteilt Currier A
die vier Klassen als `∅:41, E:3, O:34, EO:5`, Currier B als
`∅:114, E:53, O:8, EO:8`. Die beste Zwischenlesung ist daher
„registergeprägte, lokal auswählbare Form- oder Sachklasse“, noch nicht
„vier Schreibweisen desselben Wortes“ und noch nicht „vier benannte Stoffe“.

## Was außerhalb des Rasters liegt

Der breitere ZL3b-Zensus enthält 260 fusionierte Token, die mit `ch/sh`
beginnen und später `cth` enthalten. Das vorab definierte Vierklassenraster
erfasst 255 davon. Die fünf übrigen Formen sind vollständig bekannt:

| Stelle | Form | Einordnung |
|---|---|---|
| f29r.1 | `cheecthy` | `ee`-Nahkonkurrent des E-Slots |
| f82v.36 | `sheecthey` | `ee`-Nahkonkurrent des E-Slots |
| f34r.15 | `cheolchcthy` | längeres äußeres OL/CH-Kompositum |
| f3r.10 | `cholcthom` | längeres äußeres OL/CH-Kompositum |
| f93r.17 | `cholchecthody` | längeres äußeres OL/CH-Kompositum |

Die beiden `ee`-Formen sind ein echter nächster Erweiterungskandidat: Der
E-Slot könnte eine zweite Stufe besitzen. Die drei langen Formen testen eher
äußere Schachtelung als eine fünfte einfache Interfixzelle. Deshalb heißt das
Ergebnis „vollständiges `∅/e/o/eo`-Raster“ und nicht „vollständige Grammatik
aller Q…CTH-Formen“.

## Bild- und historische Reichweite

Keines der geerbten manuell geprüften Bilder trägt ein E-, O- oder EO-Zieltoken.
Die Bilder erlauben weiterhin nur den gemeinsamen CTH-Materialkopf und im
Herbal die engere Blatt-/Krautlesung. Sie unterscheiden `e/o` nicht nach Blatt,
Wurzel, Blüte, Samen, Medium, Gefäß oder Operation.

Zwei zeitnahe Vergleiche zeigen, dass die angenommene Mischarchitektur historisch
plausibel ist:

- [Pal.lat.1256](https://portail.biblissima.fr/en/ark:/43093/mdata4be843cf8c997190b99e016b5ad7760c77a6e2b9),
  1401–1450, kombiniert gelernte Drogennamen, lateinisch-deutsche Synonyme,
  Ersatzangaben und Dosisrubriken.
- [Wellcome MS 542](https://wellcomecollection.org/works/n674z2xd), frühes
  15. Jahrhundert, stellt Ganznamen und Pflanzenteil neben gebundene
  Qualitätsformen, Kürzel und expliziten Grad.

Das stützt ein System aus gelernten Namen plus kompakten Fachslots. Es liefert
keinen Voynich-Schlüssel und insbesondere kein `e=X` oder `o=Y`.

## Wörterbuchstand und nächster Hebel

V9 enthält 67 Einträge: 47 aus V8 und zwanzig neue Kompositionskarten. Neu sind
der geordnete Rahmen, die acht linken Shell-/Zielklassen, der innere
`o+cth+R`-Kopf und konkrete `...cthy`-Defaults. `e` und `o` bleiben bewusst
ohne deutsches Lexem.

Der nächste Hebel ist jetzt eng und praktisch: `octheey` im nächsten zulässigen
Material suchen, die beiden `ee`-Rivalen als mögliche E-Stufe prüfen und
gleichrestige E/O-Kontexte danach vergleichen, ob sie einen stabilen
Sachunterschied tragen. Erst dort können Begriffe wie Medium, Teil, Gefäß oder
Operation sinnvoll in einen freien Slot eintreten. Das vorliegende Ergebnis
liefert dafür die genaue Stelle im Wort, erfindet den Inhalt aber nicht vorab.
