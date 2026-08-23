# Sidequest: Schliessung der gebundenen Traegerschicht

## Ergebnis

Die mittlere `p`-Schicht ist nicht mehr noetig. Ihre zwanzig Kartentypen und 21
Vorkommen lassen sich mit acht kleinen Werkstattregeln vollstaendig lesen,
ohne die bisherigen deutschen Arbeitsanweisungen zu veraendern.

Die Gesamtarchitektur wird dadurch zweistufig:

```text
151 produktiv gebaute Kartentypen   353 Ereignisse
 22 gelernte Ganzkartentypen         28 Ereignisse
-----------------------------------------------
173 Kartentypen                     381 Ereignisse
```

Von 116 Aussagen sind jetzt 94 vollstaendig zusammengesetzt. Nur die bereits
bekannten 22 Codebuchsaetze enthalten mindestens eine der 22 Ganzkarten.

## Was die acht Regeln sind

Die Traeger sind keine acht gleichartigen Woerter. Sie haben drei verschiedene
Aufgaben.

### Zwei Schreibrahmen

1. `R... / T...` bindet einen bekannten Kern an den lokal aktiven Posten. Der
   Rahmen bekommt kein eigenes Sachwort.
2. `D...D` oder eine lizenzierte exakte `...DY`-Endkarte setzt einen bekannten
   Arbeitsgang als geschlossene Zelle. Das bedeutet weiterhin nicht, dass jedes
   sichtbare `D` oder `DY` allgemein „Ende“ heisst.

Damit werden beispielsweise:

```text
rol       R + OL                 weiterfuehren
ral       R + AL                 zur Zielstelle
tshol     T + HO + L             Zutat entnehmen
rsheal    R + SH + E + AL        kurz am Ziel ruhen
tshey     T + SHEY               Klarlauf
ldy       L + exakte Endkarte    abziehen; Ende
```

### Drei gebundene Klassifikatoren

3. `O` innerhalb `L-O` oder `L-O-CHED` waehlt den Rest- oder Nebenast.
4. `S` nach `L` waehlt den markierten Auslass.
5. `KY` nach `OL` haelt denselben lokalen Arbeitsweg aktiv.

So entstehen kurze technische Unterschiede:

```text
lo        L + O                  den Nebenast abfuehren
lochedy   L + O + CHED + CLOSE   den Rest abfuehren; Schluss
ls        L + S                  markierter Auslass
qolky     OL + KY                auf demselben Arbeitsweg weiterfuehren
```

### Drei wirkliche Fachkerne

6. `DAN = ANWENDEN`
7. `SK = AUSGIESSEN`
8. `T...AM = VERWAHREN`

Sie ergeben die drei besonders klaren Karten:

```text
sotodan   OT + DAN       danach anwenden
skar      SK + AR        von dort ausgiessen
talam     T + AL + AM    am Ziel verwahren
```

`T...AM` wird dabei wie ein kleiner Speicherrahmen behandelt, in dessen Mitte
`AL=ZIEL` eingesetzt wird. Das passt besser zu einer technischen
Werkstattkuerzung als ein unzerlegtes langes Wort TALAM.

## Vier Karten brauchten gar keinen neuen Traeger

Diese vier waren bereits aus dem vorhandenen Kasten lesbar und werden nur
redaktionell von `p` nach `P` verschoben:

```text
otytchol   OT + TY + OL       naechsten Teilposten weiterfuehren
lol        L + OL             von dort weiterfuehren
cheeety    EEE + TY           ganzen Teilposten
sheey      SH + EE + Y        diesen Posten laenger ruhen lassen
```

## Was ein Lehrling jetzt lernen muss

Das Schreibsystem besteht nun nur noch aus zwei praktischen Ebenen:

1. Gebaute Karten: bekannte Bedeutungsbausteine plus die acht kurzen
   Rahmen-/Klassifikatorregeln.
2. Ganzkarten: das bereits abgeschlossene sechzehnkoepfige Codebuch mit 22
   exakten Formen.

Der bisherige Merksatz kann deshalb gekuerzt werden:

> Baue alles, was der Komponenten- und Traegerkasten erlaubt; schlage nur die
> 22 ausdruecklich gelernten Ganzkarten nach.

Es gibt keinen unscharfen Zwischenstatus mehr. Eine Karte ist entweder gebaut
oder absichtlich als Ganzkarte gelernt.

## Beispielpassagen

### f56r, H5-S005

`sotodan` ist jetzt kein lokaler Rest mehr:

```text
OT = danach
DAN = anwenden
OT+DAN = danach anwenden
```

Die Passage liest sich: „Setze den Ansatz als Zutat an, nimm den Auszug daraus
und wende ihn danach an.“

### f83r, B4-S016

```text
dal -> skar -> shedy
Ziel -> SK+AR -> absetzen und schliessen
```

Ruecklesung: „Gib eine weitere Portion dorthin, giesse sie von dort aus, lass
absetzen und schliesse.“

### f82r, B2-S022

```text
lochedy = L + O + CHED + exakter Schluss
```

Ruecklesung: „Fuehre den Rest ab und schliesse.“

## Artefakte

- `BOUND_CARRIER_LEAF.md`: das Lehrblatt der acht Regeln;
- `BOUND_CARRIER_8_LEXICON.tsv`: Rahmen, Klassifikatoren und Fachkerne;
- `PARTIAL_20_CLOSURE.tsv`: alle zwanzig bisherigen `p`-Karten;
- `CLOSED_173_CARD_DICTIONARY.tsv`: zweistufiges Gesamtwoerterbuch;
- `CLOSED_381_EVENT_INTERLINEAR.tsv`: alle Ereignisse als `P` oder `W`;
- `CLOSED_116_PHRASES.tsv` und `CLOSED_11_RECORDS.md`: komplette Lesefassung;
- `CARRIER_8_DRILLS.tsv`: je eine Lehrlingsuebung pro Regel;
- Builder, Validator und Zusammenfassungen.

Die Runde bleibt auf den festen Prosaseiten. Die Astro-Lesung bleibt getrennt;
die versiegelten Seiten wurden nicht benutzt.
