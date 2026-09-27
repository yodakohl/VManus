# GDT1051 — die vorhandene Wortstruktur tatsächlich angewandt

27. September 2026. **Der vorige f89v1-Vergleich nutzte die Wortgrammatik als
bekannte Einschränkung, führte sie aber nicht aus.** Sein Validator prüfte
rohe ganze Gruppen und Nachbarpaare. Diese Korrektur wendet nun zwei bereits
vorhandene, unveränderte formale Zerlegungen auf **alle** gespeicherten Gruppen
der beiden f68r2-Ringe und des gesamten Absatzes f89v1.13–20 an. Sie liefert
keine neue Wortbedeutung.

## Vollständiger Lauf und konkrete Unterscheidung

Sechs Ringzeilen und24 Absatzzeilen in drei alternativen Lesungen enthalten
58+230=288 Quellgruppen.269 reine Buchstabengruppen sind zerlegbar,19
editoriell markierte bleiben unaufgelöst. Die bekannten kleinen unsicheren
Abstände ergeben279 harte Chunks;260 sind mit den unveränderten64 GDT605-
Merges zerlegbar. Jeder Ausgangseintrag, sein Abstand und jede Ablehnung
stehen in [RESULT.json](artifacts/RESULT.json); es gibt keinen herausgegriffenen
Treffer oder nachträglich gelöschten Buchstaben.

| Gleiche exakte Form in allen drei Lesungen | GDT012/062-Vorstufe: Wrapper + Host vor O/OT-Stufe + rechte Familie | GDT605: fertige Einheiten |
|---|---|---|
| `okoaiin`, Ring f68r2.31 und Absatz f89v1.14 | NONE + `oko` + `aiin` | `ok · o · aN` |
| `okaiin`, f89v1.16 | NONE + `ok` + `aiin` | `okaN` |
| `qokaiin`, f89v1.16 | `q` + `ok` + `aiin` | `qokaN` |
| `chokaiin`, f89v1.18 | `ch` + `ok` + `aiin` | `C · okaN` |

`aN` ist die alte Kollaps-/Merge-Bezeichnung für sichtbares `aiin`; `C`
steht in dieser Darstellung für `ch`. Die Einheiten sind gelernte
Schriftbausteine, keine übersetzten Morpheme. Im GDT062-Modell teilen drei
Formen den formalen Host `ok`; `okoaiin` hat **`oko`**. Sein zusätzliches
`o` liegt also innerhalb des modellierten Hosts. Die GDT605-Zerlegung
bestätigt die bloße Gruppierung nicht identisch: zwei Formen sind dort ganze
gelernte Merge-Einheiten, eine hat ein vorangestelltes `C`, und `okoaiin`
bleibt dreiteilig. GDT608 belegt gerichtete Verwendung solcher Teile,
zugleich aber wesentliche Information der exakten Gesamt-Merge und besonders
heterogenes Verhalten von `o`-Verbindungen.

Die alte GDT062-Inventarliste hatte `okoaiin`, `qokaiin` und `okaiin` an den
aktuellen f89v1-Stellen bereits genau so erfasst. Sie deckt die aktuelle
Zeile mit `chokaiin` nicht ab. Die alte pure Zerlegungsfunktion ist darauf
hier auf den vollständigen Absatz angewandt. Das ist eine verbesserte
Nutzung bestehender Erkenntnisse, keine Entdeckung einer neuen Wortregel.

## Konsequenz für den scheinbaren Sonnen-/Mond-Kontrast

Die zweite Rohgruppe des oberen Rings ist bei ZL3b `ok[a:?]r` und bleibt
deshalb ungeklärt; RF1b liest `okar`, IT2a `okor`. Unten steht in allen
drei `okoaiin`. Der formale Vergleich ist somit:

| Lesung | Oberer Ring | GDT012/062 | GDT605 | Unterer Ring |
|---|---|---|---|---|
| ZL3b | `ok[a:?]r` | offen | offen | `oko + aiin` / `ok · o · aN` |
| IT2a | `okor` | `okor` + NONE | `ok · or` | `oko + aiin` / `ok · o · aN` |
| RF1b | `okar` | `ok` + `ar` | `ok · ar` | `oko + aiin` / `ok · o · aN` |

Unter den eingefrorenen GDT062-Regeln ist `okor` **nicht** `ok+or`: `or`
gehört nicht zu dessen rechter Fünferliste. GDT915 verwendet für seine
eigenen bekannten r/l-Zweierfamilien wiederum eine andere Abtrennung.
Diese Parser dürfen nicht zu einem behaupteten universellen Morphembaum
vereinheitlicht werden. Vor allem ergibt sich aus dem Ringvergleich keine
gesicherte Eins-zu-eins-Ersetzung für „Sonne“ und „Mond“.

## Entscheidung und Grenze

Eine Lesung, die `okoaiin`, `okaiin`, `qokaiin` und `chokaiin` als einfache
Schreibvarianten **mit identischem Stamm ohne Rest** behandelt, verwirft
Information, die beide vorhandenen Strukturmodelle behalten. Die sparsamere
formale Beschreibung lautet: ein gemeinsamer rechter Komplex ist möglich;
Wrapper `q`/`ch`, exakter Host `ok`/`oko`, Gesamtform und Schreibkontext
müssen getrennt erhalten bleiben. Das ist eine Anforderung an eine künftige
inhaltliche Hypothese, kein Beweis verschiedener oder gleicher Bedeutungen.

GDT282/286/318 zeigten bereits übertragbare Wrapper- und
Positionszusammenhänge; sie identifizieren weder `q` noch `ch` als Kasus
oder Handlungsart. GDT326 scheiterte an freier neuer Host-Koordinaten-
Kombination; GDT915s bekannte r/l-Familien übertragen sich nicht automatisch
auf neue Stamm-Paare (GDT916). [Gezielte Primärprüfung](../../../research_registry/proposals/laufenberg_f85r2_20260926/WORD_GRAMMAR_PREDECESSOR_AUDIT_20260927.md)
hält die Einzelfälle und Gegenbeispiele fest.

`okoaiin = SONNE` bleibt eine **unbestätigte** Arbeitslesung. Sie wird durch
die Struktur weder widerlegt noch gegenüber den Alternativen bevorzugt.
GDT815 hatte `okaiin` ebenfalls nicht semantisch identifiziert; keine der
alten `okaiin`-Glossen wird auf `okoaiin` übertragen. Der
nächste bedeutungstragende Vorschlag müsste erklären, warum gerade `oko`
in beiden Ring- und Arzneistellen auftritt, wie er sich zu `ok+aiin` verhält
und welche konkrete, anders erwartete Textfolge daraus entsteht. Eine
solche Regel wurde hier nicht geraten oder nachträglich gebaut.

Der [Validator](src/validate.py) bestätigt die komplette formale Wiedergabe,
alle unveränderten Eingaben und die vier fokalen Zerlegungen. Er bestätigt
keine historische Wortbedeutung. Alle drei Transkriptionen gehören zu einer
Handschrift. Keine neue Bild- oder Seitenzulassung, kein Reservegebrauch,
keine Signifikanzbehauptung; bestätigte übersetzte Wörter: **0**.
