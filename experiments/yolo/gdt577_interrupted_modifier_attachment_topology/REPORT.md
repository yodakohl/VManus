# GDT577 — fünf Anschlussformen genügen für alle unterbrochenen Wiederholungen

## Ergebnis

`PASS_62_INTERRUPTED_GROUPS__125_SLOTS__75_EXISTING_ATTACHMENTS_REPLAYED__50_EXPLORATORY_HEAD_CANDIDATES__5_TOPOLOGIES__ONE_RENDERER_HISTORY_CONFLICT__ZERO_SLOT_COLLAPSE`.

Die 62 unterbrochenen Wiederholungsgruppen sind keine 62 Sonderwörter. Ihre
125 geschriebenen Slots fallen vollständig auf fünf kleine Anschlussformen:

| Form | Gruppen | Lesbare Konsequenz |
|---|---:|---|
| verschiedene Handlungsvorkommen | 35 | jeden Modifier beim eigenen Handlungskopf sprechen |
| Klammer um denselben Kopf | 15 | ersten Slot vor, zweiten erneut nach der Handlung erhalten |
| gleicher Kopf, gleiche Seite | 3 | ein Kopfbündel, aber zwei geordnete Slots |
| aktiver Kontextkopf | 8 | die Slotfolge unter der fortgeführten Handlung lesen |
| Handlung plus Fortsetzungsträger | 1 | ersten Slot bei der Handlung, zweiten bei OL erhalten |

Damit gibt es nun für jeden Slot eine Default-Anschlussstelle. Kein Slot wird
gelöscht, als bloße Dopplung behandelt oder zu `zweimal` zusammengezogen.

## Was schon fest war und was neu vorgeschlagen wird

75 Slots — 71 aus den alten 26 Seiten und vier aus den neueren vier Seiten —
besitzen bereits Fokusbindungen für E, EE oder AR. GDT577 reproduziert alle
75 exakt.

Die 50 O-/D_ADDR-Slots hatten solche Bindungen bisher nicht. Für sie wird
explorativ dieselbe lokale Werkstattlogik angewandt:

- 21 stehen nach dem nächstgelegenen sichtbaren Handlungskopf;
- 14 stehen vor ihm;
- 14 gehören zum schon aktiven Besitzerkopf;
- genau einer, das zweite D_ADDR in `G407-E3030`, gehört zum geschriebenen
  OL-Fortsetzungsträger.

Das ist ein Anschlussmodell für die deutsche Arbeitsstimme, keine neue
Bedeutung von O oder D_ADDR.

## Konkrete Lesefolgen

`G407-E0491 · CH+E+T+E+LOCAL_CHAR_G`

```text
CH → E    und    T → E
Nehmen auf Grad I; Einstellen ebenfalls auf Grad I.
```

Die beiden Grade hängen an zwei verschiedenen Handlungen. Ein globales
„Grad I zweimal“ wäre weniger informativ.

`G407-E0607 · O+P+O+AM_ADDR`

```text
O → P → erneut O → AM_ADDR
```

Hier umklammern beide O-Slots denselben P-Kopf. Die Arbeitsstimme darf diese
Folge aussprechen, soll aber O keine zusätzliche Prozessdefinition geben.

`G407-E3030 · D_ADDR+SH+OL+Y+D_ADDR`

```text
D-Stelle → Halten; OL → wieder D-Stelle
```

Das ist der einzige gemischte Handlung/Fortsetzung-Fall.

`G407-E3605 · D_ADDR+CH+E+O+K+E+D_ADDR+Y`

E und D_ADDR benutzen dieselben zwei lokalen Köpfe CH und K. Solche
überlappenden Gruppen werden auf Ereignisebene einmal gemeinsam gerendert,
nicht zweimal unabhängig übereinandergelegt.

## Ein nützlicher Fehlerfund

`G407-E1755 · D_ADDR+AR+D_ADDR+AR+DY` besitzt zwei frühere Stimmen:

- GDT416 erzeugte für die AR-Wiederholung automatisch `[außen]` und
  `[innen]`;
- GDT565 erzeugte später die schlichte schriftnahe Folge
  D_ADDR → AR → D_ADDR → AR.

Die beiden wirklichen AR-Fokuszeilen sind jedoch `SINGLE/SINGLE`; sie
belegen nur denselben geerbten OK-Kopf. Deshalb bleibt dieses eine Ereignis
unverändert und wird weder als Wiederholung verkürzt noch zum achtzehnten
Scope-Paar erklärt. 58 der 59 Ereignisse beziehungsweise 60 der 62 Gruppen
sind sofort rendererbereit.

## Historische Arbeitsstimme

Zeitnahe Rezepttexte stützen die Trennung der Partikel, nicht die Voynich-
Bedeutungen selbst:

- Die [Hamburger Sammlung Ha1-I, um 1463](https://diglib.hab.de/edoc/ed000270/texts/tei-transcription.html)
  verwendet Folge-, Rückkehr- und additive Marker verschieden.
- [S 392, um 1500](https://d-nb.info/138537974X/34) kennt „noch einmal“,
  Rückkehr zum Feuer und `desgleichen` für ein analoges Verfahren.
- [Cenninis Werkstattanweisung, Kapitel 145](https://it.wikisource.org/wiki/Il_libro_dell%27arte/Capitolo_CXLV)
  ordnet mehrere `gradi` lokal zu und kehrt zu früheren Stufen zurück.

Daraus folgt eine brauchbare moderne Stimme: `ebenfalls` bei parallelen
Köpfen, `erneut` bei einer späteren O-/Gradnennung und `wieder` bei einer
Stellen- oder Ausgangsrückkehr. `danach` wird nicht pauschal ergänzt, weil
es eine stärkere Zeitbehauptung wäre als die bloße Schriftfolge.

## Nächster Schritt

Die 58 konfliktfreien Ereignisse können nun aus ihren geordneten
Slot-Kopf-Spuren neu formuliert und in die vollständige 5.122-Ereignis-Ausgabe
zurückgespielt werden. `G407-E1755` bleibt dabei bytegleich. Danach sind die
siebzehn getrennten äußeren/inneren Paare als eigener Koordinationspass dran.

GDT577 ändert keine Seite, Oberfläche, Segmentierung, Rezeptfolge, Wurzel,
Bedeutung oder Scopezuweisung. Die 49 unabhängigen Prüfungen bestehen.
