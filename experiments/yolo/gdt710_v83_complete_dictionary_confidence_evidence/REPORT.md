# GDT710 — Vollständiges Wörterbuch mit Confidence und Evidenz

Status: `PASS_V83_2115_MASTER_CARDS__1430_GLOBAL_SURFACES__1582_COMPLETE_WORD_SURFACES_1594_READINGS__320_LIVE_SURFACES_332_LIVE_READINGS_479_OCCURRENCES__ALL_H0_NONE__CONFIDENCE_IS_NOT_PLAINTEXT`

## Ergebnis

Die primäre Worttabelle enthält 1.582 verschiedene Oberflächenformen und 1.594 Lesarten. Sie verwendet für jede der 320 aktiven Formen den neueren V68-Sinnbestand und für die übrigen Formen den globalen V48-Default. Polyseme Formen werden nicht zusammengemittelt.

Die 2.115 Zeilen des Master-Wörterbuchs sind separat bewertet, weil darunter Regeln und 563 praktische Renderer-Karten stehen. Eine Renderer-Karte ist kein zusätzliches Voynich-Wort.

Jede Zeile nennt positive Evidenz, Gegenbeleg, Formniveau, sechs Scorekomponenten, Abzüge/Caps und den letzten semantischen Writer. Der Zahlenwert ist ein Auditindex innerhalb der Arbeitstheorie, keine Wahrscheinlichkeit.

Nur 127/479 aktive Positionen stimmen zugleich in Surface und Gloss mit V48 überein. Weitere 152 haben dieselbe Surface, aber einen später revidierten Gloss; 200 besitzen keine V48-Surfacekarte. Alte V48-Glossen sind dann superseded prior, nicht Evidenz der neuen Bedeutung.

## Verteilung der vollständigen Worttabelle

| Level | Lesarten |
|---|---:|
| `W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY` | 296 |
| `W1_WEAK_WORKING` | 345 |
| `W2_PROVISIONAL_WORKING` | 510 |
| `W3_SOLID_WORKING_THEORY` | 443 |

## Aktive 332 Lesarten

| Level | Lesarten |
|---|---:|
| `W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY` | 16 |
| `W1_WEAK_WORKING` | 165 |
| `W2_PROVISIONAL_WORKING` | 132 |
| `W3_SOLID_WORKING_THEORY` | 19 |

Sechs Formen sind polysem und besitzen eigene Sinnzeilen: `daiin`, `dain`, `dchey`, `dy`, `ol`, `y`. Die abstrakten globalen Wertzellen `daiin/dain` sind stabiler als jede konkrete lokale Grad-/Mengenbindung; `dchey` erreicht W3 nur innerhalb seines benannten Action/Result-Scopes; `dy/y` können formal brauchbar sein, bleiben semantisch strukturell.

## Reality-Check an Schlüsselwörtern

| Lesart | Score/Level | Warum |
|---|---:|---|
| `dchey` Aktionslesart | 79 / W3 | neun scope-konsistente Aktionsbelege auf neun Seiten |
| `dchey` Resultatlesart | 74 / W3 | fünf getrennte Resultatbelege auf fünf Seiten |
| `chol = trocken` | 69 / W3 | wiederholter Zustandswert nach expliziter GDT685-Reparatur |
| `qokaiin = heiß, Grad III` | 61 / W3 | geordnete Wertzelle plus sichtbarer Qualitätskopf |
| `pchedaiin` | 59 / W2 | zwei konsistente Kompositionsbelege, aber offene Achse und Identität |
| `olkar` | 39 / W1 | häufig, jedoch weiterhin lokale provisorische Holzbindung |
| `shx = eingeweichtes Gummi` | 19 / W0 | LOW-Singleton; Feuchte sichtbar, Gummi nicht unabhängig belegt |
| konkrete `daiin/dain`-Bindungen | 26–30 / W1 | jeweils lokaler Grad-/Mengenentscheid mit lebendem Rivalen |
| freies `dy/y` | höchstens 19 / W0 | struktureller/punktueller Renderer, kein portables Wort |

Die drei gebundenen V67-Spans B001–B003 sind an sechs Positionen markiert und haben `bound_span_global_export_allowed=0`; eine kombinierte Spanbedeutung wird nicht doppelt als zwei Lexemevidenzen gezählt.

## Historische Grenze

Alle 1594 aktuellen Wortlesarten und alle 2.115 Masterkarten stehen auf `H0_NONE`. Zeitnahe Fachbuch- oder Kürzelanalogien wären Kategorienvergleiche, keine Bestätigung einer Voynich-Klartextzuordnung.

## Nullbeitrag der Relationsrunden

GDT696 bis GDT709 sind `ZERO_WORD_DELTA`. C019, C021, A048 und alle anderen Relationskanten geben daher exakt null Punkte zur Wortconfidence.

## Dateien

- `V83_COMPLETE_WORD_CONFIDENCE.tsv`: primäre vollständige Wort-/Sinnliste
- `V83_2115_MASTER_CARD_CONFIDENCE.tsv`: alle Masterkarten, inklusive Regel-/Rendererobjekte
- `V83_1430_GLOBAL_SURFACE_CONFIDENCE.tsv`: globaler V48-Snapshot
- `V83_332_LIVE_READING_CONFIDENCE.tsv`: aktive Sinne
- `V83_479_LIVE_OCCURRENCE_EVIDENCE.tsv`: positionsgenaue Belegkette
- `V83_CONFIDENCE_RUBRIC.tsv`: vollständige Rubrik

## Claim ceiling

Die Ausgabe ordnet die vorhandene explorative Arbeitstheorie und macht ihre Schuld sichtbar. Sie bestätigt kein einziges historisches Lexem, keine Sprache, keinen Codebook-Schlüssel und keinen Klartext.
