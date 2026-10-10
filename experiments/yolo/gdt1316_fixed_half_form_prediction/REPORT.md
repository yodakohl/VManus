# GDT1316: fixed halves improve total prediction but fail the unseen-word gate

**NO_PRODUCTIVE_HALF_FORM_LEAD.** The fixed fragment mixture improves complete-word
prediction overall, including all46ZLphysical leaves. It also beats1308's whole-form
mixture overall. But on ALLglobally TRAIN-unseen whole words it loses to the same
M1character baseline in every reading. The preregistered conjunction therefore
fails. Retain the positive aggregate result and the incomplete novel-form coverage
together; do not promote this particular midpoint rule as a successful productive
writer or change its split/weight after seeing the outcome.

| Reading | ALLheld words | Positive leaves/46 | ALLgain versusM1, nat/word | ALLgain versus whole mixture | TRAIN-unseen words | Unseen positive leaves/46 | Unseen gain versusM1 |
|---|---:|---:|---:|---:|---:|---:|---:|
|ZL3b primary|7628|46|+.162811|+.075461|1592|4|−.245110|
|IT2a sensitivity|8623|43|+.138111|+.067491|1856|3|−.256621|
|RF1b sensitivity|7245|43|+.159988|+.072256|1640|1|−.277827|

Gains in this table average within each physical leaf and then equally across
leaves. Allold1308rows, negatives and missing fragment cases count. Both ALL and
UNSEEN required>=100words,>=10leaves,mean>=.01and>=two-thirdspositive leaves.
ALLpasses;UNSEENfails. Alternative transcriptions describe one manuscript, not
independent confirmations. This is an exposed predictive comparison without a
new simulation or significance claim.

## The exact simple construction

For supplied Currier and working-unit lengthn, split at floor(n/2). Choose a
complete left half with its TRAINfrequency. Choose a complete right half using
its TRAINfrequency after the last unit of that left half. Concatenate the two.
Only that one unit connects the halves; the whole left-half identity is not used
to choose the right. Unknown lefts or unknown right/seam combinations receiveH=0.
The distributionHnormalizes over all22^nstrings. It can assign probability to a
whole never seen in TRAIN, but does not invent previously unseen pieces.

The scored predictor is MIX_H=(M1+H)/2, with originalM1alone only in wholly empty
TRAINcells. Original1308M1andMIX_Q are unchanged. A target-dependent fallback to
M1wheneverH=0was not used: simply doing that while retaining gains elsewhere would
add probability mass and is not the registered normalized predictor. No silent
penalty removal. Word length and Currier are given, not predicted.

## Where novel recombination helps, and where it stops

Post-result accounting of the fixed unseen cohort:

| Reading | Unseen words withH>0 | Their token-mean gain | Unseen words withH=0 | Their token-mean gain |
|---|---:|---:|---:|---:|
|ZL3b|480|+.817126|1112|−.691901|
|IT2a|597|+.760536|1259|−.693147|
|RF1b|502|+.733749|1138|−.691320|

These conditional subsets are descriptive, not extra success gates. H>0means the
left half and the right half under its required seam were available. For an
unseen whole, this is an actual new pairing of learned pieces. Some individual
Hpositive words nevertheless lose; it is not a count of480correct predictions.
For everyHzero word in a nonempty cell the cost is exactly−log2. ZL2andRF3unseen
words have no TRAINcell and get the registered zero-change fallback, explaining
the slight deviations from−log2in those aggregates. Their complete costs remain
in the primary failed UNSEENcomparison.

A post-selected illustration is ZL`alalor`,f106v.1G008,CurrierB,6working units.
The prescribed split is`ala|lor`. TRAINcontains the left half in`alaiin`(count1),
and right`lor`after a left ending ina in`chealor`,`okalor`,`opalor`(count1each).
The whole`alalor`is globally TRAIN-unseen. H=.000007832 versusM1=.000001055;
the50:50mixture's gain is1.437766nats for this occurrence. This small example
illustrates the registered arithmetic, not an identified stem/ending, a meaning,
a known historical word, or independent evidence selected before the result.

## Table cost and retained interpretation

| Reading | Left-half/cell entries | Right-half/seam/cell entries | Sum of fragment entries | Old whole/cell entries |
|---|---:|---:|---:|---:|
|ZL3b|925|1349|2274|2329|
|IT2a|996|1493|2489|2591|
|RF1b|922|1354|2276|2299|

This is not a tiny hand code: fragment entries are only modestly fewer than whole
entries, and their string lengths and stored counts are not priced by an MDL
criterion. M1is still present in both mixtures. On globally known words, the half
mixture beatsM1but loses toMIX_Q(equal-leaf−.047386/−.053907/−.052019). It wins
againstMIX_Qoverall by recovering some new combinations, whileMIX_Qgives every
unseen word in a nonempty cellQ=0. Beating that mixture on unseen words
alone would be insufficient; the stronger preregisteredM1comparison is failed.

1308's exact-whole weighting remains useful, but its improvement does not require
claiming that a scribe stored every whole indivisibly. This fixed recombination
also provides useful aggregate weighting. Its midpoint is an analytical convention,
not a discovered physical, syllabic or grammatical boundary. No actual author,
source alphabet, language, semantic message writer or word meaning is identified.

## Predecessors, decision and verification

160concerns edit-operation pairings at fixed graph/vocabulary;608BPEexterior roles;
326opaque host/renderer combinations;1246a conditional identical-half count in
dy-final words. Their different positives/failures stay.1305/1306selection caveats,
1285's failed estimator and the old opening/closing negative are not rescued.
No BPE, new last-letter target, tuned higher-order retry or reserve was used here.

Do not extend this failed fixed midpoint model with a selected new split, smoothing,
seam or mixture weight. Preserve its positive aggregate evidence as a comparison
baseline, not a selected complete productive mechanism. A different writer needs
an independently motivated construction and distinct prediction.

The source-free normalization/decision review preceded counting. Contract, programs
and sources were hash-locked before the run. The independent same-author verifier
reconstructs61181source joins and all23496native held scores from1233/915, checks the
unchanged1308M1/Qtables and scores, and verifies49fragment tables by exact rational
summation. All gates and leaf scores agree. PASS is computational/source fidelity,
not independent palaeography or language validation. The additional Hpositive/Hzero
unseen accounting was written after the result; its separate script and timing are
explicit. No change to the frozen predictor or primary decision followed.

No new rawTSV, corpus, image, old327/336body, f84/f84r/f116v/f1rbody or reserves.
Zero word meanings. Allworkincludingpublication within08:17–08:52UTCbudget10October.
