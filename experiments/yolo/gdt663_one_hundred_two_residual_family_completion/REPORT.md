# GDT663 — die 102er-Restfront wird zu einem konkreten V40-Rezeptregister

Status: `PASS_1105_TARGET_POSITIONS__V40_CONCRETE_RECIPE_REGISTER`

## Ergebnis

V40 schließt alle 1.105 V39-Restpositionen: 102 Formen in 949 Zeilen auf 168
Seiten. Sämtliche 105 Ausgangszeilen sind vollständig übersetzt. Global werden
118 weitere Mehrwortzeilen vollständig.

Die neue Fassung ist konkreter als V39. Sie enthält nicht nur Trocken-, Feucht-,
Heiz- und Kühlstufen, sondern erstmals auch ausdrücklich Salz, Laugensalz, ein
Pfundmaß, ein Bündel Kraut, ein Holzgefäß, Rückstand und Ruhenlassen. Diese
Lesungen sind aggressive, ersetzbare Arbeitskarten; die riskanten Karten sind
nicht als bewiesener Klartext versteckt.

## Architektur

| Kartentyp | Formen | Positionen |
|---|---:|---:|
| produktive Komposita | 82 | 817 |
| Eintragskomposita | 7 | 76 |
| gelernte Handlungswörter | 8 | 44 |
| andere gelernte Ganzwörter | 4 | 5 |
| freies `l`, kontext-/lesergebunden | 1 | 163 |

Das produktive Grundschema bleibt:

`[Rahmen] + [Stoffkopf] + [Behandlung] + [Stufe/Form] + [Menge] + [Abschluss]`

Die Ganzwörter verhindern, dass ein auffälliger Teilstring automatisch überall
dieselbe Bedeutung erhält. So ist freies `l` ein mögliches Gewichtssigel,
während gebundenes initiales `l-` weiterhin die Holzdrogenfamilie organisiert.
Ebenso darf `alkal=Laugensalz` keinen freien Wert `alk` erzeugen.

## Die dichte Front

| Form | n | V40-Arbeitslesung |
|---|---:|---|
| `l` | 163 | freies Gewichtssigel oder belegte Leserzusammenschreibung |
| `chody` | 78 | abgeschlossener Trockenansatz |
| `char` | 75 | Trockenfraktion I |
| `shody` | 46 | vollständig eingeweichter Ansatz |
| `olaiin` | 39 | Drogenstoff, Menge III |
| `ytaiin` | 39 | Eintrag: kalt, Stufe III |
| `lkain` | 33 | Holzdroge, heiß auf Stufe II |
| `chedaiin` | 32 | abgemessene Trockendroge, Dosis III |
| `chedar` | 31 | abgemessene Trockenfraktion I, Mittelstufe |
| `olkaiin` | 28 | heiße Drogenbasis, Stufe III |
| `lkedy` | 26 | erhitzte Holzdroge, Mittelstufe, fertig |
| `opchey` | 26 | Trockenpulveransatz, Form I |
| `ldy` | 24 | fertig aufbereitete Holzdroge |
| `dchor` | 23 | abgemessener Pflanzenteil |
| `qor` | 21 | nimm eine Drogenportion |
| `lo` | 20 | Holzabsud |
| `dary` | 19 | abgemessene Fraktion I, abgeschlossen |
| `okair` | 18 | heiße Drogenfraktion II im Ansatz |
| `chdar` | 17 | abgemessene Trockenfraktion I, Anfangsstufe |
| `ched` | 17 | Trockenstufe Mitte, abgeschlossen |

Die komplette 102er-Karte mit Zerlegung, Rivalen, Häufigkeit und
Leservarianten steht in `artifacts/TARGET_DECISION_DECK.tsv`.

## Die `l`-Korrektur

Ein blindes `l=Holzdroge` an allen 163 Stellen wäre falsch. Nur 38 Stellen sind
in den drei Leserfassungen als freies `l` exakt stabil. Die beiden
Alternativleser schreiben 105 weitere ZL3b-Grenzen sichtbar zusammen, darunter
15-mal `o | l -> ol`, dreimal `qo | l -> qol` und zahlreiche `l | X -> lX`
vor bereits bekannten Holzdrogenformen. V40 benutzt an diesen Stellen genau die
belegte Zusammenschreibung als occurrence-spezifische Karte und unterdrückt in
der praktischen Satzfassung die doppelte Nachbarglosse.

Außerhalb einer sichtbaren Zusammenschreibung liest V40 freies `l` vorläufig
als `Pfund/Gewichtseinheit`; im einzigen Frontbeispiel `f80v.12` ergibt das
zeilenfinal tatsächlich „ein Pfund“. Der Holzdrogenwert bleibt der stärkste
Rivale. Historisch ist ein gemischtes Register aus Wörtern und Maßsiglen
plausibel: medizinische Rezepte verwenden *libra* als Pfund mit Kürzeln wie
`lib`, `lb` oder einem Pfundzeichen. Das ist nur ein Vergleich, keine
Glyphidentifikation ([Übersicht zu Gewichten und Siglen in medizinischen
Rezepten](https://www.ncbi.nlm.nih.gov/books/NBK608570/)).

## Bewusst riskante, aber informative Ganzwörter

| Form | V40 | ernsthafter Rivale |
|---|---|---|
| `alkal` | Laugensalz / Alkali | heißer Rohstoff I |
| `solaiin` | Salz, Menge III | Saatgut, Charge III |
| `cthoj` | ein Bündel Kraut | bloßer Krautansatz |
| `ylg` | in ein Holzgefäß geben | Drogenposten/Abschlusszeichen |
| `deeeese` | bis zur letzten Stufe ruhen lassen | vierfach konzentrierte Species |
| `dosg` | eine Dosis Rückstand | abgemessener Samenansatz |
| `cthosg` | Krautrückstand | fertige Krautarzneispecies |

`alkal` sieht verführerisch wie ein lesbares Lehnwort aus; gerade deshalb
bleibt es eine LOW-Karte und erzeugt keine Buchstaben- oder Sprachbehauptung.
`sol=Salz`, `sg=Rückstand`, `j=Bündeleinheit` und `ylg=Holzgefäß` sind
Vorhersagen für kommende Schwesterformen, nicht nachträgliche Gewissheiten.

## Konkrete Passagen

`f23v.7 — otor oiin sho shol qokol daiin sol daiin ylg`

> Kalte Drogenportion im Ansatz, Zubereitungsform III; Feuchtansatz und
> Feuchtgut auf Stufe III erhitzen; drei Teile Salz; in ein Holzgefäß geben.

`f24r.17 — sshey otam sham cthoj oky`

> Eingeweichte Saat Form I; ein Maß kalter Ansatz und ein Maß Flüssigkeit; ein
> Bündel Kraut; leicht erhitzten Ansatz beginnen.

`f75v.63 — oteey qol chey qokey oldy olyly`

> Ansatz auf Kühlendstufe; bis zur mittleren Trockenstufe getrockneten Stoff
> zugeben; bis zur mittleren Heizstufe; fertiger Auszug; ein zweites Mal
> abseihen.

`f80v.12 — ycheol kain shey qokain chedy qokol olkain shy l`

> Trockener Drogenstoff dieser Droge; Heizstufe II; bis zur mittleren
> Einweichstufe; nochmals Heizstufe II; Trocknung abschließen; heißes
> Drogenmaterial Stufe II erhitzen; leicht anfeuchten; ein Pfund.

`f81r.5 — qol cheol okeey ol ol olaiin ol or ain`

> Trockenen Drogenstoff zugeben; Ansatz bis Heizendstufe; Grundansatz; drei
> Teile Trägerflüssigkeit; weiterer Grundansatz; zwei Drogenportionen.

`f82v.12 — dal shol dar ol qoky qol chedy qokar qoteytyqoky chcthy qoky`

> Rohstoffmenge I und Fraktion I abmessen; Feuchtgut und Grundansatz leicht
> erhitzen; getrockneten Stoff und heiße Fraktion I zugeben; bis Mittelstufe
> kühlen und danach heiß ansetzen; getrocknete Krautdroge; leicht erhitzen.

`f93r.29 — dain cho ctho cthosg`

> Zwei Maße; Trockenansatz; Krautansatz; Krautrückstand.

Die algorithmischen Fassungen aller 105 Grenzzeilen stehen in
`artifacts/FRONTIER_102_COMPLETIONS.tsv`; die praktische manuelle Glättung und
die drei unabhängigen Leserrollen sind in `MANUAL_PASSAGE_AUDIT.md`
dokumentiert.

## Praktische Sprache statt Metaglosse

Die strukturelle V39-Karte für nacktes `ol` bleibt unverändert. In einer
praktischen Übersetzung erscheint jedoch nicht mehr
„Eigenschafts-/Zustands-/Materialträger“, sondern `Grundansatz`; Mengenreihen
werden als Teile/Maße und `ch/sh/k/t`-Reihen als Trocken-, Einweich-, Heiz- und
Kühlstufen formuliert. Strukturdiagnose und deutsche Übersetzung bleiben damit
getrennte Spalten.

## Abdeckung

| Größe | V39 | V40 | Änderung |
|---|---:|---:|---:|
| bekannte Tokenpositionen | 19.312 | 20.417 | +1.105 |
| unbekannte Tokenpositionen | 13.027 | 11.922 | −1.105 |
| vollständige Mehrwortzeilen | 331 | 449 | +118 |
| davon dreileser-streng | 125 | 147 | +22 |
| Ein-Loch-Zeilen | 302 | 333 | +31 netto |
| davon dreileser-streng | 67 | 80 | +13 |
| Glossaroberflächen | 632 | 734 | +102 |
| Wörterbucheinträge | 785 | 976 | +191 |

781/1.105 Zielpositionen sind reader-exakt, die konservative
Split-Normalisierung erreicht 797. Alle 31.234 Nichtzielpositionen bleiben in
Glosse, Quelle und Scope identisch. Der unabhängige source-first Validator
besteht 7.784 Prüfungen samt bytegleichem 19-Dateien-Replay.

## Historische Ähnlichkeit, nicht Identifikation

Ein Rezeptregister, das Fachkürzel, Maße, Stoffnamen und Herstellungsbefehle
mischt, ist für den Zeitraum nicht exotisch. Vergleichbar sind eine englische
Sammlung aus dem ersten Viertel des 15. Jahrhunderts
([Wellcome MS 5262](https://wellcomecollection.org/works/hkxxeu85)), eine
norditalienische lateinische Sammlung aus der Mitte des Jahrhunderts
([Wellcome MS 683](https://wellcomecollection.org/works/w6ne7k4t)) und eine
französische Sammlung medizinischer Wässer
([Wellcome MS 418](https://wellcomecollection.org/works/f6nzyzh4)). Diese
Parallelen stützen nur die Registerform; sie identifizieren kein Voynich-Wort.

## Nächste Front

V40 exponiert 146 neue Ein-Loch-Zeilen mit 140 Restformen und zusammen 1.141
geerbten Vorkommen. Die dichte Spitze lautet `o` 146, `air` 56, `cheky` 55,
`lkaiin` und `opchedy` je 48, `okeol` 44, `chodaiin` 42, `olkeedy` 42,
`olkeey` 35 und `olchedy` 34. GDT664 sollte zuerst nacktes `o` als
reader-sensitive Ansatz-/Verbindungsform behandeln und danach die sichtbaren
II/III- und Zustandsfamilien schließen. Es braucht weiterhin keine neue Seite
oder Bildfreigabe.

## Aussagegrenze

V40 ist die bisher konkreteste Arbeitsübersetzung dieser Seitefront, aber noch
keine Entzifferung. Eine Karte darf stehen bleiben, bis sie klar unmöglich wird
oder eine bessere Karte mehr Formen und Passagen zugleich erklärt. Genau
deshalb sind die riskanten Stoff-/Behälter-/Rückstandskarten offen benannt und
nicht durch bedeutungslose Platzhalter ersetzt.
