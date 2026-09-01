# GDT710 — Methode

## Frage

Kann jede aktuell geführte Wortlesart und jede Masterkarte eine explizite,
vergleichbare Arbeitsconfidence mit positiver Evidenz, Gegenbeleg und genauer
Herkunft erhalten, ohne Formstabilität oder flüssige Prosa als historische
Entzifferung auszugeben?

## Drei getrennte Bestände

1. `WORKING_DICTIONARY_V48.tsv` enthält 2.115 heterogene Masterkarten. Dazu
   gehören Komponenten, Kompositionsregeln, gelernte Ganzformen und 563
   praktische Renderer-Karten. Diese Zeilen sind nicht alle Wörter.
2. `V48_WORKING_TOKEN_GLOSSARY.tsv` enthält 1.430 eindeutige globale
   Oberflächenformen. Exakte ZL3b-Zähler werden über alle 4.128 freigegebenen
   Zeilen des V48-Coverage-Artefakts rekonstruiert.
3. Der aktuelle V68-Reader enthält 479 Positionen, 320 Formen und 332
   `surface × gloss`-Lesarten. Sechs Formen sind polysem: `daiin`, `dain`,
   `dchey`, `dy`, `ol`, `y`.

Die primäre Gesamttabelle nimmt für aktive Formen immer die neuere V68-Lesart
und sonst den globalen V48-Default. Das ergibt 1.582 Formen und 1.594 Lesarten.
Ein älterer V48-Gloss zählt nur bei exakter `(surface, gloss)`-Gleichheit als
Evidenz; 127/479 aktive Positionen erfüllen das. Ein bloßer Surface-Match ist
ein superseded prior.

## Positionsgenaue Herkunft

Der aktuelle Gloss wird über exakte Schlüssel
`(page, locus, token_ordinal, surface)` von V57 durch GDT685–GDT695 replayt.
Die finale Writer-Verteilung ist:

| Writer | Positionen |
|---|---:|
| GDT684/V57 geerbt | 201 |
| GDT685 | 8 |
| GDT686 | 8 |
| GDT687 | 32 |
| GDT689 | 36 |
| GDT690 | 64 |
| GDT691 | 50 |
| GDT692 | 1 |
| GDT693 | 57 |
| GDT694 | 22 |

Für die 201 V57-Survivors wird zusätzlich V50–V57 replayt. Dadurch bleiben
`position_assignment_writer_gdt` und `semantic_card_origin_gdt` getrennt.
Unverändert wiederverwendete Karten, etwa `pchedaiin`, erhalten keine falsche
neue semantische Bestätigung. Die drei gebundenen V67-Spans B001–B003 werden
positionsgenau markiert und nie global exportiert.

## Confidence-Rubrik

`form_level` bewertet nur die Sichtbarkeit/Segmentierung: F0 ohne exakten
Beleg, F1 reader-unstabil/ambig, F2 kontext- oder Reader-Variante, F3 exakte
geschriebene ZL3b-Form. Formconfidence erhöht die Bedeutungsconfidence nicht.

Der `working_model_score_0_100_not_probability` summiert sechs dokumentierte
Achsen:

- Attestation 0–20;
- Invarianz 0–10;
- Regel-/Kompositionspfad 0–25, aktuell maximal 20;
- Provenienz 0–15;
- Spezifität/Scope 0–15;
- Stress/Survival 0–15.

W0 = 0–19, W1 = 20–39, W2 = 40–59, W3 = 60–79, W4 = 80–100.
Da kein echter prospektiver Klartexttest vorliegt, sind alle Einträge bei 79
gedeckelt. LOW/EXPLORATORY-Quellen, aktuelle GDT684-Schuld, lebende Rivalen,
Singletons, reine Renderer und kontextgebundene Karten erhalten explizite
Abzüge/Caps. Die vollständige maschinenlesbare Rubrik steht in
`V83_CONFIDENCE_RUBRIC.tsv`.

Manuelle Reality-Controls verhindern bekannte Fehlrankings: `olkar` darf nicht
durch Häufigkeit über `chol/qokaiin` steigen; konkrete `daiin/dain`-Achsen
bleiben unter der abstrakten Wertzelle; `dy/y` können formal stabil, aber nicht
semantisch hoch sein; LOW-Singletons mit konkreter Stoffidentität bleiben W0/W1.
Alle Controls stehen offen in `src/V83_MANUAL_CONFIDENCE_CONTROLS.tsv`.

## Historische und relationale Grenze

`historical_confirmation` ist für jede Wortlesart und Masterkarte `H0_NONE`.
Historische Analogien geben null Scorepunkte. GDT696–GDT709 sind
`ZERO_WORD_DELTA`; C019, C021, A048 und andere Relationskanten erhöhen daher
keine Wortconfidence.

## Entscheidung und Claim ceiling

PASS verlangt vollständige Populationen, exakte Source-Parität, den
mismatch-freien Writer-Replay, getrennte Polysemie, zweiseitige Evidenz,
korrekte Caps und null historische Bestätigungen. Das Ergebnis ist ein Audit
der explorativen Arbeitstheorie, kein Klartext, keine Sprachidentifikation und
kein historisch bestätigtes Lexikon.
