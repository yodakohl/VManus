# GDT701 method

## Question

Do the complete current C001--C011 relation edges form exactly nine
occurrence-node connected components whose practical microrecords can be
published without adding an edge, participant identity, result name or word
meaning?

## Inputs

- GDT696 supplies the original nine edge rows, all 17 held relation rivals and
  all 27 reference-census rows.
- GDT697 supplies the seven exact C001--C009 microrecords, their nine-edge
  coverage and the 19 position-role rows from which those microrecords were
  built.
- GDT699 supplies C010 at `f86v5.24#1 → #3`.
- GDT700 supplies the cumulative eleven-edge register, C011 at
  `f26r.2#4 → #6`, its exact boundary controls, and the immutable current-scope
  projections: 479 tokens, 51 lines and three bound spans.
- `src/V74_2_NEW_COMPONENT_SPECS.tsv` fixes only the editorial render windows
  for C010 and C011.  It does not nominate a new relation.

## Method

Each edge is represented by its exact occurrence nodes `(locus, ordinal)`.
Union-find joins two edges only when those node sets intersect.  Sharing a
locus, sitting in adjacent hulls, having the same surface form, resembling a
prototype, or appearing in the held rival/reference decks cannot join them.
A synthetic control containing two disjoint edges on one locus must therefore
return two components.

The resulting components receive stable M001--M009 identifiers in manuscript
order.  For M001--M007 the builder reproduces every GDT697 microrecord, window,
surface and topology byte-for-byte at field level.  M008 and M009 are appended
from the fixed two-row specification and must reproduce the exact C010/C011
edge endpoints.

Three kinds of positions remain separate:

1. **edge node** -- an ordinal explicitly present in at least one inherited
   relation edge;
2. **hull-only** -- an ordinal between the minimum and maximum edge node but
   absent from every edge; and
3. **render-only structural** -- punctuation/closure included for readable
   rendering but outside the minimal edge hull.

Consequently `f86v5.24#2 aiin` and `f26r.2#5 chedy` are hull-only, while
`f26r.2#7 dy` is render-only structural.  Neither class becomes a relation
node.  The builder also verifies that the 17 held rivals and 27 reference rows
are unchanged, and replays all 479 token glosses, 51 line translations and
three bound spans byte-identically.

## Decision rule and claim ceiling

Pass requires exactly 11 inherited edges, 9 exact node-connected components,
23 unique edge nodes, 25 edge-node incidences, 25 minimal-hull positions, 2
hull-only positions and 1 render-only structural position.  Exactly two nodes
must be shared by edges: `f80v.35#3` in the repeated-destination fan-out and
`f86v6.25#4` in the serial action-output chain.  The synthetic same-locus
control must remain split.  No edge, rival decision, reference decision,
participant identity, word meaning or page may change.

V74 is a cumulative integration edition, not a new semantic discovery.  The
nine German microrecords are the most concrete current occurrence-bound
working readings, but they are not verified plaintext.  In particular,
M009's “erhitzte Krautdroge” remains the inherited C011 B-tier hypothesis;
M008's quantity remains unbound; and no component names the final result of
its last action.
