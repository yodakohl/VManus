# GDT706 method — delayed written-result census

## Question

After exposing every still-unwritten later nominal item, does the nearest
rank-2/rank-3 window behind GDT705's twenty partial-open sources support a
concrete written result bundle?

## Inputs

- GDT703's complete 83-action right-context census;
- GDT705's complete 60-case immediate nominal classification, cumulative
  C001-C018 graph, 479-token projection, 51-line projection and three spans;
- the unchanged GDT695 clause boundaries;
- `src/V79_28_DELAYED_RESULT_CELL_SPECS.tsv`, which records every manual
  reading in the bounded inner window.

No page, image, OCR product, f84 row, or f84r row is opened.

## Complete outer map

The 83 actions are first partitioned without discarding a right context:

| disposition | count |
|---|---:|
| immediate result already bound | 5 |
| initially unbound nominal block with later items | 42 |
| unbound one-item nominal block | 13 |
| next clause is another action | 15 |
| line end | 8 |

The 42 delayed nominal windows contain 163 positions after their first nominal
item. Two are existing period renderings (`A043#6 y`, `A047#10 dy`), leaving
161 semantic `(action, later item)` pairs. Every pair retains all intervening
ordinals, surfaces, and German glosses in order; repeated items are not
collapsed.

## Bounded inner census

The manually read inner window contains every rank-2 and rank-3 item behind the
twenty GDT705 `OPEN_PARTIAL` sources. Sixteen sources supply a rank-2 item;
twelve also supply rank 3, for 28 cells total. Four open sources have no later
item and therefore contribute no cell.

Each cell keeps the immediate nominal item, every additional bridge item, the
candidate target, a practical German reading, the best bridge interpretation,
and the decisive missing or conflicting information. The resulting decisions
are one admitted result bundle, ten holds, and seventeen stops. A stop only
blocks that occurrence path; it does not redefine a surface.

## C019 and graph representation

For A077, existing M007 already carries the measured drug share into
`f86v6.25#5 ykaiin`, *erhitze hiervon auf Stufe III*. The following two written
items are read together:

- #6 `or`: *Drogenportion* — visible material carrier;
- #7 `okeeeey`: *Zubereitung vollständig bis zur letzten Heizstufe geführt* —
  final heat state.

C019 therefore has graph endpoints #5 and #7 while #6 remains inside the
minimal render hull as a named, non-endpoint material carrier. This avoids both
a silent skip and an invented second edge. M007 is extended; no new component
is created.

## Preservation and claim ceiling

The builder must preserve all 479 V78 token glosses, 51 line translations and
three bound spans byte-for-byte. It adds one occurrence relation, zero word
meanings, zero pages, and zero portable output rules. C019 is an exploratory
working reading, not recovered plaintext, a historical decipherment, or a
general meaning of `ykaiin`, `or`, or `okeeeey`.
