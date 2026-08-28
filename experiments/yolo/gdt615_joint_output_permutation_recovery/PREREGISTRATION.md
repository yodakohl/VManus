# GDT615 prospective execution contract

Date: 2026-08-29

This contract is committed before any GDT615 primitive/output permutation is
solved or scored. GDT614's failed fixed mapping is an input and cannot be
reported as a GDT615 candidate. It remains inside the complete permutation
domain and is not manually excluded from the search space. Its published
GDT614 TRAIN-intersection-HELD minimum is 18. Recomputed under GDT615's
train-only selection protocol, it has 25/64 raw-supported merges and an exact
minimum cover of 15, so it remains a failing fixed negative control.

## Fixed versus variable

Fixed unchanged from GDT614:

- the 34 primitive IDs and their roles;
- the complete role-wise primitive output deck;
- four paid short and four paid macro outputs;
- the directed 98-unit/64-merge tree and left-then-right order;
- the V2 grammar, 21 transitions, macro side licenses, hosted contexts,
  edge-only layout null, qok paid-macro prohibition, and eight-card budget;
- Latin carrier train/held and LM A/B partitions;
- all card, merge, paid-child, focal, oracle, decoy, three-world, and blind
  recovery thresholds registered by GDT614.

Variable in Stage 0 only:

- the bijection from complete output cards to primitive IDs of the same role.

Output length travels with its card. Roles may not change, strings may not be
edited, and cards may not collide or be omitted. Each card moves as one
indivisible tuple `(card_id, role, output, derived length, side license and all
other licensing metadata)`; all-different is enforced on `card_id`. The exact
pools and ordering are sealed in `artifacts/REGISTERED_SEARCH.json`. The
selected binding is a newly optimized synthetic key, not a historically
attested key.

## Train design and held confirmation relations

Enumerate every distinct substring of length 1 through 12 separately from
frozen carrier train and held plaintext. `TRAIN_SUBSTRINGS` alone is visible to
the binding solver. `HELD_SUBSTRINGS` remains unavailable until the complete
primitive mapping and all three train worlds, including each world's actual
eight paid locations, have been serialized and hash-committed. No frequency
threshold, LM score, candidate word, or target value enters either relation.

For a proposed primitive binding, recursively concatenate primitive output
cards in each GDT608 merge's directed leaf order to obtain its raw render. A
direct source unit must occupy a contiguous plaintext interval, so membership
in the active partition's substring set is necessary unless a paid card
changes that node or one of its recursive merge descendants.

Let `core_hit[m]` be a Boolean for each of 64 named merge nodes. The Stage-0
existence formula is:

```text
same-role output cards form a bijection
sum_m core_hit[m] <= 8
for every merge u:
    raw_render(u) in TRAIN_SUBSTRINGS
    OR exists m in recursive_merge_subtree(u): core_hit[m]
```

Here `recursive_merge_subtree(u)` is inclusive: it contains `u` itself and
every merge-node descendant reached by recursively expanding its left and
right merge children. Primitive leaves are not selectable hit nodes. Thus a
hit node can cover exactly itself and its merge ancestors, never a sibling or
an unrelated branch. Repeated descendants are identified by merge ID rather
than equal rendered strings, and all 64 raw renders must be nonempty.

This remains a relaxation: it ignores grammar, transition placement, paid
types/outputs, child counterparts, ambiguity, and exact unit tiling. Failure
is therefore decisive; success only opens the stricter stages.

## Solver and deterministic selection

The primary encoding uses finite card-index variables, role-wise all-different
constraints, recursive concatenation, exact membership in the hash-bound
`TRAIN_SUBSTRINGS` table, and 64 `core_hit` Booleans. A second implementation must
replay the published candidate and hitting minimum without importing primary
solver code.

Train-only selection hierarchy is exact and lexicographic:

1. maximize the number of raw renders already in `TRAIN_SUBSTRINGS`;
2. minimize the exact paid-subtree hitting number;
3. choose the lexicographically smallest output-card ID sequence in primitive
   ID order.

For the selected mapping, choose the lexicographically earliest
minimum-cardinality cover, represented as an ascending merge-rank tuple. This
`core_hit` tuple is a necessary-bound certificate, not the actual paid-location
choice. There is no frequency objective, adaptive fallback, incumbent pass, or
manual candidate choice. A timeout or incomplete optimality proof is
`SEARCH_INCOMPLETE` even if a feasible incumbent exists.

After the selected mapping and its bound certificate are committed, Stage 1
uses train only to choose exactly eight distinct actual paid merge locations,
the fixed four short plus four macro cards, all legal traces, and all tilings.
These actual locations need not equal the relaxed minimum cover. A complete
Stage-1 UNSAT proof is `MAPPING_BOUND_PASS__FULL_WORLD_INFEASIBLE`; timeout or
`unknown` is `SEARCH_INCOMPLETE`. Neither outcome permits a second Stage-0
mapping under GDT615.

Only after the complete three-world train bundle is committed is held revealed
exactly once. For every merge whose raw render is absent from
`HELD_SUBSTRINGS`, at least one of the same eight actual frozen paid locations
must lie in its recursive subtree, and all full held traces for all three worlds
must pass unchanged. Any failure is `HELD_BINDING_NONTRANSFER`; mapping, output
cards, paid locations, seed attempt, or world may not be changed inside GDT615.
Held counts never enter train objectives or tie-breaks. Trying a second mapping
or seeded world requires a new experiment ID.

`LM_B/lm_confirm` and every statistic derived from it are forbidden in Stages
0--2. Its later panels are confirmation relative to the GDT615 mapping/world
search, not a claim that the inherited deck was never examined earlier in the
research history. GDT614's deck design inspected the old synthetic held block
and its published held supports motivated this permutation route. GDT615 is
algorithmically train-only for its new binding and world, but it is not
historically pristine held discovery.

Once the deterministic Stage-0 binding and bound certificate are committed,
any Stage-1/2, held, oracle, null, or recovery failure terminates GDT615. No
next-best binding, alternate bound certificate, revised paid location, or
fallback result may be tried under this experiment ID.

The exact solver may run up to four wall-clock hours with up to 32 workers.
`unknown`, timeout, memory exhaustion, or an incomplete objective proof is
`SEARCH_INCOMPLETE`; it cannot establish global infeasibility. A complete
UNSAT proof for the existence formula is `NO_EIGHT_HIT_BINDING`.

## Mapping certificate

A Stage-0 pass publishes:

- all 34 primitive IDs, roles, output card IDs, values, and lengths;
- all 64 raw renders, recursive affecting subtrees, and train-substring
  membership flags in the pre-held certificate;
- the exact minimum hitting number and canonical minimum-cover certificate;
- solver status/statistics, complete input hashes, and a byte-stable rerun;
- an independent SAT replay at the minimum and UNSAT replay at minimum minus
  one;
- an independent full-space proof that no binding has a larger raw-support
  count, none tied there has a smaller cover minimum, and no lexicographically
  earlier card-ID prefix remains feasible under both optimal values. The
  independent implementation may not import the primary encoding or solver
  model.

After this mapping certificate is hash-committed, a separate pre-held train
audit may read raw carrier train and add per-render train-type counts. Those
diagnostics cannot alter the binding, objectives, or bound certificate.

Only `minimum <= 8` opens Stage 1. Separate Stage-1/2 artifacts publish every
world's eight actual paid locations and complete train traces. The later held
artifact adds held support and pass/fail for those already committed locations.
The chosen bindings and worlds stay immutable.

## Inherited full-world gates

Stage 1 constructs W0 with the registered GDT614 V2 grammar and requires one ordered,
multiplicity-preserving, span-bearing card trace plus a nonoverlapping
top-level unit tiling per train plaintext type. It must cover all 34
primitive cards, eight paid cards, 56 defaults, eight paid-child counterparts,
all 64 named merges in train, all 21 transitions, macro licenses, rank-42 focal
carriers, and train null-mass bounds. Primitive mapping, eight paid
locations, paid card assignment, and train parse selection are chosen on train
and committed before held encoding. The eight locations are distinct, receive
exactly four short and four macro cards, obey all macro/qok side restrictions,
have paid outputs distinct from their recursive child render, and leave every
default as the exact left-to-right effective-child concatenation.

Stage 2 constructs W1 and W2 with the registered seeds, equal-role/equal-length
permutation rule, distinctness rule, and 10,000-attempt ceiling. GDT615 overrides
GDT614's held-dependent paid-location objective: selection and acceptance use
only this exact lexicographic hierarchy: maximize minimum train-type exposure
over 42 cards; maximize minimum direct train occurrence over eight paid cards;
maximize total distinct labelled merge-node occurrences; then minimize the
tuple of merge ranks and card IDs. The held objective is omitted, not replaced.
The first train-passing seeded world is fixed. Complete failure
to construct W0/W1/W2 is `MAPPING_BOUND_PASS__FULL_WORLD_INFEASIBLE`; timeout or
an incomplete proof is `SEARCH_INCOMPLETE`. All three worlds, paid assignments,
and train traces are hash-committed together. Held is then opened once and must
satisfy every inherited held coverage/exposure/trace threshold without any
change, or the outcome is `HELD_BINDING_NONTRANSFER`.

Stage 3 runs the exact
twelve `LM A/B x train/held x event/type/focal` oracle panels, every declared
single and paired mutation, `que -> qua`, at least 100,000 decoys, and the core
order null. Stage 4 runs eight blind starts per world and requires at least
7/8 exact recoveries in each. The GDT614 thresholds cannot be weakened inside
GDT615.

## Outcomes and exclusions

- `NO_EIGHT_HIT_BINDING`
- `HELD_BINDING_NONTRANSFER`
- `SEARCH_INCOMPLETE`
- `MAPPING_BOUND_PASS__FULL_WORLD_INFEASIBLE`
- `OBJECTIVE_NON_IDENTIFYING`
- `OPTIMIZER_INSUFFICIENT`
- `SYNTHETIC_RECOVERY_PASS`
- `IMPLEMENTATION_OR_VALIDATION_FAILURE`

No outcome is a Voynich translation or meaning claim. No Voynich target,
target key, target glossary, aligned plaintext, f84, or f84r material may be
read.
