# SME003 cross-folio concordance — target-free calibration freeze

Status: **FROZEN BEFORE CALIBRATION CODE; REAL MORPHOLOGY FORBIDDEN**

## Purpose and distinct estimand

SME003 tests cross-folio vector reproducibility: a distributed high-minus-low
paragraph profile learned on other physical folios must predict a held folio.
It is not a second individual-feature scan, a pooled classifier, or a relaxed
SME001 analysis. The calibration must decide whether this distinct estimand is
powered before any real ray/tail row is parsed or joined.

The strongest later claim remains an anonymous, cross-folio-reproducible
paragraph profile associated with marker morphology under the existing ordinal
pairing. No object ownership, ray/tail meaning, recipe class, number, feature
or root meaning, lexeme, plaintext, language, or translation follows.

## Frozen anonymous inputs

The calibration may read only the frozen anonymous paragraph matrix, feature
inventory, final SME003 preflight artifact, and this/source code. It must bind
their exact hashes. The 156-unit universe, 12 page sizes, seven physical
folios, three alternate readings, 83 eligible features, nuisance transform,
feature order, and analytic shrinkage are inherited unchanged from the
validated preflight. The 21 baseline transform digests must reconstruct before
any plant. Every planted matrix emits new transform digests; these are not
expected to equal baseline because row positions, nuisance fits, scales, and
covariances legitimately change.

The calibration code may not open or hash any morphology binding, capacity,
annotation, ray, tail, core, or color source. It encodes only the already
published aggregate capacity constraints:

- ray-like: 66 low, 83 high, seven ignored third states; every one of 12 pages
  and all seven folios is informative;
- tail-like: 133 low, 22 high, one ignored third state; exactly eight pages on
  exactly six folios are informative.

These counts generate new deterministic synthetic sequences. They are not the
real sequence, page counts, positions, or target join.

Every SME001/SME003 target artifact must be absent before and after every run.

## Deterministic synthetic label worlds

There are 64 paired null worlds with integer IDs `0..63`; power and adversarial
controls use IDs `0..7` from that same panel. Define `rank(domain,item)` as the
full SHA-256 digest of ASCII
`SME003_SYNTH_V1|world|domain|item`, ordered lexicographically as unsigned
bytes, with literal item as tie-break.

Target IDs are `RAY_LIKE` and `TAIL_LIKE`; stored state codes are `L`, `H`,
and `X` for ignored third. The driver-selection rank domain is
`DRIVER_SELECT|target|driver`; the sign domain is
`DRIVER_SIGN|target|driver`, with digest low bit zero mapped to `-1` and one to
`+1`.

Ray-like generation processes units in page/ordinal order. On every page the
lowest `RAY_LOW_ANCHOR|page` rank is protected low; the lowest
`RAY_HIGH_ANCHOR|page` rank among other units is protected high. The seven
lowest global `RAY_THIRD` ranks among unprotected units become ignored third
states. All other units default low. After retaining the 12 protected highs,
the lowest `RAY_REMAINING_HIGH` ranks among units that are neither a protected
low, an existing protected high, nor a third state become high until there are exactly 83. The result must
contain exactly 66/83/7 and both directed states on every page.

Tail-like generation omits the lowest `TAIL_OMIT_FOLIO`-ranked physical folio.
For each remaining folio its lowest `TAIL_PRIMARY_PAGE|folio`-ranked page is
selected. The two lowest `TAIL_EXTRA_PAGE`-ranked unselected pages belonging
to those folios are also selected, yielding eight informative pages. The
lowest `TAIL_THIRD`-ranked unit on a noninformative page is the ignored third
state. On every informative page the lowest `TAIL_HIGH_ANCHOR|page`-ranked
nonthird unit is protected high and the lowest `TAIL_LOW_ANCHOR|page`-ranked
other unit is protected low. All other units default low. Additional highs
are selected only inside the eight informative pages, in
`TAIL_REMAINING_HIGH` rank order, excluding protected lows and the third state,
and excluding existing protected highs, until there are exactly 22. The result must contain exactly 133/22/1, eight
informative pages, and six informative folios.

Generation must reject rather than repair any count, support, page/folio,
ordinal, or duplicate-unit violation. Canonical paired-label digests use ASCII
rows `world,target,page,ordinal,state\n` in world/target/page/ordinal order. No
paired synthetic world may equal another.

## Frozen fold transform and statistic

For every matrix presented to the scorer, rerun the exact SME003 preflight
nuisance residualization, scale estimation, 83-feature intersection, analytic
shrinkage, and held-folio coordinate construction. A power injection therefore
affects its own target-blind scales and covariance just as a real distributed
effect would. Eligibility must remain the exact preflight list or the world
stops.

For target `t`, phase assignment `i`, edition `e`, and an informative held
folio `f`:

1. In the coordinate system fitted while holding out `f`, compute each page's
   high-minus-low feature vector and average informative pages within physical
   folio to obtain `Delta_{g|f,e,i}`.
2. Compute the held contribution
   `c_{f,e,i}=Delta_{f|f,e,i}' W_{-f,e}
   mean_{g!=f}(Delta_{g|f,e,i}) / p`, where `p=83` and only target-informative
   folios enter the training mean.
3. Compute `T_{t,e,i}=mean_f(c_{f,e,i})`, equal-weighting physical folios.

Every vector in one contribution uses the same held-`f` nuisance coefficients,
training RMS, eligible order, and weight matrix. No fold coordinates mix.

For each target, edition, and phase ensemble, use the population mean and
population standard deviation of all assignment `T` values. Zero or nonfinite
standard deviation stops the world. Define
`z_{t,e,i}=(T_{t,e,i}-mean_i(T_{t,e,i}))/sd_i(T_{t,e,i})` and
`R_{t,i}=min_e(z_{t,e,i})`. Define the joint family statistic
`M_i=max_t(R_{t,i})`. The inclusive exact Monte Carlo tail is
`p=(1 + count_{i>0}(M_i >= R_{t,0}-1e-12))/N`, with identity assignment zero.

All non-tail numeric gate decisions use absolute tolerance `1e-15`: positive
means greater than `1e-15`, and a lower threshold is met at
`value >= threshold-1e-15`. Population null SD is computed with `ddof=0`.
The separate inclusive tail tie tolerance is exactly `1e-12`.

The raw material coordinate is
`A_{t,e}=sign(T_{t,e,0})*sqrt(abs(T_{t,e,0}))`. A target can pass only if:

- its joint-family `p <= .05` in both phase ensembles;
- every raw `T_{t,e,0}` is positive and `min_e A_{t,e} >= .05`;
- the three pairwise cross-reading orientation cosines defined below are each
  at least `.10`;
- the same at least five of seven ray folios, or four of six tail folios, have
  positive identity contribution in all three readings;
- after deleting each informative folio from every label-dependent held and
  training-direction average, every remaining-reading raw `T` is positive.

Deletion keeps the already fitted label-blind nuisance/scaling/weight
coordinates; the deleted folio contributes no label-dependent vector or
direction. This is a conditional robustness deletion, not a new independent
score.

More explicitly, when folio `d` is deleted, every surviving held contribution
`f != d` recomputes its training direction as the mean over informative
`g != f,d` in the unchanged held-`f` coordinate system, and the deletion
statistic is the equal mean of those contributions over surviving `f`. The
least-squares solver remains the preflight solver
`numpy.linalg.lstsq(..., rcond=None)` and the relative-quarter bins remain the
preflight half-open bins `[0,.25)`, `[.25,.50)`, `[.50,.75)`, and `[.75,1]`.

No individual feature statistic, coefficient, loading, weight, favorable root,
or post-hoc subset may be emitted for a real target.

### Cross-reading orientation gate

The quadratic within-reading score is invariant if one reading alone reverses
all contrasts, so it cannot establish shared orientation by itself. Freeze a
separate label-dependent orientation gate. For each edition, fit the same
nuisance and RMS transform on all seven folios without covariance weighting,
then compute its equal-page-within-folio and equal-folio identity effect vector
`D_{t,e}` over the 83 common standardized features. All three ordinary cosine
similarities among `D_ZL`, `D_IT`, and `D_RF` must be finite and at least `.10`.
Reversing every target label in all readings reverses all three vectors and is
invariant; reversing only one reading reverses two cosines and must fail.

## Phase ensembles

Calibration uses 8,192 assignments including identity. Final production, if
later authorized, must use 65,536 including identity. Both use rejection-
sampled SHA-256 shifts with no modulo bias.

Assignment zero contains all-zero shifts. Page columns use exact sorted page
order. For assignment `i>0`, key `k`, and counter beginning at zero, interpret
the first eight digest bytes of
`SME003_ROT_V1|ensemble|i|k|counter` as an unsigned big-endian integer. Reject
values at or above `2^64-(2^64 mod L)` and otherwise take modulo `L`. A page
key is its literal page ID. A coupled key is `FOLIO:` plus the physical folio,
with `L` the least common multiple of its page lengths and page shift
`floor(phase*page_length/L)`.

The initial frozen construction was corrected before any calibration score
because floor-mapped coupled phases can produce duplicate complete rows. For
each `i>0`, construct row attempt zero with the domain above. If its complete
12-column row duplicates any previously accepted row, increment a row-attempt
integer from one and regenerate every key using ASCII
`SME003_ROT_V1|ensemble|i|ROW_RETRY:{attempt}|{key}|{counter}` with the same
per-key modulo-rejection counter beginning at zero. Accept the first complete
row not previously present; hard-stop if no unique row is found by attempt
65535. Emit every row-attempt count and their maximum. This is deterministic
sampling without replacement over complete rotation rows, not silent duplicate
retention.

1. `INDEPENDENT_PAGE`: every page receives an independent cyclic shift.
2. `COUPLED_FOLIO`: every physical folio receives one phase on the least-
   common-multiple grid of its page lengths; a page receives the explicit
   floor-mapped shift above. This is a coupled floor-normalized phase model,
   not an exact common fractional phase.

Every rotation row must be unique. The stored array is C-contiguous
little-endian unsigned 16-bit with shape `N x 12`; SHA-256 is over its raw
bytes. The same assignment shifts both ray-like and tail-like sequences, preserving
their within-page cross-target relation. Every shift preserves each page's
label multiset, ignored states, and cyclic adjacency/run structure while
relocating the linear cut. A positive shift is exactly
`numpy.roll(states, shift)`: destination zero-based position `j` receives source position
`(j-shift) mod page_length`. Canonical little-endian rotation matrices and
digests are mandatory.

## Shared-manuscript whole-row power plant

Additive per-feature shifts are forbidden as primary power evidence because
they can create fractional counts, out-of-range rates, and algebraically
incompatible paragraph profiles. The primary plant synchronously permutes
complete three-reading physical-row triplets within each page. It therefore
preserves every actual 84-feature row, all feature algebra and ranges, each
page inventory, and the observed alternate-reading perturbations.

Construct one target-blind projection matrix by applying the frozen nuisance
residualization and RMS scaling on all seven folios, then averaging each of the
83 standardized feature values across the three readings. For target `t`,
world `w`, and projection driver, `rank` fixes signs from each digest's low bit
and:

- `DENSE_83_DRIVER` uses all eligible features;
- `BALANCED_24_DRIVER` uses the 12 formal and 12 root eligible features with lowest
  world/target-specific SHA ranks.

These are projection drivers only. Whole-row reassignment can induce effects
in correlated nondriver features, so `BALANCED_24_DRIVER` does not claim a
signal confined to 24 features. Every power world reports full-profile
material plus realized RMS identity effect inside and outside its driver.
For that diagnostic, use the already defined all-folio identity vector
`D_{t,e}`. Report separately for every reading the population RMS of its
coordinates inside the selected driver and outside it. The outside value is
explicitly `null` for `DENSE_83_DRIVER`, whose complement is empty; there is no
across-reading scalar aggregation and this diagnostic is not a gate.

The unit projection is the signed driver-feature sum divided by the square
root of the driver count. Only target-informative pages are planted;
noninformative pages remain identity. Within an informative page, ignored-
third destinations remain fixed. Sort low destinations by current donor
projection descending, then destination ordinal and unit ID. Sort high
destinations by donor projection ascending, then destination ordinal and unit
ID. Pair them by rank; each disjoint pair with
`low_projection > high_projection` is a beneficial low/high donor swap. Order
beneficial pairs by decreasing projection gain, then low destination ordinal,
then high destination ordinal. This minimal class-partition trace contains no
within-low or within-high reordering. Strength `q` applies the first
`floor(q*K_page)` beneficial swaps, where `K_page` is the trace length. A
zero-length trace, including an already optimally aligned informative page, is
a valid no-op and is reported; it is never repaired or rejected. The same
donor permutation is applied to all three reading feature rows while metadata
remains at the synthetic destination unit.

Calibration strengths are `.25`, `.50`, `.75`, and `1.00`. There are eight
power worlds for each target, projection driver, and strength. In each power run the
other synthetic target remains in the joint family and sees the same permuted
matrix. Every world reports realized weakest-reading material `A`, pairwise
orientation cosines, swap counts, and the fraction of the complete trace.

The mandatory power gate is, separately for both projection drivers at strength `.75`,
at least 7/8 ray worlds and 6/8 tail worlds passing every gate under both phase
ensembles. Strength `1.00` must meet at least the same counts; pass counts must
obey, for every target, driver, and adjacent strengths,
`passes(stronger) >= passes(weaker)-1`, where a pass is the complete
dual-ensemble world decision. If
the real page inventories cannot generate `.05` material at those strengths,
SME003 stops rather than substituting impossible additive effects.

## Null and adversarial acceptance

On each of the 64 paired no-injection worlds, record whether the union of the
two targets contains at least one complete dual-ensemble pass. At most four of
64 union-world indicators may be true. This is an empirical whole-pipeline
false-positive ceiling, not a substitute for the exact target p value.

The following fixed controls must all behave:

Every whole-row plant control below is run separately under both
`DENSE_83_DRIVER` and `BALANCED_24_DRIVER`; its rejection requirement applies
to all eight worlds under each driver.

- for worlds `0..7`, the one-folio plant uses the lowest
  `CONTROL_ONE_FOLIO|target`-ranked informative folio and applies ordinary
  strength-`1.00` swaps only there; it fails common-support or deletion gates
  in every ray and tail world;
- the one-reading plant applies ordinary strength-`1.00` donor swaps only to
  ZL3b. The reversal plant applies the ordinary mapping to ZL3b/IT2a but builds
  RF1b swaps from the negated shared projection. Both fail common reading
  direction/material in all eight worlds per target;
- the folio-random control derives signs from
  `CONTROL_FOLIO_DIRECTION|target|folio|feature`, builds strength-`1.00` swaps
  separately within every informative folio, and fails in all eight worlds per
  target despite within-folio alignment;
- the opposite-cluster control orders informative folios by
  `CONTROL_CLUSTER|target|folio` rank. It uses the shared projection forward
  on the first four and negated on the last three ray folios, and forward on
  the first three and negated on the last three tail folios. It fails in all
  eight worlds per target despite strong within-folio associations;
- the held-fold leakage sentinel permutes complete three-reading row triplets
  within every page of held folio `f` by
  `CONTROL_HELD_MUTATION|f|unit` rank. It cannot change
  `W_{-f,e}`, any training-folio transformed row, or the training direction for
  its held contribution; exact pre/post digests are required for every fold;
- pure absolute-rank cubic, relative-rank cubic, parity, early/late, and
  quarter components are added separately to every eligible response except
  `PARA_WORD_COUNT`. This means seven separate controls named `ABS_CUBIC`,
  `REL_CUBIC`, `PARITY`, `EARLY`, `QUARTER_1`, `QUARTER_2`, and `QUARTER_3`.
  Their raw unit bases are respectively absolute rank cubed, relative rank
  cubed, odd-ordinal indicator, the exact preflight early indicator, and the
  three exact preflight quarter dummy columns; page-center the selected basis.
  For each reading and feature separately, scale it to `.500` times that
  response's baseline page-centered population RMS, using sign from
  `CONTROL_NUISANCE|basis|feature`. A zero/nonfinite response or basis RMS
  hard-stops. All raw residual arrays and all scores equal the unmodified
  fixture within `1e-10`, with identical gates;
- centered linear and cubic `log1p(PARA_WORD_COUNT)` components are two
  separate controls `LENGTH_LINEAR` and `LENGTH_CUBIC`. Page-center the raw
  power, then for each reading and root feature separately scale it to `.500`
  times that response's baseline page-centered population RMS, using sign from
  `CONTROL_LENGTH|basis|feature`. They leave every raw residual array and all
  scores unchanged within `1e-10`, with identical gates;
- bounded page-constant shifts form one control. For each reading and eligible
  response except `PARA_WORD_COUNT`, its page-specific constant has magnitude
  `.10` times that response's baseline page-centered population RMS and sign
  from `CONTROL_PAGE_CONSTANT|page|feature`. Every raw residual array and score
  remains unchanged within `1e-12`;
- after ordinary label validation, a scorer-only copy exchanging low/high
  state names bypasses the directed 66/83 and 133/22 generation gate. It
  reverses every page contrast but leaves cross-folio
  concordance and the two-sided profile orientation invariant; this is
  expected and forbids assigning which morphology state is semantically
  positive;
- duplicate, missing, extra, page-split, folio-drift, ordinal-gap, locus-drift,
  edition-drift, reordered-feature, negative-word-count, nonfinite, zero-scale,
  nonpositive-shrunk-covariance, rotation-bias, and target-artifact mutations
  hard-stop;
- independently within-page-row-permuted reading baselines with a shared
  strength-`1.00` whole-row plant are reported as an adversarial dependence
  sensitivity under both drivers for worlds `0..7`. For each edition and page,
  donor rows are independently ordered by
  `CONTROL_INDEPENDENT_BASELINE|edition|page|unit` rank before applying the
  shared plant mapping. Exactly: list the page's original donors in increasing
  destination ordinal/unit-ID order, list its destinations by the stated rank
  with ordinal/unit-ID tie-breaks, assign donor `k` to ranked destination `k`,
  independently in each reading, and then apply the ordinary shared
  destination-swap plan. Metadata remains at the destination and complete
  page inventories remain fixed. Emit each reading/page permutation and
  planted-matrix digest. This diagnostic may not replace the actual-reading
  primary power gate.

The nuisance, length, page-constant, scorer-only complement, and held-fold
sentinel controls use paired synthetic world zero. Whole-row plant controls
and the independent-reading sensitivity use worlds `0..7` exactly as stated.
All signs take the low bit of the full SHA-256 digest, with zero mapped to
`-1` and one to `+1`.

All invariance controls compare every reading, target, ensemble, assignment,
and applicable gate—not only the final decision. The scorer-only complement is
the sole explicit bypass of directed synthetic-generation counts.

## Calibration decision

Calibration passes only if every source/hash/separation/integrity/control gate,
the null ceiling, both strength-`.75` driver-by-target power gates, numeric
finiteness, determinism, full-family inference, and target-absence gate passes.
Failure closes this exact SME003 design before target access. No gate,
projection driver, strength, feature set, nuisance, shrinkage, support threshold,
rotation count, or claim may be changed after execution.

A passing production implementation must then be separately hash-frozen,
independently reconstructed, and registered before exactly one real target
join. Calibration itself supplies no manuscript association or meaning.
