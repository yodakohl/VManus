# GDT527 — Der Stamm braucht ein Zertifikat, und `ol` bleibt meist ganz

## Ergebnis

Die Verallgemeinerung von GDT526 gelingt, aber nicht als freie Endungsregel.
Ein altes Ganzstück darf nur dann produktiver Stamm sein, wenn sein Rezept
mindestens drei alte Oberflächen besitzt oder wenn der Stamm bereits einen
anderen einbuchstabigen rechten Ausbau trägt.

Mit diesem Zertifikat schließt der transparente Schluss `s→S`:

```text
okedal = OK+AL
okedals = OK+AL+S
```

`OK+AL` besitzt fünf alte Oberflächenträger: `chokal`, `chykald`,
`okal`, `okedal` und `qokal`. Der Schluss `s→S` hat 20/23 alte
Träger. `okedals` springt damit von Rang 3 auf Rang 1. Die zweite aktivierte
Route `ral→rals` war schon Rang 1 und bleibt dort.

## Scorekarten

| Deck | Stand | Rang 1 | Top 2 | Top 3 | Top 5 | Rangsumme |
|---|---|---:|---:|---:|---:|---:|
| alter Vierfachlauf | GDT526 | 1.098 | 1.328 | 1.386 | 1.418 | 2.109 |
| alter Vierfachlauf | GDT527 | 1.098 | 1.328 | 1.386 | 1.418 | 2.109 |
| 159 geerbte Ziele | GDT526 | 147 | 155 | 158 | 158 | 181 |
| 159 geerbte Ziele | GDT527 | **148** | **156** | 158 | 158 | **179** |
| K- und `keeol`-revidiert | GDT526 | 149 | 155 | 158 | 158 | 179 |
| K- und `keeol`-revidiert | GDT527 | **150** | **156** | 158 | 158 | **177** |

147 richtige Entscheidungen bleiben erhalten, eine wird korrigiert, elf
geerbte Fehler bleiben. Es gibt keinen Verlust. Die komplette alte Scorekarte
bleibt exakt gleich.

## Warum `keeol` nicht `keeo+l` ist

Der zunächst verlockende Parallelweg wäre:

```text
keeo = K+EE+O
keeol = K+EE+O+L
```

Er ist als lokale Möglichkeit nicht absurd: `l→L` hat 12/12 Unterstützung,
und `keeo` besitzt mit `keeod` ein altes rechtes Schwesterstück. Aber der
vollständige alte `ol`-Bestand entscheidet anders:

| alter sichtbarer Schluss `ol` | Typen |
|---|---:|
| Rezept endet in atomarem `OL` | **103** |
| Rezept endet in `O+L` | 6 |
| anderes Ende | 3 |

Bei genügend Gewicht zerlegt die produktive L-Regel konkret `alol`,
`cphol`, `okeol`, `qokeeol` und `shol` falsch in `...O+L`.
Rang 1 im alten Vierfachlauf fällt bei Gewicht 2,5 von 1.098 auf 1.093.

Der bessere aktuelle Default ist deshalb:

```text
keeol = K+EE+OL
```

Das ist zugleich schon die GDT526-Rang-1-Lesung. Die alte
`K+EE+O+L`-Annahme wird nicht verteidigt, wenn ein deutlich besseres
Ganzkartenmuster vorhanden ist.

## Was die Werkstattlesung ungefähr sagt

Unter den weiterhin nur provisorischen deutschen Kernwerten:

- `okedals = OK+AL+S` → „setzen – am Zielort wählen“;
- `keeol = K+EE+OL` → „geben, Grad II – fortsetzen“.

Diese Phrasen sind Arbeitsparaphrasen der strukturellen Rezepte, keine
entzifferten Sätze.

## Architektur nach GDT527

Das gemischte Codebuchmodell wird präziser:

1. kurze technische Atome können produktiv kombiniert werden;
2. ganze Formen können eine atomare Karte besitzen, die eine scheinbare
   Buchstabenzerlegung überstimmt;
3. ein gelerntes Ganzstück wird erst mit zusätzlicher Paradigma- oder
   Mehrfachträger-Evidenz zum produktiven Stamm;
4. selbst dann bleibt jeder Schlusskanal einzeln beschränkt: `s→S` trägt,
   freies `l→L` nicht.

## Nächster Griff

Neun Rang-1-Abweichungen bleiben:

```text
aiicthy  chekchy  cthom  dairykodas  dalcheeeky
dsholdaiir  qef  qocthedy  saiis
```

Der klarste nächste Kandidat ist `qocthedy`: Sein Arbeitsrezept ist exakt
dasselbe wie beim alten `qocthey`; nur sichtbares inneres `d` kommt hinzu.
Als Nächstes sollte daher eine zertifizierte rezepttreue Null-Einfügung geprüft
werden. Sie darf weder das breite `q→NULL` wiederbeleben noch beliebige
`d`-Zeichen verschlucken. Neue Seiten sind nicht nötig.
