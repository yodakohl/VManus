# GDT734-Artefakte

## Kanonische vollständige Ausgaben

- `V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv`: vollständiges V99R7-Wörterbuch
  mit Bedeutung, Score, Confidence, Evidenz, Gegenbeleg und Scope.
- `V99R7_32339_COMPACT_CELL_REGISTER.tsv`: positionsgenaues Register aller
  Cache-Zellen, ihrer Quelle, Präzedenz und finalen Fassung.
- `V99R7_4128_INTEGRATED_LINE_READER.tsv`: vollständiger praktischer
  Zeilenreader unter Erhalt der GDT733-Unit-Schicht.
- `RESULT.json` und `VALIDATION.json`: maschinenlesbares Ergebnis und
  unabhängiger Validierungsnachweis.

## Deltas und Entscheidungsdecks

- `V99R7_71_ACTIVE_WHOLE_EXPORT_REPAIR.tsv`: technischer Pass 1, 71 Formen an
  305 Positionen.
- `V99R7_28_EDITORIAL_SCOPE_PRECEDENCE_AUDIT.tsv`: redaktioneller Audit von 28
  aktiven Ganzwortfassungen, davon 26 mit gekürztem gesprochenem Renderer.
- `V99R7_20_UNIQUE_SPLIT_CANDIDATE_DECK.tsv`: Pass 2 mit den individuellen
  9/5/6-Entscheidungen, Scores und Grenzen.
- `V99R7_531_POSITION_DELTA.tsv`: sämtliche 531 geänderten Cache-Zellen.
- `V99R7_19_FAMILY_ROLE_MATRIX.tsv`: beobachtete Kopf×Rollen-Kreuzmatrix;
  Rollen sind keine frei exportierten Lexeme.
- `V99R7_TOP100_RESIDUAL_SPLIT_INVENTORY.tsv`: verbleibende häufige
  Restformen und ihre technischen Splitmöglichkeiten.

## Zusammenfassungen und Leser

- `V99R7_RENDER_QUALITY_SUMMARY.tsv`, `V99R7_BLOCKER_CENSUS.tsv` und
  `V99R7_INHERITED_ARTIFACT_PARITY.tsv`: Qualitäts-, Blocker- und Hashkontrollen.
- `V99R7_50_CHANGE_DENSE_PASSAGES.tsv` und
  `GDT734_V99R7_50_CHANGE_DENSE_READER.md`: die 50 änderungsdichtesten
  Passagen; Rang ist keine semantische Wichtigkeit.
- `HISTORICAL_MICROENTRY_COMPARATORS.tsv`: institutionelle historische
  Architekturvergleiche mit durchgehend null Relations- und Zeichenwertkredit.

## Warum die großen Register erhalten bleiben

Das 32.339-Zellen-Register und der 4.128-Zeilen-Reader überschreiten die
kompakte Standardgröße. Sie sind notwendig, um die vollständige Schlüssel- und
Nichtzielparität, alle 531 positionsgenauen Änderungen, die Präzedenz exakter
Kontexte, 16 Render-once-Spans, vier Interpunktionsanhänge, 32.319 praktische
Einheiten sowie die unveränderten Confidence-, Evidenz- und Scope-Felder
unabhängig nachzurechnen. Aggregierte Tabellen können diese Behauptungen nicht
reproduzieren.
