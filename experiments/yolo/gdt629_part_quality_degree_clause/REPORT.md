# GDT629 report — die kleinste konkrete `chor`-Klausel

## Ergebnis

Die derzeit beste kleinste Arbeitsübersetzung ist:

```text
chor | chol | daiin
Pflanzen-/Reproduktionsteil | trocken | Grad III

Pflanzen-/Reproduktionsteil: trocken, Grad III.
```

Sie ist kein geglätteter Platzhaltertext. Jeder der drei sichtbaren Slots hat
eine konkrete Funktion, und die gleiche Oberfläche steht an zwei verschiedenen
Manuskriptstellen in allen drei alternativen Lesungen:

| Locus | ZL3b | IT2a | RF1b |
|---|---|---|---|
| f21r.12 | `chor chol daiin` | `chor chol daiin` | `chor chol daiin` |
| f32v.10 | `chor chol daiin` | `chor chol daiin` | `chor chol daiin` |

Das macht `chor | chol | daiin` zur ersten mehrfach replizierten
Part–Qualität–Grad-Klausel der aktuellen Arbeitslesung. Es beweist nicht die
historische Sprache oder Aussprache, aber es kann nun weitere Vorkommen
kompositionell vorhersagen.

## Fusion und Trennung sind hier dieselbe Phrase

An zwei weiteren physischen Spans lesen ZL3b und RF1b eine fusionierte Form,
IT2a dagegen dieselben Zeichen mit einer Wortgrenze:

| Locus | ZL3b | IT2a | RF1b | Normalisierung |
|---|---|---|---|---|
| f49r.6 | `choldaiin` | `chol daiin` | `choldaiin` | `ch+ol+d+a+III` |
| f100r.22 | `choldaiin` | `chol daiin` | `choldaiin` | `ch+ol+d+a+III` |

Hier ist die Gleichheit stärker als eine bloße Ähnlichkeit zweier
Wörter: Es ist derselbe Manuskriptspan, und nur die transkribierte Leerstelle
wechselt. Für diesen Ausdruck gelten daher:

```text
choldaiin  = chol daiin = trocken, Grad III
```

Das erklärt zugleich, warum Leerzeichen im Manuskript keine verlässliche
Grenze für technische Komposition sind. Es erlaubt noch nicht, jedes beliebige
`d` mit seinem linken Nachbarn zu fusionieren.

## f27r.6 ist eine echte Leservariante

Der dritte Partlocus darf nicht in dasselbe Spacing-Muster gepresst werden:

```text
ZL3b  chor cholaiin
IT2a  chor chol chaiin
RF1b  chor cholchaiin
```

Alle drei Fassungen besitzen unmittelbar vor dem Trocken-III-Ausdruck
`chor`, aber IT2a/RF1b tragen gegenüber ZL3b ein zusätzliches `ch`. Die
Arbeitssemantik bleibt „Pflanzenteil: trocken III“; nur ZL3b belegt jedoch die
direkte Form `chor cholaiin`. Die anderen beiden Fassungen lesen eher
„trockenes Gut: trocken III“. GDT629 wertet f27 deshalb als semantische
Leservariante, nicht als dritten exakten Oberflächenbeleg.

## Was fusionierte Formen noch nicht sagen

Die dreifach exakte fusionierte Phrase f17v.8 ist `choldaiin`. Dazu kommen die
beiden Grenzvarianten f49r.6 und f100r.22. An keiner dieser drei Stellen steht
unmittelbar davor ein bereits identifizierter Partanker. Die zulässige Lesung
ist deshalb nur:

```text
choldaiin = trocken, Grad III; äußerer Träger offen
```

Nicht zulässig ist, aus der Fusion allein ein unsichtbares `chor` oder einen
beliebigen Stoff zu erfinden.

## Der Dosisrival bleibt real

Spätmittelalterliche Rezepte können auf einen Bestandteil eine Einheit und
eine Kardinalzahl folgen lassen. Daher bleibt für die getrennte Form:

```text
chor | chol | daiin
Pflanzenteil / Trockenmaterial | drei Portionen
```

als lokale Gegenlesung offen. Die Gradlesung ist derzeit besser, weil sie
gleichzeitig erklärt:

- die direkte Form `cholaiin`,
- die fusionierte Form `choldaiin`,
- die getrennte Form `chol daiin`,
- das fast vollständige heiß/kalt/trocken/feucht-OL-Gitter,
- und die komplette I–IV-Reihe nach `chol`.

Eine Dosisanalyse müsste dagegen in den direkten Formen eine wechselnde oder
unausgedrückte Einheit annehmen. Sie wird nicht verworfen, aber für diese
OL-Familie auf Rang zwei gesetzt.

## Historische Passform

Der engste zeitnahe Vergleich in GDT627 ist Wellcome MS 542, frühes
15. Jahrhundert: Ein Wurzel-/Drogenteil wird als heiß und trocken im dritten
Grad beschrieben. Ein weiterer Eintrag setzt einen Arzneistoff vor eine
gekoppelte Heiß-/Trockenqualität und einen gemeinsamen Grad. Pal.lat.1234 um
1400 besitzt eine vollständige I–IV-Wärmegradachse. Wellcome MS 492 liefert
die konkurrierende Ingredienz–Einheit–Zahl-Syntax.

Damit ist `PART → QUALITY → DEGREE` fachlich und zeitlich eine sparsame
Passform; die historischen Texte bestimmen aber keine Voynich-Oberfläche.

## Gesamtkontext statt ausgesuchter Beispiele

Alle 43 bereits in GDT628 registrierten `chol`-Wertausdrücke wurden erneut
eingeteilt:

| Kontextrolle | Zahl |
|---|---:|
| vollständige Part–Qualität–Grad-Klausel | 3 |
| Qualitätsphrase mit nahem Partanker | 7 |
| Qualitätsphrase, äußerer Träger offen | 33 |

35 der 43 Ausdrücke sind als vollständiger Ausdruck in allen drei Lesungen
stabil. Die drei vollständigen Klauselkontexte sind f21r.12, f27r.6 und
f32v.10; nur f21 und f32 sind oberflächlich dreifach exakt.

## Keine neue Pseudoübersetzung der Restzeilen

Die acht Zielzeilen enthalten in ZL3b 65 Tokens. Dreißig erhalten durch die
geerbten oder hier verdichteten Regeln eine konkrete Rolle; 35 bleiben
`OPEN`. Kein Token fehlt in der Tabelle, aber ein offener Token bekommt nicht
mehr den inhaltslosen Ersatz „Arbeitsgut“, „halte“ oder „führe aus“.

Beispiel f32v.10:

```text
sho keol | chor chol daiin | cpho l cthol da ar
OPEN OPEN | Pflanzenteil: trocken, Grad III | OPEN OPEN OPEN OPEN OPEN
```

Die praktische Information sitzt exakt in der mittleren Klammer. Die beiden
Reste werden nicht so formuliert, als seien sie bereits verstanden.

## Wörterbuch V6

V6 enthält die 28 V5-Einträge unverändert und vier neue Einträge:

| Ausdruck | Default |
|---|---|
| `chor chol daiin` | Pflanzenteil: trocken, Grad III |
| `chor cholaiin` | dieselbe Klausel, aber direkt nur in ZL3b |
| `choldaiin \| chol daiin` | fusionierte/getrennte Grenze derselben Trocken-III-Phrase |
| `cholchaiin \| chol chaiin` | reduplizierte Trocken-III-Leservariante |

Damit bleiben Stamm (`ch`), Träger (`ol`), freier Wertkopf (`d`), Linker
(`a`) und Wert (`III`) in allen drei Schreibwegen gleichartig interpretierbar.

## Nächster bedeutungsentscheidender Schritt

Die offene Frage ist nun nicht mehr, ob fusionierte und getrennte Trocken-III-
Formen zusammengehören. Das ist an zwei identischen Manuskriptspans gezeigt.
Als Nächstes muss der äußere Träger der 15 fusionierten `OL+dN`-Vorkommen
gegen die 120 getrennten `OL dN`-Vorkommen verfolgt werden. Gesucht wird eine
sichtbare wiederkehrende Part-/Stoffanbindung, die auch außerhalb von `chor`
konkrete Substantive liefert; es werden dafür zunächst keine neue Seite und
kein neues Bild geöffnet.

## Grenze

GDT629 ist keine Gesamtentschlüsselung. Es ersetzt aber einen generischen
Platzhalter durch eine mehrfach belegte, kompositionelle Arbeitsklausel und
zeigt genau, welcher Teil konkret ist, welche Oberflächengrenze variabel ist
und wo die Dosis-Gegenlesung noch lebt.
