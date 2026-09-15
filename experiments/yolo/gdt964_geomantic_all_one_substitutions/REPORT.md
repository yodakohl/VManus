# GDT964 — Ähnliche ganze Formen tragen keine gemeinsame Elementlesung

**Entscheidung:** Die neue Regel „jede einzelne Zeichenänderung bewahrt die Elementklasse“ trägt keine der sieben bisherigen Gesamtlesungen über alle drei Transkriptionen. Sie wird nicht zur allgemeinen Wortregel erweitert. GDT957 und GDT959 bleiben unverändert; ihre engeren Hypothesen sind dadurch nicht rückwirkend widerlegt.

## Vollständige Konsequenzen

Öffentlich registriert in `cfe691913` vor der vollständigen Kandidatenprüfung. [PREDICTIONS.tsv](artifacts/PREDICTIONS.tsv) enthält alle16.920 Positionsvorhersagen:15 unveränderte Namen und Elementwerte für jeden der1.128 Fälle. [CANDIDATE_TABLE.tsv](artifacts/CANDIDATE_TABLE.tsv) berichtet jeden Kandidaten mit altem und neuem Status; [EDGE_CONSEQUENCES.tsv](artifacts/EDGE_CONSEQUENCES.tsv) enthält alle4.224 tatsächlich geprüften Paarfolgen mit beiden Namen und Elementen.

Alle105 ungeordneten Positionspaare pro Transkription wurden berücksichtigt. Bei bekannten vollständigen Rohwörtern gilt die Relation genau bei gleicher Länge und einer unterschiedlichen ASCII-EVA-Position. Unbekannte Zeichen werden nicht ergänzt; weder Einfügung noch Löschung oder Teilstringähnlichkeit zählt.

| Transkription | Tatsächliche Beziehungen | Unklare Paare | Keine Beziehung |
|---|---|---:|---:|
| ZL3b | rary/dary, rary/fary, dary/fary, saly/salf |27|74|
| IT2a | rary/fary |0|104|
| RF1b | rary/fary, sals/saly, sals/salf, saly/salf |27|74|

IT2a liest `syly`, daher entsteht dort keine neue Bedingung gegenüber GDT959. Das RF1b-Dreieck an Positionen2/6/7 ist zwingend vollständig zu prüfen. Das Weglassen von `sals` würde ein günstigeres Ergebnis erzeugen und ist nicht erlaubt.

Über sämtliche ursprünglichen Populationen ergeben sich **1.102 widersprochene Fälle,16 Fälle mit passenden bekannten Kanten und10 nur mit unbekannter Quellenzuordnung mögliche Fälle**. Die18 nach Edition/Richtung/Tabelle getrennten Populationen stehen in [SUMMARY.tsv](artifacts/SUMMARY.tsv). Die26 lokal verbliebenen Fälle identifizieren keine gemeinsame Lesung.

## Alle sieben vorherigen Gesamtlesungen

Die vollständigen15 Namen pro Kandidat bleiben in den Vorhersagen und [PREVIOUS_SEVEN.json](artifacts/PREVIOUS_SEVEN.json) nachlesbar. Hier stehen die neuen, unterscheidenden Konsequenzen; sämtliche zusätzlichen Konflikte enthält die Kantentabelle.

| Richtung / Schlüssel / Tabelle | ZL3b | IT2a | RF1b | Konkreter Widerspruch |
|---|---|---|---|---|
| TOP_DOWN18557 B | Widerspruch | passt | Widerspruch | saly/salf: Puella AIR / Albus EARTH |
| TOP_DOWN18621 B | passt | passt | Widerspruch | RF sals/saly: Laetitia AIR / Carcer EARTH |
| BOTTOM_UP18557 C | passt | passt | Widerspruch | RF sals/saly: Via WATER / Amissio FIRE |
| BOTTOM_UP18663 A | Widerspruch | Quellenwert unklar | Widerspruch | saly/salf: Carcer EARTH / Fortuna minor FIRE |
| BOTTOM_UP27441 A | Widerspruch | Quellenwert unklar | Widerspruch | saly/salf: Albus AIR / Puer FIRE |
| BOTTOM_UP31011 C | Widerspruch | passt | Widerspruch | saly/salf: Tristitia EARTH / Cauda draconis FIRE |
| BOTTOM_UP48658 A | Widerspruch | Quellenwert unklar | Widerspruch | saly/salf: Fortuna major FIRE / Acquisitio WATER |

Damit bleiben in ZL3b unter den vorherigen sieben zwei klare Rivalen: TOP_DOWN18621 B und BOTTOM_UP18557 C. RF1b widerspricht beiden. Das zeigt eine Transkriptionsabhängigkeit; es erlaubt weder die Wahl von ZL3b wegen des Ergebnisses noch die universelle Widerlegung einer alternativen Transkription. Sämtliche96 vollständigen IT2a-Schlüssel/Tabellen-Verknüpfungen zu den anderen Editionen wurden geprüft. Keine hat eine gemeinsame untere oder obere Lösung, auch nicht mit einer einzigen konsistenten Ergänzung des unbekannten A-Quellenwerts.

## Mehrdeutigkeit, Exposition und Prüfung

Alle1.128 vollständigen Namensvorhersagen bilden [312 identische physische Vorhersagegruppen](artifacts/IDENTICAL_PHYSICAL_PREDICTIONS.json). Die tatsächlich geprüften Elementkanten bilden [769 Beobachtungsgruppen](artifacts/IDENTICAL_OBSERVED_PREDICTIONS.json). Namen außerhalb dieser Kanten kann dieser Test nicht unterscheiden; ein bestandener Klassenzwang wäre keine Bestätigung der vollständigen Namen.

Die Hypothese ist ausdrücklich nach Kenntnis von GDT959 entstanden. Root bemerkte `saly/salf` und korrigierte eine anfänglich falsche Elementvermutung anhand der eingefrorenen Quelle. Der separate Reviewer berechnete vor Veröffentlichung Positionsquoten; dessen zunächst nicht umgekehrte BOTTOM_UP-Zählung ist im Audit als ungültiger Pilot erhalten und korrigiert. Sie floss nicht in den Runner ein. Auch der Source-only-Validator berechnete vor Veröffentlichung bereits die Paaranzahlen. Somit wird keine Blindheit behauptet. Die öffentliche Registrierung fixierte die gesamte Regel, alle Vorhersagen, Kandidaten und Daten vor der vollständigen Auswertung.

Der unabhängige Validator rekonstruiert957-Charts und Richtungen, alle16.920 Vorhersagen,315 Paare,1.128 Kandidaten,4.224 Kantenfolgen, sämtliche Aggregationen und beide Gruppierungen. **VALIDATION_PASS**, bezogen auf Daten und Rechnung. Die historische Grundlage sind weiterhin die drei rivalisierenden Tabellen der späten [Turner-Fassung1655](https://www.princeton.edu/~ezb/geomancy/agrippa.html); ihre Anwendung um1420 ist nicht belegt. Die unklare Form Amitia wurde nicht still zu Amissio normalisiert.

Ein schon exponiertes physisches Blatt; **0 unabhängige Bestätigungsblätter und0 bestätigte Wörter**. Reserven einschließlich f84/f84r blieben geschlossen. Keine geeignete Gegenkontrolle der gesamten Suche, daher keine Signifikanzbehauptung. Kein GDT388-PASS und keine Element-, Pflanzen- oder Wortbedeutung abgeleitet. Eine weitere Ähnlichkeitsradius-, Transkriptions- oder Elementtabellen-Reparatur folgt nicht. Der nächste Arbeitszweig untersucht eine konkrete Bild- und Textfolge aus vollständigen Pflanzenbeschreibungen.
