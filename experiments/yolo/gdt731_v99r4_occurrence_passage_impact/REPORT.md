# GDT731 report — where V99R4 helps and where it still fails

Status: `PASS_94_SURFACES_1039_POSITIONS_911_LINES__351_COMPLETE_LINES__50_TARGET_DENSE_PASSAGES__GDT696_OVERLAYS_BYTE_STABLE__CACHED_DEFAULT_IMPACT_ONLY__NO_POLISHED_TRANSLATION_OR_NEW_PAGE`

## Result

All 94 GDT730 surfaces reconstruct exactly at all 1,039 canonical occurrences
inside 911 of the 4,128 cached lines. Every per-surface count matches V99R4.
Exactly 31,300 non-target token cells remain unchanged. Of the affected lines,
351 already had zero unknown tokens in the inherited V48 register.

Inside the changed cells, visible alternative notation drops as follows:

| Marker | V99R3 | V99R4 |
|---|---:|---:|
| slash | 823 | 0 |
| standalone `oder` | 76 | 0 |
| case-insensitive `menge` | 251 | 0 |

The mean target-cell length falls from 4.05 to 2.68 words. This is a measured
gain in concision and audible single-default dispatch: the dictionary no
longer speaks two rival guesses at once. Practical informativeness is mixed;
some cells merely replace one analytic placeholder with a shorter one. None
of these changes is evidence that the chosen guess is plaintext.

## Concrete passage effect

At `f19v.6`, the relevant projection changes from:

> Eintrag/Bezug: Trockenansatz am Gradanfang; Drogenportion, heiß-trocken;
> CTH-Drogenstoff; im Kräuterbuch Blatt- oder Krautdroge; trockene
> CTH-Drogenzubereitung; im Herbal trockene Blatt-/Krautzubereitung;
> Samen-/Saatgutposten

to:

> Eintrag: Trockenansatz am Gradanfang; Drogenportion, heiß-trocken;
> Pflanzendrogenstoff; trockene Pflanzenzubereitung; Samen-/Saatgutposten

At `f80r.18`, the two CTH alternatives collapse to `feuchtes
Pflanzenmaterial`, and `paiin` becomes `Pulver, Charge III`. The surrounding
line still says `feuchtes Material`, `kaltes Material`, grade language and
another repeated `feuchtes Pflanzenmaterial`. That is useful precisely because
it exposes the next real bottleneck instead of hiding it behind fluent filler.

The complete reader of the fifty most target-dense passages is
`artifacts/GDT731_V99R4_50_TARGET_DENSE_READER.md`. Its ranking is target count,
then inherited completeness and locus; it is not a ranking of semantic
importance.

## Reality check: this is still not polished prose

The explicit blocker census over the complete 1,586-row V99R4 dictionary finds:

| Blocker | Rows | Canonical occurrences | Cells in affected passages |
|---|---:|---:|---:|
| audible grade frame | 175 | 2,431 | 1,836 |
| `Wertstufe/Form/Charge/Klasse` union | 111 | 691 | 363 |
| strict unnamed material carriers | 18 | 191 | 170 |
| audible `Eintrag/Eintragsform` | 17 | 146 | 105 |
| inherited unknown cells | — | — | 1,609 |

The grade-frame renderer is now the largest avoidable prose defect: phrases
such as `heiß am Ende des Grades` carry a plausible ordered state but sound
like analysis metadata. The next pass should retain the formal tag separately
and speak the state as `leicht`, `bis zur Mittelstufe` or `vollständig`
heated, cooled, dried or soaked. Audible Y structure is a smaller, lower-risk
cleanup. Truly unnamed `Material` heads need family evidence rather than a
blanket substitution.

## Limits

GDT731 projects global whole defaults; it does not overwrite GDT696's locally
bound actions, patients or relation clauses, whose three artifacts remain
byte-identical. The 351 complete lines are complete under the inherited V48
coverage definition, not historically verified translations. No new page or
transcription is used.
