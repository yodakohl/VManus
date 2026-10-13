# GDT1371 — Most frozen half-model gain is known/unseen allocation

**FROZEN_NOVELTY_SCORE_ACCOUNTING.** In the unchanged1316half-mixture comparison
with1308M1,93.27–97.01%of the positive aggregate equal-leaf gain lies in the
known-versus-unseen category term. The remaining conditional-identity gain is
small overall. Yet on globallyTRAIN-unseen forms, conditional identity gain is
positive in every reading while the original raw gain is negative. Both facts
must be retained. This is exact post-result accounting, not a new successgate,
mechanism identification, statistical confirmation or rescue of1316.

## The big picture that motivated this check

The positive baseline requires directed reusable spelling structure, frequency
information beyond a simple character predictor, and writing/context effects.
1308's wholeform gain and1309's broad contribution are not proof of indivisible
lexical entries:1316's fixed pieces improve aggregate prediction too.1320's
word-conditioned fusion gain likewise does not require word-specific spelling
memory;1333found no positive PRIMARY residual after immediate expanded flanks.
Those are distinct experiments, not interchangeable estimates of one effect.

Recent exclusion/capacity work makes narrow writing contracts precise, but does
not measure what fraction of possible languages remains.1364shows unit-scope
sensitivity;1368/1369leave a bounded-fragment representative model structurally
possible without binding real vowels or words.1367constructs full recurrent-form
coverage under at least16!arbitrary mappings. Coverage alone cannot select a
reading.1370is a valid narrow literal-overlap counterexample, not a languageban.

We therefore returned to a substantial positive predictive result and asked
what its gain actually consists of. No modelparameter, word, cohort or leaf was
changed. This numerical question had not been answered by1317's logical example
or1316's H>0/H=0table. The independent sourceword/carrier gap remains unresolved.

## Complete frozen score decomposition

All values are nats per form, averaged first within each leaf, then equally
across the46held physical leaves. Positive favors the oldhalfmixture MoverM1 P.

| Reader / cohort | Raw gain | Known/unseen category term | Identity gain conditional on category |
|---|---:|---:|---:|
| IT2a ALL |+0.138111|+0.128818|+0.009292|
| RF1b ALL |+0.159988|+0.155201|+0.004787|
| ZL3b ALL |+0.162811|+0.156432|+0.006379|
| IT2a UNSEEN |−0.256621|−0.384841|+0.128219|
| RF1b UNSEEN |−0.277827|−0.389711|+0.111883|
| ZL3b UNSEEN |−0.245110|−0.395885|+0.150775|
| IT2a KNOWN |+0.279631|+0.314418|−0.034788|
| RF1b KNOWN |+0.316908|+0.359048|−0.042140|
| ZL3b KNOWN |+0.310342|+0.355081|−0.044740|

Unrounded terms add exactly within numerical tolerance. Rounding may leave a
one-unit difference in the last displayed digit. Cohorts each retain their own
old within-leaf denominators; do not recombine the three equal-leaf means with
a single global word fraction. The93.27/97.01/96.08%shares (IT/RF/ZL) divide the
ALLcategory term by the ALLrawgain under IDENTICALweights. They are accounting
shares, not percentages of meaning, dictionary content or historically memorized
words. Readers concern one manuscript, not independent replications.

All23496oldheldevents remain: IT8623,RF7245,ZL7628. UNSEENcontains1856/1640/1592;
KNOWN6767/5605/6036. Everycohort has46leaves. ConditionalUNSEENgains arepositive
on34/34/36leaves, respectively; these descriptive counts install no newgate or
p-value. H=0cases remain, ratherthan retaining only supported recombinations.

## Why raw and conditional results differ

For a supplied Currier/lengthcell, Scontains every globallyTRAIN-seen wholeform
ofthatlength, including forms known only in anotherCurrier. Uis its complement
over the original22-unit universe. Let Cbe the observed S/Ucategory. Then

    log(M(w)/P(w)) = log(M(C)/P(C))
                     + log(M(w|C)/P(w|C)).

We sum the finiteSprobabilities under frozen P,H,Mand obtainUmass bycomplement.
No enumeration or truncation of the enormous unseen universe is needed. Empty
TRAINcells retain the original M=Pfallback with Hundefined, not a new repair.
All52heldcells and their masses are saved, with zero roundoffclamps. The primary
and validator reproduce all oldevent probabilities and rawscores before deriving
newterms.

WithinUNSEEN, Mallocates less category mass thanP, but its normalized distribution
over unseen identities scores better on average. This does NOTshow that Mgives
novelty too little probability in the fulltask. The binary known/unseen logscore
is BETTER forMonALLheldevents: its gains on known outcomes outweigh its losses
on unseen outcomes under the originalweights. GivingUmore mass automatically
would tradeagainst that benefit and is not selected here.

Conversely, withinKNOWN the conditional identity comparison isnegative in every
reading. Overall the large gain should therefore not be described as a large
improvement in choosing exact identities once known/unseen status is supplied.
The diagnostics concern probabilities, not newly classified linguistic words.

## Decision and next direction

1316remains NO_PRODUCTIVE_HALF_FORM_LEAD under its registered ALL+rawUNSEEN
conjunction.1317alreadyproved that such failure neednot imply a falsegenerating
mechanism;1371now quantifies the native frozen distinction without replacing the
gate. No midpoint, smoothing, mixture or unseen-only fallback was tuned. This
also does not turn a post-result conditional improvement into an independent
productive-writing confirmation.

For future modelselection, distinguish allocation to familiar forms from the
choice of a particular novel form. A prospective mechanism must predict a
consequence beyond broadcoverage or a count of excluded toywriters. The new
unreviewed IDEA1047spelling-memory proposal supplies one potential contrasting
prediction: persistence between consecutive occurrences of the SAME word/site,
versus a static spelling preference or general physical-neighbor drift. It has
not been tested or selected; actual expansion/opportunity binding, temporal
ordering, counterexamples and mobilecapacity must be reviewed first. The present
gain does not itself establish temporal memory or justify its fixed probability.

No further retuning of1316is authorized by this report. No language, sourceword
identity, glyph alphabet, actualmorpheme or wordmeaning has been recovered.
Confirmed lexemes remain0.

## Verification and access

The primary uses storedMODEL_Hand floatingproducts/accuratesums. The independent
validator reconstructs Hfrom1308TRAINwholecounts, builds rationalM1probabilities,
sums exactknownmass and verifies all52cells,23496events,cohort/leaf terms and
oldcounts/rawmeans within1e-10. A finite exact50:50control separates negative
UNSEENrawgain from positiveconditionalidentity and positiveALLbinarygain.
ValidationPASS is computational; no new scientific successgate exists.

Protocol, proofreview, programs, fittedtables andoldresults were hash-locked
before newmasscalculation. The question was selected afterknown oldoutcomes;
alltargetdata were historically exposed. No new training, corpusquery, rawTSV,
image, source-language control, reserve, f84/f84r,f116v orf1rbody access. Old
artifacts and decisions remain unchanged. SCORES retains every oldeventID and
allthree terms; CELLS and RESULT allow complete reproduction.
