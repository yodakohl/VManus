# GDT1427 — one Syriac vocabulary, one forward table

## Decision before implementation

Inclusive budget: 2026-10-17 10:27:37–11:07:37 UTC, including predecessor
review, preparation, implementation, control, native evaluation, validation
and publication. At that checkpoint stop expansion and assess; no automatic
solver, corpus or control repair.

The unknown is whether the exact GDT1426 Syriac word inventory can cover all
59 unchanged IT2a f75v.38–42 groups under ONE source-letter-to-working-unit
function, without requiring their source-word neighbours to occur in the
reference book. GDT1426's independent relaxed diagnostic loses all paths at
position10 even with a different letter table allowed for every word. Its
failure therefore does not answer this separate shared-table question.
All59 local word domains were nonempty; that necessary observation does not
establish a jointly consistent table or a language reading.

GDT1424 tested a vocabulary-only Boolean encoding, but on eight different
sources and the old46/77 core. Its16 decisions remain UNKNOWN_OPEN after the
independent solver. GDT1425's different Hebrew convention stopped at control.
GDT1339 concerns source spaces and variable-width minim runs with a different
fixed inventory; it supplies no exclusion for this test. An independent
bounded preselection review found no executed identical Syriac case. GDT1426
remains failed, not repaired or superseded.

The smallest adequate test is one full59-group FWD case with exactly the same
source, units, paragraph and source-positive message as GDT1426. Remove ONLY
the external source-bigram condition. Use unchanged GDT1424 Boolean search
and unchanged GDT1421 row-join search at their declared caps.

## Contract and assumptions

- Source vocabulary: the2133 distinct forms in GDT1426 SOURCE_PROJECTION.json,
  all23 retained source codepoints; unchanged edited HUNAYNNET Hippocratic
  Aphorisms subset. GDT1426 source XML, independent extraction validation,
  provenance and license remain authoritative. No source extension or
  normalization change. Source record order and edges are unused here.
- Native packet: the exact cached59 whole groups, raw spaces and order of
  GDT1426 NATIVE_INPUT.json; fixed22 working units,15 active. The unique-
  segmentation parser is an assumed representation, not established glyph
  or sound values. One whole group equals one whole source written word.
- One globally fixed function maps each source codepoint to one working unit.
  Collisions are allowed; splitting, nulls, reversal, word-boundary changes,
  e/i collapse, unit changes and target omissions are forbidden. Logical
  source order FWD only. No E/C role or native word meaning is supplied.
- Every selected source word belongs to the fixed vocabulary. No adjacency,
  grammar, morphology, frequency or source-position constraint is imposed.
  Deduplicating native groups is valid for this existence question only.
- Control: exact same GDT1426 CONTROL_INPUT.json,32 groups, same source words
  and j%20 planted key. Search receives only groups, vocabulary and signs,
  never the planted key or aligned words. Both actual ANY-key searches and
  direct independent certificate replay must pass before native search.
  The planted table is a direct witness, not a substitute for search. Exact
  planted recovery and uniqueness are not gates and must not be inferred.
- Primary caps:10seconds preparation,20seconds solver, unchanged1424 code.
  Independent caps:20seconds,250000nodes,5000000checks, unchanged1421 code.
  One call per engine per control/native case. No retry after stop or UNKNOWN.

## Outcomes and reading consequence

Publish protocol, code and locked input identities before first control search.
An UNKNOWN control stops with zero native cases; an UNSAT planted control is
an invalid-control stop. A passing gate permits the one native case on both
engines. Each SAT must have a directly checked full59-word/key certificate.
SAT/UNSAT disagreement is invalid. Dual exhaustive UNSAT excludes this finite
source-vocabulary/representation/channel conjunction, not Syriac generally.
Without a valid SAT or dual exhaustive negative the decision is UNKNOWN_OPEN.

A valid SAT preserves each engine's first returned key and its complete inverse
source-word set for every distinct native group, with all59 positions retained.
This is unassessed capacity, not a preferred key or a connected Syriac reading:
without the edge condition source-word choices can vary independently by
position. Any later whole-passage language review must expose ambiguity,
missing arguments and every required insertion or reordering. GDT905/906's
word-list candidates failed grammar; GDT911 shows that grammar alone need
not select content. Concrete native word assignments still require existing
word profiles and claim-bearing priors. No English meaning is assigned here.

After dual UNSAT: do not attempt linguistic reading of this contract. After
SAT: review whole-message linguistic plausibility separately before selecting
any native meanings. After UNKNOWN/control stop: retain the open question,
do not automatically increase caps, repair engines or replace the source.
All outcomes retain0 confirmed word meanings and f84/f84r seals. No source
selection here is independent identification of the manuscript's language.
