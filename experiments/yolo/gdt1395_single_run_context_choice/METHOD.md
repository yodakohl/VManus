# GDT1395 — independent categorical single-run choices and external context

Prospective decision, before native context counts. Inclusive budget10:40–11:40UTC
16October2026 includes predecessor preparation, code, validation and publication.
At the limit stop expansion and reassess. No automatic threshold/cohort repair.

## Question and changed decision
Can arbitrary categorical run-length allographs be chosen independently of the
external symbolic source context? This is a distinct writer and falsifier from
1328's geometric law. Its six failures stay frozen. No native collapsed word or
word meaning is selected. A failure retires only the independent categorical
rule under the declared premises; nonfailure does not license collapsing words.
A capacity failure stops before random permutations. No decoder follows either.

## Complete restricted writer and reader
Source messages are finite ordered lists of nonempty words over22abstract
working drawings, without adjacent e/e or i/i. Other repeats are retained.
A fixed supplied line scaffold partitions the source word sequence. For each
page, complete sourceword and e/i-slot, a finite paid table of rational categorical
probabilities chooses a positive run length; unspecified cells use length1.
Every slot/occurrence draw is independent. Other units and all source word gaps
are copied unchanged. Collapsing maximal e/i runs returns the exact symbolic
source, but NOT established natural-language words, phonemes or meanings.
The test additionally permits habits by the fixed line-position third, a generous
relaxation. There are no per-occurrence probability parameters or free deletions.

## Fixed native scope and projection
Use the unchanged strict Pgroup cache of1233 and its original cached915 source
rows for IT2a and ZL3b separately. Verify old ids/raw units/boundaries, allowlist
and complete line indices/counts. No new TSV extraction, selector, image, source
corpus, reserve, f84/f84r, f116v, f1rbody or327/336body. All data are exposed,
not fresh confirmation. RF1b is not selected. Readers are alternatives, not
independent manuscripts or pooled capacity.

Target and both immediate same-line neighbors must be strict1233groups at exact
indices j-1,j,j+1. Target must have exactly ONE maximal e/i run (including length1).
No bridging a missing/uncertain group or physical line. Collapse BOTH e and i in
all three forms. The exact full collapsed target has one run slot and defines its
source tuple. Position third=min(2,3*(j-1)//line_group_count). Group by exact page,
full collapsed target and third. Retain every stratum with n>=3 and varying
observed run lengths. No family/word/section selection after outcomes.

Neighbor covariates use their COLLAPSED unit tuples; they are invariant when any
run length, including an adjacent target's, is permuted. Do not hold raw neighbor
spellings fixed while silently permuting their own lengths. Width and framing
are separately assumed, not inferred from this bookkeeping.

## Fixed statistic
For each side form the SET of adjacent working-unit pairs in
[BOS]+collapsed_neighbor+[EOS]. Assign each feature1/sqrt(2*side_set_size), with
left/right namespaces distinct; the concatenated feature vector has norm1.
K is its Gram matrix. Labels are run lengths, represented one-hot over the
stratum's observed categories. Z is this one-hot matrix minus column means.
S=trace(Z^T K Z)/trace(Z^T Z). No ordinal meaning is assigned to run lengths.
Average S equally across all retained strata within each physical leaf fNN,
then equally over represented leaves. r/v/foldouts share their physical leaf.
The one combined left/right statistic is fixed; do not pick a favored side,
family, feature set, run threshold or manuscript section after results.

## Capacity before scoring permutations
For each retained stratum calculate S at the original labeling and after every
single swap of two unequal labels. The first absolute change>1e-9 is a saved
witness of statistic mobility. Failure to find one is NOT proof of invariance.
At least20witnessed strata,100occurrences in them and10physical leaves with a
witness are required per reader. ALL predeclared eligible varying strata remain
in the observed/null score, including unwitnessed ones. The witnessed subset
is only a conservative capacity gate, not an adaptively selected scoring sample.
It may depend on labels; no conditional-on-capacity calibration is claimed.
If a reader fails capacity, draw zero permutations for that reader and record
CAPACITY_STOP. This must not become model rejection.

## Conditional null and decisions
Condition on each stratum's complete run-length histogram. Under independent
fixed categorical draws every distinct assignment to its occurrence slots is
uniform; unknown probabilities cancel. Source context is fixed, not fitted.
Shuffle the length labels independently per stratum, preserving all multiplicities.
For each reader use random.Random(1395+reader_index), order IT2a,ZL3b. Strata are
sorted by(page,tuple(collapsed_target),third); events sorted by original id.
Within each stratum generate1999permutations in draw order: start indices0..n-1,
call rng.shuffle(indices), and assign original_labels[indices]. No reseeding per
stratum. Both observed and permuted labels use the same fixed kernel and weights.

p_upper=(1+number(null_global>=observed-1e-12))/2000. Relative gain is
(observed-null_mean)/null_mean; if mean<=0, no rejection. A reader rejects only
with capacity, p_upper<=.005, relative gain>=.10, and at least2/3represented
physical leaves having observed score>their own null mean (tolerance1e-12).
Joint rejection requires BOTH readers, without claiming independence. Otherwise
NOT_REJECTED or CAPACITY_STOP. This is an exposed conditional model comparison,
not search-wide calibrated significance. Retain contrary leaves and all failures.

## Assumptions, predecessors and limits
Strict-panel selection/uncertainty masks and the fixed line scaffold must preserve
exchangeability conditional on the declared strata. Length-sensitive wrapping,
legibility, scribal geometry, serial dependence or unmodeled context could break
this assumption. A positive result would NOT distinguish those alternatives from
meaning-bearing variation; a negative result would NOT establish synonyms.
Adjacent targets share source contexts, but those contexts are invariant under
all tested length permutations; independence of run draws is the null premise.

1170tests external contexts of XX versus X, not internal run lengths;1329tests
two internal slots and stopped for capacity.1323uses same-bag anagrams, whereas
length changes alter the bag.787compares family remainders,854/1254test e-placement
and cross-kernel prediction. Their outcomes remain. The inherited semantic
minimal-pair closed-family row has an unavailable linked primary in this workspace;
we neither reopen its synonyms nor claim exhaustive novelty from this missing file.
New1068does not overwrite996or call1328passed. No new semantic relation packet
is scored and no lexical English value is proposed.

## Verification and freeze
Source-free controls enumerate complete small label orbits, check histogram
multiplicity/categorical probability cancellation, include mobile and invariant
kernels (n2 and all-unique labels), and adjacent-target collapse invariance.
Lock protocol, primary, independent validator, SPEC and inputs before native
projection. Validator must not import primary; use direct normalized intersections
for K and centered-kernel label-block sums for S, reconstruct old rows and all
mobility witnesses/conditional draws/decisions. Floating comparisons have explicit
tolerances and independent reconstruction; this is not interval arithmetic.
