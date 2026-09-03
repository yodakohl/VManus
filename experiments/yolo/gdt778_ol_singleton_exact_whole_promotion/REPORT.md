# GDT778 — exakte Ganzwort-Promotion des alten Singleton-Decks nach `ol`

Status: `PASS__39_EXACT_WHOLES__32_FALLBACK_REPLACEMENTS__5_SHARPENINGS__2_CONFIRMATIONS__195_CONTEXTUAL__155_CONSUMED__NO_COMPONENT_EXPORT`.

## Ergebnis

Die occurrence-ID-freie Regel prüft alle 376 Positionen des finalen GDT777-
Renderers und nimmt **jedes** Vorkommen auf, dessen vollständiges rechtes Wort
im festen 29er-Deck steht und reader-exakt ist. Das ergibt **41** rohe
Kandidaten und **39** exakte `ol + Ganzwort`-Spannen auf **31** Seitenlabels
und **25** physischen Folios. Nur `keey` bei `G769-T0284` und `dal` bei
`G769-T0391` fallen wegen nicht-exakter rechter Lesung aus.

Von den 39 exakten Fällen ersetzen **32** den generischen Fallback. Fünf
vorhandene Strukturwerte werden tatsächlich konkreter: `ar` einmal, `kain`
zweimal und `chy` zweimal. Die zwei `chol`-Stellen bestätigen dagegen nur das
schon vorhandene `Zustand: trocken` und werden nicht als Verbesserung gezählt.
Damit steigt die kontextuelle Abdeckung **163→195**, während die Fallbacks
**213→181** fallen. Die Passage-Tabelle enthält genau die **37** wirklich
veränderten Anzeigen.

## Strukturtreue Komposition

- `f104v.33`: `ol ar` — `und` → **und; Anteil** (`CONTEXTUAL_SHARPENING`).
- `f80v.35`: `ol kain` — `und` → **und; erhitzte Form II** (`CONTEXTUAL_SHARPENING`).
- `f78v.4`: `ol chy` — `Ansatz: trocken am Anfang des Grades` → **Ansatz: trockene Grundform** (`CONTEXTUAL_SHARPENING`).
- `f17v.18`: `ol chol` — `Zustand: trocken` → **Zustand: trocken** (`CONTEXTUAL_CONFIRMATION`).
- `f78v.27`: `ol ols` — `Ansatz-/Zubereitungsposten` → **Produktposten** (`FALLBACK_REPLACEMENT`).

`und` und `Ansatz:` bleiben als geerbte Strukturrahmen sichtbar; das neue
Ganzwort wird darin ergänzt. Eine unveränderte `chol`-Bestätigung wird nicht
als semantische Schärfung umetikettiert.

## Bedeutungsbasis und Quellenkonflikt

Vier Werte (`ar`, `chor`, `chol`, `dair`) stützen sich auf spätere
Ganzwortbefunde. **24** weitere Werte werden bewusst neu aus den gebundenen
GDT736/GDT737-body-Kandidaten befördert: ausschließlich als vollständiges
rechtes Wort in einer exakten `ol X`-Spanne. Sie exportieren weder ein Präfix
noch einen body oder ein einzelnes EVA-Zeichen.

`ols` bleibt der explizite Sonderfall. GDT769 bietet nur einen schwachen
Maß-/Produktposten-Rivalen, während GDT772 formal `OLS_NULL` wählt. GDT778
setzt für Durchsatz den neuen lokalen C0-Default **Produktposten**; die ältere
Filtrat-/Abseihlesung ist verworfen und liefert dem neuen Wert keine Evidenz.

## Konsum und Grenze

Vier rechte Token (`chol` zweimal, `chy` zweimal) waren bereits im selben
Elternziel konsumiert und wechseln nur den Besitzer. Die übrigen 35 sind neu;
so steigt die eindeutige Gesamtmenge **120→155**. Es gibt keine Kollision mit
einem anderen Ziel.

Das GDT388-Paket enthält 39 rein deskriptive Textnachbarschaften und bleibt
`VALID_ACQUISITION_NOT_SCORE_READY`. Es wurden keine neuen Seiten, Bilder,
OCR, Transkriptionen, `f84`- oder `f84r`-Daten geöffnet. Die deutschen Werte
sind ersetzbare explorative Renderer-Defaults, keine Übersetzung oder
Lexemidentifikation.
