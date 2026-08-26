# GDT493 — 110 owner-abhängige T/R-Arbeitslesungen

GDT493 legt jeden der elf T/R-Rahmen in jedem der fünf Register aus. Die Herkunft steht auf jeder Karte: `OBSERVED_CLAUSE` ist eine wortwörtliche alte GDT416-Klausel; `COMPOSED_WORKING` ist eine neue, ausdrücklich so markierte Arbeitslesung aus dem unveränderten GDT416-Renderer und ausschließlich alten Registerwerten.

- Vollständiges Raster: **110/110**.
- Wortwörtlich beobachtete Zellen: **37** mit **76** Trägern und **44** Formen.
- Slotweise zusammengesetzte Arbeitszellen: **73**; unmarkiert ausgegebene Kompositionen: **0**.
- T/R-Kontrastkarten: **55/55**, alle mit verschiedenen Ausgaben und identischem formalen Rest.
- Alte Wert×Register-Zellen: **55/55**; neue Slotwerte: **0**.

## Deck-Legende

- `OBSERVED_CLAUSE`: Der vollständige Rezept×Register-Satz hat mindestens einen alten Eventträger. Angezeigt wird der häufigste alte Satz, bei Gleichstand der kürzere, dann der alphabetisch erste.
- `COMPOSED_WORKING`: Das genaue Rezept ist in diesem Register noch nicht als vollständiger Satz belegt. Der angezeigte Satz wird vom alten GDT416-Renderer aus alten Slotwerten gebaut.
- Bei Rahmen ohne sichtbares Argument (`@ACTION`, `@ACTION+AL`, `@ACTION+OL`, `CH+@ACTION`) verwendet nur die Arbeitskomposition `Y=POSTEN` als klar ausgewiesenen Default des aktiven Arguments; ein realer Satz darf stattdessen WERT, ANTEIL oder EINHEIT erben.

## Alle 110 Karten

### `@ACTION` — 6 beobachtet / 4 zusammengesetzt

| Aktion | Register | Status | Ausgabe | Komponentenlesung |
|---|---|---|---|---|
| `T` | SOURCE_SECTION_T | **COMPOSED_WORKING** | Lege den laufenden Eintrag [wie zuvor] fest. | `EINSTELLEN` |
| `T` | HERBAL | **OBSERVED_CLAUSE** | Stelle den Pflanzenposten [wie zuvor] ein. | `EINSTELLEN` |
| `T` | BIOLOGICAL | **COMPOSED_WORKING** | Stelle den Stationsposten [wie zuvor] ein. | `EINSTELLEN` |
| `T` | CELESTIAL | **COMPOSED_WORKING** | Stelle den Positionsposten [wie zuvor] ein. | `EINSTELLEN` |
| `T` | PHARMA | **COMPOSED_WORKING** | Stelle den Drogenposten [wie zuvor] ein. | `EINSTELLEN` |
| `R` | SOURCE_SECTION_T | **OBSERVED_CLAUSE** | Kennzeichne den laufenden Eintrag [wie zuvor]. | `MARKIEREN` |
| `R` | HERBAL | **OBSERVED_CLAUSE** | Markiere den Pflanzenposten [wie zuvor]. | `MARKIEREN` |
| `R` | BIOLOGICAL | **OBSERVED_CLAUSE** | Markiere den Stationsposten [wie zuvor]. | `MARKIEREN` |
| `R` | CELESTIAL | **OBSERVED_CLAUSE** | Markiere den Positionsposten [wie zuvor]. | `MARKIEREN` |
| `R` | PHARMA | **OBSERVED_CLAUSE** | Markiere den Drogenposten [wie zuvor]. | `MARKIEREN` |

### `@ACTION+AIIN` — 5 beobachtet / 5 zusammengesetzt

| Aktion | Register | Status | Ausgabe | Komponentenlesung |
|---|---|---|---|---|
| `T` | SOURCE_SECTION_T | **COMPOSED_WORKING** | Lege den Kennwert fest. | `EINSTELLEN · WERT` |
| `T` | HERBAL | **OBSERVED_CLAUSE** | Stelle den Arbeitswert ein. | `EINSTELLEN · WERT` |
| `T` | BIOLOGICAL | **OBSERVED_CLAUSE** | Stelle den Stationswert ein. | `EINSTELLEN · WERT` |
| `T` | CELESTIAL | **COMPOSED_WORKING** | Stelle den Positionswert ein. | `EINSTELLEN · WERT` |
| `T` | PHARMA | **OBSERVED_CLAUSE** | Stelle den Mengenwert ein. | `EINSTELLEN · WERT` |
| `R` | SOURCE_SECTION_T | **COMPOSED_WORKING** | Kennzeichne den Kennwert. | `MARKIEREN · WERT` |
| `R` | HERBAL | **OBSERVED_CLAUSE** | Markiere den Arbeitswert. | `MARKIEREN · WERT` |
| `R` | BIOLOGICAL | **OBSERVED_CLAUSE** | Markiere den Stationswert. | `MARKIEREN · WERT` |
| `R` | CELESTIAL | **COMPOSED_WORKING** | Markiere den Positionswert. | `MARKIEREN · WERT` |
| `R` | PHARMA | **COMPOSED_WORKING** | Markiere den Mengenwert. | `MARKIEREN · WERT` |

### `@ACTION+AIN` — 3 beobachtet / 7 zusammengesetzt

| Aktion | Register | Status | Ausgabe | Komponentenlesung |
|---|---|---|---|---|
| `T` | SOURCE_SECTION_T | **COMPOSED_WORKING** | Lege den Teilwert fest. | `EINSTELLEN · ANTEIL` |
| `T` | HERBAL | **COMPOSED_WORKING** | Stelle den Materialanteil ein. | `EINSTELLEN · ANTEIL` |
| `T` | BIOLOGICAL | **OBSERVED_CLAUSE** | Stelle den Stationsanteil ein. | `EINSTELLEN · ANTEIL` |
| `T` | CELESTIAL | **COMPOSED_WORKING** | Stelle den Sektoranteil ein. | `EINSTELLEN · ANTEIL` |
| `T` | PHARMA | **OBSERVED_CLAUSE** | Stelle den Drogenanteil ein. | `EINSTELLEN · ANTEIL` |
| `R` | SOURCE_SECTION_T | **COMPOSED_WORKING** | Kennzeichne den Teilwert. | `MARKIEREN · ANTEIL` |
| `R` | HERBAL | **COMPOSED_WORKING** | Markiere den Materialanteil. | `MARKIEREN · ANTEIL` |
| `R` | BIOLOGICAL | **OBSERVED_CLAUSE** | Markiere den Stationsanteil. | `MARKIEREN · ANTEIL` |
| `R` | CELESTIAL | **COMPOSED_WORKING** | Markiere den Sektoranteil. | `MARKIEREN · ANTEIL` |
| `R` | PHARMA | **COMPOSED_WORKING** | Markiere den Drogenanteil. | `MARKIEREN · ANTEIL` |

### `@ACTION+AL` — 4 beobachtet / 6 zusammengesetzt

| Aktion | Register | Status | Ausgabe | Komponentenlesung |
|---|---|---|---|---|
| `T` | SOURCE_SECTION_T | **COMPOSED_WORKING** | Lege den laufenden Eintrag [wie zuvor] fest; zur Zielspalte. | `EINSTELLEN · ZIELORT` |
| `T` | HERBAL | **COMPOSED_WORKING** | Stelle den Pflanzenposten [wie zuvor] ein; zur Zielstelle. | `EINSTELLEN · ZIELORT` |
| `T` | BIOLOGICAL | **OBSERVED_CLAUSE** | Stelle den Stationsposten [wie zuvor] ein; zur Zielstation. | `EINSTELLEN · ZIELORT` |
| `T` | CELESTIAL | **OBSERVED_CLAUSE** | Stelle den Positionsposten [wie zuvor] ein; zur Zielposition. | `EINSTELLEN · ZIELORT` |
| `T` | PHARMA | **COMPOSED_WORKING** | Stelle den Drogenposten [wie zuvor] ein; zum Zielgefäß. | `EINSTELLEN · ZIELORT` |
| `R` | SOURCE_SECTION_T | **COMPOSED_WORKING** | Kennzeichne den laufenden Eintrag [wie zuvor]; zur Zielspalte. | `MARKIEREN · ZIELORT` |
| `R` | HERBAL | **COMPOSED_WORKING** | Markiere den Pflanzenposten [wie zuvor]; zur Zielstelle. | `MARKIEREN · ZIELORT` |
| `R` | BIOLOGICAL | **OBSERVED_CLAUSE** | Markiere den Stationsposten [wie zuvor]; zur Zielstation. | `MARKIEREN · ZIELORT` |
| `R` | CELESTIAL | **COMPOSED_WORKING** | Markiere den Positionsposten [wie zuvor]; zur Zielposition. | `MARKIEREN · ZIELORT` |
| `R` | PHARMA | **OBSERVED_CLAUSE** | Markiere die Ansatzeinheit [wie zuvor]; zum Zielgefäß. | `MARKIEREN · ZIELORT` |

### `@ACTION+AL+Y` — 2 beobachtet / 8 zusammengesetzt

| Aktion | Register | Status | Ausgabe | Komponentenlesung |
|---|---|---|---|---|
| `T` | SOURCE_SECTION_T | **COMPOSED_WORKING** | Lege den laufenden Eintrag fest; zur Zielspalte. | `EINSTELLEN · ZIELORT · POSTEN` |
| `T` | HERBAL | **COMPOSED_WORKING** | Stelle den Pflanzenposten ein; zur Zielstelle. | `EINSTELLEN · ZIELORT · POSTEN` |
| `T` | BIOLOGICAL | **COMPOSED_WORKING** | Stelle den Stationsposten ein; zur Zielstation. | `EINSTELLEN · ZIELORT · POSTEN` |
| `T` | CELESTIAL | **OBSERVED_CLAUSE** | Stelle den Positionsposten ein; zur Zielposition. | `EINSTELLEN · ZIELORT · POSTEN` |
| `T` | PHARMA | **COMPOSED_WORKING** | Stelle den Drogenposten ein; zum Zielgefäß. | `EINSTELLEN · ZIELORT · POSTEN` |
| `R` | SOURCE_SECTION_T | **COMPOSED_WORKING** | Kennzeichne den laufenden Eintrag; zur Zielspalte. | `MARKIEREN · ZIELORT · POSTEN` |
| `R` | HERBAL | **COMPOSED_WORKING** | Markiere den Pflanzenposten; zur Zielstelle. | `MARKIEREN · ZIELORT · POSTEN` |
| `R` | BIOLOGICAL | **OBSERVED_CLAUSE** | Markiere den Stationsposten; zur Zielstation. | `MARKIEREN · ZIELORT · POSTEN` |
| `R` | CELESTIAL | **COMPOSED_WORKING** | Markiere den Positionsposten; zur Zielposition. | `MARKIEREN · ZIELORT · POSTEN` |
| `R` | PHARMA | **COMPOSED_WORKING** | Markiere den Drogenposten; zum Zielgefäß. | `MARKIEREN · ZIELORT · POSTEN` |

### `@ACTION+CH+E+Y` — 2 beobachtet / 8 zusammengesetzt

| Aktion | Register | Status | Ausgabe | Komponentenlesung |
|---|---|---|---|---|
| `T` | SOURCE_SECTION_T | **OBSERVED_CLAUSE** | Lege den laufenden Eintrag fest und entnimm den laufenden Eintrag; auf Grad I. | `EINSTELLEN · NEHMEN · GRAD I · POSTEN` |
| `T` | HERBAL | **COMPOSED_WORKING** | Stelle den Pflanzenposten ein und nimm den Pflanzenposten; auf Grad I. | `EINSTELLEN · NEHMEN · GRAD I · POSTEN` |
| `T` | BIOLOGICAL | **COMPOSED_WORKING** | Stelle den Stationsposten ein und entnimm den Stationsposten; auf Grad I. | `EINSTELLEN · NEHMEN · GRAD I · POSTEN` |
| `T` | CELESTIAL | **COMPOSED_WORKING** | Stelle den Positionsposten ein und nimm den Positionsposten auf; auf Grad I. | `EINSTELLEN · NEHMEN · GRAD I · POSTEN` |
| `T` | PHARMA | **COMPOSED_WORKING** | Stelle den Drogenposten ein und nimm den Drogenposten; auf Grad I. | `EINSTELLEN · NEHMEN · GRAD I · POSTEN` |
| `R` | SOURCE_SECTION_T | **COMPOSED_WORKING** | Kennzeichne den laufenden Eintrag und entnimm den laufenden Eintrag; auf Grad I. | `MARKIEREN · NEHMEN · GRAD I · POSTEN` |
| `R` | HERBAL | **COMPOSED_WORKING** | Markiere den Pflanzenposten und nimm den Pflanzenposten; auf Grad I. | `MARKIEREN · NEHMEN · GRAD I · POSTEN` |
| `R` | BIOLOGICAL | **OBSERVED_CLAUSE** | Markiere den Stationsposten und entnimm den Stationsposten; auf Grad I. | `MARKIEREN · NEHMEN · GRAD I · POSTEN` |
| `R` | CELESTIAL | **COMPOSED_WORKING** | Markiere den Positionsposten und nimm den Positionsposten auf; auf Grad I. | `MARKIEREN · NEHMEN · GRAD I · POSTEN` |
| `R` | PHARMA | **COMPOSED_WORKING** | Markiere den Drogenposten und nimm den Drogenposten; auf Grad I. | `MARKIEREN · NEHMEN · GRAD I · POSTEN` |

### `@ACTION+CHD+Y` — 3 beobachtet / 7 zusammengesetzt

| Aktion | Register | Status | Ausgabe | Komponentenlesung |
|---|---|---|---|---|
| `T` | SOURCE_SECTION_T | **COMPOSED_WORKING** | Lege den laufenden Eintrag fest und bearbeite den laufenden Eintrag. | `EINSTELLEN · BEARBEITEN · POSTEN` |
| `T` | HERBAL | **OBSERVED_CLAUSE** | Stelle den Pflanzenposten ein und bearbeite den Pflanzenposten. | `EINSTELLEN · BEARBEITEN · POSTEN` |
| `T` | BIOLOGICAL | **OBSERVED_CLAUSE** | Stelle den Stationsposten ein und bearbeite den Stationsposten. | `EINSTELLEN · BEARBEITEN · POSTEN` |
| `T` | CELESTIAL | **COMPOSED_WORKING** | Stelle den Positionsposten ein und bearbeite den Positionsposten. | `EINSTELLEN · BEARBEITEN · POSTEN` |
| `T` | PHARMA | **COMPOSED_WORKING** | Stelle den Drogenposten ein und bearbeite den Drogenposten. | `EINSTELLEN · BEARBEITEN · POSTEN` |
| `R` | SOURCE_SECTION_T | **COMPOSED_WORKING** | Kennzeichne den laufenden Eintrag und bearbeite den laufenden Eintrag. | `MARKIEREN · BEARBEITEN · POSTEN` |
| `R` | HERBAL | **COMPOSED_WORKING** | Markiere den Pflanzenposten und bearbeite den Pflanzenposten. | `MARKIEREN · BEARBEITEN · POSTEN` |
| `R` | BIOLOGICAL | **OBSERVED_CLAUSE** | Markiere den Stationsposten und bearbeite den Stationsposten. | `MARKIEREN · BEARBEITEN · POSTEN` |
| `R` | CELESTIAL | **COMPOSED_WORKING** | Markiere den Positionsposten und bearbeite den Positionsposten. | `MARKIEREN · BEARBEITEN · POSTEN` |
| `R` | PHARMA | **COMPOSED_WORKING** | Markiere den Drogenposten und bearbeite den Drogenposten. | `MARKIEREN · BEARBEITEN · POSTEN` |

### `@ACTION+OL` — 5 beobachtet / 5 zusammengesetzt

| Aktion | Register | Status | Ausgabe | Komponentenlesung |
|---|---|---|---|---|
| `T` | SOURCE_SECTION_T | **OBSERVED_CLAUSE** | Weiter lege den laufenden Eintrag [wie zuvor] fest. | `EINSTELLEN · FORTSETZEN` |
| `T` | HERBAL | **OBSERVED_CLAUSE** | Weiter stelle den Pflanzenposten [wie zuvor] ein. | `EINSTELLEN · FORTSETZEN` |
| `T` | BIOLOGICAL | **OBSERVED_CLAUSE** | Weiter stelle den Stationsposten [wie zuvor] ein. | `EINSTELLEN · FORTSETZEN` |
| `T` | CELESTIAL | **COMPOSED_WORKING** | Weiter stelle den Positionsposten [wie zuvor] ein. | `EINSTELLEN · FORTSETZEN` |
| `T` | PHARMA | **OBSERVED_CLAUSE** | Weiter stelle den Drogenanteil [wie zuvor] ein. | `EINSTELLEN · FORTSETZEN` |
| `R` | SOURCE_SECTION_T | **COMPOSED_WORKING** | Weiter kennzeichne den laufenden Eintrag [wie zuvor]. | `MARKIEREN · FORTSETZEN` |
| `R` | HERBAL | **COMPOSED_WORKING** | Weiter markiere den Pflanzenposten [wie zuvor]. | `MARKIEREN · FORTSETZEN` |
| `R` | BIOLOGICAL | **OBSERVED_CLAUSE** | Weiter markiere den Stationsposten [wie zuvor]. | `MARKIEREN · FORTSETZEN` |
| `R` | CELESTIAL | **COMPOSED_WORKING** | Weiter markiere den Positionsposten [wie zuvor]. | `MARKIEREN · FORTSETZEN` |
| `R` | PHARMA | **COMPOSED_WORKING** | Weiter markiere den Drogenposten [wie zuvor]. | `MARKIEREN · FORTSETZEN` |

### `@ACTION+OR+Y` — 2 beobachtet / 8 zusammengesetzt

| Aktion | Register | Status | Ausgabe | Komponentenlesung |
|---|---|---|---|---|
| `T` | SOURCE_SECTION_T | **COMPOSED_WORKING** | Lege die Eintragseinheit und den laufenden Eintrag fest. | `EINSTELLEN · EINHEIT · POSTEN` |
| `T` | HERBAL | **OBSERVED_CLAUSE** | Stelle die Arbeitseinheit und den Pflanzenposten ein. | `EINSTELLEN · EINHEIT · POSTEN` |
| `T` | BIOLOGICAL | **COMPOSED_WORKING** | Stelle die Stationseinheit und den Stationsposten ein. | `EINSTELLEN · EINHEIT · POSTEN` |
| `T` | CELESTIAL | **COMPOSED_WORKING** | Stelle die Positionseinheit und den Positionsposten ein. | `EINSTELLEN · EINHEIT · POSTEN` |
| `T` | PHARMA | **COMPOSED_WORKING** | Stelle die Ansatzeinheit und den Drogenposten ein. | `EINSTELLEN · EINHEIT · POSTEN` |
| `R` | SOURCE_SECTION_T | **COMPOSED_WORKING** | Kennzeichne die Eintragseinheit und den laufenden Eintrag. | `MARKIEREN · EINHEIT · POSTEN` |
| `R` | HERBAL | **COMPOSED_WORKING** | Markiere die Arbeitseinheit und den Pflanzenposten. | `MARKIEREN · EINHEIT · POSTEN` |
| `R` | BIOLOGICAL | **OBSERVED_CLAUSE** | Markiere die Stationseinheit und den Stationsposten. | `MARKIEREN · EINHEIT · POSTEN` |
| `R` | CELESTIAL | **COMPOSED_WORKING** | Markiere die Positionseinheit und den Positionsposten. | `MARKIEREN · EINHEIT · POSTEN` |
| `R` | PHARMA | **COMPOSED_WORKING** | Markiere die Ansatzeinheit und den Drogenposten. | `MARKIEREN · EINHEIT · POSTEN` |

### `@ACTION+Y` — 3 beobachtet / 7 zusammengesetzt

| Aktion | Register | Status | Ausgabe | Komponentenlesung |
|---|---|---|---|---|
| `T` | SOURCE_SECTION_T | **COMPOSED_WORKING** | Lege den laufenden Eintrag fest. | `EINSTELLEN · POSTEN` |
| `T` | HERBAL | **OBSERVED_CLAUSE** | Stelle den Pflanzenposten ein. | `EINSTELLEN · POSTEN` |
| `T` | BIOLOGICAL | **OBSERVED_CLAUSE** | Stelle den Stationsposten ein. | `EINSTELLEN · POSTEN` |
| `T` | CELESTIAL | **COMPOSED_WORKING** | Stelle den Positionsposten ein. | `EINSTELLEN · POSTEN` |
| `T` | PHARMA | **COMPOSED_WORKING** | Stelle den Drogenposten ein. | `EINSTELLEN · POSTEN` |
| `R` | SOURCE_SECTION_T | **COMPOSED_WORKING** | Kennzeichne den laufenden Eintrag. | `MARKIEREN · POSTEN` |
| `R` | HERBAL | **COMPOSED_WORKING** | Markiere den Pflanzenposten. | `MARKIEREN · POSTEN` |
| `R` | BIOLOGICAL | **OBSERVED_CLAUSE** | Markiere den Stationsposten. | `MARKIEREN · POSTEN` |
| `R` | CELESTIAL | **COMPOSED_WORKING** | Markiere den Positionsposten. | `MARKIEREN · POSTEN` |
| `R` | PHARMA | **COMPOSED_WORKING** | Markiere den Drogenposten. | `MARKIEREN · POSTEN` |

### `CH+@ACTION` — 2 beobachtet / 8 zusammengesetzt

| Aktion | Register | Status | Ausgabe | Komponentenlesung |
|---|---|---|---|---|
| `T` | SOURCE_SECTION_T | **COMPOSED_WORKING** | Entnimm den laufenden Eintrag [wie zuvor] und lege den laufenden Eintrag [wie zuvor] fest. | `NEHMEN · EINSTELLEN` |
| `T` | HERBAL | **OBSERVED_CLAUSE** | Nimm den Arbeitswert [wie zuvor] und stelle den Arbeitswert [wie zuvor] ein. | `NEHMEN · EINSTELLEN` |
| `T` | BIOLOGICAL | **COMPOSED_WORKING** | Entnimm den Stationsposten [wie zuvor] und stelle den Stationsposten [wie zuvor] ein. | `NEHMEN · EINSTELLEN` |
| `T` | CELESTIAL | **COMPOSED_WORKING** | Nimm den Positionsposten [wie zuvor] auf und stelle den Positionsposten [wie zuvor] ein. | `NEHMEN · EINSTELLEN` |
| `T` | PHARMA | **COMPOSED_WORKING** | Nimm den Drogenposten [wie zuvor] und stelle den Drogenposten [wie zuvor] ein. | `NEHMEN · EINSTELLEN` |
| `R` | SOURCE_SECTION_T | **COMPOSED_WORKING** | Entnimm den laufenden Eintrag [wie zuvor] und kennzeichne den laufenden Eintrag [wie zuvor]. | `NEHMEN · MARKIEREN` |
| `R` | HERBAL | **COMPOSED_WORKING** | Nimm den Pflanzenposten [wie zuvor] und markiere den Pflanzenposten [wie zuvor]. | `NEHMEN · MARKIEREN` |
| `R` | BIOLOGICAL | **OBSERVED_CLAUSE** | Entnimm den Stationswert [wie zuvor] und markiere den Stationswert [wie zuvor]. | `NEHMEN · MARKIEREN` |
| `R` | CELESTIAL | **COMPOSED_WORKING** | Nimm den Positionsposten [wie zuvor] auf und markiere den Positionsposten [wie zuvor]. | `NEHMEN · MARKIEREN` |
| `R` | PHARMA | **COMPOSED_WORKING** | Nimm den Drogenposten [wie zuvor] und markiere den Drogenposten [wie zuvor]. | `NEHMEN · MARKIEREN` |

## 55 direkte T/R-Ausgaben

Jeder Rahmen×Register-Paarvergleich behält denselben Komponentenrest. Acht Paare sind beidseitig beobachtet, 21 haben eine beobachtete und eine zusammengesetzte Seite, 26 sind beidseitig zusammengesetzt. Alle 55 bleiben sprachlich verschieden.

| Rahmen | Register | T | R | Evidenzpaar |
|---|---|---|---|---|
| `@ACTION` | SOURCE_SECTION_T | Lege den laufenden Eintrag [wie zuvor] fest. | Kennzeichne den laufenden Eintrag [wie zuvor]. | MIXED_OBSERVED_COMPOSED |
| `@ACTION` | HERBAL | Stelle den Pflanzenposten [wie zuvor] ein. | Markiere den Pflanzenposten [wie zuvor]. | BOTH_OBSERVED |
| `@ACTION` | BIOLOGICAL | Stelle den Stationsposten [wie zuvor] ein. | Markiere den Stationsposten [wie zuvor]. | MIXED_OBSERVED_COMPOSED |
| `@ACTION` | CELESTIAL | Stelle den Positionsposten [wie zuvor] ein. | Markiere den Positionsposten [wie zuvor]. | MIXED_OBSERVED_COMPOSED |
| `@ACTION` | PHARMA | Stelle den Drogenposten [wie zuvor] ein. | Markiere den Drogenposten [wie zuvor]. | MIXED_OBSERVED_COMPOSED |
| `@ACTION+AIIN` | SOURCE_SECTION_T | Lege den Kennwert fest. | Kennzeichne den Kennwert. | BOTH_COMPOSED_WORKING |
| `@ACTION+AIIN` | HERBAL | Stelle den Arbeitswert ein. | Markiere den Arbeitswert. | BOTH_OBSERVED |
| `@ACTION+AIIN` | BIOLOGICAL | Stelle den Stationswert ein. | Markiere den Stationswert. | BOTH_OBSERVED |
| `@ACTION+AIIN` | CELESTIAL | Stelle den Positionswert ein. | Markiere den Positionswert. | BOTH_COMPOSED_WORKING |
| `@ACTION+AIIN` | PHARMA | Stelle den Mengenwert ein. | Markiere den Mengenwert. | MIXED_OBSERVED_COMPOSED |
| `@ACTION+AIN` | SOURCE_SECTION_T | Lege den Teilwert fest. | Kennzeichne den Teilwert. | BOTH_COMPOSED_WORKING |
| `@ACTION+AIN` | HERBAL | Stelle den Materialanteil ein. | Markiere den Materialanteil. | BOTH_COMPOSED_WORKING |
| `@ACTION+AIN` | BIOLOGICAL | Stelle den Stationsanteil ein. | Markiere den Stationsanteil. | BOTH_OBSERVED |
| `@ACTION+AIN` | CELESTIAL | Stelle den Sektoranteil ein. | Markiere den Sektoranteil. | BOTH_COMPOSED_WORKING |
| `@ACTION+AIN` | PHARMA | Stelle den Drogenanteil ein. | Markiere den Drogenanteil. | MIXED_OBSERVED_COMPOSED |
| `@ACTION+AL` | SOURCE_SECTION_T | Lege den laufenden Eintrag [wie zuvor] fest; zur Zielspalte. | Kennzeichne den laufenden Eintrag [wie zuvor]; zur Zielspalte. | BOTH_COMPOSED_WORKING |
| `@ACTION+AL` | HERBAL | Stelle den Pflanzenposten [wie zuvor] ein; zur Zielstelle. | Markiere den Pflanzenposten [wie zuvor]; zur Zielstelle. | BOTH_COMPOSED_WORKING |
| `@ACTION+AL` | BIOLOGICAL | Stelle den Stationsposten [wie zuvor] ein; zur Zielstation. | Markiere den Stationsposten [wie zuvor]; zur Zielstation. | BOTH_OBSERVED |
| `@ACTION+AL` | CELESTIAL | Stelle den Positionsposten [wie zuvor] ein; zur Zielposition. | Markiere den Positionsposten [wie zuvor]; zur Zielposition. | MIXED_OBSERVED_COMPOSED |
| `@ACTION+AL` | PHARMA | Stelle den Drogenposten [wie zuvor] ein; zum Zielgefäß. | Markiere die Ansatzeinheit [wie zuvor]; zum Zielgefäß. | MIXED_OBSERVED_COMPOSED |
| `@ACTION+AL+Y` | SOURCE_SECTION_T | Lege den laufenden Eintrag fest; zur Zielspalte. | Kennzeichne den laufenden Eintrag; zur Zielspalte. | BOTH_COMPOSED_WORKING |
| `@ACTION+AL+Y` | HERBAL | Stelle den Pflanzenposten ein; zur Zielstelle. | Markiere den Pflanzenposten; zur Zielstelle. | BOTH_COMPOSED_WORKING |
| `@ACTION+AL+Y` | BIOLOGICAL | Stelle den Stationsposten ein; zur Zielstation. | Markiere den Stationsposten; zur Zielstation. | MIXED_OBSERVED_COMPOSED |
| `@ACTION+AL+Y` | CELESTIAL | Stelle den Positionsposten ein; zur Zielposition. | Markiere den Positionsposten; zur Zielposition. | MIXED_OBSERVED_COMPOSED |
| `@ACTION+AL+Y` | PHARMA | Stelle den Drogenposten ein; zum Zielgefäß. | Markiere den Drogenposten; zum Zielgefäß. | BOTH_COMPOSED_WORKING |
| `@ACTION+CH+E+Y` | SOURCE_SECTION_T | Lege den laufenden Eintrag fest und entnimm den laufenden Eintrag; auf Grad I. | Kennzeichne den laufenden Eintrag und entnimm den laufenden Eintrag; auf Grad I. | MIXED_OBSERVED_COMPOSED |
| `@ACTION+CH+E+Y` | HERBAL | Stelle den Pflanzenposten ein und nimm den Pflanzenposten; auf Grad I. | Markiere den Pflanzenposten und nimm den Pflanzenposten; auf Grad I. | BOTH_COMPOSED_WORKING |
| `@ACTION+CH+E+Y` | BIOLOGICAL | Stelle den Stationsposten ein und entnimm den Stationsposten; auf Grad I. | Markiere den Stationsposten und entnimm den Stationsposten; auf Grad I. | MIXED_OBSERVED_COMPOSED |
| `@ACTION+CH+E+Y` | CELESTIAL | Stelle den Positionsposten ein und nimm den Positionsposten auf; auf Grad I. | Markiere den Positionsposten und nimm den Positionsposten auf; auf Grad I. | BOTH_COMPOSED_WORKING |
| `@ACTION+CH+E+Y` | PHARMA | Stelle den Drogenposten ein und nimm den Drogenposten; auf Grad I. | Markiere den Drogenposten und nimm den Drogenposten; auf Grad I. | BOTH_COMPOSED_WORKING |
| `@ACTION+CHD+Y` | SOURCE_SECTION_T | Lege den laufenden Eintrag fest und bearbeite den laufenden Eintrag. | Kennzeichne den laufenden Eintrag und bearbeite den laufenden Eintrag. | BOTH_COMPOSED_WORKING |
| `@ACTION+CHD+Y` | HERBAL | Stelle den Pflanzenposten ein und bearbeite den Pflanzenposten. | Markiere den Pflanzenposten und bearbeite den Pflanzenposten. | MIXED_OBSERVED_COMPOSED |
| `@ACTION+CHD+Y` | BIOLOGICAL | Stelle den Stationsposten ein und bearbeite den Stationsposten. | Markiere den Stationsposten und bearbeite den Stationsposten. | BOTH_OBSERVED |
| `@ACTION+CHD+Y` | CELESTIAL | Stelle den Positionsposten ein und bearbeite den Positionsposten. | Markiere den Positionsposten und bearbeite den Positionsposten. | BOTH_COMPOSED_WORKING |
| `@ACTION+CHD+Y` | PHARMA | Stelle den Drogenposten ein und bearbeite den Drogenposten. | Markiere den Drogenposten und bearbeite den Drogenposten. | BOTH_COMPOSED_WORKING |
| `@ACTION+OL` | SOURCE_SECTION_T | Weiter lege den laufenden Eintrag [wie zuvor] fest. | Weiter kennzeichne den laufenden Eintrag [wie zuvor]. | MIXED_OBSERVED_COMPOSED |
| `@ACTION+OL` | HERBAL | Weiter stelle den Pflanzenposten [wie zuvor] ein. | Weiter markiere den Pflanzenposten [wie zuvor]. | MIXED_OBSERVED_COMPOSED |
| `@ACTION+OL` | BIOLOGICAL | Weiter stelle den Stationsposten [wie zuvor] ein. | Weiter markiere den Stationsposten [wie zuvor]. | BOTH_OBSERVED |
| `@ACTION+OL` | CELESTIAL | Weiter stelle den Positionsposten [wie zuvor] ein. | Weiter markiere den Positionsposten [wie zuvor]. | BOTH_COMPOSED_WORKING |
| `@ACTION+OL` | PHARMA | Weiter stelle den Drogenanteil [wie zuvor] ein. | Weiter markiere den Drogenposten [wie zuvor]. | MIXED_OBSERVED_COMPOSED |
| `@ACTION+OR+Y` | SOURCE_SECTION_T | Lege die Eintragseinheit und den laufenden Eintrag fest. | Kennzeichne die Eintragseinheit und den laufenden Eintrag. | BOTH_COMPOSED_WORKING |
| `@ACTION+OR+Y` | HERBAL | Stelle die Arbeitseinheit und den Pflanzenposten ein. | Markiere die Arbeitseinheit und den Pflanzenposten. | MIXED_OBSERVED_COMPOSED |
| `@ACTION+OR+Y` | BIOLOGICAL | Stelle die Stationseinheit und den Stationsposten ein. | Markiere die Stationseinheit und den Stationsposten. | MIXED_OBSERVED_COMPOSED |
| `@ACTION+OR+Y` | CELESTIAL | Stelle die Positionseinheit und den Positionsposten ein. | Markiere die Positionseinheit und den Positionsposten. | BOTH_COMPOSED_WORKING |
| `@ACTION+OR+Y` | PHARMA | Stelle die Ansatzeinheit und den Drogenposten ein. | Markiere die Ansatzeinheit und den Drogenposten. | BOTH_COMPOSED_WORKING |
| `@ACTION+Y` | SOURCE_SECTION_T | Lege den laufenden Eintrag fest. | Kennzeichne den laufenden Eintrag. | BOTH_COMPOSED_WORKING |
| `@ACTION+Y` | HERBAL | Stelle den Pflanzenposten ein. | Markiere den Pflanzenposten. | MIXED_OBSERVED_COMPOSED |
| `@ACTION+Y` | BIOLOGICAL | Stelle den Stationsposten ein. | Markiere den Stationsposten. | BOTH_OBSERVED |
| `@ACTION+Y` | CELESTIAL | Stelle den Positionsposten ein. | Markiere den Positionsposten. | BOTH_COMPOSED_WORKING |
| `@ACTION+Y` | PHARMA | Stelle den Drogenposten ein. | Markiere den Drogenposten. | BOTH_COMPOSED_WORKING |
| `CH+@ACTION` | SOURCE_SECTION_T | Entnimm den laufenden Eintrag [wie zuvor] und lege den laufenden Eintrag [wie zuvor] fest. | Entnimm den laufenden Eintrag [wie zuvor] und kennzeichne den laufenden Eintrag [wie zuvor]. | BOTH_COMPOSED_WORKING |
| `CH+@ACTION` | HERBAL | Nimm den Arbeitswert [wie zuvor] und stelle den Arbeitswert [wie zuvor] ein. | Nimm den Pflanzenposten [wie zuvor] und markiere den Pflanzenposten [wie zuvor]. | MIXED_OBSERVED_COMPOSED |
| `CH+@ACTION` | BIOLOGICAL | Entnimm den Stationsposten [wie zuvor] und stelle den Stationsposten [wie zuvor] ein. | Entnimm den Stationswert [wie zuvor] und markiere den Stationswert [wie zuvor]. | MIXED_OBSERVED_COMPOSED |
| `CH+@ACTION` | CELESTIAL | Nimm den Positionsposten [wie zuvor] auf und stelle den Positionsposten [wie zuvor] ein. | Nimm den Positionsposten [wie zuvor] auf und markiere den Positionsposten [wie zuvor]. | BOTH_COMPOSED_WORKING |
| `CH+@ACTION` | PHARMA | Nimm den Drogenposten [wie zuvor] und stelle den Drogenposten [wie zuvor] ein. | Nimm den Drogenposten [wie zuvor] und markiere den Drogenposten [wie zuvor]. | BOTH_COMPOSED_WORKING |

## Registerabdeckung

| Register | beobachtet | zusammengesetzt | alte Träger |
|---|---:|---:|---:|
| SOURCE_SECTION_T | 3 | 19 | 3 |
| HERBAL | 9 | 13 | 15 |
| BIOLOGICAL | 17 | 5 | 46 |
| CELESTIAL | 3 | 19 | 4 |
| PHARMA | 5 | 17 | 8 |

## Drei sichtbare Zustandskorrekturen

In 34/37 beobachteten Zellen ist auch die Y-Default-Ausgabe des Renderers tatsächlich belegt. Drei beobachtete Zellen erben stattdessen ein anderes aktives Argument; die Beobachtung gewinnt immer:

- `R+AL` / PHARMA: Renderer-Y „Markiere den Drogenposten [wie zuvor]; zum Zielgefäß.“; beobachtet „Markiere die Ansatzeinheit [wie zuvor]; zum Zielgefäß.“; geerbtes Argument `OR`.
- `CH+T` / HERBAL: Renderer-Y „Nimm den Pflanzenposten [wie zuvor] und stelle den Pflanzenposten [wie zuvor] ein.“; beobachtet „Nimm den Arbeitswert [wie zuvor] und stelle den Arbeitswert [wie zuvor] ein.“; geerbtes Argument `AIIN`.
- `CH+R` / BIOLOGICAL: Renderer-Y „Entnimm den Stationsposten [wie zuvor] und markiere den Stationsposten [wie zuvor].“; beobachtet „Entnimm den Stationswert [wie zuvor] und markiere den Stationswert [wie zuvor].“; geerbtes Argument `AIIN`.

Das sind keine Fehler des Komponentenmodells: Das Rezept enthält dort kein sichtbares Argument, also entscheidet der laufende Besitzerzustand, ob POSTEN, WERT, ANTEIL oder EINHEIT eingesetzt wird.

## Arbeitsfolgerung

Das Deck liefert nun für keine der 110 Kombinationen mehr eine leere Bedeutung. Gleichzeitig bleibt die Herkunft hörbar: Beobachtung und produktive Arbeitskomposition werden nicht vermischt. Das ist genau die gesuchte Mischarchitektur aus kurzen Fachkürzeln, stabilen Kompositionsplätzen, registergebundenem Wortschatz und wenigen getragenen Zuständen.

## Nächster Schritt

Verdichte die 73 zusammengesetzten Zellen zu Vorhersagekarten für die weiterhin geschlossenen Seiten. Priorität haben Zellen, die durch mindestens zwei alte Nachbarhandlungen im selben Rahmen und durch alte Slotwerte in genau diesem Register gestützt sind. Die Ausgabe bleibt `COMPOSED_WORKING`, bis ein späterer echter Träger sie beobachtet.
