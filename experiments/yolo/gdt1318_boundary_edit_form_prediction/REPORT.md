# GDT1318: transferred boundary edits lack consistent whole-form prediction gain

**NO_BOUNDARY_EDIT_PREDICTIVE_LEAD.** The fixed edit sampler reaches hundreds of
TRAIN-unseen whole forms, but fails the preregistered cross-leaf consistency gate
in every reading. Its equal-leaf mean gain over the unchanged whole mixture is
slightly positive; its token-weighted gain is negative. Retain that disagreement,
not just the favorable mean or a few successful new words.

| Reading | Held words | Equal-leaf gain vsOLD, nat/word | Positive leaves/46 | Token-weighted gain vsOLD | Unseen E-positive occurrences/leaves |
|---|---:|---:|---:|---:|---:|
|ZL3b primary|7628|+.016497|20|−.040337|658/46|
|IT2a sensitivity|8623|+.019466|22|−.034404|788/46|
|RF1b sensitivity|7245|+.015738|23|−.028898|667/46|

The fixed primary gate required>=.01equal-leaf mean AND>=two-thirdspositive leaves,
with>=100words and>=10leaves. Coverage separately required>=100globally unseen
E-positive occurrences on>=10leaves. Coverage and mean pass; consistency fails.
The observations remain alternate readings of one manuscript, not independent
replications. No pvalue, new reserve or causal writer identification follows.

## Complete construction, including its costs

Learn ordered FIRSTorLASTsingle-working-unit substitution rules from distinct
TRAINwhole pairs sharing the complete remainder. Each ordered pair contributes
one count, regardless of token frequency. Pool lengths within Currier; each
observed pair itself has the same length. Reverse counts are symmetric.

Draw a baseword from the original empiricalQ(Currier,length). Select one applicable
FIRSTorLASTrule proportional to its count, with one shared denominator across both
sides. Apply exactly that one replacement. No applicable rule means copy the base.
Apply learned rules to every suitable base, not just to its previously observed
neighbors. Sum all derivations of an output, keeping unattested outputs. This
normalized distribution isE. It preserves length and every interior working unit.

The new predictor is .5M1+.25Q+.25E, compared with originalOLD=.5M1+.5Q. Entirely
missingTRAINcells useM1inboth. There is no hidden insertion/deletion, interior edit,
multiple step, language value, best-neighbor selection or target-vocabulary filter.

| Reading | Rule entries across Currier | Ordered TRAINpair supports | Generated output/cell entries | Original whole/cell entries |
|---|---:|---:|---:|---:|
|ZL3b|566|3782|41682|2329|
|IT2a|604|4520|48080|2591|
|RF1b|586|3762|40322|2299|

These generated inventories are possible outcomes of this specific sampler, not
newly discovered manuscript words or evidence that unattested forms are illegal.
The rule table is additional to the full base inventory and M1, not a tiny paid
code or minimum-description-length demonstration. Mass assigned to unobserved
outcomes remains part of the normalized likelihood comparison.

## Known forms pay for the extension

| Reading | Globally known words: equal-leaf gain vsOLD | Globally unseen: gain vsOLD | Globally unseen: gain vsM1 |
|---|---:|---:|---:|
|ZL3b|−.164132|+.574153|−.118493|
|IT2a|−.156937|+.553059|−.140088|
|RF1b|−.161247|+.512767|−.176102|

For unseen wordsQ=0, so NEW/OLD=1+E/(2M1). BeatingOLDon those words wheneverE>0
is algebraically guaranteed, not an independent success of prediction. The coverage
gate measures how often such new combinations are reached; it is NOT a count of
correct predictions. Generic cohort gate booleans inRESULT do not override the
registered primaryALLgate. All raw-unseen comparisons are descriptive, and1317's
warning against mechanism rejection from subset scores remains in force.

Across ALLwords, NEWstill beats the character-onlyM1(+.103847/+.090086/+.103471
equal-leaf nats), but that weaker comparison is not the primary test. The intended
addition to the stronger whole-frequency baseline is not consistent across leaves.
No page-specific writing mechanism is inferred from the heterogeneous scores.

## One post-selected illustration, not a rescued decision

ZL`airod`,f104r.19G011,CurrierB, is absentfromTRAINas a whole. The sampler can
reach it from TRAIN`airol`by the learnedLASTl→dsubstitution. Here E=.0000228483;
NEWgains1.350184nats overOLDand.657037overM1. The neighboring alphabetical example
`airoy`,f114r.26G009, is reached byLASTl→yfrom the same base. These are literal
unit substitutions in a model; they establish no meaning-preserving variant,
end-component meaning or actual scribal derivation. They were inspected only after
the full result. The failures elsewhere are not excluded or retuned around them.

## Predecessors and research decision

160/161test operation compatibility and latent host classes.522/524rerank supplied
forms' component recipes;746compares already observed forms' distribution profiles
and explicitly makes no unseen-form prediction. No old recipe atom or gloss was
adopted.914's failure of recurrent local parallel edits and1170's duplication
context result stay closed; this sampler contains no chronological copying claim.
1316's midpoint model and1317's source-free score limit remain unchanged.

Stop this fixed boundary-edit completion. Do not search different end lengths,
interior positions, mixture weights, rule thresholds or extra edits as automatic
repairs. The result does not reject analogy, morphology, optional spelling or all
human copying. It says this exact normalized transfer rule does not reliably add
to the existing whole-form predictor under the declared criterion. Mean positivity
and novel coverage remain recorded, without a new native language or word meaning.

## Reproduction and assumptions

The code, protocol and source bindings were sealed before rulelearning/scoring.
A source-free reviewer checked normalization, unseen-score algebra and the fact
that interiors cannot change. Primary learning groups TRAINtypes by their shared
remainder; the independent same-author validator discovers neighbors by literal
replacement and reconstructs probabilities by inverse derivations. It rechecks
61181original source joins/TRAINcounts,130084generated output probabilities and
all23496held scores, with exact rational normalization and all cohort decisions.
The original1308M1andQscores are hashbound and unchanged; no native parser or
baseline is retuned. Validation is accounting, not independent manuscript reading.

Only the unchanged1233/915/1308current guarded caches are used. No newrawTSV,
image, sourcecorpus, f84/f84r/f116v/f1rbody, old327/336body or reserved material.
The22units, boundaries, Currier/length inputs and exposed odd/even split remain
assumptions. Zero word meanings. Inclusive08:43–09:18UTCbudget10Octoberincludes
selection, preparation, verification and publication.
