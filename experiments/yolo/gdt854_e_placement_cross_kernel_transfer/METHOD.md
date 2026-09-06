# GDT854 — e-placement transfer across kernels and folios

The fixed question is whether moving the single literal e to either of two
positions predicts outside neighbors across cth/ckh, beyond their common
literal ASCII-transcription character inventory and length. Root reviewed
GDT787/802/853 primary reports and IL008/IL026 closed-family boundaries;
The IL026 primary report was not recovered; no IL008 primary reread is
claimed. This is not their semantic projection, l/m global profile, spacing comparator
or shape/higher-order test. Known GDT849 counts motivated the exact family;
its source was already exposed. No untouched-confirmation claim. Equal character inventory here is an ASCII
string property, not established phonemes, alphabet letters or identical
physical ink. The relocated e could have different allographic realization;
its physical geometry is not validated.

Only cached GDT851 ZL3b source and179selectors. Exactly8target forms:
{ch,sh}+e+{cth,ckh}+y (OUTER), or
{ch,sh}+{cth,ckh}+e+y (INNER).
Whole-target raw equality, no annotation normalization. Immediate external
neighbors must be plain [a-z]+, consecutive source indices and definite
boundaries on both sides within one source line. Exclude an occurrence if
either neighbor is any of the8target forms, avoiding direct target echoes.
No images, new query, reader, page, endpoint or family widening; f84/f84r sealed.

Cell key: physical folio fN, exact selector, source kind, section, hand,
prefix, kernel, line half. Index is source_group_index,1-based; EARLY iff
2*index <= source_group_count, otherwise LATE. Retain all eligible events
and cells, but model/evaluate only cells containing both placements. Event
IDs sort lexicographically within each cell; cells sort by their JSON key.

For each held physical folio and held kernel, train only mixed cells of the
OTHER kernel on ALL OTHER physical folios (both prefixes allowed). Each
training cell contributes, separately for LEFT and RIGHT, its per-class
relative-frequency difference OUTER minus INNER for every literal neighbor.
Average these differences equally across training cells. Score a held event
by the equal mean of its left and right weights; unseen neighbors have0weight.
No fitted smoothing, tuning or held-kernel training. Excluding the entire
held folio also removes its other-kernel cells.

Within a held mixed cell, AUC is the fraction of all OUTER/INNER event pairs
where score(OUTER)>score(INNER), with ties worth0.5. Average cell AUCs equally
within folio×kernel, then average folios equally within each kernel, then
average the two kernel means. Use exact rational arithmetic for weights,
comparisons and nested means to avoid floating-point near-zero ties.

Capacity, before neighbor models: at least8unique evaluation folios, at least
3evaluation folios for each kernel, and every evaluation fold has mixed
other-kernel training cells on at least2physical folios. If any gate fails,
stop without scores or permutations. Keep every registered eligible fold;
no dropping unsupported folds or choosing another positional partition.

If capacity passes, flip placement-label polarity for whole physical folios,
inverting OUTER/INNER in ALL mixed cells/events on each selected folio
together. This preserves each folio's local ordering and layout structure;
class counts swap, and cell-normalized differences handle the swap. Let F
be the union of mixed-cell folios used in training or evaluation. Fix the
lowest numeric folio unflipped because globally flipping all labels leaves
the statistic invariant. If F<=12, enumerate all2^(F-1) binary flip patterns
in lexicographic bit order, including the observed all-zero pattern; exact
tail fraction is count(null AUC>=observed)/number of patterns. Otherwise use
999iid uniform patterns with replacement from one Python random.Random(854),
calling getrandbits(1) for
each remaining folio in numeric order for each pattern; Monte Carlo
p=(1+count(null AUC>=observed))/1000. Refit the entire LOFO-other-kernel model
and rescore for every pattern, with exact rational tail comparisons. Report
all patterns/statistics and observed events, cells, folds and model coverage.
This null unit was selected before any data inspection in this experiment;
within-cell occurrence shuffling is not run. Whole-folio flips test a fixed
cross-folio direction against arbitrary folio polarity, assuming folio sign
exchangeability; not general conditional independence or causal randomization.

Narrow descriptive pass requires overall AUC>=0.65, BOTH kernel AUCs>0.5,
and folio-flip p<=0.01. Otherwise the fixed comparator fails. The p value
assumes physical-folio sign exchangeability; it is not a general conditional
independence or causal randomization test. Nearby events, omitted layout, reading choices,
and residual lexical confounds can remain. No power guarantee, language,
meaning, morpheme or authorial-intent claim follows, even on a pass. Only the shared cross-kernel channel is tested; no within-family
model is fit. Failure cannot prefer whole-word meanings over placement
conventions. Success remains compatible with contextual spelling and learned
whole forms; it does not uniquely identify a function bit.

Budget25min including preparation, public registration, run, independent
validation and root publication, starting about05:14UTC. Tiny invented fixtures check direction, zero-unknown contributions, ties,
global-flip invariance and held-folio/held-kernel leakage traps; no synthetic
power project. Freeze all before manuscript data loading; root publishes and
sends GO. Stop after this comparator with all earlier stops preserved.
