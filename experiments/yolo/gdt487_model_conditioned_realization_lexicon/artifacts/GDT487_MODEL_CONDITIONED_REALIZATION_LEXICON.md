# GDT487 — modellgebundenes deutsches Realisierungslexikon

GDT487 dreht die 48 GDT486-Paare um: Nicht mehr die Kante, sondern jeder einzelne Bedeutungswert ist der Einstieg. Jede beobachtete deutsche Form ist an konkrete Kontrastrecords gebunden; unbelegte Modellzellen bleiben `OPEN`.

- Bedeutungswerte: **13**.
- Komponenten×Modell-Zellen: **25 beobachtet / 14 offen**.
- Unterschiedliche beobachtete Realisierungsformen: **29** aus **56** Record×Wert-Zeugen.
- Einzelregeln: **16** = 13 lokale Zyklen + 1 externer Brückenzyklus + 2 nur am Endpunkt verankerte Regeln; völlig unverankert: **0**.

## Lexikon der dreizehn Werte

| Wert | Wurzel/Schicht | Klasse | Katalog | Koordinate | Anweisung | lokale Wiederholkanten | Anker |
|---|---|---|---|---|---|---:|---|
| `ANTEIL` | `AIN` | ARGUMENT | Anteils- (Koordination)<br>Anteilsangabe | Sektoranteil | Drogenanteil | 3 | LOCAL_RECURRENT_GRAPH |
| `AUSGANG` | `AR` | RELATION | Ausgangszuordnung | Ausgangsposition | ausgehend von der Ausgangsposition<br>von der Ausgangsposition aus | 4 | LOCAL_RECURRENT_GRAPH |
| `BAHN` | `AIR` | RELATION | Bahnvermerk | OPEN | OPEN | 1 | LOCAL_RECURRENT_GRAPH |
| `DANACH` | `OT` | ORDER_CONTROL | Folgevermerk | OPEN | OPEN | 0 | DIRECT_TO_LOCAL_RECURRENT_GRAPH |
| `EINHEIT` | `OR` | ARGUMENT | Einheitsangabe | OPEN | OPEN | 1 | LOCAL_RECURRENT_GRAPH |
| `EINSTELLEN` | `T` | ACTION | OPEN | OPEN | stelle … ein | 0 | EXTERNAL_ACTION_ENDPOINT_ANCHOR |
| `FORTSETZEN` | `OL` | ORDER_CONTROL | OPEN | OPEN | Führe das Setzen … fort | 1 | LOCAL_RECURRENT_GRAPH |
| `HALTEN` | `SH` | ACTION | OPEN | OPEN | halte ihn | 0 | EXTERNAL_ACTION_ENDPOINT_ANCHOR |
| `HIER` | `LOCAL_HIER` | LOCAL_SCOPE | Hier-Vermerk | bezeichnete Stelle | an der bezeichneten Stelle | 4 | LOCAL_RECURRENT_GRAPH |
| `POSTEN` | `Y` | ARGUMENT | Postenangabe | Positionsposten | Positionsposten | 4 | LOCAL_RECURRENT_GRAPH |
| `SCHLUSS` | `LICENSED_CLOSE_HULL` | LOCAL_SCOPE | OPEN | OPEN | schließe den Schritt | 2 | LOCAL_RECURRENT_GRAPH |
| `WERT` | `AIIN` | ARGUMENT | Wertangabe | Positionswert | Mengenwert<br>Positionswert | 1 | LOCAL_RECURRENT_GRAPH |
| `ZIELORT` | `AL` | RELATION | Zielzuordnung | Zielposition | am Zielgefäß<br>zur Zielposition | 5 | LOCAL_RECURRENT_GRAPH |

`OPEN` heißt nur, dass der enge GDT486-Kontraststapel in diesem Modell keine Form isoliert. Es ist keine Erlaubnis, eine Form zu erfinden und kein Gegenbeispiel gegen den Wert.

## Die sechzehn Einzelregeln

| Regel | Wechsel | Rahmen | Triangulation | Pfad/Anker |
|---|---|---|---|---|
| `G486-CR06` | `DANACH ↔ EINHEIT` | `CATALOGUE_ENTRY` | `EXTERNAL_TO_LOCAL_CYCLE` | DANACH —GDT429→ FORTSETZEN → ZIELORT → ANTEIL → EINHEIT |
| `G486-CR07` | `EINHEIT ↔ HIER` | `CATALOGUE_ENTRY` | `LOCAL_RECURRENT_CYCLE` | EINHEIT → ANTEIL → HIER |
| `G486-CR08` | `HIER ↔ ZIELORT` | `CATALOGUE_ENTRY` | `LOCAL_RECURRENT_CYCLE` | HIER → ZIELORT |
| `G486-CR10` | `AUSGANG ↔ ZIELORT` | `CATALOGUE_SEQUENCE` | `LOCAL_RECURRENT_CYCLE` | AUSGANG → HIER → ZIELORT |
| `G486-CR11` | `ANTEIL ↔ ZIELORT` | `COORDINATE_AFTER` | `LOCAL_RECURRENT_CYCLE` | ANTEIL → ZIELORT |
| `G486-CR12` | `AUSGANG ↔ HIER` | `COORDINATE_AFTER` | `LOCAL_RECURRENT_CYCLE` | AUSGANG → HIER |
| `G486-CR13` | `AUSGANG ↔ ZIELORT` | `COORDINATE_AFTER` | `LOCAL_RECURRENT_CYCLE` | AUSGANG → HIER → ZIELORT |
| `G486-CR14` | `HIER ↔ ZIELORT` | `COORDINATE_AFTER` | `LOCAL_RECURRENT_CYCLE` | HIER → ZIELORT |
| `G486-CR15` | `POSTEN ↔ WERT` | `COORDINATE_AFTER` | `LOCAL_RECURRENT_CYCLE` | POSTEN → AUSGANG → WERT |
| `G486-CR16` | `AUSGANG ↔ ZIELORT` | `INSTRUCTION_HALTEN` | `LOCAL_RECURRENT_CYCLE` | AUSGANG → HIER → ZIELORT |
| `G486-CR17` | `EINSTELLEN ↔ HIER` | `INSTRUCTION_NEHMEN` | `EXTERNAL_ENDPOINT_ANCHOR_ONLY` | EINSTELLEN —GDT428→ MARKIEREN; anderer Endpunkt HIER liegt lokal |
| `G486-CR18` | `ANTEIL ↔ WERT` | `INSTRUCTION_SETZEN` | `LOCAL_RECURRENT_CYCLE` | ANTEIL → HIER → AUSGANG → WERT |
| `G486-CR22` | `AUSGANG ↔ ZIELORT` | `INSTRUCTION_SETZEN` | `LOCAL_RECURRENT_CYCLE` | AUSGANG → HIER → ZIELORT |
| `G486-CR24` | `HALTEN ↔ ZIELORT` | `INSTRUCTION_SETZEN` | `EXTERNAL_ENDPOINT_ANCHOR_ONLY` | HALTEN —GDT428→ BEARBEITEN; anderer Endpunkt ZIELORT liegt lokal |
| `G486-CR26` | `HIER ↔ SCHLUSS` | `INSTRUCTION_SETZEN` | `LOCAL_RECURRENT_CYCLE` | HIER → AUSGANG → SCHLUSS |
| `G486-CR27` | `HIER ↔ WERT` | `INSTRUCTION_SETZEN` | `LOCAL_RECURRENT_CYCLE` | HIER → AUSGANG → WERT |

Dreizehn Einzelkanten besitzen bereits einen alternativen Weg ausschließlich durch die dreizehn wiederkehrenden GDT486-Regeln. `DANACH ↔ EINHEIT` erhält einen vollständigen Zyklus über GDT429s vierzehn exakte `DANACH ↔ FORTSETZEN`-Rahmen und den lokalen Weg von FORTSETZEN zu EINHEIT.

`EINSTELLEN ↔ HIER` und `HALTEN ↔ ZIELORT` haben noch keinen zweiten lokalen Weg. Ihre Aktionsenden hängen aber nicht frei: GDT428 trägt EINSTELLEN über elf exakte T/R-Rahmen gegen MARKIEREN und HALTEN über vierzehn SH/CHD-Rahmen gegen BEARBEITEN. Diese beiden Regeln bleiben deshalb **endpoint-anchored**, nicht zyklisch geschlossen.

## Drei geerbte Kontrastanker

| Wert | alter Kontrast | exakte Rahmen | Partner | Rolle im Netz |
|---|---|---:|---|---|
| `DANACH` | `GDT429 OL~OT` | 14 | `FORTSETZEN` | `DIRECT_TO_LOCAL_RECURRENT_GRAPH` |
| `EINSTELLEN` | `GDT428 T~R` | 11 | `MARKIEREN` | `EXTERNAL_ACTION_ENDPOINT_ANCHOR` |
| `HALTEN` | `GDT428 SH~CHD` | 14 | `BEARBEITEN` | `EXTERNAL_ACTION_ENDPOINT_ANCHOR` |

## Konsequenz

Das Realisierungslexikon sagt jetzt nicht mehr nur `ZIELORT`, sondern wo der Wert tatsächlich wie gesprochen wird: im Katalog als „Zielzuordnung“, in Koordinaten als „Zielposition“ und in Anweisungen als „zur Zielposition“ oder pharmazeutisch „am Zielgefäß“. Entsprechend trennt es `WERT` in Wertangabe, Positionswert und Mengenwert, ohne daraus drei Wörterbuchbedeutungen zu machen.

Der nächste engste Schritt ist klar: Suche innerhalb der vorhandenen 135 Records nach je einem zweiten, nur leicht gelockerten Satzrahmen für EINSTELLEN und HALTEN. Die übrigen vierzehn Einzelregeln besitzen bereits einen alternativen Kontrastweg; globale Umdeutung wäre derzeit kontraproduktiv.
