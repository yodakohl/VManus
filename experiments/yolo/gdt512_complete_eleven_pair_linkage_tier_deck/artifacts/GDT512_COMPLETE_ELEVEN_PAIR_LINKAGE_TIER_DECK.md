# GDT512 — Aktuelles Elf-Karten-Blatt in sieben Stützstufen

Status: `ELEVEN_PAIR_CARDS_REISSUED_IN_SEVEN_SUPPORT_TIERS__THREE_RETAIN_CROSS_PAIR_ORDER`

| Stufe | Karten | Bedeutung | Paarordnung nur fremd |
|---|---:|---|---:|
| T1_LOCAL_ARGUMENT_COMPATIBLE_FRAME_REDUCTION | 3 | Lokaler argumentkompatibler Rahmenabbau | 0 |
| T2_LOCAL_CONTEXT_BRIDGE | 3 | Lokale unmittelbare/innerhalb-Karte-Kontextbrücke | 0 |
| T3_LOCAL_REPEATED_PACKAGE_PROJECTION | 1 | Lokale Wiederholung eines größeren Pakets | 0 |
| T4_LOCAL_CONTIGUOUS_SUFFIX_REDUCTION | 1 | Lokaler exakter zusammenhängender Suffix | 0 |
| T5_LOCAL_LONG_SAME_STATEMENT_HEAD_INVENTORY | 1 | Langes lokales Kopf-Inventar in derselben Anweisung | 1 |
| T6_LOCAL_LONG_SAME_OWNER_PAGE_HEAD_INVENTORY | 1 | Langes lokales Kopf-Inventar bei demselben Besitzer | 1 |
| T7_LOCAL_LONG_SAME_PAGE_CROSS_OWNER_HEAD_INVENTORY | 1 | Langes lokales Kopf-Inventar nur auf derselben Seite | 1 |

## Lokaler argumentkompatibler Rahmenabbau

- **PHARMA `CH+P`:** Nimm das zuvor Genannte und setze es ein.
  - Stütze: Ein alter Träger im Zielregister reduziert geordnet auf den Zielrahmen und behält denselben Argumentmodus.
  - Rest: Das nackte Zielrezept selbst ist nicht beobachtet.
- **SOURCE_SECTION_T `CH+P`:** Entnimm das zuvor Genannte und setze es ein.
  - Stütze: Ein alter Träger im Zielregister reduziert geordnet auf den Zielrahmen und behält denselben Argumentmodus.
  - Rest: Das nackte Zielrezept selbst ist nicht beobachtet.
- **PHARMA `P+CH+E+Y`:** Setze den Drogenposten ein und nimm den Drogenposten; auf Grad I.
  - Stütze: Ein alter Träger im Zielregister reduziert geordnet auf den Zielrahmen und behält denselben Argumentmodus.
  - Rest: Das nackte Zielrezept selbst ist nicht beobachtet.

## Lokale unmittelbare/innerhalb-Karte-Kontextbrücke

- **PHARMA `CH+CH`:** Nimm das zuvor Genannte zweimal.
  - Stütze: Die Paarordnung ist alt; im Zielregister trägt eine konkrete gleiche-Argument-Folge die fehlende Kontextmechanik.
  - Rest: Paarordnung und Kontextmechanik können auf verschiedene alte Karten verteilt sein.
- **PHARMA `CH+SH`:** Nimm das zuvor Genannte und halte es.
  - Stütze: Die Paarordnung ist alt; im Zielregister trägt eine konkrete gleiche-Argument-Folge die fehlende Kontextmechanik.
  - Rest: Paarordnung und Kontextmechanik können auf verschiedene alte Karten verteilt sein.
- **SOURCE_SECTION_T `CH+SH`:** Entnimm das zuvor Genannte und halte es fest.
  - Stütze: Die Paarordnung ist alt; im Zielregister trägt eine konkrete gleiche-Argument-Folge die fehlende Kontextmechanik.
  - Rest: Paarordnung und Kontextmechanik können auf verschiedene alte Karten verteilt sein.

## Lokale Wiederholung eines größeren Pakets

- **SOURCE_SECTION_T `CH+CH`:** Entnimm das zuvor Genannte zweimal.
  - Stütze: Die Paarordnung ist alt; im Source-Register wiederholt ein exaktes CH-tragendes Paket denselben geerbten Wert, und je ein CH-Slot bleibt erhalten.
  - Rest: Die lokale Brücke liegt auf Paketprojektionsebene, nicht als nacktes CH+CH-Ereignis.

## Lokaler exakter zusammenhängender Suffix

- **CELESTIAL `P+CH+E+Y`:** Setze den Positionsposten ein und nimm den Positionsposten auf; auf Grad I.
  - Stütze: Der vollständige Zielrahmen steht im Zielregister als exakter zusammenhängender Suffix einer längeren Karte.
  - Rest: Der Zielrahmen ist nur als Suffix einer längeren lokalen Drei-Aktions-Karte alt; die nackte Zielkarte bleibt unbelegt.

## Langes lokales Kopf-Inventar in derselben Anweisung

- **SOURCE_SECTION_T `S+CHD+Y`:** Wähle den laufenden Eintrag und bearbeite den laufenden Eintrag.
  - Stütze: Beide Köpfe liegen in derselben Anweisung, aber nicht unmittelbar und nicht unter durchgehendem Y-Zustand. Die gerichtete Paarordnung bleibt bei G407-E1883.
  - Rest: Die lokalen Köpfe bilden weder ein unmittelbares noch ein Y-kontinuierliches Paar; das nackte Zielrezept bleibt unbelegt.

## Langes lokales Kopf-Inventar bei demselben Besitzer

- **PHARMA `S+CHD+Y`:** Wähle den Drogenposten und bearbeite den Drogenposten.
  - Stütze: Beide Köpfe liegen beim selben Besitzer auf derselben Seite, aber nicht in derselben Anweisung oder unter durchgehendem Y-Zustand. Die gerichtete Paarordnung bleibt bei G407-E1883.
  - Rest: Die lokalen Köpfe bilden weder ein unmittelbares noch ein Y-kontinuierliches Paar; das nackte Zielrezept bleibt unbelegt.

## Langes lokales Kopf-Inventar nur auf derselben Seite

- **CELESTIAL `S+CHD+Y`:** Wähle den Positionsposten und bearbeite den Positionsposten.
  - Stütze: Beide Köpfe liegen auf derselben Seite, aber bei verschiedenen Besitzern und nicht unter durchgehendem Y-Zustand. Die gerichtete Paarordnung bleibt bei G407-E1883.
  - Rest: Die lokalen Köpfe bilden weder ein unmittelbares noch ein Y-kontinuierliches Paar; das nackte Zielrezept bleibt unbelegt.

## Gemeinsame Grenze

Alle elf Zielrezepte bleiben unbeobachtete `COMPOSED_WORKING`-Karten. Acht besitzen im Zielregister eine gerichtete Paar-, Intervall- oder Paketprojektion; bei den drei `S+CHD+Y`-Karten bleiben nur die Einzelköpfe lokal und die Paarordnung kommt weiterhin aus `G407-E1883`. Keine Phrase oder Wurzelbedeutung ändert sich.
