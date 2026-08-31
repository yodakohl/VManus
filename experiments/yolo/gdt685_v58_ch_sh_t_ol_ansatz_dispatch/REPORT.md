# GDT685 — Zustandszelle statt erfundenem Ansatzkopf

Status: `REJECT_UNIVERSAL_ANSATZ_HEAD__PASS_540_STATE_CELL_DISPATCH__V58_EIGHT_GENERIC_HEADS_REMOVED`

## Ergebnis

Die von GDT684 vorgeschlagene nächste Konkretisierung war zu groß:

```text
chol = Trockenansatz
shol = Feuchtansatz
tol  = Kaltansatz
```

Die vollständige Prüfung trägt den Zustand, aber nicht das gemeinsame
Substantiv. Die beste Arbeitsregel ist:

```text
chol -> trocken; Kopf sichtbar oder lokal geerbt
shol -> feucht; Kopf sichtbar oder lokal geerbt
tol  -> kalt; Kopf sichtbar oder lokal geerbt
```

Steht ein Pflanzenteil, Pulverstoff, Holzstoff oder Ansatz tatsächlich im
lokalen Block, bindet die Qualität daran. Fehlt der Kopf, bleibt er offen.
`Trockengut`, `Feuchtgut`, `Kaltgut` und die drei `-Ansatz`-Formen sind keine
Defaultwörter mehr.

Das ist keine Rückkehr zum generischen Renderer. Im Gegenteil: V58 entfernt
acht erfundene Sammelnomen und lässt genau die Information stehen, die das
Zeichenfeld selbst derzeit trägt.

## Vollständiger Bestand

| Form | Vorkommen | Seiten | dreifach reader-exakt | Gradformen | V58-Reparaturen |
|---|---:|---:|---:|---:|---:|
| `chol` | 343 | 125 | 303 | 43 | 6 |
| `shol` | 163 | 86 | 146 | 13 | 1 |
| `tol` | 34 | 25 | 27 | 1 | 1 |
| gesamt | 540 | 151 | 476 | 57 | 8 |

Alle 540 Quellrollen sind `QUALITY_STATE_CARRIER`; keine einzige ist als
Zubereitungsnomen oder Aktion registriert. Das größere kernhaltige OL-Gitter
umfasst 935 Token auf 167 Seiten, davon 833 dreifach reader-exakt. 23 der 24
erwarteten Qualitätszellen sind belegt. Diese Produktivität ist der Grund,
warum drei separat gelernte Ganzwörter unnötig werden.

## Warum `-Ansatz` nicht mitkomponiert

Vier voneinander unabhängige Beobachtungen zeigen dieselbe Richtung:

1. 57 Ausdrücke realisieren `chol/shol/tol` mit einem Wert I–IV. Darunter sind
   49 exakte getrennte Basistoken. Die Zieloberfläche besetzt dort den
   Qualitätsslot, nicht einen neuen Stoffslot.
2. Sieben Ausdrücke besitzen einen sichtbaren Pflanzenteilkopf. Lesungen wie
   `chor chol daiin` ergeben `Pflanzenteil: trocken, Grad III`; ein zusätzliches
   `Trockenansatz` würde den geschriebenen Kopf verdrängen.
3. Exakte `E+OL`-Ganzwörter tragen den Nomenkopf ausdrücklich:
   `cheol = trockener Drogenstoff` (142), `cheor = trockener Drogenteil` (71)
   und `tcheol = kalt-trockener Drogenstoff` (6). Ihre publizierte Lizenz
   verbietet gerade die Rückübertragung eines nackten OL-Kopfes.
4. Zehn Zieltoken berühren sichtbar ein weiteres `ol`. Acht davon sind echte
   freie Kontakte, zwei werden von einem Alternativleser gebunden. Folgen wie
   `chol | ol` und `ol | shol` sind mit `trocken | Grundansatz` beziehungsweise
   `Grundansatz | feucht` lesbar. Ein universal eingebauter Ansatzkopf würde
   hier zwei Ansatzkarten erzeugen.

GDT628 hatte bereits festgestellt, dass OL unter einem sichtbaren
Qualitätskern im Deutschen meistens keinen eigenen Beitrag braucht. GDT685
zieht diese Kompositionsregel nun konsequent bis in den praktischen Reader.

## Der verbleibende Grenzrivale

Eine lokale Segmentierung `CHO|L` oder `SHO|L` bleibt formal denkbar, weil
`cho/sho` als Zubereitungsschalen und gebundenes `l` in anderen Ganzwörtern
existieren. Sie ist kein gemeinsames Modell für die drei Ziele: `tol` bräuchte
eine neue `TO|L`-Karte, und in den sichtbaren Teil–Qualität–Grad-Klauseln würde
ein pauschales Holz- oder Ansatznomen übervorhersagen. Darum bleibt sie ein
lokaler Grenzrivale, nicht der Rendererdefault.

## Was V58 tatsächlich ändert

Sieben Zeilen und acht Positionen werden neu gerendert:

| Stelle | V58-Lesung |
|---|---|
| f27r.9#4 `chol` | `trocken`; Kopf zwischen Feucht- und Kaltansatzzelle offen |
| f30r.9#3 `chol` | erste Trockenfraktion: `trocken` |
| f80v.35#1 `tol` | `kalt`; das folgende Wort benennt den Holzdrogenansatz bereits |
| f86v3.18#5 `shol` | vorheriger Pulverstoff: `feucht` |
| f86v3.19#5/#7 `chol` | zwei getrennte Zustandszellen: jeweils `trocken` |
| f86v6.5#3 `chol` | Holzstoff: `trocken` |
| f8r.15#3 `chol` | Arzneikompositumstoff: `trocken` |

Die vollständige Vorher-/Nachher-Prosa steht in `V58_PATCHED_LINES.tsv`.
Zwei Beispiele zeigen die gewünschte Richtung:

```text
f86v3.18
Fertig getrockneten Pulverstoff nehmen: feucht; den angefeuchteten Ansatz
fertigstellen.

f8r.15
Arzneikompositumstoff: trocken, bis zur Mittelstufe; eine Charge unter Wärme
getrockneter Droge leicht nachtrocknen.
```

## Ehrlicher Informationsgewinn

| Schuldmaß | V57 | V58 | Änderung |
|---|---:|---:|---:|
| kuratierte Kartenpositionen | 139 | 131 | -8 |
| Slash-/Mehrfachglossen | 44 | 36 | -8 |
| harte generische Träger | 47 | 39 | -8 |
| reine Zustände ohne gebundenes Objekt | 65 | 73 | +8 |
| mechanische Schuldunion | 172 | 172 | 0 |
| breite Spezifität offen | 335 | 335 | 0 |

Die acht Positionen sind semantisch sauberer, aber noch nicht objektvollständig.
Darum sinken die falschen generischen Karten, während die ehrliche Kategorie
`Zustand ohne gebundenen Kopf` steigt. Die Union bleibt unverändert. Das ist
gewollt: Ein Renderer wird nicht besser, indem er fehlende Nomen erfindet.

Alle 86 bereits lizenzierten Aktionspositionen bleiben unverändert.

## Nächster Zug

Die nächste große Reparaturachse ist `dain/daiin/qodaiin`. Der vierstufige
Schriftwert I–IV ist bereits produktiv. Offen ist sein konkreter Kopf:

- nach einer Qualitätszelle ist er Grad;
- an einem sichtbaren Stoff-/Teilkopf kann er Menge oder Portion sein;
- in anderen Frames kann er Klasse oder Strukturwert bleiben;
- `qodaiin` darf nicht frei zwischen `Grad III` und `drei Teilen` springen.

Der nächste Durchlauf soll deshalb nicht noch mehr Wörter mit einer
universellen Zahl belegen. Er soll jede aktuelle V58-Position nach ihrem
sichtbaren Wertkopf dispatchen und nur dort konkrete `Grad`-, `Mengen-` oder
`Klassen`prosa erzeugen, wo der lokale Kopf sie trägt.

## Claim ceiling

GDT685 ist eine vollständige, reproduzierbare Arbeitslesung der 540 bereits
zugelassenen Zielvorkommen und ein konkretes V58-Rendererupdate. Es öffnet
keine neue Seite. Es identifiziert keine Pflanze, Zutat, Flüssigkeit,
Krankheit, Person, Heilung, Sprache, Lautung oder historisches Codebuch.
`tol = kalt` bleibt ein Arbeitsdefault; 64 Zielpositionen besitzen weiterhin
Alternativleser-Varianten.
