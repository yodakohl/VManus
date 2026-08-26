# GDT511 — Wie eng hängen die lokalen `S`- und `CHD`-Bauteile wirklich zusammen?

Status: `SOURCE_SAME_STATEMENT__PHARMA_SAME_OWNER_PAGE__CELESTIAL_SAME_PAGE__ZERO_IMMEDIATE_OR_Y_CONTINUOUS`

## Ergebnis

GDT510 zeigte, dass alle drei Zielregister sowohl `S` auf `Y` als auch `CHD`
auf `Y` besitzen. GDT511 betrachtet nun nicht drei ausgewählte Beispiele,
sondern alle 62 möglichen Kombinationen.

| Register | alle Rechtecke | `S→CHD` | gleiche Seite | gleicher Besitzer | gleiche Anweisung |
|---|---:|---:|---:|---:|---:|
| Celestial | 24 | 21 | 5 | 0 | 0 |
| Pharma | 34 | 21 | 3 | 1 | 0 |
| Source | 4 | 4 | 4 | 1 | 1 |
| **Gesamt** | **62** | **46** | **12** | **2** | **1** |

Die gewünschte Reihenfolge ist also häufig, wenn jede beliebige Stelle im
Register mit jeder anderen kombiniert wird. Die räumlich-textuelle Verbindung
wird jedoch schnell dünn. Kein Kandidat ist unmittelbar, keiner hat nur eine
Zwischenkarte, und in keinem der drei Zielregister steht `S>CHD` innerhalb
einer einzelnen Karte.

## Die stärksten drei lokalen Griffe

### Source: gleiche Anweisung

`G407-E0079 → G407-E0102` liegt im selben f1r-Textblock und in derselben
Anweisung. Das ist die stärkste lokale Stufe. Zwischen den Köpfen stehen aber
22 Karten. Der aktive Argumentlauf lautet:

`Y>AIN>Y>AIIN>Y>AIIN>Y>AIIN>Y>AIN>AIIN>AIN>Y`

`Y` bezeichnet an beiden Enden denselben Argumenttyp, wird im Korridor aber
mehrfach durch ANTEIL und WERT abgelöst. Das ist kein fortgesetzter Bezug auf
denselben Posten.

### Pharma: gleicher Besitzer und dieselbe Seite

`G407-E3999 → G407-E4028` liegt auf f88v in derselben zweiten
Gefäß-/Zutatengruppe, aber über vier Anweisungen und 28 Zwischenkarten. Der
Argumentlauf ist:

`Y>AIIN>Y>AIIN>Y>AIIN>Y>AIN>Y`

### Celestial: nur dieselbe Seite

Der kürzeste seitenlokale Griff ist `G407-E1243 → G407-E1276` auf f72r. Er
überschreitet bereits den Besitzer von Tierkreis-Ringgruppe D zu E, umfasst
zwei Anweisungen und 32 Zwischenkarten. Der Argumentlauf ist:

`Y>AIIN>Y>AIIN>Y>AIIN>Y>AIIN>Y>AIIN>Y`

Das ist schwächer als der in GDT510 wegen seiner sauberen Restframes gewählte
Zeuge `G407-E1243 → G407-E1408`, aber näher. Beide Sichtweisen bleiben im
Atlas erhalten: GDT510 minimiert fremde Rahmenatome, GDT511 maximiert lokale
Verknüpfung.

## Vergleich mit GDT507

Die dreizehn GDT507-Brücken sind unmittelbare Kartenfolgen im selben Satz und
tragen dasselbe geerbte Argument ohne Unterbrechung. Von den 46 gerichteten
`S→CHD`-Rechtecken erreicht kein einziges diese Form. Auch kein weiterer
Korridor hält `Y` durchgehend aktiv.

Die passende Lesart lautet deshalb nicht „lokales Paar gefunden“, sondern:

- Source: langes Kopf-Inventar in derselben Anweisung;
- Pharma: langes Kopf-Inventar beim selben Besitzer;
- Celestial: langes Kopf-Inventar auf derselben Seite;
- die eigentliche Paarordnung bleibt durch Biological `G407-E1883 =
  S+OL+CHD+Y` getragen.

## Konsequenz für die Übersetzungen

Die drei Sätze bleiben als explorative Standardkompositionen stehen:

- „Wähle den Positionsposten und bearbeite den Positionsposten.“
- „Wähle den Drogenposten und bearbeite den Drogenposten.“
- „Wähle den laufenden Eintrag und bearbeite den laufenden Eintrag.“

GDT511 verwirft sie nicht, verhindert aber eine zu starke Begründung: lokal
sind die Köpfe und der Argumenttyp, nicht die fertige Paarfolge. Alle nackten
Zielrezepte bleiben unbelegt. Der unabhängige Validator rekonstruiert alle 62
Kandidaten und alle 88 Ereignisse der drei ausgewählten Korridore; 1.700/1.700
Prüfungen bestehen.

## Nächster Arbeitsgriff

GDT509 ist durch GDT510–511 nun in einem Punkt veraltet: Seine vier
„cross-register-only“-Karten haben lokale Faktoren, aber von sehr
unterschiedlicher Stärke. Der nächste Pass soll deshalb keine weitere Ferne
absuchen, sondern die elf Paarübersetzungen einmal neu in ehrliche Stufen
setzen—lokaler Rahmen, unmittelbare Kontextfolge, Paketwiederholung, exakter
Suffix und die drei langen Kopf-Inventare. Danach ist diese Paarfront fertig.
