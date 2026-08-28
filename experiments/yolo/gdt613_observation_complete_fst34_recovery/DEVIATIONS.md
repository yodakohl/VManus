# GDT613 pre-score implementation clarifications

Date: 2026-08-28

These issues were found after the public execution contract but before any new
truth world, oracle-decoy score or recovery run was accepted.

## 1. Fixed allocation is a nominal submodel

GDT609 calls `18/4/3/3/2/2/1/1` a soft prior and permits paid ±1 exchanges
between adjacent functional buckets. GDT613's fixed 34 length cards therefore
test the nominal exact-allocation submodel first; they are not the entire soft
GDT609 capacity. A passing nominal recovery must later receive the registered
soft-swap ablation before any target claim. A nominal failure cannot falsify the
larger soft model.

## 2. The published EBNF has a scope ambiguity

GDT609 says both that every one of 64 merge units composes recursively from
primitive roles and that `CORE` contains one `LITERAL` or `SYLLABIC`. It does
not say whether the chunk FST consumes flattened primitive pieces or an
aggregate role of each outer 98-unit token. The distinction is material:
literal flattening of the GDT612 planted truth makes only 1,922/14,553 train
events (13.21%) legal under the published EBNF.

A diagnostic, explicitly unregistered widening that permits adjacent complete
`CORE` values raises this to 14,461/14,553 train events (99.37%) and
3,562/3,639 held records (97.88%).  All 92 remaining train events contain an
interior null.  Of the 77 held failures, seventeen contain an interior null and
sixty are deliberately repeated exposure probes with a context mark outside
its licensed literal adjacency.  This large discontinuity is evidence about
the grammar scope, not permission to adopt the widening inside GDT613.  A
run-capable grammar must receive a new model identifier and its own prospective
recovery test.

Before truth generation, GDT613 must publish a grammar-scope feasibility table.
The literal flattened-piece reading is the normative exact-text reading. If it
cannot produce the registered observation-complete natural-Latin worlds, this
run stops as `MODEL_SCOPE_UNDERSPECIFIED_OR_INFEASIBLE`; it does not silently
widen `CORE` to a literal run or invent aggregate merge roles. Any such repair
requires a separately named model version.

## 3. Nonwhole card transition

GDT609 permits paid pair-specific nonwhole overrides but supplies no separate
FST state for them. GDT613 declares one nonwhole `short` card to occupy one
`SYLLABIC` core. Whole cards occupy `WHOLE`. This choice is compiled into the
model artifact and must be reported as an implementation choice, not a quoted
historical rule.

## 4. Language-model boundaries

The GDT612 fourth-order model trained one continuous word stream but evaluated
each chunk from a three-boundary reset. GDT613 trains and scores the same reset
context: three start boundaries, the word, and one end boundary. The bridge
audit reports both legacy-compatible and corrected scores so the change cannot
manufacture an unlabelled win.

## 5. Tree identity

Hashing GDT608 and separately loading a GDT612 unit table is insufficient.
The preparer now checks all 64 ranks, left/right unit names and IDs, merged
names and primitive leaf sequences before emitting `compiled_model.json`.

## 6. Fixed length deck has insufficient one-character capacity

The registered deck contains 23 nonempty length-one cards.  The frozen
synthetic train and held Latin blocks contain 22 distinct characters; only 21
meet the registered minimum of eight train word types and sixteen held events.
This is a second pre-world infeasibility independent of grammar scope.  GDT613
does not silently lengthen a card.  A successor must move at least two
functional one-character cards to length two and register the new deck.

The same audit finds a separate WHOLE-state deficit.  Even granting either of
the two globally eligible connectors independently at both chunk edges, a
fixed WHOLE output of length 3/4/5/6 can reach at most 5/4/3/3 frozen train word
types.  The registered threshold is eight for every scored parameter.  A
successor must therefore change the WHOLE transition (for example to an
embeddable macro core) or register a weaker exposure rule; core runs alone are
insufficient.

## 7. Literal-before-context parser arm

The first implementation checked atomic `LITERAL` before the longer
`LITERAL CONTEXT_MARK` alternative, making the latter unreachable.  This was
found before publication of a GDT613 result.  Both exact and diagnostic bridge
parsers now test the two-piece alternatives first.  The structural solver was
unaffected because it enumerated both published alternatives directly; all
bridge legality counts were regenerated after the correction.
