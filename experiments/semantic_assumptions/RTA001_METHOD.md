# RTA001 — graph-to-text operator induction

Status: frozen before final leave-one-physical-folio-out scores were computed.

## Question and claim ceiling

RTA001 tests whether already established author-visible relations between text
positions correspond to a small transferable library of anonymous formal
transformations.  It does not test whether an object has a name or whether a
visible attribute has a prefix.  Retained operators are named `OP01`, `OP02`,
and so on.

A pass may establish only that anonymous formal transformations predict held
out author-visible relation panels.  It cannot assign words, sounds, parts of
speech, a language, cipher values, object names, qualities, directions,
seasons, elements, plaintext, or translation.

## Frozen inventory

The inventory is built without reading a transcription surface.  It retains:

1. complete ordered arrays in the published special-circle text-blind
   inventory, with cyclic successor edges and complete dihedral symmetry;
2. numbered lines inside the twelve author-drawn f67r2 moon sectors;
3. the ten explicitly annotated f75v two-line label stacks; and
4. the published native-visual Rosettes five-record by three-row layout.

Incomplete cycles, f57v inner/outer proximity matches, ambiguous f84r figure
ownership, and circle-band pairings without an author-visible correspondence
are excluded.  The physical folio, not an individual edge, is the holdout unit.

## Exact edge programs

The five representations are evaluated separately:

- manual-transcription character surface;
- STA family symbols;
- exact STA members;
- literal roots;
- construction roles with word and outer-boundary markers.

ZL3b, IT2a, and RF1b are alternate deterministic readings of the same object.
They are never treated as independent samples.  Each available reading gets a
separate exact program; its integer feature vector is averaged with the other
available readings into one edge vector before any fit or score.  The stored
integer vector uses six times this mean (`sum * 6 / available_readings`), which
is exact for two or three readings; distances are divided by six.  A missing
reading is retained as missing and contributes neither a zero vector nor an
imputed reading.

The exact CPU dynamic program and DSL are frozen in
`RTA001_OPERATOR_DSL.md`.  Every minimum cost and its number of optimal
alignments are retained.  The canonical rendering is used only to construct a
reproducible atom vector.

## Discrete operator model

For a representation and training fold, an edge vector contains:

- counts of generic `(opcode, zone, argument-class)` atoms;
- signed target-minus-source counts for each training-vocabulary token;
- source length, target length, and boundary edit counts.

Unknown held-out literals map to one frozen `UNSEEN_LITERAL` coordinate.  No
embedding or neural hidden state enters a result.

An operator is a training-edge medoid and therefore has an explicit DSL
program.  Weighted Manhattan distance is used only for discrete proposals and
hard-EM medoid updates.  The scientific residual is an exact add-one
categorical code for every integer program coordinate inside the assigned
operator.  A training edge uses its leave-one-out count; a held-out edge uses
the frozen full training count.  Each cluster pays `U(number of observed
values)` for every coordinate.  Thus a larger library cannot receive an
uncalibrated nearest-medoid advantage on unrelated data.

For a codebook of size `K`, the exact CPU objective is

```
L = U(K)
  + sum_k (U(nonzero_k) + explicit_medoid_description_bits_k)
  + E * ceil(log2(K))
  + sum_e residual_bits(e, z_e)
  + 2 * composition_residual_bits
  + 2 * cycle_closure_residual_bits
  + 2 * rectangle_commutation_residual_bits.
```

`U(n)=2*floor(log2(n+1))+1`.  Composition residual compares the signed token
delta of a direct row-skip operator with the sum of the two adjacent-row
operator deltas.  Cycle residual is the weighted L1 norm of the sum of medoid
deltas around each complete cycle.  Rectangle residual is evaluated only for
a rectangle registered in the text-blind graph.  The initial graph has no
admissible rectangle; its rectangle term and diagnostic are exactly zero.

The frozen codebook grid is `K = 2,4,6,8,12,16,24,32`, truncated at the number
of training edges.  `K`, representation, and all symmetry preferences are
chosen using training panels only.  Ties select smaller `K`, then the more
abstract representation in this fixed order: construction, root, family,
member, surface.

## Symmetries

Complete cyclic panels admit the registered dihedral group.  Rotations only
rename a complete successor edge set and are marginalized analytically.
Reflection reverses every edge in a panel.  Training evaluates both global
orientations for that panel and pays one bit for the orientation.  A held-out
cycle is scored by the two-orientation log code (`min(code)+1`); no held-out
orientation is fed back into training.  Row-panel column/record reversals only
rename complete edge bundles and are marginalized without a fitted parameter.

## GPU proposal and CPU verification

`rta001_cuda_proposer.cu` batches weighted Manhattan assignment for many
discrete medoid codebooks and random restarts.  It writes only proposed medoid
indices and seeds.  Before use, the runner benchmarks one representative
training matrix on deterministic CPU and CUDA.  CUDA is used only when it is
available and either achieves at least a 1.25x speedup or permits at least four
times as many restarts within the benchmark budget.  Otherwise the exact CPU
search is used and the benchmark is reported.

The frozen search supports 64 restarts per `(fold, representation, K)` through
the CUDA proposer or 16 through the CPU proposer. The retained calibration may
instead use process-parallel exact CPU proposals when that is faster end to
end; the artifact records the actual backend. Ten hard-EM iterations use seeds
derived from SHA-256 of the fold, representation, `K`, and restart.  The CPU independently reconstructs every
proposal, assignment, medoid update, residual, algebra term, and MDL value.
Hard-EM updates each cluster to its exact minimum-total-distance training
medoid, with the smallest training row breaking a tie, until stable or ten
iterations.  Only the CPU-reconstructed winner can enter the result.

## Synthetic calibration

Synthetic graph-text worlds are generated without manuscript strings.  They
use the registered topology sizes and an artificial twelve-symbol alphabet.
The frozen registry contains:

- 32 unrelated null worlds;
- 8 worlds each with 2, 4, 6, and 8 transferred operators;
- 8 local-only worlds;
- 8 one-panel-only worlds;
- 8 length/frequency-confounded worlds;
- 8 true-composition worlds;
- 8 edge-fit/cycle-violation worlds; and
- 8 reflected/rotated transferred worlds.

For planted worlds the primary calibration label is the known operator ID up
to a Hungarian-free exhaustive label permutation for `K<=8`.  A calibration
pass requires all three:

1. no more than 1/32 unrelated null worlds has positive held-out gain;
2. no local-only or one-panel-only world has positive gain on more than two
   physical holdouts; and
3. at least 28/32 transferred 2--8-operator worlds have positive held-out gain
   and at least 75% planted assignment recovery; and
4. the true-composition worlds have strictly lower mean cycle residual than
   the recurring edge-fit/cycle-violation controls.

If calibration fails, final real held-out scoring is forbidden until the
method is changed and versioned.  Real results are not used to repair a failed
calibration.

## Whole-folio held-out evaluation

Each of the nine physical folios is held out in turn.  No edge on that folio
enters codebook induction, `K`, representation, weights, vocabulary, or
symmetry choice.  The primary model description length for a held-out edge is
the operator assignment code plus its residual under the training library.

Required baselines are:

1. one edge-independent training medoid;
2. one medoid per relation type;
3. one medoid inside exact `(relation type, source length,
   target length)` cells, backing off deterministically to relation type;
4. same-page wrong-target pairing;
5. topology-preserving target-node permutation;
6. symbol-frequency and sequence-length preserving target shuffle; and
7. a panel-specific codebook trained with the held-out panel, reported only as
   a diagnostic upper bound.

Each baseline medoid pays the same explicit library code as an operator medoid.
The strongest admissible baseline for the primary comparison is the minimum
training MDL among baselines 1--3, selected separately inside each training
fold without using held-out outcomes.  Baselines 4--6 form the null and
specificity diagnostics, not a favorable baseline selection.  Baseline 7 is
never eligible for the primary gain.

## Frozen primary statistic and null

The one primary statistic is the equal-folio mean

```
gain = strongest_admissible_baseline_bits_per_edge
       - trained_operator_library_bits_per_edge.
```

Within a folio, readings are averaged within edges, edges within panels, and
panels equally.  Folios are then weighted equally.

The primary null has 4,096 keyed worlds plus the observed world.  In each null
world, targets are permuted as indivisible node records within every panel:
cycles use a nonidentity rotation or reflection-offset mapping; repeated row
systems permute target records/columns while preserving target row position;
all three readings move together.  Source/target lengths and token
frequencies are held fixed.  Fold-trained libraries and baseline choices stay
fixed.  The exact inclusive CPU p-value is

```
p = count(null_gain >= observed_gain) / 4096.
```

The result is positive only if `gain > 0` and `p <= 0.01`.  Essential
robustness requirements are limited to: positive equal-folio gain on at least
seven of nine folios; at least one anonymous operator supported on three
physical folios in training and used on a held-out folio; and positive gain in
at least one abstract representation (family, root, or construction) after
removing exact literal-identity atoms.  These are robustness descriptions, not
additional independently optimized primary tests.

## Interpretation of failure

Failure closes this registered transformation resolution.  It does not show
that no operator system exists.  Per the route contract, the next route would
be latent grapheme/transcription-channel reconstruction, not another visual
binary-attribute or exact-label screen.
