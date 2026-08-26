# GDT504 — semantische Deltas der 46 Vergleichskarten

Status: `FORTY_SIX_PHRASE_DELTAS_RESOLVE_WITH_FIXED_VALUES__PAIR_FRAME_EDITS_REMAIN_SEPARATE`

Jede Karte wird als geordnete Differenz aus altem Klauselträger und
aktuellem Arbeitssatz gelesen. Zielzusätze und fremde Trägerreste
bleiben getrennt; die Wörterbuchwerte werden nicht verändert.

## Drei Stützentiefen

- **DIRECT_LOCAL_DELTA:** 22 Karten. Altes Teilrezept und Ziel liegen im selben Register.
- **CROSS_REGISTER_NORMALIZED_DELTA:** 13 Karten. Das exakte Teilrezept liegt in einem anderen Register; verglichen wird über portable Werte.
- **PAIR_BACKBONE_FRAME_EDIT:** 11 Karten. Nur das alte Handlungspaar wird übertragen; fremde Trägerkomponenten bleiben als Entfernung sichtbar.

## Die 46 Deltakarten

### G504-D01 · `SH+CH+E+Y` · CELESTIAL

- Alter Satz: Halte den Positionsposten; auf Grad I.
- Aktueller Satz: **Halte den Positionsposten und nimm den Positionsposten auf; auf Grad I.**
- Gemeinsam: `SH+E+Y`; hinzu: `CH`; nicht übertragen: `NONE`.
- Operation: `ADD_SERIAL_ACTION` — Der Zielsatz ergänzt genau eine weitere Handlung in sichtbarer Reihenfolge.
- Stützentiefe: `DIRECT_LOCAL_DELTA`; Effektprüfungen: 1/1.

### G504-D02 · `SH+CH+E+Y` · PHARMA

- Alter Satz: Halte den Drogenposten; auf Grad I.
- Aktueller Satz: **Halte den Drogenposten und nimm den Drogenposten; auf Grad I.**
- Gemeinsam: `SH+E+Y`; hinzu: `CH`; nicht übertragen: `NONE`.
- Operation: `ADD_SERIAL_ACTION` — Der Zielsatz ergänzt genau eine weitere Handlung in sichtbarer Reihenfolge.
- Stützentiefe: `DIRECT_LOCAL_DELTA`; Effektprüfungen: 1/1.

### G504-D03 · `CH+CH+E+Y` · PHARMA

- Alter Satz: Nimm den Drogenposten; auf Grad I.
- Aktueller Satz: **Nimm den Drogenposten zweimal; auf Grad I.**
- Gemeinsam: `CH+E+Y`; hinzu: `CH`; nicht übertragen: `NONE`.
- Operation: `COUNTED_REPEAT` — Der zweite gleiche Handlungskopf wird flüssig als zweimal realisiert.
- Stützentiefe: `DIRECT_LOCAL_DELTA`; Effektprüfungen: 1/1.

### G504-D04 · `OK+OR+Y` · PHARMA

- Alter Satz: Setze den Drogenposten als Ansatz an.
- Aktueller Satz: **Setze die Ansatzeinheit und den Drogenposten als Ansatz an.**
- Gemeinsam: `OK+Y`; hinzu: `OR`; nicht übertragen: `NONE`.
- Operation: `ADD_UNIT_ARGUMENT` — Der Zielsatz ergänzt die owner-lokale Einheit als zweites Argument.
- Stützentiefe: `DIRECT_LOCAL_DELTA`; Effektprüfungen: 1/1.

### G504-D05 · `CH+OR+Y` · PHARMA

- Alter Satz: Nimm die Ansatzeinheit.
- Aktueller Satz: **Nimm die Ansatzeinheit und den Drogenposten.**
- Gemeinsam: `CH+OR`; hinzu: `Y`; nicht übertragen: `NONE`.
- Operation: `ADD_SECOND_POST_ARGUMENT` — Der Zielsatz ergänzt den owner-lokalen Posten neben der Einheit.
- Stützentiefe: `DIRECT_LOCAL_DELTA`; Effektprüfungen: 1/1.

### G504-D06 · `CHD+AL+Y` · HERBAL

- Alter Satz: Bearbeite den Pflanzenposten.
- Aktueller Satz: **Bearbeite den Pflanzenposten; zur Zielstelle.**
- Gemeinsam: `CHD+Y`; hinzu: `AL`; nicht übertragen: `NONE`.
- Operation: `ADD_DESTINATION` — Der Zielsatz ergänzt genau die owner-lokale Zielangabe.
- Stützentiefe: `DIRECT_LOCAL_DELTA`; Effektprüfungen: 1/1.

### G504-D07 · `K+AL+Y` · HERBAL

- Alter Satz: Gib den Pflanzenposten zu.
- Aktueller Satz: **Gib den Pflanzenposten zu; zur Zielstelle.**
- Gemeinsam: `K+Y`; hinzu: `AL`; nicht übertragen: `NONE`.
- Operation: `ADD_DESTINATION` — Der Zielsatz ergänzt genau die owner-lokale Zielangabe.
- Stützentiefe: `DIRECT_LOCAL_DELTA`; Effektprüfungen: 1/1.

### G504-D08 · `OK+OR+Y` · CELESTIAL

- Alter Satz: Setze die Positionseinheit.
- Aktueller Satz: **Setze die Positionseinheit und den Positionsposten.**
- Gemeinsam: `OK+OR`; hinzu: `Y`; nicht übertragen: `NONE`.
- Operation: `ADD_SECOND_POST_ARGUMENT` — Der Zielsatz ergänzt den owner-lokalen Posten neben der Einheit.
- Stützentiefe: `DIRECT_LOCAL_DELTA`; Effektprüfungen: 1/1.

### G504-D09 · `K+OR+Y` · PHARMA

- Alter Satz: Gib die Ansatzeinheit zu.
- Aktueller Satz: **Gib die Ansatzeinheit und den Drogenposten zu.**
- Gemeinsam: `K+OR`; hinzu: `Y`; nicht übertragen: `NONE`.
- Operation: `ADD_SECOND_POST_ARGUMENT` — Der Zielsatz ergänzt den owner-lokalen Posten neben der Einheit.
- Stützentiefe: `DIRECT_LOCAL_DELTA`; Effektprüfungen: 1/1.

### G504-D10 · `CHD+OR+Y` · CELESTIAL

- Alter Satz: Bearbeite den Positionsposten.
- Aktueller Satz: **Bearbeite die Positionseinheit und den Positionsposten.**
- Gemeinsam: `CHD+Y`; hinzu: `OR`; nicht übertragen: `NONE`.
- Operation: `ADD_UNIT_ARGUMENT` — Der Zielsatz ergänzt die owner-lokale Einheit als zweites Argument.
- Stützentiefe: `DIRECT_LOCAL_DELTA`; Effektprüfungen: 1/1.

### G504-D11 · `CHD+CHD+Y` · CELESTIAL

- Alter Satz: Bearbeite den Positionsposten.
- Aktueller Satz: **Bearbeite den Positionsposten zweimal.**
- Gemeinsam: `CHD+Y`; hinzu: `CHD`; nicht übertragen: `NONE`.
- Operation: `COUNTED_REPEAT` — Der zweite gleiche Handlungskopf wird flüssig als zweimal realisiert.
- Stützentiefe: `DIRECT_LOCAL_DELTA`; Effektprüfungen: 1/1.

### G504-D12 · `CHD+OR+Y` · PHARMA

- Alter Satz: Bearbeite den Drogenposten.
- Aktueller Satz: **Bearbeite die Ansatzeinheit und den Drogenposten.**
- Gemeinsam: `CHD+Y`; hinzu: `OR`; nicht übertragen: `NONE`.
- Operation: `ADD_UNIT_ARGUMENT` — Der Zielsatz ergänzt die owner-lokale Einheit als zweites Argument.
- Stützentiefe: `DIRECT_LOCAL_DELTA`; Effektprüfungen: 1/1.

### G504-D13 · `CHD+AL+Y` · SOURCE_SECTION_T

- Alter Satz: Bearbeite den laufenden Eintrag.
- Aktueller Satz: **Bearbeite den laufenden Eintrag; zur Zielspalte.**
- Gemeinsam: `CHD+Y`; hinzu: `AL`; nicht übertragen: `NONE`.
- Operation: `ADD_DESTINATION` — Der Zielsatz ergänzt genau die owner-lokale Zielangabe.
- Stützentiefe: `DIRECT_LOCAL_DELTA`; Effektprüfungen: 1/1.

### G504-D14 · `CHD+CHD+Y` · PHARMA

- Alter Satz: Bearbeite den Drogenposten.
- Aktueller Satz: **Bearbeite den Drogenposten zweimal.**
- Gemeinsam: `CHD+Y`; hinzu: `CHD`; nicht übertragen: `NONE`.
- Operation: `COUNTED_REPEAT` — Der zweite gleiche Handlungskopf wird flüssig als zweimal realisiert.
- Stützentiefe: `DIRECT_LOCAL_DELTA`; Effektprüfungen: 1/1.

### G504-D15 · `CHD+CHD+Y` · SOURCE_SECTION_T

- Alter Satz: Bearbeite den laufenden Eintrag.
- Aktueller Satz: **Bearbeite den laufenden Eintrag zweimal.**
- Gemeinsam: `CHD+Y`; hinzu: `CHD`; nicht übertragen: `NONE`.
- Operation: `COUNTED_REPEAT` — Der zweite gleiche Handlungskopf wird flüssig als zweimal realisiert.
- Stützentiefe: `DIRECT_LOCAL_DELTA`; Effektprüfungen: 1/1.

### G504-D16 · `K+AL+Y` · SOURCE_SECTION_T

- Alter Satz: Ordne den laufenden Eintrag zu.
- Aktueller Satz: **Ordne den laufenden Eintrag zu; zur Zielspalte.**
- Gemeinsam: `K+Y`; hinzu: `AL`; nicht übertragen: `NONE`.
- Operation: `ADD_DESTINATION` — Der Zielsatz ergänzt genau die owner-lokale Zielangabe.
- Stützentiefe: `DIRECT_LOCAL_DELTA`; Effektprüfungen: 1/1.

### G504-D17 · `CHD+CH+E+Y` · CELESTIAL

- Alter Satz: Bearbeite den Positionsposten.
- Aktueller Satz: **Bearbeite den Positionsposten und nimm den Positionsposten auf; auf Grad I.**
- Gemeinsam: `CHD+Y`; hinzu: `CH+E`; nicht übertragen: `NONE`.
- Operation: `ADD_SERIAL_ACTION_AND_GRADE` — Der Zielsatz ergänzt eine weitere Handlung samt Grad I.
- Stützentiefe: `DIRECT_LOCAL_DELTA`; Effektprüfungen: 2/2.

### G504-D18 · `CHD+CH+E+Y` · PHARMA

- Alter Satz: Bearbeite den Drogenposten.
- Aktueller Satz: **Bearbeite den Drogenposten und nimm den Drogenposten; auf Grad I.**
- Gemeinsam: `CHD+Y`; hinzu: `CH+E`; nicht übertragen: `NONE`.
- Operation: `ADD_SERIAL_ACTION_AND_GRADE` — Der Zielsatz ergänzt eine weitere Handlung samt Grad I.
- Stützentiefe: `DIRECT_LOCAL_DELTA`; Effektprüfungen: 2/2.

### G504-D19 · `CH+CH+E+Y` · CELESTIAL

- Alter Satz: Nimm den Positionsposten [wie zuvor] auf; auf Grad I.
- Aktueller Satz: **Nimm den Positionsposten zweimal auf; auf Grad I.**
- Gemeinsam: `CH+E`; hinzu: `CH+Y`; nicht übertragen: `NONE`.
- Operation: `COUNTED_REPEAT_AND_EXPLICITIZE_POST` — Zweimal realisiert die Wiederholung; der zuvor geerbte Posten wird explizit.
- Stützentiefe: `DIRECT_LOCAL_DELTA`; Effektprüfungen: 2/2.

### G504-D20 · `SH+CHD+Y` · CELESTIAL

- Alter Satz: Halte den Stationsposten.
- Aktueller Satz: **Halte den Positionsposten und bearbeite den Positionsposten.**
- Gemeinsam: `SH+Y`; hinzu: `CHD`; nicht übertragen: `NONE`.
- Operation: `ADD_SERIAL_ACTION` — Der Zielsatz ergänzt genau eine weitere Handlung in sichtbarer Reihenfolge.
- Stützentiefe: `CROSS_REGISTER_NORMALIZED_DELTA`; Effektprüfungen: 1/1.

### G504-D21 · `P+CH+E+Y` · PHARMA

- Alter Satz: Weiter setze die Ansatzeinheit [wie zuvor] ein und nimm die Ansatzeinheit [wie zuvor]; als Ausführung und auf Grad I.
- Aktueller Satz: **Setze den Drogenposten ein und nimm den Drogenposten; auf Grad I.**
- Gemeinsam: `P+CH+E`; hinzu: `Y`; nicht übertragen: `O+OL`.
- Operation: `PAIR_REPLACE_CARRIER_CONTEXT_WITH_POST` — Das alte Handlungspaar bleibt; Ausführung/Fortsetzung weichen dem expliziten Posten.
- Stützentiefe: `PAIR_BACKBONE_FRAME_EDIT`; Effektprüfungen: 3/3.

### G504-D22 · `S+CHD+Y` · CELESTIAL

- Alter Satz: Weiter wähle den Stationsposten und bearbeite den Stationsposten.
- Aktueller Satz: **Wähle den Positionsposten und bearbeite den Positionsposten.**
- Gemeinsam: `S+CHD+Y`; hinzu: `NONE`; nicht übertragen: `OL`.
- Operation: `PAIR_DROP_CONTINUATION` — Das alte Handlungspaar bleibt; nur die fremde Fortsetzungsangabe fällt weg.
- Stützentiefe: `PAIR_BACKBONE_FRAME_EDIT`; Effektprüfungen: 1/1.

### G504-D23 · `CH+CHD+Y` · CELESTIAL

- Alter Satz: Bearbeite den Positionsposten.
- Aktueller Satz: **Nimm den Positionsposten auf und bearbeite den Positionsposten.**
- Gemeinsam: `CHD+Y`; hinzu: `CH`; nicht übertragen: `NONE`.
- Operation: `ADD_SERIAL_ACTION` — Der Zielsatz ergänzt genau eine weitere Handlung in sichtbarer Reihenfolge.
- Stützentiefe: `DIRECT_LOCAL_DELTA`; Effektprüfungen: 1/1.

### G504-D24 · `P+OR+Y` · PHARMA

- Alter Satz: Setze den Stationsposten ein.
- Aktueller Satz: **Setze die Ansatzeinheit und den Drogenposten ein.**
- Gemeinsam: `P+Y`; hinzu: `OR`; nicht übertragen: `NONE`.
- Operation: `ADD_UNIT_ARGUMENT` — Der Zielsatz ergänzt die owner-lokale Einheit als zweites Argument.
- Stützentiefe: `CROSS_REGISTER_NORMALIZED_DELTA`; Effektprüfungen: 1/1.

### G504-D25 · `SH+CHD+Y` · PHARMA

- Alter Satz: Halte den Stationsposten.
- Aktueller Satz: **Halte den Drogenposten und bearbeite den Drogenposten.**
- Gemeinsam: `SH+Y`; hinzu: `CHD`; nicht übertragen: `NONE`.
- Operation: `ADD_SERIAL_ACTION` — Der Zielsatz ergänzt genau eine weitere Handlung in sichtbarer Reihenfolge.
- Stützentiefe: `CROSS_REGISTER_NORMALIZED_DELTA`; Effektprüfungen: 1/1.

### G504-D26 · `SH+CHD+Y` · SOURCE_SECTION_T

- Alter Satz: Halte den Stationsposten.
- Aktueller Satz: **Halte den laufenden Eintrag fest und bearbeite den laufenden Eintrag.**
- Gemeinsam: `SH+Y`; hinzu: `CHD`; nicht übertragen: `NONE`.
- Operation: `ADD_SERIAL_ACTION` — Der Zielsatz ergänzt genau eine weitere Handlung in sichtbarer Reihenfolge.
- Stützentiefe: `CROSS_REGISTER_NORMALIZED_DELTA`; Effektprüfungen: 1/1.

### G504-D27 · `P+CH+E+Y` · CELESTIAL

- Alter Satz: Setze den Positionsposten ein und nimm den Positionsposten auf; von der Ausgangsposition; als Ausführung.
- Aktueller Satz: **Setze den Positionsposten ein und nimm den Positionsposten auf; auf Grad I.**
- Gemeinsam: `P+CH+Y`; hinzu: `E`; nicht übertragen: `O+AR`.
- Operation: `PAIR_REPLACE_CARRIER_CONTEXT_WITH_GRADE` — Das alte Handlungspaar bleibt; Ausführung/Ausgang weichen Grad I.
- Stützentiefe: `PAIR_BACKBONE_FRAME_EDIT`; Effektprüfungen: 3/3.

### G504-D28 · `S+CHD+Y` · PHARMA

- Alter Satz: Weiter wähle den Stationsposten und bearbeite den Stationsposten.
- Aktueller Satz: **Wähle den Drogenposten und bearbeite den Drogenposten.**
- Gemeinsam: `S+CHD+Y`; hinzu: `NONE`; nicht übertragen: `OL`.
- Operation: `PAIR_DROP_CONTINUATION` — Das alte Handlungspaar bleibt; nur die fremde Fortsetzungsangabe fällt weg.
- Stützentiefe: `PAIR_BACKBONE_FRAME_EDIT`; Effektprüfungen: 1/1.

### G504-D29 · `S+CHD+Y` · SOURCE_SECTION_T

- Alter Satz: Weiter wähle den Stationsposten und bearbeite den Stationsposten.
- Aktueller Satz: **Wähle den laufenden Eintrag und bearbeite den laufenden Eintrag.**
- Gemeinsam: `S+CHD+Y`; hinzu: `NONE`; nicht übertragen: `OL`.
- Operation: `PAIR_DROP_CONTINUATION` — Das alte Handlungspaar bleibt; nur die fremde Fortsetzungsangabe fällt weg.
- Stützentiefe: `PAIR_BACKBONE_FRAME_EDIT`; Effektprüfungen: 1/1.

### G504-D30 · `CH+CHD+Y` · PHARMA

- Alter Satz: Bearbeite den Drogenposten.
- Aktueller Satz: **Nimm den Drogenposten und bearbeite den Drogenposten.**
- Gemeinsam: `CHD+Y`; hinzu: `CH`; nicht übertragen: `NONE`.
- Operation: `ADD_SERIAL_ACTION` — Der Zielsatz ergänzt genau eine weitere Handlung in sichtbarer Reihenfolge.
- Stützentiefe: `DIRECT_LOCAL_DELTA`; Effektprüfungen: 1/1.

### G504-D31 · `CH+CHD+Y` · SOURCE_SECTION_T

- Alter Satz: Bearbeite den laufenden Eintrag.
- Aktueller Satz: **Entnimm den laufenden Eintrag und bearbeite den laufenden Eintrag.**
- Gemeinsam: `CHD+Y`; hinzu: `CH`; nicht übertragen: `NONE`.
- Operation: `ADD_SERIAL_ACTION` — Der Zielsatz ergänzt genau eine weitere Handlung in sichtbarer Reihenfolge.
- Stützentiefe: `DIRECT_LOCAL_DELTA`; Effektprüfungen: 1/1.

### G504-D32 · `CH+OR+Y` · CELESTIAL

- Alter Satz: Nimm die Arbeitseinheit.
- Aktueller Satz: **Nimm die Positionseinheit und den Positionsposten auf.**
- Gemeinsam: `CH+OR`; hinzu: `Y`; nicht übertragen: `NONE`.
- Operation: `ADD_SECOND_POST_ARGUMENT` — Der Zielsatz ergänzt den owner-lokalen Posten neben der Einheit.
- Stützentiefe: `CROSS_REGISTER_NORMALIZED_DELTA`; Effektprüfungen: 1/1.

### G504-D33 · `K+OR+Y` · CELESTIAL

- Alter Satz: Gib den Pflanzenposten zu.
- Aktueller Satz: **Ordne die Positionseinheit und den Positionsposten zu.**
- Gemeinsam: `K+Y`; hinzu: `OR`; nicht übertragen: `NONE`.
- Operation: `ADD_UNIT_ARGUMENT` — Der Zielsatz ergänzt die owner-lokale Einheit als zweites Argument.
- Stützentiefe: `CROSS_REGISTER_NORMALIZED_DELTA`; Effektprüfungen: 1/1.

### G504-D34 · `S+AL+Y` · HERBAL

- Alter Satz: Wähle den Stationsposten [wie zuvor]; zur Zielstation.
- Aktueller Satz: **Wähle den Pflanzenposten; zur Zielstelle.**
- Gemeinsam: `S+AL`; hinzu: `Y`; nicht übertragen: `NONE`.
- Operation: `EXPLICITIZE_INHERITED_POST` — Der schon sprachlich geerbte Posten wird im Rezept ausdrücklich gesetzt.
- Stützentiefe: `CROSS_REGISTER_NORMALIZED_DELTA`; Effektprüfungen: 1/1.

### G504-D35 · `S+AL+Y` · SOURCE_SECTION_T

- Alter Satz: Wähle den Stationsposten [wie zuvor]; zur Zielstation.
- Aktueller Satz: **Wähle den laufenden Eintrag; zur Zielspalte.**
- Gemeinsam: `S+AL`; hinzu: `Y`; nicht übertragen: `NONE`.
- Operation: `EXPLICITIZE_INHERITED_POST` — Der schon sprachlich geerbte Posten wird im Rezept ausdrücklich gesetzt.
- Stützentiefe: `CROSS_REGISTER_NORMALIZED_DELTA`; Effektprüfungen: 1/1.

### G504-D36 · `SH+AL+Y` · HERBAL

- Alter Satz: Halte den Stationsposten [wie zuvor]; zur Zielstation.
- Aktueller Satz: **Halte den Pflanzenposten; zur Zielstelle.**
- Gemeinsam: `SH+AL`; hinzu: `Y`; nicht übertragen: `NONE`.
- Operation: `EXPLICITIZE_INHERITED_POST` — Der schon sprachlich geerbte Posten wird im Rezept ausdrücklich gesetzt.
- Stützentiefe: `CROSS_REGISTER_NORMALIZED_DELTA`; Effektprüfungen: 1/1.

### G504-D37 · `SH+AL+Y` · SOURCE_SECTION_T

- Alter Satz: Halte den Stationsposten [wie zuvor]; zur Zielstation.
- Aktueller Satz: **Halte den laufenden Eintrag fest; zur Zielspalte.**
- Gemeinsam: `SH+AL`; hinzu: `Y`; nicht übertragen: `NONE`.
- Operation: `EXPLICITIZE_INHERITED_POST` — Der schon sprachlich geerbte Posten wird im Rezept ausdrücklich gesetzt.
- Stützentiefe: `CROSS_REGISTER_NORMALIZED_DELTA`; Effektprüfungen: 1/1.

### G504-D38 · `P+AL+Y` · HERBAL

- Alter Satz: Setze den Stationsposten ein.
- Aktueller Satz: **Setze den Pflanzenposten ein; zur Zielstelle.**
- Gemeinsam: `P+Y`; hinzu: `AL`; nicht übertragen: `NONE`.
- Operation: `ADD_DESTINATION` — Der Zielsatz ergänzt genau die owner-lokale Zielangabe.
- Stützentiefe: `CROSS_REGISTER_NORMALIZED_DELTA`; Effektprüfungen: 1/1.

### G504-D39 · `P+AL+Y` · SOURCE_SECTION_T

- Alter Satz: Setze den Stationsposten ein.
- Aktueller Satz: **Setze den laufenden Eintrag ein; zur Zielspalte.**
- Gemeinsam: `P+Y`; hinzu: `AL`; nicht übertragen: `NONE`.
- Operation: `ADD_DESTINATION` — Der Zielsatz ergänzt genau die owner-lokale Zielangabe.
- Stützentiefe: `CROSS_REGISTER_NORMALIZED_DELTA`; Effektprüfungen: 1/1.

### G504-D40 · `P+OR+Y` · CELESTIAL

- Alter Satz: Setze den Stationsposten ein.
- Aktueller Satz: **Setze die Positionseinheit und den Positionsposten ein.**
- Gemeinsam: `P+Y`; hinzu: `OR`; nicht übertragen: `NONE`.
- Operation: `ADD_UNIT_ARGUMENT` — Der Zielsatz ergänzt die owner-lokale Einheit als zweites Argument.
- Stützentiefe: `CROSS_REGISTER_NORMALIZED_DELTA`; Effektprüfungen: 1/1.

### G504-D41 · `CH+P` · PHARMA

- Alter Satz: Weiter nimm den Drogenposten [wie zuvor] und setze den Drogenposten [wie zuvor] ein.
- Aktueller Satz: **Nimm das zuvor Genannte und setze es ein.**
- Gemeinsam: `CH+P`; hinzu: `NONE`; nicht übertragen: `OL`.
- Operation: `PAIR_DROP_CONTINUATION` — Das alte Handlungspaar bleibt; nur die fremde Fortsetzungsangabe fällt weg.
- Stützentiefe: `PAIR_BACKBONE_FRAME_EDIT`; Effektprüfungen: 1/1.

### G504-D42 · `CH+P` · SOURCE_SECTION_T

- Alter Satz: Entnimm den Kennwert [wie zuvor] und setze den Kennwert [wie zuvor] ein; von der Ausgangszeile.
- Aktueller Satz: **Entnimm das zuvor Genannte und setze es ein.**
- Gemeinsam: `CH+P`; hinzu: `NONE`; nicht übertragen: `AR`.
- Operation: `PAIR_DROP_ORIGIN` — Das alte Handlungspaar bleibt; nur die fremde Ausgangsangabe fällt weg.
- Stützentiefe: `PAIR_BACKBONE_FRAME_EDIT`; Effektprüfungen: 1/1.

### G504-D43 · `CH+CH` · PHARMA

- Alter Satz: Nimm die Arbeitseinheit und den Pflanzenposten und nimm die Arbeitseinheit und den Pflanzenposten.
- Aktueller Satz: **Nimm das zuvor Genannte zweimal.**
- Gemeinsam: `CH+CH`; hinzu: `NONE`; nicht übertragen: `OR+Y`.
- Operation: `PAIR_CONTEXTUALIZE_REPEAT_ARGUMENTS` — Das wiederholte Handlungspaar bleibt; fremde Einheit und Posten werden zum Vorbezug.
- Stützentiefe: `PAIR_BACKBONE_FRAME_EDIT`; Effektprüfungen: 2/2.

### G504-D44 · `CH+CH` · SOURCE_SECTION_T

- Alter Satz: Nimm die Arbeitseinheit und den Pflanzenposten und nimm die Arbeitseinheit und den Pflanzenposten.
- Aktueller Satz: **Entnimm das zuvor Genannte zweimal.**
- Gemeinsam: `CH+CH`; hinzu: `NONE`; nicht übertragen: `OR+Y`.
- Operation: `PAIR_CONTEXTUALIZE_REPEAT_ARGUMENTS` — Das wiederholte Handlungspaar bleibt; fremde Einheit und Posten werden zum Vorbezug.
- Stützentiefe: `PAIR_BACKBONE_FRAME_EDIT`; Effektprüfungen: 2/2.

### G504-D45 · `CH+SH` · PHARMA

- Alter Satz: Weiter nimm den Pflanzenposten und halte den Pflanzenposten; an der bezeichneten Stelle.
- Aktueller Satz: **Nimm das zuvor Genannte und halte es.**
- Gemeinsam: `CH+SH`; hinzu: `NONE`; nicht übertragen: `OL+D_ADDR+Y`.
- Operation: `PAIR_CONTEXTUALIZE_AND_DROP_ADDRESS` — Das Handlungspaar bleibt; Fortsetzung, Adresse und fremder Posten werden nicht übertragen.
- Stützentiefe: `PAIR_BACKBONE_FRAME_EDIT`; Effektprüfungen: 3/3.

### G504-D46 · `CH+SH` · SOURCE_SECTION_T

- Alter Satz: Weiter nimm den Pflanzenposten und halte den Pflanzenposten; an der bezeichneten Stelle.
- Aktueller Satz: **Entnimm das zuvor Genannte und halte es fest.**
- Gemeinsam: `CH+SH`; hinzu: `NONE`; nicht übertragen: `OL+D_ADDR+Y`.
- Operation: `PAIR_CONTEXTUALIZE_AND_DROP_ADDRESS` — Das Handlungspaar bleibt; Fortsetzung, Adresse und fremder Posten werden nicht übertragen.
- Stützentiefe: `PAIR_BACKBONE_FRAME_EDIT`; Effektprüfungen: 3/3.

## Arbeitslesart

Die 35 Teilrezeptkarten sind echte Erweiterungen: 22 lokal und dreizehn
registerübergreifend normalisiert. Die elf Paarkarten bleiben eine
eigene schwächere Schublade, weil nur das Handlungspaar alt ist und
Trägerkontext entfernt oder ersetzt wird. Alle 59 sichtbaren
Token-Effekte passen zur aktuellen deutschen Phrase; das ist eine
Konsistenzprüfung der Arbeitssprache, keine neue Manuskriptbeobachtung.

`EDITORIAL_SEMANTIC_DELTA_ONLY__NO_TARGET_OBSERVATION_OR_SURFACE_PREDICTION`
