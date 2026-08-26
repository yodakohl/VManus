# GDT498 — Das 495-Zellen-Handlungsraster ist vollständig lesbar

Status: `ALL_FOUR_HUNDRED_NINETY_FIVE_CELLS_READABLE__ZERO_UNAVAILABLE__OBSERVED_AND_COMPOSED_VISIBLE`

## Ergebnis

Die elf bisher für T/R verwendeten Rahmen wurden auf alle neun kurzen
Handlungswurzeln und alle fünf Register ausgeweitet. Das ergibt 9×11×5 = 495
konkrete Arbeitszellen:

- 143 Zellen sind exakt in GDT416 beobachtet;
- sie enthalten 660 alte Events;
- 352 Zellen sind sichtbar als `COMPOSED_WORKING` markiert;
- 495/495 verwenden ausschließlich alte owner-lokale Werte;
- null Zellen sind unverfügbar;
- alle 110 T/R-Zellen stimmen wortgleich mit GDT497 überein.

Der zunächst fehlende Wert war `E=GRAD I`: Er liegt nicht im
Neunzehn-Kern-Atlas GDT415, sondern im ergänzenden alten Slotatlas GDT493. Nach
Vereinigung beider bereits vorhandenen Werttabellen ist auch der komplette
`@ACTION+CH+E+Y`-Rahmen in allen Registern lesbar. Dafür wurde kein neuer Wert
erfunden.

## Wie stark die 352 Kompositionen sind

Die Kompositionen teilen sich verständlich:

- 165 haben mindestens zwei andere beobachtete Handlungsköpfe im selben
  Rahmen und Register;
- 88 haben genau einen solchen lokalen Kopf;
- 49 haben denselben Handlungskopf und Rahmen in einem anderen Register;
- 50 besitzen bisher nur alte Einzelwerte, aber noch keine beobachtete
  komplette Nachbarzelle.

Damit stehen 253/352 Kompositionen bereits in einer lokalen beobachteten
Ganzrahmenfamilie. Die 50 letzten Fälle sind klar lokalisierbar und bleiben
sichtbar schwächer; sie werden nicht wie Beobachtungen behandelt.

## Handlung und Rahmenprofil

`OK` ist mit 29/55 Zellen und 275 Events der am dichtesten beobachtete Kopf.
`P` ist mit 3/55 Zellen der dünnste und benötigt 52 Kompositionen. CH, SH, K,
S, CHD, T und R liegen dazwischen. Das passt zur bisherigen Mischarchitektur:
Einige häufige Fachhandlungen tragen viele Rahmen direkt, seltenere Köpfe
bleiben trotzdem aus denselben alten Slots lesbar.

Die einfachen Rahmen sind am stabilsten. Nackte Handlung, WERT, ANTEIL,
ZIELORT, FORTSETZEN und POSTEN haben zusammen keine reine
Einzelwert-Komposition. Die 50 schwächsten Zellen konzentrieren sich auf
`@ACTION+AL+Y`, `@ACTION+CH+E+Y`, `@ACTION+CHD+Y`, `@ACTION+OR+Y` und
`CH+@ACTION`. Genau dort treten mehrere Handlungen oder mehrere ausdrückliche
Argumente zugleich auf.

## Aktuelle Arbeitsübersetzung

Jede der 495 Zellen besitzt einen deutschen Default. Beobachtete Zellen zeigen
eine alte Klausel; komponierte Zellen verwenden den unveränderten GDT416-
Renderer und die GDT497-Kontextregel. 115 unbeobachtete Ellipsen generalisieren
156 geerbte Nominalstellen. Dadurch kommt keine Kombination ohne Bedeutung
davon, ohne dass ihre tatsächliche Vorkunft behauptet wird.

Der Validator besteht 3064 von 3064 Prüfungen. Es wird keine Manuskript-
Oberfläche und kein künftiges Vorkommen vorhergesagt.

## Nächster sinnvoller Schritt

Die 352 Kompositionen sollen nun innerhalb ihrer vier Stützklassen geordnet
werden. Zuerst werden die 165 lokalen Mehrkopf-Fälle als produktive
Hauptschicht veröffentlicht. Danach werden die 50 Einzelwert-Fälle gegen alte
Teilrahmen und benachbarte Aktionspaare gelesen. Wiederholte Handlungen wie
`CH+CH` oder `CHD+CHD+Y` erhalten dabei eine flüssige, aber bedeutungsgleiche
deutsche Verdichtung statt einer mechanischen Wortwiederholung. Die Seiten
bleiben geschlossen.
