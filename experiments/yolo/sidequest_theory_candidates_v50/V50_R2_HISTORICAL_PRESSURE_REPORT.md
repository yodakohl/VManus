# V50 R2 — Historischer Drucktest der sieben V49-PAGE_HOST-Glossen

Status: begrenzte kreative Werkstattprüfung, **keine Entzifferung** und keine
Behauptung gelesener deutscher Wörter.

## Auftrag, Material und Zählung

Geprüft wurden ausschließlich die sieben aktiven V49-PAGE_HOST-Werte `OK`,
`OT`, `L`, `AL`, `E`, `OR` und `CHEY`. Die Zählung erfolgte nur über exakte
Werte in der Spalte `page_host`, niemals über Teilstrings. Damit umfasst der
Test 21 feste Ganzkarten-Typen und 93 feste Ereignisse:

| Host | V49 | Kartentypen | Ereignisse | Seitenverteilung |
|---|---:|---:|---:|---|
| `OK` | `SETZEN` | 5 | 24 | f55v 2; f81v 4; f82r 9; f83r 9 |
| `OT` | `MARKIEREN` | 3 | 7 | f81v 1; f82r 1; f83r 5 |
| `L` | `VERKNÜPFEN` | 5 | 26 | f10r 3; f55v 1; f81v 11; f82r 2; f83r 9 |
| `AL` | `ZU` | 2 | 11 | f56r 1; f81v 3; f82r 2; f83r 5 |
| `E` | `BIS` | 2 | 14 | f81v 4; f82r 1; f83r 9 |
| `OR` | `ANSATZ` | 2 | 8 | f10r 4; f55v 2; f83r 2 |
| `CHEY` | `ANTEIL` | 2 | 3 | f10r 1; f56r 1; f83r 1 |

Auf f11r und den drei Kreis-Seiten hat keiner dieser sieben Hosts ein festes
Ereignis. Das ist eine Verteilungsgrenze, kein medizinischer Beweis. `f84` und
`f84r` wurden nicht geöffnet; keine weitere Voynich-Seite und keine
Geschwisterdatei aus V50 wurde gelesen.

## Urteil

| Host | R2-Entscheidung | V50-R2-Wert | Geltung | zwei atomare Rivalen |
|---|---|---|---|---|
| `OK` | **BEHALTEN** | `SETZEN` | nur editorischer Formaloperator | `GEBEN`, `STELLEN` |
| `OT` | **ERSETZEN** | `MERKEN` | historischerer Name für den Formaloperator | `ZEICHNEN`, `BEZEICHNEN` |
| `L` | **BEHALTEN** | `VERKNÜPFEN` | nur editorischer Formaloperator | `WEITER`, `FOLGEN` |
| `AL` | **ERSETZEN** | `AN` | schwache Relation, ohne Zielinhalt | `ZU`, `BEI` |
| `E` | **BEHALTEN** | `BIS` | schwacher Grenzoperator, ohne Endzustand | `ENDE`, `SOLANGE` |
| `OR` | **ERSETZEN** | `BEREITUNG` | schwaches neutrales Stoff-/Arbeitsnomen | `MISCHUNG`, `ARZNEI` |
| `CHEY` | **ERSETZEN** | `TEIL` | schwaches Teil-/Mengenwort | `ANTEIL`, `STÜCK` |

Kein Wert erhält ein stilles Gefäß, eine Flüssigkeit, eine Pflanze, eine
Körperstelle, ein Ziel oder einen Endzustand. Insbesondere bedeuten die
Entscheidungen nicht `OK = gib etwas in ein Gefäß`, `E = bis es bereit ist`
oder `CHEY = nimm die Wurzel`.

## Historischer Maßstab

Die paläographische Kontrolle erlaubt kurze Formen, aber nicht beliebig große
Expansionen. Die Universität Zürich unterscheidet für hoch- und
spätmittelalterliche Kürzungen Silbenkürzung, Suspension, Kontraktion und
Sonderzeichen. Sie betont zugleich, dass kein einheitliches System bestand,
dass deutsche Texte weniger stark kürzen und dass einzelne Schreiber häufige
Wörter oder Wortgruppen individuell behandelten; feste Zeichen sind besonders
für Münz-, Maß- und Gewichtseinheiten gewöhnlich. Das lizenziert eine gelernte
Einwort- oder Operator-Sigle, nicht automatisch Handlung plus Objekt plus
Bedingung ([Ad fontes, „Abbreviations“](https://www.adfontes.uzh.ch/en/tutorium/schriften-lesen/abkuerzungen)).

Eine schwäbische Rezeptsammlung von etwa 1463 ist kein Voynich-Paralleltext,
aber ein brauchbarer Größenmaßstab: Sie schreibt kurze Imperative mit ihren
Objekten aus (`Nym`, `tů`, `leg`, `güss`), setzt Fortsetzung ausdrücklich als
`dar nach` oder in einer Überschrift als `Item` und formuliert Grenzen als
`vncz/byss` **mit** folgendem Resultat. Die Edition löst vorhandene
Abbreviaturen ausdrücklich auf. Daraus folgt nicht, dass jede Handschrift so
aussehen muss; es zeigt aber, wie viel unzulässige Prosa in einer angeblich
atomaren Glosse stecken würde ([HAB, Cod. germ. 1, Ha1-I](https://diglib.hab.de/edoc/ed000270/texts/tei-transcription.html)).

Für medizinische Rezeptsammlungen ist dieselbe Vorsicht nötig. Die im
15. Jahrhundert entstandene *Lylye of Medicynes* kennzeichnet 360 Rezepte mit
`Rx`; der normale Ablauf nennt Arzneiform/Indikation, Zutaten und oft Mengen,
danach Zubereitungsschritte. Fachkundige Leser durften Details ergänzen, doch
solche pragmatische Auslassung beweist nicht, dass ein kurzes Zeichen alle
ergänzten Details lexikalisch enthielt
([Connelly et al., *mBio* 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7018648/)).

## Widerspruchsledger nach Host

### `OK`: `SETZEN` bleibt nur als Formaloperator

Die 24 Ereignisse teilen sich in fünf feste Typen: neunmal „beginne den
nächsten abgemessenen Posten“, siebenmal „gib einen abgemessenen Anteil in das
Gefäß“, sechsmal „mische beide Anteile“, einmal eine bloße Ortsangabe und
einmal „öffne den oberen Lauf“. Kein historisches Rezeptverb *setzen* kann all
diese lokalen Sätze wörtlich tragen. Die V49-Formeln sind jedoch in allen fünf
Typen einheitlich `SET(<ARG_...>)`. Deshalb bleibt `SETZEN` als deutscher Name
dieser **editorischen** Operation, nicht als expandierte Quellform.

`GEBEN` passt am ehesten zu sieben Ereignissen, scheitert aber an Beginn,
Mischen, Öffnen und Ortsangabe. `STELLEN` ist historisch als Platzierungsverb
kleiner als die V49-Satzexpansion, deckt aber dieselben Abweichungen nicht.

### `OT`: `MARKIEREN` wird zu `MERKEN`

Die sieben Ereignisse verteilen sich auf drei Bezugsarten: dreimal dieselbe
Dauer, dreimal Richtung zum unteren Ablauf, einmal dessen anschließende
Benutzung. Der gemeinsame Nenner ist daher kein medizinischer Gegenstand,
sondern nur die formale Kennzeichnung eines anonymen Arguments. `MARKIEREN` ist
als modernes Metawort verständlich, aber historisch unnötig fern.

Das Frühneuhochdeutsche Wörterbuch belegt `merken` im Sinn von „mit einem
Merkzeichen versehen“, darunter Maß, Gefäß und Handlung; Belege stehen schon
für 1412 und 1420. Es belegt außerdem die schriftliche Bedeutung
„fixieren/aufzeichnen“. Darum ist `MERKEN` der kleinere historische
Operatorname. Er heißt hier nicht „sich erinnern“ und enthält weder Dauer noch
Ablauf ([FWB, „merken II“](https://fwb-online.de/lemma/merken.rII.3v)).

`ZEICHNEN` und `BEZEICHNEN` bleiben möglich, legen aber stärker ein sichtbares
Zeichen oder einen benannten Gegenstand nahe, den die V49-Daten nicht liefern.

### `L`: `VERKNÜPFEN` bleibt nur als Formaloperator

Neunzehn von 26 Ereignissen expandiert V49 als Fortsetzung mit der vorigen
Zubereitung. Die restlichen sieben sind zweimal „das bereitete Öl“, zweimal
Kochen-plus-Abschluss, zweimal Ablassen-plus-Abschluss und einmal Schließen des
unteren Ablaufs. Damit wäre `WEITER` eine attraktive Mehrheitsglosse, aber kein
Allvorkommenswert. `FOLGEN` hat dasselbe Problem. Die fünf Formeln teilen
dagegen den abstrakten Kern `LINK`, teils mit Rahmen, Argument oder Abschluss.

`VERKNÜPFEN` bleibt deshalb als formaler Analyseoperator. Als angebliches
historisches Rezeptwort wäre es zurückzuweisen: die normale Rezeptfortsetzung
arbeitet eher mit `und`, `dar nach`, `Item` oder einer expliziten Wiederaufnahme,
nicht mit einem Verb, das zugleich Öl, Kochen, Ablassen und Schließen bedeuten
soll.

### `AL`: `ZU` wird zu `AN`

Zehn Ereignisse lauten lokal „an die bezeichnete Zielstelle“; das elfte lautet
„an der zweiten Öffnung“ und trägt zusätzlich `CLOSE`. `ZU` ist nur allativ und
passt zur elften, lokativen Verwendung schlechter. `AN` ist der kleinere
gemeinsame Relationswert, weil es Richtung und Lage zulässt. Es enthält **kein**
Ziel, keine Öffnung und kein Führen. Diese Größen müssen außerhalb des Atoms
bleiben.

`BEI` würde die eine Lage, aber die zehn Richtungsfälle schlechter abbilden;
`ZU` bleibt der direkte Rivale. Die Evidenz bleibt schwach, weil die lokalen
Expansionen selbst kreativ und kein unabhängiger Paralleltext sind.

### `E`: `BIS` bleibt

Zwölf Ereignisse expandieren als Warten bis zur Bereitschaft, zwei als Ziehen
bis zur Klarheit; alle 14 tragen formal `CLOSE`, zweimal zusätzlich `FRAME_OT`.
Der einzige atomare gemeinsame Textwert ist die terminative Relation `BIS`.
Historische Rezepte verwenden genau solche `vncz/byss`-Konstruktionen, nennen
den Resultatszustand aber außerhalb der Konjunktion. Deshalb enthält `BIS` hier
weder `BEREIT` noch `KLAR`, auch nicht `STEHEN` oder `BEENDEN`.

`ENDE` verdoppelte den schon vorhandenen `CLOSE`-Rahmen und machte aus einer
Relation ein Nomen. `SOLANGE` bezeichnet Dauer, nicht das erreichte Ende.

### `OR`: `ANSATZ` wird zu `BEREITUNG`

Sieben der acht Ereignisse nennen lokal die bereitete Arbeitsflüssigkeit; das
achte fordert den frischen Gebrauch der fertigen Flüssigkeit. Der gemeinsame
Kern ist also etwas Bereitetes, nicht notwendig eine Flüssigkeit, Arznei oder
Mischung. `ANSATZ` ist dafür historisch besonders riskant: Das FWB führt für
`ansaz` unter anderem Unrat, gerichtliche Einweisung, Verfügung, Festlegung und
Angriff, aber keinen pharmazeutischen Batch
([FWB, „ansaz“](https://www.fwb-online.de/lemma/ansaz.s.0m)).

`BEREITUNG` ist dagegen bereits für Zu-/Vorbereitung und Herrichtung eines
Stoffes oder einer Materie belegt. Es bleibt absichtlich ein schwaches,
neutrales Arbeitsnomen; der flüssige Zustand ist nicht Teil des Worts
([FWB, „Bereitung“](https://www.fwb-online.de/lemma/bereitung.h1.1f)).
`MISCHUNG` würde mehrere Bestandteile voraussetzen, `ARZNEI` den medizinischen
Gebrauch und damit eine noch unbewiesene Gattung.

### `CHEY`: `ANTEIL` wird zu `TEIL`

Ein Ereignis expandiert als faserige untere Wurzel, zwei als bezeichneter
Anteil. `ANTEIL` zieht die Lesung zur abstrakten Quote; `TEIL` kann dagegen
einen konkreten Pflanzenteil und eine abgemessene Teilmenge bezeichnen, ohne
Wurzel, Faser, Lage oder Nehmen einzubauen. Besonders passend für die
historische Größenordnung ist ein chirurgisches Rezept von 1446/48 mit
`nym ein teÿl ...`; das FWB führt sowohl den Teil eines Ganzen als auch den
Anteilssinn
([FWB, „teil“](https://www.fwb-online.de/lemma/teil.s.0mn)).

`STÜCK` würde eine abgegrenzte feste Einheit nahelegen. `ANTEIL` bleibt für
die zwei Mengenfälle brauchbar, ist aber für den konkreten Pflanzenteil enger
und abstrakter als nötig.

## Eng begrenzte Pseudoübersetzung

Unter R2-Druck darf das siebenstellige Arbeitslexikon nur so gelesen werden:

```text
OK    SETZEN       [formalen Eintrag setzen; Argument extern]
OT    MERKEN       [formalen Bezug kennzeichnen; Argument extern]
L     VERKNÜPFEN   [formal anschließen; Anschlussinhalt extern]
AL    AN           [Relation; Ziel/Lage unbekannt]
E     BIS          [Grenze; Resultat unbekannt]
OR    BEREITUNG    [bereitetes Arbeitsgut?; Stoff und Gebrauch unbekannt]
CHEY  TEIL         [Teil/Teilmenge?; Gegenstand und Handlung unbekannt]
```

Die drei Großbuchstaben-Operatoren sind moderne Analyseetiketten. Die vier
anderen Werte bleiben schwache Werkstattglossen. Keine davon ist ein
bestätigtes Lexem, und keine lokale V49-Satzexpansion darf zurück in das eine
Wort gepackt werden.
