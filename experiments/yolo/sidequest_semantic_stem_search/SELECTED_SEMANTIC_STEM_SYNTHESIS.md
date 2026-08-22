# Konsolidierte konkrete Wortstammtheorie

## Wonach wir gesucht haben

Nicht nach abstrakten Slots, Clustern oder vorab festgelegten grammatischen
Achsen, sondern nach einem kleinen Wörterbuch, mit dem ein Werkstattschreiber
konkrete Dinge und Handlungen ausdrücken könnte: Wasser, Portion, Maß, Stelle,
Ansatz, Pflanze, Gießen, Waschen, Baden, Rühren, Seihen, Ruhen und Abschluss.

Vier konkurrierende Lesarten wurden schnell gegeneinander gehalten:

1. möglichst kleine sichtbare Atome wie `o`, `a`, `e`, `l`;
2. ein weitgehend kompositionales Flüssigkeits-/Rezeptmodell;
3. ein medizinisch-apothekarisches Stammlexikon mit vielen lokalen
   Zusammensetzungen;
4. ein konservatives Hybridmodell aus längsten selbständigen Stämmen,
   wenigen engen Kompositionsregeln und konkreten Ganzwörtern.

Ausgewählt ist Modell 4. Es erklärt 263 der 381 Prosaereignisse durch sichtbare
Stämme oder Komposita. Die übrigen 118 Ereignisse haben ebenfalls einen kurzen
konkreten Wert, werden aber als ganze Karten gelernt. Dadurch muss kein Stamm
seine Bedeutung wechseln, nur um eine höhere Abdeckungszahl zu erzeugen.

## Das neue Kernwörterbuch

| Stamm | kurze Arbeitsbedeutung | typische Bildungen |
| --- | --- | --- |
| `AIR` | fließende Flüssigkeit | `chair` Quellwasser, `kair` Rückstrom, `okair` Oberlauf, `schedair` klarer Abfluss |
| `AIIN` | Maß | `aiin` Maß, `otaiin` gleiches Maß/Dauer, `okaiin` nach Maß |
| `AIN` | Portion | `kain` Portion, `okain` Portion zugeben, `orain` frische Portion |
| `AL` | Stelle | `al` Stelle, `okal` an der Stelle auftragen, `otal` folgende/untere Stelle |
| `AR` | aus/von | `dar` daraus, `qokar` von oben/an der Quelle, `cheoar` aus dem Auszug |
| `OR` | Zubereitung | `or/chor` Ansatz, `orain` frische Zubereitung |
| `OL` | weiter/und | allein als Verbindung, in ausgewählten Bildungen Weiterführung |
| `OK` | geben/aufbringen | `okain` Portion geben, `okal` an Stelle geben, `oky` Ansatz anwenden |
| `OT` | danach/folgend | `otaiin` folgendes Maß, `otal` folgende Stelle, `otar` danach auslassen |
| `HO` | Pflanze | `cho/sho` Bildpflanze, `chochor` Pflanzenteil |
| `Y` | Ansatz | `y` laufender Ansatz, `oky` Ansatz geben, `lchy` Ansatz abziehen |
| `DY` | Ende | an abgeschlossenen Wasch-, Heiz-, Ruhe- und Ablasswörtern |
| `E` | ruhen | `cheedy/shedy/tedy` stehen lassen; Ende |
| `EEY` | warm | `okeey` Wärme geben/temperieren |
| `CTHY` | bereit | Reife- oder Bereitschaftszustand |
| `CHD` | rühren | `chdy/chedy` gleichmäßig rühren |
| `LCH` | ablassen | `lchy`, `lchedy`, `lchedal` |
| `LSH` | waschen | `lsho`, `lshedy` |
| `CKHY` | Durchlauf | verbundener Lauf oder Kanal |
| `CKHE` | seihen | durch Tuch oder engen Filter führen |

Die vollständigen 27 Einträge einschließlich schwächerer Werkstattstämme
stehen in `SELECTED_CONCRETE_STEMS.tsv`.

## Die stärkste innere Wortfamilie

Nur in einer eng begrenzten Umgebung wird sichtbare Länge als Bedeutung
gelesen:

```text
qokedy    = spülen; Ende
qokeedy   = baden/eintauchen; Ende
qokeeedy  = vollständig durchtränken; Ende
```

Das zusätzliche `e` verlängert hier den Flüssigkeitskontakt. Diese Regel wird
nicht auf jedes `e` im Wörterbuch ausgedehnt.

## Was nicht übernommen wurde

- `o = Wasser` verliert gegen den engeren Stamm `AIR`. `o` steckt ebenso in
  Zubereitungs-, Folge-, Orts- und Ganzwörtern.
- `ol = Öl` verliert gegen die häufige Verbindungs-/Weiterlesung von `ol`.
  Öl bleibt ein konkreter lokaler Stoffwert, aber kein tragfähiger globaler
  `OL`-Stamm.
- `ch`, `k`, `e` und End-`y` werden nicht überall als Morpheme gelesen. Ihre
  vermeintlichen Bedeutungen würden bei den längeren Karten sofort wechseln.
- Die A-Reihe wird nicht zu `A + Endung` zerlegt. `AL`, `AR`, `AIN`, `AIIN`
  und `AIR` sind fünf selbständige Werkstattkürzel: Stelle, Herkunft, Portion,
  Maß und Fluss.

## Historische Ähnlichkeit

Das Modell ist keine einfache Buchstabenchiffre. Zeitnahe Schlüssel zeigen
aber, dass Werkstätten Alphabete, Silben, häufige Ganzwörter, Varianten und
eigene Nomenklatorwerte mischten. Ein System mit produktiven Kürzeln plus
memorierten Ganzkarten wäre daher leicht lehrbar.

Der konkrete Wortschatz ähnelt knapper Rezeptpraxis. Wellcome MS.418 verwendet
in einer Sammlung medizinischer Wässer Formeln wie `Recype herbam`, `aqua`
und die Gabe des Wassers als Trank. Wellcome MS.683 bietet `Recipe`, `infunde`,
Öle, `fiat unguentum` und `ana`. Diese Quellen liefern keine Voynich-Lautwerte,
aber genau die richtige semantische Granularität: **Wasser**, **Öl**, **Anteil**,
**Maß**, **gießen**, **mischen**, **seihen**, **erwärmen**, **ruhen**, nicht
„Pflanzenmaterial zeitgebunden beschaffen“.

- [Wellcome MS.418 – medizinische Wässer](https://wellcomecollection.org/works/f6nzyzh4)
- [Wellcome MS.683 – norditalienisches Receptarium](https://wellcomecollection.org/works/w6ne7k4t)
- [Wellcome MS.140 – Wässer, Öle und Salze](https://wellcomecollection.org/works/actgjagb)
- [Liber Secreti Naturali, 1425–1450](https://digital.sciencehistory.org/works/wg1tm9j)

## Kurze Rücklesung

`chey daiin chey lchedy`

> Ansatzteil – Maß – Ansatzteil – ablassen; Ende.
>
> Einen Teil nach dem vorgeschriebenen Maß nehmen und anschließend ablassen.

`lsho qokey lshedy`

> Waschwasser beginnen – Wasser zugeben – waschen; Ende.
>
> Waschwasser einlassen, warmes Wasser zugeben und einmal waschen.

`cheedar chldaiin chedy qokain checthy chealror solkeedy`

> Beckenstation – Ruhezeit – rühren – Portion geben – bereit – bis klar –
> absetzen; Ende.
>
> Das Becken richten, den Ansatz ruhen lassen, rühren und eine Portion
> zugeben; wenn der Strom klar ist, erneut absetzen lassen.

## Neue Arbeitsbasis

Die zehn Seiten werden nun als gemischtes Werkstattregister gelesen:

- Pflanzenbilder liefern die unausgesprochene Bildpflanze; der Text nennt
  Portion, Maß, Flüssigkeit, Zubereitung und Arbeitsschritte.
- Die Biological-Seiten verwenden denselben Kernwortschatz für Becken,
  Körperstellen, Spülen, Baden, Rühren, Seihen und Ablassen.
- Die drei Kreis-/Sternseiten behalten ein separates, lokal memoriertes
  Etikettenwörterbuch; Prosa-Stämme werden dort nicht erzwungen.

Das ist ab jetzt die bevorzugte kreative Lesung dieses Sidequests. Die
vollständigen Dateien enthalten 173 Karten, 381 Prosaereignisse und konkrete
Übersetzungsauszüge. `f84` und `f84r` wurden nicht geöffnet.
