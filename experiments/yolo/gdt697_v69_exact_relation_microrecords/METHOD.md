# GDT697 method

## Question and scope

Can all nine V69 occurrence edges be composed into concrete source/action
microrecords without inventing another edge, result, word meaning or page?

The input is exactly the GDT696 deck: nine admitted edges, 27 exhaustively
classified reference positions, seventeen held rivals, 479 tokens, 51 lines,
three bound spans and 36 pages. f84/f84r remain forbidden.

## Deterministic window construction

Each V69 edge contributes its exact source ordinal(s), optional reference
ordinal, action target and any written right participant. Edges are connected
only when they share an exact `(locus, ordinal)` node. Mere adjacency never
joins them. The smallest contiguous hull around each connected component is
its V70 window.

This construction yields exactly seven disjoint windows:

- five single-edge windows;
- one ordered common-destination fan-out at f80v.35, where C004 and C008 share
  only destination #3 and target the two distinct `qol` at #5 and #6;
- one serial action-output chain at f86v6.25, where C007's target #4 is exactly
  C006's `DONOR_ACTION_OUTPUT`.

The seven hulls contain nineteen distinct token positions. If every edge were
housed separately, their hulls would sum to 23 positions; the four-position
difference is precisely the shared-node composition in the two multi-edge
windows.

## Practical rendering

`src/V70_MICRORECORD_SPECS.tsv` fixes one German microrecord per window and the
exact surface, V69 gloss and role trace expected at every position. A rendering
may resolve only the relations named by its member edge IDs. Its left and right
neighbours, nonmember references and held rivals are written into the same row
as explicit boundaries.

The builder separately copies the complete V69 token, line and span tables. It
never substitutes the microrecord into the inherited line translation. This
keeps the useful practical sentence visible without silently changing a word
card or converting the editorial relation into plaintext.

## Decision rule

Pass requires:

- seven exact endpoint-sharing components and minimal convex hulls;
- 9/9 V69 edges used exactly once across nineteen positions;
- the fixed 5 single / 1 repeated-destination / 1 serial topology;
- exact surface, gloss, clause and role joins back to V69;
- six written reference positions, one action-output bridge, one shared
  destination and one preposed output label;
- zero held-rival targets inside a window and zero adjacency-derived edges;
- one named intermediate output but no named final result;
- 479/51/3 unchanged token/line/span records, zero new word meanings or pages,
  and no f84/f84r access.

V70 remains an occurrence-bound editorial rendering of an exploratory working
edition. It does not establish plaintext, a language, a portable deictic rule,
or a universal meaning for any Voynich surface.
