# GDT506 — Rahmenverträglichkeit der elf Paarziele

Status: `SEVEN_TARGET_FRAMES_HAVE_ARGUMENT_COMPATIBLE_REDUCTIONS__FOUR_CONTEXTUAL_TRANSFERS_REMAIN_OPEN`

Jedes Zielrezept wird als geordnete Teilfolge aller alten Träger seines
Handgriffs gesucht. Zusätzlich muss der alte Argumentmodus zum Ziel
passen. Eine offene Karte bleibt als Annahme erhalten.

## Elf Karten in Prioritätsreihenfolge

### Rang 1 · G506-T06 · `CH+P` · PHARMA

**Nimm das zuvor Genannte und setze es ein.**

- Tier: `A_LOCAL_ARGUMENT_COMPATIBLE_REDUCTION` — Ein alter Träger im Zielregister reduziert auf das Zielrezept und hat denselben Argumentmodus.
- Reduktionen: 25; argumentverträglich: 13; davon lokal: 3.
- Bester alter Träger: `CH+P+OL` · PHARMA; entfernt `OL`.

### Rang 2 · G506-T07 · `CH+P` · SOURCE_SECTION_T

**Entnimm das zuvor Genannte und setze es ein.**

- Tier: `A_LOCAL_ARGUMENT_COMPATIBLE_REDUCTION` — Ein alter Träger im Zielregister reduziert auf das Zielrezept und hat denselben Argumentmodus.
- Reduktionen: 25; argumentverträglich: 13; davon lokal: 3.
- Bester alter Träger: `CH+P+AR` · SOURCE_SECTION_T; entfernt `AR`.

### Rang 3 · G506-T01 · `P+CH+E+Y` · PHARMA

**Setze den Drogenposten ein und nimm den Drogenposten; auf Grad I.**

- Tier: `A_LOCAL_ARGUMENT_COMPATIBLE_REDUCTION` — Ein alter Träger im Zielregister reduziert auf das Zielrezept und hat denselben Argumentmodus.
- Reduktionen: 1; argumentverträglich: 1; davon lokal: 1.
- Bester alter Träger: `P+CH+E+O+L+Y` · PHARMA; entfernt `O+L`.

### Rang 4 · G506-T02 · `S+CHD+Y` · CELESTIAL

**Wähle den Positionsposten und bearbeite den Positionsposten.**

- Tier: `B_CROSS_REGISTER_ARGUMENT_COMPATIBLE_REDUCTION` — Die passende Rahmenreduktion ist alt, aber nur in einem anderen Register.
- Reduktionen: 4; argumentverträglich: 4; davon lokal: 0.
- Bester alter Träger: `S+OL+CHD+Y` · BIOLOGICAL; entfernt `OL`.

### Rang 5 · G506-T04 · `S+CHD+Y` · PHARMA

**Wähle den Drogenposten und bearbeite den Drogenposten.**

- Tier: `B_CROSS_REGISTER_ARGUMENT_COMPATIBLE_REDUCTION` — Die passende Rahmenreduktion ist alt, aber nur in einem anderen Register.
- Reduktionen: 4; argumentverträglich: 4; davon lokal: 0.
- Bester alter Träger: `S+OL+CHD+Y` · BIOLOGICAL; entfernt `OL`.

### Rang 6 · G506-T05 · `S+CHD+Y` · SOURCE_SECTION_T

**Wähle den laufenden Eintrag und bearbeite den laufenden Eintrag.**

- Tier: `B_CROSS_REGISTER_ARGUMENT_COMPATIBLE_REDUCTION` — Die passende Rahmenreduktion ist alt, aber nur in einem anderen Register.
- Reduktionen: 4; argumentverträglich: 4; davon lokal: 0.
- Bester alter Träger: `S+OL+CHD+Y` · BIOLOGICAL; entfernt `OL`.

### Rang 7 · G506-T03 · `P+CH+E+Y` · CELESTIAL

**Setze den Positionsposten ein und nimm den Positionsposten auf; auf Grad I.**

- Tier: `B_CROSS_REGISTER_ARGUMENT_COMPATIBLE_REDUCTION` — Die passende Rahmenreduktion ist alt, aber nur in einem anderen Register.
- Reduktionen: 1; argumentverträglich: 1; davon lokal: 0.
- Bester alter Träger: `P+CH+E+O+L+Y` · PHARMA; entfernt `O+L`.

### Rang 8 · G506-T08 · `CH+CH` · PHARMA

**Nimm das zuvor Genannte zweimal.**

- Tier: `C_ACTION_HANDGRIP_ONLY__ARGUMENT_MODE_OPEN` — Die Handlungskette ist alt; alte Träger nennen jedoch Argumente explizit, während das Ziel sie aus dem Kontext erbt.
- Reduktionen: 7; argumentverträglich: 0; davon lokal: 0.
- Bester alter Träger: `CH+OR+CH+Y` · HERBAL; entfernt `OR+Y`.

### Rang 9 · G506-T09 · `CH+CH` · SOURCE_SECTION_T

**Entnimm das zuvor Genannte zweimal.**

- Tier: `C_ACTION_HANDGRIP_ONLY__ARGUMENT_MODE_OPEN` — Die Handlungskette ist alt; alte Träger nennen jedoch Argumente explizit, während das Ziel sie aus dem Kontext erbt.
- Reduktionen: 7; argumentverträglich: 0; davon lokal: 0.
- Bester alter Träger: `CH+OR+CH+Y` · HERBAL; entfernt `OR+Y`.

### Rang 10 · G506-T10 · `CH+SH` · PHARMA

**Nimm das zuvor Genannte und halte es.**

- Tier: `C_ACTION_HANDGRIP_ONLY__ARGUMENT_MODE_OPEN` — Die Handlungskette ist alt; alte Träger nennen jedoch Argumente explizit, während das Ziel sie aus dem Kontext erbt.
- Reduktionen: 3; argumentverträglich: 0; davon lokal: 0.
- Bester alter Träger: `OT+CH+O+SH+OR` · HERBAL; entfernt `OT+O+OR`.

### Rang 11 · G506-T11 · `CH+SH` · SOURCE_SECTION_T

**Entnimm das zuvor Genannte und halte es fest.**

- Tier: `C_ACTION_HANDGRIP_ONLY__ARGUMENT_MODE_OPEN` — Die Handlungskette ist alt; alte Träger nennen jedoch Argumente explizit, während das Ziel sie aus dem Kontext erbt.
- Reduktionen: 3; argumentverträglich: 0; davon lokal: 0.
- Bester alter Träger: `OT+CH+O+SH+OR` · HERBAL; entfernt `OT+O+OR`.

## Arbeitsentscheidung

Drei Zielkarten haben eine lokale argumentverträgliche Reduktion, vier
eine solche Reduktion nur in einem anderen Register. Vier Karten
(`CH+CH` und `CH+SH` in Source/Pharma) behalten ihren Handgriff, aber
kein alter Träger zeigt dort den Wechsel von explizitem zum geerbten
Argument. Diese Annahmen bleiben stehen, werden jedoch separat markiert.

`FRAME_COMPATIBILITY_RANK_ONLY__OPEN_CONTEXTUAL_TARGETS_RETAINED_NOT_REJECTED`
