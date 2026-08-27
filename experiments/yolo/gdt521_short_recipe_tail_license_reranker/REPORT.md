# GDT521 — Der Komponentenschwanz entscheidet die gleiche Endung

## Ergebnis

Die sichtbare Fuge allein war bei `...eody` am Ende: `shckheody` braucht
`O+DY`, `psheody` aber `O+D_ADDR+Y`. GDT521 ergänzt deshalb keine neue
Zeichenregel, sondern fragt nach höchstens vier vorhergehenden Komponenten.

Der ausgewählte Fünferkontext wird aus 1.558 alten Formtypen gelernt. Er
enthält 1.993 verschiedene Verläufe und 3.284 beobachtete Übergänge. Jede alte
Oberfläche zählt einmal, damit häufig wiederholte Karten die Kompositionsregel
nicht allein bestimmen.

## Gesamtwirkung

| Deck | Modell | Rang 1 | Top 2 | Top 3 | Top 5 | Rangsumme | tiefster Rang |
|---|---|---:|---:|---:|---:|---:|---:|
| vier rotierende Altgruppen | GDT520 | 1.089 | 1.321 | 1.381 | 1.416 | 2.139 | 22 |
| vier rotierende Altgruppen | GDT521 | **1.090** | **1.325** | **1.387** | **1.418** | **2.118** | 22 |
| aktuelle 159 Formen | GDT520 | 139 | 154 | 158 | 158 | 190 | 9 |
| aktuelle 159 Formen | GDT521 | **140** | 154 | 158 | 158 | **189** | 9 |

Der Rang-1-Gewinn ist klein, aber die ganze Rangordnung wird sauberer: im
alten Vierfachlauf sinkt die Rangsumme um 21 und sechs weitere Ziele erreichen
die ersten drei Plätze.

## Der konkrete Gewinn

`psheody` wird wieder als

`P + SH + E + O + D_ADDR + Y`

gewählt, während `shckheody` bei

`SH + CH + K + E + O + DY`

bleibt. Das Modell speichert weder `psheody` noch `shckheody` als Ganzwort. Es
kennt nur kurze Komponentenfolgen. Damit kann dieselbe sichtbare Endung zwei
Schreibweisen tragen, deren Auswahl aus dem vorhergehenden Arbeitsgang kommt.

Die alten Endfamilien bestätigen, dass beide Varianten wirklich zum
Arbeitscodebuch gehören:

- `O+DY`: 30 Oberflächentypen / 45 Ereignisse;
- `O+D_ADDR+Y`: 17 / 37;
- `O+Y`: 20 / 36;
- terminal `OL`: 107 / 420;
- terminal `O+L`: 6 / 35.

## Was noch nicht gelöst ist

`dyky` wechselt von der falschen Lesung `DY+K+Y` zur ebenfalls falschen
Lesung `Y+K+Y`; richtig wäre `D_ADDR+Y+K+Y`. Das zeigt, dass der kurze
Kompositionsprior eine Kandidatenfamilie ordnen kann, aber ein sichtbar
verschlucktes oder zusätzliches Adresszeichen nicht immer identifiziert.

Noch wichtiger: Die exakten alten Schwanzfolgen `D_ADDR+IIN+R` versus
`D_ADDR+AIIN+R` und `S+IIN+S` versus `S+A_ADDR+IIN+S` kommen in dieser Form
gar nicht vor. Die offenen `dsholdaiir`- und `saiis`-Fälle dürfen deshalb nicht
durch erfundene alte Häufigkeiten entschieden werden.

Der nächste Arbeitsgriff ist eine analoge Familienkarte: Für jede der 19
Restformen suchen wir alte Karten, die genau eine lokale Einfügung, Löschung
oder Zusammenziehung im sichtbaren Stamm und im Komponentenrezept teilen.
Das Ziel sind wiederkehrende Transformationskarten, keine 19 Vollform-Ausnahmen.

Bekannte Ereignis- und Oberflächenkarten behalten stets Vorrang. Der kurze
Komponentenkontext ist eine Arbeitsgrammatik, kein bestätigter Satzbau.
