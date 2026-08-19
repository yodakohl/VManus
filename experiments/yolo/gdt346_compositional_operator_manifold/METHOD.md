# GDT346 method — compositional operator manifold

Date: 2026-08-19

Status: `FROZEN_BEFORE_COMPATIBILITY_GRAPH_SCORING`

## Question

After freezing GDT345 V2's six fair target-coordinate marginal transition
models, is there a sparse, transferable compatibility graph between coordinate
deltas that improves complete-operator decoding? The purpose is to distinguish
a real low-order compositional manifold from marginal persistence, smoothing,
and exact-operator memorization.

No semantic alignment is run. Exact GDT327 tuples remain opaque and atomic;
PAGE_HOST is not factored or inspected.

## Frozen source and state

The sole event source is GDT345's corrected, independently validated,
f84-free transition inventory. Each occurrence supplies source state, target
state, the applied six-delta operator, exact atomic predecessor ID, and
independently observable boundary/layout context. The coordinates are:

`local_frame`, `inner_d`, `right_family`, `dy_closure`, `b3`, and canonical
wrapper. Supported `s@LINE_START` and `q@POST_DY` rendering was already
canonicalized by GDT345. No new normalization is permitted.

## Marginals and baselines

All target-value models retain GDT345 V2's fixed Jeffreys .5 global prior,
layout-to-global concentration 64, and source-to-layout concentration 32.
Predicted target values are translated mechanically to `KEEP` or
`SET:<value>` relative to the source.

1. `PLACEMENT`: target-coordinate marginals from observable layout.
2. `EXACT_PREDECESSOR`: six independent target coordinates conditioned on the
   opaque exact source tuple and layout.
3. `SOURCE_STATE_TABLE`: six independent coordinates conditioned on the full
   six-coordinate source state and layout.
4. `INDEPENDENT_MARGINAL`: each target coordinate conditioned only on the
   corresponding source coordinate and layout; this is corrected GDT345's
   factorized model and the mandatory comparison for compatibility.
5. `EXACT_OPERATOR_LEXICON`: a joint training-frequency code over complete
   six-delta operators, shrunk from exact layout to the global lexicon. It is a
   memorization ceiling only and never supplies a feature to another model.

## Sparse pair compatibility

The candidate graph contains the 15 unordered pairs among six delta
coordinates. For a candidate pair, training-only expected delta-pair counts
are calculated from the frozen independent marginals within boundary scope.
Observed/expected pair ratios use fixed shrinkage 16 toward ratio one. No exact
complete operator, target coordinate ID, target tuple, or target-derived
signature is a feature.

Within every outer fold, each candidate edge is independently fitted without
one training environment and scored on that held training environment. An
edge is admissible only if its isolated held gain is positive in aggregate and
in at least 60% of powered categories in each of two predeclared environment
families. LOFO uses register and hand; held-section uses register and hand;
held-register uses section and hand; held-hand uses section and register.
Categories require 50 events. At most three admissible edges are retained,
ranked by the smaller normalized gain across the two environment families.

Two graph decoders are fixed:

- `PAIR_GRAPH_NONWRAPPER`: only retained edges whose two endpoints are among
  frame, inner-D, right-family, DY, and B3;
- `PAIR_GRAPH_FULL`: every retained edge, including wrapper edges.

For a candidate complete target state, its unnormalized probability is the
product of the six independent marginal probabilities and all retained pair
energies. Exact enumeration over the frozen 3×2×6×2×2×8 = 1,152 target-state
space supplies the normalization, complete-operator rank, top-k, and exact
next-state prediction. Graph topology pays `log2(C(15,k))` bits in each outer
fold; both raw and selector-paid gains are reported.

`TRAINING_UNLICENSED_OPERATOR` mass is probability on complete delta vectors
never observed in that training fold. `TRAINING_UNLICENSED_STATE` mass is
probability on six-coordinate formal states never observed as a source or
target in that fold. These are empirical structural-license diagnostics, not
proof of authorial impossibility.

## Decisive recombination panel

The primary panel contains outer-LOFO events for which:

- the full source state is present in training;
- the full registered operator is present in training;
- their exact source-state×operator combination is absent; and
- each corresponding `(source-coordinate value, component delta)` was observed
  separately in training.

The count-only audit yields 1,027 events before scoring. Main endpoints are
held codelength, true complete-operator rank, top-1/top-5, exact next-state
recovery, and the two unlicensed-mass measures. All-event scores are secondary.

Support requires selector-paid `PAIR_GRAPH_FULL` improvement over independent
marginals, exact predecessor, and full state table on the decisive panel;
better mean rank, top-5 and exact recovery than independent marginals; at least
one retained non-wrapper/non-wrapper edge in 60% of folds; selector-paid
`PAIR_GRAPH_NONWRAPPER` improvement over independent marginals; positive graph
gain in at least 60% of folios and powered held sections/registers/hands; and
max-two p <= .05.

## Coupling-destruction null

The fixed held predictions are not refit. In each of 4,096 worlds, every true
delta coordinate is shuffled independently within held folio × exact layout ×
that coordinate's source value. Thus each coordinate's complete
source-conditioned marginal and layout distribution is preserved while
cross-coordinate co-occurrence is destroyed. The null evaluates full and
non-wrapper graph codelength gain over independent marginals and their max-two
statistic on the decisive panel.

## Herbal A diagnosis

Herbal A is not repaired post hoc. A graph is selected and fitted on all
non-Herbal-A records. In nested Herbal-A LOFO, Herbal-A marginal priors are
learned from the other Herbal-A folios and combined unchanged with that foreign
graph. A separate Herbal-A-only graph may select at most three edges using
inner held-folio transfer. Outcomes are:

- `SAME_GRAPH_DIFFERENT_PRIORS` if the foreign graph adds positive held gain
  with Herbal-A marginals and the local graph does not materially improve it;
- `NEW_COMPATIBILITY_EDGES_REQUIRED` only if the foreign graph is nonpositive,
  the local graph is selector-paid positive, and it selects a new edge;
- `NO_TRANSFERABLE_HERBAL_A_GRAPH` or `INSUFFICIENT_HERBAL_A_CAPACITY`.

## Decisions

- `COMPOSITIONAL_OPERATOR_MANIFOLD_SUPPORTED`
- `MARGINAL_TRANSITION_SMOOTHING_ONLY`
- `LOCAL_COMPATIBILITY_WITHOUT_TRANSFER`
- `INSUFFICIENT_CAPACITY`

If the graph does not transfer, the active conclusion is that GDT345 captured
marginal transition smoothing, and this route stops.

## Claim ceiling

At most GDT346 can establish a transferable low-order dependency manifold over
formal coordinate changes. It cannot establish linguistic morphology,
semantics, a word, sound, language, plaintext, translation, tuple equivalence,
PAGE_HOST factorization, or any f84 result.
