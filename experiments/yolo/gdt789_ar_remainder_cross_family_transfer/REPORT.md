# GDT789 — Ganzwort-Arbeitsdefault `ar = Anteil`; Resttransfer gescheitert

## Ergebnis

Der beste kurze Arbeitswert ist jetzt:

```text
ar = Anteil
```

Das ist präziser als die ältere Karte `Drogenanteil I`: Weder eine bestimmte
Droge noch ein automatisch mitgeschriebenes „I“ ist im neuen Test nötig.  Die
Karte beschreibt das vollständige Wort `ar` als relativen Mengen-, Teil- oder
Verhältniskopf.  Seine stärksten Rivalen bleiben **Portion/Teilmenge**,
**Stoffklasse** und **Wertfeld**.

Was nicht funktioniert, ist die automatische Fortsetzung:

```text
Xar = X-Anteil
```

Die sichtbare Familie ist groß und real.  Nach der eindeutigen längsten-Endung-
Regel—`*dar` gehört zur bereits behandelten DAR-Familie—bleiben **285 rohe
`*ar`-Formen mit 1.698 Token**, davon **225 Formen/1.348 Token reader-exakt**.
Das nackte `ar` allein hat 242 exakte Vorkommen auf 51 physischen Folios.

GDT789 prüft erstmals 47 robuste vollständige `Xar/Xor`-Paare mit einem
target-maskierten Restmodell:

```text
ADD_AR(Xar) = Xor + ar - or
```

In der 31-Typen-Stützkohorte verbessert dieses Modell `Xor` in 21/31 Fällen.
Das ist ein distributioneller Hinweis auf einen AR/OR-Familienkontrast, noch
keine Bedeutung. Gegen unabhängig ausgewählte gelernte Ganzwörter gewinnt
ADD_AR aber nur 11/31 und gegen **beide** Kontrollen nur **7/31**. Eine zweite,
mechanisch definierte, aber teilweise überlappende 31-Typen-Sicht endet bei
**8/31**. Sie ist eine historische Ausschluss-Sensitivität, keine unabhängige
Replikation: 16 Präfixe liegen in beiden Sichten, je 15 nur in einer. Die
praktische Entscheidung lautet deshalb:

```text
FORM:       starke AR/OR-Oberflächenfamilie
ar:         Anteil                         [eigenes Ganzwort]
Xar:        gelernte oder formgebundene Ganzwörter
TRANSFER:   WHOLE_ONLY
EXPORT:     kein freier ar-Rest
```

## Warum das kein umgedrehtes GDT788 ist

GDT788 benutzte zehn `Xar`-Formen als Schwesterzellen, um `Xdal`
vorherzusagen.  GDT789 macht daraus keine scheinbar neue Entdeckung.  Das alte
40-Zellen-Raster steht nur als Referenzartefakt bereit und erhält null
Scorekredit.

Die neue Hauptfrage ist AR gegen OR.  Die robuste Grundmenge enthält 47
Präfixtypen/94 Zellen und 1.647 exakte Vorkommen.  Zwei verschiedene
Typauswahlen verhindern, dass nur die bekannten Hochfrequenzformen das
Ergebnis bestimmen:

| Kohorte | `Xar` | `Xor` | ADD_AR > `Xor` | ADD_AR > gelernt | ADD_AR > beide |
|---|---:|---:|---:|---:|---:|
| 31 gut gestützte Typen | 817 | 712 | 21 | 11 | **7** |
| 31 historisch nicht vorbelastete robuste Typen | 233 | 275 | 21 | 13 | **8** |
| alle 47 robusten Typen | 861 | 786 | 29 | 17 | **9** |

Die vollständigen Profilwerte sind:

| Kohorte/Sicht | ADD_AR | `Xor` | gelerntes Ganzwort | Siege gegen beide |
|---|---:|---:|---:|---:|
| Stütze, voll | .787 | .763 | .810 | 7/31 |
| Stütze, Struktur | .868 | .855 | .877 | 10/31 |
| Stütze, Bedeutung | .410 | .351 | .454 | 8/29 |
| Stütze, Wertbindung/Nichtbindung | .964 | .962 | .968 | 4/31 |
| historischer Ausschluss, voll | .755 | .725 | .768 | 8/31 |
| historischer Ausschluss, Bedeutung | .328 | .171 | .349 | 7/21 |

ADD_AR hebt sich regelmäßig von der bloßen OR-Schwester ab, aber die
formgebundenen Ganzwörter bleiben im Mittel besser.  Das ist genau das Muster
eines begrenzten Familienkontrasts ohne frei exportierbares Wörterbuchstück.
Die sehr hohen Werte der Konstruktion-Sicht stammen außerdem überwiegend aus
gemeinsamer **Nichtbindung**; sie sind kein positives Transferargument und
gehen in keine Freigabeschwelle ein.

Die sieben Stützkohorten-Treffer sind `lar`, `opar`, `otchar`, `par`, `qopar`,
`sar` und `shear`. In der historischen Ausschlusssicht kommen `choar` und `keear` hinzu,
während `shear` dort definitionsgemäß nicht mitstimmt.  Die Treffer bilden
keine gemeinsame Stoff-, Temperatur- oder Prozessgruppe.

## Die orthogonale R/N-Leiter fällt vollständig aus

Der stärkere Gegencheck benutzt nicht AL/DAL, sondern zwei reale
Viererzellen-Leitern:

```text
RN12: Xar   aus Xan + Xair - Xain       7 Typen
RN23: Xaiir aus Xaiin + Xair - Xain     6 Typen
```

Im Vollprofil schlägt die additive Vorhersage in **0/7** beziehungsweise
**0/6** Fällen alle Kontrollen.  Bei RN12 ist das gelernte Ganzwort im Mittel
sehr deutlich besser (.896 gegen .714); bei RN23 liegen alle Modelle näher,
aber auch dort gibt es keinen Volltreffer.  Damit fällt gerade die Idee, ein
einfacher R-Rest trage über die geschriebenen Indexstufen dieselbe Bedeutung,
am klarsten durch.

## Ist `ar` Anteil, Portion oder Wertfeld?

Die beobachteten Konstruktionen machen `ar` zu einem brauchbaren zähl- oder
wertgebundenen Kopf:

| Ausdruck | reader-exakt getrennt | fusioniert reader-exakt |
|---|---:|---:|
| `ar ain` | 5 | `arain` 0 |
| `ar aiin` | 16 | `araiin` 4 |
| `ar aiiin` | 6 | `araiiin` 0 |
| `or ain/aiin/aiiin` | 42 | `orain/oraiin/oraiiin` 36 |
| `s ain/aiin/aiiin` | 25 | `sain/saiin/saiiin` 143 |

Somit trägt `ar + Wert` 27 strikte Stellen.  Es ist aber weder der einzige
solche Kopf noch ein identifiziertes Maßzeichen.  `ar aiin` darf explorativ
„drei Anteile“ heißen; ebenso sichtbar bleiben „Anteil, Wert III“ und „drei
Teilwerte“.

Die vier Verschachtelungen sind ebenfalls real: `ar ar` 6-mal, `ar or` 8-mal,
`or ar` 5-mal und `or or` 3-mal reader-exakt.  Dazu kommen die fusionierten
Ganzen `arar` einmal, `aror` fünfmal, `orar` fünfmal und `oror` zweimal.  Das
macht eine relative Lesung wie **Anteil einer Portion** oder **Portion eines
Anteils** praktisch plausibler als zwei perfekte Synonyme, beweist die
deutschen Wörter jedoch nicht.

Die direkten Außenachsen helfen nur wenig.  Im 31er-Stützdeck liegt PART bei
Radius 1 in sechs AR-Typen höher und nur in einem OR-Typ höher, aber 24 Typen
binden gar keinen Unterschied; der mittlere Abstand ist nur +.008.  AMOUNT ist
6:4 bei 21 Bindungen und +.017.  Bei Radius 3 werden beide Bilder gemischter.
MATERIAL liegt sogar überwiegend auf der OR-Seite.  Es gibt daher keinen
konkreten Stoff, der `ar` identifiziert.

Eine 2.140 Oberflächen große Leckage-Maske hält die bereits mit AR/OR/R/N oder
älteren AR-Deutungen verbundenen Karten aus Nachbarschaften und Donoren.

Ein separater Rollenklassifikator bestätigt diese Grenze.  Er verwendet 253
saubere, maskenfremde Arbeitskarten: 12 PART, 33 AMOUNT und 208 VALUE.  Im
Leave-one-surface-out erreicht er 64,4 % klassengewichtete Genauigkeit, aber
nur 27,3 % Recall für AMOUNT.  Deshalb wird sein Vorschlag `ar→VALUE` nicht
übernommen: Derselbe Klassifikator nennt auch `or` und `s` VALUE und erkennt
offenbar die gemeinsame Feldposition, nicht die feine Bedeutung der drei
Köpfe.

`Anteil` bleibt somit die beste **Arbeitswahl**, weil sie den AR/OR-Kontrast,
die gemischten Verschachtelungen und die Wertbindung gemeinsam ausdrückt,
ohne Trennung, Extraktion oder eine bestimmte Einheit zu behaupten.

## Grenzen: starkes getrenntes Wort, schwache innere Segmentierung

Es gibt **318** rohe Folgen `X ar`; **192** davon mit 126 verschiedenen linken
Wörtern bewahren beide Token und ihre Reihenfolge in allen drei aktuellen
Lesungen. Zwanzig linke Wörter kommen außerdem an anderer Stelle fusioniert
als `Xar` vor. Das ist mit beweglichen Wortgrenzen vereinbar, belegt sie aber
nicht: Es ist eine Cross-Locus-Brücke, kein gleichlokaler Split.

Unter den aktuellen Lesern gibt es keinen reader-exakten gleichlokalen Split.
Die Stolfi-Sensitivität erreicht 422 Zielvorkommen am gleichen Locus; davon
sind 352 längere Formen und 70 das nackte `ar`. In 67 dieser 70 nackten Fälle
liest Stolfi dort ebenfalls genau `ar`; drei sind abweichende Grenzlesungen:
327 bleiben fusioniert, 22 werden anders gelesen, fünf zeigen eine andere
AR-Grenze und genau **ein** Vorkommen splittet passend:

```text
f5r.1: oar → o,ar
```

Nur 352 der 1.106 längeren exakten Zieltoken sind bei Stolfi am selben Locus
vergleichbar; 754 fehlen auf Seiten- oder Locus-Ebene. Ein passender Split
unter diesen 352 ist ein guter Warnhinweis, aber kein tragfähiger
Komponentenbeweis. Das 192-Kanten-Paket besteht den
Relation-Validator als Erfassungsbestand und bleibt absichtlich nicht
score-ready, weil es Textreihenfolge und keine unabhängige Bildgeometrie ist.

## Konkrete Arbeitskarten ohne alte Drogenholz-Prosa

Alle 285 beobachteten Formen haben jetzt einen nichtleeren Default, drei
Rivalen, Evidenz, Gegenbeleg und ein redaktionelles Konfidenzgewicht:

| Form | bevorzugte Arbeitsanzeige | Gewicht* | wichtigste Rivalen |
|---|---|---:|---|
| `ar` | **Anteil** | 64 | Portion/Teilmenge · Stoffklasse · Wertfeld |
| `qokar` | heißer Anteil | 52 | heiße Teilmenge · heißes Wertfeld · Ganzname |
| `otar` | kalter Zubereitungsanteil | 48 | kalte Teilmenge · kaltes Wertfeld · Ganzname |
| `okar` | Anteil des heißen Ansatzes | 50 | heiße Teilmenge · heißes Wertfeld · Ganzname |
| `char` | trockener Anteil | 48 | trockene Teilmenge · Trockenklasse · Ganzname |
| `shar` | angefeuchteter Anteil | 42 | feuchte Teilmenge · Feuchteklasse · Ganzname |
| `shear` | eingeweichter Anteil | 40 | feuchte Teilmenge · Feuchteklasse · Ganzname |
| `arar` | Anteil eines Anteils | 32 | zwei Anteilfelder · Wiederholungsmarker · Ganzname |
| `otarar` | Unteranteil des kalten Ansatzes | 38 | zwei Anteilfelder · kaltes Klassenfeld · Ganzname |

\*Keine Wahrscheinlichkeit, sondern ein nachvollziehbares redaktionelles
Evidenzgewicht.

Die alten automatisch mitgeschleppten Patienten **Droge, Holz, Samen, Wurzel
und Pulver** werden nicht aus EVA-Anfängen rekonstruiert. Der durchgefallene
Rollenklassifikator darf nun auch `sar`, `lar` oder `par` nicht mehr zum
bevorzugten Default machen. Solche rekurrenten Formen erhalten stattdessen das
neutrale, absichtlich austauschbare **wiederkehrendes Verhältnisfeld**; die
konkreteren Rollen bleiben als Rivalen sichtbar.

Von 285 Karten sind 19 gezielte Ganzwortanzeigen, 63 wiederkehrende
Familienfallbacks, 143 exakte Singletonkarten und 60 rohe Lesewarnungen. Keine
wird global in den laufenden Renderer exportiert.

Ein Beispiel zeigt den Zweck der Ausgabe:

```text
f100v.14
deey · sheocphy · qoteody · ckhoor · ⟦ar = Anteil⟧ · chor · oteey · daiin · qokomo
```

Die Nachbarn bleiben sichtbar unbekannt oder tragen nur ihre eigenen Karten;
GDT789 erfindet daraus keinen flüssigen Rezeptsatz.

## Historische Passform und nächster Hebel

Die bereits erfassten Vergleichsquellen um 1400–1420 erlauben eine Mischung
aus gelernten Drogennamen, Anteilen/Portionen, Mengenwerten, Graden und
Zustandsfeldern.  Das macht `Anteil` als kurze Werkstattlesung möglich.  Keine
Quelle verbindet aber EVA `ar` mit einem historischen Wort, Lautwert oder
Abkürzungszeichen.

GDT789 verbessert die Arbeitstheorie in zwei Punkten: Bare `ar` verliert den
unnötigen Drogenpatienten und die unbelegte Stufe I; zugleich werden 224
längere exakte Formen davor geschützt, automatisch dieselbe Bedeutung zu
erben.  Als Nächstes folgt `ol`, nun mit demselben AR-Lerneffekt: eigenständige
Ganzwortbedeutung, produktiver Rest und kontextueller Operator müssen getrennt
gegeneinander antreten.

GDT789 öffnet keine neue Seite, kein Bild, keine OCR oder Transkription;
`f84/f84r` bleiben gesperrt.  Bestätigte Lexeme und Klartextsätze bleiben null.
