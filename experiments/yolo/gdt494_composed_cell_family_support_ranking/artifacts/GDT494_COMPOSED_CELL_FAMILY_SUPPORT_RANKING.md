# GDT494 — Priorität der 73 zusammengesetzten T/R-Karten

GDT494 ändert keine GDT493-Lesung und wertet keine Komposition zur Beobachtung auf. Es sortiert die 73 `COMPOSED_WORKING`-Karten ausschließlich danach, welche exakten alten GDT416-Handlungsköpfe denselben formalen Rest im selben Register bereits tragen.

- Rangierte Arbeitskarten: **73/73**.
- Tier A, mindestens zwei andere Nicht-T/R-Köpfe im selben Register: **27**.
- Tier B, genau ein anderer Nicht-T/R-Kopf: **19**.
- Tier C, nur die lokale T/R-Gegenaktion: **5**.
- Tier D, nur dieselbe Zielhandlung in anderen Registern: **22**.
- Karten mit irgendeinem Nicht-T/R-Kopf im selben Register: **46**; mit irgendeiner lokalen Familienstütze: **51**.
- Karten mit derselben Zielhandlung in einem anderen Register: **73/73**.

## Ranglogik

Es gibt keinen vermischten Geheimscore. Zuerst zählt die verständliche Stufe A–D. Innerhalb einer Stufe folgen: mehr verschiedene Nicht-T/R-Köpfe, mehr ihrer Eventträger, vorhandene T/R-Gegenseite, mehr andere Register mit derselben Zielhandlung, dann Rezept und Register. Jede Karte bleibt `COMPOSED_WORKING`.

## Tier A — mindestens zwei andere Fachhandlungen im selben Register (`A_MULTIHEAD_SAME_REGISTER`)

| Rang | Rezept | Register | Arbeitslesung | lokale Nicht-T/R-Köpfe | T/R-Paar | andere Zielregister | Zustand |
|---:|---|---|---|---|---|---:|---|
| 1 | `T` | BIOLOGICAL | Stelle den Stationsposten [wie zuvor] ein. | `OK|CH|SH|S|CHD` | YES | 1 | ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT |
| 2 | `R+AL` | CELESTIAL | Markiere den Positionsposten [wie zuvor]; zur Zielposition. | `OK|CH|K|S|CHD` | YES | 2 | ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT |
| 3 | `T+AIIN` | CELESTIAL | Stelle den Positionswert ein. | `OK|K|S|CHD` | NO | 3 | NONE |
| 4 | `R+AIIN` | CELESTIAL | Markiere den Positionswert. | `OK|K|S|CHD` | NO | 2 | NONE |
| 5 | `T+AIN` | HERBAL | Stelle den Materialanteil ein. | `OK|K|S|CHD` | NO | 2 | NONE |
| 6 | `R+AIN` | HERBAL | Markiere den Materialanteil. | `OK|K|S|CHD` | NO | 1 | NONE |
| 7 | `R+Y` | HERBAL | Markiere den Pflanzenposten. | `OK|K|CHD` | YES | 1 | NONE |
| 8 | `R+OL` | HERBAL | Weiter markiere den Pflanzenposten [wie zuvor]. | `OK|SH|K` | YES | 1 | ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT |
| 9 | `T+AL` | HERBAL | Stelle den Pflanzenposten [wie zuvor] ein; zur Zielstelle. | `OK|CH|K` | NO | 2 | ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT |
| 10 | `T+Y` | PHARMA | Stelle den Drogenposten ein. | `OK|K|CHD` | NO | 2 | NONE |
| 11 | `R+AL` | HERBAL | Markiere den Pflanzenposten [wie zuvor]; zur Zielstelle. | `OK|CH|K` | NO | 2 | ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT |
| 12 | `R+Y` | PHARMA | Markiere den Drogenposten. | `OK|K|CHD` | NO | 1 | NONE |
| 13 | `R+AIIN` | PHARMA | Markiere den Mengenwert. | `OK|CH|S` | YES | 2 | NONE |
| 14 | `T+OL` | CELESTIAL | Weiter stelle den Positionsposten [wie zuvor] ein. | `OK|SH|K` | NO | 4 | ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT |
| 15 | `R+OL` | CELESTIAL | Weiter markiere den Positionsposten [wie zuvor]. | `OK|SH|K` | NO | 1 | ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT |
| 16 | `R+OL` | SOURCE_SECTION_T | Weiter kennzeichne den laufenden Eintrag [wie zuvor]. | `OK|SH|K` | YES | 1 | ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT |
| 17 | `T` | SOURCE_SECTION_T | Lege den laufenden Eintrag [wie zuvor] fest. | `OK|SH|S` | YES | 1 | ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT |
| 18 | `T+AIIN` | SOURCE_SECTION_T | Lege den Kennwert fest. | `OK|SH|K` | NO | 3 | NONE |
| 19 | `R+AIIN` | SOURCE_SECTION_T | Kennzeichne den Kennwert. | `OK|SH|K` | NO | 2 | NONE |
| 20 | `T+Y` | SOURCE_SECTION_T | Lege den laufenden Eintrag fest. | `OK|K|CHD` | NO | 2 | NONE |
| 21 | `R+Y` | SOURCE_SECTION_T | Kennzeichne den laufenden Eintrag. | `OK|K|CHD` | NO | 1 | NONE |
| 22 | `R+AIN` | PHARMA | Markiere den Drogenanteil. | `OK|S|CHD` | YES | 1 | NONE |
| 23 | `R+CH+E+Y` | HERBAL | Markiere den Pflanzenposten und nimm den Pflanzenposten; auf Grad I. | `OK|K|S` | NO | 1 | NONE |
| 24 | `T+CH+E+Y` | HERBAL | Stelle den Pflanzenposten ein und nimm den Pflanzenposten; auf Grad I. | `OK|K|S` | NO | 1 | NONE |
| 25 | `T+AL+Y` | BIOLOGICAL | Stelle den Stationsposten ein; zur Zielstation. | `OK|CH` | YES | 1 | NONE |
| 26 | `R+OR+Y` | SOURCE_SECTION_T | Kennzeichne die Eintragseinheit und den laufenden Eintrag. | `SH|S` | NO | 1 | NONE |
| 27 | `T+OR+Y` | SOURCE_SECTION_T | Lege die Eintragseinheit und den laufenden Eintrag fest. | `SH|S` | NO | 1 | NONE |

## Tier B — ein anderer Fachhandlungskopf im selben Register (`B_SINGLE_NONTR_HEAD`)

| Rang | Rezept | Register | Arbeitslesung | lokale Nicht-T/R-Köpfe | T/R-Paar | andere Zielregister | Zustand |
|---:|---|---|---|---|---|---:|---|
| 28 | `T` | PHARMA | Stelle den Drogenposten [wie zuvor] ein. | `S` | YES | 1 | ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT |
| 29 | `R+OL` | PHARMA | Weiter markiere den Drogenposten [wie zuvor]. | `OK` | YES | 1 | ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT |
| 30 | `T` | CELESTIAL | Stelle den Positionsposten [wie zuvor] ein. | `S` | YES | 1 | ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT |
| 31 | `R+CHD+Y` | HERBAL | Markiere den Pflanzenposten und bearbeite den Pflanzenposten. | `K` | YES | 1 | NONE |
| 32 | `R+AL+Y` | CELESTIAL | Markiere den Positionsposten; zur Zielposition. | `OK` | YES | 1 | NONE |
| 33 | `T+Y` | CELESTIAL | Stelle den Positionsposten ein. | `CHD` | NO | 2 | NONE |
| 34 | `R+Y` | CELESTIAL | Markiere den Positionsposten. | `CHD` | NO | 1 | NONE |
| 35 | `R+AL+Y` | PHARMA | Markiere den Drogenposten; zum Zielgefäß. | `CH` | NO | 1 | NONE |
| 36 | `T+AL+Y` | PHARMA | Stelle den Drogenposten ein; zum Zielgefäß. | `CH` | NO | 1 | NONE |
| 37 | `T+AL` | PHARMA | Stelle den Drogenposten [wie zuvor] ein; zum Zielgefäß. | `OK` | YES | 2 | ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT |
| 38 | `CH+T` | BIOLOGICAL | Entnimm den Stationsposten [wie zuvor] und stelle den Stationsposten [wie zuvor] ein. | `K` | YES | 1 | ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT |
| 39 | `T+AL` | SOURCE_SECTION_T | Lege den laufenden Eintrag [wie zuvor] fest; zur Zielspalte. | `CH` | NO | 2 | ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT |
| 40 | `R+AL` | SOURCE_SECTION_T | Kennzeichne den laufenden Eintrag [wie zuvor]; zur Zielspalte. | `CH` | NO | 2 | ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT |
| 41 | `T+AIN` | CELESTIAL | Stelle den Sektoranteil ein. | `S` | NO | 2 | NONE |
| 42 | `T+AIN` | SOURCE_SECTION_T | Lege den Teilwert fest. | `OK` | NO | 2 | NONE |
| 43 | `R+AIN` | CELESTIAL | Markiere den Sektoranteil. | `S` | NO | 1 | NONE |
| 44 | `R+AIN` | SOURCE_SECTION_T | Kennzeichne den Teilwert. | `OK` | NO | 1 | NONE |
| 45 | `CH+R` | CELESTIAL | Nimm den Positionsposten [wie zuvor] auf und markiere den Positionsposten [wie zuvor]. | `S` | NO | 1 | ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT |
| 46 | `CH+T` | CELESTIAL | Nimm den Positionsposten [wie zuvor] auf und stelle den Positionsposten [wie zuvor] ein. | `S` | NO | 1 | ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT |

## Tier C — nur die beobachtete T/R-Gegenseite (`C_OPPOSITE_TR_ONLY`)

| Rang | Rezept | Register | Arbeitslesung | lokale Nicht-T/R-Köpfe | T/R-Paar | andere Zielregister | Zustand |
|---:|---|---|---|---|---|---:|---|
| 47 | `CH+R` | HERBAL | Nimm den Pflanzenposten [wie zuvor] und markiere den Pflanzenposten [wie zuvor]. | `NONE` | YES | 1 | ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT |
| 48 | `R+CH+E+Y` | SOURCE_SECTION_T | Kennzeichne den laufenden Eintrag und entnimm den laufenden Eintrag; auf Grad I. | `NONE` | YES | 1 | NONE |
| 49 | `R+OR+Y` | HERBAL | Markiere die Arbeitseinheit und den Pflanzenposten. | `NONE` | YES | 1 | NONE |
| 50 | `T+CH+E+Y` | BIOLOGICAL | Stelle den Stationsposten ein und entnimm den Stationsposten; auf Grad I. | `NONE` | YES | 1 | NONE |
| 51 | `T+OR+Y` | BIOLOGICAL | Stelle die Stationseinheit und den Stationsposten ein. | `NONE` | YES | 1 | NONE |

## Tier D — nur registerübergreifende Zielhandlungsstütze (`D_CROSS_REGISTER_ONLY`)

| Rang | Rezept | Register | Arbeitslesung | lokale Nicht-T/R-Köpfe | T/R-Paar | andere Zielregister | Zustand |
|---:|---|---|---|---|---|---:|---|
| 52 | `T+CHD+Y` | CELESTIAL | Stelle den Positionsposten ein und bearbeite den Positionsposten. | `NONE` | NO | 2 | NONE |
| 53 | `T+CHD+Y` | PHARMA | Stelle den Drogenposten ein und bearbeite den Drogenposten. | `NONE` | NO | 2 | NONE |
| 54 | `T+CHD+Y` | SOURCE_SECTION_T | Lege den laufenden Eintrag fest und bearbeite den laufenden Eintrag. | `NONE` | NO | 2 | NONE |
| 55 | `R+CHD+Y` | CELESTIAL | Markiere den Positionsposten und bearbeite den Positionsposten. | `NONE` | NO | 1 | NONE |
| 56 | `R+CHD+Y` | PHARMA | Markiere den Drogenposten und bearbeite den Drogenposten. | `NONE` | NO | 1 | NONE |
| 57 | `R+CHD+Y` | SOURCE_SECTION_T | Kennzeichne den laufenden Eintrag und bearbeite den laufenden Eintrag. | `NONE` | NO | 1 | NONE |
| 58 | `CH+R` | PHARMA | Nimm den Drogenposten [wie zuvor] und markiere den Drogenposten [wie zuvor]. | `NONE` | NO | 1 | ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT |
| 59 | `CH+R` | SOURCE_SECTION_T | Entnimm den laufenden Eintrag [wie zuvor] und kennzeichne den laufenden Eintrag [wie zuvor]. | `NONE` | NO | 1 | ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT |
| 60 | `CH+T` | PHARMA | Nimm den Drogenposten [wie zuvor] und stelle den Drogenposten [wie zuvor] ein. | `NONE` | NO | 1 | ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT |
| 61 | `CH+T` | SOURCE_SECTION_T | Entnimm den laufenden Eintrag [wie zuvor] und lege den laufenden Eintrag [wie zuvor] fest. | `NONE` | NO | 1 | ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT |
| 62 | `R+AL+Y` | HERBAL | Markiere den Pflanzenposten; zur Zielstelle. | `NONE` | NO | 1 | NONE |
| 63 | `R+AL+Y` | SOURCE_SECTION_T | Kennzeichne den laufenden Eintrag; zur Zielspalte. | `NONE` | NO | 1 | NONE |
| 64 | `R+CH+E+Y` | CELESTIAL | Markiere den Positionsposten und nimm den Positionsposten auf; auf Grad I. | `NONE` | NO | 1 | NONE |
| 65 | `R+CH+E+Y` | PHARMA | Markiere den Drogenposten und nimm den Drogenposten; auf Grad I. | `NONE` | NO | 1 | NONE |
| 66 | `R+OR+Y` | CELESTIAL | Markiere die Positionseinheit und den Positionsposten. | `NONE` | NO | 1 | NONE |
| 67 | `R+OR+Y` | PHARMA | Markiere die Ansatzeinheit und den Drogenposten. | `NONE` | NO | 1 | NONE |
| 68 | `T+AL+Y` | HERBAL | Stelle den Pflanzenposten ein; zur Zielstelle. | `NONE` | NO | 1 | NONE |
| 69 | `T+AL+Y` | SOURCE_SECTION_T | Lege den laufenden Eintrag fest; zur Zielspalte. | `NONE` | NO | 1 | NONE |
| 70 | `T+CH+E+Y` | CELESTIAL | Stelle den Positionsposten ein und nimm den Positionsposten auf; auf Grad I. | `NONE` | NO | 1 | NONE |
| 71 | `T+CH+E+Y` | PHARMA | Stelle den Drogenposten ein und nimm den Drogenposten; auf Grad I. | `NONE` | NO | 1 | NONE |
| 72 | `T+OR+Y` | CELESTIAL | Stelle die Positionseinheit und den Positionsposten ein. | `NONE` | NO | 1 | NONE |
| 73 | `T+OR+Y` | PHARMA | Stelle die Ansatzeinheit und den Drogenposten ein. | `NONE` | NO | 1 | NONE |

## Rahmenprofil

| Rahmen | Karten | A | B | C | D |
|---|---:|---:|---:|---:|---:|
| `@ACTION` | 4 | 2 | 2 | 0 | 0 |
| `@ACTION+AIIN` | 5 | 5 | 0 | 0 | 0 |
| `@ACTION+AIN` | 7 | 3 | 4 | 0 | 0 |
| `@ACTION+AL` | 6 | 3 | 3 | 0 | 0 |
| `@ACTION+AL+Y` | 8 | 1 | 3 | 0 | 4 |
| `@ACTION+CH+E+Y` | 8 | 2 | 0 | 2 | 4 |
| `@ACTION+CHD+Y` | 7 | 0 | 1 | 0 | 6 |
| `@ACTION+OL` | 5 | 4 | 1 | 0 | 0 |
| `@ACTION+OR+Y` | 8 | 2 | 0 | 2 | 4 |
| `@ACTION+Y` | 7 | 5 | 2 | 0 | 0 |
| `CH+@ACTION` | 8 | 0 | 3 | 1 | 4 |

## Registerprofil

| Register | Karten | A | B | C | D |
|---|---:|---:|---:|---:|---:|
| SOURCE_SECTION_T | 19 | 8 | 4 | 1 | 6 |
| HERBAL | 13 | 8 | 1 | 2 | 2 |
| BIOLOGICAL | 5 | 2 | 1 | 2 | 0 |
| CELESTIAL | 19 | 5 | 8 | 0 | 6 |
| PHARMA | 17 | 4 | 5 | 0 | 8 |

## Was Tier A praktisch bedeutet

Die 27 A-Karten sind die besten gegenwärtigen Arbeitsvorhersagen innerhalb der geschlossenen 26-Seiten-Basis. Beispiel: celestial `T+AIIN` und `R+AIIN` sind noch nicht als ganze T/R-Sätze belegt, aber derselbe WERT-Rahmen steht dort bereits mit OK, K, S und CHD. Herbal `T/R+CH+E+Y` hat denselben Rest bereits mit OK, K und S. Das macht die neue T/R-Füllung kompositionell natürlich, ohne ihre Oberfläche oder tatsächliche Vorkunft vorherzusagen.

Tier D bleibt ebenfalls lesbar, aber schwächer: Dort kennen wir die Zielhandlung mit diesem Rahmen aus einem anderen Register und jeden Slot lokal, jedoch noch keinen anderen kompletten Handlungskopf im Zielregister.

## Nächster Schritt

Verdichte die 27 Tier-A-Karten zu einem kurzen Zukunftsblatt mit Komponentenlesung, owner-lokalem Satz, allen lokalen Alternativköpfen und der expliziten Warnung `KEINE OBERFLÄCHENVORHERSAGE`. Danach kann dasselbe Rankingprinzip auf andere eng begrenzte Aktionspaare angewendet werden, ohne die Seiten zu öffnen.
