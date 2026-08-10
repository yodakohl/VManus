# LRS001-R1 target-blind masked-record calibration specification

Status: **FROZEN_UNSCORED — TARGET-BLIND CALIBRATION ONLY**
Date drafted: 2026-08-10
Date frozen: 2026-08-10

## Question and non-duplicate boundary

Can a fixed instrument distinguish ordered, nonadjacent within-record content
from page vocabulary, exact record geometry, immediate-neighbour grammar,
unordered record content, and propagated first-order structure?

At target ordinal `j`, added content may use only physical ordinals `k` with
`abs(k-j) >= 2`.  `ORDER` must improve the proper held log score over both
`BAG`, which receives exactly the same distant groups without order, and
`NUIS`, which receives page, geometry, length and immediate-neighbour controls
but no distant group content.  No code may infer an alignment, choose a field
count, move a boundary, invent `K` columns, or name a slot.  This is therefore
not a rerun of the archived K18/K22/K26/K30, paragraph-ordinal, local-trigram,
exact-neighbour, or chained-line routes.

A future fully gated manuscript pass could establish only:

> Ordered nonadjacent content in corrected prose records predicts supported
> masked complete source-family forms across physical folios beyond page
> background, exact geometry, immediate neighbours, first-order grammar, and
> unordered record content.

It cannot establish a field, word, part of speech, sentence role, recipe,
language, sound, cipher, plaintext, or translation.

## Exact input isolation

Calibration may read only:

- `experiments/semantic_assumptions/results/lrs001r1_anonymous_geometry.tsv`, SHA-256
  `37f06364effab97140d50fd64984ee561ed84f9087866314db7fec4f059647df`;
- `experiments/semantic_assumptions/results/lrs001r1_anonymous_geometry.json`, SHA-256
  `0c251db4526f54a1b3bec15528f32a95c782d3a7d8f134ab49b6afb872bd1542`;
- `experiments/semantic_assumptions/LRS001R1_TARGET_BLIND_CALIBRATION_SPEC.md`;
- `experiments/semantic_assumptions/lrs001r1_core.py`;
- `experiments/semantic_assumptions/lrs001r1_synthetic.py`;
- `experiments/semantic_assumptions/run_lrs001r1_target_blind_calibration.py`;
- `experiments/semantic_assumptions/validate_lrs001r1_target_blind_calibration.py`; and
- `experiments/semantic_assumptions/LRS001R1_TARGET_BLIND_CALIBRATION_FREEZE.json`.

The runner must enforce those exact eight repository-relative paths, with no
extra path.  It may import the standard library and NumPy first, then must
install the audit hook before importing any repository module or reading any
repository file.  The five code/specification files must exist and be hash-bound by the
freeze before
the calibration freeze is made.  Invocation must supply the previously
published freeze SHA-256; the runner must hash the freeze bytes before parsing
and require exact equality.  The freeze object contains `experiment`,
`status`, `registration_commit`, decision literal
`AUTHORIZE_TARGET_BLIND_CALIBRATION_ONLY`, `bound_files` mapping exactly the
seven non-freeze paths above to lowercase SHA-256, and `outputs_absent`
containing exactly the two calibration destinations named below.  Every bound
hash must match and both outputs must still be absent.  It may not open the geometry validation
artifact, capacity JSON, drawing atlas, split source, geometry builder,
parser,
transcription/content table, target code, or target output.  Workers inherit
the already loaded geometry.  A fork-worker initializer must switch the audit
hook to deny every repository open, including otherwise allowed inputs; worker
scientific file access is therefore a hard stop rather than an unobserved
convention.

The geometry is label-free and pseudonymous, not privacy-anonymous.  Its
eligibility bit is surface-derived, but it supplies no real class identity or
context/target pairing.  The only class layout available to calibration is the
opaque symbol-count map `{1:3, 2:8, 3:23, 4:19, 5:10, 6:3}`.  Synthetic class
IDs are `T<m>_<c>` for zero-based `c`; they are not manuscript forms.

## Fixed 648 group block

The synthetic alphabet is `ABCDEFGHJKLMNPQRSTUVWXYZ`.  For every observed
geometry symbol count `m=1..11`, construct 24 unique prototype sequences.
Candidate `(m,c)` starts
at nonce zero, consumes SHA-256 bytes from
`LRS001R1|PROTO|m|c|nonce`, reduces bytes modulo 24, and takes `m` symbols.
Increment the nonce until the sequence is new at that `m`.

Map sequence `a_1...a_m` to the root-free 648 block:

1. 24 normalized family counts;
2. 24 first-family indicators;
3. 24 last-family indicators;
4. 576 normalized directed adjacent-family counts, zero for `m=1`.

The four block sums are `1,1,1,1` for `m>1` and `1,1,1,0` for `m=1` within
`1e-12`.  No learned embedding, PCA, image feature, root, or member code is
used.  Blocks, prototypes and row assignments may not be emitted.

## Synthetic primitives

All fixed and world-generation keys begin `LRS001R1|`.  Define

`U(s) = (int.from_bytes(SHA256(s)[0:8], "little") + .5) / 2**64`.

Only world-generation draw keys contain world family and world index.  Fixed
prototype and assignment domains do not.  All ordering is UTF-8 bytewise
lexicographic.  Categorical sampling takes the
first inclusive cumulative probability at least `U(key)`.  Hash-rank ties,
nonfinite numerics, unexpected classes, or prototype collisions after 10,000
nonces hard-stop.  Numerical work is NumPy `float64`; BLAS thread counts are
forced to one before NumPy import.  Up to 32 forked workers may process whole
worlds and must return registered order.

For pool size `Q`, define class direction
`u(Q,c)=(cos(2*pi*c/Q), sin(2*pi*c/Q))`.  `z(key)` is the unit direction at
angle `2*pi*U(key)`, and `R(L,k)` rotates a direction by
`2*pi*(k-1)/L`.  Given direction `v` and amplitude `A`, class logits are
`A*u(Q,c).v` followed by stable softmax and the registered draw.

Supported targets (which have `m=1..6`) draw from their opaque class count; other groups draw from
all 24 context prototypes of their observed symbol count.  A supported target
uses the same drawn prototype as its group block except in the four explicitly
registered falsifiers `ONE_SURFACE`, `ONE_POSITION`, `RANDOM_DONOR`, and
`REVERSED_MAPPING`.

## Events, page background and whole-donor bundles

TRAIN and CAL use every row with `supported_class_target=1`.  TEST uses rows
with both `supported_class_target=1` and `strict_test_movable=1`: exactly 1,784
targets in 445 target-bearing records, 118 strict cells, 40 pages and 21
folios.  Those cells contain 453 movable records in total; all 453 participate
in every donor bijection, including the eight records without a scored target.

For all three splits, reconstruct the strict-cell key exactly as
`(page, segment_group_count, code, segment_count, segment_index,
starts_after_drawing, ends_before_drawing, original_group_count)`.  TRAIN and
CAL store no cell ID, so this reconstructed tuple is their only cell identity.
For TEST, its canonical serialization and record count must exactly reproduce
the stored `strict_cell_id` and `strict_cell_record_count`; any mismatch stops.
The canonical cell string joins the eight UTF-8 values with byte `0x1f`; its
ID is literal `C` followed by the first 20 lowercase hex characters of
`SHA256("LRS001R1|C|" + canonical_cell_string)`.  The count is the number of
distinct TEST records with that tuple.

For every split/page/strict-cell, compute one page-background 648 vector from
all groups on that page whose records are **outside the entire strict cell**.
If `R` such records remain and retained record `r` has `G_r` groups, each of
its groups has weight `1/(R*G_r)`; the background is their weighted sum.  It
is shared by every recipient and donor in that cell.  If no such group
exists, use an equal-folio TRAIN group-block mean after excluding every TRAIN
record in the current reconstructed cell.  If that retained pool is empty,
stop.  For retained TRAIN group `t`, use weight
`1/(F * P_f * R_p * G_r)`, where `F` is the number of retained physical
folios, `P_f` the number of retained pages in its folio, `R_p` the number of
retained records on its page, and `G_r` the number of groups in its record;
renormalize weights to sum one.  CAL/TEST cells have no TRAIN records, but use
the same definition.  This prevents recipient or donor records from entering
their own page nuisance and restores exact within-cell exchangeability.

Under any assignment a recipient supplies only its synthetic target class,
target symbol count, target ordinal, and strict-cell metadata.  The assigned
donor supplies the entire content bundle: immediate left/right blocks and
lengths, every distant block, and every distant length.  Never combine
recipient neighbours with donor distant content.  Donor position `j` is never
a predictor; donor `j±1` appears only in `NUIS`; only `abs(k-j)>=2` appears in
`BAG` or the content part of `ORDER`.

## Fixed BAG and DCT order contrasts

For donor record length `L` and recipient target ordinal `j`, let
`D={k:1<=k<=L, abs(k-j)>=2}`.  `BAG` is the arithmetic mean of donor blocks in
`D`.

For contrast `r=1,2`, start with
`v_r(k)=cos(pi*r*(2*k-1)/(2*L))` on `D`.  Center it on `D`, Gram–Schmidt it
against earlier accepted contrasts, and normalize to Euclidean norm one.
A residual norm at most `1e-12` yields an all-zero unavailable contrast.
Every accepted contrast sums to zero within `1e-12`.  Content contrast `r` is
`sum_k v_r(k)*block(d,k)`.  The identical weights applied to
`log1p(symbol_count(d,k))` are ordered length controls and belong to `NUIS`,
not to added content.

The registered order rank is `q in {1,2}`.  `ORDER` receives BAG plus the
first `q` content contrasts.  These are fixed physical-coordinate contrasts,
not selected columns or semantic slots.

## Model designs

TRAIN defines all categorical levels and numeric transforms.  Unseen levels
map to an explicit `OTHER`; no TEST level can create a column.

`NUIS`, in fixed order, contains:

1. one-hot recipient Currier, section, hand, code, record length, target
   ordinal, segment count/index, both drawing flags, original group count, and
   target symbol count;
2. the fixed cell-excluded page-background 648 block;
3. donor immediate-left then immediate-right 648 blocks, zero if absent;
4. `log1p` of their lengths, zero if absent;
5. distant mean `log1p` length and both DCT ordered-length contrasts.

`BAG` appends the distant mean 648 block.  `ORDER(q)` appends BAG and the first
`q` 648 content contrasts.  Physical folio/page/IDs/split/cell ID, target
class, target block, and donor position `j` are never predictors.

For each design and target symbol-count head, compute exact five-level
hierarchy weights.  In the head's event set let `F` be its folio count, `P_f`
the page count in folio `f`, `C_p` the strict-cell count on page `p`, `R_c`
the target-bearing record count in cell `c`, and `T_r` the target count in
record `r`.  Target weight is
`1/(F * P_f * C_p * R_c * T_r)`; these weights sum one and are rescaled to the
head's event count.  On TRAIN only, weighted-center every
feature, divide by weighted population SD, and drop SD at most `1e-12`.
Reuse the exact columns/center/scales on CAL, TEST and the final TRAIN+CAL
refit.

## Six deterministic diagonal-LDA heads

Fit one head per target symbol count.  For class `c`, weighted mean is `mu_c`;
the pooled within-class diagonal variance is

`v = sum_i w_i*(x_i-mu_yi)^2 / sum_i w_i`.

Add registered ridge `lambda in {.25,1,4,16}` to every standardized variance.
Smoothed prior is
`pi_c=(.5+sum_i w_i*[y_i=c])/(.5*C_m+sum_i w_i)`.
The common-covariance diagonal-LDA logit, omitting the class-common quadratic,
is

`x @ (mu_c/(v+lambda)) - .5*sum(mu_c^2/(v+lambda)) + log(pi_c)`.

Apply stable softmax within the target-length head, clamp probabilities below
`1e-6`, and renormalize.  The proper score is natural log probability of the
true synthetic class.  A true-class pre-clamp probability below `1e-6` is
floor-dominated.  Missing classes, nonfinite values, negative variances, or a
head with fewer than two candidates hard-stop.

## CAL selection and refit

For every `(q,lambda)` in `{1,2} x {.25,1,4,16}`, fit NUIS, BAG and ORDER on
TRAIN and score self-donor CAL.  Aggregate log scores by the five-level
hierarchy.  Compute CAL `ORDER-BAG` and `ORDER-NUIS`.  Select lexicographically
by: largest minimum of the two gains; largest ORDER score; smaller `q`; larger
`lambda`.  Ties use tolerance `1e-12`.

Stop before TEST unless both selected CAL gains are strictly positive, every
head is finite, and every model has at most 5% floor-dominated CAL targets.
Then refit class priors, means and pooled variances once on TRAIN+CAL using the
already frozen TRAIN columns/centers/scales.  TEST fits/selects nothing.

## 8,192 synchronous whole-record assignments

Assignment row zero is the identity.  For rows `a=1..8191`, within each strict
TEST cell sort recipients, then sort donors by
`SHA256("LRS001R1|ASSIGN|"+a+"|"+retry+"|"+cell_id+"|"+donor_id)` and map recipient rank
to donor rank.  Hash ties stop.  Each cell map is bijective.  Fixed points are
allowed and derangements are never forced.  Start `retry=0`; if the complete
global map duplicates an earlier row, increment the row-local retry and rebuild
every cell until unique, stopping at retry 10,000.  All 8,192 global map rows
must be unique over the exact 453-record donor panel and the retry vector is
hashed.  In canonical C-order little-endian int64 serialization the map SHA-256
is `48a20b6b16f38f7cfab037cae72da8d24ff2f2f4cdcf1c6e08945ab5dc6dc7e6`;
the retry-vector SHA-256 is
`de2f256064a0af797747c2b97505dc0b9f3df0de4f489eac731c23ae9ca9cc31`,
with maximum retry zero.  The same map supplies every target ordinal, donor bundle, model,
channel and robustness view.

Fit no model during assignments.  Precompute each target/eligible-donor log
score inside its cell and then perform indexed lookup only.

For target `t` and assignment `a`:

- `delta_OB = logp_ORDER(y_t|donor_a) - logp_BAG(y_t|donor_a)`;
- `delta_ON = logp_ORDER(y_t|donor_a) - logp_NUIS(y_t|donor_a)`.

Aggregate target means inside recipient records, records inside strict cells,
cells inside pages, pages inside folios, and folios equally.

For channel `c`, null rows are `1:8192`.  Use their population mean and SD
(`ddof=0`).  Standardize observed and null effects.  For each null row set
`M_a=max(Z_a,OB,Z_a,ON)`.  Conservative maxT value is

`p_c=(1+count(M_a >= Z_obs,c-1e-12))/8192`.

Both channels must pass; BAG-NUIS is descriptive only.
Zero or nonfinite channel null SD, standardized value, or maxT value is a hard
stop before any decision is emitted.

## Frozen decision gates

The identical `passes()` function governs synthetic and future manuscript
worlds.  Set `TOL=1e-12`.  For every non-strict minimum gate compare
`value >= threshold-TOL`; for every maximum gate compare
`value <= threshold+TOL`.  Strict-positive CAL, folio and deletion gates use
literal `>0`.  The position lower exclusion uses `value > -0.01+TOL` because
the boundary itself is forbidden.  Hash equality, counts and Boolean gates
have no tolerance.  Both channels require:

1. positive CAL gain;
2. TEST effect at least `+.030000` nat/target;
3. maxT `p<=.01` and `Z>=3`;
4. at least 16/21 positive folios;
5. every leave-one-folio-out effect positive;
6. maximum absolute folio contribution fraction at most `.20`;
7. Currier A and B each at least `+.010000`, weaker/stronger at least `.25`;
8. sections B, H and S each at least `+.010000`, balance at least `.25`;
9. record-length bands 5–8 and 9–12 each at least `+.010000`, balance `.25`;
10. target-position tertiles: at least two at `+.010000`, none at or below
    `-.010000`;
11. every leave-one-class-out effect positive and maximum absolute class
    contribution fraction at most `.20`;
12. after deleting every synthetic record signature duplicated anywhere in
    its split, at least 1,500 TEST targets/20 folios remain, both effects are
    at least `+.010000`, and all folio deletions remain positive;
13. finite normalized probabilities and at most 5% floor-dominated observed
    TEST targets;
14. exact frozen 66 classes, six heads, 1,784 targets, 445 target-bearing
    records, 118 cells, 40 pages and 21 folios.

Subgroup effects recompute the same target→record→strict-cell→page→folio
hierarchy after subsetting, with all five counts rederived.  The minimum 100
target gate applies only to each Currier view, each B/H/S section view, each
record-length band, and each target-position tertile; leave-one-class and
leave-one-folio gates use their explicitly defined remaining panels.  Target
position band is `min(2,floor(3*(j-1)/(L-1)))`.  Folio/class contribution
fractions use full-panel normalized hierarchical weights.  For channel values
`x_t` and full-panel weights `h_t`, folio contribution is
`c_f=sum_{t in f} h_t*x_t` and class contribution is
`c_y=sum_{t:class(t)=y} h_t*x_t`; the registered fraction is respectively
`max_f |c_f| / sum_f |c_f|` or `max_y |c_y| / sum_y |c_y|`.  Zero or
nonfinite denominators fail.  Complete physical reversal and class-label permutation must preserve
aggregate scores, p-values, gates and decisions within `1e-10`; row-order
permutation must be byte-exact after canonical sorting.

Invariance controls conjugate an already generated world rather than rehashing
it.  Row-order permutation reverses the canonical UTF-8 group-ID order and then
canonical-sorts before comparison.  Record renaming maps the `r`th canonical
UTF-8 record ID to the ID at rank `N-1-r` and carries all draws, prototypes,
labels, and donor maps without rehashing.  Class permutation maps `c` to
`(c+1) mod C_m` separately in each symbol-count head, relabels both true and
logit coordinates, and leaves predictor blocks fixed.  Physical reversal maps
each ordinal `k` to `L+1-k`, maps target `j` likewise, keeps every group
prototype sequence indivisible, swaps left/right neighbours, and recomputes
the DCT contrasts.  Strict-cell metadata are held fixed and the donor map is
carried through rather than redrawn.  All three models are refit on the
conjugated TRAIN/CAL view.

## Target-free worlds

`MASTER=20260810`.  Every `world` below is the zero-based index local to its
named family.  Register exactly 208 worlds: 64 `NULL`, eight
`ORDER_FULL`, eight `ORDER_REDUCED`, then eight for each of these 16 families:

`PAGE_TOPIC`, `GLOBAL_FIXED_COLUMN`, `LENGTH_BY_COLUMN`, `CODE_DRAWING_STATE`,
`ORDERED_LENGTH_SHAPE`, `UNORDERED_BAG_TOPIC`, `PURE_FIRST_ORDER`,
`ONE_FOLIO`, `ONE_CURRIER`, `ONE_SECTION`, `ONE_POSITION`,
`ONE_RECORD_LENGTH`, `ONE_SURFACE`, `EXACT_DUPLICATE_ONLY`, `RANDOM_DONOR`,
`REVERSED_MAPPING`.

World family and index enter every world-generation draw domain, but never the
fixed prototype or assignment domains.  Default independent group draw is
`z(group_id)` at amplitude `1.0`.  Intended plants use
`R(L,k)z(record_id)` at amplitude `3.0` (FULL) or `2.0` (REDUCED), distributed
over all splits, folios, Curriers, B/H/S, record lengths, position bands and
classes.

Except in `EXACT_DUPLICATE_ONLY`, complete ordered prototype-index signatures
must be unique inside each split.  Generate records in lexicographic ID order;
on collision increment a record-local nonce included in every group draw and
regenerate that record, stopping at nonce 10,000.

The exact world key is
`LRS001R1|WORLD|20260810|<family>|<decimal-index>|<purpose>|<parts...>`.
Parts are unescaped decimal integers or literal geometry strings joined by
`|`.  Directions and categorical draws use distinct purposes.  Ordinary FULL
uses `RECORD_DIRECTION|record_id`; ordinary NULL uses
`NULL_DIRECTION|group_id`; their categorical draw is
`GROUP_DRAW|group_id|nonce`.  The concentrated-context purposes are exactly
`PAGE_DIRECTION`, `COLUMN_DIRECTION`, `LENGTH_COLUMN_DIRECTION`,
`CODE_DRAWING_DIRECTION`, `LENGTH_SHAPE_CONTEXT`, and `BAG_DIRECTION` with the
arguments shown below.  Separated targets use `TARGET_NULL_DIRECTION` where
needed and `TARGET_DRAW|group_id|nonce`.  First-order purposes are
`FIRST_ORDER_INITIAL_DIRECTION`, `FIRST_ORDER_TRANSITION`,
`FIRST_ORDER_INDEPENDENT_DIRECTION`, and `FIRST_ORDER_DRAW`.  Duplicate FULL
draws use `DUPLICATE_FULL_DRAW`; collision nonces enter only categorical draw
keys, never direction keys.

Adversarial generation is fixed:

- PAGE_TOPIC: `z(page)`, amplitude 3, no record rotation.
- GLOBAL_FIXED_COLUMN: `z(L,k)`, amplitude 3.
- LENGTH_BY_COLUMN: `z(L,k,symbol_count)`, amplitude 3.
- CODE_DRAWING_STATE:
  `z(code,segment_count,segment_index,starts_after_drawing,
  ends_before_drawing,original_group_count)`, amplitude 3.
- ORDERED_LENGTH_SHAPE: context direction `z(k,symbol_count)`; target direction
  is the normalized pair of odd/even sums of `log1p` lengths; amplitude 3.
- UNORDERED_BAG_TOPIC: `z(record_id)` at every ordinal, amplitude 3.
- PURE_FIRST_ORDER: position one is an independent NULL draw at amplitude 1;
  at every later position use the previous chosen prototype's unit direction
  at amplitude 3 with probability `.8`, otherwise an independent NULL
  direction at amplitude 1, using distinct transition and categorical-draw
  hashes.
- ONE_FOLIO: every TRAIN/CAL record is FULL.  In TEST, order the physical
  folios containing movable targets by UTF-8 bytes, select
  `world mod test_folio_count`, make only that folio FULL, and make every other
  TEST folio NULL.
- ONE_CURRIER: FULL only in A for even worlds and B for odd, NULL elsewhere.
- ONE_SECTION: FULL only in B/H/S selected by `world mod 3`, NULL elsewhere.
- ONE_POSITION: FULL target draw only in position band `world mod 3`; contexts
  are FULL and other target draws NULL.
- ONE_RECORD_LENGTH: FULL only in short 5–8 for even worlds and long 9–12 for
  odd worlds, NULL elsewhere.
- ONE_SURFACE: order opaque classes by increasing `(symbol_count,class_index)`
  and let `s=world mod 66`; contexts are FULL.  For a supported target of
  length `m`, draw once from logits
  `u(C_m,c).z(group_id) + 3*[global(m,c)=s] *
  u(C_m,c).R(L,k)z(record_id)` using stable softmax.  Thus exactly one global
  class receives the concentrated ordered term while every class retains the
  same NULL term.
- EXACT_DUPLICATE_ONLY: lexicographically pair compatible records within each
  `(split, ordered symbol-count signature, ordered supported-target bitmask)`
  stratum; leave an odd final record unpaired.  Generate the first member of
  each pair with FULL group prototypes and matching target classes; the second
  copies that complete ordered prototype and target-class signature.  Thus
  both paired records are exact FULL duplicates, while unpaired records are
  unique NULL records.  A record signature is the ordered tuple of
  `(symbol_count,prototype_index)` at every physical ordinal.  Process pairs,
  then unpaired records, in UTF-8 record-ID order within split; on collision
  with any prior signature in that split, increment the pair/record
  categorical-draw nonce and regenerate, stopping at nonce 10,000.  The
  duplicate-deleted gate must fail.
- RANDOM_DONOR: TRAIN/CAL are FULL; TEST target directions use the next record
  cyclically inside their strict cell while contexts retain self directions.
- REVERSED_MAPPING: TRAIN/CAL are FULL; TEST target directions use
  `R(L,L+1-k)z(record)` while contexts use physical `R(L,k)z(record)`.

The four named target/context separation falsifiers must be flagged internally
and no other family may separate a target draw from its group prototype.

Calibration passes only with 0/64 NULL, 8/8 FULL, 8/8 REDUCED, and 0/8 for
every adversarial family.  It must also reject malformed cells, repeated or
split-crossing donors, nonzero-sum contrasts, use of target/donor position j,
recipient-neighbour mixing, record-only rather than cell-excluded page
background, undeclared reads, nonfinite probabilities, class loss, and output
overwrite.  Representative row-order, record-renaming, class-permutation and
physical-reversal controls must pass.

## Output and next authority

Calibration may atomically create only
`experiments/semantic_assumptions/results/lrs001r1_target_blind_calibration.json`
and
`experiments/semantic_assumptions/results/lrs001r1_target_blind_calibration.md`, with
refusal to overwrite.  Output contains only family/world aggregate summaries,
selected hyperparameters, named aggregate gate Booleans, exact synthetic-array
digests, selected-candidate-grid digests, assignment-effect digests, and
isolation facts—never row,
record, page, folio, class, position, prototype, block, coefficient, donor-map,
or score arrays.

World digests use canonical core geometry order: prototype and target-class
arrays are C-order little-endian int16, target-separation is C-order uint8,
record nonces are C-order little-endian int64, and copied record IDs are a
sorted compact canonical-JSON string array.  The eight CAL candidate summaries
are hashed as compact canonical JSON in registered `(ridge,q)` evaluation
order.  Each 8,192-value channel-effect vector is hashed as C-order
little-endian float64.  A CAL-stop world still publishes every synthetic digest
and its exact stop reason, with candidate/effect digests null only when they
were not returned by the stopped calibration routine.

Stage both complete files in one `mkdtemp` directory outside the repository,
fsync them, recheck both destinations absent, then install each with a
no-clobber hard link.  If the second install fails, unlink only the first file
created by this invocation; always remove the external staging directory.
No repository-side temporary path is permitted.  Recheck both calibration
output-absence facts and the audit log immediately before installation.

A nonimporting validator must independently rebuild every geometry guard,
prototype, block, fit, selection, assignment, statistic, gate and report before
any target registration.  Calibration failure closes this instrument before
target access.  Calibration success authorizes only a separately committed
target method, producer, production-free validator and hash freeze with all
target outputs absent; it does not authorize immediate manuscript scoring.
