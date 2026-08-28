# GDT596 — kompositionelles Bad-Scope-Phrasebook

Status: `PASS_254_EXACT_COMPOSITIONAL_REPLAYS__5_TYPING_CARDS__3_REFERENCE_SCOPE_CARDS__100_WRITTEN__25_BLOCKER__74_BOUND_REFERENCE__12_AIN_OR_TYPE__43_BODY_DEFAULT__70_LEFT_ANAPHORIC__9_RIGHT_OR_TIE_DEFINITE__175_LOCAL_OR_DEFAULT_DEFINITE__7_LEMMAS__11_OBJECT_FORMS__15_MODIFIER_FRAGMENTS__40_OBSERVED_SEQUENCES__184_DEFINITE__70_ANAPHORIC__247_SINGLE_7_MULTI_PARTICIPANT__0_EXCEPTIONS__23_WORKSHOP_REVIEWS__16_STYLE__6_OBJECT_RIVAL__1_BINDING_RIVAL__2_IMMEDIATE_OBJECT_FORKS`

## Kurzfassung

Alle 254 konkreten GDT595-Badeklauseln entstehen ohne Einzel-Ausnahme aus fünf
Typkarten, drei unabhängigen Bezugskarten, sieben Objektlemmas, vier Artikelregeln, zwei
Badrahmen, fünfzehn Modifikatorfragmenten und drei einfachen Listenregeln.
AIIN-Füllung bleibt ein Modifikator und wählt niemals den Patienten.

## Die fünf Typregeln

| Karte | Regel | n | Klassen | Referenz |
|---|---|---:|---|---|
| `T01_WRITTEN_TYPED_OBJECT` | Geschriebener Objektträger gewinnt | 100 | `BATH_UNIT:6|BODY:52|PORTION:2|STATION:40` | `DEFINITE:100` |
| `T02_BLOCKER_STATION` | Blockierter leerer SH-Slot wird Station | 25 | `STATION:25` | `DEFINITE:25` |
| `T03_BOUND_TYPED_REFERENCE` | Gebundene getypte Quelle kopieren | 74 | `BATH_UNIT:5|BODY:5|FLOW:2|PORTION:5|STATION:57` | `ANAPHORIC:65|DEFINITE:9` |
| `T04_STABLE_AIN_OR_TYPE` | Gelernten AIN/OR-Typ verwenden | 12 | `BATH_UNIT:4|PORTION:8` | `ANAPHORIC:5|DEFINITE:7` |
| `T05_BODY_FIRST_DEFAULT` | Leerer, blockerfreier Slot erhält Körper | 43 | `BODY:43` | `DEFINITE:43` |

Arbeitsreihenfolge: **geschriebener Träger → Blocker-Station → gebundene getypte
Quelle → stabiler AIN/OR-Typ → Körperdefault**.
Sie liefert immer einen Default; Rivalen werden markiert, nicht in einen Stop verwandelt.
Maximal zusammengezogen sind das drei Werkstattoperatoren: `T` liest einen
geschriebenen oder stabil gelernten Typ (112), `R` kopiert eine gebundene getypte
Quelle (74), und `D` setzt den Hostdefault Station oder Körper (68). Die fünf Karten
bewahren innerhalb dieser Kurznotation die entscheidenden Unterfälle.

## Die drei unabhängigen Bezugsregeln

| Karte | Richtung | Ausgabe | n | Klassen |
|---|---|---|---:|---|
| `Q01_LEFT_ANAPHORIC` | `LEFT` | `ANAPHORIC` | 70 | `BATH_UNIT:7|BODY:3|FLOW:2|PORTION:8|STATION:50` |
| `Q02_RIGHT_OR_TIE_DEFINITE` | `RIGHT` | `DEFINITE` | 9 | `BODY:2|STATION:7` |
| `Q03_LOCAL_OR_DEFAULT_DEFINITE` | `LOCAL_OR_DEFAULT` | `DEFINITE` | 175 | `BATH_UNIT:8|BODY:95|PORTION:7|STATION:65` |

Die zweite Karte umfasst acht echte rechte Endträger und E2952 als sichtbare
Links/Rechts-Pakettie; sie verschweigt diese eine Sonderprovenienz nicht.

## Objekt-NP

| Klasse | Lemma | Bezug | Form | n |
|---|---|---|---|---:|
| `BATH_UNIT` | Badeinheit | `ANAPHORIC` | dieselbe Badeinheit | 1 |
| `BATH_UNIT` | Badeinheit | `DEFINITE` | die Badeinheit | 8 |
| `BATH_UNIT` | Becken- oder Körpereinheit | `ANAPHORIC` | dieselbe Becken- oder Körpereinheit | 2 |
| `BATH_UNIT` | Stationseinheit | `ANAPHORIC` | dieselbe Stationseinheit | 4 |
| `BODY` | Körper | `ANAPHORIC` | denselben Körper | 3 |
| `BODY` | Körper | `DEFINITE` | den Körper | 97 |
| `FLOW` | Strom | `ANAPHORIC` | denselben Strom | 2 |
| `PORTION` | Anwendungsportion | `ANAPHORIC` | dieselbe Anwendungsportion | 8 |
| `PORTION` | Anwendungsportion | `DEFINITE` | die Anwendungsportion | 7 |
| `STATION` | Stationsansatz | `ANAPHORIC` | denselben Stationsansatz | 50 |
| `STATION` | Stationsansatz | `DEFINITE` | den Stationsansatz | 72 |

Maskulin: `den/denselben`; feminin: `die/dieselbe`. Daraus entstehen die elf
beobachteten Formen. 70 linke Bezüge sind anaphorisch, 184 übrige Formen definit.

## Modifikatoren

| Karte | Wurzel | Phrase | n |
|---|---|---|---:|
| `M01_FILL` | `AIIN_FILL` | bei der angegebenen Füllung | 11 |
| `M02_APPLY` | `O` | in Anwendungsform | 11 |
| `M03_GRADE_III` | `EEE` | auf Grad III | 1 |
| `M04_GRADE_II` | `EE` | auf Grad II | 61 |
| `M05_GRADE_I` | `E` | auf Grad I | 166 |
| `M06_FINE` | `LOCAL_CHAR_F` | in Feinform | 2 |
| `M07_NEW_BATCH` | `CARRIER_Q` | als neuer Bad- oder Stationsansatz | 3 |
| `M08_MAIN_SITE` | `A_ADDR` | an der Stations-Hauptstelle | 4 |
| `M09_SIDE_SITE` | `AM_ADDR` | an der Stations-Nebenstelle | 1 |
| `M10_WORK_SITE` | `D_ADDR` | an der Stations-Arbeitsstelle | 24 |
| `M11_END_SITE` | `S_ADDR` | an der Stations-Endstelle | 2 |
| `M12_TARGET` | `AL` | zur Zielstation oder ins Zielbecken | 12 |
| `M13_SOURCE` | `AR` | von der Ausgangsstation oder aus dem Ausgangsbecken | 8 |
| `M14_CONTACT` | `L` | über den Stationskontakt oder die Leitung | 31 |
| `M15_PATH` | `AIR` | entlang des Stationswegs oder Kanals | 1 |

`AIIN_FILL + Grad` bildet zuerst eine enge Gruppe (`bei der angegebenen Füllung
auf Grad …`). Alle übrigen Gruppen werden wie eine normale kurze Liste verbunden:
eine Gruppe allein, zwei mit `und`, drei oder mehr mit Kommas und letztem `und`.
Diese eine Regel erzeugt alle 40 beobachteten Modifikatorfolgen exakt.

## Satzbau

```text
HALTE + TEILNEHMERLISTE + (im Bad | im Badbetrieb) + MODIFIKATORLISTE
```

247 Aktionen haben einen Teilnehmer, sechs haben zwei und eine hat drei. In 251
Klauseln steht das ausgewählte Objekt zuerst; in E1433, E1648 und E1795 ist es
der zweite geschriebene Teilnehmer. Die Listenregel erhält diese Reihenfolge.

## Je ein konkretes Typbeispiel

- `T01_WRITTEN_TYPED_OBJECT` / `G407-E1433`:
  Halte die Anwendungsportion und den Stationsansatz im Bad auf Grad I und über den Stationskontakt oder die Leitung
- `T02_BLOCKER_STATION` / `G407-E1489`:
  Halte den Stationsansatz im Bad auf Grad I und an der Stations-Arbeitsstelle
- `T03_BOUND_TYPED_REFERENCE` / `G407-E1445`:
  Halte dieselbe Anwendungsportion im Bad auf Grad II
- `T04_STABLE_AIN_OR_TYPE` / `G407-E1560`:
  Halte dieselbe Stationseinheit im Bad auf Grad I
- `T05_BODY_FIRST_DEFAULT` / `G407-E1431`:
  Halte den Körper im Bad auf Grad I

## Ergebnis und Grenze

254/254 Klauseln werden bytegenau rekonstruiert; es gibt keine Sonderausnahme.
Die sechs GDT595-Hostbindungsrivalen bleiben im Replay markiert und behalten den
gewählten Default. Das Phrasebook komprimiert eine explorative Arbeitsübersetzung.
Eine vollständige manuelle Werkstattlektüre markiert zusätzlich 16 flache Stil-/
Scopeformulierungen, sechs Objektrivalen und eine Bindungsmechanismus-Gabel. Nur
E2952 und E3224 sind unmittelbare Objektgabeln; alle 23 Arbeitsdefaults bleiben aktiv.
Es bestätigt weder Klartext noch globale Lexeme, reale Stoffe, Patienten oder
Verfahren und öffnet keine neue Seite, Wurzel, Surface oder Segmentierung.
