# GDT684 — 479 Belegungen sind noch keine Übersetzung

Status: `PASS_479_POSITION_INFORMATION_CENSUS__FORMAL_COMPLETENESS_NOT_SEMANTIC_COMPLETENESS`

## Ergebnis

V57 ist vollständig belegt, aber nicht vollständig verstanden. GDT684 hat
erstmals jede der 479 Positionen der 51 Zeilen einzeln nach ihrem tatsächlichen
Informationsgehalt gelesen. Der bisherige Zähler `residual_unknown_positions =
0` war nur ein Belegungszähler: An jeder Stelle stand irgendeine Karte. Er sagte
nicht, ob diese Karte einen Stoff, eine Handlung, eine Menge oder bloß eine
moderne Strukturbezeichnung liefert.

Der neue Stand trennt drei sich überlappende Ebenen:

| Ebene | Positionen | Was sie misst |
|---|---:|---|
| kuratierte Reparaturwarteschlange | 139 | konkret benannte Kartenfamilien, die als Nächstes repariert werden können |
| mechanischer Sichtalarm | 172 | offen, mehrwertig, strukturell, generischer Stoffkopf oder Zustand ohne Objekt |
| breite Spezifität offen | 335 | keine vollständige Identität, kein gebundenes Objekt oder keine gebundene Wertachse |
| mindestens ein Signal aus diesen drei Ebenen | 371 | derzeit nicht ohne Vorbehalt als konkrete Bedeutung ausgebbar |
| LOW/EXPLORATORY-Provenienz | 30 | aktuelle Karte ist in ihrer Quelle ausdrücklich schwach markiert |
| Union einschließlich Evidenzstärke | 381 | mindestens Schuld oder schwache Kartenprovenienz |
| kein Signal aus allen vier Ebenen | 98 | informationsstark innerhalb der Arbeitstheorie, nicht historisch bestätigt |

Die Zahlen dürfen nicht addiert werden. Das vollständige Acht-Felder-Kreuz
steht in `DEBT_LAYER_CROSSWALK.tsv`. Gerade die Überlappungen sind nützlich:
Sie zeigen, ob eine Karte wegen einer bekannten Reparaturfamilie, wegen ihres
sichtbaren Wortlauts oder wegen fehlender Spezifität auffällt.

## Der mechanische Reality-Check

Dieser Test schaut nicht darauf, wie flüssig die deutsche Zeile klingt.

| Alarm | Positionen | Bedeutung |
|---|---:|---|
| `OPEN_COMPOSITION` | 20 | die publizierte Karte sagt selbst „offen“ |
| `NON_SINGLE_GLOSS` | 44 | Slash oder „oder“ lässt mehrere Werte stehen |
| `STRUCTURAL_META_AS_VALUE` | 18 | Eintrag, Bezug, Rahmen oder Wertfeld wird als Tokenwert ausgegeben |
| `HARD_GENERIC_CARRIER` | 47 | Objekt bleibt Gut, Material, Drogenstoff, Pulverstoff, Holzstoff oder Rohstoff |
| `STATE_ONLY_NO_OBJECT` | 65 | Zustand/Stufe/Abschluss ohne gebundenen Stoffkopf |

Die 194 Klassenmitgliedschaften vereinigen sich zu 172 Positionen. Damit ist
klar, warum Sätze wie „trocken, Mittelstufe, abgeschlossen“ formal
unterscheidend und trotzdem keine selbständige Stoff- oder Handlungsübersetzung
sind.

## Die konkrete 139er-Reparaturliste

| Familie | Positionen | Nächster sinnvoller Eingriff |
|---|---:|---|
| generischer Träger | 10 | produktive Trägerkomposition prüfen |
| Wertdimension offen | 19 | Zahl von Maß/Grad/Klasse trennen |
| ungelöste Bindung | 20 | `olkar/olam` samt Holzrivalen sichtbar halten |
| Strukturkarte | 11 | Strukturkanal statt erfundenem Plaintext |
| Taxonomie-/Materialalternative | 16 | exakte Carrierfamilie statt stiller Auswahl |
| generischer Drogenkopf | 21 | Aktionsobjekt lokal binden |
| Rohstoffklasse ohne Identität | 20 | Klasse nicht als konkrete Droge verkaufen |
| opaker Formcode | 12 | Formachse erst kalibrieren |
| Menge/Einheit ohne Kopf | 11 | lokalen Stoffkopf oder „wovon offen“ ausgeben |

Die Summe ist 140, weil f114v.36#2 `oidal` zugleich Rohstoffklasse und opaker
Formcode ist. Die Vereinigung bleibt 139.

## Sieben echte Schichtfehler

Die wichtigsten Fehler sind nicht bloß „zu allgemein“, sondern ändern die
Information zwischen Tokenkarte, ausgerichteter Zeile und Praxisprosa.

| Stelle | Fehler |
|---|---|
| f26r.2#1 `dchey` | Literal ist eine Trockenaktion, Metadaten lizenzieren sie nicht, aligned macht daraus ein Ergebnis |
| f26r.2#7 `dy` | ein Wertfeldschluss wird zu „Den Posten schließen“ |
| f26r.2#9 `ls` | Holzdrogencharge wird ohne sichtbaren Rivalen zu Wurzelholz |
| f7r.2#2–3 `keo+r` | Ansatz plus Wurzel verschwindet hinter „heiße Drogenportion“ |
| f86v3.13#5 `qodaiin` | Qualitätsgrad III wird in der Praxis zu drei Teilen |
| f86v3.13#6 `olkar` | die offene Holzbindung verschwindet |
| f114r.26#10 `olam` | offenes Ansatz-/Drogenmaterial schrumpft zu einem bloßen Maßbefehl |

`dchey` macht das Grundproblem besonders sichtbar. Dasselbe Surface trägt zehn
Literal-Aktionskarten und vier nominale Ergebniskarten; nur neun der zehn
Aktionsliterale sind in `action_ordinals` registriert. Aktion gegen Ergebnis
muss daher lokal dispatcht werden, nicht durch freie deutsche Satzbildung.

## Die Praxisprosa erfindet noch Handlungen

Die Quellmetadaten lizenzieren 86 Aktionspositionen. Der reproduzierbare
31-Lemma-Scan findet auf 29/51 Praxiszeilen insgesamt 74 zusätzliche
Operation-Label×Zeile-Paare, die in den lizenzierten Tokenaktionsglossen der
jeweiligen Zeile fehlen. Das beweist nicht, dass jede dieser 74 Formulierungen
falsch ist; es beweist, dass sie derzeit nicht aus der sichtbaren
Aktionsprovenienz stammen.

Beispiele sind „verbinden“, „halten“, „abteilen“, „bilden“ und „verwenden“ in
Zeilen, deren betreffender Teil nominale Zustände oder Warenkarten enthält.
GDT684 ersetzt sie noch nicht. Es macht sie erstmals als prüfbare Renderer-
Schuld sichtbar.

## Schwache Karten, die bisher stark klangen

Ein exakter Join von aktuellem Surface plus aktuellem Literalgloss gegen die
publizierten Kartenquellen findet 30 Positionen / 28 Karten mit `LOW`,
`LOW_EXPLORATORY` oder einer anderen ausdrücklich explorativen Stärke. Zehn
davon waren in den drei inhaltlichen Schuldebenen unauffällig und klangen daher
fälschlich „fertig“.

Dazu gehören unter anderem `shx = eingeweichtes Gummiharz`,
`qoeeo = zweiter Mazerationsansatz`, `solky = Saatgutansatz, leicht erhitzt`,
`tolg = ein Gran kalten Drogenmaterials`, `ypchesy = hiervon Samenpulver ...`
und `lchl = getrocknetes Drogenholz`. Diese Bedeutungen werden nicht verworfen.
Ihre schwache Herkunft bleibt jetzt neben jeder Position sichtbar. Der lokal
neu gerenderte Compoundteil f115r.1#5 `cheop` wird bewusst nicht fälschlich an
seine ältere längere LOW-Karte gejoint.

## `Grundansatz` bleibt eine Arbeitshypothese

GDT683 entfernte an fünf freien `ol`-Stellen den alten Metatext und setzte
`Grundansatz` ein. Das war als Rendererreparatur sinnvoll, aber die
Leserübereinstimmung stützt primär die Wortgrenze, nicht die Bedeutung.
GDT664 führt die Karte ausdrücklich als:

```text
ol | LEARNED_OL_BASE | Grundansatz | exaktes nacktes Ganzwort | MEDIUM
```

Darum bleiben die fünf Stellen in V57 stehen, zählen nicht erneut als akute
139er-Rendererreparatur, liegen aber in der breiten Spezifitätsschuld und nun
zusätzlich in `V57_PROVISIONAL_SEMANTIC_CONFIDENCE_WATCH.tsv`. „Zero OL debt“
bedeutet nur: kein alter OL-Metaglossa-String mehr. Es bedeutet nicht:
historisch bestätigtes Wort.

Das freie `l` auf f111v.18 ist dagegen keine der 479 V57-Positionen. Es bleibt
als genau ein outside-V57-Begleitposten separat erhalten.

## Was bereits brauchbare Information ist

Der Reality-Check setzt nicht alles auf null. Die Arbeitstheorie unterscheidet
an vielen Stellen stabil:

- Handlungen gegenüber nominalen Waren-/Zustandskarten;
- heiß, kalt, trocken und feucht;
- Anfangs-, Mittel- und Endstufen sowie Abschluss;
- Mengen-/Fraktionsmuster;
- Arbeitsklassen wie Wurzel, Samen, Holz, Pulver und reproduktiver Pflanzenteil;
- lokale Bezugsketten und gebundene Spans.

Das Problem ist die letzte Bindung: Welcher konkrete Stoff trägt den Zustand,
welche Dimension hat der Zahlenwert, und welches sichtbare Token lizenziert
das Verb? Genau diese fehlenden Bindungen stehen nun positionsgenau im
Reparaturdeck.

## Nächster Zug

Der kleinste produktive Bedeutungsversuch ist die vollständige
`CH/SH/T + OL`-Familie. In V57 stehen sechs `chol`, ein `shol` und ein `tol`.
Die Arbeitsvorhersagen lauten:

```text
chol -> Trockenansatz
shol -> Feuchtansatz
tol  -> Kaltansatz
```

Der nächste Versuch soll alle bereits zugelassenen exakten Vorkommen dieser drei Oberflächen
und ihre lokalen Stoff-/Aktionsköpfe durchgehen. Die Karte darf übernommen
werden, wenn dieselbe Komposition die Kontexte besser und kürzer erklärt als
„trocken/feucht/kalt; Gut/Material“. Ein lokaler Kopf darf den Träger
konkretisieren; er darf nicht global erfunden werden.

Danach folgen in dieser Reihenfolge: `qodaiin/dain/daiin` nach Wertachse,
`dchey/y/dy` nach Aktion versus Struktur, die sichtbare `olkar/olam`-Warnung
und schließlich die 21 generischen Drogenköpfe mit lokalem Objektscope.

## Claim ceiling

GDT684 ist ein vollständiger Schulden- und Reparaturcensus des bestehenden
V57-Readers. Es ersetzt keine Karte und öffnet keine Seite. Die 98 Positionen
ohne aktuelles Schuldsignal sind innerhalb der explorativen Arbeitstheorie
informationsstark, aber keine bestätigten Lexeme. Sprache, Lautwert, konkrete
Pflanze, Krankheit, Patient, Heilung, Trägerflüssigkeit und historisches
Codebuch bleiben unbestimmt.
