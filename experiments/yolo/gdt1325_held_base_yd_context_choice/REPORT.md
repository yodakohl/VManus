# GDT1325 — external-flank choice does not transfer robustly to excluded By/Bdy bases

**NO_COMMON_HELD_BASE_CHOICE_TRANSFER; all three readings NOT_CONFIRMED.** Capacity and score mobility pass in every reading. The fixed learned flank predictor does not meet the registered joint effect, leaf-consistency and conditional-permutation gates. This is a tested nonconfirmation, not a missing-data stop or a general rejection of morphology.

| Reading | Paired training bases / used events | Held bases / cells | Held events / leaves | Equal-leaf AUC | Leaves above0.5 | One-sided p |
|---|---:|---:|---:|---:|---:|---:|
| ZL3b |50 /577|26 /93|452 /15|0.463316|9 /15|0.7555|
| IT2a |63 /794|30 /121|657 /18|0.573847|13 /18|0.1155|
| RF1b |43 /438|19 /70|314 /14|0.501143|7 /14|0.5020|

Required per reading: AUC>=0.55, at least two thirds of all retained leaves above0.5, and p<=0.05/3. IT retains a positive ranking effect and passes the first two gates, but does not pass the permutation gate. ZL and RF also miss effect/consistency. None passes even an unadjusted0.05permutation threshold. Do not invert the ZL score, select IT alone, remove zero leaves or change features after these outcomes. AUC is pairwise ranking performance, not translation or transcription accuracy. Readers are alternate transcriptions of one manuscript.

## Exact question and why it differs from earlier work

The transparent formal module has nonempty B not ending in d: tag0writes B+y, tag1writes B+d+y. Reading terminaldy before terminaly yields one unique analysis under that restriction. The source objects are abstract base/tag pairs, not translated words; this is not a full natural-language writing system. The competing nuisance account discards the tag and permits an independent spelling coin with a separate probability for every base and exact page.

GDT1204already excludes an exceptionless immediate-neighbor choice; its multiple analyses of some physical words were not carried over here. GDT1284's matched d→next-qmean remains positive but failed its consistency gate. GDT311found stochastic choices on licensed known pairs, and GDT865held out carriers/leaves for different ol/eol and edy/eodycontrasts. The present target is learned ranking on wholly excluded TARGETbases and physical leaves, evaluated within the same held base/page. It neither restores the old d→qresult nor weakens its gate.

## Selection, fitting and scoring

All unchanged strict1233groups have definite outer spaces and a unique22working-unit reading. Eligible center groups require both original-index-consecutive strict neighbors in the same source line and Currier A/B. No gap/line crossing. The full exposed cache licenses300/309/254paired bases in ZL/IT/RF; this license is not independent confirmation. It is invariant under the declared held-cell permutations.

Training uses odd physical leaves and base-hash parity0; testing uses even leaves and parity1. Other quadrants are not fitted/scored. Every target occurrence of a test base is excluded from training. Such a form may occur as a neighbor, but only its first/last unit enters, never its tag, body or identity. Both endpoint features are invariant to the modeled d insertion/deletion.

Within each Currier, only training base cells with both tags contribute. Each base/tag supplies total weight1to a separate left-last-unit and right-first-unit histogram. Sum over bases, add0.5per one of22units, normalize by K+11. The score is the exact rational product of dy/yflank-probability ratios. An untrained Currier falls back to equal scores; no such events are dropped by rule. No feature, sign or smoothing was selected using held labels.

Held comparisons use base/exact-page cells containing both tags. AUC compares dyagainst ywithin that same cell, with ties worth one half. Cells receive equal weight within a physical leaf and leaves receive equal weight overall, including tied/chance cases. This controls held-base/page tag proportions without using those labels to fit the predictor. The test covers the1423retained held events; it does not claim coverage of all unseen bases or forms.

The conditional null shuffles tags only within these held cells, retaining their counts and fixed scores. Under the independent percell coin these arrangements are exchangeable. Inserting/removing ddoes not change the first or last unit of any eligible group, so neighbor features remain fixed even when eligible groups are adjacent. Training is on disjoint leaves and unchanged.1999draws per reader were fixed in advance; all computations and ties use exact rationals or integer-scaled AUCs. Selection/transcription masks and layout being tag-independent after conditioning remain assumptions.

## Validation and decision

The separate validator reconstructs original915source-line windows, reparses raw groups and verifies61,181joins and11,746eligible events. It rebuilds training probabilities with rational per-event weights, verifies1423held scores and every matched cell, and recomputes all5997permutation scores by direct dy/ycomparisons rather than the primary rank-sum algorithm. Source-free inverse and endpoint-invariance checks cover160module alternatives; primary tied-rank fixtures cover14labelings. Validation PASS confirms the computation under shared source assumptions, not palaeography or semantic truth.

Do not use this predictor as evidence that dhas a shared grammatical meaning, or that y/dycan be freely merged. The result stops this specific transferable two-flank ranking rule. It does not prove no context dependence, equivalence of the forms, absence of a source feature, or the failure of every other grammar. No additional context features, split, matching, smoothing or subgroup repair is selected. Earlier positive family structure,311/865transfer findings and1204/1284limits remain intact.

This is exposed exploratory structural work, not reserved confirmation. No new image, raw mixed TSV, external source corpus, f84/f84r/f116v/f1rbody,327/336body or concrete word meaning was accessed or assigned. Protocol, both code paths and all input hashes were locked before native enumeration. Reproduce with the manifest commands.
