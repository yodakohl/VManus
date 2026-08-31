# GDT687 — V60 action/result/boundary dispatch

## Ergebnis

V60 ersetzt die bisherige Mehrdeutigkeit von `dchey`, nacktem `y` und der
gesamten sichtbaren `dy`-Familie durch eine vollständige lokale
Rollenentscheidung. Auf den 51 aktuellen Zeilen liegen 95 Zielpositionen in
40 Zeilen:

| Familie | Positionen | V60-Rollen |
|---|---:|---|
| `dchey` | 14 | 9 Aktionen, 5 fertige Resultate |
| nacktes `y` | 4 | 3 Rechtsbezüge, 1 Zeilenschluss |
| freies `dy` | 3 | 2 Feldgrenzen, 1 Zeilenschluss |
| gebundenes `*dy*` | 74 | 15 Aktionen, 59 fertige Resultate/Zustände |
| **gesamt** | **95** | **24 Aktionen, 64 Resultate, 3 Bezüge, 4 Grenzen** |

Der operative Kern ist einfach: Die ganze geschriebene Form entscheidet über
das Verb. `dy` selbst bedeutet in V60 nur, dass ein Vorgang oder Zustand an
seinem Endpunkt steht. Es kann daher als Resultatadjektiv oder Interpunktion
sichtbar werden, aber nicht selbst *schließen*, *fertigstellen*, *halten* oder
*überführen* erzeugen.

## Die drei konkreten Regeln

### `dchey`

Die vierzehn aktuellen Stellen teilen sich exakt nach Scope. Neun
zeileninitiale Instruktionsstellen erhalten den Arbeitswert:

> eine abgemessene Portion bis zur Mittelstufe trocknen

Fünf mediale oder unmittelbar wertgebundene Stellen erhalten den
Resultatwert:

> fertige abgemessene Mittelstufen-Trockenportion

Mit der f81r-Quellstelle lautet der globale Arbeitszensus 10 Aktionen zu 5
Resultaten. Das ist eine Ganzform- und Scopekarte, kein sicher zerlegtes Wort:
GDT675 verwendet `D+CH+E+Y`, während vier ältere exakte GDT425-Ereignisse
`CH+E+Y` und ausdrücklich `has_close=NO` tragen. V60 behält deshalb die
praktische Lesung, entfernt aber jeden automatisch ergänzten Schluss und lässt
die interne Zerlegung offen.

### Nacktes `y`

Die vier aktuellen Stellen bekommen vier lokale Ausgaben:

- f23r.6#2: `Hierzu:`
- f56r.6#6: `.`
- f80v.35#4: `Hierzu:` (ein ungelöstes Scharnier bleibt der Rival)
- f86v3.13#8: `Hierzu:`

Das globale 270-Positionen-Inventar hat acht Kontextklassen. `y` ist daher
kein Universalwort für „dazu“ und erst recht keine Handlung.

### Freies und gebundenes `dy`

Die drei freien V59-Stellen werden vollständig stumm:

- f26r.2#7: `;`
- f56r.6#2: `;`
- f76v.10#10: `.`

Unter den 74 gebundenen Positionen haben nur fünfzehn eine unabhängige
Ganzwort-Aktion. Die anderen 59 werden als fertige Zustände gelesen, etwa
`fertige mittlere Trockenstufe`, `fertige heiße Endstufe`, `fertig
eingeweichtes Drogenholz` oder `drei fertig abgeteilte Teile`.

Der wichtigste Einzelfall ist f105r.2#13 `qody`. V59 führte die Stelle als
Aktion, doch ihr einziges Verb war das aus `dy` ergänzte *fertigstellen*.
V60 liest nur noch `fertige Zubereitung`. Dadurch sinkt der Gesamtbestand von
86 auf 85 Aktionspositionen.

## Drei sichtbare Reparaturen

`f105r.2` endet nun nicht mehr mit einem erfundenen Befehl:

> … erste Ansatzfraktion abmessen; fertiger Trockenansatz; fertige
> Zubereitung.

`f56r.6` enthält nur noch die einzige geschriebene Handlung und danach einen
Zustandsblock:

> Hieraus einen heiß-trockenen Ansatz bereiten; fertige abgemessene
> Mittelstufen-Trockenportion; heiß am Ende des Grades; Qualitätsgrad III des
> heißen Endzustands.

`f86v3.13` wahrt den Unterschied zwischen zwei Ganzwort-Aktionen und dem
späteren Resultat:

> … Hierzu: fertige mittlere Trockenstufe; einen gleichen Teil
> erhitzen; Trockengut, heiß auf Stufe II.

`f26r.2` verliert zwar den aus freiem `dy` erzeugten Satz „Den Posten
schließen“, enthält aber noch ein geerbtes *abschließen* in `ykecthey`. Das
liegt außerhalb der GDT687-Zielfamilie und ist ausdrücklich der nächste
Rendererfehler, nicht ein gelöstes Detail.

## Was sich messbar verbessert

| Schuldenmaß | V59 | V60 |
|---|---:|---:|
| strikte Kartenpositionen | 120 | 106 |
| mechanisch sichtbare Union | 163 | 152 |
| mechanische Flag-Mitgliedschaften | 177 | 162 |
| breite Spezifität offen | 324 | 285 |
| Vier-Schichten-Union | 370 | 330 |
| ohne aktuelle Schuld/Unsicherheit | 109 | 149 |

V60 versteckt die Restprobleme nicht: 22 der Zielzustände besitzen noch kein
explizites Objekt, eine Zielkarte behält ihre alte niedrige Sicherheit. Der
Validator reproduziert alle vierzehn generierten Ergebnisdateien
byte-identisch und besteht 254 unabhängige Prüfungen.

## Grenze und nächster Hebel

Der 705er GDT557-DY-Zensus ist ein formaler Atomprior, kein Zensus des exakten
Oberflächenworts `dy`. GDT559 trennt Y und DY ebenfalls formal; in allen 28
gemeinsamen Karten steht Y vor DY. Beides stützt die Rollenarchitektur, beweist
aber keinen historischen Wortwert.

V60 ist noch keine vollständige brauchbare Übersetzung: Geerbte praktische
Prosa enthält weiterhin Verben, die nicht sauber einem geschriebenen
Aktionsordinal zugeordnet sind. Der nächste Pass muss deshalb jedes deutsche
Verb auf eine exakte Quellposition zurückbinden. Der bekannte Ausgangspunkt
sind 66 zusätzliche Verb×Zeile-Paare auf 28 Zeilen; jedes Paar wird entweder
einer geschriebenen Ganzwort-Aktion zugewiesen oder in einen Zustand bzw. eine
Nominalgruppe zurückgebaut. Keine neue Seite wird dafür benötigt.
