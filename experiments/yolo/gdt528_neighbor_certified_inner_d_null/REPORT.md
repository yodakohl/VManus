# GDT528 — `qocthedy` ist eine begrenzte Schreibvariante, kein neues `d`-Wort

## Ergebnis

`qocthedy` erhält erstmals eine vollständig zusammengesetzte Standardlesung:

```text
qocthey  = CARRIER_Q+O+CH+T+E+Y
qocthedy = CARRIER_Q+O+CH+T+E+Y
```

Das zusätzliche sichtbare `d` trägt in genau dieser lizenzierten Endvariante
kein weiteres Atom. Daraus folgt ausdrücklich nicht `d=NULL` im Allgemeinen.

Der alte Nachbar liefert die Brücke:

```text
qockhey  = O+CH+K+E+Y
qockhedy = O+CH+K+E+Y
```

`qocthey` und `qockhey` unterscheiden sich sichtbar nur in `t/k`. Nach dem
Entfernen des strukturellen `CARRIER_Q` unterscheiden sich ihre Rezepte genau
in derselben bekannten Aktionsstelle: `T/K`. Das ist deutlich stärker als
eine beliebige optische Ein-Zeichen-Nähe.

## Warum die erste einfache Idee nicht genügte

Im alten Bestand gibt es sechzehn exakte rezeptgleiche Paare mit einem
zusätzlichen inneren `d`; neun davon haben die enge Form `...y/...dy`. Eine
erste kreative Regel benutzte nur diese Endform plus einen optisch um ein
Zeichen verschiedenen Nachbarn. Sie repariert zwar `qocthedy`, kostet aber
einen alten Top-2-Platz: `1328→1327`, Rangsumme `2109→2110`.

Die bessere Regel verlangt zusätzlich den passenden Wechsel eines bekannten
Aktionsstamms im Rezept. Damit verschwindet der alte Schaden vollständig.

## Scorekarten

| Deck | Stand | Rang 1 | Top 2 | Top 3 | Top 5 | Rangsumme |
|---|---|---:|---:|---:|---:|---:|
| alter Vierfachlauf | GDT527 | 1.098 | 1.328 | 1.386 | 1.418 | 2.109 |
| alter Vierfachlauf | GDT528 | 1.098 | 1.328 | 1.386 | 1.418 | 2.109 |
| 159 geerbte Ziele | GDT527 | 148 | 156 | 158 | 158 | 179 |
| 159 geerbte Ziele | GDT528 | **149** | **157** | 158 | 158 | **177** |
| bisher revidierte Lesungen | GDT527 | 150 | 156 | 158 | 158 | 177 |
| bisher revidierte Lesungen | GDT528 | **151** | **157** | 158 | 158 | **175** |

148 richtige aktuelle Entscheidungen bleiben richtig, eine wird korrigiert,
zehn geerbte Fehler bleiben. Keine richtige aktuelle Entscheidung geht
verloren. Unter den 1.441 im alten Vierfachlauf erzeugten Rezepten bleiben
sämtliche Einzelränge und Top-1-Entscheidungen gleich.

## Was die Arbeitsübersetzung ungefähr sagt

Die unveränderte Atomspur lautet:

```text
[CARRIER_Q: Strukturträger] · [O: Ausführung] · CH: NEHMEN ·
T: EINSTELLEN · [E: Grad I] · Y: POSTEN
```

Als knappe Werkstattparaphrase: „Unter q-Träger/Ausführung: nehmen, auf Grad I
einstellen und posten.“ Das ist eine bewusst provisorische Funktionslesung,
kein entzifferter deutscher Satz. Das sichtbare `d` erhält hier keine eigene
deutsche Bedeutung, weil die ganze `...y/...dy`-Variante dieselbe Rezeptkarte
trägt.

## Was diese Runde am Mischcodebuch verbessert

Die Architektur hat nun vier sauber unterscheidbare Ebenen:

1. bekannte kurze technische Atome werden geordnet zusammengesetzt;
2. gelernte Ganzstücke können als produktive Zwischenstämme dienen;
3. transparente Endungen dürfen nur über eigene alte Kanäle anschließen;
4. ein zusätzliches sichtbares Zeichen kann eine begrenzte Schreibvariante
   markieren, wenn sowohl die Oberflächenfamilie als auch der Rezeptbau passen.

Damit ist `d` weder pauschal bedeutungslos noch zwangsläufig ein eigenes Atom.
Sein Wert bleibt von der sichtbaren Konstruktion abhängig.

## Nächster Griff

Acht Rang-1-Abweichungen bleiben:

```text
aiicthy  chekchy  cthom  dairykodas
dalcheeeky  dsholdaiir  qef  saiis
```

Der nächste produktive Angriff sollte die knappe `cthom`-Alternative
`M_LOCAL` gegen `AM_ADDR` sowie die alten sichtbaren `...om/...am`-Familien
prüfen. Dafür werden weiterhin keine neuen Seiten benötigt.
