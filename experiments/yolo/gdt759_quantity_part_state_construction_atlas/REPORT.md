# GDT759 — aus Einzelwörtern werden erstmals belastbare Mini-Ausdrücke

## Ergebnis

Der Pass findet 122 reader-exakte Zweiwortspans aus dem vorab festgelegten
Konstruktionsdeck. Sie zerfallen in 96 Mengen-, 23 Pflanzenteil/Zustands- und
drei Zubereitungs/Wert-Ausdrücke. Siebzehn der 26 möglichen gerichteten Paare
sind wirklich belegt. Nur diese siebzehn erhalten eine Ausdruckslesung.

Die wichtigste Korrektur lautet:

```text
s aiin = saiin
Arbeitslesung: drei Drachmen
Rivalen: drei gleiche Teile | drei Unzen
```

Das ist nicht aus der EVA-Form geraten. Vier verschiedene physische Zeilen
werden über ZL3b, IT2a und RF1b vollständig identisch, sobald lediglich die
Grenze `s aiin`/`saiin` normalisiert wird. Insgesamt gibt es 23 getrennte
reader-exakte `s aiin` und 89 fusionierte `saiin`.

## Die alte Samenfamilie fällt

GDT758 hatte `s=Samen` bereits entfernt. GDT759 zieht die notwendige Konsequenz
für die fusionierten Formen:

| Form | fusionierte Vorkommen | getrennte Vorkommen | neuer Default | Konfidenz |
|---|---:|---:|---|---|
| `san` | 2 | 0 | eine Drachme | C0 |
| `sain` | 53 | 1 | zwei Drachmen | C1 |
| `saiin` | 89 | 23 | drei Drachmen | C1 |
| `saiiin` | 1 | 1 | vier Drachmen | C0 |

Damit verlassen `ein Teil Saatgut`, `Samen, Charge II`, `Samencharge III` und
`Saatgutcharge IV` die aktive Arbeitslesung. Ihre einzige konkrete
Stoffidentität stammte aus dem bereits verworfenen EVA-Initial-Mnemonic.

Warum Drachmen als Leitkandidat? Die historische Vergleichsbank belegt genau
die benötigte technische Architektur: Drachmen- und Unzenzeichen stehen mit
Werten; *ana* drückt gleiche Mengen aus. Der Drachmenmarker ist in der
abgeglichenen Rezeptüberlieferung die häufigste konsequent gekürzte
Maßformel. Das wählt eine praktische Arbeitshypothese, nicht die historische
Identität. Deshalb bleiben `drei gleiche Teile` und `drei Unzen` sichtbar.

## `s` ist kontextabhängig, nicht ein magisches Universalwort

Alle 154 exakten `s`-Vorkommen haben nun einen Dispatch:

| Kontext | Vorkommen | Default |
|---|---:|---|
| vor `ain/aiin/aiiin` | 25 | zwei/drei/vier Drachmen |
| exaktes `s om` | 1 | je eine Handvoll |
| zeilenfinal | 34 | zu gleichen Teilen |
| andere Kontexte | 94 | je, C0-Fallback; Maß-/Anteilszeichen bleibt Rivale |

So bleibt die konkrete `ana`-artige Lesung dort erhalten, wo sie wirklich
nützlich ist, ohne den starken Einheit-plus-Wert-Rahmen zu überschreiben.

## Die drei Mengenköpfe unterscheiden sich

| Kopf | exakte Wertpaare | beobachtete Werte | Arbeitsfunktion |
|---|---:|---|---|
| `s` | 25 | II, III, IV | Drachmen-/Maßformel; gleich-Teile-Rivale |
| `or` | 44 | II, III, IV | Portionen |
| `ar` | 27 | II, III, IV | Anteile |

Die konkreten Hauptausdrücke sind `or aiin=drei Portionen` (36-mal) und
`ar aiin=drei Anteile` (16-mal). Neben den vier `s aiin/saiin`-Brücken gibt
es je eine vollständig normalisierte Brücke für `or ain/orain`,
`or aiin/oraiin` und `ar aiin/araiin`. Leerzeichen trennen hier also nicht
zuverlässig Wort von Kompositum.

Beispielausschnitte:

```text
f16r.7   ... schy s aiin doal ...
          ... schy; drei Drachmen; doal ...

f76r.47  ... chckhy or aiin sheey ...
          ... chckhy; drei Portionen; sheey ...

f113v.2  ... ar al ar aiin okal ...
          ... Anteil; al; drei Anteile; okal ...
```

Ungeklärte Nachbarformen bleiben EVA; sie werden nicht mit „Arbeitsgut“ oder
ähnlichem Fülltext verdeckt.

## Pflanzenteil plus Zustand funktioniert in beiden Richtungen

Die 23 direkten Kontakte ergeben ein kleines, wiederverwendbares System:

| Ausdrucksfamilie | beide Richtungen | Arbeitslesung |
|---|---:|---|
| `chor` ↔ `chol` | 15 | getrockneter Blüten-/Samenstand |
| `cthy` ↔ `chol` | 6 | getrocknetes Blattgut |
| `chor` ↔ `qokchol` | 2 | erhitzter und getrockneter Blüten-/Samenstand |
| `chor/cthy` ↔ `sheol` | 0 | keine direkte Ausdruckslizenz |

Die flexible Reihenfolge ist praktisch wichtig: `chol` funktioniert wie eine
Zustandszelle, die vor oder nach dem sichtbaren Pflanzenteil stehen kann. Die
stärkste vollständige Klausel bleibt:

```text
chor chol daiin
Blüten-/Samenstand: trocken, dritter Grad
```

Sie steht reader-exakt an f21r.12 und f32v.10. `Blüten-/Samenstand` bleibt der
C1-Leitkandidat; das sicherere `Pflanzenteil` bleibt der erste Rivale.

## `odol` und `ols`

`odol=abgemessene Zubereitung` bleibt C1. Seine zwei Herbal-Vorkommen passen
zu einem Zubereitungskopf, liefern aber kein reader-exaktes `odol + Wert`-Paar.

`ols` steht dreimal direkt vor einem geordneten Wert, obwohl es nur fünf
exakte rechte Kontexte besitzt; zugleich steht es in fünf von zwölf Fällen am
Zeilenende. Das spricht gegen den bloßen Imperativ `seihe ab` und gegen das zu
enge Nomen `Endprodukt`. Der neue Default lautet deshalb:

```text
ols = abgeseihte Zubereitung (C0)
ols aiin = drei Portionen abgeseihte Zubereitung
ols aiiin = vier Portionen abgeseihte Zubereitung
```

`Öl/ölige Zubereitung` bleibt ein ernsthafter Rivale, wird aber nicht allein
wegen der EVA-Schreibgestalt bevorzugt. Die revidierte `ychor`-Zeile lautet:

```text
f99r.52  ychor ols or agairom
ferner/ebenso: abgeseihte Zubereitung; eine Portion;
eine Handvoll, dritter Anteil
```

## Was sich tatsächlich verbessert hat

Wir haben jetzt nicht nur Einzelglossen, sondern siebzehn beobachtete
Ausdruckstypen mit 122 konkreten Stellen. Die bedeutendste Altlast – die aus
`s=Samen` abgeleitete Samencharge-Reihe – ist ausgeräumt. Gleichzeitig sagt
der Pass offen, wo Komposition noch nicht funktioniert: Es gibt kein einziges
direktes `sheol`-Pflanzenteilpaar und daher noch keine globale Lesung
„eingeweichtes Blatt“.

Bestätigte Lexeme, Einheiten und Klartextsätze bleiben null. Die neue
Drachmenlesung ist bewusst konkret und angreifbar; eine bessere Erklärung kann
sie ersetzen.

## Nächster Schritt

Der nächste Pass soll von den Mengenformeln nach links gehen: Welche
wiederkehrenden Ganzwörter besetzen unmittelbar vor `s/or/ar + Wert` den
Zutaten- oder Zubereitungsslot? Dort suchen wir gezielt nach stabilen
Kandidaten für Wasser, Wein, Öl, Salz, Pulver und konkrete Pflanzenteile. Die
Mengenformel liefert dabei den Satzanker; die Stoffidentität darf nicht wieder
aus einem EVA-Anfangsbuchstaben stammen.
