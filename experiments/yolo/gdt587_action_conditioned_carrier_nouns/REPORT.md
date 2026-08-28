# GDT587 — konkrete Trägernomen am Handlungshost

## Ergebnis

`PASS_1243_ACTION_CONDITIONED_CARRIERS__953_EXACT_ACTION_HOSTS__136_OBSERVED_ACTION_ROOT_CELLS__793_STATEMENTS__744_LOCAL_CARDS__ZERO_GLOBAL_ROOT_CHANGE`

GDT587 löst den wichtigsten Restfehler des GDT586-Lesers: `Y`, `AIIN`, `AIN`
und `OR` mussten bislang auch bei einem bereits konkreten Verb oft als
„Charge oder Posten“, „Maß oder Wert“ und „Gefäß- oder Arbeitseinheit“ stehen.
Jetzt besitzt jede ihrer 1.243 geschriebenen Stellen unter einer bereits
verfeinerten `T/SH/CHD/S`-Handlung eine occurrence-genaue Nomenform.

| Ebene | Zahl |
|---|---:|
| geschriebene Trägerstellen | 1.243 |
| exakte Handlungshosts | 953 |
| beobachtete Register×Regel×Root-Zellen | 136 |
| betroffene Lauftexte | 379 |
| betroffene lokale Karten | 70 |

Die vier Stammkerne ändern sich dabei nicht:

```text
Y     POSTEN
AIIN  WERT
AIN   ANTEIL
OR    EINHEIT
```

Die konkrete Wortwahl entsteht erst aus Stammkern, Register, Handlung und –
in wenigen Fällen – der gemeinsam geschriebenen Trägergruppe.

## Das aktuelle konkrete Nomenmodell

| Register | `Y` | `AIIN` | `AIN` | `OR` |
|---|---|---|---|---|
| Quelle | Arbeitsgut oder bei physischer Handlung Arbeitsmaterial | Arbeitsflüssigkeit; beim Festlegen Flüssigkeitsmenge | Teilmenge | Ansatz |
| Herbal | Pflanzenmaterial | Pflanzenauszug; beim Maßeinstellen Auszugsmenge | Pflanzenportion | Pflanzeneinheit, Arbeitseinheit oder Pflanzenansatz nach Handlung |
| Himmel | Ringposition | Positionswert | Sektoranteil | Ringsegment |
| Biological | Stationsansatz; nur im sauberen Bade-/Abkühlpacket Körper | Badfüllung oder Stationsmaß | Anwendungsportion; im exakten Körperpacket Teil | Badeinheit, Stationseinheit oder Beckeninhalt |
| Pharma | Drogenmaterial | Arzneiauszug; beim Maßeinstellen Dosismaß | Zutatenportion | Materialeinheit, Gefäßeinheit oder Arzneiansatz |

Das ist kein Wörterbuch mit Bedeutungen wie „Pflanzenmaterial zeitgebunden
beschaffen“. Der Zustand bleibt beim Verb. `Y=Pflanzenmaterial` kann daher in
„trockne das Pflanzenmaterial“, „zerreibe das Pflanzenmaterial“ und „weiche
das Pflanzenmaterial ein“ gleich bleiben.

Von den 1.243 Stellen behalten 632 ihre bisherige Basisform. 526 erhalten eine
engere Handlungsform und 85 liegen in einem kompositionell engeren Packet.
2.011 weitere `Y/AIIN/AIN/OR`-Stellen außerhalb dieser exakten
`T/SH/CHD/S`-Population bleiben unangetastet.

## Der eigentliche Fortschritt: Packets statt Nomenlisten

Einige alte Sätze waren nicht deshalb schlecht, weil ein einzelnes Nomen falsch
war, sondern weil drei Träger als drei gleichrangige Gegenstände ausgegeben
wurden.

### Ringpacket

G407-S047 vorher:

> Stelle die Ringposition, die Sektoreinheit und den Positionswert ein.

Jetzt:

> Stelle die Ringposition des Ringsegments auf den Positionswert ein.

`Y`, `OR` und `AIIN` bleiben drei getrennte Slots; nur ihre deutsche
syntaktische Beziehung wird ausgesprochen.

### Flusspacket

G407-S440 vorher:

> Leite die Becken- oder Körpereinheit und das Stations- oder Badmaß um.

Jetzt:

> Leite die angegebene Menge des Beckeninhalts um.

Bei einem zusätzlichen `Y` kann dasselbe feste Packet „… als Strom“ lauten.
Das ist einfacher und handlungsnäher als drei fast synonyme Stationsnomen.

### Körperteilpacket

G407-S621 vorher:

> Behandle die Anwendungsportion und den Stationsansatz.

Jetzt:

> Behandle den Körperteil.

Dabei liefert `Y` den Körper- und `AIN` den Teil-Atom. Keine der beiden Wurzeln
wird deshalb global „Körperteil“.

### Material und Prozess bleiben getrennt

G407-S696 lautet jetzt:

> Trockne das Pflanzenmaterial. Zerreibe das Pflanzenmaterial.

Und G407-S667:

> Weiche das Drogenmaterial ein. Seihe den Auszug aus der Zutatenportion ab.

Trockenheit, Zerkleinern, Einweichen und Abseihen liegen in den Verben; Material,
Auszug und Portion bleiben unterscheidbare Nomenrollen.

## Reality Check: „Körper“ wurde bewusst wieder eingeschränkt

Die erste Umsetzung machte jedes reine Biological-`Y` unter `SH_BIO_BATHE` zu
„Körper“. Das war zu grob. G407-S572 trägt am selben Host zusätzlich
„als neuer Bad- oder Stationsansatz“ und eine Arbeitsstellenangabe; G407-S115
trägt Ziel-, Quellen- und Leitungsrelationen. In beiden Sätzen kollidierte
„Körper“ mit der restlichen Packetstruktur.

Die endgültige Regel erlaubt die Körperlesung nur, wenn der Bade- oder
Abkühlhost außer Gradangaben keine Relation, Adresse, Form oder
Neuansatzmarkierung trägt. Dadurch bleiben beide negativen Fälle bytegleich zu
GDT586, während der klare G407-S151 sinnvoll lautet:

> Halte den Körper im Bad auf Grad II. Lass den Körper anschließend abkühlen.

Die Annahme wurde also nicht verworfen, sondern auf den Teil der Daten begrenzt,
in dem sie tatsächlich besser liest.

## Namen und laufende Träger bleiben getrennt

Keiner der 1.243 Trägerslots ist ein GDT585-Namensslot; auch die Governor-Keys
überlappen nicht. Nur eine lokale Karte enthält beides als getrennte Stellen:

> Nimm den Drogeneintrag »dunkle Faserwurzeldroge [cheo]« und das
> Drogenmaterial und stelle den Drogeneintrag »dunkle Faserwurzeldroge [cheo]«
> und das Drogenmaterial ein.

Damit wird weder `cheo` aus `Y` abgeleitet noch `Y` zur Faserwurzeldroge.
Die übrigen 88 namenstragenden Karten bleiben exakt auf ihrer GDT586-Lesung.
`Heilmittel` in G515-S050 wird am exakten laufenden `LOCAL_X` erneut eingesetzt;
`Beschwerde` in G515-S046 bleibt bytegleich erhalten.

## Vollständiger Leser

Von den 793 Aussagen ändern sich gegenüber GDT586 genau 227, von den 744 lokalen
Karten genau 14. Alle 414 nicht betroffenen Aussagen und 674 nicht betroffenen
Karten bleiben bytegleich. Die 379 Kandidatenaussagen werden trotzdem komplett
mit ihren unveränderten Governor-Gruppen neu aufgebaut, damit alle 384 entfernt
geschriebenen Träger korrekt an ihren Handlungskopf gelangen.

Der vollständige aktuelle Leser steht in
`artifacts/GDT587_COMPLETE_THIRTY_PAGE_READER.md`; die 25 manuell gelesenen
Passagen und Belastungsfälle in `artifacts/GDT587_MANUAL_PASSAGE_AUDIT.md`.
Alle 69 unabhängigen Prüfungen bestehen.

## Neue Arbeitsbasis

GDT587 ist jetzt die beste vollständige Arbeitslesung der dreißig zugelassenen
Seiten. Es ersetzt nicht die kurzen Stammkerne, sondern ergänzt sie um eine
vorhersagbare Einsetzregel:

```text
Trägerkern + Register + exakter Handlungskopf + geschriebene Packetpartner
→ konkretes deutsches Nomen und Satzform
```

Ein weiterer registerweiter Nomenpass über `OK/CH/K/R/P` wäre weitgehend eine
Wiederholung von GDT496/GDT567. Der nächste wirklich informative Schritt ist
daher der Transfer dieses festen Modells auf weitere ausdrücklich freigegebene
Seiten. Bis dahin wird keine neue Seite, Wurzel oder Substringanalyse geöffnet.

## Claim ceiling

Die 1.243 Formen sind occurrence-gebundene, austauschbare Arbeitslesungen. Weil
mehrere GDT584-Aktionsregeln selbst mit Hilfe dieser Trägerklassen gewählt
wurden, sind sie keine unabhängige Bestätigung. GDT587 bestätigt kein
Voynich-Wort, keinen Wortstamm, Klartext, Sprache, Stoff, Pflanzenteil,
Körperteil, Patienten, Heilvorgang, Rezept, Sternwert oder historisches
Codebuch.
