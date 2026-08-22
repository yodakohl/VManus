# V62 R2 — Historische Ellipse, Anaphora und aktive Referenten

## Ergebnis

Die ausgewählten 116 V61-Statements lassen sich als historisch denkbare
Herbal-/Rezept- und Bade-/Gefäßklauseln lesen, wenn der Schreiber vier kleine,
record-lokale Gedächtnisregister führt:

1. den stillen Bild- oder Recordbesitzer;
2. den aktiven Simplex, Pflanzenteil, Ansatz oder Flüssigkeitsposten;
3. das aktuelle Ziel beziehungsweise die sichtbare Station;
4. bei wirklicher Rücknahme den anonymen Antezedenten.

Das Modell ist ausführbar, aber teuer: Es benötigt **360 stille
Argumentbindungen**. Davon sind 116 Bildbesitzer, 116 aktive Gegenstände, 105
Ziele/Stationen und 23 frühere Gegenstände. Die 116 Aussagen verwenden elf
Besitzer-IDs, 39 aktive Gegenstands-IDs und 44 Ziel-/Stations-IDs. Diese IDs
sind ausschließlich editorielle Gedächtnisstützen; im Manuskript sind sie nicht
sichtbar und keinem Zeichen zugewiesen.

Die historische Plausibilität lautet daher: **möglich als stark elliptische,
bildgestützte Werkstattquelle; nicht aus den Karten allein rekonstruierbar**.
Der hohe Ergänzungsbedarf stärkt zugleich den Listen-/Formularrivalen.

## Registerkonvention

Alle IDs beginnen neu am Recordanfang:

```text
H2:O01  stiller Besitzer des H2-Artikels
H2:I01  erster aktiver Simplex-/Ansatzgegenstand
H2:I02  nach Parallel- oder Phasenreset neu eröffneter Gegenstand
H2:T01  erstes Ziel beziehungsweise erste Station
H2:I00  nur falls ein schon vor Recordbeginn aktiver Exemplarposten nötig ist
```

`INTRODUCE` eröffnet einen Bildbesitzer oder Arbeitsgegenstand. `CARRY` behält
ihn innerhalb derselben Recordwelt. `RESUME` beginnt eine neue Klausel und
nimmt denselben Gegenstand wieder auf. `RESET` eröffnet nach neuem Pflanzenteil,
neuem Posten oder paralleler Zelle eine neue anonyme ID. Der einzige `I00`-Fall
ist B6: Die ausgewählte Klausel beginnt bereits „mit der vorigen Zubereitung“;
ein antecedierender Exemplarposten muss daher vor dem sichtbaren Record liegen.

Die vollständige Ausgabe markiert jede Erweiterung:

```text
[STILL:OWNER=...]
[STILL:ACTIVE=...]
[STILL:TARGET=...]
[STILL:PREVIOUS=...]
[EXACT:VORIGES?→...;ANTECEDENT_TYPE_STILL_SILENT]
```

Nur der unveränderte V60-Kurzmerker innerhalb `EXACT` ist kartengebunden.
Besitzer, Stoffklasse, konkretes Ziel und Antezedentenart bleiben stiller
lokaler Exemplartext. Die deutsche Klausel nach den Markern ist die
unveränderte ausgewählte V61-Werkstattlektüre.

## Quantifizierte Recordregister

| Record | Statements | aktive IDs | Ziel-IDs | Statements mit früherem Gegenstand | stille Bindungen |
|---|---:|---:|---:|---:|---:|
| H1 | 2 | 1 | 1 | 2 | 7 |
| H2 | 3 | 2 | 0 | 1 | 7 |
| H3 | 4 | 3 | 2 | 1 | 11 |
| H4 | 4 | 2 | 1 | 0 | 10 |
| H5 | 6 | 4 | 1 | 2 | 17 |
| B1 | 21 | 6 | 9 | 6 | 69 |
| B2 | 22 | 6 | 7 | 1 | 67 |
| B3 | 34 | 7 | 13 | 6 | 108 |
| B4 | 16 | 6 | 7 | 2 | 50 |
| B5 | 3 | 1 | 2 | 1 | 10 |
| B6 | 1 | 1 | 1 | 1 | 4 |
| **Summe** | **116** | **39** | **44** | **23** | **360** |

Die Bio-Statements benötigen sämtlich eine Station oder ein Körper-/Gefäßziel;
bei den Herbal-Statements wird ein Ziel nur gesetzt, wenn die ausgewählte
lokale Klausel Anwendung, Indikation, Gefäß oder Körperstelle verlangt. Ein
Phasenwechsel ersetzt das Ziel nicht automatisch. Eine neue Ziel-ID entsteht
nur bei echter Parallelzelle oder sichtbarer/ausgeschriebener
Öffnungs-, Becken- oder Ablaufrichtung.

## Alle Carries

Das V61-Grenzledger enthält 27 positive Carries: 19
`CONTINUE_SAME_CLAUSE` und 8 `RESUME_ACTIVE_ITEM`. Alle stehen mit Besitzer-,
Gegenstands- und gegebenenfalls Ziel-ID in
`V62_R2_46_BOUNDARY_CARRY_AUDIT.tsv`. Die übrigen 10
`NEXT_PARALLEL_CELL`, 8 `START_NEW_CLAUSE` und eine ungelöste Grenze behalten
mindestens den Recordbesitzer, dürfen den aktiven Posten oder die Station aber
zurücksetzen.

Die Zustandsedition eröffnet elf erste aktive Gegenstände, führt 28
begründete Gegenstandsresets aus und markiert acht explizite Wiederaufnahmen.
Ein `CONTINUE` innerhalb desselben V61-Statements behält zwingend dieselbe ID;
ein `RESUME` behält dieselbe ID in einer neuen Klausel. Bei
`NEXT_PARALLEL_CELL` wurde ein neuer Posten nur dort eröffnet, wo die
ausgewählte V61-Lesung selbst einen anderen Pflanzenteil, eine neue Charge oder
eine neue Arbeitszelle verlangt.

## Die beiden exakten VORIGES?-Bindungen

### H2-S002

`VORIGES?` bindet an `H2:I01`, den in H2-S001 aktiven Simplex-/Ansatzbestand.
Die Markierung sagt nur: Rückverweis auf diesen anonymen Gegenstand. Ob er Saft,
Sud, Ölansatz oder eine formale Charge ist, bleibt still. Der stärkste Rivale
ist eine neue parallele Erntevariante; dann wäre der scheinbare Antezedent bloß
eine wiederholte Artikelrubrik.

### B1-S002

Das Statement eröffnet `B1:I02` als nächsten gemessenen Posten. Am Übergang
F022→F023 bindet das exakte `VORIGES?` innerhalb derselben zweizeiligen Klausel
an `B1:I02`. Auch hier ist nur die Rückrelation kurz markiert; „Ansatz“, Öl,
Becken und verbundene Läufe stammen aus der lokalen Expansion. Der starke
Rivale trennt F023 als neue Klausel am gleichen Apparat.

Diese zwei Belege tragen eine anaphorische Werkstattfunktion, aber keine
Bestimmung der Referentenart und schon gar keine lateinische Gleichsetzung.

## f82r.3→f82r.4: Randkopie ohne Gloss

An `B2-LB02` steht dieselbe sichtbare Ganzkarte `qokaiin` unmittelbar vor und
nach dem Zeilenreset. V61 führt F050 und F051 als ein Statement; V62 hält daher
den neu eröffneten Posten `B2:I03` über die Grenze. Die Wiederholung kann wie
eine anticipatorische Randkopie oder eine Wiederaufnahme den Abschreiber zum
gleichen Posten zurückführen.

Sie erhält **keinen Kartenwert**: Der ausgewählte V60-Skeleton ist an beiden
Stellen `∅`. Absichtliche Wiederholung, Dittographie oder zwei gleichartige
Formularposten erklären dieselbe Kante ebenso gut. Gerade weil die Form kopiert
wird, darf aus ihr keine zusätzliche Semantik gewonnen werden.

## Historische Mechanismen

In einem kompilierten Herbal kann ein Bildlemma den Simplex über mehrere
Rezeptglieder halten. Imperativische Reihen, `item`-artige Fortsetzungen und
elliptische Wiederaufnahme vermeiden die ständige Wiederholung von Pflanze,
Teil und Präparat. *Idem*, *de eodem* und *praedictum* sind dafür passende
zeitgenössische Funktionsvergleiche. Sie sind weder Übersetzungen noch
Lautwerte irgendeiner Voynich-Form.

Ein Bade-, Wasch- oder Gefäßregimen kann entsprechend eine sichtbare Zelle als
Besitzer benutzen und Flüssigkeit, Gefäß und Station in mehreren kurzen
Operationen fortgelten lassen. Der gleiche Mechanismus funktioniert jedoch
ebenso in einem nichtmedizinischen Wasserwerk- oder Werkstattformular. Die
Figuren machen Patient und Apparat nicht eindeutig; sie liefern nur den
stillen Besitzerraum.

## Stärkster Listen-/Formularrivale

Der Rivale benötigt wesentlich weniger sprachliche Anaphora: Jede Bild- oder
Feldzelle adressiert Besitzer, Stoff und Station direkt durch ihre Lage; kurze
Gruppen sind Werte oder Operationen innerhalb dieser Zelle. Dann sind die 105
Zielbindungen keine ausgelassenen Satzargumente, sondern Formularadressen, und
die 28 Gegenstandsresets sind bloße nächste Listenposten. Die f82-Randkopie ist
in diesem Modell Wiederholung eines Buchungswerts statt syntaktischer Carry.

Gegen den reinen Formularrivalen sprechen die 27 ausgewählten Carries, die
beiden exakten `VORIGES?`-Relationen und fragmentarische Fortsetzungen wie B5.
Für ihn sprechen der universelle Bedarf an stillen Besitzer-/Aktivwerten, die
vielen terminalen Kurzfelder und die 360 insgesamt erforderlichen Bindungen.
Historisch bleibt deshalb ein **bildgestütztes Mischregister** plausibler als
voll ausformulierte Prosa.

## Artefakte und Validierung

- `V62_R2_116_STATEMENT_REFERENT_TRACE.tsv`: alle Statements mit Zustand vor
  und nach der Klausel, Aktionen, stillen Slots und markierter deutscher
  Quellenklausel.
- `V62_R2_46_BOUNDARY_CARRY_AUDIT.tsv`: sämtliche Zeilengrenzen einschließlich
  beider `VORIGES?`-Fälle und der f82-Randkopie.
- `V62_R2_11_RECORD_REFERENT_REGISTERS.tsv`: vollständige Recordregister,
  Zählungen, Gesamtlektüre und stärkster Listen-/Formularrivale.
- `V62_R2_VALIDATION.json`: **PASS** für 116/46/11, 27 Carries, zwei exakte
  `VORIGES?`-Bindungen und eine unglossierte f82-Randkopie.

Alle V60-Kurzmerker und V61-Klauseln bleiben unverändert. Keine V62-Siblings,
keine neuen Seiten, kein f84/f84r und keine externe Recherche wurden benutzt.
