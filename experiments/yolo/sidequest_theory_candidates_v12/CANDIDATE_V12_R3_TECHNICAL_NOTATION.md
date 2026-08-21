# V12 R3 — Technischer Register- und Notationsschreiber

Datum: 2026-08-21

Rolle: **Technischer Register-, Rechen- und Notationsschreiber um 1420**.

Status: unabhängiger V12-Kandidat; spekulative Seitentheorie, kein GDT-Ergebnis
und keine Übersetzung.

## Entscheidung

**Gewinner: `NOT_DISTINGUISHABLE_WITH_TWO_OCCURRENCES`.**

Der positive Mindestbefund lautet nur:

```text
Y — AIIN — Y = eine echte, wiederkehrende, opake Drei-Karten-Formel
```

Die Formel ist auf den sieben festen Prosaseiten die einzige exakte
Drei-Karten-Folge, die zweimal und auf zwei Seiten vorkommt. Sie überlebt stark
verschiedene sichtbare Wrapper und ist deshalb kein bloßer Renderer-Effekt.
Aber die zwei Belege unterscheiden **nicht**, ob die Formel einen aktiven Wert
wieder aufnimmt, zwei Endpunkte verbindet, einen abstrakten Formularplatz
aufruft oder einfach eine feste Wendung der abgekürzten Fachprosa ist.

`PAIRED_EQUAL_VALUE` wird verworfen: In keinem Beleg sind zwei selbständig
erkennbare, symmetrische Operanden vorhanden. Gleiche äußere Karten beweisen
nur gleiche formale Kartenidentität, nicht gleiche Mengen oder Zustände.

## Grenzen und Arbeitsweise

- Zugelassen waren nur `f10r`, `f11r`, `f55v`, `f56r`, `f81v`, `f82r` und
  `f83r` für die Prosa-Prüfung.
- `f84` und `f84r` wurden nicht geöffnet, geparst, angezeigt, verbunden oder
  bewertet.
- Gemischte TSV-Quellen wurden ausschließlich mit `./vmanus-exp query-tsv`,
  expliziten Seiten-Allow-Werten, expliziten Ausgabespalten und
  `--forbid-prefix f84` gelesen. Beide Abfragen meldeten 381 zugelassene und
  null verbotene Zeilen.
- Y (`b921a237be883a820352`) und AIIN (`2f1c5e56e8f0ff459065`) werden als
  opake Karten behandelt. Sichtbare Teilfolgen, Lautwerte und vermeintliche
  Wortbestandteile wurden nicht ausgewertet.
- Kein anderer V12-Kandidatenbericht wurde gelesen.

## Die beiden vollständigen Zielzeilen

`|` bezeichnet eine im Quellinventar getrennte physische Feldscheibe;
`{DY}` bezeichnet eine an der Karte befestigte DY-Schließung. Die Umschrift
ist nur ein Oberflächen-Audit, nicht die Grundlage der Kartenidentität.

```text
f10r.6, Herbal-A, record 2, ein offenes Feld:
ycheor cthy chor cthaiin qoctholy dy chy taiin shy
                                  ^  ^^^ ^^^^^ ^^^
                                  Y   Y  AIIN   Y
```

Die exakte Zielformel beginnt bei Gruppe 7. Gruppe 6 ist eine zusätzliche
exakte Y-Karte. Das sichtbare `cthaiin` in Gruppe 4 ist eine andere ganze Karte
und wird nicht durch Teilzeichen-Mining zu AIIN gemacht.

```text
f83r.3, Biological-B, record 1:
olkeedy{DY} | qotal chkeedy{DY} | chey daiin chey lchedy{DY} | qokaiin qotal dar
                                      Y   AIIN  Y   LCHE-COMMIT
```

Hier steht die Formel am Kopf des dritten Feldes, unmittelbar nach einem
bereits geschlossenen Feld, und wird selbst durch eine weitere opake
payload-tragende Karte mit DY geschlossen.

## Vollständige Absatzrecords

### f10r, record 2 — 24 Karten auf drei physischen Zeilen

```text
f10r.6  ycheor cthy chor cthaiin qoctholy dy chy taiin shy
f10r.8  qotchor chor otol chol cholor chol daiin dar
f10r.9  oykchor shor chor chy kaiiin dy chodaiin
```

Jede Zeile besitzt eine offene Feldscheibe; in diesem Record gibt es keine
angehängte DY/B3-Schließung. Nach der Zielkarte endet die physische Zeile, der
Absatz läuft jedoch über zwei weitere Zeilen weiter.

### f83r, record 1 — 86 Karten auf zehn physischen Zeilen

```text
f83r.3   olkeedy{DY} | qotal chkeedy{DY} | chey daiin chey lchedy{DY} | qokaiin qotal dar
f83r.6   schedy{DY} | chedchy qokal olchedy{DY} | qokaiin chedy qokeedy{DY} | lchedy{DY} | qoky
f83r.8   pchedal otedy{DY} | shecthedchy qoky chedy chary
f83r.11  sor shedy{DY} | qokaiin chkain shcthey qokedy{DY} | okair sheedy{DY} | lchedy{DY} | lo
f83r.14  qokchedy{DY} | qokeedy{DY} | shedy{DY} | qokshedy{DY} | dal lchedy{DY} | qokaiin shcthy dal sy
f83r.15  saiin shedal shecthy chey tal shcthy dalchdy{DY} | qotchedy{DY} | lchedy{DY}
f83r.16  tchedy{DY} | qokchdy{DY} | cheedar chldaiin chedy qokain checthy chealror
f83r.20  solkeedy{DY} | qoteedy{DY} | qokeey qokedy{DY} | sol cheeety qokedy{DY} | qoky saiin
f83r.22  schedair otchedy{DY} | qokeedy{DY} | chedain chedy qotedaiin otaiin otedy{DY} | ldy{DY}
f83r.24  soiiin checthy chety otaiin olsaly shedy{DY}
```

Die Zielformel ist also kein ganzer Absatz und keine ganze Zeile. Sie belegt
den Anfang einer kurzen, lokal geschlossenen Bio-Zelle innerhalb eines langen
Records.

## Vollinventar von Y und AIIN

Gesamt: Y 18-mal auf sechs Seiten; AIIN 20-mal auf allen sieben Seiten.

| Seite | Y | AIIN |
|---|---:|---:|
| f10r | 5 | 3 |
| f11r | 3 | 1 |
| f55v | 1 | 3 |
| f56r | 0 | 2 |
| f81v | 1 | 2 |
| f82r | 2 | 2 |
| f83r | 6 | 7 |

Positionsprofil:

| Karte | FIRST | MIDDLE | LAST | physischer Zeilenanfang | nach DY |
|---|---:|---:|---:|---:|---:|
| Y | 2 | 13 | 3 | 0 | 2 |
| AIIN | 6 | 9 | 5 | 4 | 2 |

AIIN ist in allen drei Feldpositionen beweglich. Y ist überwiegend intern,
aber weder an einen Feldkopf noch an einen Abschluss gebunden. Von 15
Y-Vorkommen mit einem folgenden Kartenslot stehen nur drei unmittelbar vor
einer angehängten Schließung. Bei AIIN sind es null von 15. Eine schmale
Lesung als obligatorischer infixer Mengenoperator passt deshalb nicht zum
Gesamtinventar.

### Jedes einzelne Vorkommen mit unmittelbarer Oberfläche

`<LINE>` bedeutet physische Zeilengrenze. Sternchen markieren die sechs
Karten der beiden Zielformeln; das zusätzliche f10r.6-Y in Gruppe 6 ist nicht
Bestandteil des wiederkehrenden Tripels.

| Karte | locus:g | Feldposition | links | Oberfläche | rechts |
|---|---|---|---|---|---|
| AIIN | f10r.2:9/10 | MIDDLE | oky | daiin | etyd |
| Y | f10r.6:6/9 | MIDDLE | qoctholy | dy | chy |
| Y | f10r.6:7/9* | MIDDLE | dy | chy | taiin |
| AIIN | f10r.6:8/9* | MIDDLE | chy | taiin | shy |
| Y | f10r.6:9/9* | LAST | taiin | shy | `<LINE>` |
| AIIN | f10r.8:7/8 | MIDDLE | chol | daiin | dar |
| Y | f10r.9:4/7 | MIDDLE | chor | chy | kaiiin |
| Y | f10r.9:6/7 | MIDDLE | kaiiin | dy | chodaiin |
| Y | f11r.4:2/5 | MIDDLE | dchol | chy | kchy |
| Y | f11r.4:4/5 | MIDDLE | kchy | dy | daiin |
| AIIN | f11r.4:5/5 | LAST | dy | daiin | `<LINE>` |
| Y | f11r.7:4/4 | LAST | cthy | dy | `<LINE>` |
| AIIN | f55v.5:2/8 | MIDDLE | qokaiin | chaiin | ykain |
| AIIN | f55v.5:6/8 | FIRST | ody | daiin | chedy |
| AIIN | f55v.11:5/10 | FIRST | oldy | aiin | okal |
| Y | f55v.11:9/10 | MIDDLE | or | y | orain |
| AIIN | f56r.5:4/4 | LAST | chodaly | daiin | `<LINE>` |
| AIIN | f56r.19:3/3 | LAST | keol | daiin | `<LINE>` |
| AIIN | f81v.7:4/9 | MIDDLE | sheckhal | daiin | qokeedal |
| AIIN | f81v.7:6/9 | MIDDLE | qokeedal | daiin | chckhy |
| Y | f81v.18:2/10 | FIRST | qokchdy | chey | ol |
| Y | f82r.2:4/8 | MIDDLE | qokain | dy | qokeedy |
| AIIN | f82r.23:5/9 | MIDDLE | lcheey | daiin | chey |
| Y | f82r.23:6/9 | MIDDLE | daiin | chey | qokeeedy |
| AIIN | f82r.26:6/9 | MIDDLE | ches | aiin | oteey |
| Y | f83r.3:4/10* | FIRST | chkeedy | chey | daiin |
| AIIN | f83r.3:5/10* | MIDDLE | chey | daiin | chey |
| Y | f83r.3:6/10* | MIDDLE | daiin | chey | lchedy |
| Y | f83r.14:10/10 | LAST | dal | sy | `<LINE>` |
| AIIN | f83r.15:1/9 | FIRST | `<LINE>` | saiin | shedal |
| Y | f83r.15:4/9 | MIDDLE | shecthy | chey | tal |
| AIIN | f83r.20:9/9 | LAST | qoky | saiin | `<LINE>` |
| AIIN | f83r.28:1/6 | FIRST | `<LINE>` | saiin | cheeky |
| AIIN | f83r.35:1/5 | FIRST | `<LINE>` | saiin | cheky |
| Y | f83r.38:2/4 | MIDDLE | or | chey | qockhey |
| AIIN | f83r.48:5/5 | LAST | chdal | aiin | `<LINE>` |
| AIIN | f83r.54:1/5 | FIRST | `<LINE>` | daiin | ol |
| Y | f83r.54:4/5 | MIDDLE | dain | chey | ldalor |

Die beiden Einzelpaare sind ebenfalls nicht exklusiv: Y→AIIN kommt dreimal
vor (`f10r.6`, `f11r.4`, `f83r.3`), AIIN→Y ebenfalls dreimal (`f10r.6`,
`f82r.23`, `f83r.3`). Erst die Überlappung zum ganzen ABA-Tripel wiederholt
sich zweimal.

## Antezedenten, Operanden und Folgen

| Frage | f10r.6 | f83r.3 | Ergebnis |
|---|---|---|---|
| unmittelbarer Vorgänger | zusätzliches Y in derselben offenen Feldscheibe | opake `chkeedy`-Karte mit DY, Ende des vorigen Feldes | nicht derselbe Typ von Antezedent |
| weitere Kandidaten davor | fünf opake Karten derselben Zeile; ein AIIN liegt nur im vorigen Absatzrecord | zwei zuvor geschlossene Felder im selben Record | kein eindeutig aktiver Wert |
| linker äußerer Y-Platz | intern, nach einem weiteren Y | FIRST im dritten Feld | nicht dieselbe Position |
| rechter äußerer Y-Platz | LAST und physisches Zeilenende | MIDDLE, danach LCHE+DY | nicht dieselbe Position |
| unmittelbare Folge | keine Karte; offener Absatz läuft später weiter | opake LCHE-Karte mit DY schließt die Zelle | keine gemeinsame Folgehandlung |
| zwei unabhängige Operanden | nicht sichtbar; zusätzliche Y-Karte verschärft die Zählambiguität | nicht sichtbar; nur Reihenfolge links/rechts | nicht belegt |
| symmetrische Operanden | nein | nein; Feldkopf und Vor-Schließungsplatz sind asymmetrisch | Gleichheitslesung fällt |

Ein technischer Schreiber könnte fehlende Operanden aus Bild oder
Werkstattformular ergänzen. Das macht die Modelle historisch möglich, liefert
aber gerade **keine unabhängige Beobachtung**, mit der eines von ihnen gewählt
werden könnte.

## Formel- und Renderer-Kontrollen

### Gematchte Formeln

Auf den 381 Karten der sieben Seiten gibt es 267 vollständige, innerhalb einer
physischen Zeile liegende Drei-Karten-Fenster. Davon sind 266 verschiedene
exakte Tripeltypen. Nur ein Tripeltyp wiederholt sich:

```text
b921a237... — 2f1c5e56... — b921a237...
Y            AIIN          Y
```

Sieben verschiedene ABA-Typen kommen insgesamt vor. Sechs sind Einzelfälle;
nur Y–AIIN–Y steht auf zwei Seiten. Das stützt eine kopierte Formel, aber
nicht deren Bedeutung. Die Auswahl der Zielkonstruktion erfolgte nach Sichtung
dieses auffälligen Wiederholers; die bloße Seltenheit ist daher kein
vorregistrierter semantischer Test.

### Position

```text
f10r: Feld 1, MIDDLE — MIDDLE — LAST, danach Zeilenende
f83r: Feld 3, FIRST  — MIDDLE — MIDDLE, danach payload+DY
```

Damit scheitert ein fester physischer Checklistenslot. Ein abstrakter,
layoutunabhängiger Slot bleibt möglich, ist ohne extern bekannte Schablone
aber nicht von einer mobilen Formel zu unterscheiden.

### Wrapper und Renderer

Die sichtbaren Realisierungen sind:

```text
f10r: chy   taiin shy    = ch-Y  t-AIIN sh-Y
f83r: chey  daiin chey   = che-Y d-AIIN che-Y
```

Im Gesamtinventar besitzt Y sechs beobachtete Wrapperklassen
(`che` 7, `d` 5, `ch` 3, `sh` 1, `s` 1, NONE 1), AIIN fünf
(`d` 11, `s` 4, NONE 3, `t` 1, `ch` 1). Die f83r-Symmetrie der beiden
`che`-Wrapper wiederholt sich auf f10r gerade nicht und kann deshalb kein
Gleichheitszeichen sein.

Alle sechs Zielereignisse sind `EXECUTABLE_POWERED_CELL`. Ihre beobachteten
Wrapperwahrscheinlichkeiten im eingefrorenen Renderer sind:

| Beleg | Karte | Wrapper | P(Wrapper) | Überraschungsbits |
|---|---|---|---:|---:|
| f10r.6:g7 | Y | ch | .179654 | 2.476710 |
| f10r.6:g8 | AIIN | t | .037585 | 4.733683 |
| f10r.6:g9 | Y | sh | .101732 | 3.297160 |
| f83r.3:g4 | Y | che | .351718 | 1.507511 |
| f83r.3:g5 | AIIN | d | .568337 | .815181 |
| f83r.3:g6 | Y | che | .352814 | 1.503021 |

Der f10r-`t`-Wrapper ist selten, aber als bekannte Realisierung lizenziert.
Das exakte Kartentripel bleibt trotz der Oberflächenabweichung bestehen.
`RENDERER_OR_SEGMENTATION_ARTIFACT` wird deshalb verworfen: Der Renderer
erzeugt die Wrapper, nicht die dreifache Kartenidentität; beide Belege besitzen
drei getrennte Quellgruppen in einem Feld.

## Fünf ausführbare Schreib- und Lesemodelle

Die Regeln setzen nur Dinge voraus, die ein Schreiber um 1420 mit Musterblatt,
laufender Zeile und Gedächtnis ausführen könnte. Buchstabenrechnung,
Wahrscheinlichkeiten oder moderne Algebra sind kein Bestandteil der Regeln.

### 1. `SHARED_ACTIVE_REFERENCE`

**Schreibregel:** Der Meister kennzeichnet im laufenden Record zuerst einen
Standard — etwa Maß, Grad, Dauer, Stufe oder Einstellung. Solange dieser
Standard gilt, schreibt der Schreiber für zwei lokale Merkplätze nacheinander
Y, AIIN, Y. Wrapper werden erst beim Einpassen in die Zeile gewählt.

**Beispielbuchung:** „Standard des vorigen Kästchens beibehalten; linker und
rechter Merkplatz folgen ihm“ → `Y AIIN Y`.

**Kontrollierte Rücklesung:** Nur „zwei anonyme Merkplätze berufen sich auf
einen zuvor gesetzten Standard“. Der Inhalt des Standards bleibt unbekannt.

**Scheitert, wenn:** kein eindeutiger früherer Standard vorhanden ist; zwei
mögliche Vorgänger konkurrieren; nur einer der Merkplätze eine passende Folge
hat; oder ein Vorkommen einen neuen Standard eröffnet. Genau die ersten beiden
Probleme liegen hier vor. Das Modell ist möglich, aber nicht entschieden.

### 2. `PAIRED_EQUAL_VALUE`

**Schreibregel:** Zwei vorher bekannte, verschiedene Einträge stehen als Paar.
Für jeden wird ein Y-Platz geschrieben; AIIN dazwischen befiehlt, beiden
dasselbe Maß oder denselben Zustand zuzuteilen.

**Beispielbuchung:** „linker Bestandteil und rechter Bestandteil, von gleicher
zugeteilter Stufe“ → `Y AIIN Y`.

**Kontrollierte Rücklesung:** „Der linke und der rechte selbständig bekannte
Operand erhalten denselben Wert.“

**Scheitert, wenn:** die zwei Operanden nicht unabhängig erkennbar sind, ihre
Rollen asymmetrisch sind, mehr als zwei Y-Plätze konkurrieren oder kein Wert
identifiziert werden kann. f10r besitzt unmittelbar drei Y-Karten; f83r hat
einen Feldkopf- und einen Vor-Schließungsplatz. Beide Belege scheitern am
eingefrorenen Symmetrieerfordernis. **Verworfen.**

### 3. `DYADIC_RELATION_FRAME`

**Schreibregel:** Das Bild, die Spalten oder der vorherige Text liefern zwei
Endpunkte. Der Schreiber setzt für den ersten Y, dann die erlernte
Relationskarte AIIN, dann für den zweiten Y. Die Relation muss keine Gleichheit
sein.

**Beispielbuchung:** „erster Anschluss — vorgeschriebene Beziehung — zweiter
Anschluss“ → `Y AIIN Y`.

**Kontrollierte Rücklesung:** „zwei geordnete, aber unbenannte Endpunkte stehen
in der AIIN-Beziehung.“ Kein *mit*, *gleich*, *zu* oder anderes Wort darf
eingesetzt werden.

**Scheitert, wenn:** keine zwei Endpunkte außerhalb der Formel identifiziert
werden können, die äußeren Plätze nur Formelrahmen sind oder ein dritter
gleichartiger Platz nicht zugeordnet werden kann. Die festen Seiten liefern
keine unabhängigen Endpunkte. Möglich, aber nicht nachgewiesen.

### 4. `INDEXED_CHECKLIST_FRAME`

**Schreibregel:** Ein bekanntes Musterblatt weist einem wiederkehrenden
Prüfpunkt die Dreikartenform Y–AIIN–Y zu. Der Schreiber kopiert sie, wenn dieser
Prüfpunkt erreicht ist; die Oberflächenwrapper richten sich nach Hand und
Zeilenplatz.

**Beispielbuchung:** „Prüfpunkt des Musterblatts erreicht; festes Zeichenpaket
eintragen“ → `Y AIIN Y`.

**Kontrollierte Rücklesung:** „dieser Record enthält den anonymen Prüfpunkt K“;
der Inhalt von K bleibt ohne Musterblatt unbekannt.

**Scheitert, wenn:** die Formel keinen stabilen Feld-, Reihen- oder
Folgeplatz besitzt und kein externes Musterblatt die abstrakte Koordinate
besitzt. Sie steht hier einmal am offenen Feldende und einmal am Kopf des
dritten, geschlossenen Feldes. Ein physischer Slot ist widerlegt; ein rein
abstrakter Slot ist unprüfbar.

### 5. `ORDINARY_FORMULAIC_PROSE`

**Schreibregel:** Der Schreiber lernt eine häufige Fachwendung als drei ganze
Abkürzungskarten. Wo die Quellwendung vorkommt, kopiert er Y–AIIN–Y; die
Wrapper werden beim Einpassen in die Zeile gesetzt.

**Beispielbuchung:** „die im Werkstattglossar unter Formel F bekannte Wendung“
→ `Y AIIN Y`, ohne Operandenregister.

**Kontrollierte Rücklesung:** Ohne externes Glossar nur
`UNEXPANDED_FORMULA_F`. Eine sprachliche Expansion ist nicht erlaubt.

**Scheitert, wenn:** ein unabhängig identifizierter Wert über Recordgrenzen
regelmäßig von AIIN aufgenommen wird, die beiden Y-Plätze nachweislich
verschiedene Objekte binden oder die Formel stets denselben Formularslot mit
derselben Folgehandlung besitzt. Nichts davon ist auf den festen Seiten
gegeben. Dieses Modell erklärt die Mobilität am sparsamsten, ist aber mit nur
zwei Belegen nicht sicher von technischer Notation zu trennen.

## Sichere 1420er Minimalregel

Dies ist die einzige vorwärts und rückwärts ausführbare Regel, die die Belege
nicht überdehnt:

```text
VORWÄRTS
1. Erkennt der Schreiber auf Musterblatt oder Vorlage die feste Formel F,
   kopiert er die drei Karten Y, AIIN, Y in genau dieser Reihenfolge.
2. Er darf F in ein offenes Feld oder eine zu schließende Zelle setzen.
3. Er wählt sichtbare Wrapper nach Hand, Zeilenanfang und lokaler Umgebung.
4. Eine folgende payload-tragende Schließkarte gehört nicht zu F.

RÜCKWÄRTS
1. Drei aufeinanderfolgende exakte Karten Y, AIIN, Y in einem Feld werden als
   FORMULA_F erkannt.
2. Festgestellt werden nur Reihenfolge und Gleichheit der äußeren Karten.
3. Referent, Gleichheit, Relation, Slot und Quellwort bleiben UNBESTIMMT,
   solange kein externes Musterblatt oder eindeutig aktiver Wert sie bindet.
```

Beispielbuchungen:

```text
Herbal, offener Lauf:    ... Y | FORMULA_F endet die Zeile
Bio, geschlossene Zelle: FORMULA_F + OPAQUE_PAYLOAD_COMMIT
```

Diese Regel ist lehrbar, von Hand ausführbar und reversibel auf genau der
Stufe, die das Manuskript trägt. Sie behauptet nicht, dass der Schreiber selbst
die Expansion von F kannte; Kopieren aus einem Werkstattexemplar genügt.

## Auswahlwertung

Die Punkte messen Belegpassung unter dem eingefrorenen V12-Raster, nicht
historische Schönheit.

| Kandidat | Rekonstruktion 20 | Gesamtinventar 20 | Operanden/Folgen 15 | Kontrollen 15 | 1420-Fit 10 | Regel 10 | Falsifikation 10 | Summe |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| NOT_DISTINGUISHABLE | 20 | 20 | 15 | 15 | 10 | 10 | 10 | **100** |
| ORDINARY_FORMULAIC_PROSE | 20 | 19 | 11 | 14 | 10 | 10 | 8 | 92 |
| DYADIC_RELATION_FRAME | 20 | 17 | 7 | 13 | 10 | 10 | 8 | 85 |
| SHARED_ACTIVE_REFERENCE | 20 | 16 | 5 | 12 | 10 | 10 | 8 | 81 |
| INDEXED_CHECKLIST_FRAME | 20 | 15 | 4 | 8 | 10 | 10 | 8 | 75 |
| PAIRED_EQUAL_VALUE | 20 | 10 | 0 | 8 | 9 | 10 | 5 | 62 |
| RENDERER_OR_SEGMENTATION_ARTIFACT | 8 | 5 | 2 | 2 | 8 | 5 | 5 | 35 |

`NOT_DISTINGUISHABLE` gewinnt, weil es den echten Formelbefund bewahrt und
zugleich die durch die Daten nicht identifizierbaren Quellfunktionen offen
lässt. Die 100 Punkte bedeuten vollständige Erfüllung der Auditpflicht, nicht
100-prozentige Gewissheit über das Manuskript.

## Feste Vorhersagen für einen späteren Test

1. **Aktiver Verweis:** Ein neuer, unabhängig festgelegter Seitenbeleg muss vor
   der Formel genau einen strukturell ausgezeichneten Standard besitzen; nach
   der Formel müssen beide gebundenen Plätze mit ihm fortgesetzt werden.
2. **Gleichwertiges Paar:** Zwei unabhängig erkennbare und symmetrische
   Operanden müssen vor Betrachtung der Karten feststehen. Fehlt einer, darf
   `PAIRED_EQUAL_VALUE` nicht reaktiviert werden.
3. **Dyade:** Ein Bild oder Formular muss zwei geordnete Endpunkte besitzen und
   dieselbe Formel bei denselben Endpunktrollen wiederholen.
4. **Indexslot:** Die Formel muss in mehreren vollständigen Records dieselbe
   extern definierte Schablonenkoordinate oder dieselbe Nachfolgekarte tragen.
5. **Formelprosa:** Die Formel darf weiter zwischen Feldkopf, Feldmitte und
   Feldende wandern und muss keine stabile Commit-Folge besitzen.
6. Ein dritter ungeankerter Beleg erhöht nur die Formelhäufigkeit. Er löst die
   Bedeutungsfrage nicht automatisch.

## Endurteil des Registerschreibers

Ich würde diese drei Karten in einem Werkstattregister als **feste Formel F**
abschreiben und beim Rücklesen wiedererkennen. Ich würde daneben aber weder
„gleich viel“, noch „wie oben“, noch „zwei verbundene Dinge“, noch eine
Slotnummer ausschreiben. Dafür fehlen das eindeutig gesetzte Bezugsmaß, zwei
erkennbare Operanden und ein stabiles Kästchen. Die korrekte technische
Lesung ist vorerst nicht ein moderner Operator, sondern ein opakes,
wiederholbares Formelpaket.

## Reproduktionsanker

```text
d9129ad342a35da3903591c6caac7d49744ac2ec5c4e1ef32ab94cb4ba150cc7  VOYNICH_CURRENT_ROUTE.md
07079ca738d77611c141debc8aff34f2c4934cc99317992d97e1f2405015cb60  SIDEQUEST_SCRIBE_WORKSHOP_CURRENT.md
cdf8a799c92eaf9789d0dc89debe889ac7c7e5f6e293c1ef6fa938dd97e4c201  SIDEQUEST_FOUR_AGENT_BACKGROUNDS.md
46f44e50327db319cd85170d8f5507b94f74fab2dedbff297a8f164b672308ee  V12_SELECTION_PROTOCOL.md
7eba46774be44992064cc114f67329723ac7bf589321b0d763fb7f7f748cc1e9  gdt327_joint_tuple_interlinear.tsv
6309382ea344ed77997980372b47161d10e5761e29d9f5cc67eda6fd1070c6d7  gdt276_event_inventory.tsv
```
