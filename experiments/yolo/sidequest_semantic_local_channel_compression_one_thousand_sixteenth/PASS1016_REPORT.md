# Pass 1016 — vier lokale Kanäle statt neunzehn lokaler Wörter

## Ergebnis

Die 19 lokalen Zeichen sind keine 19 zusätzlichen Wörter. Für einen Werkstattschreiber genügen vier kurze Bedeutungen:

1. **LOCAL_PLACE = HIER** — wähle die lokal bezeichnete Stelle;
2. **LOCAL_INDEX = VARIANTE** — nimm die lokal markierte Ausführung;
3. **LOCAL_CLASS = KLASSE** — übernimm die lokale Stoff-/Zusatzklasse;
4. **LOCAL_REFERENCE = VORBEZUG** — nimm den vorausgesetzten lokalen Bezug wieder auf.

Die 46 sichtbaren Zeichenformen bleiben unverändert. Semantisch muss der Lehrling aber nur noch **19 portable Kerne + 8 Kontrollen + 4 lokale Kanäle = 31 Kategorien** lernen.

## Warum diese Kürzung funktioniert

- **LOCAL_PLACE** trägt 473 von insgesamt 527 lokalen Zeichenbeiträgen. Das ist der eigentliche lokale Mechanismus.
- `D_ADDR` ist der flexible Standardselektor; `AM_ADDR` steht 50/59-mal am Ereignisende, `S_ADDR` 12/13-mal. Das sind Positionsvarianten desselben HIER-Kanals, keine eigenen Ortswörter.
- **LOCAL_INDEX** sammelt die seltenen G/I/B/J/Z-Kennungen. Sie wählen eine Variante, ohne automatisch *eins, zwei, unten, prüfen* oder *verbinden* zu bedeuten.
- **LOCAL_CLASS** hat eine klare Schreibsyntax: `HO` steht 16/16-mal am Beginn seines Ereignisses, `AN` 7/7-mal am Ende. Beide markieren KLASSE, aber an entgegengesetzten Rändern.
- **LOCAL_REFERENCE** ist der kleine Vorbezugsrest: `OS` setzt den lokalen Bezug, die einmalige Wiederaufnahmekarte greift ihn wieder auf.
- Drei Formen (`S_LABEL`, `Z_ADDR`, `LOCAL_CHAR_Z`) sind im laufenden Text nicht aktiv. Sie bleiben reservierte lokale Exemplarzeichen, nicht drei Wörter ohne Beleg.

## Die neue Schreibregel

Ein unbekannter seltener Buchstabenteil bekommt nicht sofort einen Stoff- oder Tätigkeitsnamen. Der Schreiber fragt zuerst:

> **Wählt er einen Platz, eine Variante, eine Klasse oder einen Vorbezug?**

Erst das Bild oder die Tabelle füllt den lokalen Wert: Wurzelteil, Beckenrand, Sternposition, Gefäßgruppe, Paarvariante und so weiter. Das konkrete Substantiv gehört dem Besitzer, nicht dem Zeichen.

## Kompositionsvorhersagen

- Ein neuer D/A/AM/S/F/M/Z-artiger Einschub wird als **HIER** gelesen.
- Ein neuer G/I/B/J/Z-Mikrocharakter wird als **VARIANTE** gelesen.
- Eine HO-artige Vorsilbe oder AN-artige Endung wird als **KLASSE** gelesen.
- Eine alleinstehende OS-/Wiederaufnahmeform wird als **VORBEZUG** gelesen.
- Erst wenn eine Form diese vier Rollen wiederholt verletzt, darf ein neues lokales Wort erwogen werden.

## Wirkung auf die Gesamtausgabe

Alle **627 Aussagen / 3.888 Gruppen** bleiben bytegleich in Oberfläche, Reihenfolge, Besitzer, Handlung, Grad und Ende. **210 Aussagen** enthalten mindestens einen lokalen Kanal. Ihre Pass-1015-Lesung bleibt erhalten; die neue Ausgabe ersetzt lediglich die Liste scheinbarer lokaler Wörter durch die vier Kanäle.

Damit ist der nächste Engpass kleiner: Nicht 46 Bedeutungen müssen auf weiteren Seiten halten, sondern 31 Kategorien. Die 15 übrigen Unterschiede sind grafische Auswahlvarianten innerhalb der vier lokalen Kanäle.
