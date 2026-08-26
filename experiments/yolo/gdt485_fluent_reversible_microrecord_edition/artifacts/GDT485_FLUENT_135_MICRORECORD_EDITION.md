# GDT485 — flüssige, rückführbare Ausgabe der 135 Mikrorecords

Diese Ausgabe besitzt zwei gleichzeitige Kanäle: eine kurze deutsche Werkstattfassung zum Lesen und die unveränderte technische GDT484-Fassung zur Rückprojektion. Komponenten, Eventgrenzen, Namen und OT/OL-Spuren bleiben separat sichtbar; die Glättung ersetzt keinen davon.

- Werkstattfassungen: **135/135**.
- Exakte Event-Rückprojektionen: **183/183**.
- Unverändert bereits flüssig: **14**; redaktionell geglättet: **121**.
- Ausgelagerte Reihenfolgespuren: **54 Records / 69 OT/OL-Stellen**.

## Was die Redaktion entfernt hat

| mechanischer Marker | technische Fassung | Werkstattfassung | Differenz |
|---|---:|---:|---:|
| eingeschobener OT/OL-Metasatz | 57 | 0 | 57 |
| nummerierter Eventmarker | 67 | 0 | 67 |
| technischer Adresspfeil | 52 | 0 | 52 |
| vorangestelltes Weiter + Imperativ | 12 | 0 | 12 |
| wörtlich doppeltes Weiter | 1 | 0 | 1 |
| Arbeitsgang als eigener Metapräfix | 6 | 0 | 6 |
| zugehörige Adressspur als Metapräfix | 2 | 0 | 2 |
| mit Schrägstrich verbundene Kataloglabels | 10 | 0 | 10 |
| Komma vor Schrittabschluss | 4 | 0 | 4 |

Die OT/OL-Angaben sind dabei nicht gelöscht: Sie stehen pro Record im Feld `exact_order_scope_trace_de` und pro Event nochmals mit Wurzel-, Zustands- und Orientierungsfolge.

## Redaktionsgriffe

| Griff | Records | Erklärung |
|---|---:|---|
| `ALREADY_FLUENT` | 14 | technische Fassung war bereits flüssig |
| `CATALOGUE_PROSE` | 53 | Katalogsyntax in kurze deutsche Prosa überführt |
| `CONTINUATION_SMOOTHED` | 17 | FORTSETZEN-Konstruktion geglättet |
| `COORDINATE_PROSE` | 26 | Adresspfeile als deutscher Satz wiedergegeben |
| `DUPLICATE_COLLAPSED` | 15 | sichtbare Wiederholung als Anzahl/Mehrzahl formuliert |
| `GDT483_RETAINED` | 1 | GDT483-sodar-Fassung unverändert übernommen |
| `LIST_COMPACTED` | 28 | nummerierte Eventliste zu einer Satzfolge verdichtet |
| `MULTI_LOCUS_SMOOTHED` | 8 | mehrere verbundene Loci als ein Arbeitsgang redigiert |
| `OBJECT_REFERENCE_SMOOTHED` | 21 | wiederholtes Objekt durch Pronomen/Mehrzahl ersetzt |
| `ORDER_TRACE_SEPARATED` | 54 | OT/OL-Metakommentar in eigenes Spurfeld ausgelagert |
| `PUNCTUATION_SMOOTHED` | 3 | technische Interpunktion geglättet |
| `QUALIFIER_REORDERED` | 12 | Qualifikatoren in natürlichere deutsche Stellung gebracht |
| `SAME_GANG_SMOOTHED` | 11 | Arbeitsgang-Metapräfix in den Satz integriert |

## Vollständige Ausgabe

### f17r · HERBAL

#### G475-R001 · `oteeeon|oiil`

- **Werkstattfassung:** Katalogfolge: Pflanzenname »eeeon« mit Folgevermerk; Pflanzenname »oiil«.
- Technische Fassung: 1. Pflanzenname »eeeon« — Folgevermerk. 2. Pflanzenname »oiil«. Reihenfolge konkret: OT — danach Pflanze »eeeon«.
- Komponenten: `DANACH · {N1} || {N1}`
- OT/OL-Spur: `OT:danach Pflanze »eeeon«`
- Herkunft: Stufe 4 · mindestens ein striktes Parallelevent.

### f71v · CELESTIAL

#### G475-R002 · `char|arom`

- **Werkstattfassung:** Katalogfolge: Eintrag »char« mit Ausgangszuordnung; Sternstelle »om« mit Ausgangszuordnung.
- Technische Fassung: 1. Eintrag »char« — Ausgangszuordnung. 2. Sternstelle »om« — Ausgangszuordnung.
- Komponenten: `AUSGANG || AUSGANG · {N1}`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 2 · vollständige Rollenform wiederholt sich.

#### G475-R003 · `chfaly`

- **Werkstattfassung:** Sternstelle »chf« mit Zielzuordnung und Postenangabe.
- Technische Fassung: Sternstelle »chf« — Zielzuordnung, Postenangabe.
- Komponenten: `{N1} · ZIELORT · POSTEN`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R004 · `okolar`

- **Werkstattfassung:** Führe das Setzen des Eintrags von der Ausgangsposition aus fort.
- Technische Fassung: Weiter setze den Eintrag von der Ausgangsposition. Reihenfolge konkret: OL — Setzen in Ausgang weiterführen.
- Komponenten: `SETZEN · FORTSETZEN · AUSGANG`
- OT/OL-Spur: `OL:Setzen in Ausgang weiterführen`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R005 · `otchody`

- **Werkstattfassung:** Sternstelle »chody« mit Folgevermerk.
- Technische Fassung: Sternstelle »chody« — Folgevermerk. Reihenfolge konkret: OT — danach Sternstelle »chody«.
- Komponenten: `DANACH · {N1}`
- OT/OL-Spur: `OT:danach Sternstelle »chody«`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R006 · `alcphy`

- **Werkstattfassung:** Nimm den Positionsposten auf und setze ihn zur Zielposition ein.
- Technische Fassung: Nimm den Positionsposten auf und setze den Positionsposten ein zur Zielposition.
- Komponenten: `ZIELORT · NEHMEN · EINSETZEN · POSTEN`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R007 · `otaiin`

- **Werkstattfassung:** Die Adressspur führt danach zum Positionswert.
- Technische Fassung: Adressspur: danach → Positionswert. Reihenfolge konkret: OT — danach Wert.
- Komponenten: `DANACH · WERT`
- OT/OL-Spur: `OT:danach Wert`
- Herkunft: Stufe 3 · alle Events besitzen strikte Parallelträger.

#### G475-R008 · `okaraiin`

- **Werkstattfassung:** Setze den Positionswert von der Ausgangsposition aus.
- Technische Fassung: Setze den Positionswert von der Ausgangsposition.
- Komponenten: `SETZEN · AUSGANG · WERT`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 2 · vollständige Rollenform wiederholt sich.

#### G475-R009 · `otar|ar|aly`

- **Werkstattfassung:** Die erste Adressspur weist danach zur Ausgangsposition. Die zweite bezeichnet die Ausgangsposition. Die dritte führt von der Zielposition zum Positionsposten.
- Technische Fassung: 1. Adressspur: danach → Ausgangsposition. 2. Adressspur: Ausgangsposition. 3. Adressspur: Zielposition → Positionsposten. Reihenfolge konkret: OT — danach Ausgang.
- Komponenten: `DANACH · AUSGANG || AUSGANG || ZIELORT · POSTEN`
- OT/OL-Spur: `OT:danach Ausgang`
- Herkunft: Stufe 4 · mindestens ein striktes Parallelevent.

#### G475-R010 · `opalar|am|dan`

- **Werkstattfassung:** Die erste Adressspur führt von Sternstelle »op« über die Zielposition zur Ausgangsposition. Die zweite bezeichnet die bezeichnete Stelle, die dritte den Sektoranteil.
- Technische Fassung: 1. Adressspur: Sternstelle »op« → Zielposition → Ausgangsposition. 2. Adressspur: hier. 3. Adressspur: Sektoranteil.
- Komponenten: `{N1} · ZIELORT · AUSGANG || HIER || ANTEIL`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 6 · mindestens ein Rollenparallelevent.

#### G475-R011 · `opalor|ar`

- **Werkstattfassung:** Katalogfolge: Sternstelle »op« mit Zielzuordnung und Einheitsangabe; Eintrag »ar« mit Ausgangszuordnung.
- Technische Fassung: 1. Sternstelle »op« — Zielzuordnung, Einheitsangabe. 2. Eintrag »ar« — Ausgangszuordnung.
- Komponenten: `{N1} · ZIELORT · EINHEIT || AUSGANG`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 4 · mindestens ein striktes Parallelevent.

#### G475-R012 · `ofaom`

- **Werkstattfassung:** Sternstelle »aom« mit Ausführungs- und Hier-Vermerk.
- Technische Fassung: Sternstelle »aom« — Ausführungsvermerk, Hier-Vermerk.
- Komponenten: `AUSFÜHRUNG · HIER · {N1}`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R013 · `otalody`

- **Werkstattfassung:** Sternstelle »ody« mit Folgevermerk und Zielzuordnung.
- Technische Fassung: Sternstelle »ody« — Folgevermerk, Zielzuordnung. Reihenfolge konkret: OT — danach Zielort.
- Komponenten: `DANACH · ZIELORT · {N1}`
- OT/OL-Spur: `OT:danach Zielort`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R014 · `otalaiin`

- **Werkstattfassung:** Danach führt die Adressspur über die Zielposition zum Positionswert.
- Technische Fassung: Adressspur: danach → Zielposition → Positionswert. Reihenfolge konkret: OT — danach Zielort.
- Komponenten: `DANACH · ZIELORT · WERT`
- OT/OL-Spur: `OT:danach Zielort`
- Herkunft: Stufe 2 · vollständige Rollenform wiederholt sich.

#### G475-R015 · `otar|shar`

- **Werkstattfassung:** Beziehe danach den Eintrag von der Ausgangsposition und halte ihn dort.
- Technische Fassung: 1. Danach beziehe den Eintrag von der Ausgangsposition. 2. Halte den Eintrag von der Ausgangsposition. Reihenfolge konkret: OT — danach Ausgang.
- Komponenten: `DANACH · AUSGANG || HALTEN · AUSGANG`
- OT/OL-Spur: `OT:danach Ausgang`
- Herkunft: Stufe 6 · mindestens ein Rollenparallelevent.

#### G475-R016 · `sholshdy`

- **Werkstattfassung:** Halte den Sternstelleneintrag »dy« weiter und halte ihn ein zweites Mal.
- Technische Fassung: Weiter halte den Sternstelleneintrag »dy« und halte den Sternstelleneintrag »dy«. Reihenfolge konkret: OL — Halten in Halten weiterführen.
- Komponenten: `HALTEN · FORTSETZEN · HALTEN · {N1}`
- OT/OL-Spur: `OL:Halten in Halten weiterführen`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

### f72r · CELESTIAL

#### G475-R017 · `oshodady`

- **Werkstattfassung:** Halte die Sternstelleneinträge »o« und »odady«.
- Technische Fassung: Halte den Sternstelleneintrag »o« und den Sternstelleneintrag »odady«.
- Komponenten: `{N1} · HALTEN · {N2}`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R018 · `chdaiirdainy`

- **Werkstattfassung:** Sternstelle »chdaiird« mit Anteils- und Postenangabe.
- Technische Fassung: Sternstelle »chdaiird« — Anteilsangabe, Postenangabe.
- Komponenten: `{N1} · ANTEIL · POSTEN`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 5 · alle Events besitzen Rollenparallelen.

#### G475-R019 · `oaiin|ar|ary`

- **Werkstattfassung:** Drei Adressspuren: vom Ausführungspunkt zum Positionswert; die Ausgangsposition; von der Ausgangsposition zum Positionsposten.
- Technische Fassung: 1. Adressspur: Ausführungspunkt → Positionswert. 2. Adressspur: Ausgangsposition. 3. Adressspur: Ausgangsposition → Positionsposten.
- Komponenten: `AUSFÜHRUNG · WERT || AUSGANG || AUSGANG · POSTEN`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 4 · mindestens ein striktes Parallelevent.

#### G475-R020 · `okalam`

- **Werkstattfassung:** Setze den Eintrag an der bezeichneten Stelle zur Zielposition.
- Technische Fassung: Setze den Eintrag zur Zielposition an der bezeichneten Stelle.
- Komponenten: `SETZEN · ZIELORT · HIER`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 2 · vollständige Rollenform wiederholt sich.

#### G475-R021 · `ytalshdy`

- **Werkstattfassung:** Halte die Sternstelleneinträge »yt« und »dy« zur Zielposition.
- Technische Fassung: Halte den Sternstelleneintrag »yt« und den Sternstelleneintrag »dy« zur Zielposition.
- Komponenten: `{N1} · ZIELORT · HALTEN · {N2}`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 2 · vollständige Rollenform wiederholt sich.

#### G475-R022 · `char|alif`

- **Werkstattfassung:** Katalogfolge: Eintrag »char« mit Ausgangszuordnung; Sternstelle »if« mit Zielzuordnung.
- Technische Fassung: 1. Eintrag »char« — Ausgangszuordnung. 2. Sternstelle »if« — Zielzuordnung.
- Komponenten: `AUSGANG || ZIELORT · {N1}`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 2 · vollständige Rollenform wiederholt sich.

#### G475-R023 · `otaraldy`

- **Werkstattfassung:** Danach führt die Adressspur von der Ausgangsposition über die Zielposition zum Positionsposten.
- Technische Fassung: Adressspur: danach → Ausgangsposition → Zielposition → Positionsposten. Reihenfolge konkret: OT — danach Ausgang.
- Komponenten: `DANACH · AUSGANG · ZIELORT · POSTEN`
- OT/OL-Spur: `OT:danach Ausgang`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R024 · `otaiin|otain`

- **Werkstattfassung:** Die erste Adressspur führt danach zum Positionswert, die zweite danach zum Sektoranteil.
- Technische Fassung: 1. Adressspur: danach → Positionswert. 2. Adressspur: danach → Sektoranteil. Reihenfolge konkret: OT — danach Wert; OT — danach Anteil.
- Komponenten: `DANACH · WERT || DANACH · ANTEIL`
- OT/OL-Spur: `OT:danach Wert | OT:danach Anteil`
- Herkunft: Stufe 4 · mindestens ein striktes Parallelevent.

#### G475-R025 · `otalef|ys|ainam`

- **Werkstattfassung:** Beziehe danach den Sternstelleneintrag »ef« zur Zielposition; wähle den Positionsposten und im selben Gang den Sektoranteil an der bezeichneten Stelle.
- Technische Fassung: 1. Danach beziehe den Sternstelleneintrag »ef« zur Zielposition. 2. Wähle den Positionsposten. 3. Im selben Gang wähle den Sektoranteil an der bezeichneten Stelle. Reihenfolge konkret: OT — danach Zielort.
- Komponenten: `DANACH · ZIELORT · {N1} || POSTEN · WÄHLEN || ANTEIL · HIER`
- OT/OL-Spur: `OT:danach Zielort`
- Herkunft: Stufe 4 · mindestens ein striktes Parallelevent.

#### G475-R026 · `ochol|sharam`

- **Werkstattfassung:** Führe den Bezug des Eintrags als Ausführung weiter; halte ihn anschließend von der Ausgangsposition an der bezeichneten Stelle.
- Technische Fassung: 1. Weiter beziehe den Eintrag, als Ausführung. 2. Halte den Eintrag von der Ausgangsposition an der bezeichneten Stelle. Reihenfolge konkret: OL — Ausführung weiterführen.
- Komponenten: `AUSFÜHRUNG · FORTSETZEN || HALTEN · AUSGANG · HIER`
- OT/OL-Spur: `OL:Ausführung weiterführen`
- Herkunft: Stufe 6 · mindestens ein Rollenparallelevent.

#### G475-R027 · `ofaralar`

- **Werkstattfassung:** Adressfolge: Ausführungspunkt, bezeichnete Stelle, Ausgangsposition, Zielposition, erneut Ausgangsposition.
- Technische Fassung: Adressspur: Ausführungspunkt → hier → Ausgangsposition → Zielposition → Ausgangsposition.
- Komponenten: `AUSFÜHRUNG · HIER · AUSGANG · ZIELORT · AUSGANG`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R028 · `otchoshy`

- **Werkstattfassung:** Sternstelle »cho« mit Folgevermerk und Postenangabe.
- Technische Fassung: Sternstelle »cho« — Folgevermerk, Postenangabe. Reihenfolge konkret: OT — danach Sternstelle »cho«.
- Komponenten: `DANACH · {N1} · POSTEN`
- OT/OL-Spur: `OT:danach Sternstelle »cho«`
- Herkunft: Stufe 2 · vollständige Rollenform wiederholt sich.

#### G475-R029 · `otchdal`

- **Werkstattfassung:** Sternstelle »ch« mit Folgevermerk und Zielzuordnung.
- Technische Fassung: Sternstelle »ch« — Folgevermerk, Zielzuordnung. Reihenfolge konkret: OT — danach Sternstelle »ch«.
- Komponenten: `DANACH · {N1} · ZIELORT`
- OT/OL-Spur: `OT:danach Sternstelle »ch«`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R030 · `okeey|ary`

- **Werkstattfassung:** Setze den Positionsposten auf Grad II; setze ihn im selben Gang von der Ausgangsposition aus.
- Technische Fassung: 1. Setze den Positionsposten, auf Grad II. 2. Im selben Gang setze den Positionsposten von der Ausgangsposition.
- Komponenten: `SETZEN · GRAD II · POSTEN || AUSGANG · POSTEN`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R031 · `otainy`

- **Werkstattfassung:** Danach führt die Adressspur vom Sektoranteil zum Positionsposten.
- Technische Fassung: Adressspur: danach → Sektoranteil → Positionsposten. Reihenfolge konkret: OT — danach Anteil.
- Komponenten: `DANACH · ANTEIL · POSTEN`
- OT/OL-Spur: `OT:danach Anteil`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R032 · `ofchdamy`

- **Werkstattfassung:** Sternstelle »chdamy« mit Ausführungs- und Hier-Vermerk.
- Technische Fassung: Sternstelle »chdamy« — Ausführungsvermerk, Hier-Vermerk.
- Komponenten: `AUSFÜHRUNG · HIER · {N1}`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R033 · `oklairdy`

- **Werkstattfassung:** Setze die Sternstelleneinträge »l« und »dy« entlang der Ringbahn.
- Technische Fassung: Setze den Sternstelleneintrag »l« und den Sternstelleneintrag »dy« entlang der Ringbahn.
- Komponenten: `SETZEN · {N1} · BAHN · {N2}`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R034 · `okaram`

- **Werkstattfassung:** Setze den Eintrag von der Ausgangsposition aus an der bezeichneten Stelle.
- Technische Fassung: Setze den Eintrag von der Ausgangsposition an der bezeichneten Stelle.
- Komponenten: `SETZEN · AUSGANG · HIER`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 2 · vollständige Rollenform wiederholt sich.

#### G475-R035 · `okairy`

- **Werkstattfassung:** Setze den Sternstelleneintrag »y« entlang der Ringbahn.
- Technische Fassung: Setze den Sternstelleneintrag »y« entlang der Ringbahn.
- Komponenten: `SETZEN · BAHN · {N1}`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 2 · vollständige Rollenform wiederholt sich.

#### G475-R036 · `okealar`

- **Werkstattfassung:** Setze den Sternstelleneintrag »e« zur Zielposition, ausgehend von der Ausgangsposition.
- Technische Fassung: Setze den Sternstelleneintrag »e« zur Zielposition und von der Ausgangsposition.
- Komponenten: `SETZEN · {N1} · ZIELORT · AUSGANG`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R037 · `otaraldy`

- **Werkstattfassung:** Danach führt die Adressspur von der Ausgangsposition über die Zielposition zum Positionsposten.
- Technische Fassung: Adressspur: danach → Ausgangsposition → Zielposition → Positionsposten. Reihenfolge konkret: OT — danach Ausgang.
- Komponenten: `DANACH · AUSGANG · ZIELORT · POSTEN`
- OT/OL-Spur: `OT:danach Ausgang`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R038 · `okalar`

- **Werkstattfassung:** Setze den Eintrag zur Zielposition, ausgehend von der Ausgangsposition.
- Technische Fassung: Setze den Eintrag zur Zielposition und von der Ausgangsposition.
- Komponenten: `SETZEN · ZIELORT · AUSGANG`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R039 · `okal`

- **Werkstattfassung:** Setze den Eintrag zur Zielposition.
- Technische Fassung: Setze den Eintrag zur Zielposition.
- Komponenten: `SETZEN · ZIELORT`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R040 · `okaly`

- **Werkstattfassung:** Setze den Positionsposten zur Zielposition.
- Technische Fassung: Setze den Positionsposten zur Zielposition.
- Komponenten: `SETZEN · ZIELORT · POSTEN`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R041 · `okal`

- **Werkstattfassung:** Setze den Eintrag zur Zielposition.
- Technische Fassung: Setze den Eintrag zur Zielposition.
- Komponenten: `SETZEN · ZIELORT`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R042 · `okeey|ary`

- **Werkstattfassung:** Setze den Positionsposten auf Grad II; setze ihn im selben Gang von der Ausgangsposition aus.
- Technische Fassung: 1. Setze den Positionsposten, auf Grad II. 2. Im selben Gang setze den Positionsposten von der Ausgangsposition.
- Komponenten: `SETZEN · GRAD II · POSTEN || AUSGANG · POSTEN`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R043 · `oteeary`

- **Werkstattfassung:** Sternstellen »ee« und »y« mit Folgevermerk und Ausgangszuordnung.
- Technische Fassung: Sternstelle »ee« / Sternstelle »y« — Folgevermerk, Ausgangszuordnung. Reihenfolge konkret: OT — danach Sternstelle »ee«.
- Komponenten: `DANACH · {N1} · AUSGANG · {N2}`
- OT/OL-Spur: `OT:danach Sternstelle »ee«`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R044 · `otair|dy`

- **Werkstattfassung:** Die erste Adressspur führt danach zur Ringbahn; die zweite bezeichnet den Positionsposten.
- Technische Fassung: 1. Adressspur: danach → Ringbahn. 2. Adressspur: Positionsposten. Reihenfolge konkret: OT — danach Bahn.
- Komponenten: `DANACH · BAHN || POSTEN`
- OT/OL-Spur: `OT:danach Bahn`
- Herkunft: Stufe 5 · alle Events besitzen Rollenparallelen.

#### G475-R045 · `okaircham`

- **Werkstattfassung:** Setze den Sternstelleneintrag »ch« entlang der Ringbahn an der bezeichneten Stelle.
- Technische Fassung: Setze den Sternstelleneintrag »ch« entlang der Ringbahn an der bezeichneten Stelle.
- Komponenten: `SETZEN · BAHN · {N1} · HIER`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 5 · alle Events besitzen Rollenparallelen.

#### G475-R046 · `okeal`

- **Werkstattfassung:** Setze den Sternstelleneintrag »e« zur Zielposition.
- Technische Fassung: Setze den Sternstelleneintrag »e« zur Zielposition.
- Komponenten: `SETZEN · {N1} · ZIELORT`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R047 · `otar`

- **Werkstattfassung:** Danach weist die Adressspur zur Ausgangsposition.
- Technische Fassung: Adressspur: danach → Ausgangsposition. Reihenfolge konkret: OT — danach Ausgang.
- Komponenten: `DANACH · AUSGANG`
- OT/OL-Spur: `OT:danach Ausgang`
- Herkunft: Stufe 2 · vollständige Rollenform wiederholt sich.

#### G475-R048 · `okaly`

- **Werkstattfassung:** Setze den Positionsposten zur Zielposition.
- Technische Fassung: Setze den Positionsposten zur Zielposition.
- Komponenten: `SETZEN · ZIELORT · POSTEN`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R049 · `orary`

- **Werkstattfassung:** Sternstelle »y« mit Einheitsangabe und Ausgangszuordnung.
- Technische Fassung: Sternstelle »y« — Einheitsangabe, Ausgangszuordnung.
- Komponenten: `EINHEIT · AUSGANG · {N1}`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 3 · alle Events besitzen strikte Parallelträger.

#### G475-R050 · `okyd`

- **Werkstattfassung:** Setze den Sternstelleneintrag »yd«.
- Technische Fassung: Setze den Sternstelleneintrag »yd«.
- Komponenten: `SETZEN · {N1}`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R051 · `otolam`

- **Werkstattfassung:** Die Adressspur wird danach bis zur bezeichneten Stelle fortgesetzt.
- Technische Fassung: Adressspur: danach → weiter → hier. Reihenfolge konkret: OT — danach Fortsetzung; OL — Folgeschritt in bezeichnete Stelle weiterführen.
- Komponenten: `DANACH · FORTSETZEN · HIER`
- OT/OL-Spur: `OT:danach Fortsetzung | OL:Folgeschritt in bezeichnete Stelle weiterführen`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R052 · `otal`

- **Werkstattfassung:** Danach weist die Adressspur zur Zielposition.
- Technische Fassung: Adressspur: danach → Zielposition. Reihenfolge konkret: OT — danach Zielort.
- Komponenten: `DANACH · ZIELORT`
- OT/OL-Spur: `OT:danach Zielort`
- Herkunft: Stufe 2 · vollständige Rollenform wiederholt sich.

#### G475-R053 · `ralal`

- **Werkstattfassung:** Sternstelle »r« mit zweifacher Zielzuordnung.
- Technische Fassung: Sternstelle »r« — Zielzuordnung, Zielzuordnung.
- Komponenten: `{N1} · ZIELORT · ZIELORT`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R054 · `okam`

- **Werkstattfassung:** Setze den Eintrag an der bezeichneten Stelle.
- Technische Fassung: Setze den Eintrag an der bezeichneten Stelle.
- Komponenten: `SETZEN · HIER`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 2 · vollständige Rollenform wiederholt sich.

#### G475-R055 · `otalshy`

- **Werkstattfassung:** Danach führt die Adressspur von der Zielposition zum Positionsposten.
- Technische Fassung: Adressspur: danach → Zielposition → Positionsposten. Reihenfolge konkret: OT — danach Zielort.
- Komponenten: `DANACH · ZIELORT · POSTEN`
- OT/OL-Spur: `OT:danach Zielort`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R056 · `okaldy`

- **Werkstattfassung:** Setze den Eintrag zur Zielposition und schließe den Schritt.
- Technische Fassung: Setze den Eintrag zur Zielposition, und schließe den Schritt.
- Komponenten: `SETZEN · ZIELORT · SCHLUSS`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 2 · vollständige Rollenform wiederholt sich.

#### G475-R057 · `chosar`

- **Werkstattfassung:** Sternstelle »chos« mit Ausgangszuordnung.
- Technische Fassung: Sternstelle »chos« — Ausgangszuordnung.
- Komponenten: `{N1} · AUSGANG`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 2 · vollständige Rollenform wiederholt sich.

#### G475-R058 · `otam`

- **Werkstattfassung:** Danach weist die Adressspur zur bezeichneten Stelle.
- Technische Fassung: Adressspur: danach → hier. Reihenfolge konkret: OT — danach bezeichnete Stelle.
- Komponenten: `DANACH · HIER`
- OT/OL-Spur: `OT:danach bezeichnete Stelle`
- Herkunft: Stufe 5 · alle Events besitzen Rollenparallelen.

#### G475-R059 · `ainaly`

- **Werkstattfassung:** Sternstelle »ain« mit Zielzuordnung und Postenangabe.
- Technische Fassung: Sternstelle »ain« — Zielzuordnung, Postenangabe.
- Komponenten: `{N1} · ZIELORT · POSTEN`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R060 · `okarcham|olkalaiin|olalsy`

- **Werkstattfassung:** Setze den Sternstelleneintrag »ch« von der Ausgangsposition aus an der bezeichneten Stelle. Führe im selben Arbeitsgang den Bezug des Sternstelleneintrags »k« und des Positionswerts zur Zielposition fort. Die zugehörige Adressspur wird bis zur Zielposition und zum Positionsposten fortgesetzt.
- Technische Fassung: Setze den Sternstelleneintrag »ch« von der Ausgangsposition an der bezeichneten Stelle. Im selben Arbeitsgang: Weiter beziehe den Sternstelleneintrag »k« und den Positionswert zur Zielposition. Reihenfolge konkret: OL — weiter mit Sternstelle »k«. Dazugehörige Adressspur: weiter → Zielposition → Positionsposten. Reihenfolge konkret: OL — weiter mit Zielort.
- Komponenten: `SETZEN · AUSGANG · {N1} · HIER || FORTSETZEN · {N1} · ZIELORT · WERT || FORTSETZEN · ZIELORT · POSTEN`
- OT/OL-Spur: `OL:weiter mit Sternstelle »k« || OL:weiter mit Zielort`
- Herkunft: Stufe 6 · mindestens ein Rollenparallelevent.

#### G475-R061 · `oraiinam`

- **Werkstattfassung:** Sternstelle »aiin« mit Einheitsangabe und Hier-Vermerk.
- Technische Fassung: Sternstelle »aiin« — Einheitsangabe, Hier-Vermerk.
- Komponenten: `EINHEIT · {N1} · HIER`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R062 · `osarsheeeo`

- **Werkstattfassung:** Halte die Sternstelleneinträge »os« und »eeeo« von der Ausgangsposition aus.
- Technische Fassung: Halte den Sternstelleneintrag »os« und den Sternstelleneintrag »eeeo« von der Ausgangsposition.
- Komponenten: `{N1} · AUSGANG · HALTEN · {N2}`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 2 · vollständige Rollenform wiederholt sich.

#### G475-R063 · `oto|aiin`

- **Werkstattfassung:** Die erste Adressspur führt danach zum Ausführungspunkt; die zweite bezeichnet den Positionswert.
- Technische Fassung: 1. Adressspur: danach → Ausführungspunkt. 2. Adressspur: Positionswert. Reihenfolge konkret: OT — danach Ausführung.
- Komponenten: `DANACH · AUSFÜHRUNG || WERT`
- OT/OL-Spur: `OT:danach Ausführung`
- Herkunft: Stufe 4 · mindestens ein striktes Parallelevent.

#### G475-R064 · `opoiiinoin|al|ches`

- **Werkstattfassung:** Beziehe den Sternstelleneintrag »opoiiin« als Ausführung auf der bezeichneten Stufe; beziehe den Eintrag zur Zielposition; nimm ihn auf und wähle ihn auf Grad I.
- Technische Fassung: 1. Beziehe den Sternstelleneintrag »opoiiin«, als Ausführung und auf der bezeichneten Stufe. 2. Beziehe den Eintrag zur Zielposition. 3. Nimm den Eintrag auf und wähle den Eintrag, auf Grad I.
- Komponenten: `{N1} · AUSFÜHRUNG · STUFE || ZIELORT || NEHMEN · GRAD I · WÄHLEN`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 4 · mindestens ein striktes Parallelevent.

#### G475-R065 · `ypaiin|alaly`

- **Werkstattfassung:** Katalogfolge: Sternstelle »yp« mit Wertangabe; Eintrag »alaly« mit zweifacher Zielzuordnung und Postenangabe.
- Technische Fassung: 1. Sternstelle »yp« — Wertangabe. 2. Eintrag »alaly« — Zielzuordnung, Zielzuordnung, Postenangabe.
- Komponenten: `{N1} · WERT || ZIELORT · ZIELORT · POSTEN`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 4 · mindestens ein striktes Parallelevent.

#### G475-R066 · `oteey|daiin`

- **Werkstattfassung:** Die erste Adressspur führt danach über Grad II zum Positionsposten; die zweite bezeichnet den Positionswert.
- Technische Fassung: 1. Adressspur: danach → Grad II → Positionsposten. 2. Adressspur: Positionswert. Reihenfolge konkret: OT — danach Grad II.
- Komponenten: `DANACH · GRAD II · POSTEN || WERT`
- OT/OL-Spur: `OT:danach Grad II`
- Herkunft: Stufe 4 · mindestens ein striktes Parallelevent.

#### G475-R067 · `oeeodaiin`

- **Werkstattfassung:** Sternstelle »oeeo« mit Wertangabe.
- Technische Fassung: Sternstelle »oeeo« — Wertangabe.
- Komponenten: `{N1} · WERT`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R068 · `ofsholdy`

- **Werkstattfassung:** Halte den Sternstelleneintrag »dy« an der bezeichneten Stelle als Ausführung weiter.
- Technische Fassung: Weiter halte den Sternstelleneintrag »dy«, als Ausführung an der bezeichneten Stelle. Reihenfolge konkret: OL — Halten in Sternstelle »dy« weiterführen.
- Komponenten: `AUSFÜHRUNG · HIER · HALTEN · FORTSETZEN · {N1}`
- OT/OL-Spur: `OL:Halten in Sternstelle »dy« weiterführen`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R069 · `opoeey|okaiin|ykolairol`

- **Werkstattfassung:** Beziehe den Sternstelleneintrag »opo« und den Positionsposten auf Grad II; setze den Positionswert. Führe im selben Arbeitsgang den Bezug des Sternstelleneintrags »yk« entlang der Ringbahn zweimal weiter.
- Technische Fassung: 1. Beziehe den Sternstelleneintrag »opo« und den Positionsposten, auf Grad II. 2. Setze den Positionswert. Im selben Arbeitsgang: Weiter und weiter beziehe den Sternstelleneintrag »yk« entlang der Ringbahn. Reihenfolge konkret: OL — Sternstelle »yk« in Bahn weiterführen; OL — Bahn weiterführen.
- Komponenten: `{N1} · GRAD II · POSTEN || SETZEN · WERT || {N1} · FORTSETZEN · BAHN · FORTSETZEN`
- OT/OL-Spur: `OL:Sternstelle »yk« in Bahn weiterführen | OL:Bahn weiterführen`
- Herkunft: Stufe 4 · mindestens ein striktes Parallelevent.

#### G475-R070 · `oralkam`

- **Werkstattfassung:** Sternstelle »k« mit Einheitsangabe, Zielzuordnung und Hier-Vermerk.
- Technische Fassung: Sternstelle »k« — Einheitsangabe, Zielzuordnung, Hier-Vermerk.
- Komponenten: `EINHEIT · ZIELORT · {N1} · HIER`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R071 · `ytairal`

- **Werkstattfassung:** Sternstelle »yt« mit Bahnvermerk und Zielzuordnung.
- Technische Fassung: Sternstelle »yt« — Bahnvermerk, Zielzuordnung.
- Komponenten: `{N1} · BAHN · ZIELORT`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 2 · vollständige Rollenform wiederholt sich.

#### G475-R072 · `oeeesaiin`

- **Werkstattfassung:** Sternstelle »oeees« mit Wertangabe.
- Technische Fassung: Sternstelle »oeees« — Wertangabe.
- Komponenten: `{N1} · WERT`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R073 · `ory`

- **Werkstattfassung:** Die Adressspur führt von der Positionseinheit zum Positionsposten.
- Technische Fassung: Adressspur: Positionseinheit → Positionsposten.
- Komponenten: `EINHEIT · POSTEN`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 8 · vollständig aus modellübergreifend wiederkehrenden Komponenten gebaut.

#### G475-R074 · `ochey|fydy`

- **Werkstattfassung:** Nimm den Positionsposten als Ausführung der Stufe I auf; nimm im selben Gang den Sternstelleneintrag »f« und den Positionsposten auf und schließe den Schritt.
- Technische Fassung: 1. Nimm den Positionsposten auf, als Ausführung und auf Grad I. 2. Im selben Gang nimm den Sternstelleneintrag »f« und den Positionsposten auf, und schließe den Schritt.
- Komponenten: `AUSFÜHRUNG · NEHMEN · GRAD I · POSTEN || {N1} · POSTEN · SCHLUSS`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R075 · `of|o|eeesaly`

- **Werkstattfassung:** Katalogfolge: Eintrag »of« mit Ausführungs- und Hier-Vermerk; Eintrag »o« mit Ausführungsvermerk; Sternstelle »eees« mit Zielzuordnung und Postenangabe.
- Technische Fassung: 1. Eintrag »of« — Ausführungsvermerk, Hier-Vermerk. 2. Eintrag »o« — Ausführungsvermerk. 3. Sternstelle »eees« — Zielzuordnung, Postenangabe.
- Komponenten: `AUSFÜHRUNG · HIER || AUSFÜHRUNG || {N1} · ZIELORT · POSTEN`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 4 · mindestens ein striktes Parallelevent.

#### G475-R076 · `ykaraiin|airal`

- **Werkstattfassung:** Katalogfolge: Sternstelle »yk« mit Ausgangszuordnung und Wertangabe; Eintrag »airal« mit Bahnvermerk und Zielzuordnung.
- Technische Fassung: 1. Sternstelle »yk« — Ausgangszuordnung, Wertangabe. 2. Eintrag »airal« — Bahnvermerk, Zielzuordnung.
- Komponenten: `{N1} · AUSGANG · WERT || BAHN · ZIELORT`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 6 · mindestens ein Rollenparallelevent.

#### G475-R077 · `okalar`

- **Werkstattfassung:** Setze den Eintrag zur Zielposition, ausgehend von der Ausgangsposition.
- Technische Fassung: Setze den Eintrag zur Zielposition und von der Ausgangsposition.
- Komponenten: `SETZEN · ZIELORT · AUSGANG`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R078 · `orara|olaiin|olay|olfsheoral`

- **Werkstattfassung:** Sternstelle »a« mit Einheitsangabe und Ausgangszuordnung. Führe den Katalog mit Eintrag »olaiin« samt Fortsetzungs- und Wertvermerk und mit Sternstelle »ay« samt Fortsetzungsvermerk weiter. Führe im selben Arbeitsgang das Halten der Sternstelleneinträge »f« und »eor« zur Zielposition fort.
- Technische Fassung: Sternstelle »a« — Einheitsangabe, Ausgangszuordnung. Fortgesetzter Katalogeintrag: 1. Eintrag »olaiin« — Fortsetzungsvermerk, Wertangabe. 2. Sternstelle »ay« — Fortsetzungsvermerk. Reihenfolge konkret: OL — weiter mit Wert; OL — weiter mit Sternstelle »ay«. Im selben Arbeitsgang: Weiter halte den Sternstelleneintrag »f« und den Sternstelleneintrag »eor« zur Zielposition. Reihenfolge konkret: OL — weiter mit Sternstelle »f«.
- Komponenten: `EINHEIT · AUSGANG · {N1} || FORTSETZEN · WERT || FORTSETZEN · {N1} || FORTSETZEN · {N1} · HALTEN · {N2} · ZIELORT`
- OT/OL-Spur: `OL:weiter mit Wert | OL:weiter mit Sternstelle »ay« || OL:weiter mit Sternstelle »f«`
- Herkunft: Stufe 4 · mindestens ein striktes Parallelevent.

#### G475-R079 · `opalal`

- **Werkstattfassung:** Sternstelle »op« mit zweifacher Zielzuordnung.
- Technische Fassung: Sternstelle »op« — Zielzuordnung, Zielzuordnung.
- Komponenten: `{N1} · ZIELORT · ZIELORT`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R080 · `yfary`

- **Werkstattfassung:** Sternstellen »yf« und »y« mit Ausgangszuordnung.
- Technische Fassung: Sternstelle »yf« / Sternstelle »y« — Ausgangszuordnung.
- Komponenten: `{N1} · AUSGANG · {N2}`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R081 · `oraiiral`

- **Werkstattfassung:** Sternstelle »aiir« mit Einheitsangabe und Zielzuordnung.
- Technische Fassung: Sternstelle »aiir« — Einheitsangabe, Zielzuordnung.
- Komponenten: `EINHEIT · {N1} · ZIELORT`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R082 · `ytoar|shar`

- **Werkstattfassung:** Katalogfolge: Sternstelle »yto« mit Ausgangszuordnung; Eintrag »shar« mit Haltevermerk und Ausgangszuordnung.
- Technische Fassung: 1. Sternstelle »yto« — Ausgangszuordnung. 2. Eintrag »shar« — Haltevermerk, Ausgangszuordnung.
- Komponenten: `{N1} · AUSGANG || HALTEN · AUSGANG`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 4 · mindestens ein striktes Parallelevent.

#### G475-R083 · `octho`

- **Werkstattfassung:** Nimm zwei Vorkommen des Sternstelleneintrags »o« auf und stelle beide ein.
- Technische Fassung: Nimm den Sternstelleneintrag »o« und den Sternstelleneintrag »o« auf und stelle den Sternstelleneintrag »o« und den Sternstelleneintrag »o« ein.
- Komponenten: `{N1} · NEHMEN · EINSTELLEN · {N1}`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R084 · `aral|oletal`

- **Werkstattfassung:** Die Adressspur führt von der Ausgangs- zur Zielposition; die zugehörige Spur wird anschließend über Sternstelle »et« zur Zielposition fortgesetzt.
- Technische Fassung: Adressspur: Ausgangsposition → Zielposition. Dazugehörige Adressspur: weiter → Sternstelle »et« → Zielposition. Reihenfolge konkret: OL — weiter mit Sternstelle »et«.
- Komponenten: `AUSGANG · ZIELORT || FORTSETZEN · {N1} · ZIELORT`
- OT/OL-Spur: `OL:weiter mit Sternstelle »et«`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

### f77r · BIOLOGICAL

#### G475-R085 · `darchdar|olkchs`

- **Werkstattfassung:** Badstationen »d« und »chd« mit je einer Ausgangszuordnung; fortgesetzter Katalogeintrag: Badstation »kchs« mit Fortsetzungsvermerk.
- Technische Fassung: Badstation »d« / Badstation »chd« — Ausgangszuordnung, Ausgangszuordnung. Fortgesetzter Katalogeintrag: Badstation »kchs« — Fortsetzungsvermerk. Reihenfolge konkret: OL — weiter mit Badstation »kchs«.
- Komponenten: `{N1} · AUSGANG · {N2} · AUSGANG || FORTSETZEN · {N1}`
- OT/OL-Spur: `OL:weiter mit Badstation »kchs«`
- Herkunft: Stufe 4 · mindestens ein striktes Parallelevent.

#### G475-R086 · `otedy`

- **Werkstattfassung:** Danach führt die Adressspur über Grad I zum Endpunkt.
- Technische Fassung: Adressspur: danach → Grad I → Endpunkt. Reihenfolge konkret: OT — danach Grad I.
- Komponenten: `DANACH · GRAD I · SCHLUSS`
- OT/OL-Spur: `OT:danach Grad I`
- Herkunft: Stufe 8 · vollständig aus modellübergreifend wiederkehrenden Komponenten gebaut.

#### G475-R087 · `otork`

- **Werkstattfassung:** Badstation »ork« mit Folgevermerk.
- Technische Fassung: Badstation »ork« — Folgevermerk. Reihenfolge konkret: OT — danach Badstation »ork«.
- Komponenten: `DANACH · {N1}`
- OT/OL-Spur: `OT:danach Badstation »ork«`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R088 · `otol`

- **Werkstattfassung:** Die Adressspur wird danach fortgesetzt.
- Technische Fassung: Adressspur: danach → weiter. Reihenfolge konkret: OT — danach Fortsetzung; OL — Folgeschritt weiterführen.
- Komponenten: `DANACH · FORTSETZEN`
- OT/OL-Spur: `OT:danach Fortsetzung | OL:Folgeschritt weiterführen`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R089 · `dchdy`

- **Werkstattfassung:** Bearbeite den Eintrag und schließe den Schritt.
- Technische Fassung: Bearbeite den Eintrag, und schließe den Schritt.
- Komponenten: `BEARBEITEN · SCHLUSS`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 2 · vollständige Rollenform wiederholt sich.

#### G475-R090 · `soral`

- **Werkstattfassung:** Badstation »sor« mit Zielzuordnung.
- Technische Fassung: Badstation »sor« — Zielzuordnung.
- Komponenten: `{N1} · ZIELORT`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 2 · vollständige Rollenform wiederholt sich.

#### G475-R091 · `dotedy`

- **Werkstattfassung:** Katalogfolge: Badstation »d« mit Folgevermerk; danach Badstation »edy«.
- Technische Fassung: Badstation »d« / Badstation »edy« — Folgevermerk. Reihenfolge konkret: OT — nach Badstation »d« folgt Badstation »edy«.
- Komponenten: `{N1} · DANACH · {N2}`
- OT/OL-Spur: `OT:nach Badstation »d« folgt Badstation »edy«`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R092 · `otchdy`

- **Werkstattfassung:** Bearbeite danach den Eintrag und schließe den Schritt.
- Technische Fassung: Danach bearbeite den Eintrag, und schließe den Schritt. Reihenfolge konkret: OT — danach Bearbeiten.
- Komponenten: `DANACH · BEARBEITEN · SCHLUSS`
- OT/OL-Spur: `OT:danach Bearbeiten`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R093 · `otolaiin|o`

- **Werkstattfassung:** Die erste Adressspur wird danach bis zum Stationswert fortgesetzt; die zweite bezeichnet den Ausführungspunkt.
- Technische Fassung: 1. Adressspur: danach → weiter → Stationswert. 2. Adressspur: Ausführungspunkt. Reihenfolge konkret: OT — danach Fortsetzung; OL — Folgeschritt in Wert weiterführen.
- Komponenten: `DANACH · FORTSETZEN · WERT || AUSFÜHRUNG`
- OT/OL-Spur: `OT:danach Fortsetzung | OL:Folgeschritt in Wert weiterführen`
- Herkunft: Stufe 6 · mindestens ein Rollenparallelevent.

### f88v · PHARMA

#### G475-R094 · `okalyd`

- **Werkstattfassung:** Setze den Drogeneintrag »yd« als Ansatz am Zielgefäß an.
- Technische Fassung: Setze den Drogeneintrag »yd« als Ansatz an zum Zielgefäß.
- Komponenten: `SETZEN · ZIELORT · {N1}`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 2 · vollständige Rollenform wiederholt sich.

#### G475-R095 · `cheocthy`

- **Werkstattfassung:** Nimm den Drogeneintrag »cheo« sowie den Drogenposten und stelle beide ein.
- Technische Fassung: Nimm den Drogeneintrag »cheo« und den Drogenposten und stelle den Drogeneintrag »cheo« und den Drogenposten ein.
- Komponenten: `{N1} · NEHMEN · EINSTELLEN · POSTEN`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R096 · `cpheor`

- **Werkstattfassung:** Droge »cphe« mit Einheitsangabe.
- Technische Fassung: Droge »cphe« — Einheitsangabe.
- Komponenten: `{N1} · EINHEIT`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 2 · vollständige Rollenform wiederholt sich.

#### G475-R097 · `otar|arody`

- **Werkstattfassung:** Katalogfolge: Eintrag »otar« mit Folgevermerk und Ausgangszuordnung; Droge »ody« mit Ausgangszuordnung.
- Technische Fassung: 1. Eintrag »otar« — Folgevermerk, Ausgangszuordnung. 2. Droge »ody« — Ausgangszuordnung. Reihenfolge konkret: OT — danach Ausgang.
- Komponenten: `DANACH · AUSGANG || AUSGANG · {N1}`
- OT/OL-Spur: `OT:danach Ausgang`
- Herkunft: Stufe 4 · mindestens ein striktes Parallelevent.

#### G475-R098 · `otokol`

- **Werkstattfassung:** Setze den Eintrag danach als Ansatz an und führe das Setzen weiter.
- Technische Fassung: Danach und weiter setze den Eintrag als Ansatz an. Reihenfolge konkret: OT — danach Setzen; OL — Setzen weiterführen.
- Komponenten: `DANACH · SETZEN · FORTSETZEN`
- OT/OL-Spur: `OT:danach Setzen | OL:Setzen weiterführen`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R099 · `otoram`

- **Werkstattfassung:** Droge »or« mit Folgevermerk und Hier-Vermerk.
- Technische Fassung: Droge »or« — Folgevermerk, Hier-Vermerk. Reihenfolge konkret: OT — danach Droge »or«.
- Komponenten: `DANACH · {N1} · HIER`
- OT/OL-Spur: `OT:danach Droge »or«`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R100 · `otora`

- **Werkstattfassung:** Droge »ora« mit Folgevermerk.
- Technische Fassung: Droge »ora« — Folgevermerk. Reihenfolge konkret: OT — danach Droge »ora«.
- Komponenten: `DANACH · {N1}`
- OT/OL-Spur: `OT:danach Droge »ora«`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R101 · `cheosdy`

- **Werkstattfassung:** Droge »cheosdy« — Drogenfamilie »cheo«.
- Technische Fassung: Droge »cheosdy« — Drogenfamilie »cheo«.
- Komponenten: `{F1}:NAMENSFAMILIE · {N1}`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 10 · funktional erklärt; gelernter Name/Familienname bleibt.

#### G475-R102 · `okaiin`

- **Werkstattfassung:** Setze den Mengenwert als Ansatz an.
- Technische Fassung: Setze den Mengenwert als Ansatz an.
- Komponenten: `SETZEN · WERT`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 2 · vollständige Rollenform wiederholt sich.

#### G475-R103 · `daramdal`

- **Werkstattfassung:** Drogen »d« und »am« mit Ausgangs- beziehungsweise Zielzuordnung.
- Technische Fassung: Droge »d« / Droge »am« — Ausgangszuordnung, Zielzuordnung.
- Komponenten: `{N1} · AUSGANG · {N2} · ZIELORT`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 5 · alle Events besitzen Rollenparallelen.

#### G475-R104 · `otydary`

- **Werkstattfassung:** Zweimal Droge »y«, mit Folgevermerk, Hier-Vermerk und Ausgangszuordnung.
- Technische Fassung: Droge »y« / Droge »y« — Folgevermerk, Hier-Vermerk, Ausgangszuordnung. Reihenfolge konkret: OT — danach Droge »y«.
- Komponenten: `DANACH · {N1} · HIER · AUSGANG · {N1}`
- OT/OL-Spur: `OT:danach Droge »y«`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R105 · `otdordy`

- **Werkstattfassung:** Droge »dordy« mit Folgevermerk.
- Technische Fassung: Droge »dordy« — Folgevermerk. Reihenfolge konkret: OT — danach Droge »dordy«.
- Komponenten: `DANACH · {N1}`
- OT/OL-Spur: `OT:danach Droge »dordy«`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R106 · `dararda`

- **Werkstattfassung:** Drogen »d« und »da« mit je einer Ausgangszuordnung.
- Technische Fassung: Droge »d« / Droge »da« — Ausgangszuordnung, Ausgangszuordnung.
- Komponenten: `{N1} · AUSGANG · AUSGANG · {N2}`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

### f89r · PHARMA

#### G475-R107 · `okchshy|qkol|oldam`

- **Werkstattfassung:** Setze den Drogenposten als Ansatz an und nimm ihn. Führe im selben Arbeitsgang den Bezug weiter: zuerst für Drogeneintrag »qk«, dann für Drogeneintrag »d« an der bezeichneten Stelle.
- Technische Fassung: Setze den Drogenposten als Ansatz an und nimm den Drogenposten. Im selben Arbeitsgang: Weiter beziehe den Drogeneintrag »qk«. Reihenfolge konkret: OL — Droge »qk« weiterführen. Im selben Arbeitsgang: Weiter beziehe den Drogeneintrag »d« an der bezeichneten Stelle. Reihenfolge konkret: OL — weiter mit Droge »d«.
- Komponenten: `SETZEN · NEHMEN · POSTEN || {N1} · FORTSETZEN || FORTSETZEN · {N1} · HIER`
- OT/OL-Spur: `OL:Droge »qk« weiterführen || OL:weiter mit Droge »d«`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R108 · `otoldy`

- **Werkstattfassung:** Droge »dy« mit Folge- und Fortsetzungsvermerk.
- Technische Fassung: Droge »dy« — Folgevermerk, Fortsetzungsvermerk. Reihenfolge konkret: OT — danach Fortsetzung; OL — Folgeschritt in Droge »dy« weiterführen.
- Komponenten: `DANACH · FORTSETZEN · {N1}`
- OT/OL-Spur: `OT:danach Fortsetzung | OL:Folgeschritt in Droge »dy« weiterführen`
- Herkunft: Stufe 3 · alle Events besitzen strikte Parallelträger.

#### G475-R109 · `ararchodaiin`

- **Werkstattfassung:** Droge »cho« mit zweifacher Ausgangszuordnung und Wertangabe.
- Technische Fassung: Droge »cho« — Ausgangszuordnung, Ausgangszuordnung, Wertangabe.
- Komponenten: `AUSGANG · AUSGANG · {N1} · WERT`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R110 · `ykyd|chol|ches`

- **Werkstattfassung:** Gib die beiden Drogenposten — außen und innen — an der bezeichneten Stelle zu. Beziehe den Eintrag im selben Arbeitsgang weiter; nimm ihn dann auf und wähle ihn auf Grad I.
- Technische Fassung: Gib den Drogenposten [außen] und den Drogenposten [innen] zu an der bezeichneten Stelle. Im selben Arbeitsgang: 1. Weiter beziehe den Eintrag. 2. Nimm den Eintrag und wähle den Eintrag, auf Grad I. Reihenfolge konkret: OL — im aktiven Eintrag weiter.
- Komponenten: `POSTEN · GEBEN · POSTEN · HIER || FORTSETZEN || NEHMEN · GRAD I · WÄHLEN`
- OT/OL-Spur: `OL:im aktiven Eintrag weiter`
- Herkunft: Stufe 4 · mindestens ein striktes Parallelevent.

#### G475-R111 · `otorain`

- **Werkstattfassung:** Droge »or« mit Folgevermerk und Anteilsangabe.
- Technische Fassung: Droge »or« — Folgevermerk, Anteilsangabe. Reihenfolge konkret: OT — danach Droge »or«.
- Komponenten: `DANACH · {N1} · ANTEIL`
- OT/OL-Spur: `OT:danach Droge »or«`
- Herkunft: Stufe 2 · vollständige Rollenform wiederholt sich.

#### G475-R112 · `okaiin|dan`

- **Werkstattfassung:** Setze den Mengenwert und im selben Gang den Drogenanteil als Ansatz an.
- Technische Fassung: 1. Setze den Mengenwert als Ansatz an. 2. Im selben Gang setze den Drogenanteil als Ansatz an.
- Komponenten: `SETZEN · WERT || ANTEIL`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 4 · mindestens ein striktes Parallelevent.

#### G475-R113 · `ykocfhy`

- **Werkstattfassung:** Nimm den Drogeneintrag »yko« sowie den Drogenposten an der bezeichneten Stelle.
- Technische Fassung: Nimm den Drogeneintrag »yko« und den Drogenposten an der bezeichneten Stelle.
- Komponenten: `{N1} · NEHMEN · HIER · POSTEN`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R114 · `saldam`

- **Werkstattfassung:** Drogen »s« und »d« mit Zielzuordnung beziehungsweise Hier-Vermerk.
- Technische Fassung: Droge »s« / Droge »d« — Zielzuordnung, Hier-Vermerk.
- Komponenten: `{N1} · ZIELORT · {N2} · HIER`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R115 · `sydarary`

- **Werkstattfassung:** Drogen »sy« und »y« mit Hier-Vermerk sowie zweifacher Ausgangszuordnung.
- Technische Fassung: Droge »sy« / Droge »y« — Hier-Vermerk, Ausgangszuordnung, Ausgangszuordnung.
- Komponenten: `{N1} · HIER · AUSGANG · AUSGANG · {N2}`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R116 · `yddy`

- **Werkstattfassung:** Die Adressspur führt vom Drogenposten über die bezeichnete Stelle zurück zum Drogenposten.
- Technische Fassung: Adressspur: Drogenposten → hier → Drogenposten.
- Komponenten: `POSTEN · HIER · POSTEN`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R117 · `odory|doly`

- **Werkstattfassung:** Droge »od« mit Einheits- und Postenangabe; fortgesetzter Katalogeintrag: Droge »d« mit Fortsetzungsvermerk und Postenangabe.
- Technische Fassung: Droge »od« — Einheitsangabe, Postenangabe. Fortgesetzter Katalogeintrag: Droge »d« — Fortsetzungsvermerk, Postenangabe. Reihenfolge konkret: OL — Droge »d« in Posten weiterführen.
- Komponenten: `{N1} · EINHEIT · POSTEN || {N1} · FORTSETZEN · POSTEN`
- OT/OL-Spur: `OL:Droge »d« in Posten weiterführen`
- Herkunft: Stufe 6 · mindestens ein Rollenparallelevent.

#### G475-R118 · `opchosam`

- **Werkstattfassung:** Droge »opchos« mit Hier-Vermerk.
- Technische Fassung: Droge »opchos« — Hier-Vermerk.
- Komponenten: `{N1} · HIER`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R119 · `saloiinsheol`

- **Werkstattfassung:** Führe das Halten der Drogeneinträge »s«, »oiin« und »e« zum Zielgefäß fort.
- Technische Fassung: Weiter halte den Drogeneintrag »s«, den Drogeneintrag »oiin« und den Drogeneintrag »e« zum Zielgefäß. Reihenfolge konkret: OL — Droge »e« weiterführen.
- Komponenten: `{N1} · ZIELORT · {N2} · HALTEN · {N3} · FORTSETZEN`
- OT/OL-Spur: `OL:Droge »e« weiterführen`
- Herkunft: Stufe 10 · funktional erklärt; gelernter Name/Familienname bleibt.

#### G475-R120 · `opcheor`

- **Werkstattfassung:** Setze die Ansatzeinheit ein und nimm sie als Ausführung auf Grad I.
- Technische Fassung: Setze die Ansatzeinheit ein und nimm die Ansatzeinheit, als Ausführung und auf Grad I.
- Komponenten: `AUSFÜHRUNG · EINSETZEN · NEHMEN · GRAD I · EINHEIT`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R121 · `otold|y`

- **Werkstattfassung:** Katalogfolge: Droge »d« mit Folge- und Fortsetzungsvermerk; Eintrag »y« mit Postenangabe.
- Technische Fassung: 1. Droge »d« — Folgevermerk, Fortsetzungsvermerk. 2. Eintrag »y« — Postenangabe. Reihenfolge konkret: OT — danach Fortsetzung; OL — Folgeschritt in Droge »d« weiterführen.
- Komponenten: `DANACH · FORTSETZEN · {N1} || POSTEN`
- OT/OL-Spur: `OT:danach Fortsetzung | OL:Folgeschritt in Droge »d« weiterführen`
- Herkunft: Stufe 4 · mindestens ein striktes Parallelevent.

#### G475-R122 · `okol|shol|dy`

- **Werkstattfassung:** Führe das Ansetzen des Eintrags fort; führe auch sein Halten fort und halte im selben Gang den Drogenposten.
- Technische Fassung: 1. Weiter setze den Eintrag als Ansatz an. 2. Weiter halte den Eintrag. 3. Im selben Gang halte den Drogenposten. Reihenfolge konkret: OL — Setzen weiterführen; OL — Halten weiterführen.
- Komponenten: `SETZEN · FORTSETZEN || HALTEN · FORTSETZEN || POSTEN`
- OT/OL-Spur: `OL:Setzen weiterführen | OL:Halten weiterführen`
- Herkunft: Stufe 5 · alle Events besitzen Rollenparallelen.

#### G475-R123 · `opchoroiin`

- **Werkstattfassung:** Droge »opchor« mit Ausführungs- und Stufenvermerk.
- Technische Fassung: Droge »opchor« — Ausführungsvermerk, Stufenvermerk.
- Komponenten: `{N1} · AUSFÜHRUNG · STUFE`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 8 · vollständig aus modellübergreifend wiederkehrenden Komponenten gebaut.

#### G475-R124 · `korainy`

- **Werkstattfassung:** Gib die Ansatzeinheit, den Drogenanteil und den Drogenposten zu.
- Technische Fassung: Gib die Ansatzeinheit, den Drogenanteil und den Drogenposten zu.
- Komponenten: `GEBEN · EINHEIT · ANTEIL · POSTEN`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R125 · `sodar`

- **Werkstattfassung:** Wähle den Eintrag und markiere ihn – als Ausführung auf der zweiten Stufe.
- Technische Fassung: Wähle den Eintrag und markiere ihn – als Ausführung auf der zweiten Stufe.
- Komponenten: `WÄHLEN · AUSFÜHRUNG · ZWEITE STUFE · MARKIEREN`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 9 · exakte laufende Oberfläche und Rezeptträger.

#### G475-R126 · `cheys`

- **Werkstattfassung:** Wähle den Drogenposten.
- Technische Fassung: Wähle den Drogenposten.
- Komponenten: `POSTEN · WÄHLEN`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 3 · alle Events besitzen strikte Parallelträger.

#### G475-R127 · `cheody`

- **Werkstattfassung:** Nimm den Drogenposten als Ausführung auf Grad I.
- Technische Fassung: Nimm den Drogenposten, auf Grad I und als Ausführung.
- Komponenten: `NEHMEN · GRAD I · AUSFÜHRUNG · POSTEN`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R128 · `oporain`

- **Werkstattfassung:** Droge »opor« mit Anteilsangabe.
- Technische Fassung: Droge »opor« — Anteilsangabe.
- Komponenten: `{N1} · ANTEIL`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R129 · `okshdchos`

- **Werkstattfassung:** Setze den Drogeneintrag »dchos« als Ansatz an und halte ihn.
- Technische Fassung: Setze den Drogeneintrag »dchos« als Ansatz an und halte den Drogeneintrag »dchos«.
- Komponenten: `SETZEN · HALTEN · {N1}`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R130 · `okain`

- **Werkstattfassung:** Setze den Drogenanteil als Ansatz an.
- Technische Fassung: Setze den Drogenanteil als Ansatz an.
- Komponenten: `SETZEN · ANTEIL`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 2 · vollständige Rollenform wiederholt sich.

#### G475-R131 · `yorain`

- **Werkstattfassung:** Droge »yor« mit Anteilsangabe.
- Technische Fassung: Droge »yor« — Anteilsangabe.
- Komponenten: `{N1} · ANTEIL`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R132 · `ofakal`

- **Werkstattfassung:** Droge »ak« mit Ausführungsvermerk, Hier-Vermerk und Zielzuordnung.
- Technische Fassung: Droge »ak« — Ausführungsvermerk, Hier-Vermerk, Zielzuordnung.
- Komponenten: `AUSFÜHRUNG · HIER · {N1} · ZIELORT`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

#### G475-R133 · `otalsy`

- **Werkstattfassung:** Danach führt die Adressspur vom Zielgefäß zum Drogenposten.
- Technische Fassung: Adressspur: danach → Zielgefäß → Drogenposten. Reihenfolge konkret: OT — danach Zielort.
- Komponenten: `DANACH · ZIELORT · POSTEN`
- OT/OL-Spur: `OT:danach Zielort`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R134 · `ytarem`

- **Werkstattfassung:** Drogen »yt« und »em« mit Ausgangszuordnung.
- Technische Fassung: Droge »yt« / Droge »em« — Ausgangszuordnung.
- Komponenten: `{N1} · AUSGANG · {N2}`
- OT/OL-Spur: `keine OT/OL-Stelle`
- Herkunft: Stufe 1 · vollständiger Record wiederholt sich bedeutungsgleich.

#### G475-R135 · `otolarol`

- **Werkstattfassung:** Die Adressspur wird danach fortgesetzt, führt zum Ausgangsgefäß und wird dort nochmals fortgesetzt.
- Technische Fassung: Adressspur: danach → weiter → Ausgangsgefäß → weiter. Reihenfolge konkret: OT — danach Fortsetzung; OL — Folgeschritt in Ausgang weiterführen; OL — Ausgang weiterführen.
- Komponenten: `DANACH · FORTSETZEN · AUSGANG · FORTSETZEN`
- OT/OL-Spur: `OT:danach Fortsetzung | OL:Folgeschritt in Ausgang weiterführen | OL:Ausgang weiterführen`
- Herkunft: Stufe 7 · vollständig aus Komponenten desselben Modells gebaut.

Die Werkstattfassung ist bewusst kein neuer Decoder: Ihre Rückseite ist die bytegleich erhaltene technische Lesung samt 183 Eventspuren. Jede spätere Änderung kann deshalb gegen Oberfläche, Rezept, Komponentensequenz, Namen und OT/OL-Richtung geprüft werden.
