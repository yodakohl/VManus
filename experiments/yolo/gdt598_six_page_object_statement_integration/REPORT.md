# GDT598 — 650 fertige Objektaktionen im vollständigen Satzstrom

## Ergebnis

Die getrennten GDT596- und GDT597-Phrasebooks stehen jetzt erstmals in einem
gemeinsamen Leser. Der Join ist vollständig und kollisionsfrei:

```text
313 Aussagen / 2.272 Hosts
└── 1.443 Aktionshosts
    ├── 650 objektfertig
    │   ├── 254 SH aus GDT596
    │   └── 396 T/CHD/S aus GDT597
    └── 793 sichtbare Restaktionen
        ├── 298 mit geschriebenem Teilnehmerpacket
        ├──  46 nur mit AIIN-Maßparameter
        └── 449 ohne Träger
```

420 Hostklauseln in 258 Aussagen werden gegenüber GDT584 tatsächlich
konkreter; 230 der 650 fertigen Klauseln waren schon wortgleich. Alle 1.622
nicht ersetzten Hosts bleiben exakt erhalten. Absatzstruktur und Hostfolge
bleiben in 313/313 Aussagen identisch.

## Was bereits lesbar ist

Die gemeinsame fertige Objektschicht enthält 399 Stationen, 113 Körper, 36
Flüsse, 34 Portionen, 25 Einheiten, 24 Maße, 16 Bedingungen und drei
Körperteile. Das ist die Addition der beiden unveränderten Phrasebooks, keine
neue Bedeutungsrunde.

71 Aussagen sind bereits für jede ihrer Aktionen objektfertig. 229 mischen
fertige und offene Aktionen; 13 bestehen ausschließlich aus Restaktionen.
Damit berührt die fertige Schicht 300/313 Aussagen. Es ist sofort sichtbar, wo
eine folgende Objektentscheidung den ganzen Absatz verbessert und wo sie nur
eine isolierte Klausel betrifft.

## Der korrigierte Rest

Der relevante Rest ist nicht der breitere 900er GDT582-Hostcensus, sondern die
exakte GDT584-Aussageebene:

| Root | Rest | Teilnehmerpacket | nur AIIN | ohne Träger |
|---|---:|---:|---:|---:|
| CH | 196 | 32 | 1 | 163 |
| K | 159 | 106 | 7 | 46 |
| OK | 285 | 132 | 34 | 119 |
| P | 55 | 8 | 0 | 47 |
| R | 52 | 20 | 4 | 28 |
| übriges SH | 46 | 0 | 0 | 46 |

Das zusätzliche SH-Restfeld ist wichtig: GDT596 schloss 254
`SH_BIO_BATHE`-Hosts, während GDT584 auf den sechs Seiten 300 SH-Hosts besitzt.
44 lesen bisher generisch `Halte den Zustand`, zwei gehören zur
CH→SH-Brücke. Sie müssen im nächsten Pass zusammen mit CH/K/P/OK/R einen
konkreten Gegenstand erhalten.

## Nächste Runde

Die 793 Restaktionen können jetzt ohne Suchnebel geschlossen werden:

1. 298 geschriebene Teilnehmerpackets aus ihren sichtbaren Y/AIN/OR-Slots
   typen und AIIN nur als zusätzlichen Parameter behandeln;
2. 46 AIIN-only- und 449 trägerlose Hosts über Teilnehmer-/Parameterzustand,
   gleichereignige Komplemente und kurze Rootdefaults lesen;
3. die fertigen Klauseln wieder in genau diese 313 Aussagen einsetzen.

## Warum der Join selbst ein Ergebnis ist

Die 650 fertigen Action-Slots liegen nur in 610 Ereignissen. 36 Ereignisse
tragen mehrere fertige Aktionen, 20 davon gleichzeitig GDT596- und
GDT597-Klauseln. Ein Ereignisschlüssel würde 40 gültige Klauseln verlieren.
Auch Textsuche scheitert: Nur 154 verschiedene GDT584-Basisklauseln stehen den
650 Slots gegenüber; zehn alte Strings haben an 240 Slots mehr als eine
Endfassung. Allein `Halte im Bad auf Grad I` erscheint 104-mal und führt zu
zehn konkreten Varianten.

GDT598 bewahrt außerdem alle 40 manuellen Reviewkarten unter namespaceten IDs
und führt die 40 lokalen Seitenkarten in einem strikt getrennten Anhang. Damit
gehen weder Rivalen noch sieben lokale Name-Overrides in den Lauftext über.

Keine neue Seite, Wurzel oder Segmentierung ist dafür nötig. GDT598 ist die
neue Satzbasis und GDT599 kann direkt auf dem 793er Restblatt arbeiten.
