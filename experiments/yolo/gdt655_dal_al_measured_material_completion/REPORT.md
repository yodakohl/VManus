# GDT655 — DAL ist eine abgemessene Rohstoffmenge

## Ergebnis

V32 ordnet die große AL/DAL-Familie zu einem gemeinsamen Werkstattmodell. 18
Karten besitzen mindestens einen dreileser-exakten Anker; `daiil` kommt als
eine ausdrücklich reader-instabile, aber vollständig vorhergesagte Karte
dazu. Insgesamt werden 567 Zielpositionen auf 499 Zeilen neu gelesen oder
revidiert. 426 Zielpositionen sind dreileser-exakt, 429 split-normalisiert.

Der neue Sachunterschied lautet:

```text
AR    Mischungsanteil / Fraktion
AL    Rohstoffklasse
DAL   abgemessene Rohstoffmenge
OR    abgeteilte Portion
```

Damit ist `DAL` nicht länger bloß ein isoliertes Etikett
„Rohdrogenposten“. Praktisch kann man es als **abgewogene Eingangsmenge**
lesen: erst wird ein Rohstoff einer Klasse bezeichnet, dann eine Menge davon
für den Ansatz abgemessen, später eine Portion abgeteilt.

| Reihe | Stufe I | Stufe II | Stufe III |
|---|---|---|---|
| Rohstoffklasse | `al` Klasse I | `ail` Klasse II | `aiil` Klasse III |
| abgemessene Menge | `dal` Menge I | `dail` Menge II | `daiil` Menge III |

Die Grund- und Abschlussformen werden ebenfalls konkret:

- `aly` — Rohstoffklasse I, Grundform;
- `aldy` — Rohstoffklasse I, abgeschlossen;
- `daly` — abgemessene Rohstoffmenge I, Grundform;
- `daldy` — abgemessene Rohstoffmenge I, abgeschlossen.

Die beobachteten Schalen bleiben kurz und verwenden dieselbe Qualitätsachse
wie die schon gelesenen `chy/chey`- und `shy/shey`-Paare. Null E markiert die
Anfangsposition, ein E die Mitte; die alte Zusatzdeutung „gebunden“ oder
„angefeuchtet“ wird hier nicht weitergetragen:

- `chdal` — trockene abgemessene Rohstoffmenge I am Gradanfang;
- `chedal` — trockene abgemessene Rohstoffmenge I in der Gradmitte;
- `shdal` — feuchte abgemessene Rohstoffmenge I am Gradanfang;
- `shedal` — feuchte abgemessene Rohstoffmenge I in der Gradmitte;
- `odal` — abgemessene Rohstoffmenge I im Ansatz;
- `qodal` — dieselbe Menge im QO-Rahmen.

Drei alte Ganzkarten werden sichtbar revidiert. `chdaly` heißt nun
**trockene abgemessene Rohstoffmenge I am Gradanfang, Grundform**, `sodal`
**abgemessene Saat-Rohstoffmenge I im Ansatz**. Vor allem wird die geerbte
Kollision `oral = Ansatz aus Wurzelrohstoff` beseitigt: f79r.19 trennt in IT2a
und RF1b direkt `or al`, also liest V32 `oral` als **Rohstoffportion, Klasse I**.
Die alte O+RAL-Zubereitungslesung bleibt als Rivale sichtbar.

## Der entscheidende Parallelbeleg

f45v.4 ist in allen drei Transkriptionen identisch:

```text
okchy qockhy dain dail dair shy
            └──┬──┘ └─┬─┘ └─┬─┘
             Wert II  AL II  AR II
```

`dair` war bereits die abgemessene Fraktion II. Genau zwischen dem Wertträger
`dain` und der R-Fraktion steht `dail`. „Abgemessene Rohstoffmenge II“ erhält
den L/R-Unterschied; ein unabhängiger „Rohdrogenposten II“ wäre eine neue
Sonderklasse nur für diese eine Zelle.

Zwei weitere Stellen zeigen, dass D abfallen kann:

- f55r.9 hat in ZL3b `dar … dal … dar`, während RF1b parallel
  `ar … al … ar` schreibt;
- f78r.27 hat in ZL3b und IT2a `daiil`, RF1b dagegen `aiil`.

Das ist der Grund, `daiil` trotz null dreileser-exakter Belege aufzunehmen.
Die Karte ist nicht als sicher etikettiert: Sie hat einen eigenen
`READER_UNSTABLE_COMPOSITIONAL_WHOLE`-Status. Ihr Wert wird von den Stufen I
und II vorhergesagt, zwei Leser stimmen überein, der dritte liefert genau die
erwartete Form ohne D, und die Karte schließt eine reale Zeile. `aiiil` bleibt
dagegen draußen: Dort lesen beide anderen Leser M statt L, und die Karte
schließt nichts. Auch `chdaldy` bleibt ohne Karte.

## Sichtbare Grenzen — und die fehlende Grenze

AL ist als rechter Block in `s al`, `r al`, `ch al` und `or al` sichtbar.
DAL wird nach außen dreimal durch `daldy ↔ dal dy/dal y` abgegrenzt; `sodal ↔
s odal` zeigt zusätzlich die äußere S+ODAL-Struktur.

Es gibt aber in den 4.137 zugelassenen Zeilen kein direktes `d al ↔ dal` und
kein `a l ↔ al`. Darum bleiben `D_MEASURE` und `AL_CLASS_I` interne
Strukturtags, keine frei übersetzbaren Voynich-Wörter. Der stärkste Rivale
bleibt ein gelerntes Ganzwort `DAL = Rohdrogenposten`; für AL bleibt
`Rohstoffform I` möglich.

## Sieben neu vollständige Zeilen

```text
f75r.40  dar shedy qokain shedy dal keedy rshedy
          Abgemessene Fraktion I; in der Gradmitte feucht abgeschlossen;
          heiß, Grad II; erneut in der Gradmitte feucht abgeschlossen;
          abgemessene Rohstoffmenge I; am Gradende heiß abgeschlossen;
          eingeweichte Wurzel.

f77v.13  sor sheol chdy qokeedy dar shedy chedy qokal chedy qokey
          lshedy dal
          Samenportion; feuchtes Drogenmaterial; am Gradanfang trocken
          abgeschlossen; am Gradende heiß abgeschlossen; abgemessene
          Fraktion I; in der Gradmitte feucht, dann trocken abgeschlossen;
          heiße Substanz; erneut in der Gradmitte trocken abgeschlossen;
          heiß in der Gradmitte; eingeweichtes Drogenholz; abgemessene
          Rohstoffmenge I.

f77v.30  shey ol sheey qokedy lchedy qokaiin dal daiin chedy
          In der Gradmitte feucht; Drogenstoff/Ansatz; feucht am Gradende;
          in der Gradmitte heiß abgeschlossen; getrocknetes Drogenholz;
          heiß, Grad III; abgemessene Rohstoffmenge I; Menge III;
          in der Gradmitte trocken abgeschlossen.

f78r.27  daiin chckhal daiil aldy
          Menge III; trockenes Arzneikompositum, Rohstoffform I;
          abgemessene Rohstoffmenge III; Rohstoffklasse I, abgeschlossen.

f83r.14  qokchedy qokeedy shedy qokshedy dal lchedy qokaiin shcthy dal sy
          In der Gradmitte heiß-trocken abgeschlossen; am Gradende heiß;
          in der Gradmitte feucht und danach heiß-feucht abgeschlossen;
          abgemessene Rohstoffmenge I; getrocknetes Drogenholz; heiß,
          Grad III; feuchtes Blatt-/Krautgut; erneut abgemessene
          Rohstoffmenge I; Saatgut, Grundform.

f83r.47  otchdy qokchdy shedal
          Kalt-trockener Ansatz am Gradanfang abgeschlossen;
          heiß-trockener Ansatz am Gradanfang abgeschlossen;
          feuchte abgemessene Rohstoffmenge I in der Gradmitte.

f83r.48  dal cheol lol chdal aiin
          Abgemessene Rohstoffmenge I; trockener Drogenstoff; Holzstoff;
          trockene abgemessene Rohstoffmenge I am Gradanfang; Menge III.
```

f83r.47 und f83r.48 sind dreileser-strikt. f78r.27 ist bewusst nicht strikt,
weil RF1b `aiil` statt `daiil` und `ol y` statt `aldy` liest.

## Abdeckungsgewinn

V31→V32 erhöht die bekannten Tokenpositionen von 15.846 auf 16.398 und senkt
die unbekannten von 16.493 auf 15.941. Vollständige Mehrwortzeilen steigen von
123 auf 130, strikte Vollzeilen von 75 auf 77. Das Wörterbuch wächst von 510
auf 529 Einträge, das laufende Arbeitsglossar von 437 auf 453 Oberflächen. Es
enthält 452 dreileser-verankerte Karten und die gesondert markierte
`daiil`-Vorhersage. 225 Zeilen besitzen jetzt nur noch ein unbekanntes Token,
davon 54 dreileser-strikt.

## Historische Passung und nächste Arbeit

Die Abfolge Droge/Rohstoffklasse → abgemessene Eingangsmenge → Portion passt
zu einer kompakten Rezept- oder Materia-medica-Notation um 1420.
[Huntington HM 19079](https://www.huntington.org/collections/lib-p15150coll7-49482)
von 1400–1425 erklärt pharmazeutische Gewichtszeichen vor seinen Rezepten;
Tadhg Ó Cuinns [Materia medica von 1415](https://celt.ucc.ie/published/G600005/index.html)
verbindet Drogennamen, Pflanzenteile, Qualitäten und Grade und unterscheidet
bei Einträgen ausdrücklich Anfang, Mitte und Ende innerhalb eines Grades;
[Wellcome MS.542](https://wellcomecollection.org/works/n674z2xd) verbindet
Rezepte und Materia-medica-Glossare. Diese Texte stützen die gemischte
Codebook-Architektur, nicht die Lautung oder Einzelbedeutung eines Zeichens.

Der nächste logische Ausbau ist die schon beobachtete AL-Schalenfamilie um
`chal/cheal/shal/sheal` und ihre K/T-/O-/QO-Schwestern. Besonders `chal`
schließt bereits eine strikte V32-Ein-Loch-Zeile. V32 bleibt eine explorative
Arbeitsübersetzung, kein behaupteter historischer Klartext.
