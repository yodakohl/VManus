# GDT510 — Die vier registerfremden Karten bekommen lokale Bauteile

Status: `CELESTIAL_PCH_HAS_LOCAL_SUFFIX__THREE_SCHD_TARGETS_HAVE_LOCAL_HEAD_ARGUMENT_RECTANGLES`

## Ergebnis

GDT509 ließ vier von elf Paarübersetzungen vollständig auf einem Träger aus
einem anderen Register ruhen. Dieser Pass findet für alle vier etwas im
jeweiligen Zielregister, ohne ihre Bedeutungen umzuschreiben.

Das stärkste neue Stück ist Celestial `P+CH+E+Y`. Auf f67r2 enthält
`G407-E0966` die Folge nicht nur als lose Sammlung von Wurzeln, sondern als
exakten zusammenhängenden Suffix:

`Y+T+O+E+O + P+CH+E+Y`

Nach Entfernung des sichtbaren Präfixes bleibt genau die GDT509-Zielkarte. Ihre
Arbeitsübersetzung bleibt:

> Setze den Positionsposten ein und nimm den Positionsposten auf; auf Grad I.

Für `S+CHD+Y` gibt es in allen drei Zielregistern lokale `S`-auf-`Y`- und
`CHD`-auf-`Y`-Zeugen:

| Register | `S` auf `Y` | `CHD` auf `Y` | mögliche Rechtecke | gewählte Zeugen |
|---|---:|---:|---:|---|
| Celestial | 6 | 4 | 24 | `G407-E1243` + `G407-E1408` |
| Pharma | 17 | 2 | 34 | `G407-E3999` + `G407-E4028` |
| Source | 4 | 1 | 4 | `G407-E0079` + `G407-E0102` |

Alle sechs gewählten Kopfzeugen sind alte
`CROSS_PAGE_ACTION_FACTORS_COMPLETE`-Fälle und stimmen im laufenden Reader mit
dem Referenzzustand überein. Alle drei Paare liegen auf derselben Seite; Pharma
und Source teilen zusätzlich denselben Besitzer, Source sogar dieselbe
Anweisung. In allen drei gewählten Paaren steht `S` vor `CHD` im Strom.

## Was sich dadurch verbessert

Die elf GDT509-Zielkarten besitzen jetzt sämtlich irgendeinen Baustein im
eigenen Register. Die vier alten „nur fremdes Register“-Karten teilen sich nun
in zwei Mechanismen:

- eine echte lokale Suffixreduktion für Celestial `P+CH+E+Y`;
- drei lokale Kopf-/Argument-Rechtecke für `S+CHD+Y`, kombiniert mit dem alten
  gerichteten Biological-Träger `G407-E1883`.

Das macht die Arbeitsübersetzungen kompositionell weniger fremd: Die benötigten
Handlungen und der benötigte Postentyp sind nicht bloß anderswo im Manuskript
bekannt, sondern auch dort vorhanden, wo die hypothetische Karte gelesen würde.

## Was ausdrücklich offen bleibt

Keine der vier nackten Zielkarten kommt vor. Ein Paar aus zwei getrennten
Ereignissen ist kein gefundenes Ganzwort, und das celestiale Suffix bleibt Teil
einer längeren Drei-Aktions-Karte. Deshalb ändern sich weder die vier deutschen
Sätze noch ihre Einstufung `COMPOSED_WORKING`.

Der unabhängige Validator rekonstruiert 27 lokale `S`-auf-`Y`-Fälle, sieben
`CHD`-auf-`Y`-Fälle, 62 Rechteckkombinationen und den einzelnen Suffixträger
direkt aus den 4.576 Klauseln; 189/189 Prüfungen bestehen.

## Nächster Arbeitsgriff

Nicht noch mehr bloße Rechtecke sammeln. Der nächste sinnvolle Pass soll die
drei `S+CHD+Y`-Register nach der stärksten bereits sichtbaren lokalen
Verknüpfung ordnen: gleiche Anweisung, gleicher Besitzer, unmittelbare
Nachbarschaft oder wiederkehrendes Rahmenmuster. Ziel ist eine feinere
Übergangsstufe zwischen „beide Köpfe lokal“ und „das ganze Paar lokal“, ohne
die Zielkarte als beobachtet auszugeben.
