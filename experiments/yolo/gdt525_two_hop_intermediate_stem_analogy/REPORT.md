# GDT525 — Der erste geschlossene K-Zwischenstamm

## Ergebnis

GDT525 verbindet zwei bereits gelernte lokale Änderungen über einen expliziten
Zwischenstamm. Die brauchbare Regel ist eng:

```text
K-Basis + rechtes y -> Y + inneres e -> E
```

Sie ordnet genau drei aktuelle Oberflächen neu und bringt sie auf eine
gemeinsame Schlussstruktur:

| Oberfläche | alter Arbeitsstand | GDT525-Arbeitsrezept |
|---|---|---|
| `kcheody` | `K+CH+E+O+Y` | `K+CH+E+O+D_ADDR+Y` |
| `kechody` | `K+E+CH+O+DY` | `K+E+CH+O+D_ADDR+Y` |
| `keody` | `K+E+O+DY` | `K+E+O+D_ADDR+Y` |

Damit erben alle drei den Schluss des in GDT524 reparierten Zwischenstamms
`kchody=K+CH+O+D_ADDR+Y`. `kcheody` ist eine echte Arbeitskorrektur: GDT515
hatte seine direkte Sichtlesung ausdrücklich nur bis zu einem besseren Parse
beibehalten. Die neue Kette ist dieser bessere Parse.

## Zwei ehrliche Scorekarten

| Deck | Stand | Rang 1 | Top 2 | Top 3 | Top 5 | Rangsumme |
|---|---|---:|---:|---:|---:|---:|
| alter Vierfachlauf | GDT524 | 1.098 | 1.328 | 1.386 | 1.418 | 2.109 |
| alter Vierfachlauf | GDT525 | 1.098 | 1.328 | 1.386 | 1.418 | 2.109 |
| 159 Formen, geerbte GDT516-Ziele | GDT524 | 144 | 154 | 158 | 158 | 185 |
| 159 Formen, geerbte GDT516-Ziele | GDT525 | **145** | 154 | 158 | 158 | **184** |
| 159 Formen, familienkorrigiert | GDT524 | 143 | 153 | 158 | 158 | 187 |
| 159 Formen, familienkorrigiert | GDT525 | **146** | **154** | 158 | 158 | **183** |

Gegen die alte Zielspalte zählen `kechody` und `keody` als Korrekturen und
`kcheody` als Verlust. Gegen die jetzt bessere Arbeitstheorie sind alle drei
Korrekturen. Beide Sichtweisen bleiben in den Artefakten nebeneinander stehen.

## Weshalb nicht alle Zwei-Hop-Ketten gelten

Der erste breite Versuch fand 642 aktuelle Kandidatenketten. Er reparierte nur
`chap`, verlor aber neun vorhandene Treffer; alter Rang 1 fiel 1.098→1.084 und
aktueller Rang 1 144→136. Auch die Beschränkung auf wiederholte geordnete
Paare blieb zu breit. Häufige Einzeländerungen können viele falsche
Übersegmentierungen zusammenbauen.

Die ausgewählte Karte verlangt deshalb eine konkrete wiederholte Reihenfolge,
einen K-beginnenden Basisstamm und zwei fest gerichtete Atomkanäle. Sie erreicht
nur vier Kandidaten auf drei Oberflächen. Alle Gewichte von 0,25 bis 1,25
lassen den gesamten alten Vierfachlauf unverändert; ab 0,85 werden die beiden
noch falschen K-Formen geschlossen, und ab 0,30 erscheint bereits die
`kcheody`-Familienkorrektur.

## Was die Familie nun sagt

Die sichtbaren Varianten sind keine drei isolierten Wörter. Sie bilden ein
kleines Paradigma:

```text
kchod   -> kchody   -> kcheody
          D_ADDR+Y     E + D_ADDR+Y

kod     -> kody     -> keody
          D_ADDR+Y     E + D_ADDR+Y
```

`kechody` benutzt denselben `kchod -> kchody`-Zwischenstamm, setzt das innere
`E` aber an der anderen zulässigen Stelle im Rezept. Der finite Basisscore
entscheidet zwischen diesen beiden E-Positionen; die Kettenkarte entscheidet
nur den gemeinsamen Schluss.

Die Regel wird nicht auf CH- oder SH-beginnende `eody`-Formen ausgedehnt.
GDT521 hatte bereits gezeigt, dass derselbe sichtbare Schluss je nach
vorangehendem Operationspaket sowohl `DY` als auch `D_ADDR+Y` tragen kann.

## Nächster Griff

Nach der Arbeitskorrektur bleiben dreizehn Rang-1-Abweichungen. Die nächsten
besten Gruppen sind:

- `chady` und `chap`: gemeinsamer `ch -> cha`-Adresszwischenstamm, aber kein
  wiederholtes altes Editpaar;
- `cthom` und `dalcheeeky`: echte, jedoch zu schwache Zwei-Hop-Ketten;
- `dsholdaiir`, `aiicthy`, `qef` und `saiis`: kein brauchbarer Zwei-Hop-Weg.

Als Nächstes sollte der `ch -> cha`-Stamm als eigene sichtbare
Adress-/Argumentfamilie geprüft werden. Neue Seiten sind dafür nicht nötig.
