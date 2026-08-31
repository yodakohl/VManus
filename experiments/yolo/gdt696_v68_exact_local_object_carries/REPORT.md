# GDT696 — nine concrete local source/action relations

Status: `PASS_V69_6_STRONG_PLUS_3_WORKING_LOCAL_EDGES__27_REFERENCE_CENSUS__17_RIVALS_HELD__ZERO_WORD_DELTA`

## Result

V69 makes nine exact passages more concrete without changing the V68
dictionary. Six relations have stronger written or inherited local support;
three are useful working defaults confined to one occurrence. They affect
seven of the 51 loci:

| locus | edge | practical relation |
|---|---|---|
| f105v.1 | C001 | Das trocken gebundene Holzpulver, Form II, auf Stufe III erhitzen. |
| f113v.17 | C002 | Von den drei Portionen Krautdroge eine Portion bis zur letzten Stufe abkühlen. |
| f75r.3 | C003 | Die vorstehende, bis zur Mittelstufe getrocknete Drogenportion anschließend nehmen. |
| f80v.35 | C004 | Dem Anteil I des heißen Holzansatzes Drogenstoff zugeben. |
| f77r.38 | C005 | Das bis zur Mittelstufe getrocknete und abgeschlossene Arzneikompositum zugeben. |
| f86v6.25 | C006 | Den so abgemessenen Drogenanteil I auf Stufe III erhitzen. |
| f86v6.25 | C007, working | Aus dem Anteil I des heißen Holzansatzes einen heißen Drogenanteil I abmessen. |
| f80v.35 | C008, working | Dem Anteil I des heißen Holzansatzes nochmals Drogenstoff zugeben. |
| f104v.2 | C009, working | Eines der drei Maße des kalten Ansatzes nehmen und erhitzen. |

This produces the first bounded two-step practical chain in the current
edition at f86v6.25:

> Aus dem Anteil I des heißen Holzansatzes einen heißen Drogenanteil I
> abmessen. Den so abgemessenen Drogenanteil I auf Stufe III erhitzen.

The leading “Hiervon bis zur Endstufe abkühlen” on the same line remains
unresolved. The concrete chain therefore adds information without pretending
that the whole line is already understood.

## What was not forced

All 27 visible German reference expressions were counted rather than sampling
only the convenient six. Twenty-one do not receive a new object edge. The
important holds include the direction conflict around `ypcheddy` at f105v.1,
the competing cooling donors before `ytol` at f86v5.2, the two-token source
rival before `ykain` at f86v5.24, and five line-initial references with no
written donor inside their line.

Seventeen fully spelled-out alternatives remain in the rival artifact. Ten of
them demonstrate why mere proximity would overgenerate: an adjacent noun and
action can make plausible recipe prose without a written reference or an older
occurrence license. V69 therefore contains no “nearest material” fallback.

## Freeze and validation target

- 479/479 V68 token glosses are unchanged.
- 51/51 V68 line translations are unchanged.
- 3/3 bound spans are unchanged.
- The target of every admitted edge and every rival is a licensed V68 action
  clause.
- There are zero new word meanings, pages, f84 accesses or f84r accesses.

During the independent source audit, a malformed P008 row was caught before
validation: the missing target-surface field had shifted the final columns. It
was repaired to the actual V68 target `chetain`; the strict TSV-width check now
makes that error fatal.

The final schema also prevents a subtler C007 error. Its two written left
participants are no longer both labeled “source”: `qokar` is the selected
`OUTPUT_LABEL`, while `olkar` alone is `DONOR_SOURCE_SHARE`. The wider ordinal
span records the whole relation block; the per-position role map records what
each member does.

## Interpretation and next route

The useful advance is relational, not lexical. We can now say what a handful
of already translated action cards act on, instead of printing isolated
imperatives beside inventory fragments. The nine relations are still editorial
working hypotheses bound to exact occurrences; they do not prove that any
Voynich form means “this”, “object” or “carry”.

The next productive step is to render only these nine exact edges as compact
source–operation–result microclauses and compare whether they produce coherent
multi-step chains. No additional deictic, nearest-neighbour edge, word meaning
or page is needed for that pass.
