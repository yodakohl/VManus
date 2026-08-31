# GDT703 — all-action written-result census

Status: `PASS_V76_83_ACTION_RIGHT_CONTEXTS__60_NOMINAL_15_ACTION_8_EOS__7_FINISHED_STATE_FIRSTS__3_LOCAL_READS_4_OPEN__C013_C014_ADDED__ZERO_WORD_DELTA`

## Result

The no-skip census covers all 83 current action clauses.  Their immediate
right contexts divide into 60 nominal blocks, 15 action clauses, and 8 line
ends.  Exactly seven first right entries are independently typed by GDT687 as
`HIGH / NOMINAL_FINISHED_RESULT_STATE`.

One case retains C012, two become new occurrence-bound working relations, and
four remain open non-edge readings.  No candidate was found by skipping over
an intervening entry.

## Concrete additions

### C013 — f26r.2

> Die Krautdroge bis zur Mittelstufe erhitzen und abschließen [Quelle von
> „hiervon“ offen]. Zustand: mittlere Trockenstufe erreicht. Dieselbe erhitzte
> Krautdroge bis zur Mittelstufe abkühlen und abschließen
> [C011/C013-Arbeitshypothese].

C013 is `#4 ykecthey → #5 chedy`.  GDT700 had already classified #5 as the
exact state-only result checkpoint between #4 and #6.  C013 now records the
local result relation.  C011 remains the separate `#4→#6` carry.  The graph is
a common-source fork, not a new `#5→#6` chain.

### C014 — f115r.23

> Heißen Auszug bereiten und abschließen. Ergebnis: leicht getrocknete,
> abgeschlossene Zubereitung.

C014 is `#3 qokeod → #4 chody`.  It is deliberately lower-confidence: #4 may
instead be an independent material checkpoint, and the light drying is not a
separate verb in #3.  The working relation ends at #4; action #5 is not drawn
into it.

## Complete seven-case contrast

| Locus | Immediate pair | Decision | Practical reason |
|---|---|---|---|
| f105r.2 | `odar#11 → cheody#12` | HOLD_OPEN | measuring does not itself create a dry state |
| f105v.1 | `ykaiin#4 → olpchedy#5` | retain C012 | written wood powder remains a wood-powder result |
| f105v.14 | `qokaiir#3 → olpchedy#4` | HOLD_OPEN | taking a hot drug share does not produce wood-extract powder |
| f115r.1 | `qochedain#3 → otedy#4` | HOLD_OPEN | measuring dried goods does not explain a cold preparation |
| f115r.23 | `qokeod#3 → chody#4` | add C014 | completed hot extract can locally precede the written completed preparation |
| f26r.2 | `ykecthey#4 → chedy#5` | add C013 | written herb-heating action is followed by the exact written state checkpoint |
| f77v.7 | `ycheedy#5 → okedy#6` | HOLD_OPEN | unresolved dry/end-stage patient conflicts with hot/middle-stage preparation |

## Graph result

The cumulative graph changes from 12 to 14 edges and from 9 to 10 components.
It contains 27 unique edge nodes, 31 edge incidences, 28 minimal-hull positions,
29 render positions, 4 shared nodes, 1 hull-only position, and 1 render-only
structural position.

The sole remaining hull-only position is `f86v5.24#2`; the sole structural
render position is `f26r.2#7`.  The exact shared nodes are `f105v.1#4`,
`f26r.2#4`, `f80v.35#3`, and `f86v6.25#4`.

## Scope and next move

All 479 token glosses, 51 line translations, and 3 bound spans remain
byte-identical.  No page, word meaning, or sealed material was added.  The
combined GDT388 intake correctly remains invalid/not score-ready with the two
formal-access errors.

Next inspect, inside the same 36-page scope, whether C013 or C014 has a later
compatible consumer or a repeated written material head.  That is the most
direct way to turn either local result reading into a longer practical process
without manufacturing a portable word rule.
