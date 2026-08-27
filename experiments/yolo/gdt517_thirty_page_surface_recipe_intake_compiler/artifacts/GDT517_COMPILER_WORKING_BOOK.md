# GDT517 — Kompakte Compiler-Arbeitsbasis

## Der neue Normalweg

```text
sichtbare Form
  -> bekannte Ereigniskarte?       ja: exaktes Rezept/Paket
  -> bekannte Oberfläche+Rolle?    ja: endliche Rezeptoption
  -> sonst Stückcompiler           Rang 1 + Alternativen
  -> Rollenprüfung
  -> bei Prose: zustandsabhängige Ausführung
```

Keine kachelbare Form darf ohne Default bleiben. Der Default ist eine
Arbeitsentscheidung, keine bestätigte Übersetzung.

## Bestand

- alt trainiert: 4.576 Ereignisse, 1.558 Oberflächen;
- alte Stücktafel: 4.403 Formen, 5.555 Kandidaten;
- Rücklauf: 159/159 zerlegt, 117 Rang 1, 157 Top 5;
- aktuelle laufende Basis: 5.122 Ereignisse, 1.711 Oberflächen;
- aktuelle Stücktafel: 4.783 Formen, 5.999 Kandidaten;
- exakte 30-Seiten-Karten: 5.866;
- kompakte Oberflächen-/Rollenoptionen: 2.243;
- ausgewählter Textstrom: 546 Karten, null verbleibende Stopps.

## Markante Stücke

```text
q    -> CARRIER_Q             147/150
i    -> LOCAL_CHAR_I           47/56
eee  -> EEE                    58/61
dy   -> DY                    491/847
dy   -> D_ADDR+Y              175/847
dy   -> Y                     152/847
```

`dy` bleibt kontextabhängig. `x -> LOCAL_X` und `c -> LOCAL_C` gelten nur im
f66r-Lokalregister; im allgemeinen Compiler bleibt `c -> CH` verfügbar.

## Zwei tiefe Fälle

- `aiicthy`: aktuelles Rezept
  `A_ADDR+LOCAL_CHAR_I+LOCAL_CHAR_I+CH+T+Y`, alter Compiler-Rang 6;
- `dalcheeeky`: aktuelles Rezept `AL+CH+EEE+K+Y`, alter Compiler-Rang 56.

Bei bekannten 30-Seiten-Ereignissen ist das folgenlos, weil die exakte Karte
vor dem Compiler gewinnt. Für neue Seiten sollen Nachbarn und Rolle diese
Rangfolge verbessern.

## Endliche lokale Doppeloptionen

Nur diese neun Oberfläche-/Domänenpaare haben im aktuellen Index zwei Rezepte:

```text
cheody  CH+E+O+Y | CHEO+Y
d       D_ADDR | SECTION_MARKER
doly    LOCAL_LABEL_PACKAGE::G473-E162 | LOCAL_NAME_CORE_D+OL+Y
l       L | SECTION_MARKER
o       O | SECTION_MARKER
okeal   LOCAL_LABEL_PACKAGE::G473-E064 | OK+E+AL
okealar LOCAL_LABEL_PACKAGE::G473-E052 | OK+E+AL+AR
r       R | SECTION_MARKER
s       S | SECTION_MARKER
```

Die Ereigniskarte beziehungsweise sichtbare Rolle entscheidet; es gibt keinen
globalen Zwang auf eine der beiden Lesarten.

## Sieben besondere Ausführungskarten

- `shtchy`: alte gelbe Lesung bleibt;
- `qotedy`, `otedy`, `oteedy`: lesbare Adresscontainer;
- `axor`, `chxar`: lokale Namensschalen, keine Aktionsstopps;
- `shso`: einmalige gelbe Direktpaarlesung `SH>S`.

## Nächster Hebel

Die 42 alten Rang-1-Abweichungen nach Nachbarschaft, Besitzer und Kartenrolle
neu ordnen. Dabei bleiben die aktuellen Rezepte die Basis; neue Seiten sind
dazu nicht nötig.
