# GDT492 — die vier Owner-Varianten sind vollständig slotweise lesbar

GDT492 zerlegt nur die vier GDT491-Karten, deren beobachtete T- und R-Sätze verschiedene Besitzerwörter tragen. Kein Satz wird umformuliert. Stattdessen werden die alten Registerrealisierungen jedes formalen Slots danebengestellt und die vollständigen Rahmenfamilien nach weiteren alten Handlungsköpfen durchsucht.

- Offene Owner-Karten zerlegt: **4/4**.
- Formale Slotvorkommen: **12**; undefinierte Slots: **0**.
- Relevante Werte: **7** über **35/35** beobachtete Registerzellen.
- Exakte Rahmenfamilie: **23** alte Träger, **17** Aktionszellen und **19** Satzformen.
- Davon zusätzliche Nicht-T/R-Zellen: **9**; gleiche Handlung über mehrere Register: **2**.

## Vier zerlegte Karten

### `@ACTION+AL+Y`

- beobachtetes T: Stelle den Positionsposten ein; zur Zielposition.
- beobachtetes R: Markiere den Stationsposten; zur Zielstation.
- Rahmenfamilie: 10 Events, 4 Handlungsköpfe, 6 Satzformen, Register `BIOLOGICAL|CELESTIAL|PHARMA`.

| Slot | portabler Wert | T-Registerform | R-Registerform | Relation |
|---:|---|---|---|---|
| 1 | `EINSTELLEN ↔ MARKIEREN` | WERT EINSTELLEN | STATION MARKIEREN | ACTION_CONTRAST_WITH_OWNER_LOCAL_REALIZATIONS |
| 2 | `ZIELORT` | ZIELPOSITION | ZIELSTATION | OWNER_LOCAL_REALIZATION_OF_SAME_PORTABLE_VALUE |
| 3 | `POSTEN` | POSITIONSPOSTEN | STATIONSPOSTEN | OWNER_LOCAL_REALIZATION_OF_SAME_PORTABLE_VALUE |

### `@ACTION+CH+E+Y`

- beobachtetes T: Lege den laufenden Eintrag fest und entnimm den laufenden Eintrag; auf Grad I.
- beobachtetes R: Markiere den Stationsposten und entnimm den Stationsposten; auf Grad I.
- Rahmenfamilie: 5 Events, 5 Handlungsköpfe, 5 Satzformen, Register `BIOLOGICAL|HERBAL|SOURCE_SECTION_T`.

| Slot | portabler Wert | T-Registerform | R-Registerform | Relation |
|---:|---|---|---|---|
| 1 | `EINSTELLEN ↔ MARKIEREN` | FESTLEGEN | STATION MARKIEREN | ACTION_CONTRAST_WITH_OWNER_LOCAL_REALIZATIONS |
| 2 | `NEHMEN` | ENTNEHMEN | POSTEN ENTNEHMEN | OWNER_LOCAL_REALIZATION_OF_SAME_PORTABLE_VALUE |
| 3 | `GRAD I` | GRAD I | GRAD I | REGISTER_STABLE_REALIZATION |
| 4 | `POSTEN` | LAUFENDER EINTRAG | STATIONSPOSTEN | OWNER_LOCAL_REALIZATION_OF_SAME_PORTABLE_VALUE |

### `@ACTION+OR+Y`

- beobachtetes T: Stelle die Arbeitseinheit und den Pflanzenposten ein.
- beobachtetes R: Markiere die Stationseinheit und den Stationsposten.
- Rahmenfamilie: 4 Events, 4 Handlungsköpfe, 4 Satzformen, Register `BIOLOGICAL|HERBAL|SOURCE_SECTION_T`.

| Slot | portabler Wert | T-Registerform | R-Registerform | Relation |
|---:|---|---|---|---|
| 1 | `EINSTELLEN ↔ MARKIEREN` | ARBEITSSTUFE EINSTELLEN | STATION MARKIEREN | ACTION_CONTRAST_WITH_OWNER_LOCAL_REALIZATIONS |
| 2 | `EINHEIT` | ARBEITSEINHEIT | STATIONSEINHEIT | OWNER_LOCAL_REALIZATION_OF_SAME_PORTABLE_VALUE |
| 3 | `POSTEN` | PFLANZENPOSTEN | STATIONSPOSTEN | OWNER_LOCAL_REALIZATION_OF_SAME_PORTABLE_VALUE |

### `CH+@ACTION`

- beobachtetes T: Nimm den Arbeitswert [wie zuvor] und stelle den Arbeitswert [wie zuvor] ein.
- beobachtetes R: Entnimm den Stationswert [wie zuvor] und markiere den Stationswert [wie zuvor].
- Rahmenfamilie: 4 Events, 4 Handlungsköpfe, 4 Satzformen, Register `BIOLOGICAL|CELESTIAL|HERBAL`.

| Slot | portabler Wert | T-Registerform | R-Registerform | Relation |
|---:|---|---|---|---|
| 1 | `NEHMEN` | PFLANZENTEIL NEHMEN | POSTEN ENTNEHMEN | OWNER_LOCAL_REALIZATION_OF_SAME_PORTABLE_VALUE |
| 2 | `EINSTELLEN ↔ MARKIEREN` | ARBEITSSTUFE EINSTELLEN | STATION MARKIEREN | ACTION_CONTRAST_WITH_OWNER_LOCAL_REALIZATIONS |

## Was den Unterschied trägt

Von den acht nicht-aktionalen Slotvorkommen wechseln sieben nur ihre bereits festgelegte Registerform: Zielposition/Zielstation, Positionsposten/Stationsposten, Eintrag/Stationsposten, Arbeitseinheit/Stationseinheit sowie die registergebundenen NEHMEN-Formen. Ein Slot bleibt sogar wörtlich stabil: `E=GRAD I`. Die Aktionsslots sind der beabsichtigte T/R-Kontrast und werden nicht als Owner-Differenz gezählt.

## Alle sieben Werte sind in allen fünf Registern alt

| Wurzel | portabler Wert | fünf beobachtete Registerformen | Events über alle Register |
|---|---|---|---:|
| `T` | EINSTELLEN | SOURCE_SECTION_T=FESTLEGEN / HERBAL=ARBEITSSTUFE EINSTELLEN / BIOLOGICAL=STATIONSWERT EINSTELLEN / CELESTIAL=WERT EINSTELLEN / PHARMA=ANSATZWERT EINSTELLEN | 295 |
| `R` | MARKIEREN | SOURCE_SECTION_T=KENNZEICHNEN / HERBAL=TEIL MARKIEREN / BIOLOGICAL=STATION MARKIEREN / CELESTIAL=POSITION MARKIEREN / PHARMA=POSTEN MARKIEREN | 114 |
| `AL` | ZIELORT | SOURCE_SECTION_T=ZIELSPALTE / HERBAL=ZIELSTELLE / BIOLOGICAL=ZIELSTATION / CELESTIAL=ZIELPOSITION / PHARMA=ZIELGEFÄSS | 348 |
| `Y` | POSTEN | SOURCE_SECTION_T=LAUFENDER EINTRAG / HERBAL=PFLANZENPOSTEN / BIOLOGICAL=STATIONSPOSTEN / CELESTIAL=POSITIONSPOSTEN / PHARMA=DROGENPOSTEN | 1545 |
| `CH` | NEHMEN | SOURCE_SECTION_T=ENTNEHMEN / HERBAL=PFLANZENTEIL NEHMEN / BIOLOGICAL=POSTEN ENTNEHMEN / CELESTIAL=POSITION AUFNEHMEN / PHARMA=DROGENPOSTEN NEHMEN | 770 |
| `E` | GRAD I | SOURCE_SECTION_T=GRAD I / HERBAL=GRAD I / BIOLOGICAL=GRAD I / CELESTIAL=GRAD I / PHARMA=GRAD I | 965 |
| `OR` | EINHEIT | SOURCE_SECTION_T=EINTRAGSEINHEIT / HERBAL=ARBEITSEINHEIT / BIOLOGICAL=STATIONSEINHEIT / CELESTIAL=POSITIONSEINHEIT / PHARMA=ANSATZEINHEIT | 262 |

## Die Rahmenfamilien liefern zusätzliche Handlungen

| Rahmen | Handlung | Events | Register | beobachtete Formen | T/R? |
|---|---|---:|---|---:|---|
| `@ACTION+AL+Y` | `OK` | 5 | BIOLOGICAL|CELESTIAL | 2 | NO |
| `@ACTION+AL+Y` | `CH` | 3 | BIOLOGICAL|PHARMA | 2 | NO |
| `@ACTION+AL+Y` | `T` | 1 | CELESTIAL | 1 | YES |
| `@ACTION+AL+Y` | `R` | 1 | BIOLOGICAL | 1 | YES |
| `@ACTION+CH+E+Y` | `OK` | 1 | HERBAL | 1 | NO |
| `@ACTION+CH+E+Y` | `K` | 1 | HERBAL | 1 | NO |
| `@ACTION+CH+E+Y` | `S` | 1 | HERBAL | 1 | NO |
| `@ACTION+CH+E+Y` | `T` | 1 | SOURCE_SECTION_T | 1 | YES |
| `@ACTION+CH+E+Y` | `R` | 1 | BIOLOGICAL | 1 | YES |
| `@ACTION+OR+Y` | `SH` | 1 | SOURCE_SECTION_T | 1 | NO |
| `@ACTION+OR+Y` | `S` | 1 | SOURCE_SECTION_T | 1 | NO |
| `@ACTION+OR+Y` | `T` | 1 | HERBAL | 1 | YES |
| `@ACTION+OR+Y` | `R` | 1 | BIOLOGICAL | 1 | YES |
| `CH+@ACTION` | `K` | 1 | BIOLOGICAL | 1 | NO |
| `CH+@ACTION` | `S` | 1 | CELESTIAL | 1 | NO |
| `CH+@ACTION` | `T` | 1 | HERBAL | 1 | YES |
| `CH+@ACTION` | `R` | 1 | BIOLOGICAL | 1 | YES |

Besonders nützlich ist `@ACTION+AL+Y`: `OK` realisiert exakt denselben Rahmen celestial und biologisch, `CH` biologisch und pharmazeutisch. Diese zwei alten Brücken zeigen direkt, dass Positions-/Stations-/Drogenwortlaut am Besitzerregister hängt, während `AL+Y = ZIELORT · POSTEN` stehen bleibt.

## Zwei direkte Registerbrücken

- `OK+AL+Y`: BIOLOGICAL|CELESTIAL — Setze den Stationsposten im Stationsgang an; zur Zielstation. || Setze den Positionsposten; zur Zielposition.
- `CH+AL+Y`: BIOLOGICAL|PHARMA — Entnimm den Stationsposten; zur Zielstation. || Nimm den Drogenposten; zum Zielgefäß.

## Arbeitsfolgerung

Die vier GDT491-Abweichungen verlangen keine neue Bedeutung und kein zusammengesetztes Geheimwort. Sie verhalten sich wie dieselbe kleine Komponentenkarte mit registergebundenem Fachwortschatz. Das stärkt die Lesart *Mischung aus kurzen produktiven Fachkürzeln und gelernten owner-lokalen Ganzwörtern*: Die Kürzel bestimmen Slot und portablen Wert; der Seitenbesitzer bestimmt den konkreten deutschen Werkstattwortlaut.

## Nächster Schritt

Kompiliere aus den 35 beobachteten Registerzellen eine kleine Owner-abhängige Satzschablone für alle elf T/R-Rahmen. Jede Ausgabe muss entweder eine bereits beobachtete Klausel sein oder ausdrücklich als slotweise zusammengesetzte Arbeitslesung markiert bleiben. So bekommen auch die vier Varianten eine gemeinsame Vorhersageform, ohne sie als beobachteten Satz auszugeben.
