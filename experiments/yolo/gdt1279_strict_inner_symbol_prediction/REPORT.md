# GDT1279: exact previous-unit identity predicts strictly inner transitions

**INNER_EXACT_TRANSFER; EXACT_IDENTITY_ADDS_PREDICTIVE_VALUE.** On the same held
word positions, exact previous-unit identity improves next-unit prediction over
both an exact-position baseline and the fixed binary previous-unit class. The
primary gates pass for ALL and previously unseen interiors. The gain remains
when no transition touching the first or last unit is scored.

This is a positive formal prediction result, not discovery that Voynich words
are nonrandom. Whole-word transition prediction was already positive. The new
comparison locates a transferable contribution on strictly inner edges and
compares class versus exact identity on those same events.

| Reading | INNER cohort | Transitions | EXACT−POS: positive/all leaves | Mean gain | EXACT−BIT: positive/all leaves | Mean gain |
|---|---|---:|---:|---:|---:|---:|
| ZL3b | ALL |17399|46/46|+.637906|46/46|+.431377|
| ZL3b | UNSEEN_INTERIOR |2737|38/45|+.325913|35/45|+.202400|
| IT2a | ALL |19287|46/46|+.650711|46/46|+.440922|
| IT2a | UNSEEN_INTERIOR |3079|42/45|+.328905|34/45|+.199636|
| RF1b | ALL |16195|46/46|+.636865|46/46|+.432370|
| RF1b | UNSEEN_INTERIOR |2826|40/46|+.281128|35/46|+.182155|

Means are natural-log likelihood gains per transition, with equal physical-leaf
weight. They are not accuracy percentages, translation fractions or significance.
Each primary contrast required>=100transitions,>=10leaves,mean>=.01and>=two-thirds
positiveleaves. All primary requirements pass. Alternate readers are readings of
the same manuscript; sensitivity agreement is not independent replication.
The full per-leaf tables include every nonpositive novel-interior leaf.

## What is compared
All three models predict the SAME next working unit among the fixed22inventory.
All receive Currier, exact whole length and exact target ordinal. POS receives
nothing else; BIT also receives the previous unit's fixed1264class; EXACT also
receives its full identity. Additive smoothing is .5PERpossibleoutputsymbol in
every cell, with unseen contexts uniform1/22. Each reader fits only its odd leaves;
even leaves are scored unchanged. There is no hyperparameter or class search.

For zero-based target index i, INNER is2..n−2 in a word of n>=4units. EDGE is
first-to-second or penultimate-to-last. Thus neither endpoint of an INNER edge
is the first/last unit. Exact length/ordinal remain supplied; this is not a claim
that wider word context or outer forms are causally irrelevant.

The class itself retains useful information: ZLINNER BIT−POS is+.206529on46/46
leaves forALL, and+.123513on38/45fornovelinteriors. Exact identity adds more under
these fixed estimators. It does not follow that every compressed alphabet is
impossible or that this is the smallest sufficient representation.

## A concrete training-table illustration
For CurrierB, words of7workingunits, prediction of the third unit(i=2): after
`o`, odd-leaf data contain300next`k` among476transitions; after`e`,12next`k` among68.
Both `o` and`e` belong to the SAME fixed binary class. The smoothed EXACTmodel
therefore distinguishes contexts that BIT combines. These counts are a post-result
illustration from the saved training model, not a separately tested discovery,
a universal adjacency law, letter sounds, or a decoding table.

## Edges, scope and predecessors
For ZLALL, EDGE EXACT−POS is+.736839andEXACT−BIT+.381409, both46/46positive;
for novelinteriors they are+.650029(44/45)and+.314620(41/45). These are descriptive
edge comparisons. Different edge/interior denominators do not yield a causal
percentage attributable to boundaries, or a claim that boundaries never matter.

1278's failed model predicted BINARYordergivenlengthandbag. This test predicts
an exactnextunit with observedprecedingunit and exactposition. Its positive result
does not rescue1278, refititsbeta, or retroactively explain its failure causally.
The old endpoint-free failure concerns POSITIONstructure, not the present Markov
increment. Old full-word Markov,1264/65positives,1266capacitystop and1278nonconfirmation
all retain their original decisions. No claim of a fresh untouched corpus.

Novelty uses complete trimmed unitstrings from the own-reader oddn>=4inventory,
before excluding any individual edge. It therefore includes length2interiors,
unlike1265/66's length>=3scope. It does not mean far from oldfamilies, unseen in
project history, or a newly predicted exactword. Probabilities are not renormalized
on this outcome-defined diagnostic cohort. No copied/nearby-family mechanism is
ruled out by the novelty label.

## Source and numerical checks
All61181cached1233groups were joined to915raw groupIDs/forms and line metadata.
The inherited cache contains Pprose, definite outer wordspaces, pure raw groups
and the fixed22unitsegmentation; these are source conventions, not a known alphabet.
HeldeligiblegroupsZL7628/IT8623/RF7245yield32656/36534/30685transitionopportunities.
Exactly1ZLand1ITprevious-m transition have no frozen class and are excluded from
ALLmodels in both comparisons; RFhasnone. Unknownprevious counts inTRAINare also
explicit. m remains a legal output unit. No hidden classassignment or asymmetry.

Independent validation imports no primarycode and reconstructs all three count
tables, sourcejoins, all99873scoredheldtransitions, probabilities/normalization,
exclusions, novelty, every leaf/cohort and gate. PASS. Source-based counts and
frozenmodelhash are retained. Five toy probability checks cover normalization,
unseenuniformity and a knowncell. The separate source-free reviewer checked the
support/index/smoothing/novelty contract and its noncausal limits. These checks
are not independent palaeography or semantic confirmation.

## Decision for construction work
Retain exact-unit-conditioned inner transitions as a demonstrated predictive
constraint, including the specified new-interior cohort. A proposed writer must
account for these specific connections as well as wholeform and boundary effects;
blindly alternating the two classes is too coarse under this matched comparison.
No full writer, source language, phonetic interpretation, semantic root or word
meaning has been selected. Positive logloss does not identify a physical action
used by the scribe, and smoothing/modelcapacity remain parts of this comparison.
Do not automatically fit more classes or a decoder. No new source/image, sealed
or reserve access, relation edge, or public push. Local checkpoint only.
