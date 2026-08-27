# GDT526 — `cha` funktioniert als gelernter Zwischenstamm

## Ergebnis

Der direkte nächste Ansatz funktioniert überraschend sauber. Die alte Karte

```text
cha = CH+A_ADDR
```

kann als ganzer gelernter Stamm weitergebaut werden. Ein neuer rechter Schluss
darf angehängt werden, wenn genau dieser sichtbare Schluss bereits anderswo
einen positiven Atomkanal besitzt. Damit werden zwei aktuelle Formen ohne
eigene Ganzwort-Ausnahme richtig geordnet:

| Oberfläche | GDT525 Rang 1 | GDT526 Rang 1 | Route |
|---|---|---|---|
| `chady` | `CH+DY` | `CH+A_ADDR+DY` | `cha` + `dy→DY` |
| `chap` | `CH+P` | `CH+A_ADDR+P` | `cha` + `p→P` |

Die eigentliche neue Information lautet also nicht „`chady` bedeutet X“.
Sie lautet: Ein im alten Material als Ganzes gelernter Stamm kann produktiv
einen separat bekannten Schluss tragen.

## Scorekarten

| Deck | Stand | Rang 1 | Top 2 | Top 3 | Top 5 | Rangsumme |
|---|---|---:|---:|---:|---:|---:|
| alter Vierfachlauf | GDT525 | 1.098 | 1.328 | 1.386 | 1.418 | 2.109 |
| alter Vierfachlauf | GDT526 | 1.098 | 1.328 | 1.386 | 1.418 | 2.109 |
| 159 Formen, geerbte Ziele | GDT525 | 145 | 154 | 158 | 158 | 184 |
| 159 Formen, geerbte Ziele | GDT526 | **147** | **155** | 158 | 158 | **181** |
| 159 Formen, K-Familie revidiert | GDT525 | 146 | 154 | 158 | 158 | 183 |
| 159 Formen, K-Familie revidiert | GDT526 | **148** | **155** | 158 | 158 | **180** |

Von den 159 Entscheidungen bleiben 145 bereits richtige erhalten, zwei
werden korrigiert und zwölf bleiben zunächst falsch. Es gibt keinen Verlust.
Alle zehn getesteten Gewichte zwischen 0,25 und 1,25 lassen sämtliche alten
Kennzahlen exakt unverändert; ab 0,80 werden beide Zielentscheidungen repariert.

## Weshalb das kein freies `cha-`-Präfix ist

Das alte Material enthält mehrere `cha...`-Formen mit anderen Zerlegungen:

```text
chaiin = CH+AIIN       chair = CH+AIR
chal   = CH+AL         cham  = CH+AM_ADDR
char   = AR            chas  = CH+A_ADDR+S
```

Darum gilt kein mechanisches „alles, was mit `cha` beginnt, beginnt mit
`CH+A_ADDR`“. Die Regel ist genauer: Das alte exakte Ganzwort gewinnt immer.
Nur ein noch nicht belegter rechter Ausbau darf den gelernten Stamm als Default
weiterführen. `chas` zeigt zugleich, dass ein solcher Ausbau im alten Material
tatsächlich vorkommt.

## Die zwei neuen Wege

- `chady`: Der Schluss `dy→DY` hat 32 positive Träger unter 52 sichtbaren
  Gelegenheiten; Feature `1,557417`.
- `chap`: Der Schluss `p→P` hat 2/2 Träger; Feature `1,55`.

Die Karte bewertet nicht die vollständigen Zieloberflächen. Sie verbindet das
alte `cha` mit zwei unabhängig gelernten rechten Kanälen. Genau dieses
„Mischung aus gelernten Ganzstämmen und Fachkürzeln“-Verhalten war das gesuchte
Modell.

## Aktuelle Arbeitstheorie

Die beste Arbeitsarchitektur wird dadurch konkreter:

```text
gelernter ganzer Stamm + produktiver, separat lizenzierter Schluss
```

Neben frei kombinierbaren strukturellen Atomen und vollständig memorisierten
Formen gibt es damit eine mittlere Ebene. Ein Ganzstück kann einen stabilen
Arbeitswert besitzen und dennoch einige Endungen aufnehmen. Alte abweichende
Ganzformen bleiben eigene gelernte Karten. Das ähnelt funktional einem kleinen
Codebuch mit Kürzeln plus erlernten Stammkarten, ohne dass damit schon ein
historisches Codebuch oder eine Wortbedeutung identifiziert wäre.

## Nächster Griff

Nach der familienkorrigierten Auswertung bleiben elf Rang-1-Abweichungen:

```text
aiicthy  chekchy  cthom  dairykodas  dalcheeeky  dsholdaiir
keeol    okedals  qef    qocthedy    saiis
```

Der nächste sinnvolle Schritt ist kein weiterer allgemeiner Bonus. Diese elf
Formen zerfallen in konkrete Konflikttypen: verschluckter sichtbarer Stamm
(`chekchy`, `dalcheeeky`), konkurrierende zusammengesetzte Kurzkarte
(`keeol`, `dsholdaiir`), Trägerfrage (`qef`, `qocthedy`) und lokale
Zeichen bzw. Adressen (`aiicthy`, `cthom`, `dairykodas`, `okedals`,
`saiis`). Als Nächstes sollte geprüft werden, welche dieser Gruppen durch
bereits vorhandene Ganzstämme mit genau einem produktiven Ausbau geschlossen
wird. Neue Seiten sind dafür noch nicht nötig.
