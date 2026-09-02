# GDT732 report — the grade frame becomes audible state prose

Status: `PASS_175_GRADE_READINGS_2431_LICENSED_POSITIONS__162_GLOBAL_2401_PLUS_13_ACTIVE_30__1784_TARGET_ACTIVE_SURFACE_LEAK_CONTROLS__75_DIRECT_ROWS_1748_POSITIONS__100_NEUTRAL_ROWS_683_POSITIONS__ZERO_TARGET_GRADE_FRAMES__4752_V48_BASELINE_RESIDUALS_4692_ACTIVE_OUTSIDE_EXACT_PLUS_52_SUPERSEDED_EXACT_PLUS_8_ALIAS_MERGE__V99R4_SEMANTIC_DICTIONARY_BYTE_STABLE__NO_NEW_PAGE`

## Result

GDT732 finds 175 grade-bearing readings in the 1,586-row V99R4 dictionary and
reconstructs all 2,431 of their licensed cache positions. The exact scope is
162 global readings/2,401 positions plus thirteen active readings/thirty
positions. Every original dictionary field remains byte-identical; the new
spoken channel is an overlay.

Seventy-five readings/1,748 positions support direct state prose. The other
100/683 remain deliberately neutral because they contain several modalities,
a composite whose stage attachment is ambiguous, or no explicit modality.

| Renderer | Readings | Positions |
|---|---:|---:|
| single-axis participle | 71 | 1,710 |
| clause-local two-stage participles | 4 | 38 |
| mixed state, neutral stage | 82 | 604 |
| single composite, neutral stage | 9 | 21 |
| no modality, neutral stage | 9 | 58 |

Across the licensed cells, 2,469 audible grade markers fall to zero. The 728
explicit `abgeschlossen/fertig` markers and all 3,015 modality mentions remain
exactly preserved. Mean target-cell length falls from 6.03 to 3.77 words. That
is a measured rendering gain, not evidence that the inherited word meanings
are true.

## What the new voice says

Representative exact changes are:

- `heiß am Ende des Grades` → `vollständig erhitzt`;
- `kalt in der Mitte des Grades` → `bis zur Mittelstufe abgekühlt`;
- `trocken am Ende des Grades, abgeschlossen` → `vollständig getrocknet,
  abgeschlossen`;
- `kalt-feuchter Ansatz in der Mitte des Grades, abgeschlossen` →
  `kalt-feuchter Ansatz, Mittelstufe erreicht; abgeschlossen`;
- `trocken am Gradende, dann heiß am Gradanfang` → `vollständig getrocknet,
  dann leicht erhitzt`.

The wording was manually corrected after audit. `Abgekühlt` now expresses an
attained cold state more naturally than `gekühlt`, and neutral stage plus
workflow closure are separated so `Mittelstufe abgeschlossen` cannot be read
as closing the stage itself.

At `f111r.8`, five licensed target cells now read:

> vollständig getrocknet, abgeschlossen; vollständig erhitzt;
> kalt-feuchter Ansatz, Mittelstufe erreicht; abgeschlossen; Drogenholz,
> vollständig erhitzt; kalt und trocken, Anfangsstufe erreicht; abgeschlossen

Two other grade cells on the same line remain untouched and are now explicitly
listed by ordinal in the reader. This distinction matters more than making the
whole line look superficially finished.

## Scope audit: why the V48-baseline projection shows 4,752 grade cells

The target result is complete, but this output intentionally begins from the
inherited V48 cache rather than pretending that all later overlays have already
been merged. After the 2,431 licensed rewrites, that target-only projection
still displays 4,752 grade-bearing V48 cells:

| Residual lineage | All cache lines | On 1,661 changed lines |
|---|---:|---:|
| thirteen GDT732 active surfaces outside thirty exact positions | 1,784 | 932 |
| 41 other active surfaces outside their own exact positions | 2,908 | 1,538 |
| old V48 cells already superseded at other exact V99 positions | 52 | 18 |
| legacy contextual alias/merge cells (`o`, `ch`, `dom`) | 8 | 6 |
| **Total** | **4,752** | **2,494** |

The apparent 4,925-to-2,494 passage delta uses only the 1,661 lines affected by
GDT732: 2,431 target cells plus 2,494 residual cells. The full-cache residual
adds 2,258 cells on untouched lines. These denominators must not be mixed.

The first two classes are not permission to promote an active reading to a
global word meaning. They are inherited contextual V48 cells. The third class
is different: its displayed V48 wording is already obsolete. Substituting the
current V99 context removes the grade marker in 51 of those 52 cells; only
`f104v.2`, ordinal 3 (`chockhy`) still contains `am Gradanfang`. The eight
remaining cells are narrower contextual alias/merge products. GDT732 leaves
the baseline cells unchanged but publishes their current V99 values and exact
lineage instead of hiding the mismatch in a polished-looking line.

## What this changes and what it does not

All 29,908 non-target positions remain unchanged. Scores, confidence levels,
positive evidence, counterevidence, semantic scope, export rights, action
defaults and component relation credit do not change. The three GDT696 local
relation artifacts and five GDT727 active-reader artifacts remain
byte-identical.

`Vollständig` renders the end of the inherited degree scale. It does not by
itself assert workflow completion: `OPEN`, `CLOSED` and `FINISHED` remain
separate formal fields. The renderer also does not establish the historical
truth of `heiß`, `kalt`, `trocken` or `feucht`; it only speaks those already
stored working meanings more naturally.

## Next route

GDT733 should be a position-only legacy grade-cell renderer, not a dictionary
rewrite. It should first install the 52 already licensed V99 contexts, then
apply the frozen GDT732 policy to the 4,692 inherited active out-of-scope cells
while labelling them `LEGACY_V48_CONTEXT_CELL`, never as a portable surface
meaning. The one surviving exact-context grade phrase and the eight
`o/ch/dom` alias/merge cells require individual handling. One integrated
full-cache denominator should then replace the current split view. No new page
is needed.
