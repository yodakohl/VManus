# V52 R1 — Lehrbare Feldgrammatik ohne Prosarückprojektion

Status: begrenzte kreative Schreibwerkstatt-Arbeit, keine Entzifferung und
keine historische Wortidentifikation.

## Ergebnis

**Ja als Kopier- und Ankergrammatik; nein als deutsche Satzgrammatik.**

Alle 135 V49-Felder lassen sich mit sechs erschöpfenden, hierarchisch
angewandten Mustern erzeugen und rücklesen. Die Grammatik erhält jede exakte
Karte, jede Reihenfolge, jeden formalen Abschluss und jedes `UNKNOWN`. Sie
setzt aber keine Artikel, Objekte, Materialien, Ziele, Zeiten oder kausalen
Verknüpfungen ein. Deshalb erzeugt sie absichtlich **nicht** die flüssige lokale
V49-Prosa.

Die Belastungsgrenze ist deutlich:

| Schicht | Ereignisse | Anteil |
|---|---:|---:|
| formale Operatornamen `SETZEN`, `MARKIEREN`, `VERKNÜPFEN` | 57 | 15,0 % |
| schwache PAGE_HOST-Merker `AN`, `BEREITUNG`, `TEIL` | 22 | 5,8 % |
| ausgewählte unteilbare Ganzkarten-Merkwörter | 66 | 17,3 % |
| `UNKNOWN` | 236 | 61,9 % |
| **gesamt** | **381** | **100 %** |

Nur 17/135 Felder enthalten ausschließlich ausgewählte Werte; 66 sind
gemischt und 52 vollständig opak. Vollständige Abdeckung entsteht daher durch
verlustfreies Kopieren, nicht durch vollständige Übersetzung.

## Ausführbare Werkstattregel

Für jedes Feld arbeitet der Lehrling in genau dieser Reihenfolge:

1. Kopiere die belegten ganzen Karten in physischer Reihenfolge. Eine sichtbare
   Form wird niemals zerlegt.
2. Weise einer Karte zuerst ihre ausgewählte **unteilbare Ganzkartenhilfe** zu;
   andernfalls ihren ausgewählten PAGE_HOST- oder formalen Operatornamen;
   andernfalls `UNKNOWN`.
3. Behalte zwischen allen Ereignissen einen sichtbaren Trenner. `UNKNOWN`
   darf weder gelöscht noch von benachbarten Wörtern übersprungen werden.
4. Ein formales `<ARG_*>` gehört nur zu seiner eigenen exakten Karte. Die
   nächste Karte wird nie still zum deutschen Objekt des Operators.
5. Endet die letzte formale Karte in `CLOSE(...)` oder `CLOSE_B3(...)`, markiere
   nur das formale Feldende. Das bedeutet nicht Ende der Zeile, des Datensatzes
   oder eines historischen Vorgangs.
6. Lies die resultierende Folge wörtlich als Merkkette zurück. Die lokale
   kreative Prosa darf separat danebenstehen, aber keine Lücke der Merkkette
   füllen.

In Kurzform:

```text
FELD := KARTE (TRENNER KARTE)*
KARTE := GANZKARTEN_MERKWORT | PAGE_HOST_MERKER | FORMALER_OPERATOR | UNKNOWN
TRENNER := "|"
FELDSCHLUSS := CLOSE*-Eigenschaft der letzten KARTE, keine zusätzliche Karte
```

Dies ist eine Abschreib- und Kontrollregel, keine Behauptung über Syntax oder
Wortstellung.

## Die sechs Feldmuster

Die Muster werden in der folgenden Reihenfolge getestet und sind dadurch
nicht überlappend.

| Muster | Klassifikator | Felder | Ereignisse | ausgewählt | UNKNOWN |
|---|---|---:|---:|---:|---:|
| P1 `TERMINAL_CLOSE` | letzte formale Karte ist `CLOSE*` | 90 | 203 | 71 | 132 |
| P2 `OPEN_OPERATOR_ENTRY` | offen; erstes Ereignis ist ausgewählter formaler Operator | 9 | 34 | 19 | 15 |
| P3 `OPEN_OPERATOR_INTERNAL` | offen; formaler Operator erst nach Position 1 | 13 | 65 | 30 | 35 |
| P4 `OPEN_MNEMONIC_CHAIN` | offen; kein formaler Operator; mindestens zwei ausgewählte Merker | 7 | 40 | 17 | 23 |
| P5 `OPEN_SINGLE_ANCHOR` | offen; kein formaler Operator; genau ein ausgewählter Merker | 8 | 23 | 8 | 15 |
| P6 `OPEN_OPAQUE` | offen; kein ausgewählter Merker | 8 | 16 | 0 | 16 |
| **gesamt** |  | **135** | **381** | **145** | **236** |

P1 erhält Vorrang, weil die Feldgrenze die stärkste echte Regel ist. Unter
den 90 geschlossenen Feldern sind 44 vollständig opak, 28 tragen einen, 13
zwei, 3 drei und 2 vier ausgewählte Werte. `CLOSE` behauptet also keine
semantische Vollständigkeit.

## Je zwei vollständige Beispiele

### P1 `TERMINAL_CLOSE`

**Beispiel 1: `f55v`, Datensatz 1, `f55v.5`, Feld 1**

```text
Oberfläche: qokaiin chaiin ykain ykan ody
Formal:      SET(<ARG_AIIN>) | UNKNOWN_HOST[AIIN] | UNKNOWN_HOST[YK] + <ARG_AIN> | UNKNOWN_HOST[YKAN] | CLOSE(UNKNOWN_HOST[O])
R1-Folge:    SETZEN | MASS | UNKNOWN | UNKNOWN | UNKNOWN
V49-Prosa:   beginne den nächsten abgemessenen Posten ; Ein vorgeschriebenes Maß ; koche das breite Blatt sanft ; in Weißwein ; lasse es ziehen, bis die Flüssigkeit klar ist
```

**Beispiel 2: `f83r`, Datensatz 1, `f83r.20`, Feld 3**

```text
Oberfläche: qokeey qokedy
Formal:      UNKNOWN_HOST[OKEEY] | CLOSE(UNKNOWN_HOST[OKE])
R1-Folge:    WARM | SPÜLEN
V49-Prosa:   temperiere die Arbeitsflüssigkeit und halte sie lauwarm ; spüle die bezeichnete Stelle einmal und beende den Schritt
```

Lehrsatz: Der letzte formale Schluss beendet das Feld. Er verwandelt die
vorhergehenden Merker nicht in einen Satz und liefert kein deutsches *dann*.

### P2 `OPEN_OPERATOR_ENTRY`

**Beispiel 1: `f81v`, Datensatz 1, `f81v.2`, Feld 2**

```text
Oberfläche: okaiin kair okal sar ol kain olkain al ol rol dl
Formal:      SET(<ARG_AIIN>) | UNKNOWN_HOST[K] + <ARG_AIR> | SET(<ARG_AL>) | UNKNOWN_HOST[AR] | FRAME_O(LINK) | UNKNOWN_HOST[K] + <ARG_AIN> | UNKNOWN_HOST[OLK] + <ARG_AIN> | UNKNOWN_HOST[AL] | FRAME_O(LINK) | UNKNOWN_HOST[ROL] | LINK
R1-Folge:    SETZEN | UNKNOWN | SETZEN | UNKNOWN | VERKNÜPFEN | UNKNOWN | UNKNOWN | AN | VERKNÜPFEN | UNKNOWN | VERKNÜPFEN
V49-Prosa:   beginne den nächsten abgemessenen Posten ; der zurücklaufende Strom ; mische beide Anteile zusammen ; Daraus, aus demselben Ansatz ; Mit der vorigen Zubereitung weiter ; ein abgemessener Anteil ; das untere Becken ; An die bezeichnete Zielstelle führen ; Mit der vorigen Zubereitung weiter ; bevor es abkühlt ; das bereitete Öl
```

**Beispiel 2: `f81v`, Datensatz 1, `f81v.17`, Feld 4**

```text
Oberfläche: qokain shckhy dl ral
Formal:      SET(<ARG_AIN>) | UNKNOWN_HOST[CKHY] | LINK | UNKNOWN_HOST[R] + <ARG_AL>
R1-Folge:    SETZEN | UNKNOWN | VERKNÜPFEN | UNKNOWN
V49-Prosa:   gib einen abgemessenen Anteil in das Gefäß ; durch die verbundenen Läufe ; das bereitete Öl ; und lasse es abkühlen
```

Lehrsatz: Der Eingangsoperator ordnet nur seine eigene Karte. Er regiert nicht
die restlichen Feldereignisse.

### P3 `OPEN_OPERATOR_INTERNAL`

**Beispiel 1: `f10r`, Datensatz 1, `f10r.5`, Feld 1**

```text
Oberfläche: qokchy qotchol chol cthy
Formal:      UNKNOWN_HOST[OKCHY] | FRAME_OT(UNKNOWN_HOST[CHOL]) | FRAME_O(LINK) | UNKNOWN_HOST[CTHY]
R1-Folge:    UNKNOWN | UNKNOWN | VERKNÜPFEN | BEREIT
V49-Prosa:   gebrauche die frisch bereitete Arznei ; wende sie warm an ; Mit der vorigen Zubereitung weiter ; Sobald die Zubereitung gebrauchsfertig ist
```

**Beispiel 2: `f55v`, Datensatz 1, `f55v.11`, Feld 2**

```text
Oberfläche: aiin okal oltchy or y orain
Formal:      UNKNOWN_HOST[AIIN] | SET(<ARG_AL>) | UNKNOWN_HOST[OLTCHY] | UNKNOWN_HOST[OR] | UNKNOWN_HOST[Y] | UNKNOWN_HOST[OR] + <ARG_AIN>
R1-Folge:    MASS | SETZEN | UNKNOWN | BEREITUNG | UNKNOWN | BEREITUNG
V49-Prosa:   Ein vorgeschriebenes Maß ; mische beide Anteile zusammen ; bewahre es in einem bedeckten Gefäß ; Die bereitete Arbeitsflüssigkeit ; Diese aktive Portion ; gebrauche die fertige Flüssigkeit frisch
```

Lehrsatz: Ein interner Operator öffnet keinen deutschen Teilsatz. Vor- und
Nachbarn bleiben selbstständige Karten.

### P4 `OPEN_MNEMONIC_CHAIN`

**Beispiel 1: `f10r`, Datensatz 1, `f10r.2`, Feld 1**

```text
Oberfläche: dchey cthoor char chty os chair otytchol oky daiin etyd
Formal:      UNKNOWN_HOST[CHEY] | UNKNOWN_HOST[CTHOOR] | UNKNOWN_HOST[AR] | UNKNOWN_HOST[TY] | UNKNOWN_HOST[OS] | UNKNOWN_HOST[AIR] | UNKNOWN_HOST[OTYTCHOL] | UNKNOWN_HOST[OKY] | UNKNOWN_HOST[AIIN] | UNKNOWN_HOST[ETYD]
R1-Folge:    TEIL | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | VERWENDEN | MASS | UNKNOWN
V49-Prosa:   Nimm die faserige untere Wurzel ; wasche sie in fließendem Wasser ; Daraus, aus demselben Ansatz ; Gleichmäßig bearbeiten ; zerstoße sie zu grobem Pulver ; gib Rotwein hinzu ; trinke es bei Magenschmerz ; Die aktive Portion verwenden ; Ein vorgeschriebenes Maß ; bewahre die übrige Wurzel trocken auf
```

**Beispiel 2: `f56r`, Datensatz 1, `f56r.7`, Feld 1**

```text
Oberfläche: sho kchol otchor choky dal
Formal:      UNKNOWN_HOST[O] | UNKNOWN_HOST[KCHOL] | FRAME_OT(UNKNOWN_HOST[CHOR]) | UNKNOWN_HOST[OKY] | UNKNOWN_HOST[AL]
R1-Folge:    UNKNOWN | UNKNOWN | UNKNOWN | VERWENDEN | AN
V49-Prosa:   nimm danach den folgenden Zusatz oder Pflanzenteil ; lasse es in Weißwein ziehen ; vor der Blüte gesammelt ; Die aktive Portion verwenden ; An die bezeichnete Zielstelle führen
```

Lehrsatz: Mehrere Merker werden nur in Quellreihenfolge nebeneinandergestellt.
`VERWENDEN | AN` ist keine deutsche Phrase mit einem stillen Ziel.

### P5 `OPEN_SINGLE_ANCHOR`

**Beispiel 1: `f11r`, Datensatz 1, `f11r.4`, Feld 1**

```text
Oberfläche: dchol chy kchy dy daiin
Formal:      UNKNOWN_HOST[CHOL] | UNKNOWN_HOST[Y] | UNKNOWN_HOST[KCHY] | UNKNOWN_HOST[Y] | UNKNOWN_HOST[AIIN]
R1-Folge:    UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | MASS
V49-Prosa:   von diesem abgebildeten Simplex ; Diese aktive Portion ; binde es auf die geschwollene Stelle ; Diese aktive Portion ; Ein vorgeschriebenes Maß
```

**Beispiel 2: `f81v`, Datensatz 1, `f81v.18`, Feld 5**

```text
Oberfläche: chckhy qoky
Formal:      UNKNOWN_HOST[CKHY] | UNKNOWN_HOST[OKY]
R1-Folge:    UNKNOWN | VERWENDEN
V49-Prosa:   durch die verbundenen Läufe ; Die aktive Portion verwenden
```

Lehrsatz: Ein einzelner Anker benennt weder Feldtyp noch die unbekannten
Nachbarn. Er bleibt genau an seiner Kartenposition.

### P6 `OPEN_OPAQUE`

**Beispiel 1: `f56r`, Datensatz 1, `f56r.12`, Feld 1**

```text
Oberfläche: sh cho kchey qokokchy
Formal:      UNKNOWN_HOST[H] | UNKNOWN_HOST[O] | UNKNOWN_HOST[KCHEY] | UNKNOWN_HOST[OKOKCHY]
R1-Folge:    UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN
V49-Prosa:   ihren kleinen Samen- oder Knospenkopf ; nimm danach den folgenden Zusatz oder Pflanzenteil ; das getrocknete schmale Blatt ; trockne es im Schatten
```

**Beispiel 2: `f11r`, Datensatz 1, `f11r.1`, Feld 2**

```text
Oberfläche: shoyty
Formal:      UNKNOWN_HOST[OYTY]
R1-Folge:    UNKNOWN
V49-Prosa:   behalte die Blütenkrone zurück
```

Lehrsatz: Ein opakes Feld wird vollständig abgeschrieben und als `UNKNOWN`
zurückgelesen. Seine lokale Prosa ist keine Ausgabe der Grammatik.

## Widerspruchsledger

Alle beobachteten Widerspruchstypen werden bewahrt; keiner wird durch flüssige
Ergänzungen versteckt.

| Typ | Befund | Werkstattfolge |
|---|---|---|
| Deckungslücke | 236/381 Ereignisse sind `UNKNOWN`; 52/135 Felder sind ganz opak | Kopieren, nicht erraten |
| Zurückgezogene Anker | 14 ehemalige E- und 4 CKHY-Ereignisse werden in 18 Feldern jetzt `UNKNOWN` | `BIS` und `VERBINDUNG` nicht in die Feldfolge retten |
| Unbekannte Zwischenräume | In 23 Feldern liegt mindestens ein `UNKNOWN` zwischen zwei ausgewählten Werten | bekannte Enden nicht zu einer Phrase zusammenziehen |
| Operatorskopus | 10 Felder tragen mehrere formale Operatoren; in 16 Feldern steht ein Operator direkt neben einem weiteren ausgewählten Wert | nur das karteneigene formale Argument binden |
| Offener Bezug | 46 Vorkommen von `MARKIEREN`, `VERKNÜPFEN`, `AN` oder `ZUVOR` liegen in 37 Feldern | kein Ziel und keinen Referenten aus Nachbarprosa einsetzen |
| Wiederholung | 7 Felder wiederholen mindestens einen ausgewählten Wert; darunter `SETZEN`, `VERKNÜPFEN`, `MASS` und `BEREITUNG` | jede Karte einzeln bewahren, nicht zusammenziehen |
| Positionswechsel | 13/14 ausgewählte Werte belegen mindestens zwei Feldpositionstypen; nur `TEIL` steht in 3/3 Fällen am Anfang | keine allgemeine deutsche Satzposition ableiten |
| Schlussreichweite | 90/90 `CLOSE*`-Ereignisse sind feldfinal, aber 78 dieser Felder werden im selben Locus von einem weiteren Feld gefolgt | `CLOSE` beendet das Feld, nicht Zeile oder Vorgang |
| Geschlossene Ganzkarten | Alle 8 LCHE- und 8 OKE-Ereignisse tragen bereits `CLOSE`; offene Gegenformen fehlen | `ABLASSEN` und `SPÜLEN` nur als Ganzkartenmerker lehren |
| Prosagröße | Alle 145 ausgewählten Ereignisse haben mehrwortige lokale Defaults | niemals die Zusatzwörter in Atom oder Ganzkarte zurückprojizieren |

Die sieben Felder mit wiederholtem ausgewähltem Wert sind konkret:

```text
f10r.8/1   VERKNÜPFEN ×2
f10r.9/1   BEREITUNG ×2
f55v.11/2  BEREITUNG ×2
f81v.2/2   SETZEN ×2, VERKNÜPFEN ×3
f81v.7/1   MASS ×2
f81v.18/2  VERKNÜPFEN ×2
f82r.19/1  SETZEN ×2
```

## Reparaturentscheidung

Es gibt **keine erzwungene lokale Prosareparatur**. Die Reparaturdatei enthält
daher nur die Kopfzeile.

Das ist keine Schonung der V49-Prosa, sondern die Folge der Schichtentrennung:

- `E=UNKNOWN` und `CKHY=UNKNOWN` entziehen alten lokalen Sätzen atomare
  Stützung, widersprechen ihnen aber nicht logisch.
- `WARM` ist mit dem lokal engeren *lauwarm* vereinbar.
- `KLAR`, `VERWENDEN`, `ABLASSEN`, `SPÜLEN`, `BEREIT` und `ZUVOR` sind mit den
  zugehörigen lokalen Erweiterungen vereinbar, ohne sie zu enthalten.
- Ein feldfinales `CLOSE` passt zu „beende den Schritt“; die 78 folgenden Felder
  zeigen lediglich, dass damit nicht der ganze Locus endet.

Eine lokale Lesung würde erst dann geändert, wenn ein ausgewählter Wert ihr
positiv widerspricht. Ein fehlender oder schwacher Wert genügt dafür nicht.

## Lehrlingsprüfung

Ein Lehrling besteht, wenn er bei jedem der 135 Felder:

1. Ereigniszahl, Oberflächenfolge und Feldgrenze unverändert reproduziert;
2. genau die ausgewählten 145 Merker nennt und alle 236 anderen Ereignisse als
   `UNKNOWN` stehen lässt;
3. keinen unbekannten Zwischenraum überspringt;
4. kein karteneigenes `<ARG_*>` auf eine Nachbarkarte ausdehnt;
5. `CLOSE` nur als formalen Feldschluss rückliest;
6. aus der Merkkette keine flüssige deutsche Handlungsanweisung erfindet.

Der Audit bestätigt für alle 135 Felder gleiche Längen von Oberflächenfolge,
formaler Folge, atomarer Folge und lokaler Ereignisfolge. Die sechs Muster
klassifizieren 135/135 Felder und 381/381 Ereignisse.

## Schluss

V52-R1 liefert eine kleine, praktisch lehrbare Feldgrammatik mit vollständiger
formaler Abdeckung. Ihre wissenschaftlich wichtige Leistung ist gerade die
Begrenzung: Sie zeigt, wo kopiert, wo ein schwaches Merkwort gesprochen und wo
geschwiegen werden muss. Sie liefert keine vollständige Feldübersetzung und
keine deutsche Syntax.
