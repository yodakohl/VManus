# V71 R3 — ausführbarer Bildbesitzer-Compiler

Status: kreative technische Rekonstruktion, keine Entzifferung oder Übersetzung.
Alle Besitzer sind sichtbare Argumentträger; sie sind keine Wörter, Kartenwerte,
Stämme, Referenten oder Bedeutungen.

## Ergebnis

Der Ledger bindet **135 Prosa-Felder** und **142 Astro-Loci**
in insgesamt **277** Zeilen. Die 135 Felder decken 381 Ereignisse,
die 142 Astro-Loci 395 Gruppen. Jede Bindung bleibt record- oder radlokal.

Statuszählung:

| Status | Zeilen |
|---|---:|
| `DIRECT_VISIBLE` | 106 |
| `INHERITED_VISIBLE` | 141 |
| `PAGE_OWNER_ONLY` | 9 |
| `UNRESOLVED` | 21 |

## Ausführbare OWNER-Registerregeln

1. `RESET_RECORD`: Am Beginn jedes H-/B-Records wird OWNER gelöscht; am Ende darf nichts in den nächsten Record gelangen.
2. `ANCHOR_DIRECT`: Berührt/umschließt ein Bildobjekt den lokalen Schreibraum eindeutig, setze OWNER auf dieses kleinste Objekt.
3. `ANCHOR_PAGE`: Gibt es nur eine dominante Seitenfigur, darf der erste Recordposten sie als `PAGE_OWNER_ONLY` setzen.
4. `INHERIT_LOCAL`: Folgende Felder dürfen denselben OWNER nur im selben Record und ohne sichtbare Trennkante erben.
5. `BREAK_AT_GAP`: Eine sichtbare Unterbrechung oder ein neues Gefäß löscht OWNER; bloße Nähe ist keine Verbindung.
6. `ASTRO_NAMESPACE`: Jeder Kreis, jedes Paneel und jede Sternstation hat einen eigenen lokalen Namensraum.
7. `NO_DIRECTION`: Bogen, Ring und Rad geben ohne Pfeil weder Fluss, Start noch Rotation vor.
8. `UNRESOLVED`: Sind mehrere kleinste Besitzer möglich, wird nicht seitenweit vererbt; das Masterexemplar muss wählen.
9. `NO_SEMANTIC_LIFT`: Ein sichtbarer Besitzer ergänzt nur 'dieses Bildobjekt'; er benennt kein Material, Heilmittel, Gestirn oder Verfahren.

## Wichtigste Revisionen

- Herbal trägt sichtbare Pflanzenbesitzer, nicht bildsichtbare Arten oder Zubereitungen.
- f81v trägt ein gemeinsames Feld, aber keinen siebenstufigen Kreislauf.
- f82r wird bei jedem Stationswechsel zurückgesetzt; die Linie über dem Liegepodest bleibt ausdrücklich ungelöst.
- f83r bindet nur die wirklich gekoppelte Paarstation; B5 und B6 erhalten getrennte offene Endbesitzer.
- f67r2, f68r1 und f69v besitzen wheel-/panel-lokale Namensräume; die 28 f69v-Slots gelten ausschließlich links und ungeordnet.

## Vollständige Herbal-Spur (20/20)

| Feld | Record | Locus | Status | OWNER | stilles technisches Argument |
|---|---|---|---|---|---|
| F001 | H1 | f10r.2 | PAGE_OWNER_ONLY | `H1_ROOT_AXIS_AND_RED_SWELLINGS` | sichtbarer Wurzelachsen- und Speicherorganposten dieser Pflanze |
| F002 | H1 | f10r.5 | INHERITED_VISIBLE | `H1_ROOT_AXIS_AND_RED_SWELLINGS` | sichtbarer Wurzelachsen- und Speicherorganposten dieser Pflanze |
| F003 | H2 | f10r.6 | PAGE_OWNER_ONLY | `H2_UPPER_STEM_FLOWER_BUD_LEAF_SET` | sichtbarer oberer Sprossposten derselben f10r-Pflanze |
| F004 | H2 | f10r.8 | INHERITED_VISIBLE | `H2_UPPER_STEM_FLOWER_BUD_LEAF_SET` | sichtbarer oberer Sprossposten derselben f10r-Pflanze |
| F005 | H2 | f10r.9 | INHERITED_VISIBLE | `H2_UPPER_STEM_FLOWER_BUD_LEAF_SET` | sichtbarer oberer Sprossposten derselben f10r-Pflanze |
| F006 | H3 | f11r.1 | PAGE_OWNER_ONLY | `H3_WHOLE_DENSE_CROWN_PLANT` | gesamte dichtkronige f11r-Pflanze des laufenden Artikels |
| F007 | H3 | f11r.1 | INHERITED_VISIBLE | `H3_WHOLE_DENSE_CROWN_PLANT` | gesamte dichtkronige f11r-Pflanze des laufenden Artikels |
| F008 | H3 | f11r.4 | INHERITED_VISIBLE | `H3_WHOLE_DENSE_CROWN_PLANT` | gesamte dichtkronige f11r-Pflanze des laufenden Artikels |
| F009 | H3 | f11r.7 | INHERITED_VISIBLE | `H3_WHOLE_DENSE_CROWN_PLANT` | gesamte dichtkronige f11r-Pflanze des laufenden Artikels |
| F010 | H4 | f55v.5 | PAGE_OWNER_ONLY | `H4_WHOLE_BROAD_LEAF_PLANT` | gesamte breitblättrige f55v-Pflanze des laufenden Artikels |
| F011 | H4 | f55v.5 | INHERITED_VISIBLE | `H4_WHOLE_BROAD_LEAF_PLANT` | gesamte breitblättrige f55v-Pflanze des laufenden Artikels |
| F012 | H4 | f55v.11 | INHERITED_VISIBLE | `H4_WHOLE_BROAD_LEAF_PLANT` | gesamte breitblättrige f55v-Pflanze des laufenden Artikels |
| F013 | H4 | f55v.11 | INHERITED_VISIBLE | `H4_WHOLE_BROAD_LEAF_PLANT` | gesamte breitblättrige f55v-Pflanze des laufenden Artikels |
| F014 | H5 | f56r.5 | PAGE_OWNER_ONLY | `H5_WHOLE_MULTIHEAD_COILED_PLANT` | gesamte mehrköpfige f56r-Pflanze des laufenden Artikels |
| F015 | H5 | f56r.7 | INHERITED_VISIBLE | `H5_WHOLE_MULTIHEAD_COILED_PLANT` | gesamte mehrköpfige f56r-Pflanze des laufenden Artikels |
| F016 | H5 | f56r.8 | INHERITED_VISIBLE | `H5_WHOLE_MULTIHEAD_COILED_PLANT` | gesamte mehrköpfige f56r-Pflanze des laufenden Artikels |
| F017 | H5 | f56r.12 | INHERITED_VISIBLE | `H5_WHOLE_MULTIHEAD_COILED_PLANT` | gesamte mehrköpfige f56r-Pflanze des laufenden Artikels |
| F018 | H5 | f56r.13 | INHERITED_VISIBLE | `H5_WHOLE_MULTIHEAD_COILED_PLANT` | gesamte mehrköpfige f56r-Pflanze des laufenden Artikels |
| F019 | H5 | f56r.18 | INHERITED_VISIBLE | `H5_WHOLE_MULTIHEAD_COILED_PLANT` | gesamte mehrköpfige f56r-Pflanze des laufenden Artikels |
| F020 | H5 | f56r.19 | INHERITED_VISIBLE | `H5_WHOLE_MULTIHEAD_COILED_PLANT` | gesamte mehrköpfige f56r-Pflanze des laufenden Artikels |

## Vollständige Biological-Spur (115/115)

| Feld | Record | Locus | Status | OWNER | stilles technisches Argument |
|---|---|---|---|---|---|
| F021 | B1 | f81v.2 | PAGE_OWNER_ONLY | `B1_SHARED_TWO_ROW_POOL` | gemeinsame zweireihige Figuren-/Beckenstation auf f81v |
| F022 | B1 | f81v.2 | INHERITED_VISIBLE | `B1_SHARED_TWO_ROW_POOL` | gemeinsame zweireihige Figuren-/Beckenstation auf f81v |
| F023 | B1 | f81v.7 | INHERITED_VISIBLE | `B1_SHARED_TWO_ROW_POOL` | gemeinsame zweireihige Figuren-/Beckenstation auf f81v |
| F024 | B1 | f81v.7 | INHERITED_VISIBLE | `B1_SHARED_TWO_ROW_POOL` | gemeinsame zweireihige Figuren-/Beckenstation auf f81v |
| F025 | B1 | f81v.17 | INHERITED_VISIBLE | `B1_SHARED_TWO_ROW_POOL` | gemeinsame zweireihige Figuren-/Beckenstation auf f81v |
| F026 | B1 | f81v.17 | INHERITED_VISIBLE | `B1_SHARED_TWO_ROW_POOL` | gemeinsame zweireihige Figuren-/Beckenstation auf f81v |
| F027 | B1 | f81v.17 | INHERITED_VISIBLE | `B1_SHARED_TWO_ROW_POOL` | gemeinsame zweireihige Figuren-/Beckenstation auf f81v |
| F028 | B1 | f81v.17 | INHERITED_VISIBLE | `B1_SHARED_TWO_ROW_POOL` | gemeinsame zweireihige Figuren-/Beckenstation auf f81v |
| F029 | B1 | f81v.18 | INHERITED_VISIBLE | `B1_SHARED_TWO_ROW_POOL` | gemeinsame zweireihige Figuren-/Beckenstation auf f81v |
| F030 | B1 | f81v.18 | INHERITED_VISIBLE | `B1_SHARED_TWO_ROW_POOL` | gemeinsame zweireihige Figuren-/Beckenstation auf f81v |
| F031 | B1 | f81v.18 | INHERITED_VISIBLE | `B1_SHARED_TWO_ROW_POOL` | gemeinsame zweireihige Figuren-/Beckenstation auf f81v |
| F032 | B1 | f81v.18 | INHERITED_VISIBLE | `B1_SHARED_TWO_ROW_POOL` | gemeinsame zweireihige Figuren-/Beckenstation auf f81v |
| F033 | B1 | f81v.18 | INHERITED_VISIBLE | `B1_SHARED_TWO_ROW_POOL` | gemeinsame zweireihige Figuren-/Beckenstation auf f81v |
| F034 | B1 | f81v.21 | INHERITED_VISIBLE | `B1_SHARED_TWO_ROW_POOL` | gemeinsame zweireihige Figuren-/Beckenstation auf f81v |
| F035 | B1 | f81v.21 | INHERITED_VISIBLE | `B1_SHARED_TWO_ROW_POOL` | gemeinsame zweireihige Figuren-/Beckenstation auf f81v |
| F036 | B1 | f81v.21 | INHERITED_VISIBLE | `B1_SHARED_TWO_ROW_POOL` | gemeinsame zweireihige Figuren-/Beckenstation auf f81v |
| F037 | B1 | f81v.24 | INHERITED_VISIBLE | `B1_SHARED_TWO_ROW_POOL` | gemeinsame zweireihige Figuren-/Beckenstation auf f81v |
| F038 | B1 | f81v.24 | INHERITED_VISIBLE | `B1_SHARED_TWO_ROW_POOL` | gemeinsame zweireihige Figuren-/Beckenstation auf f81v |
| F039 | B1 | f81v.24 | INHERITED_VISIBLE | `B1_SHARED_TWO_ROW_POOL` | gemeinsame zweireihige Figuren-/Beckenstation auf f81v |
| F040 | B1 | f81v.24 | INHERITED_VISIBLE | `B1_SHARED_TWO_ROW_POOL` | gemeinsame zweireihige Figuren-/Beckenstation auf f81v |
| F041 | B1 | f81v.27 | INHERITED_VISIBLE | `B1_SHARED_TWO_ROW_POOL` | gemeinsame zweireihige Figuren-/Beckenstation auf f81v |
| F042 | B1 | f81v.27 | INHERITED_VISIBLE | `B1_SHARED_TWO_ROW_POOL` | gemeinsame zweireihige Figuren-/Beckenstation auf f81v |
| F043 | B1 | f81v.27 | INHERITED_VISIBLE | `B1_SHARED_TWO_ROW_POOL` | gemeinsame zweireihige Figuren-/Beckenstation auf f81v |
| F044 | B1 | f81v.27 | INHERITED_VISIBLE | `B1_SHARED_TWO_ROW_POOL` | gemeinsame zweireihige Figuren-/Beckenstation auf f81v |
| F045 | B2 | f82r.2 | DIRECT_VISIBLE | `B2_UPPER_PAIRED_BASINS_AND_CYLINDER` | obere f82r-Konfiguration aus zwei Figurengefäßen, Bögen und Mittelzylinder |
| F046 | B2 | f82r.2 | INHERITED_VISIBLE | `B2_UPPER_PAIRED_BASINS_AND_CYLINDER` | obere f82r-Konfiguration aus zwei Figurengefäßen, Bögen und Mittelzylinder |
| F047 | B2 | f82r.2 | INHERITED_VISIBLE | `B2_UPPER_PAIRED_BASINS_AND_CYLINDER` | obere f82r-Konfiguration aus zwei Figurengefäßen, Bögen und Mittelzylinder |
| F048 | B2 | f82r.2 | INHERITED_VISIBLE | `B2_UPPER_PAIRED_BASINS_AND_CYLINDER` | obere f82r-Konfiguration aus zwei Figurengefäßen, Bögen und Mittelzylinder |
| F049 | B2 | f82r.3 | INHERITED_VISIBLE | `B2_UPPER_PAIRED_BASINS_AND_CYLINDER` | obere f82r-Konfiguration aus zwei Figurengefäßen, Bögen und Mittelzylinder |
| F050 | B2 | f82r.3 | INHERITED_VISIBLE | `B2_UPPER_PAIRED_BASINS_AND_CYLINDER` | obere f82r-Konfiguration aus zwei Figurengefäßen, Bögen und Mittelzylinder |
| F051 | B2 | f82r.4 | INHERITED_VISIBLE | `B2_UPPER_PAIRED_BASINS_AND_CYLINDER` | obere f82r-Konfiguration aus zwei Figurengefäßen, Bögen und Mittelzylinder |
| F052 | B2 | f82r.4 | INHERITED_VISIBLE | `B2_UPPER_PAIRED_BASINS_AND_CYLINDER` | obere f82r-Konfiguration aus zwei Figurengefäßen, Bögen und Mittelzylinder |
| F053 | B2 | f82r.7 | DIRECT_VISIBLE | `B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE` | mittlere linke Ring-/Fächerstation samt horizontalem Inline-Knoten |
| F054 | B2 | f82r.7 | INHERITED_VISIBLE | `B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE` | mittlere linke Ring-/Fächerstation samt horizontalem Inline-Knoten |
| F055 | B2 | f82r.7 | INHERITED_VISIBLE | `B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE` | mittlere linke Ring-/Fächerstation samt horizontalem Inline-Knoten |
| F056 | B2 | f82r.7 | INHERITED_VISIBLE | `B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE` | mittlere linke Ring-/Fächerstation samt horizontalem Inline-Knoten |
| F057 | B2 | f82r.19 | UNRESOLVED | `B2_MIDDLE_RIGHT_AMBIGUOUS_STATION` | örtliche mittlere f82r-Station, die nur das Exemplar zwischen Linie und Liegepodest entscheidet |
| F058 | B2 | f82r.19 | UNRESOLVED | `B2_MIDDLE_RIGHT_AMBIGUOUS_STATION` | örtliche mittlere f82r-Station, die nur das Exemplar zwischen Linie und Liegepodest entscheidet |
| F059 | B2 | f82r.23 | DIRECT_VISIBLE | `B2_LOWER_GREEN_MULTI_FIGURE_POOL` | unteres grünes Mehrfigurenfeld auf f82r |
| F060 | B2 | f82r.23 | INHERITED_VISIBLE | `B2_LOWER_GREEN_MULTI_FIGURE_POOL` | unteres grünes Mehrfigurenfeld auf f82r |
| F061 | B2 | f82r.23 | INHERITED_VISIBLE | `B2_LOWER_GREEN_MULTI_FIGURE_POOL` | unteres grünes Mehrfigurenfeld auf f82r |
| F062 | B2 | f82r.26 | DIRECT_VISIBLE | `B2_LOWER_POOL_EDGE_STATIONS` | lokale Figurenplätze am Rand des unteren f82r-Feldes |
| F063 | B2 | f82r.26 | INHERITED_VISIBLE | `B2_LOWER_POOL_EDGE_STATIONS` | lokale Figurenplätze am Rand des unteren f82r-Feldes |
| F064 | B2 | f82r.27 | INHERITED_VISIBLE | `B2_LOWER_POOL_EDGE_STATIONS` | lokale Figurenplätze am Rand des unteren f82r-Feldes |
| F065 | B2 | f82r.27 | INHERITED_VISIBLE | `B2_LOWER_POOL_EDGE_STATIONS` | lokale Figurenplätze am Rand des unteren f82r-Feldes |
| F066 | B2 | f82r.27 | INHERITED_VISIBLE | `B2_LOWER_POOL_EDGE_STATIONS` | lokale Figurenplätze am Rand des unteren f82r-Feldes |
| F067 | B2 | f82r.27 | INHERITED_VISIBLE | `B2_LOWER_POOL_EDGE_STATIONS` | lokale Figurenplätze am Rand des unteren f82r-Feldes |
| F068 | B2 | f82r.27 | INHERITED_VISIBLE | `B2_LOWER_POOL_EDGE_STATIONS` | lokale Figurenplätze am Rand des unteren f82r-Feldes |
| F069 | B2 | f82r.27 | INHERITED_VISIBLE | `B2_LOWER_POOL_EDGE_STATIONS` | lokale Figurenplätze am Rand des unteren f82r-Feldes |
| F070 | B2 | f82r.27 | INHERITED_VISIBLE | `B2_LOWER_POOL_EDGE_STATIONS` | lokale Figurenplätze am Rand des unteren f82r-Feldes |
| F071 | B3 | f83r.3 | DIRECT_VISIBLE | `B3_UPPER_MARGIN_OPEN_FAN_STATION` | oberste f83r-Randstation mit offenem Punkt-/Fächerende |
| F072 | B3 | f83r.3 | INHERITED_VISIBLE | `B3_UPPER_MARGIN_OPEN_FAN_STATION` | oberste f83r-Randstation mit offenem Punkt-/Fächerende |
| F073 | B3 | f83r.3 | INHERITED_VISIBLE | `B3_UPPER_MARGIN_OPEN_FAN_STATION` | oberste f83r-Randstation mit offenem Punkt-/Fächerende |
| F074 | B3 | f83r.3 | INHERITED_VISIBLE | `B3_UPPER_MARGIN_OPEN_FAN_STATION` | oberste f83r-Randstation mit offenem Punkt-/Fächerende |
| F075 | B3 | f83r.6 | DIRECT_VISIBLE | `B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION` | mittlere f83r-Randfigur in rundem Gefäß |
| F076 | B3 | f83r.6 | INHERITED_VISIBLE | `B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION` | mittlere f83r-Randfigur in rundem Gefäß |
| F077 | B3 | f83r.6 | INHERITED_VISIBLE | `B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION` | mittlere f83r-Randfigur in rundem Gefäß |
| F078 | B3 | f83r.6 | INHERITED_VISIBLE | `B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION` | mittlere f83r-Randfigur in rundem Gefäß |
| F079 | B3 | f83r.6 | INHERITED_VISIBLE | `B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION` | mittlere f83r-Randfigur in rundem Gefäß |
| F080 | B3 | f83r.8 | DIRECT_VISIBLE | `B3_LOWER_MARGIN_BASKET_VESSEL_STATION` | untere f83r-Randfigur im korbartigen Gefäß |
| F081 | B3 | f83r.8 | INHERITED_VISIBLE | `B3_LOWER_MARGIN_BASKET_VESSEL_STATION` | untere f83r-Randfigur im korbartigen Gefäß |
| F082 | B3 | f83r.11 | INHERITED_VISIBLE | `B3_LOWER_MARGIN_BASKET_VESSEL_STATION` | untere f83r-Randfigur im korbartigen Gefäß |
| F083 | B3 | f83r.11 | INHERITED_VISIBLE | `B3_LOWER_MARGIN_BASKET_VESSEL_STATION` | untere f83r-Randfigur im korbartigen Gefäß |
| F084 | B3 | f83r.11 | INHERITED_VISIBLE | `B3_LOWER_MARGIN_BASKET_VESSEL_STATION` | untere f83r-Randfigur im korbartigen Gefäß |
| F085 | B3 | f83r.11 | INHERITED_VISIBLE | `B3_LOWER_MARGIN_BASKET_VESSEL_STATION` | untere f83r-Randfigur im korbartigen Gefäß |
| F086 | B3 | f83r.11 | INHERITED_VISIBLE | `B3_LOWER_MARGIN_BASKET_VESSEL_STATION` | untere f83r-Randfigur im korbartigen Gefäß |
| F087 | B3 | f83r.14 | UNRESOLVED | `B3_MARGIN_TO_MAIN_GAP_UNRESOLVED` | örtlicher f83r-Posten laut Exemplar; keine Bildvererbung über die Lücke |
| F088 | B3 | f83r.14 | UNRESOLVED | `B3_MARGIN_TO_MAIN_GAP_UNRESOLVED` | örtlicher f83r-Posten laut Exemplar; keine Bildvererbung über die Lücke |
| F089 | B3 | f83r.14 | UNRESOLVED | `B3_MARGIN_TO_MAIN_GAP_UNRESOLVED` | örtlicher f83r-Posten laut Exemplar; keine Bildvererbung über die Lücke |
| F090 | B3 | f83r.14 | UNRESOLVED | `B3_MARGIN_TO_MAIN_GAP_UNRESOLVED` | örtlicher f83r-Posten laut Exemplar; keine Bildvererbung über die Lücke |
| F091 | B3 | f83r.14 | UNRESOLVED | `B3_MARGIN_TO_MAIN_GAP_UNRESOLVED` | örtlicher f83r-Posten laut Exemplar; keine Bildvererbung über die Lücke |
| F092 | B3 | f83r.14 | UNRESOLVED | `B3_MARGIN_TO_MAIN_GAP_UNRESOLVED` | örtlicher f83r-Posten laut Exemplar; keine Bildvererbung über die Lücke |
| F093 | B3 | f83r.15 | UNRESOLVED | `B3_MARGIN_TO_MAIN_GAP_UNRESOLVED` | örtlicher f83r-Posten laut Exemplar; keine Bildvererbung über die Lücke |
| F094 | B3 | f83r.15 | UNRESOLVED | `B3_MARGIN_TO_MAIN_GAP_UNRESOLVED` | örtlicher f83r-Posten laut Exemplar; keine Bildvererbung über die Lücke |
| F095 | B3 | f83r.15 | UNRESOLVED | `B3_MARGIN_TO_MAIN_GAP_UNRESOLVED` | örtlicher f83r-Posten laut Exemplar; keine Bildvererbung über die Lücke |
| F096 | B3 | f83r.16 | UNRESOLVED | `B3_MARGIN_TO_MAIN_GAP_UNRESOLVED` | örtlicher f83r-Posten laut Exemplar; keine Bildvererbung über die Lücke |
| F097 | B3 | f83r.16 | UNRESOLVED | `B3_MARGIN_TO_MAIN_GAP_UNRESOLVED` | örtlicher f83r-Posten laut Exemplar; keine Bildvererbung über die Lücke |
| F098 | B3 | f83r.16 | UNRESOLVED | `B3_MARGIN_TO_MAIN_GAP_UNRESOLVED` | örtlicher f83r-Posten laut Exemplar; keine Bildvererbung über die Lücke |
| F099 | B3 | f83r.20 | DIRECT_VISIBLE | `B3_MAIN_ARCH_LINKED_PAIR` | untere f83r-Paarstation mit gemeinsamem ungerichtetem Bogen |
| F100 | B3 | f83r.20 | INHERITED_VISIBLE | `B3_MAIN_ARCH_LINKED_PAIR` | untere f83r-Paarstation mit gemeinsamem ungerichtetem Bogen |
| F101 | B3 | f83r.20 | INHERITED_VISIBLE | `B3_MAIN_ARCH_LINKED_PAIR` | untere f83r-Paarstation mit gemeinsamem ungerichtetem Bogen |
| F102 | B3 | f83r.20 | INHERITED_VISIBLE | `B3_MAIN_ARCH_LINKED_PAIR` | untere f83r-Paarstation mit gemeinsamem ungerichtetem Bogen |
| F103 | B3 | f83r.20 | INHERITED_VISIBLE | `B3_MAIN_ARCH_LINKED_PAIR` | untere f83r-Paarstation mit gemeinsamem ungerichtetem Bogen |
| F104 | B3 | f83r.22 | INHERITED_VISIBLE | `B3_MAIN_ARCH_LINKED_PAIR` | untere f83r-Paarstation mit gemeinsamem ungerichtetem Bogen |
| F105 | B3 | f83r.22 | INHERITED_VISIBLE | `B3_MAIN_ARCH_LINKED_PAIR` | untere f83r-Paarstation mit gemeinsamem ungerichtetem Bogen |
| F106 | B3 | f83r.22 | INHERITED_VISIBLE | `B3_MAIN_ARCH_LINKED_PAIR` | untere f83r-Paarstation mit gemeinsamem ungerichtetem Bogen |
| F107 | B3 | f83r.22 | INHERITED_VISIBLE | `B3_MAIN_ARCH_LINKED_PAIR` | untere f83r-Paarstation mit gemeinsamem ungerichtetem Bogen |
| F108 | B3 | f83r.24 | INHERITED_VISIBLE | `B3_MAIN_ARCH_LINKED_PAIR` | untere f83r-Paarstation mit gemeinsamem ungerichtetem Bogen |
| F109 | B4 | f83r.25 | DIRECT_VISIBLE | `B4_MAIN_ARCH_LINKED_PAIR` | untere f83r-Paarstation als gemeinsamer Besitzer dieses Records |
| F110 | B4 | f83r.25 | INHERITED_VISIBLE | `B4_MAIN_ARCH_LINKED_PAIR` | untere f83r-Paarstation als gemeinsamer Besitzer dieses Records |
| F111 | B4 | f83r.25 | INHERITED_VISIBLE | `B4_MAIN_ARCH_LINKED_PAIR` | untere f83r-Paarstation als gemeinsamer Besitzer dieses Records |
| F112 | B4 | f83r.26 | INHERITED_VISIBLE | `B4_MAIN_ARCH_LINKED_PAIR` | untere f83r-Paarstation als gemeinsamer Besitzer dieses Records |
| F113 | B4 | f83r.26 | INHERITED_VISIBLE | `B4_MAIN_ARCH_LINKED_PAIR` | untere f83r-Paarstation als gemeinsamer Besitzer dieses Records |
| F114 | B4 | f83r.27 | INHERITED_VISIBLE | `B4_MAIN_ARCH_LINKED_PAIR` | untere f83r-Paarstation als gemeinsamer Besitzer dieses Records |
| F115 | B4 | f83r.27 | INHERITED_VISIBLE | `B4_MAIN_ARCH_LINKED_PAIR` | untere f83r-Paarstation als gemeinsamer Besitzer dieses Records |
| F116 | B4 | f83r.27 | INHERITED_VISIBLE | `B4_MAIN_ARCH_LINKED_PAIR` | untere f83r-Paarstation als gemeinsamer Besitzer dieses Records |
| F117 | B4 | f83r.28 | INHERITED_VISIBLE | `B4_MAIN_ARCH_LINKED_PAIR` | untere f83r-Paarstation als gemeinsamer Besitzer dieses Records |
| F118 | B4 | f83r.28 | INHERITED_VISIBLE | `B4_MAIN_ARCH_LINKED_PAIR` | untere f83r-Paarstation als gemeinsamer Besitzer dieses Records |
| F119 | B4 | f83r.28 | INHERITED_VISIBLE | `B4_MAIN_ARCH_LINKED_PAIR` | untere f83r-Paarstation als gemeinsamer Besitzer dieses Records |
| F120 | B4 | f83r.35 | DIRECT_VISIBLE | `B4_MAIN_LEFT_OPEN_FRINGE_STATION` | linke Hauptstation mit blauem Unterlauf und offenen Fransen |
| F121 | B4 | f83r.37 | INHERITED_VISIBLE | `B4_MAIN_LEFT_OPEN_FRINGE_STATION` | linke Hauptstation mit blauem Unterlauf und offenen Fransen |
| F122 | B4 | f83r.37 | INHERITED_VISIBLE | `B4_MAIN_LEFT_OPEN_FRINGE_STATION` | linke Hauptstation mit blauem Unterlauf und offenen Fransen |
| F123 | B4 | f83r.37 | INHERITED_VISIBLE | `B4_MAIN_LEFT_OPEN_FRINGE_STATION` | linke Hauptstation mit blauem Unterlauf und offenen Fransen |
| F124 | B4 | f83r.38 | INHERITED_VISIBLE | `B4_MAIN_LEFT_OPEN_FRINGE_STATION` | linke Hauptstation mit blauem Unterlauf und offenen Fransen |
| F125 | B4 | f83r.39 | INHERITED_VISIBLE | `B4_MAIN_LEFT_OPEN_FRINGE_STATION` | linke Hauptstation mit blauem Unterlauf und offenen Fransen |
| F126 | B4 | f83r.41 | DIRECT_VISIBLE | `B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION` | rechte Hauptstation mit S-Lauf und blauem Mehrarmknoten |
| F127 | B4 | f83r.41 | INHERITED_VISIBLE | `B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION` | rechte Hauptstation mit S-Lauf und blauem Mehrarmknoten |
| F128 | B4 | f83r.44 | INHERITED_VISIBLE | `B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION` | rechte Hauptstation mit S-Lauf und blauem Mehrarmknoten |
| F129 | B5 | f83r.47 | DIRECT_VISIBLE | `B5_LEFT_OPEN_FRINGE_STATION` | linker offener Endposten der f83r-Hauptstation |
| F130 | B5 | f83r.47 | INHERITED_VISIBLE | `B5_LEFT_OPEN_FRINGE_STATION` | linker offener Endposten der f83r-Hauptstation |
| F131 | B5 | f83r.47 | INHERITED_VISIBLE | `B5_LEFT_OPEN_FRINGE_STATION` | linker offener Endposten der f83r-Hauptstation |
| F132 | B5 | f83r.48 | INHERITED_VISIBLE | `B5_LEFT_OPEN_FRINGE_STATION` | linker offener Endposten der f83r-Hauptstation |
| F133 | B5 | f83r.49 | INHERITED_VISIBLE | `B5_LEFT_OPEN_FRINGE_STATION` | linker offener Endposten der f83r-Hauptstation |
| F134 | B6 | f83r.52 | DIRECT_VISIBLE | `B6_RIGHT_S_RUN_MULTIPORT_STATION` | rechter S-Lauf-/Mehrarmknotenposten der f83r-Hauptstation |
| F135 | B6 | f83r.54 | INHERITED_VISIBLE | `B6_RIGHT_S_RUN_MULTIPORT_STATION` | rechter S-Lauf-/Mehrarmknotenposten der f83r-Hauptstation |

## Vollständige Astro-Spur (142/142)

| Locus | Diagramm | Gruppen | Namespace | Status | OWNER | stilles technisches Argument |
|---|---|---:|---|---|---|---|
| f67r2.1 | A1 | 3 | `A1_RIGHT_WHEEL` | DIRECT_VISIBLE | `A1_RIGHT_SECTOR_SLOT_01` | dieser lokale Sektorplatz 01 des rechten f67r2-Rades |
| f67r2.2 | A1 | 3 | `A1_RIGHT_WHEEL` | DIRECT_VISIBLE | `A1_RIGHT_SECTOR_SLOT_02` | dieser lokale Sektorplatz 02 des rechten f67r2-Rades |
| f67r2.3 | A1 | 3 | `A1_RIGHT_WHEEL` | DIRECT_VISIBLE | `A1_RIGHT_SECTOR_SLOT_03` | dieser lokale Sektorplatz 03 des rechten f67r2-Rades |
| f67r2.4 | A1 | 2 | `A1_RIGHT_WHEEL` | DIRECT_VISIBLE | `A1_RIGHT_SECTOR_SLOT_04` | dieser lokale Sektorplatz 04 des rechten f67r2-Rades |
| f67r2.5 | A1 | 2 | `A1_RIGHT_WHEEL` | DIRECT_VISIBLE | `A1_RIGHT_SECTOR_SLOT_05` | dieser lokale Sektorplatz 05 des rechten f67r2-Rades |
| f67r2.6 | A1 | 1 | `A1_RIGHT_WHEEL` | DIRECT_VISIBLE | `A1_RIGHT_SECTOR_SLOT_06` | dieser lokale Sektorplatz 06 des rechten f67r2-Rades |
| f67r2.7 | A1 | 3 | `A1_RIGHT_WHEEL` | DIRECT_VISIBLE | `A1_RIGHT_SECTOR_SLOT_07` | dieser lokale Sektorplatz 07 des rechten f67r2-Rades |
| f67r2.8 | A1 | 1 | `A1_RIGHT_WHEEL` | DIRECT_VISIBLE | `A1_RIGHT_SECTOR_SLOT_08` | dieser lokale Sektorplatz 08 des rechten f67r2-Rades |
| f67r2.9 | A1 | 2 | `A1_RIGHT_WHEEL` | DIRECT_VISIBLE | `A1_RIGHT_SECTOR_SLOT_09` | dieser lokale Sektorplatz 09 des rechten f67r2-Rades |
| f67r2.10 | A1 | 3 | `A1_RIGHT_WHEEL` | DIRECT_VISIBLE | `A1_RIGHT_SECTOR_SLOT_10` | dieser lokale Sektorplatz 10 des rechten f67r2-Rades |
| f67r2.11 | A1 | 3 | `A1_RIGHT_WHEEL` | DIRECT_VISIBLE | `A1_RIGHT_SECTOR_SLOT_11` | dieser lokale Sektorplatz 11 des rechten f67r2-Rades |
| f67r2.12 | A1 | 2 | `A1_RIGHT_WHEEL` | DIRECT_VISIBLE | `A1_RIGHT_SECTOR_SLOT_12` | dieser lokale Sektorplatz 12 des rechten f67r2-Rades |
| f67r2.13 | A1 | 4 | `A1_RIGHT_WHEEL` | INHERITED_VISIBLE | `A1_RIGHT_RING_BAND_01` | gegenwärtiges Ringband des rechten f67r2-Rades |
| f67r2.14 | A1 | 3 | `A1_RIGHT_WHEEL` | INHERITED_VISIBLE | `A1_RIGHT_RING_BAND_02` | gegenwärtiges Ringband des rechten f67r2-Rades |
| f67r2.15 | A1 | 1 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_15` | gegenwärtiges lokales Radial-/Ringfeld 15 des linken f67r2-Rades |
| f67r2.16 | A1 | 4 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_16` | gegenwärtiges lokales Radial-/Ringfeld 16 des linken f67r2-Rades |
| f67r2.17 | A1 | 3 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_17` | gegenwärtiges lokales Radial-/Ringfeld 17 des linken f67r2-Rades |
| f67r2.18 | A1 | 3 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_18` | gegenwärtiges lokales Radial-/Ringfeld 18 des linken f67r2-Rades |
| f67r2.19 | A1 | 4 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_19` | gegenwärtiges lokales Radial-/Ringfeld 19 des linken f67r2-Rades |
| f67r2.20 | A1 | 2 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_20` | gegenwärtiges lokales Radial-/Ringfeld 20 des linken f67r2-Rades |
| f67r2.21 | A1 | 3 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_21` | gegenwärtiges lokales Radial-/Ringfeld 21 des linken f67r2-Rades |
| f67r2.22 | A1 | 1 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_22` | gegenwärtiges lokales Radial-/Ringfeld 22 des linken f67r2-Rades |
| f67r2.23 | A1 | 2 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_23` | gegenwärtiges lokales Radial-/Ringfeld 23 des linken f67r2-Rades |
| f67r2.24 | A1 | 3 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_24` | gegenwärtiges lokales Radial-/Ringfeld 24 des linken f67r2-Rades |
| f67r2.25 | A1 | 1 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_25` | gegenwärtiges lokales Radial-/Ringfeld 25 des linken f67r2-Rades |
| f67r2.26 | A1 | 3 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_26` | gegenwärtiges lokales Radial-/Ringfeld 26 des linken f67r2-Rades |
| f67r2.27 | A1 | 4 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_27` | gegenwärtiges lokales Radial-/Ringfeld 27 des linken f67r2-Rades |
| f67r2.28 | A1 | 2 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_28` | gegenwärtiges lokales Radial-/Ringfeld 28 des linken f67r2-Rades |
| f67r2.29 | A1 | 2 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_29` | gegenwärtiges lokales Radial-/Ringfeld 29 des linken f67r2-Rades |
| f67r2.30 | A1 | 2 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_30` | gegenwärtiges lokales Radial-/Ringfeld 30 des linken f67r2-Rades |
| f67r2.31 | A1 | 1 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_31` | gegenwärtiges lokales Radial-/Ringfeld 31 des linken f67r2-Rades |
| f67r2.32 | A1 | 4 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_32` | gegenwärtiges lokales Radial-/Ringfeld 32 des linken f67r2-Rades |
| f67r2.33 | A1 | 3 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_33` | gegenwärtiges lokales Radial-/Ringfeld 33 des linken f67r2-Rades |
| f67r2.34 | A1 | 2 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_34` | gegenwärtiges lokales Radial-/Ringfeld 34 des linken f67r2-Rades |
| f67r2.35 | A1 | 3 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_35` | gegenwärtiges lokales Radial-/Ringfeld 35 des linken f67r2-Rades |
| f67r2.36 | A1 | 3 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_36` | gegenwärtiges lokales Radial-/Ringfeld 36 des linken f67r2-Rades |
| f67r2.37 | A1 | 1 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_37` | gegenwärtiges lokales Radial-/Ringfeld 37 des linken f67r2-Rades |
| f67r2.38 | A1 | 2 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_38` | gegenwärtiges lokales Radial-/Ringfeld 38 des linken f67r2-Rades |
| f67r2.39 | A1 | 3 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_39` | gegenwärtiges lokales Radial-/Ringfeld 39 des linken f67r2-Rades |
| f67r2.40 | A1 | 3 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_40` | gegenwärtiges lokales Radial-/Ringfeld 40 des linken f67r2-Rades |
| f67r2.41 | A1 | 2 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_41` | gegenwärtiges lokales Radial-/Ringfeld 41 des linken f67r2-Rades |
| f67r2.42 | A1 | 3 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_42` | gegenwärtiges lokales Radial-/Ringfeld 42 des linken f67r2-Rades |
| f67r2.43 | A1 | 4 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_43` | gegenwärtiges lokales Radial-/Ringfeld 43 des linken f67r2-Rades |
| f67r2.44 | A1 | 3 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_44` | gegenwärtiges lokales Radial-/Ringfeld 44 des linken f67r2-Rades |
| f67r2.45 | A1 | 3 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_45` | gegenwärtiges lokales Radial-/Ringfeld 45 des linken f67r2-Rades |
| f67r2.46 | A1 | 2 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_46` | gegenwärtiges lokales Radial-/Ringfeld 46 des linken f67r2-Rades |
| f67r2.47 | A1 | 1 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_47` | gegenwärtiges lokales Radial-/Ringfeld 47 des linken f67r2-Rades |
| f67r2.48 | A1 | 3 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_48` | gegenwärtiges lokales Radial-/Ringfeld 48 des linken f67r2-Rades |
| f67r2.49 | A1 | 3 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_49` | gegenwärtiges lokales Radial-/Ringfeld 49 des linken f67r2-Rades |
| f67r2.50 | A1 | 2 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_50` | gegenwärtiges lokales Radial-/Ringfeld 50 des linken f67r2-Rades |
| f67r2.51 | A1 | 1 | `A1_LEFT_WHEEL` | INHERITED_VISIBLE | `A1_LEFT_LOCAL_FIELD_51` | gegenwärtiges lokales Radial-/Ringfeld 51 des linken f67r2-Rades |
| f67r2.52 | A1 | 1 | `A1_LEFT_WHEEL` | DIRECT_VISIBLE | `A1_LEFT_OUTER_STAR_STATION_01` | äußerer Sternplatz 01 des linken f67r2-Rades |
| f67r2.53 | A1 | 1 | `A1_LEFT_WHEEL` | DIRECT_VISIBLE | `A1_LEFT_OUTER_STAR_STATION_02` | äußerer Sternplatz 02 des linken f67r2-Rades |
| f67r2.54 | A1 | 2 | `A1_LEFT_WHEEL` | DIRECT_VISIBLE | `A1_LEFT_OUTER_STAR_STATION_03` | äußerer Sternplatz 03 des linken f67r2-Rades |
| f67r2.55 | A1 | 1 | `A1_LEFT_WHEEL` | DIRECT_VISIBLE | `A1_LEFT_OUTER_STAR_STATION_04` | äußerer Sternplatz 04 des linken f67r2-Rades |
| f67r2.56 | A1 | 2 | `A1_LEFT_WHEEL` | DIRECT_VISIBLE | `A1_LEFT_OUTER_STAR_STATION_05` | äußerer Sternplatz 05 des linken f67r2-Rades |
| f67r2.57 | A1 | 2 | `A1_LEFT_WHEEL` | DIRECT_VISIBLE | `A1_LEFT_OUTER_STAR_STATION_06` | äußerer Sternplatz 06 des linken f67r2-Rades |
| f67r2.58 | A1 | 3 | `A1_LEFT_WHEEL` | DIRECT_VISIBLE | `A1_LEFT_OUTER_STAR_STATION_07` | äußerer Sternplatz 07 des linken f67r2-Rades |
| f67r2.59 | A1 | 1 | `A1_LEFT_WHEEL` | DIRECT_VISIBLE | `A1_LEFT_OUTER_STAR_STATION_08` | äußerer Sternplatz 08 des linken f67r2-Rades |
| f67r2.60 | A1 | 1 | `A1_LEFT_WHEEL` | DIRECT_VISIBLE | `A1_LEFT_OUTER_STAR_STATION_09` | äußerer Sternplatz 09 des linken f67r2-Rades |
| f67r2.61 | A1 | 1 | `A1_LEFT_WHEEL` | DIRECT_VISIBLE | `A1_LEFT_OUTER_STAR_STATION_10` | äußerer Sternplatz 10 des linken f67r2-Rades |
| f67r2.62 | A1 | 1 | `A1_LEFT_WHEEL` | DIRECT_VISIBLE | `A1_LEFT_OUTER_STAR_STATION_11` | äußerer Sternplatz 11 des linken f67r2-Rades |
| f67r2.63 | A1 | 1 | `A1_LEFT_WHEEL` | DIRECT_VISIBLE | `A1_LEFT_OUTER_STAR_STATION_12` | äußerer Sternplatz 12 des linken f67r2-Rades |
| f67r2.64 | A1 | 2 | `A1_RIGHT_WHEEL` | DIRECT_VISIBLE | `A1_RIGHT_PHASE_STATION_01` | lokaler Scheiben-/Bedingungsplatz 01 des rechten f67r2-Rades |
| f67r2.65 | A1 | 1 | `A1_RIGHT_WHEEL` | DIRECT_VISIBLE | `A1_RIGHT_PHASE_STATION_02` | lokaler Scheiben-/Bedingungsplatz 02 des rechten f67r2-Rades |
| f67r2.66 | A1 | 1 | `A1_RIGHT_WHEEL` | DIRECT_VISIBLE | `A1_RIGHT_PHASE_STATION_03` | lokaler Scheiben-/Bedingungsplatz 03 des rechten f67r2-Rades |
| f67r2.67 | A1 | 1 | `A1_RIGHT_WHEEL` | DIRECT_VISIBLE | `A1_RIGHT_PHASE_STATION_04` | lokaler Scheiben-/Bedingungsplatz 04 des rechten f67r2-Rades |
| f67r2.68 | A1 | 1 | `A1_RIGHT_WHEEL` | DIRECT_VISIBLE | `A1_RIGHT_PHASE_STATION_05` | lokaler Scheiben-/Bedingungsplatz 05 des rechten f67r2-Rades |
| f67r2.69 | A1 | 2 | `A1_RIGHT_WHEEL` | DIRECT_VISIBLE | `A1_RIGHT_PHASE_STATION_06` | lokaler Scheiben-/Bedingungsplatz 06 des rechten f67r2-Rades |
| f67r2.70 | A1 | 1 | `A1_RIGHT_WHEEL` | DIRECT_VISIBLE | `A1_RIGHT_PHASE_STATION_07` | lokaler Scheiben-/Bedingungsplatz 07 des rechten f67r2-Rades |
| f67r2.71 | A1 | 1 | `A1_RIGHT_WHEEL` | DIRECT_VISIBLE | `A1_RIGHT_PHASE_STATION_08` | lokaler Scheiben-/Bedingungsplatz 08 des rechten f67r2-Rades |
| f67r2.72 | A1 | 12 | `A1_LEFT_WHEEL` | DIRECT_VISIBLE | `A1_LEFT_OUTER_RING_TEXT` | äußeres Textband des linken f67r2-Rades |
| f67r2.73 | A1 | 11 | `A1_RIGHT_WHEEL` | DIRECT_VISIBLE | `A1_RIGHT_OUTER_RING_TEXT` | äußeres Textband des rechten f67r2-Rades |
| f67r2.74 | A1 | 13 | `A1_PAGE` | UNRESOLVED | `A1_PAIRED_WHEEL_LEGEND_UNRESOLVED` | seitenlokale Legende; das Exemplar entscheidet linkes oder rechtes Rad |
| f68r1.1 | A2 | 9 | `A2_LEFT_STAR_FIELD` | PAGE_OWNER_ONLY | `A2_LEFT_PANEL_HEADER` | lokale Kopf-/Legendenangabe des zugeordneten f68r1-Paneels |
| f68r1.2 | A2 | 9 | `A2_MIDDLE_STAR_FIELD` | PAGE_OWNER_ONLY | `A2_MIDDLE_PANEL_HEADER` | lokale Kopf-/Legendenangabe des zugeordneten f68r1-Paneels |
| f68r1.3 | A2 | 8 | `A2_RIGHT_SECTORIZED_MAP` | PAGE_OWNER_ONLY | `A2_RIGHT_PANEL_HEADER` | lokale Kopf-/Legendenangabe des zugeordneten f68r1-Paneels |
| f68r1.4 | A2 | 2 | `A2_MULTIPANEL_PAGE` | UNRESOLVED | `A2_MULTIPANEL_HEADER_FRAGMENT_04` | mehrpaneelige Seitenlegende laut Exemplar |
| f68r1.5 | A2 | 1 | `A2_MULTIPANEL_PAGE` | UNRESOLVED | `A2_MULTIPANEL_HEADER_FRAGMENT_05` | mehrpaneelige Seitenlegende laut Exemplar |
| f68r1.6 | A2 | 1 | `A2_MULTIPANEL_PAGE` | UNRESOLVED | `A2_MULTIPANEL_HEADER_FRAGMENT_06` | mehrpaneelige Seitenlegende laut Exemplar |
| f68r1.7 | A2 | 1 | `A2_MULTIPANEL_PAGE` | UNRESOLVED | `A2_MULTIPANEL_HEADER_FRAGMENT_07` | mehrpaneelige Seitenlegende laut Exemplar |
| f68r1.8 | A2 | 1 | `A2_MULTIPANEL_PAGE` | UNRESOLVED | `A2_CENTRE_KEY_UNRESOLVED` | eines der sichtbaren Gesichtmedaillons; genaue Wahl nur aus dem Exemplar |
| f68r1.9 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_01` | sichtbarer lokal beschrifteter Sternplatz 01 im f68r1-Atlas |
| f68r1.10 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_02` | sichtbarer lokal beschrifteter Sternplatz 02 im f68r1-Atlas |
| f68r1.11 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_03` | sichtbarer lokal beschrifteter Sternplatz 03 im f68r1-Atlas |
| f68r1.12 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_04` | sichtbarer lokal beschrifteter Sternplatz 04 im f68r1-Atlas |
| f68r1.13 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_05` | sichtbarer lokal beschrifteter Sternplatz 05 im f68r1-Atlas |
| f68r1.14 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_06` | sichtbarer lokal beschrifteter Sternplatz 06 im f68r1-Atlas |
| f68r1.15 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_07` | sichtbarer lokal beschrifteter Sternplatz 07 im f68r1-Atlas |
| f68r1.16 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_08` | sichtbarer lokal beschrifteter Sternplatz 08 im f68r1-Atlas |
| f68r1.17 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_09` | sichtbarer lokal beschrifteter Sternplatz 09 im f68r1-Atlas |
| f68r1.18 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_10` | sichtbarer lokal beschrifteter Sternplatz 10 im f68r1-Atlas |
| f68r1.19 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_11` | sichtbarer lokal beschrifteter Sternplatz 11 im f68r1-Atlas |
| f68r1.20 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_12` | sichtbarer lokal beschrifteter Sternplatz 12 im f68r1-Atlas |
| f68r1.21 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_13` | sichtbarer lokal beschrifteter Sternplatz 13 im f68r1-Atlas |
| f68r1.22 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_14` | sichtbarer lokal beschrifteter Sternplatz 14 im f68r1-Atlas |
| f68r1.23 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_15` | sichtbarer lokal beschrifteter Sternplatz 15 im f68r1-Atlas |
| f68r1.24 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_16` | sichtbarer lokal beschrifteter Sternplatz 16 im f68r1-Atlas |
| f68r1.25 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_17` | sichtbarer lokal beschrifteter Sternplatz 17 im f68r1-Atlas |
| f68r1.26 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_18` | sichtbarer lokal beschrifteter Sternplatz 18 im f68r1-Atlas |
| f68r1.27 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_19` | sichtbarer lokal beschrifteter Sternplatz 19 im f68r1-Atlas |
| f68r1.28 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_20` | sichtbarer lokal beschrifteter Sternplatz 20 im f68r1-Atlas |
| f68r1.29 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_21` | sichtbarer lokal beschrifteter Sternplatz 21 im f68r1-Atlas |
| f68r1.30 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_22` | sichtbarer lokal beschrifteter Sternplatz 22 im f68r1-Atlas |
| f68r1.31 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_23` | sichtbarer lokal beschrifteter Sternplatz 23 im f68r1-Atlas |
| f68r1.32 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_24` | sichtbarer lokal beschrifteter Sternplatz 24 im f68r1-Atlas |
| f68r1.33 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_25` | sichtbarer lokal beschrifteter Sternplatz 25 im f68r1-Atlas |
| f68r1.34 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_26` | sichtbarer lokal beschrifteter Sternplatz 26 im f68r1-Atlas |
| f68r1.35 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_27` | sichtbarer lokal beschrifteter Sternplatz 27 im f68r1-Atlas |
| f68r1.36 | A2 | 1 | `A2_LOCAL_STAR_CATALOGUE` | DIRECT_VISIBLE | `A2_STAR_STATION_28` | sichtbarer lokal beschrifteter Sternplatz 28 im f68r1-Atlas |
| f68r1.37 | A2 | 5 | `A2_MULTIPANEL_PAGE` | UNRESOLVED | `A2_CENTRAL_LEGEND_UNRESOLVED` | lokale Zentrallegende eines f68r1-Teilbildes laut Exemplar |
| f69v.1 | A3 | 40 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_WHEEL_RING_TEXT` | Ringtext des linken 28-Platz-Rades |
| f69v.2 | A3 | 38 | `A3_MIDDLE_WHEEL` | DIRECT_VISIBLE | `A3_MIDDLE_WHEEL_RING_TEXT` | Ringtext des mittleren Wolken-/Wellenrades |
| f69v.3 | A3 | 29 | `A3_RIGHT_WHEEL` | DIRECT_VISIBLE | `A3_RIGHT_WHEEL_RING_TEXT` | Ringtext des rechten Gesicht-Strahlenrades |
| f69v.4 | A3 | 2 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_01` | lokaler Radialplatz 01 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.5 | A3 | 2 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_02` | lokaler Radialplatz 02 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.6 | A3 | 1 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_03` | lokaler Radialplatz 03 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.7 | A3 | 1 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_04` | lokaler Radialplatz 04 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.8 | A3 | 1 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_05` | lokaler Radialplatz 05 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.9 | A3 | 1 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_06` | lokaler Radialplatz 06 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.10 | A3 | 1 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_07` | lokaler Radialplatz 07 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.11 | A3 | 1 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_08` | lokaler Radialplatz 08 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.12 | A3 | 1 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_09` | lokaler Radialplatz 09 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.13 | A3 | 1 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_10` | lokaler Radialplatz 10 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.14 | A3 | 1 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_11` | lokaler Radialplatz 11 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.15 | A3 | 1 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_12` | lokaler Radialplatz 12 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.16 | A3 | 1 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_13` | lokaler Radialplatz 13 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.17 | A3 | 1 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_14` | lokaler Radialplatz 14 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.18 | A3 | 1 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_15` | lokaler Radialplatz 15 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.19 | A3 | 1 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_16` | lokaler Radialplatz 16 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.20 | A3 | 1 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_17` | lokaler Radialplatz 17 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.21 | A3 | 1 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_18` | lokaler Radialplatz 18 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.22 | A3 | 1 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_19` | lokaler Radialplatz 19 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.23 | A3 | 1 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_20` | lokaler Radialplatz 20 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.24 | A3 | 1 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_21` | lokaler Radialplatz 21 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.25 | A3 | 2 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_22` | lokaler Radialplatz 22 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.26 | A3 | 2 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_23` | lokaler Radialplatz 23 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.27 | A3 | 1 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_24` | lokaler Radialplatz 24 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.28 | A3 | 1 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_25` | lokaler Radialplatz 25 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.29 | A3 | 1 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_26` | lokaler Radialplatz 26 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.30 | A3 | 1 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_27` | lokaler Radialplatz 27 des linken f69v-Rades; Nummer nur editoriale Adresse |
| f69v.31 | A3 | 2 | `A3_LEFT_WHEEL` | DIRECT_VISIBLE | `A3_LEFT_RADIAL_SLOT_28` | lokaler Radialplatz 28 des linken f69v-Rades; Nummer nur editoriale Adresse |

## Vollständige Beispielausführung vorwärts/rückwärts

### Herbal H1→H2

`RESET H1 → PAGE_OWNER(root axis) → F001 → inherit F002 → RESET → PAGE_OWNER(upper shoot) → F003 → inherit F004–F005 → RESET`.
Rückwärts darf F003 nie den H1-Wurzelposten liefern; das H2-Record setzt einen neuen sichtbaren Teilbesitzer.

### Biological f82r

`upper station(F045–F052) → BREAK → middle-left(F053–F056) → BREAK → UNRESOLVED gap(F057–F058) → BREAK → lower pool(F059–F061) → BREAK → edge stations(F062–F070)`.
Kein Rückwärtslauf darf F057/F058 über die sichtbare Lücke mit dem Podest oder dem Inline-Knoten gleichsetzen.

### Astro f69v

`LEFT_RING(f69v.1) | MIDDLE_RING(f69v.2) | RIGHT_RING(f69v.3) | LEFT_SLOT_01..28(f69v.4..31)`.
Die senkrechten Striche bedeuten parallele lokale Namensräume. Weder Vorwärts- noch Rückwärtslesen erzeugt Start, Rotation oder einen Join.

## Grenze

Das Resultat etabliert höchstens eine ausführbare Bildellipsis: Ein Schreiber kann
ein sichtbares Objekt auslassen, wenn Record und Bildraum den Besitzer erhalten.
Es bestätigt kein Voynich-Wort und keine konkrete Quellenoperation. f84 und f84r
blieben versiegelt; keine andere Seite wurde verwendet.
