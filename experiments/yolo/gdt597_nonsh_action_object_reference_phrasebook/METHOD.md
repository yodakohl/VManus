# GDT597 method

## Frage und Population

Kann die fünfteilige Objekt- und dreiteilige Bezugstechnik aus GDT596 auf alle
laufenden Nicht-SH-Werkstattaktionen derselben sechs Badseiten übertragen
werden, sodass jede `T/CHD/S`-Klausel einen konkreten Gegenstand erhält, ohne
eine neue Seite, Wurzel, Segmentierung oder Substringregel zu öffnen?

Vier gemischte Eingaben werden occurrence-genau über `vmanus-exp query-tsv`
mit der expliziten Seitenauswahl `f75r/f77r/f81r/f81v/f82r/f83r` geladen.
`f84` und `f84r` werden vor dem Materialisieren einer Zeile verworfen. GDT596
und das lokale manuelle Review-Deck enthalten ausschließlich diese sechs
Seiten und werden anschließend auf dieselbe Seitenmenge geprüft.

- GDT584: 2.272 geordnete Satzhosts und OT/OL/DY-Kontrollen.
- GDT582: 4.924 konkrete Slots, darunter Träger an anderen Aktionen.
- GDT587: 1.669 polierte Hostklauseln in Kandidatensätzen.
- GDT589: 330 vollständige laufende `T/SH/CHD/S`-Trägerhosts.
- GDT596: 254 vollständig getypte SH-Badobjekte.

Die Zielmenge enthält 396 laufende Aktionen in 219 Aussagen: 199 CHD, 104 S
und 93 T. 219 besitzen einen geschriebenen Träger; 177 sind trägerlos.

## Quellen, Zustand und Auswahl

Jede Aussage beginnt mit leerem Zustand. `Beginne danach …` und `Schließe …`
leeren ihn; OL erhält ihn. Direkte Quellen werden in dieser Reihenfolge
gebildet:

1. vollständiges SH-Objekt aus GDT596;
2. getyptes T/CHD/S-Packet aus GDT589;
3. geschriebener GDT582-Träger einer anderen Aktion.

Der Zustand hat zwei Arbeitskanäle. Teilnehmer sind Körper, Körperteil,
Stationsansatz, Portion, Einheit oder Strom. Parameter sind Maß und
Stationsbedingung. Eine trägerlose Aktion sucht nach dem letzten Cut rückwärts
bis zur nächsten aktionskompatiblen Quelle. Erst wenn keine linke Quelle
greift, darf ein passender rechter Träger desselben Ereignisses übernehmen;
danach folgt das konkrete Aktionsdefault.

Vier Scopekarten verfeinern diese allgemeine Nähe:

- E2585: `als neuer Bad- oder Stationsansatz` blockiert den älteren Körper.
- E2765: die bereits angewandte Portion wird nicht als neuer
  Behandlungspatient fortgetragen.
- E3147: ein nur aktionsintern umgeleiteter Strom wird ohne Weg-/Kanalsignal
  nicht zum Behandlungspatienten; E3650 behält den Strom gerade wegen dieses
  Signals.
- E3200: zwei unmittelbarere Maßparameter blockieren die ferne
  Stationsanapher. Ein einzelnes Maß darf übersprungen werden, wie E3707 zeigt.

E3749 verwendet entsprechend nach vollzogenem Transfer wieder die stabile
Stationseinheit. Diese Entscheidungen sind als offene Werkstattkarten und
nicht als neue Wurzelbedeutungen modelliert.

## Kartenprofil

| Typkarte | Funktion | n |
|---|---|---:|
| `T01_WRITTEN_TYPED_OBJECT` | geschriebenes GDT589-Packet | 219 |
| `T02_ACTION_INTERNAL_OBJECT` | Strom oder Stationsbedingung | 40 |
| `T03_BOUND_COMPATIBLE_REFERENCE` | kompatible linke/rechte Quelle | 81 |
| `T04_STABLE_CLASS_DEFAULT` | Stationseinheit bei WÄHLEN | 6 |
| `T05_WORKPIECE_DEFAULT` | Stationsansatz bei BEHANDELN/TEMPERIEREN | 50 |

Die drei unabhängigen Bezugskarten sind linke Anapher (77), rechtes definites
Ereigniskomplement (4) und lokal/defaultmäßig definit (315).

| GDT584-Regel | trägerloser Default | kompatible Referenzklassen |
|---|---|---|
| CHD_BIO_TREAT | Stationsansatz | Teilnehmer, aber kein Maß/keine Bedingung |
| S_BIO_DIVERT | Strom | trägerlos immer aktionsintern |
| S_REST_SELECT | Stationseinheit | alle Gegenstandsklassen außer Bedingung |
| T_AFTER_SH_COOL | Körper als Notdefault | bevorzugt SH desselben Ereignisses |
| T_BIO_RELATION_REGULATE | Stationsansatz als Notdefault | bevorzugt SH desselben Ereignisses |
| T_BIO_STATION_REGULATE | Stationsbedingung | trägerlos immer aktionsintern |
| T_PHYSICAL_GRADE_TEMPER | Stationsansatz | Teilnehmer, aber kein Maß/keine Bedingung |

Q01 rendert `derselbe/dieselbe/dasselbe`, Q02 und Q03
`der/die/das`. Alle sechs Modus×Genus-Zellen kommen im Replay vor und erzeugen
18 beobachtete Objektformen.

## Manuelle Werkstatt und Grenze

Der vollständige manuelle Pass über die 177 trägerlosen Klauseln bestätigt die
Grundtopologie. Das kompakte 17-Karten-Deck hält alle Entscheidungen fest, bei
denen ein Objekt, Scope oder Bindungsweg besonders sichtbar konkurriert. Neun
Zeilen werden zusätzlich automatisch als übersprungene oder blockierte
Referenzen ausgegeben; keine gewählte linke Quelle liegt weiter als vier Hosts.

Die Ausgabe ist eine vollständige, austauschbare deutsche Arbeitslesung und
kein behaupteter Klartext. Strukturroots und deutsche Wörter bleiben getrennte
Spalten. Ein besserer konkreter Gegenstand darf eine Defaultkarte ersetzen,
ohne geschriebene Slots oder die Oberfläche umzudeuten.
