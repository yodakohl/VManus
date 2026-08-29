# GDT630 report — sichtbare Pflanzenteile binden an Qualitätsgrade

## Ergebnis

Die aktuelle Arbeitsgrammatik liefert nun konkrete Klauseln in beiden
sichtbaren Reihenfolgen:

```text
PART | QUALITÄT | GRAD
QUALITÄT | GRAD | PART
QUALITÄT+GRAD | PART
```

Flüssig gelesen bedeuten alle drei: „Pflanzenteil: Qualität im Grad N.“ Die
Oberfläche bleibt in den Artefakten unverändert; deutsche Wortstellung wird
nicht zur Voynich-Wortstellung erklärt.

Die vier stärksten neuen Auszüge sind:

```text
f21v.3  chor qotol daiin
         Pflanzen-/Reproduktionsteil: im qo-Rahmen kalt, Grad III.

f22v.8  cthy qokol daiin
         Blattgut/Blattdroge: im qo-Rahmen heiß, Grad III.

f3r.3   chol daiin cthy
         Blattgut/Blattdroge: trocken, Grad III.

f8r.9   sholdaiin shor  ↔  shol daiin shor
         Blüten-/Fruchtstand: feucht, Grad III.
```

f21v, f22v und f3r sind als ganze Zielklausel in ZL3b, IT2a und RF1b exakt.
f8r behält dieselben Zeichen, aber IT2a setzt eine Grenze zwischen `shol` und
`daiin`. Es ist damit der erste fusionierte Qualitätswert mit unmittelbar
sichtbarem Partkopf.

## Zuerst die entscheidende Zählerkorrektur

Die GDT628-Gesamtzahlen 15 fusioniert und 120 getrennt umfassen nicht nur
Qualitätsausdrücke:

| Modus | kernhaltiges OL | nacktes `ol` | OR-Träger | Summe |
|---|---:|---:|---:|---:|
| fusioniert | 6 | 8 | 1 | 15 |
| getrennt | 80 | 11 | 29 | 120 |

Nur 86 Ausdrücke besitzen einen sichtbaren heiß/kalt/trocken/feucht-Kern.
Die acht `oldain/oldaiin`-Formen, elf getrennten `ol dN`-Phrasen und 30
OR-Fälle werden deshalb nicht automatisch als Qualitätsgrad übersetzt.

Praktische Defaults:

```text
QUALITY_CORE+ol+dN   Qualität, Grad N
ol+dN                Material-/Zustandswert N; Kern offen
OR+dN                Teil/Nominalkopf: Menge, Grad oder Klasse N
```

## Fusion betrifft die innere Phrase

Die 15 fusionierten Ausdrücke verteilen sich auf nur sechs Basis-/Wertzellen:

| Zelle | fusioniert | getrennte Gegenstücke |
|---|---:|---:|
| `ol` II | 1 | 3 |
| `ol` III | 7 | 8 |
| `or` III | 1 | 2 |
| `chol` III | 3 | 29 |
| `shol` III | 2 | 9 |
| `otol` III | 1 | 5 |

Alle sechs fusionierten Zellen besitzen getrennte Gegenstücke, zusammen 56.
Neun der 15 fusionierten Tokens sind in allen drei Lesungen exakt, 13 als
zusammenhängende Zeichenfolge grenznormalisiert. Bei f8r.9, f49r.6,
f100r.22 und f88v.15 wechselt ein Leser zwischen Fusion und Trennung, während
die Zeichenfolge in allen drei Fassungen erhalten bleibt. f55v.1 liefert eine
weitere paarweise `otoldaiin ↔ otol daiin`-Brücke, doch RF1b lässt dort `d`
aus.

Auch vier ZL-getrennte Ausdrücke erscheinen bei RF1b fusioniert: f4v.11,
f19v.3, f42r.10 und f51v.6. Insgesamt sind 93/120 getrennte Ausdrücke exakt
und 98/120 grenznormalisiert dreifach stabil.

Zwischen fusionierten und getrennten Vorkommen derselben sechs Zellen bleibt
kein lexikalisches unmittelbares Außentoken identisch. Fusion ist daher keine
Abkürzung für einen festen Stoffkopf. Sie ist die selektive Einwortschreibung
der inneren `BASE+dN`-Phrase. Ihre starke Beschränkung auf III (14/15; einmal
II, nie I/IV) verbietet vorerst eine frei produktive Fusionsregel.

## Elf unmittelbare sichtbare Partanbindungen

Unter den 80 getrennten kernhaltigen OL-Phrasen besitzen zehn einen
unmittelbaren bekannten Partkopf. Unter den sechs fusionierten Qualitätsformen
gibt es genau einen: f8r.9. Die elf Fälle liegen auf elf Seiten.

| Reihenfolge | Zahl | exakt dreifach | grenznormalisiert dreifach |
|---|---:|---:|---:|
| Part vor Qualität/Grad | 5 | 4 | 4 |
| Qualität/Grad vor Part, getrennt | 5 | 4 | 4 |
| Qualität/Grad vor Part, fusioniert | 1 | 0 | 1 |

Die neun stabilen Klauseln sind:

| Locus | sichtbare Klausel | Arbeitslesung |
|---|---|---|
| f100r.25 | `chol daiin ctheol` | cth-Pflanzenteilform: trocken III |
| f15v.11 | `chol daiin cthy` | Blattgut: trocken III |
| f21r.12 | `chor chol daiin` | Pflanzenteil: trocken III |
| f21v.3 | `chor qotol daiin` | Pflanzenteil: kalt III im qo-Rahmen |
| f22v.8 | `cthy qokol daiin` | Blattgut: heiß III im qo-Rahmen |
| f32v.10 | `chor chol daiin` | Pflanzenteil: trocken III |
| f3r.3 | `chol daiin cthy` | Blattgut: trocken III |
| f44v.3 | `otol daiin cthy` | Blattgut: kalt III im o-Rahmen |
| f8r.9 | `sholdaiin shor` / `shol daiin shor` | Blüten-/Fruchtstand: feucht III |

f5v.4 `shol daiin cthor` und f89v1.10 `cthey qokol daiin` sind kompositionell
gleich lesbar, aber nicht grenznormalisiert in allen drei Fassungen und stehen
daher außerhalb der Neuner-Ausgabe.

## Warum die rechte Partposition wichtig ist

`cthy` erscheint einmal links von `qokol daiin`, aber dreimal unmittelbar
rechts von kernhaltigen Gradphrasen. Zwei getrennte Zeilen tragen denselben
stabilen Ausdruck `chol daiin cthy`; eine weitere hat `otol daiin cthy`.
Die Dosislesung „drei Portionen“ ist bei einem erst danach genannten
Ingredienzkopf unökonomischer als eine vorangestellte Qualitätsrubrik.

Die zeitnahen Vergleichstexte erlauben beide Richtungen:

- Wellcome MS 542 setzt einen Drogenteil vor heiß/trocken und Grad III.
- Pal.lat.1234 um 1400 setzt Grad-Rubriken vor Listen von Stoffnamen.
- Wellcome MS 492 belegt Ingredienz–Einheit–Zahl und hält damit den
  Dosiskonkurrenten besonders für linksstehende Partköpfe am Leben.

Die Voynich-Folge kann natürliche Syntax oder eine technische Zellordnung
sein. Das ändert die konkrete Zellenlesung nicht.

## Offene Außenköpfe

Vier Nachbarn werden ausdrücklich weitergeführt, ohne sie zu erfinden:

1. `chcthy` steht zweimal unmittelbar links von einer kernhaltigen
   Grad-III-Phrase. f45r.3 `chcthy kchol daiin` ist dreifach exakt und erlaubt
   explorativ `ch+cthy = trockenes Blattgut`. f19v.4 verliert jedoch bei RF1b
   das `d`; die Komposition ist noch nicht allgemein genug.
2. `qotor` steht zweimal vor `chol daiin`. Es ist ein wiederkehrender
   nominaler Zutaten-/Materialkopf, aber seine konkrete Bedeutung und die
   Dosisalternative bleiben offen.
3. `chol` steht siebenmal unmittelbar links von einem Wertausdruck und kommt
   in beiden Schreibmodi vor. Das passt zu nominalem Trockenmaterial, kann bei
   `chol chol dN` und gegensätzlichen Qualitäten aber ebenso eine vorherige
   Qualitätszelle sein. Es wird nicht zum universellen Stoffkopf befördert.
4. `dy` kommt links in beiden Modi vor, bleibt aber strukturell und ohne
   Stoffbedeutung offen.

## V7 und nächster Schritt

V7 bewahrt alle 32 V6-Zeilen und ergänzt sechs Einträge: die
`sholdaiin/shol daiin`-Grenzbrücke, drei konkrete Partklauseln und zwei
beidseitige CTH-Rahmen. Unbekannte Tokens außerhalb der kleinsten Klammer
bleiben `OPEN`; es gibt keine Rückkehr zu „Arbeitsgut ausführen“.

Der engste nächste Bedeutungsschritt ist `chcthy`. Seine Lesung als
`ch+cthy = trockenes Blattgut` muss gegen die ganze geerbte `cth`-Familie und
gegen analoge `k/t/sh+cth*`-Formen bestehen. Zuerst werden nur die vorhandenen
179 Seiten benutzt; keine neue Seite und kein Bild werden geöffnet.

## Grenze

GDT630 übersetzt nicht das ganze Manuskript. Es liefert aber statt einer
generischen Satzschablone neun leserstabile, praktisch konkrete
Pflanzenteil–Qualität–Grad-Klauseln, eine neue Fusionsbrücke und eine klare
Trennung zwischen bedeutungstragenden Qualitätskernen und offenen Trägern.
