# Gesamtes Wörterbuch als Hierarchie

Die Werkstatt besitzt nicht ein flaches Wörterbuch, sondern sieben sauber
getrennte Ebenen. Nur Ebene 1 und die beobachteten Teile von Ebene 2 sind
Kartenbedeutungen. Alles darüber erklärt, wie Karten verwendet, ergänzt oder
aus Bildern und Registern konkretisiert werden.

## L1_ATOMIC_ROOT (28)

short reusable card value. read first inside a registered composition.

- `AIIN` — **sollwert**
- `AIN` — **portion**
- `IIN` — **stufe**
- `AL` — **ziel**
- `AR` — **quelle**
- `AIR` — **Lauf/Bahn**
- `OK` — **ansetzen**
- `OL` — **fortsetzen**
- `OT` — **folgend**
- `OR` — **Ansatz**
- `Y` — **dieser Posten**
- `E` — **kurz**
- `EE` — **laenger**
- `EEE` — **voll**
- `CLOSE` — **schluss**
- `CHD` — **umsetzen**
- `CTH` — **bereit**
- `CKH` — **durchlauf**
- `CKHE` — **trennen**
- `CHK` — **waermen**
- `SHED` — **absetzen**
- `SOLK` — **sammeln**
- `HO` — **eingangsposten**
- `CHEO` — **Auszug**
- `KCH` — **bearbeiten**
- `TY` — **teil**
- `SH` — **halten**
- `CHEEY` — **sichtbares Ergebnis**

## L2_LEARNED_NOMENCLATOR (15)

memorized technical body, whole card, or register split. longest learned form outranks shorter visible resemblance.

- `cfhy` — **auswringen**
- `cphy|ocphy` — **zweiter durchgang**
- `ches|chety|chty` — **abteilen**
- `cho|sho|tshol` — **eingangsposten**
- `dchey` — **unterer pflanzenteil**
- `dchol|schol` — **voriger posten**
- `lshedy|lsho|rshedy` — **waschgang**
- `qokylddy` — **festmachen und schließen**
- `skar` — **ausgiessen**
- `sotodan` — **anwenden**
- `dl` — **zusatz**
- `talam` — **am ziel verwahren**
- `dain` — **Prosa: Tuch / Astro: Portion**
- `ody` — **Prosa: kühlen / Astro: markieren**
- `os` — **Prosa: Gefäß / Astro: Feld**

## L2B_SIMULATED_MASTER_SUPPLEMENT (4)

neutral missing-card category. training placeholder only; never a manuscript surface.

- `[M01]` — **wärmen**
- `[M02]` — **trennen**
- `[M03]` — **kurz schluss**
- `[M04]` — **laenger schluss**

## L3_SILENT_MEMORY_REGISTER (4)

record-local referent carried by the scribe. expands ellipsis but is never a word gloss.

- `<OWNER>` — **welches Bildobjekt oder welche lokale Station die stillen Substantive liefert**
- `<ACTIVE>` — **der gerade bearbeitete Posten oder Ansatz**
- `<TARGET>` — **die örtlich bezeichnete Zielstelle, Öffnung, Schale oder Tabellenzelle**
- `<PREVIOUS>` — **genau den unmittelbar zuvor abgelegten oder verdrängten Posten**

## L4_PROCESS_MACRO (20)

recurring two- or three-clause move. helps execute a dossier but never defines one card.

- `CONTINUE>CONTINUE>CONTINUE` — **denselben Gang über drei Teilposten fortführen**
- `SET>CONTINUE>SETTLE` — **ansetzen, im selben Gang weiterführen und absetzen lassen**
- `TRANSFER>CONTINUE>LEAD_OUT` — **umsetzen, weiterführen und am Ende abführen**
- `READY>DIVIDE` — **bereitstellen und einen Teil abtrennen**
- `CONTINUE>SET` — **weiterführen und den nächsten Posten ansetzen**
- `SET>CONTINUE` — **ansetzen und im selben Gang weiterführen**
- `SET>PASSAGE` — **ansetzen und durch den örtlichen Gang führen**
- `PASSAGE>SET` — **durchleiten und am folgenden Posten ansetzen**
- `SET>READY` — **ansetzen und bereitstellen**
- `SET>SETTLE` — **ansetzen und absetzen lassen**
- `CONTINUE>SETTLE` — **weiterführen und absetzen lassen**
- `READY>SET` — **den bereitgestellten Posten ansetzen**
- `TRANSFER>SET` — **umsetzen und neu ansetzen**
- `SET>TRANSFER` — **ansetzen und umsetzen**
- `TRANSFER>CONTINUE` — **umsetzen und weiterführen**
- `CONTINUE>LEAD_OUT` — **weiterführen und abführen**
- `CONTINUE>TRANSFER` — **weiterführen und umsetzen**
- `WARM>CONTINUE` — **erwärmen und im selben Gang weiterführen**
- `SET>SET` — **zwei aufeinanderfolgende Setzungen ausführen**
- `CONTINUE>CONTINUE` — **denselben Gang über zwei Teilposten fortführen**

## L5_VISIBLE_OWNER (5)

picture or station supplies concrete nouns and addresses. owner content may not leak into the root.

- `BASIN_STATION` — **die aktuelle Beckencharge**
- `CELESTIAL_TABLE` — **der aktuelle Tabellenwert**
- `CLOTH_FILTER` — **der aktuelle Tuchposten**
- `GENERIC_WORKPIECE` — **das aktuelle Werkstück**
- `PLANT_BATCH` — **der aktuelle Pflanzenposten**

## L6_ASTRO_LOCAL_MODULE (13)

local diagram namespace and lookup instruction. never exported across wheels, panels, pages, or into prose.

- `RIGHT_CELESTIAL_WHEEL` — **Notiere eine einzelne Bedingungs- oder Vergleichsangabe für den Arbeitsfall.**
- `LEFT_CELESTIAL_WHEEL` — **Notiere eine einzelne Bedingungs- oder Vergleichsangabe für den Arbeitsfall.**
- `UNRESOLVED_PAGE_LEGEND` — **Notiere eine einzelne Bedingungs- oder Vergleichsangabe für den Arbeitsfall.**
- `LEFT_PANEL_HEADER` — **Notiere Stationsklasse und Bedingungswert, ohne die 28 Sterne zu einer Folge zu zwingen.**
- `MIDDLE_PANEL_HEADER` — **Notiere Stationsklasse und Bedingungswert, ohne die 28 Sterne zu einer Folge zu zwingen.**
- `RIGHT_PANEL_HEADER` — **Notiere Stationsklasse und Bedingungswert, ohne die 28 Sterne zu einer Folge zu zwingen.**
- `UNRESOLVED_MULTIPANEL_HEADER` — **Notiere Stationsklasse und Bedingungswert, ohne die 28 Sterne zu einer Folge zu zwingen.**
- `UNRESOLVED_FACE_CENTRE_KEY` — **Notiere Stationsklasse und Bedingungswert, ohne die 28 Sterne zu einer Folge zu zwingen.**
- `LOCAL_STAR_SLOT_POOL` — **Notiere Stationsklasse und Bedingungswert, ohne die 28 Sterne zu einer Folge zu zwingen.**
- `UNRESOLVED_CENTRAL_LEGEND` — **Notiere Stationsklasse und Bedingungswert, ohne die 28 Sterne zu einer Folge zu zwingen.**
- `LEFT_WHEEL_WITH_28_UNORDERED_SLOTS` — **Notiere bis zu drei getrennte Werte, wenn der Meister sie für denselben Auftrag zusammenstellt.**
- `MIDDLE_WAVE_OR_CLOUD_WHEEL` — **Notiere bis zu drei getrennte Werte, wenn der Meister sie für denselben Auftrag zusammenstellt.**
- `RIGHT_FACE_RAY_WHEEL` — **Notiere bis zu drei getrennte Werte, wenn der Meister sie für denselben Auftrag zusammenstellt.**
