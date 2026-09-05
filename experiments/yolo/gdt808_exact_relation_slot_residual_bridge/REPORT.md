# GDT808 — zwei übertragbare Record-/Formkontraste, kein gemeinsamer lokaler Operator

Status: `COMPLETE__L_AND_DY_PORTABLE_RECORD_OR_FORM__TWO_DISTINCT_OR_AXIS_BOUND_RELATIONS__R06_RECORD_CHANNEL_LEADS__ZERO_LEXEMES`

## Ergebnis

Der offizielle Lauf rekonstruiert 1.777 CORE13-Ereignisse auf 559 strikten
Absätzen, 1.403 Fokuszeilen und 169 physischen Folios. In 4.538
Carrier-und-Folio-Holdouts entstehen 7.970 Vorhersagen. Der unabhängige
Validator rekonstruiert alle Ereignisse, Features, Vorhersagen, Nullränge,
Kontakte, Entscheidungen und Artefakthashes in 34 Prüfblöcken vollständig.

Beide innerhalb ihrer eigenen Achse geprüften Kontraste sind über unbekannte
Carrier und physische Folios hinweg als Record-/Form-Beziehungen erkennbar:

| Achse | nuisance AUC | + lokaler Slot | lokaler Gewinn | K24-Rang | Carrier-Nullrang | ALL28 nuisance / +slot | Entscheidung |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `Xol :: Xeol` | 0,611534 | 0,617142 | +0,005609 | 4/25 | 3/13 | 0,669889 / 0,667348 | `PORTABLE_RECORD_OR_FORM_RELATION` |
| `Xedy :: Xeody` | 0,753049 | 0,769903 | +0,016854 | 1/25 | 1/13 | 0,791832 / 0,803026 | `PORTABLE_RECORD_OR_FORM_RELATION` |

Der lokale Zusatz bleibt auf beiden Achsen unter der vorab gesetzten Grenze
von 0,02. Bei L ist der bedingte lokale Gewinn sogar negativ (-0,044591); bei
DY ist er positiv (+0,056961), aber der Gesamteffekt bleibt mit +0,016854 zu
klein für einen lokalen Operator. DY bewahrt damit einen kleinen, ernst zu
nehmenden Slot-Hinweis, nicht aber eine Komponentenbedeutung.

Die beiden Achsen sind nicht austauschbar. Training auf L und Vorhersage von DY
ergibt für den kombinierten Score AUC 0,398734; in Gegenrichtung sind es
0,450339. Die lokalen Cross-Axis-Scores liegen nur bei 0,540197 und 0,515150.
Ohne nachträgliches Vorzeichenwenden folgt deshalb
`TWO_DISTINCT_OR_AXIS_BOUND_RELATIONS`. GDT808 lizenziert damit kein
gemeinsames `e`-, Form- oder Operationsmorphem.

Die rohe Registerrichtung macht diese Inkompatibilität sichtbar. Auf DY liegt
`Xeody` in Currier/Register A bei 48 von 51 Ereignissen, in B aber nur bei 100
von 812. Auf L liegt `Xeol` dagegen in A bei 123 von 544, in B bei 150 von 370.
Dass derselbe expanded/base-Kontrast zwischen den Achsen seine
Registerorientierung wechselt, erklärt den negativen Cross-Transfer besser als
eine einzige gemeinsame Bedeutung.

## Was das strukturell bedeutet

`Xol/Xeol` und `Xedy/Xeody` verhalten sich am besten wie zwei getrennte
Schreib- oder Recordkanäle, in denen derselbe Carrier in zwei Varianten
auftreten kann. Der übrige Absatz, Topic und Formregime sagen die Variante
deutlich besser voraus als die unmittelbaren Wörter links und rechts.

Das ist konkrete Information, aber noch kein Wörterbuch:

- `e` darf nicht als universeller Operator gelesen werden;
- L und DY dürfen nicht in eine gemeinsame Bedeutungstabelle gezwungen werden;
- eine vollständige Form muss zusammen mit ihrem Recordkanal und ihrem
  wiederkehrenden Ganzwortkopf interpretiert werden;
- die DY-Achse ist wesentlich stärker und robuster als die L-Achse.

Die destruktive ED1-Kontrolle bestätigt diese Asymmetrie. DY bleibt mit
nuisance AUC 0,726426 und augmented AUC 0,736094 deutlich erhalten. L fällt
auf 0,592049 beziehungsweise 0,567733. Auch die dünnen `Xkol/Xtal`- und die
gelernten `cheol/otal`-Kontrollen werden hauptsächlich vom Record-/Formumfeld,
nicht vom lokalen Slot getragen. Das stützt eine breite Kanalgrammatik und
spricht gegen ein aus diesen Paaren direkt ablesbares Lexikon.

## Historische und konkrete Rivalen

Der feste historische Vergleich ordnet die Arbeitsmodelle so:

1. `R06_RECORD_CHANNEL` — 6 Punkte;
2. `R04_PART_OR_FORM_SCOPE` — 4 Punkte;
3. `R05_GROUP_DOSE_OR_UNIT_VALUE` — 4 Punkte;
4. `R01_ATTRIBUTIVE_BINDING_PLUS_PREPARATION` — 2 Punkte;
5. `R07_BREVIGRAPH_OR_ORTHOGRAPHY` — 2 Punkte.

Die Kontaktatlas-Richtung liefert zwei brauchbare nächste Hebel. Auf DY ist
die expanded-Seite `Xeody` an den fünf sauberen Mengen-Kontakten gegenüber
`Xedy` stark überrepräsentiert (log OR +2,696916), allerdings nur auf vier
Folios. Auf L liegt die Part/Form-Nähe dagegen häufiger bei der base-Seite
`Xol` als bei `Xeol` (10 expanded gegenüber 59 base Kontakte; log OR
-0,941325) und verteilt sich über 48 Folios. Für Quality/Value existiert kein
einziger sauberer Kontakt. Die Gegenkontakte sind außerdem nicht null: L-Menge
liegt bei log OR +0,860986 auf sieben Folios und DY-Part/Form bei +0,853554 auf
zehn Folios. Menge und Part benennen daher keine Achse eindeutig. Diese
Richtungen sind Kandidatenführer, keine Wortbedeutungen.

## Nächster Bedeutungsweg

Der passende Anschluss ist nun der recordkonditionierte Ganzwort-HEAD-PIVOT:

1. vollständige Köpfe `H` aus bereits bekannten `H daiin`- und
   positionsrichtig gebundenen Mengenphrasen übernehmen;
2. dieselben exakten Ganzwörter an ihren übrigen Vorkommen wiederfinden;
3. L und DY getrennt fragen, welche base/expanded-Variante im selben
   Record-, Bild-, Label- und Absatzrahmen mit `H` verbunden ist;
4. erst danach konkrete historische Verhaltensprofile für
   Wasser/Wein/Öl/Salz, Wurzel/Blatt/Blüte/Samen,
   reiben/mischen/filtern/erwärmen/trocknen/einweichen und Gefäßklassen
   gegeneinander ranken.

Damit wird nicht erneut ein Nachbarclassifier gebaut. Ein Kopf muss seine Rolle
über mehrere Vorkommen tragen, und ein konkreter Kandidat muss zusätzlich zum
Recordkanal eine unabhängige Mengen-, Vorgangs-, Bild- oder Part-Signatur
besitzen. EVA-Schreibähnlichkeit zu lateinischen Wörtern erhält keinen Kredit.

## Grenze

GDT808 bestätigt keine Übersetzung, kein Wort und kein Morphem. Es ersetzt die
alte unbrauchbare Annahme eines gemeinsamen lokalen Bausteins durch ein
brauchbares Arbeitsmodell: zwei getrennte, übertragbare Record-/Formkontraste,
mit DY als starkem Kanal und L als schwächerem, ED1-empfindlichem Kanal. Genau
diese Trennung wird im nächsten Versuch benutzt, statt wieder generische
Prozessprosa zu erzeugen.

## Reproduktion

```bash
python3 experiments/yolo/gdt808_exact_relation_slot_residual_bridge/src/validate.py --no-write
python3 experiments/yolo/gdt808_exact_relation_slot_residual_bridge/src/run.py \
  --output-dir experiments/yolo/gdt808_exact_relation_slot_residual_bridge/reproduction_scratch
./vmanus-exp check-edge-packet experiments/yolo/gdt808_exact_relation_slot_residual_bridge/artifacts/GDT808_GDT388_RELATION_PACKET.tsv
```

Der Validator prüft die veröffentlichten Artefakte ohne sie zu verändern. Ein
Builder-Replay gehört in das angegebene Scratch-Verzeichnis: `runtime_seconds`
ist naturgemäß laufabhängig, daher ist dessen neues `RESULT.json` nicht
bytegleich mit dem veröffentlichten Ergebnis zu erwarten.

Das GDT388-Paket enthält 19 formale Paare und bleibt erwartungsgemäß für alle
19 allein wegen bereits erfolgtem Formalzugriff nicht score-ready.
