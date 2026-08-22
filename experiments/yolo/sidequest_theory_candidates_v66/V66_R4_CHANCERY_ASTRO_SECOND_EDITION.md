# V66 R4 — Korrektorische Astro-Zweitausgabe

Status: vollständige kreative Diagrammedition; keine Entzifferung.

## Auswahl

Die drei Seiten sind besser als **drei selbständige Nachschlageinstrumente**
denn als fortlaufender Text zu lesen:

```text
f67r2  7×12 Konfigurations- und Auswahlrahmen
f68r1  Zentrum plus 28 räumliche Stationsadressen
f69v   unabhängiger zyklischer Katalog aus 28 Arbeitsregeln
```

Die iatromathematische Defaultfüllung bleibt konkret: sieben klassische
Himmelsregenten, zwölf Tierkreisbereiche, medizinische Wahlbedingungen,
Mondstationsadressen und Regeln für Bad, Waschung, Salbung, Ruhe, Sieben,
Dosieren, Wiederholen oder Aussetzen. Diese Werte gehören zum historischen
Exemplar, nicht zu den sichtbaren Gruppen.

## Vollständige Lesung

**f67r2:** Wähle einen der sieben Regenten, einen der zwölf Bereiche und die im
Sektor notierte Bedingung. Entscheide damit, ob eine geplante Waschung,
Arzneigabe, Ruhe, Entleerung oder örtliche Anwendung ausgeführt, gemildert oder
verschoben wird. Weitere Zwölfer- und Achterfelder kontrollieren den Fall.

**f68r1:** Das Zentrum ist im Default der Mond als Katalogbesitzer. Die 28
äußeren Orte sind räumliche Adressen. Der Benutzer erkennt eine Station an der
gezeichneten Lage und ruft ihre örtlich gelernte Bezeichnung auf. Die Seite
liefert keine sichtbare erste Station.

**f69v:** Die drei Kreistextbänder geben die Bedienung an. Die 28 radialen
Plätze enthalten je eine lokale Regel, etwa warm baden, kühl waschen, salben,
ruhen, keine Entleerung vornehmen, Flüssigkeit abziehen, einmal nachspülen oder
eine Anwendung verschieben. Das ist ein Regelkatalog, keine Übersetzung in 28
englische oder deutsche Wörter.

Alle 395 Gruppen und 142 Loci behalten in den TSVs eine vollständige lokale
Defaultlesung. Keine Gruppe bleibt bedeutungsleer; zugleich wird jede als
`LOCAL_DIAGRAM_MNEMONIC_NOT_WORD_TRANSLATION` gekennzeichnet.

## Korrektorische Hauptentscheidung

Gleiche 28er-Zahl ist kein Indexschlüssel. Für f68r1 und f69v sind jeweils 28
Rotationen in zwei Richtungen sichtbar gleichwertig. Ohne extern bekannten
Start und Laufrichtung existieren 56 redaktionelle Orientierungen pro Seite.
Ein f68-Ort und eine f69-Regel werden daher **nicht** über ihre moderne Nummer
verbunden.

Die stärksten Rivalen bleiben:

- f67r2 als allgemeine 7×12 Qualitäts-/Arbeitsmatrix;
- f68r1 als räumlicher Stern- oder Stationskatalog ohne medizinische Regel;
- f69v als 28-stufiger Werkstatt- oder Kalenderplan ohne Himmelssemantik.

Kein Diagramm übernimmt eine Prosa-Karte, einen GDT327-Tuplewert oder ein
Herbal-/Biological-Wort. Die gemeinsame WHAT/HOW/WHEN-Idee bleibt nur eine
Bibliotheks- und Benutzungshypothese.

## Artefakte

- `V66_R4_395_GROUP_ASTRO_LEDGER.tsv`
- `V66_R4_142_LOCUS_READINGS.tsv`
- `V66_R4_3_DIAGRAM_EDITIONS.tsv`
- `V66_R4_ORIENTATION_ALTERNATIVES.tsv`
- `V66_R4_VALIDATION.json`

Der Validator prüft 395 Gruppen, 142 Loci, die drei Seitenpartitionen,
vollständige lokale Defaults, fehlende Crosspage-Identität und versiegelte
Seiten.
