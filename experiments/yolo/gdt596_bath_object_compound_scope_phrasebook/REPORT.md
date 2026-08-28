# GDT596 — aus 254 Badeobjekten wird ein kleines Werkstattphrasebook

Status: `PASS_254_EXACT_COMPOSITIONAL_REPLAYS__5_TYPING_CARDS__3_REFERENCE_SCOPE_CARDS__100_WRITTEN__25_BLOCKER__74_BOUND_REFERENCE__12_AIN_OR_TYPE__43_BODY_DEFAULT__70_LEFT_ANAPHORIC__9_RIGHT_OR_TIE_DEFINITE__175_LOCAL_OR_DEFAULT_DEFINITE__7_LEMMAS__11_OBJECT_FORMS__15_MODIFIER_FRAGMENTS__40_OBSERVED_SEQUENCES__184_DEFINITE__70_ANAPHORIC__247_SINGLE_7_MULTI_PARTICIPANT__0_EXCEPTIONS__23_WORKSHOP_REVIEWS__16_STYLE__6_OBJECT_RIVAL__1_BINDING_RIVAL__2_IMMEDIATE_OBJECT_FORKS`

## Ergebnis

Die 254 konkreten GDT595-Badelesungen brauchen keine 254 Einzelkarten und auch
nicht siebzehn voneinander getrennte Auswahlregeln. Sie lassen sich verlustfrei
in fünf Typkarten und drei unabhängige Bezugskarten zerlegen. Danach genügen
sieben Objektlemmas, vier Artikelregeln, zwei Badrahmen, fünfzehn bekannte
Modifikatoren und drei einfache Kompositionsregeln. Insgesamt sind das 39
Primitive. Alle 254 vollständigen Klauseln werden bytegenau rekonstruiert.

Das ist die bisher brauchbarste Form der gesuchten Mischung aus produktiven
Fachkürzeln und gelernten Ganztypen: Die Typkarte bestimmt, *was für ein Ding*
gemeint ist; die Bezugskarte bestimmt getrennt, *ob dasselbe Ding weiterläuft*
oder ein definites Objekt neu bzw. rechts eingeführt wird.

## Fünf Karten bestimmen den Objekttyp

| Karte | Arbeitsregel | n | Klassenprofil |
|---|---|---:|---|
| T01 | geschriebener getypter Objektträger | 100 | 52 Körper, 40 Station, 6 Einheit, 2 Portion |
| T02 | trägerloser vollständiger Body-Blocker | 25 | 25 Station |
| T03 | gebundene getypte Quelle kopieren | 74 | 57 Station, 5 Körper, 5 Portion, 5 Einheit, 2 Strom |
| T04 | stabiler AIN-/OR-Typ | 12 | 8 Portion, 4 Einheit |
| T05 | kein zulässiger Gegenstand: Body-first | 43 | 43 Körper |

Bei T01 bleibt die alte produktive Gabel exakt: 52 blockerfreie Y-Träger lesen
Körper, 40 Y-Träger mit Body-Blocker Station; sechs OR-Träger lesen Einheit und
zwei AIN-Träger Portion. Geschriebener Typ schlägt Blocker. Deshalb bleiben
E1503 als Einheit trotz `AR|D_ADDR` und E3113 als Portion trotz `L|O` korrekt.

Noch kürzer kann man die fünf Karten als drei Werkstattoperatoren notieren:

- `T` liest einen geschriebenen oder stabil gelernten Typ: 112 Aktionen;
- `R` kopiert eine gebundene getypte Quelle: 74 Aktionen;
- `D` setzt den Hostdefault Station oder Körper: 68 Aktionen.

Die fünf ausführlichen Karten bewahren die Unterfälle, die drei Operatoren die
eigentliche Kompositionsidee.

Alle fünf Typkarten kommen auf jeder der sechs Seiten vor. Das ist noch kein
Test auf einer neuen Seite, aber es zeigt, dass keine Karte nur eine einzelne
Seitennotlösung ist. Die rechte/Tie-Bezugskarte erscheint auf fünf Seiten; nur
f82r besitzt in diesem Bestand keinen solchen Fall.

## Drei Karten bestimmen unabhängig den Bezug

| Karte | Bezug | n | Klassenprofil |
|---|---|---:|---|
| Q01 | linke Quelle nach dem Cut, anaphorisch | 70 | 50 Station, 8 Portion, 7 Einheit, 3 Körper, 2 Strom |
| Q02 | rechter Endträger oder E2952-Pakettie, definit | 9 | 7 Station, 2 Körper |
| Q03 | lokaler Träger oder Typ-/Hostdefault, definit | 175 | 95 Körper, 65 Station, 8 Einheit, 7 Portion |

Die Kreuztabelle ist klein und ohne Formkonflikt:

| Typkarte | Q01 links | Q02 rechts/Tie | Q03 lokal/default |
|---|---:|---:|---:|
| T01 | 0 | 0 | 100 |
| T02 | 0 | 0 | 25 |
| T03 | 65 | 9 | 0 |
| T04 | 5 | 0 | 7 |
| T05 | 0 | 0 | 43 |

Q02 verschleiert den neunten Fall nicht: Nur acht Vorkommen sind echte rechte
gemeinsame Komplemente. E2952 ist eine bidirektionale Station/Portion-Gabel,
deren unmittelbare Weiterbehandlung den Stationsansatz zum Arbeitsdefault
macht.

## Sieben Lemmas erzeugen elf Formen

Die fünf Objektklassen werden in der aktuellen Werkstattsprache durch sieben
genauere Lemmas gesprochen: Körper, Stationsansatz, Anwendungsportion,
Badeinheit, Stationseinheit, Becken- oder Körpereinheit und Strom. Maskuline
Formen verwenden `den/denselben`, feminine `die/dieselbe`.

Damit entstehen exakt 70 anaphorische und 184 definite Formen. Die 70
anaphorischen Fälle sind vollständig erklärt: 65 gehören zu T03 und fünf zu
lokal weitergeführten AIN/OR-Typen aus T04. Ein eigenes langes Wörterbuch für
`denselben Stationsansatz`, `dieselbe Anwendungsportion` usw. ist unnötig.

## Der übrige Satz ist ebenfalls kompositionell

247 Aktionen haben eine Teilnehmer-NP, sechs haben zwei und eine hat drei. In
251 Fällen steht das ausgewählte Objekt zuerst. Nur E1433, E1648 und E1795
führen zunächst Portion oder Einheit und danach den ausgewählten
Stationsansatz. Eine gewöhnliche Listenregel erhält diese Reihenfolge exakt.

Nach der Teilnehmerliste folgt `im Bad`, nur bei den zwei Stromlesungen `im
Badbetrieb`. Fünfzehn vorhandene Modifikatoren erzeugen 338 Vorkommen in vierzig
beobachteten Folgen. Die einzige enge Bindung ist Füllung plus Grad:

```text
AIIN_FILL + E  →  bei der angegebenen Füllung auf Grad I
```

Danach reicht die normale Listenbildung. So wird etwa eine lange Folge ohne
eigene Ganzsatzkarte erzeugt:

```text
Halte den Stationsansatz im Bad auf Grad I,
an der Stations-Arbeitsstelle,
zur Zielstation oder ins Zielbecken,
von der Ausgangsstation oder aus dem Ausgangsbecken
und über den Stationskontakt oder die Leitung
```

AIIN bleibt in diesem Aufbau konsequent Medium/Füllung. Es ist eine
Modifikatorkarte, keine Objektkarte, und kann daher Körper, Station oder Portion
begleiten, ohne einen davon selbst auszuwählen.

## Was exakt bedeutet — und was nicht

`254/254 exakt` heißt: Das kleine Phrasebook kann unsere vollständige aktuelle
Arbeitslesart aus ihren sichtbaren Typ-, Bezugs- und Modifikatorentscheidungen
reproduzieren. Es heißt nicht, dass jede deutsche Langform natürlich oder jede
Objektbindung endgültig ist. Die sechs GDT595-Hostbindungsrivalen E2863, E3224,
E3523, E3533, E3563 und E3664 bleiben ausdrücklich markiert und behalten
trotzdem jeweils einen Primärdefault.

Eine vollständige manuelle Werkstattlektüre aller 254 Slots und ihres
793-Aussagen-Kontexts markiert deshalb ein zweites, bewusst nicht destruktives
Deck:

- 16 Stellen brauchen vor allem flüssigere Scope-, Orts- oder Trägergliederung;
- 6 Stellen behalten einen Objektrivalen;
- E3523 behält zusätzlich eine Gabel zwischen rechtem Gemeinkomplement und
  diskontinuierlicher Diskursanaphora;
- nur E2952 (Station/Portion) und E3224 (Körper/Station) sind unmittelbare
  starke Objektgabeln.

Kein Fall wird gestoppt oder aus der Übersetzung entfernt. Beispielsweise wird
E3512 natürlicher zeitlich gesprochen—„zunächst Grad II, anschließend … Grad
III“—ohne seine Objektwahl zu ändern. E3020 verbindet Haupt-, Neben- und
Arbeitsstelle als Weg statt als drei simultane Orte. Bei E1599 werden
Badeinheit und Portion zu Begleitträgern des Stationsansatzes statt zu drei
gleichrangigen Badepatienten. Das vollständige 23-Karten-Deck steht im
reproduzierbaren Artefakt.

## Nächster Schritt

Bevor neue Seiten geöffnet werden, sollte dieselbe Fünf-plus-Drei-Faktorisierung
auf den übrigen bereits zugelassenen Werkstattaktionen derselben sechs Seiten
gespiegelt werden: Entnehmen, Zuführen, Behandeln, Temperieren, Einbringen usw.
Wenn dieselben Objektquellen und Artikelregeln dort halten, erhalten wir nicht
nur einen Bad-Sonderleser, sondern eine wiederverwendbare Satzgrammatik für die
nächsten Seiten.

Keine Seite, Surface, Wurzel, Slot, Segmentierung oder Parserregel wurde
geändert. Das Phrasebook bleibt eine kreative Arbeitsübersetzung, kein Beleg
für Klartext, Sprache, reales Verfahren, Stoff, Patient, Krankheit, Heilmittel
oder historisches Codebuch.
