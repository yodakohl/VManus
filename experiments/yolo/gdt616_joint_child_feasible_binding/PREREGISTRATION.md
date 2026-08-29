# GDT616 prospective execution contract

Date: 2026-08-29

This contract is committed before any GDT616 binding, paid-location assignment,
train world, held score, or recovery result is computed. GDT615's selected
mapping is a failed prior result, not a GDT616 starting key or candidate
constraint. GDT616 returns the primitive/output binding and the eight actual
paid cards to one joint TRAIN-only search.

## Fixed inventory and access boundary

GDT616 keeps the GDT608 directed 98-unit/64-merge DAG and the complete GDT614
V2 role, output, grammar, transition, paid-card, macro-license, threshold, and
downstream recovery contracts. Exact source paths, byte counts, and SHA-256
digests are sealed in `artifacts/REGISTERED_SEARCH.json`.

Only the registered merge DAG, model/decks, transitions, TRAIN substring
relation, source units, synthetic TRAIN, and `lm_fit` may be used before the
three-world commit. The latter three are inherited transitively through the
hash-bound GDT615 input manifest. Synthetic held and `lm_confirm` remain
unreadable until all three complete TRAIN worlds have been serialized and
hash-committed. A stored digest is not permission to open a partition.

All Voynich target material, target keys, glossaries, candidate plaintext,
f84, and f84r are forbidden throughout GDT616. The GDT615 Stage-0 mapping and
its mapping commit are not GDT616 inputs.

## Variables and exact recursive model

Let `X[p]` assign one complete primitive output card to primitive `p`. `X` is
a bijection inside each of the eight fixed roles; card ID, output, length,
side license, and all metadata move together. Roles and strings cannot change.

Let `Z[m]` be `NONE` or one of the eight named paid cards for merge `m`. Every
paid card is used exactly once, no merge receives two cards, and therefore
exactly eight distinct merge locations are paid: four short and four macro.
These are actual paid locations, not GDT615's relaxed `core_hit` nodes.

In increasing GDT608 merge rank, define:

```text
eff(p)   = output(X[p])                                      for primitives
child(m) = eff(left(m)) || eff(right(m))                     for all merges
eff(m)   = paid_output(Z[m])             if Z[m] != NONE
         = child(m)                      otherwise
```

Concatenation is directed left then right. For every one of the 64 merges,
both `child(m)` and `eff(m)` must be nonempty members of the exact registered
TRAIN substring relation. Thus the unoverridden child span must exist even
when the node is paid; paying a parent never hides a missing child. Every paid
output must differ byte-for-byte from its node's `child(m)`. All 41 nonempty
card outputs remain globally distinct.

`qok` (merge rank 7) may receive a short card or remain default but may not
receive any paid macro. This is the exact registered prohibition; it is not
silently expanded to every longer `qok...` merge.

## Stage A — fail-fast joint necessary bound

Stage A solves the complete `X+Z+child+eff` formula above using TRAIN only. It
does not use grammar parses, carrier frequencies, held, an LM, or Voynich data.

- Complete exact UNSAT is `NO_JOINT_CHILD_FEASIBLE_BINDING` and terminates.
- SAT only opens Stage B. It freezes no mapping, paid location, or card.
- Timeout, `unknown`, or incomplete enumeration is `SEARCH_INCOMPLETE`.

For reproducibility a SAT run may emit one diagnostic witness by minimizing
the primitive card-ID sequence and then the sorted `(merge rank, paid card
ID)` tuple. That witness is never an incumbent for Stage B. Stage B must range
over the complete Stage-A-feasible space.

There is no raw-render support count, raw-support maximum, cover minimum,
frequency score, lexicon score, or GDT615 mapping distance in any GDT616
selection objective. All 64 child spans are hard constraints, not points.

## Stage B — integrated TRAIN-only W0 search

Stage B jointly selects `X`, `Z`, and the complete `W616_0` TRAIN traces over
the entire Stage-A-feasible space. A candidate passes only with one ordered,
multiplicity-preserving, span-bearing labelled trace and a nonoverlapping
top-level 98-unit tiling for every selected TRAIN type. Potential substring
support, card bitmasks, or mutually incompatible parses do not count.

The unchanged GDT614 V2 gates apply, including all 34 primitive cards, all
eight paid cards, all 56 defaults, all eight unoverridden paid-child
counterparts, all 64 named merges, all 21 transitions, the registered
train-exposure/null/focal-rank thresholds, collision rules, and exact grammar.

Macro licenses are enforced on the labelled trace, not approximated in Stage
A. `LEFT_HOST` requires another non-NULL core term immediately to the left in
the same core run; `RIGHT_HOST` requires one immediately to the right;
`STANDALONE_OR_LEFT_HOST` permits either a singleton body term or the
`LEFT_HOST` case. Prefixes, suffixes, connectors, and edge NULLs are not macro
hosts. These rules apply to primitive `M01=ibus` and paid `macro:1..4` with the
exact license attached to each registered card. The exact-rank-7 `qok`
paid-macro prohibition remains hard.

Among complete passing W0 bundles, the exact lexicographic objective hierarchy
is:

1. maximize the minimum distinct TRAIN-type exposure over all 42 cards;
2. maximize the minimum direct TRAIN occurrence over the eight paid cards;
3. maximize total distinct labelled merge-node occurrences;
4. minimize the 34-card ID sequence in registered primitive order;
5. minimize the ascending `(merge rank, paid card ID)` assignment tuple;
6. minimize the canonical complete trace/tiling serialization.

Every earlier objective is fixed before the next is queried. Solver-dependent
incumbents, worker order, wall time, raw support, and nondeterministic solver
statistics cannot break ties. The primary must prove the exact optimum; an
independent implementation must replay the witness and exclude every better
objective value and earlier prefix. Exact Stage-B UNSAT is
`JOINT_BOUND_PASS__W0_INFEASIBLE`; incomplete proof is `SEARCH_INCOMPLETE`.

## Three worlds and reveal order

Only the canonical complete W0 opens W1 and W2. Starting at seeds 61601 and
61602 respectively, output cards are permuted only inside equal-role,
equal-length classes. Attempts advance by two and stop after 10,000 per world.
Every attempt reruns the same recursive X/Z gates, actual paid-card assignment,
full TRAIN traces, licenses, thresholds, and Stage-B objective/tiebreaks. The
first passing attempt is fixed. No output, role, partition, or threshold may be
changed.

The three worlds must differ by at least 24/34 primitive assignments and by at
least six of eight paid locations or outputs, exactly as inherited from GDT614.
Failure to construct both contrast worlds is
`THREE_WORLD_GENERATOR_INFEASIBLE`.

W0, W1, and W2, including mappings, eight actual paid assignments, labelled
TRAIN traces, tilings, objective certificates, and input hashes, are serialized
and hash-committed as one bundle. Before that commit, neither synthetic held nor
`lm_confirm` may be opened. After it, held is revealed exactly once and must
pass unchanged; no mapping, paid card, parse, seed attempt, or world may be
retuned. A failure is `HELD_BINDING_NONTRANSFER`. Only a held pass opens
`lm_confirm` and the inherited GDT614/GDT615 oracle and recovery gates.

## Stop outcomes and claim ceiling

- `NO_JOINT_CHILD_FEASIBLE_BINDING`
- `JOINT_BOUND_PASS__W0_INFEASIBLE`
- `THREE_WORLD_GENERATOR_INFEASIBLE`
- `HELD_BINDING_NONTRANSFER`
- `SEARCH_INCOMPLETE`
- `OBJECTIVE_NON_IDENTIFYING`
- `OPTIMIZER_INSUFFICIENT`
- `SYNTHETIC_RECOVERY_PASS`
- `IMPLEMENTATION_OR_VALIDATION_FAILURE`

The exact search may use at most 32 CPU workers and 43,200 wall-clock seconds.
A feasible incumbent cannot pass without a complete optimality certificate.

Even `SYNTHETIC_RECOVERY_PASS` validates only a synthetic Latin-carrier
generator and recovery instrument. It assigns no Voynich unit, sound, word,
language, plaintext, object, operation, or meaning and does not authorize a
target run under GDT616.
