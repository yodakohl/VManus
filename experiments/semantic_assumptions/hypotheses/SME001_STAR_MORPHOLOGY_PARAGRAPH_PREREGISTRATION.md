# SME001 — star morphology versus paragraph construction

Status: **REGISTERED_UNSCORED**

## Question and ceiling

Do the author-visible seven-versus-eight-ray and one-versus-two-tail states of
final-section marginal stars condition the formal construction or reusable
root morphology of the exact manually marked paragraph paired by equal-count,
top-to-bottom ordinal with each star?

The strongest possible result is an anonymous marker-morphology-conditioned
paragraph feature or root association. It cannot name either marker state,
establish a recipe class or number, translate a root or word, identify a
language, recover plaintext, or translate the manuscript.

## Frozen evidence boundary

The morphology source and text-feature matrix remain separate until the one
registered target run. The source binding contains no feature value; the
anonymous matrix contains no ray, tail, core, paint, color, or other morphology
field.

Frozen inputs:

- `target_source_binding.tsv`: SHA-256
  `315ea24a10995caaa86a77a5a93ecfc0e666351c1ce6a44b078b08686c1d6f3b`
- `target_source_capacity.json`: SHA-256
  `e2322d841d4af6ca08737697e5eb32a104dd61178ff9f281e879dc0c5c364d44`
- `target_source_validation.json`: SHA-256
  `38cc174f38607731005e9a2567eed113d02a47114e8640e2e97fc472ede0a74b`
- `anonymous_paragraph_matrix.tsv`: SHA-256
  `b246456b181b07e847c6d5a49b959b0346eff6a4c6febb8a543de104c505a26a`
- `anonymous_feature_inventory.json`: SHA-256
  `088232b431b4b9746bb94a08328cb969fb7c21c6a28cd112286da40d6429fea5`
- `anonymous_matrix_capacity.json`: SHA-256
  `7043fd8d2f8b6b829a2ecd1724b701d3ab811ad4545434720222e1ad03138828`
- `anonymous_matrix_validation.json`: SHA-256
  `c5a5bb236dd61ecdf8a76ff05e697b8b3a636aa03145fe019a6348fac74aa3d9`

The target source contains 156 complete-sequence entries on 12 pages / seven
physical folios. `f106r` is wholly excluded because retaining its 14 otherwise
covered entries after one all-reading line-set failure would splice the marker
sequence. The anonymous matrix may retain those unused rows, but the target
join may not.

`<%>` is the manual paragraph-opening marker in the frozen ZL source. The
builder consumes every such marker on each admitted page, requires its ZL line
to be `OPEN`, and requires every following ZL line up to the next marker (or
page end) to be `CONT`. RF does not carry this marker metadata and IT omits it
at four of the 171 starts, so neither alternate metadata column is counted as
independent layout evidence. The physical line spans are nevertheless required
to match across all readings. Thus the scored unit is a ZL-editorially marked
paragraph represented in all three readings. The star-to-paragraph relation is
still only the frozen equal-count/top-to-bottom ordinal pairing, not measured
proximity or independently proven object ownership.

## Frozen targets

1. `RAY_8_MINUS_7`: compare eight-ray to seven-ray entries. The frozen source
   has 149 eligible entries (66 versus 83), internal variation on all 12 pages
   and seven folios. Six- and nine-ray entries remain explicit ignored states.
2. `TAIL_2_MINUS_1`: compare two-stroke/fat-tail to one-tail entries. The
   frozen source has 155 eligible entries (22 versus 133), internal variation
   on eight pages / six folios. The sole tail-less entry remains an explicit
   ignored state.

Core, paint, color, tail absence, six-versus-nine rays, and every other source
field are outside the target family. Opaque core state is never recoded as
absence.

## Frozen feature family

All 84 columns listed in `anonymous_feature_inventory.json` are admitted as one
joint family:

- 19 opening-line root-free formal measures;
- 15 whole-paragraph layout/formal measures;
- 32 globally supported parsed root-atom rates;
- 18 globally supported composite root-form rates that preserve within-space
  word composition.

Root features were selected without target labels by requiring, in every
alternate reading, at least 20 occurrences, 12 paragraphs, six pages, and five
physical folios. No feature may be added, removed, merged, renamed, signed, or
selected after target joining.

A target-feature pair is eligible only if, in every reading:

- all values are finite;
- the feature varies within pages on at least four physical folios among the
  156 target-bound anonymous units (the 14 unused `f106r` rows cannot affect
  eligibility);
- its page-centered residual scale is positive; and
- its registered rotation-null standard deviation is positive.

The page-centered residual scale is fixed as the root-mean-square of
`x - mean_page(x)` over the 156 target units, separately by reading and
feature. It is target-label blind.

All nonzero, variation, direction, stratum, deletion, support, residual-scale,
and null-standard-deviation decisions use an absolute numerical tolerance of
`1e-15`. The separate Monte Carlo tail-tie tolerance remains `1e-12`.

## Statistic

For a target, page, rotation, reading, and feature, compute the mean feature
value on high-state entries minus its mean on low-state entries, ignoring the
target's explicit third states. Pages without both states contribute no
contrast. Average page contrasts within physical folio, then average physical
folios equally.

For each reading, center the observed effect by the mean of its registered
random-rotation null and divide by its population standard deviation over all
262,143 registered random assignments. With
reading-specific standardized effects `z_ZL`, `z_IT`, and `z_RF`, the two-sided
same-direction statistic is

`R = max(min(z_ZL,z_IT,z_RF), min(-z_ZL,-z_IT,-z_RF), 0)`.

The material effect is the minimum across readings of the absolute raw
equal-folio effect divided by that reading's target-blind page-centered
residual scale.

The three standardized effects must also have the same sign as the three raw
effects. A large two-sided `R` in the direction opposite to the raw contrast
fails.

## Frozen phase-preserving nulls

Two separately scored ensembles are mandatory. In each, index 0 is the
physical alignment and indices 1--262143 are deterministic cyclic rotations
sampled with replacement.

1. **Independent page phase.** For assignment `i`, page `p`, and page length
   `n`, draw an unbiased integer in `[0,n)` by SHA-256 rejection sampling from
   `SME001_ROTATION_V1|i|p|counter`.
2. **Coupled physical-folio phase.** For each folio, let `L` be the least
   common multiple of its retained page lengths. Draw an unbiased integer `k`
   in `[0,L)` from `SME001_ROTATION_V1|i|FOLIO:folio|counter`; page length `n`
   receives shift `floor(k*n/L)`. This gives every page an exact uniform
   marginal shift while keeping recto/verso at one normalized folio phase.

For every draw, read the first eight digest bytes as an unsigned big-endian
integer and reject values outside the largest multiple of the requested range
below `2^64`. Every shift is a left rotation of the complete marker sequence.

The same page-shift vector synchronously rotates ray and tail sequences and is
shared by ZL3b, IT2a, and RF1b. Thus every assignment preserves each page's
complete category counts, rare states, cyclic adjacency/run structure, and the
cross-target ray/tail relation. A rotation relocates the linear top/bottom cut;
it does not preserve the literal linear run partition. The frozen early/late
gates protect against a result carried only by that ordinal boundary. Text
values, pages, folios, ordinal coordinates, and paragraph boundaries never
move.

This is deliberately a phase-alignment test conditional on the observed
within-page sequences, not a general test of morphology/text independence.
Cyclic rotations create an artificial bottom-to-top edge, so even a pass can
claim only that the physical alignment is exceptional under both registered
page-phase models. It cannot by itself establish local causation or ownership.
The paired-folio ensemble protects against understated variance from a shared
recto/verso phase. A separate target-blind ordinal-residual gate protects
against common absolute-rank, smooth relative-position, parity, half-page, and
quarter-page profiles; it does not turn the pages into literal circles.

Raw Monte Carlo p is
`(1 + random assignments with R >= observed R) / 262144`.
For family correction, take the maximum R over every eligible feature in both
targets at each random assignment and use the same plus-one tail. Ties are
inclusive with tolerance `1e-12`. All z, raw-p, family-p, and `R` thresholds
must pass separately in both ensembles; the reported conservative p-values
and robust z are the worse of the two.

## Frozen robustness and materiality gates

A target-feature pair passes only if every gate below passes:

1. exact input hashes, row contracts, target/source separation, and target
   single-use protection;
2. the three raw observed reading effects have one nonzero direction;
3. all three null-centered z values have that same raw direction;
4. `R >= 2.5` in both registered phase ensembles;
5. raw p `<= .01` in both ensembles;
6. joint two-target/84-feature max-family p `<= .05` in both ensembles;
7. material effect `>= .15` page-centered standard deviations in every
   reading;
8. odd and even ordinal strata each retain at least four informative physical
   folios and reproduce the main direction in all three readings;
9. early and late half-page strata, split by physical ordinal
   `ordinal <= page_max/2`, each retain at least four informative folios and
   reproduce the main direction in every reading;
10. deleting every informative physical folio in turn preserves the main
   direction in every reading;
11. the same set of at least five of seven ray folios, or four of six tail
    folios, has a contrast in the main direction in all three readings;
12. every feature retains the main direction and at least `.15` original
    page-centered standard deviations after target-blind pooled page-fixed-
    effect adjustment for absolute ordinal, cubic relative ordinal, parity,
    half-page, and relative quarter;
13. for a `ROOT_ATOM_RATE__*` or `ROOT_WORD_RATE__*` feature, both linear and
    cubic target-blind pooled page-fixed-effect adjustments on
    `log1p(PARA_WORD_COUNT)` retain the main direction and at least `.15`
    original page-centered standard deviations in every reading; and
14. all planted and negative controls plus a nonimporting prescore audit and
    final reconstruction pass.

Constant/insufficient strata fail rather than being skipped. ZL3b, IT2a, and
RF1b are alternate readings of one manuscript, never replications.

All fixed-effect residuals are exact: separately for each reading and feature,
center the feature and every registered nuisance column within page, fit one
pooled no-intercept OLS over all 156 centered units, and score the residual
with the ordinary equal-folio contrast. The length designs contain respectively
`log1p(word_count)` and its powers one through three. The ordinal design
contains absolute-ordinal indicators, powers one through three of
`(ordinal-.5)/page_max`, odd, early-half, and relative-quarter indicators.

Every odd/even or early/late subset first restricts rows, then recomputes each
page contrast, averages informative pages within physical folio, and averages
folios equally. Deletion equally averages the remaining folio contrasts.
Folio support uses the mean of its informative page contrasts. Explicit third
states are ignored in every contrast, including subset and residual gates.

The production core reports only `statistical_passes`; the final runner may
report an overall pass only after input/separation, single-use, control, and
independent-audit gates 1 and 14 are also certified.

## Required prescore controls

The production engine and a nonimporting implementation must agree before any
real morphology-feature join. Controls must include:

- a distributed planted ray/formal signal that passes;
- a distributed planted tail/root signal that passes including length
  residualization;
- a null feature family that fails;
- parity-only and early/late-only signals that fail the corresponding gates;
- a page-constant/bifolio-only signal that fails within-page eligibility;
- a one-folio signal that fails deletion/support;
- alternate-reading disagreement and reversed-direction controls;
- a raw/z direction contradiction that fails;
- linear, nonlinear, and near-zero-residual root signals carried by paragraph
  length that fail the strengthened length gate;
- smooth ordinal, absolute-rank, quarter-wave, and page-cut signals that fail
  the ordinal gate;
- a same-folio coupled-phase control scored under both null ensembles;
- explicit rare-state preservation, cyclic-adjacency preservation, and
  linear-cut relocation checks;
- inclusive-tie, deterministic-hash, global-complement, row duplication,
  missing-row, page/folio/ordinal/locus drift, nonfinite, and constant-feature
  checks;
- exact target-source and anonymous-matrix hash checks; and
- absence of target result/claim artifacts.

Before target access, the controls must also run repeated 84-feature null
worlds under both phase ensembles and a distributed ray/tail signal grid below,
immediately around, and above the `.15` material boundary. The frozen control
spec defines world counts and acceptance criteria; a single planted fixture is
not sufficient evidence of familywise calibration or useful power.

The controls may use only synthetic label/value fixtures and anonymous matrix
contracts. They may not join the real morphology binding to the real feature
matrix. After controls, a separate nonimporting prescore audit is mandatory,
followed by a separately hash-frozen one-shot target runner.
