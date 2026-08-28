# GDT594 — 49 Y-Badeobjekte erhalten konkrete Vorkommensdefaults

Status: `PASS_49_Y_OCCURRENCE_COMPLETIONS__17_LOCAL_STATION__2_LOCAL_FLOW__1_LOCAL_BODY__29_RESET_BODY_FIRST__20_ANAPHORIC__29_DEFINITE__254_OBJECTS__49_STATEMENTS_CHANGED__44_COLD_DEFAULTS_REMAIN`

## Ergebnis

Alle 49 nach GDT593 noch neutralen Badegut-Fälle mit spezifischem getragenem
`Y` besitzen jetzt eine konkrete Primärlesung:

- 17 sichtbare lokale Y-Quellen lesen sich als `denselben Stationsansatz`;
- 2 sichtbare Umleitungsquellen lesen sich als `denselben Strom im Badbetrieb`;
- 1 sichtbare Körperquelle liest sich als `denselben Körper`;
- 2 gleichsatzinterne Quellen liegen hinter einem echten post-donor Neustart;
- 27 weitere Fälle sind echte Besitzer-Defaults hinter einer Satzgrenze;
- diese 29 Resetfälle werden am sauberen SH-Badziel zu `dem Körper`.

Die Trennung kommt nicht aus einem globalen Wörterbuch. Sie kommt aus der
Objektweite des jeweiligen Vorkommens: lokale Quelle behalten, nach Reset den
Zielhost neu lesen. Genau deshalb steht lokal `denselben`, nach Reset aber nur
`den Körper`.

## Konkrete Lesebeispiele

Starke lokale Übergaben:

```text
E1520  Halte denselben Stationsansatz im Bad auf Grad I.
E2612  Halte denselben Stationsansatz im Bad auf Grad I.
E2897  Halte denselben Stationsansatz im Bad auf Grad II.
E3097  Halte denselben Stationsansatz im Bad auf Grad I.
E3426  Halte denselben Stationsansatz im Bad auf Grad I.
E3673  Halte denselben Stationsansatz im Bad auf Grad I.
E3684  Halte denselben Stationsansatz im Bad auf Grad I.
```

Die zwei Stromfälle werden operational gelesen, nicht als eingetauchtes
Fließgewässer:

```text
E1590  Halte denselben Strom im Badbetrieb auf Grad I.
E2869  Halte denselben Strom im Badbetrieb auf Grad I.
```

Neustarts:

```text
E1431  Beginne danach den nächsten Arbeitsgang. Halte den Körper im Bad auf Grad I.
E2783  Halte den Körper im Bad auf Grad I. Entnimm oder lass ab. Führe zu.
E3017  Bereite vor. Halte den Körper im Bad auf Grad I.
E3580  Halte den Körper im Bad auf Grad I.
E3768  Halte den Körper im Bad auf Grad I.
```

## Der Host-/Atomkonflikt verbessert die erste Fassung

Die erste Host-basierte Fassung hätte fünf gleichsatzinterne Quellen als Reset
behandelt: `E1431`, `E1658`, `E3426`, `E3673`, `E3768`. Das ist für drei Fälle
zu grob. In `E1656=OT+Y` und `E3425=OT+EE+Y` steht das frische Y **nach** OT;
bei `E3673` steht das neue Y in `E3672=OL+AL+Y` sogar ein Ereignis nach
`E3671=OT+AIIN`. GDT559 bestätigt die Weitervererbung jeweils ausdrücklich.

Darum bleiben `E1658` (`denselben Körper`), `E3426` und `E3673` (jeweils
`denselben Stationsansatz`) lokal. Nur `E1431` und `E3768` besitzen einen
Kontrollschnitt nach dem Donor und vor dem Ziel. Die ältere 17/32-Hostspur wird
bei den drei Konflikten samt Körperalternative erhalten, aber nicht als
Primärmodell benutzt. Nur `E2537` und `E2628` kreuzen zusätzlich einen
physischen Absatz; beide sind ohnehin Besitzer-Defaults.

## Manuelle Werkstattlektüre

Eine unabhängige vollständige Lektüre aller 49 Zielaussagen auf allen sechs
Seiten ergab:

- 35 unmittelbar brauchbare Arbeitslesungen;
- 11 lesbare, aber echte Körper/Stations-Gabeln;
- 2 operationale Stromfälle;
- 1 unabhängig vom Objekt fragmentierte Kontrollpassage (`E3426`).

Die elf Zweiweg-Fälle sind `E1584`, `E1702`, `E1776`, `E1814`, `E2788`,
`E3049`, `E3399`, `E3556`, `E3570`, `E3673` und `E3768`. Keine Primärklausel
ist im Werkstattsinn völlig unsinnig. Die Rivalen werden deshalb nicht
gelöscht.

## Vollständige Edition

49 von 793 Aussagen ändern sich; 744 bleiben gegenüber GDT593 byte-identisch.
Die zwölf AIN/OR-Promotionen aus GDT593 bleiben vollständig erhalten. Das
254er Badeobjektprofil lautet nun:

| Arbeitsobjekt | Anzahl |
|---|---:|
| Körper | 83 |
| Stationsansatz | 98 |
| Badegut | 46 |
| Einheit | 13 |
| Portion | 12 |
| Strom | 2 |

Damit sind alle 61 spezifischen GDT569-Kandidaten über dem neutralen Badegut
konkretisiert. Übrig bleiben 44 kalte Defaults: 17 AIIN-Füllspuren und 27
Fälle ohne spezifische GDT569-Wurzel. Sie benötigen eine andere
Bedeutungsquelle und sind der nächste sinnvolle Angriffspunkt.

## Erhaltener Möglichkeitsraum

Jede der 49 Karten enthält weiterhin:

- den bisherigen Badegut-Satz;
- die ältere GDT569-Kontextklausel mit `Stationsposten`;
- eine Körper- und eine Stationsalternative;
- einen Stromkanal, ausdrücklich operational formuliert.

GDT594 sagt daher nicht `Y = Körper`. Es sagt: *dieses* Y-Vorkommen übernimmt
eine lokale Station, einen lokalen Strom oder einen lokalen Körper; *jenes* Y-Vorkommen steht nach
einem Reset in einem körpernahen Badhost und erhält Körper als ersten
Arbeitsdefault.

Validierung: 117/117 Prüfungen grün, einschließlich exakter 49er-Zielmenge,
20/2/27-Grenzteilung, drei expliziter Host-/Atomkonflikte, vollständiger
Rivalen, E3243-Doppelaktion und
byte-identischem Neubau sämtlicher Ergebnisartefakte. Keine neue Seite wurde
geöffnet.
