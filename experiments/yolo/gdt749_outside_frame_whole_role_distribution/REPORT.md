# GDT749 — Außenstellen retten vier Rollen und verschieben `qochey`

## Ergebnis

Die 57 GDT748-Entdeckungsstellen wurden vollständig entfernt. Für die sechzehn
wiederholten Rollenformen plus `qochey` bleiben 1.627 Außenstellen, davon 1.311
reader-exakt auf 154 der bereits erlaubten Seiten. Der Test öffnet keine neue
Seite.

Der zunächst attraktivste Befund war falsch stark: ein globales Profil aus
Abschnitt, Zeilenposition, Nachbarachsen und Abschlussnähe schien sieben Rollen
zu bestätigen. Im Leave-self-out-Test auf den 46 bekannten Referenzwörtern
liefert derselbe Klassifikator aber nur 23 richtige Qualitäts-/Stufenlabels,
42 falsche und 60 verpasste. Das entspricht 35,4 Prozent Precision und 27,7
Prozent Recall. Sämtliche X-Ränge bleiben deshalb als Rohdaten sichtbar, dürfen
aber keine Bedeutung hochstufen oder verwerfen.

Nach Grundratenkorrektur der unmittelbar benachbarten bekannten Ganzwörter
bleiben vier brauchbare, weiterhin schwache Außenkompatibilitäten:

| Ganzform | Vorrolle | Außenstellen/Seiten | nur Vorrolle : nur Rivale | Referenzbasis | Anteilsplus |
|---|---|---:|---:|---:|---:|
| `chdy` | DRY | 88/46 | 7:1 | 123:37 | +0,106 |
| `cheey` | DRY | 135/59 | 13:1 | 123:37 | +0,160 |
| `okeey` | HOT | 113/43 | 22:6 | 166:87 | +0,130 |
| `qokedy` | END_STAGE | 161/44 | 13:12 | 72:109 | +0,122 |

Das sind keine Wortübersetzungen. Der praktische Arbeitsstand lautet nur:
`chdy` und `cheey` bleiben am ehesten Trockenrollen, `okeey` bleibt am ehesten
eine Heißrolle, und `qokedy` bleibt am ehesten eine End-/Vollstufenrolle.

## Schwache und offene Karten

Sechs Formen sind mit ihrer Vorrolle vereinbar, heben sich aber nur schwach
oder gar nicht von der normalen Achsenverteilung des Referenzdecks ab:

- `cheol` DRY: 10:3 außen, praktisch genau dieselbe DRY/MOIST-Basisrate;
- `okal` HOT: 11:4, kleines Plus von 0,077;
- `okedy` HOT: 8:3, Plus 0,071;
- `olkaiin` HOT: 3:1, Plus 0,094;
- `oty` COLD: 5:7, wegen der häufigeren HOT-Kontexte dennoch ein kleines
  relatives COLD-Plus von 0,073;
- `sheey` END_STAGE: 10:13, kleines relatives Plus von 0,037.

`lkeey`, `olkar` und `qokaiin` sind außen nur baseline-artig oder leicht gegen
ihre HOT-Vorrolle verschoben. Die HOT-Annahme darf explorativ stehen bleiben,
ist aber kein sinnvoller Standardrenderer. Insbesondere werden die früher
zurückgezogenen Stoffidentitäten für `lkeey` und `olkar` nicht wiederbelebt.

## Zwei Rivalen und ein knapper Sonderfall

`cheky` verliert die Mittelstufen-Voreinstellung als besten Standard. Unter 48
reader-exakten Außenstellen stehen nur eine reine MIDDLE_STAGE-Nachbarschaft
gegen sieben reine BEGIN/END-Rivalen; relativ zur Referenzbasis fällt der
Vorrollenanteil um 0,254. Die Form bleibt vorläufig eine Stufen-/Qualitätsrolle,
aber die konkrete Stufe ist offen und Anfang/Ende sind stärkere Außenrivalen.

`kchdy` hat nur zehn reader-exakte Außenstellen und nur eine polarisierte
unmittelbare Stelle. Das globale Rohprofil stellt drei COLD- und null HOT-Karten
in die Top fünf. Wegen der schlechten Kalibrierung und der einzelnen direkten
Stelle ist das kein Gegenbeweis; COLD/DRY wird lediglich als neuer Rivale neben
HOT geführt.

`okechy` besitzt außerhalb seiner zwei entdeckenden HOT-Serien nur zwei weitere
reader-exakte Stellen:

```text
f107v.4  dain cheky okechy qokain shocthy otaiin alkaiin
f99v.26  okechy
```

Beide haben keine unmittelbar bekannte Qualitätsachse. Ihre nächsten globalen
Profile sind MATERIAL/PREPARATION, COLD/PREPARATION und END_STAGE-Karten; HOT
steht erst auf Rang vier. Der neue beste Arbeitsstand ist deshalb nicht
`okechy = heiß`, sondern: **vollständige Form mit Zubereitungs-/Zustandsrolle;
HOT aus der Serie, COLD/END aus den Außenprofilen, Polarität und Stufe offen.**

## `qochey`: die Endrolle gewinnt den Außenvergleich

Außerhalb der drei GDT748-Rahmen existieren drei weitere reader-exakte Stellen.
Der getrennte Vergleich ergibt:

| Hypothese | bester Referenzrang | Treffer in Top 5 | direkte Voll-/Teiltreffer |
|---|---:|---:|---:|
| DRY + MIDDLE_STAGE | 5 | 1 | 0/0 |
| END_STAGE | 1 | 4 | 1/1 |
| HOT + END_STAGE | 4 | 1 | 1/1 |

Damit wird der frühere Einzelrahmen nicht gelöscht, aber die globale
Arbeitsreihenfolge ändert sich: **`qochey` ist eher eine End-/Übergangsrolle;
DRY/MIDDLE_STAGE bleibt die Lesart des stärksten einzelnen Serienrahmens, und
HOT/END bleibt ein lokaler Rivale.** Eine fixe Qualitätsübersetzung ist derzeit
schlechter als diese kontextabhängige Karte.

## Was sich an der Arbeitstheorie ändert

GDT749 liefert keine neue konkrete Substanz und kein Lexem. Es verhindert aber
zwei falsche Vereinfachungen:

1. globale Abschnitts-/Positionsähnlichkeit ist kein Bedeutungsdecoder;
2. eine Serienrolle darf nicht automatisch auf jedes Vorkommen derselben Form
   übertragen werden.

Die nächste produktive Schicht muss deshalb auf einzelne Vorkommen gehen: ein
kalibrierter Radius-1/2-Hostdispatch soll nur dann HOT/COLD/DRY/MOIST oder eine
Stufe sprechen, wenn die nächsten vollständigen bekannten Karten an dieser
konkreten Stelle einen eindeutigen Slot bilden. Gerade `qochey`, `okechy`,
`cheky` und `kchdy` werden dabei als rivalisierte Formen behandelt.

Der GDT388-Einlass referenziert eine gültige gleichseitige Relation und bleibt
erwartungsgemäß ausschließlich wegen unversiegelten formalen Zugriffs invalid
und nicht score-ready. Null Lexeme, null Komponentenwerte und null neue Seiten
werden exportiert.
