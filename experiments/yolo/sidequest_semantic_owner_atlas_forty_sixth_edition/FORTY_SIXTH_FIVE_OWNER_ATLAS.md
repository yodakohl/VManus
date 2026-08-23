# Besitzeratlas der 28 gemeinsamen Kerne

Jeder Kern wird unter fünf Besitzern gesprochen: Pflanze, Beckenstation, Tuchfilter,
Himmelstafel und allgemeines Werkstück. Der Kern bleibt kurz; nur Gegenstand, Quelle,
Ziel, Lauf, Satz und sichtbares Ergebnis wechseln mit dem Besitzer.

## AIIN — SOLLWERT

- PLANT_BATCH: Sollwert für der aktuelle Pflanzenposten
- BASIN_STATION: Sollwert für die aktuelle Beckencharge
- CLOTH_FILTER: Sollwert für der aktuelle Tuchposten
- CELESTIAL_TABLE: Sollwert für der aktuelle Tabellenwert
- GENERIC_WORKPIECE: Sollwert für das aktuelle Werkstück

Grenze: concrete object must come from owner; root stays short.

## AIN — PORTION

- PLANT_BATCH: Portion von der aktuelle Pflanzenposten
- BASIN_STATION: Portion von die aktuelle Beckencharge
- CLOTH_FILTER: Portion von der aktuelle Tuchposten
- CELESTIAL_TABLE: Portion von der aktuelle Tabellenwert
- GENERIC_WORKPIECE: Portion von das aktuelle Werkstück

Grenze: concrete object must come from owner; root stays short.

## IIN — STUFE

- PLANT_BATCH: Arbeitsstufe von der Pflanzenansatz
- BASIN_STATION: Arbeitsstufe von der laufende Beckengang
- CLOTH_FILTER: Arbeitsstufe von der Filteransatz
- CELESTIAL_TABLE: Arbeitsstufe von der lokale Tabellensatz
- GENERIC_WORKPIECE: Arbeitsstufe von der laufende Arbeitsansatz

Grenze: concrete object must come from owner; root stays short.

## AL — ZIEL

- PLANT_BATCH: hin zu der bezeichnete Pflanzenteil oder das Gefäß
- BASIN_STATION: hin zu die bezeichnete Öffnung oder Schale
- CLOTH_FILTER: hin zu das Empfangsgefäß
- CELESTIAL_TABLE: hin zu die bezeichnete Zielzelle
- GENERIC_WORKPIECE: hin zu die bezeichnete Arbeitsstelle

Grenze: concrete object must come from owner; root stays short.

## AR — QUELLE

- PLANT_BATCH: her aus der Pflanzenvorrat
- BASIN_STATION: her aus das Quellbecken oder der Einlauf
- CLOTH_FILTER: her aus die obere Tuchseite
- CELESTIAL_TABLE: her aus die bezeichnete Quellzelle
- GENERIC_WORKPIECE: her aus der Ausgangsvorrat

Grenze: concrete object must come from owner; root stays short.

## AIR — LAUF_BAHN

- PLANT_BATCH: entlang der Saft- oder Auszugsweg
- BASIN_STATION: entlang der Flüssigkeitslauf
- CLOTH_FILTER: entlang der Durchgang durch das Tuch
- CELESTIAL_TABLE: entlang die sichtbare Bahn oder das Ringband
- GENERIC_WORKPIECE: entlang der örtliche Arbeitsweg

Grenze: concrete object must come from owner; root stays short.

## OK — ANSETZEN

- PLANT_BATCH: der aktuelle Pflanzenposten ansetzen
- BASIN_STATION: die aktuelle Beckencharge ansetzen
- CLOTH_FILTER: der aktuelle Tuchposten ansetzen
- CELESTIAL_TABLE: der aktuelle Tabellenwert ansetzen
- GENERIC_WORKPIECE: das aktuelle Werkstück ansetzen

Grenze: concrete object must come from owner; root stays short.

## OL — FORTSETZEN

- PLANT_BATCH: der aktuelle Pflanzenposten im selben Gang fortsetzen
- BASIN_STATION: die aktuelle Beckencharge im selben Gang fortsetzen
- CLOTH_FILTER: der aktuelle Tuchposten im selben Gang fortsetzen
- CELESTIAL_TABLE: der aktuelle Tabellenwert im selben Gang fortsetzen
- GENERIC_WORKPIECE: das aktuelle Werkstück im selben Gang fortsetzen

Grenze: concrete object must come from owner; root stays short.

## OT — FOLGEND

- PLANT_BATCH: den folgenden Posten nach der aktuelle Pflanzenposten wählen
- BASIN_STATION: den folgenden Posten nach die aktuelle Beckencharge wählen
- CLOTH_FILTER: den folgenden Posten nach der aktuelle Tuchposten wählen
- CELESTIAL_TABLE: den folgenden Posten nach der aktuelle Tabellenwert wählen
- GENERIC_WORKPIECE: den folgenden Posten nach das aktuelle Werkstück wählen

Grenze: concrete object must come from owner; root stays short.

## OR — ANSATZ_SATZ

- PLANT_BATCH: der Pflanzenansatz
- BASIN_STATION: der laufende Beckengang
- CLOTH_FILTER: der Filteransatz
- CELESTIAL_TABLE: der lokale Tabellensatz
- GENERIC_WORKPIECE: der laufende Arbeitsansatz

Grenze: concrete object must come from owner; root stays short.

## Y — DIESER_POSTEN

- PLANT_BATCH: der aktuelle Pflanzenposten
- BASIN_STATION: die aktuelle Beckencharge
- CLOTH_FILTER: der aktuelle Tuchposten
- CELESTIAL_TABLE: der aktuelle Tabellenwert
- GENERIC_WORKPIECE: das aktuelle Werkstück

Grenze: concrete object must come from owner; root stays short.

## E — KURZ

- PLANT_BATCH: der aktuelle Pflanzenposten kurz
- BASIN_STATION: die aktuelle Beckencharge kurz
- CLOTH_FILTER: der aktuelle Tuchposten kurz
- CELESTIAL_TABLE: der aktuelle Tabellenwert kurz
- GENERIC_WORKPIECE: das aktuelle Werkstück kurz

Grenze: concrete object must come from owner; root stays short.

## EE — LAENGER

- PLANT_BATCH: der aktuelle Pflanzenposten länger
- BASIN_STATION: die aktuelle Beckencharge länger
- CLOTH_FILTER: der aktuelle Tuchposten länger
- CELESTIAL_TABLE: der aktuelle Tabellenwert länger
- GENERIC_WORKPIECE: das aktuelle Werkstück länger

Grenze: concrete object must come from owner; root stays short.

## EEE — VOLL

- PLANT_BATCH: der aktuelle Pflanzenposten vollständig
- BASIN_STATION: die aktuelle Beckencharge vollständig
- CLOTH_FILTER: der aktuelle Tuchposten vollständig
- CELESTIAL_TABLE: der aktuelle Tabellenwert vollständig
- GENERIC_WORKPIECE: das aktuelle Werkstück vollständig

Grenze: concrete object must come from owner; root stays short.

## CLOSE — SCHLUSS

- PLANT_BATCH: den lokalen Arbeitsschritt schließen
- BASIN_STATION: den lokalen Arbeitsschritt schließen
- CLOTH_FILTER: den lokalen Arbeitsschritt schließen
- CELESTIAL_TABLE: den lokalen Arbeitsschritt schließen
- GENERIC_WORKPIECE: den lokalen Arbeitsschritt schließen

Grenze: do not invent an Astro close sign from prose surface spelling.

## CHD — UMSETZEN

- PLANT_BATCH: der aktuelle Pflanzenposten nach der bezeichnete Pflanzenteil oder das Gefäß umsetzen
- BASIN_STATION: die aktuelle Beckencharge nach die bezeichnete Öffnung oder Schale umsetzen
- CLOTH_FILTER: der aktuelle Tuchposten nach das Empfangsgefäß umsetzen
- CELESTIAL_TABLE: der aktuelle Tabellenwert nach die bezeichnete Zielzelle umsetzen
- GENERIC_WORKPIECE: das aktuelle Werkstück nach die bezeichnete Arbeitsstelle umsetzen

Grenze: concrete object must come from owner; root stays short.

## CTH — BEREIT

- PLANT_BATCH: der aktuelle Pflanzenposten bereitstellen
- BASIN_STATION: die aktuelle Beckencharge bereitstellen
- CLOTH_FILTER: der aktuelle Tuchposten bereitstellen
- CELESTIAL_TABLE: der aktuelle Tabellenwert bereitstellen
- GENERIC_WORKPIECE: das aktuelle Werkstück bereitstellen

Grenze: concrete object must come from owner; root stays short.

## CKH — DURCHLAUF

- PLANT_BATCH: der aktuelle Pflanzenposten durch der Saft- oder Auszugsweg führen
- BASIN_STATION: die aktuelle Beckencharge durch der Flüssigkeitslauf führen
- CLOTH_FILTER: der aktuelle Tuchposten durch der Durchgang durch das Tuch führen
- CELESTIAL_TABLE: der aktuelle Tabellenwert durch die sichtbare Bahn oder das Ringband führen
- GENERIC_WORKPIECE: das aktuelle Werkstück durch der örtliche Arbeitsweg führen

Grenze: concrete object must come from owner; root stays short.

## CKHE — TRENNEN

- PLANT_BATCH: der aktuelle Pflanzenposten am Durchgang trennen
- BASIN_STATION: die aktuelle Beckencharge am Durchgang trennen
- CLOTH_FILTER: der aktuelle Tuchposten am Durchgang trennen
- CELESTIAL_TABLE: der aktuelle Tabellenwert am Durchgang trennen
- GENERIC_WORKPIECE: das aktuelle Werkstück am Durchgang trennen

Grenze: concrete object must come from owner; root stays short.

## CHK — WAERMEN

- PLANT_BATCH: der aktuelle Pflanzenposten auf die geforderte Wärme- oder Erhöhungsstufe bringen
- BASIN_STATION: die aktuelle Beckencharge auf die geforderte Wärme- oder Erhöhungsstufe bringen
- CLOTH_FILTER: der aktuelle Tuchposten auf die geforderte Wärme- oder Erhöhungsstufe bringen
- CELESTIAL_TABLE: der aktuelle Tabellenwert auf die geforderte Wärme- oder Erhöhungsstufe bringen
- GENERIC_WORKPIECE: das aktuelle Werkstück auf die geforderte Wärme- oder Erhöhungsstufe bringen

Grenze: concrete object must come from owner; root stays short.

## SHED — ABSETZEN

- PLANT_BATCH: der aktuelle Pflanzenposten stehen oder absetzen lassen
- BASIN_STATION: die aktuelle Beckencharge stehen oder absetzen lassen
- CLOTH_FILTER: der aktuelle Tuchposten stehen oder absetzen lassen
- CELESTIAL_TABLE: der aktuelle Tabellenwert stehen oder absetzen lassen
- GENERIC_WORKPIECE: das aktuelle Werkstück stehen oder absetzen lassen

Grenze: keep celestial example as a teaching paraphrase, not a dictionary promotion.

## SOLK — SAMMELN

- PLANT_BATCH: der aktuelle Pflanzenposten an der bezeichnete Pflanzenteil oder das Gefäß auffangen
- BASIN_STATION: die aktuelle Beckencharge an die bezeichnete Öffnung oder Schale auffangen
- CLOTH_FILTER: der aktuelle Tuchposten an das Empfangsgefäß auffangen
- CELESTIAL_TABLE: der aktuelle Tabellenwert an die bezeichnete Zielzelle auffangen
- GENERIC_WORKPIECE: das aktuelle Werkstück an die bezeichnete Arbeitsstelle auffangen

Grenze: keep celestial example as a teaching paraphrase, not a dictionary promotion.

## HO — EINGANGSPOSTEN

- PLANT_BATCH: Eingangsposten für der Pflanzenansatz
- BASIN_STATION: Eingangsposten für der laufende Beckengang
- CLOTH_FILTER: Eingangsposten für der Filteransatz
- CELESTIAL_TABLE: Eingangsposten für der lokale Tabellensatz
- GENERIC_WORKPIECE: Eingangsposten für der laufende Arbeitsansatz

Grenze: concrete object must come from owner; root stays short.

## CHEO — AUSGABE_AUSZUG

- PLANT_BATCH: Ausgabe aus der Pflanzenansatz
- BASIN_STATION: Ausgabe aus der laufende Beckengang
- CLOTH_FILTER: Ausgabe aus der Filteransatz
- CELESTIAL_TABLE: Ausgabe aus der lokale Tabellensatz
- GENERIC_WORKPIECE: Ausgabe aus der laufende Arbeitsansatz

Grenze: concrete object must come from owner; root stays short.

## KCH — BEARBEITEN

- PLANT_BATCH: der aktuelle Pflanzenposten bearbeiten
- BASIN_STATION: die aktuelle Beckencharge bearbeiten
- CLOTH_FILTER: der aktuelle Tuchposten bearbeiten
- CELESTIAL_TABLE: der aktuelle Tabellenwert bearbeiten
- GENERIC_WORKPIECE: das aktuelle Werkstück bearbeiten

Grenze: concrete object must come from owner; root stays short.

## TY — TEIL

- PLANT_BATCH: Teil von der aktuelle Pflanzenposten
- BASIN_STATION: Teil von die aktuelle Beckencharge
- CLOTH_FILTER: Teil von der aktuelle Tuchposten
- CELESTIAL_TABLE: Teil von der aktuelle Tabellenwert
- GENERIC_WORKPIECE: Teil von das aktuelle Werkstück

Grenze: concrete object must come from owner; root stays short.

## SH — HALTEN

- PLANT_BATCH: der aktuelle Pflanzenposten halten
- BASIN_STATION: die aktuelle Beckencharge halten
- CLOTH_FILTER: der aktuelle Tuchposten halten
- CELESTIAL_TABLE: der aktuelle Tabellenwert halten
- GENERIC_WORKPIECE: das aktuelle Werkstück halten

Grenze: concrete object must come from owner; root stays short.

## CHEEY — SICHTBARES_ERGEBNIS

- PLANT_BATCH: der sichtbare Auszug
- BASIN_STATION: der sichtbare Ablaufzustand
- CLOTH_FILTER: das sichtbare Filtrat
- CELESTIAL_TABLE: der sichtbare Ablesewert
- GENERIC_WORKPIECE: das sichtbare Arbeitsergebnis

Grenze: concrete object must come from owner; root stays short.
