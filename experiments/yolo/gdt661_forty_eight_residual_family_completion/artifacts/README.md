# GDT661 artifacts

- `TARGET_DECISION_DECK.tsv`: alle 48 Defaults, Kompositionen, Rivalen,
  Stärkestufen und Zählungen.
- `ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv`: die 46 globalen exakten Ganzformen;
  `r` und `d` fehlen hier absichtlich.
- `CONTEXT_RENDERING_CARDS.tsv`: 26 beobachtete Text-, Label-, Kopf-,
  Bezugs- und Abschlussfassungen.
- `ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv`: sämtliche 872 V37→V38-Entscheidungen.
- `READER_VARIANT_AUDIT.tsv`: drei Leserfassungen und enge
  Split-Normalisierung je Zielposition.
- `FAMILY_COMPOSITION_ATLAS.tsv`: Zielkarten und sichtbare Familienanker.
- `FRONTIER_48_COMPLETIONS.tsv`: die 48 Ausgangszeilen vollständig ausgefüllt.
- `TARGET_LINE_TRANSLATIONS.tsv`: alle 786 betroffenen Zeilen vor/nach V38.
- `ALL_LINE_CONCRETE_COVERAGE_V38.tsv`: vollständige 4.128-Zeilen-Edition.
- `COMPLETE_PASSAGES_V38.tsv` und `ONE_UNKNOWN_PASSAGES_V38.tsv`: aktuelle
  vollständige beziehungsweise Ein-Loch-Passagen.
- `NEWLY_COMPLETED_LINES.tsv` und `NEWLY_EXPOSED_ONE_HOLE_LINES.tsv`: die
  Deltas der Runde.
- `V38_WORKING_TOKEN_GLOSSARY.tsv` und `WORKING_DICTIONARY_V38.tsv`: laufende
  Arbeitslexika mit getrennten Struktur- und Übersetzungsspalten.
- `ROUND_COVERAGE_COUNTS.tsv`, `RESULT.json`, `VALIDATION.json`: Kennzahlen,
  Hashvertrag und unabhängige Prüfung.

`reader_exact` bedeutet dieselbe vollständige Oberfläche in ZL3b, IT2a und
RF1b. `split_normalized` erlaubt zusätzlich nur die exakte Konkatenation
aufeinanderfolgender vollständiger Lesertoken. Umgekehrte Fusionen und bloße
Substringtreffer zählen nicht.
