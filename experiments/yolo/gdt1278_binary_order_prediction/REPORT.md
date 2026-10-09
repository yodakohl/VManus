# GDT1278: the compact switch preference misses its predictive transfer gate

**NO_JOINT_MATERIAL_PREDICTION.** Adding one training-selected preference for
alternating the fixed1264classes improves average conditional order prediction,
but the gain is not sufficiently consistent across physical leaves. Both
primary ZLcohorts fail the frozen joint decision.1264/1265's structural positives
remain; this does not reject every possible two-class model.

| Reading | Cohort | Groups | Positive/all leaves | Equal-leaf gain, nat/interior unit | Decision |
|---|---|---:|---:|---:|---|
| ZL3b | ALL |5301|25/46|+.00262465|NONCONFIRMING|
| ZL3b | UNSEEN_INTERIOR |729|24/45|+.01217434|NONCONFIRMING|
| IT2a | ALL |5863|24/46|+.00073297|NONCONFIRMING|
| IT2a | UNSEEN_INTERIOR |819|26/45|+.01460138|NONCONFIRMING|
| RF1b | ALL |4880|25/46|+.00235946|NONCONFIRMING|
| RF1b | UNSEEN_INTERIOR |745|27/46|+.00846008|NONCONFIRMING|

Each primary cohort required >=.01gain AND >=two-thirdspositiveleaves, with
>=100groups on>=10leaves. Capacity is adequate. ALLfails both effect/direction;
UNSEEN_INTERIORpasses mean size but fails direction. Neither rescues the other.
Readers are alternative readings of one manuscript, not independent replications.

## The actual predictive question
The model is given interior length and the number of units in each fixed class.
It assigns normalized probabilities to ALLbinary orders with that inventory.
The baseline uses five relative-position weights. The added model uses the SAME
weights plus beta times the adjacent switch count. This predicts binary order
only: no lengths, class inventories, exact glyphs, word boundaries or content.
There is no recovered alphabet, phonetics, meaning or complete human writer.

Position log-odds are smoothed marginal counts from4909ZLinteriors on44odd leaves.
They are not a conditional maximum-likelihood position fit, and five bins do not
remove every possible length/position effect. Any gain is relative to precisely
this frozen baseline. beta is chosen from[0,.25,.5,1,2] using total TRAIN
conditional likelihood; beta1wins. The ZLmodel is frozen once and applied
unchanged to all readers' even-leaf data. No TESTgrid search or refit occurred.

| beta | TRAIN conditional loglikelihood |
|---:|---:|
|0|−6699.748405|
|.25|−6393.703115|
|.5|−6210.696379|
|1|−6176.318060|
|2|−7133.193350|

The mean over individual ZLALLgroups is +.02583675, versus only+.00262465when
each physical leaf has equal weight. The protocol chose the latter in advance.
The positive pooled figure cannot replace the failed gate. UNSEEN_INTERIOR's
event mean is+.00952432. All per-leaf outcomes and event predictions are retained.
For ZLALL, nonpositive leaves are2,4,6,8,10,14,18,20,22,28,30,32,36,38,42,44,
52,56,88,96,102. None was dropped or used to tune the model.

The descriptive UNSEEN_WHOLE cohort also misses the direction requirement:
ZL1358groups,30/46positive,+.01001446; IT1568,27/46,+.00573200;
RF1390,28/46,+.00692863. It is not a substitute primary. Exact-interior novelty
uses each reader's old odd-leaf inventory and remains outcome-defined; model
probabilities are not renormalized on that novelty filter. All text was already
project-exposed, so none of these splits creates untouched confirmation.

## Full coverage and verification
The unchanged1233cached population yields10007ZLheldgroups:4705too short after
removing exactly the first/last unit,5301scorable,1unclassifiedm-containing group.
No unknown class is assigned. IT/RFcoverage is explicit in RESULT.json. Every
scorable event and unknown-unit event is preserved in EVENTS.json.gz.

Forward log-space DP normalizes allbinaryordersforlength/count.390small exhaustive
length3..8/count/position/beta cases check normalizers and probability sums before
fitting. An independent validator imports no primary code: backward positive-
weight recursion reconstructs training counts, allgrid likelihoods, selection,
every16044held prediction, all cohorts, leaf scores and decisions. PASS. This
checks arithmetic/source consistency, not independent manuscript evidence.
Protocol/programs were hash-locked before parameter fitting; MODEL_LOCK was
written before evaluation. The separate source-free review covered the finite
probability model, DP, baseline limitation, fixed inventory and novelty scope.

## Research decision
Do not adopt this particular five-position-plus-one-switch rule as an adequately
portable predictive component under its registered gate. Do not retune beta on
even leaves, change the position bins, alter labels or choose favorable leaves.
The broad positive full-symbol Markov result predates this test and is unchanged;
1264's compact association and1265's restricted paired control stay positive.
1266's distant-form capacity stop is also unchanged: this did not rematch or
claim distant-form success. What failed here is the explicitly fitted small
probability rule, not all local structure or all possible writing systems.

The next construction should be judged by a new independently motivated operation
and predictive consequence, retaining specific-unit and wholeform evidence. This
result does not prove that symbol identity or any particular alternative is the
missing ingredient. No automatic more-complex decoder or model repair selected.
No new data/image, reserves, f84/f84r, f116v, semantic edge or word assignment.
Local only under4Octoberinstruction.
