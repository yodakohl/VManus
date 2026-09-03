# GDT767-Artefakte

Der Builder erzeugt zehn lesbare Ergebnisdateien sowie `RESULT.json`.

- `COFIELD_224_OCCURRENCE_ATLAS.tsv` — alle 224 Zielvorkommen mit
  zielwort-freien `D1`, `R3` und Linienmerkmalen sowie den exakten
  Geberoberflächen, Abständen und Merkmalen; der Validator bindet die
  semantischen Quellen erneut aus dem Cache.
- `COFIELD_28_FORM_MATRIX.tsv` — die zwölf Merkmale pro Ganzform als
  `D1/R3/LINE`-Zähler; alle 28 Stoffidentitäten bleiben ausdrücklich `OPEN`.
- `OFCH_43_AGGREGATE_FEATURE_SUMMARY.tsv` — kompaktes Profil der 43
  `ofch`-Vorkommen, einschließlich null exakten `cthy`- und null zugelassenen
  exakten `chor`-Ankern.
- `CHOR_CTHY_15_PARALLEL_ATLAS.tsv` — 15 `chor`-Positionen auf 14 Loci mit
  parallelem `cthy`, darunter fünf direkte Paare und beide Reihenfolgen.
- `SHADOW_REPRODUCTIVE_4_AUDIT.tsv` — die vier schwachen Kontakte mit
  `schor`, `chory` oder `shor`; alle behalten null Identitäts-, Relations- und
  Komponentenwert.
- `HISTORICAL_504_CANDIDATE_TOURNAMENT.tsv` — 18 historische Stoff- und
  Formkandidaten für jedes der 28 Zielwörter, mit Gates, Trefferzahlen,
  Evidenzstufe, Rollenpassung, Rang, Quellen und Gegenkontrollen.
- `HISTORICAL_IDENTITY_SEPARABILITY.tsv` — vollständige Supportvektorgruppen;
  identische Gruppen bleiben ungetrennte Rivalen.
- `GDT767_28_WORKING_DICTIONARY.tsv` — target-freie Stoff-/Formauswahl,
  portable Klasse, konkreter C0-Default, Rivalen, Evidenz, Gegenbeleg und
  Exportgrenzen für alle 28 Ganzwörter.
- `FIVE_LINE_REVISED_READER.tsv` — 46 eindeutig adressierte Tokenpositionen
  auf fünf vollständigen Linien; Semikolons erhalten Reihenfolge, ohne
  Anfügung oder Syntax zu behaupten.
- `HISTORICAL_REGISTER_READER.md` — menschlich lesbarer Gesamtüberblick mit
  28er-Wörterbuch, fünf Arbeitslinien, `chor`/`cthy`-Brücke und den sechs
  historischen Quellen.
- `RESULT.json` — maschinenlesbarer Status, Scope, `ofch`-Merkmalssummen,
  Formkartenauswahl, Rivalengruppen, Downgrades und Claim-Grenze.
- `VALIDATION.json` — 41.469 unabhängige Struktur-, Geber-, Gate-,
  Claim-Grenz- und Byte-Replay-Prüfungen für alle elf Builder-Ausgaben.

Die historischen Eingabekarten liegen in
`../src/HISTORICAL_CANDIDATE_DECK.tsv` und
`../src/HISTORICAL_SOURCE_REGISTRY.tsv`. Sie belegen das Mischregister, nicht
eine Voynich-Wortgleichung.

Alle konkreten Stoffwörter in den Readern sind ersetzbare Arbeitshypothesen.
Die Artefakte bestätigen null Lexeme, null Substanzen, null Klartextklauseln
und null Komponentenwerte; sie verwenden keine neue Seite oder Abbildung und
greifen weder auf `f84` noch auf `f84r` zu.
