# GDT1264 — a binary interior alternation preference transfers

**A positive exploratory structural lead.** One symbol partition learned only on
odd physical leaves predicts extra alternation on even leaves, including whole
forms absent from training. It meets both predeclared ZLmateriality gates. The
reference expectation retains each word interior's exact symbol counts. This
is not vowel/consonant identification, a complete writer or a translated word.

| Reading | Held cohort | Scorable groups | Positive leaves / all | Equal-leaf cross-rate excess |
|---|---|---:|---:|---:|
| ZL3b | ALL |5301|37/46|+0.0694991|
| ZL3b | UNSEEN_WHOLE |1358|43/46|+0.0839142|
| IT2a | ALL |5863|39/46|+0.0670860|
| IT2a | UNSEEN_WHOLE |1568|41/46|+0.0779660|
| RF1b | ALL |4880|39/46|+0.0699128|
| RF1b | UNSEEN_WHOLE |1390|43/46|+0.0779750|

For instance,+0.0695means about6.95percentage points more cross-class adjacencies
than the uniform exact-interior-bag expectation, averaged with equal leaf weight.
It is NOT6.95percent of entropy, variance or manuscript content explained. The
0.03and2/3thresholds are predeclared descriptive engineering gates, not pvalues.
Three readings are alternatives of one manuscript, not independent replications.

## The frozen partition
Training used4909eligible interiors on44odd physical leaves. Exactly21working
units appeared; m had no training interior class. Exhaustive optimization of all
1,048,575nontrivial complementary-anchored partitions had one best partition:

    class0: a e l n o p y
    class1: cfh ch ckh cph cth d f i k q r s sh t

Class names0/1carry no meanings. In particular i/e,p/fandl/r separate here; neither
Roman transcription names nor a superficial glyph resemblance justify phonetics.
The reported table is a fitted statistical feature, not a discovered alphabet.
The training objective was the fixed10^-6rounded aggregate signed-cut matrix;
the selected unrounded training excess is1930741/1260crossings. This pooled
training count objective differs from the equal-leaf TESTreport by design.

The table was hash-frozen before TESTevaluation. No held outcome chose its classes,
rounding, thresholds or partition tie. All source text was already project-exposed;
this phase split is exploratory transfer rather than untouched confirmation.

## Full coverage, countercases and novelty limits
Exactly the first and last working unit were removed, and only interiors of
length>=3were eligible. Of10007ZLheld groups,4705are too short;5302are eligible.
One eligible group, qokamdy atf104v.2#6, contains m and is explicitly unscorable.
IT has the same unscorable whole. RF has no corresponding unscorable group under
its reading. No unknown class was fitted or defaulted after seeing the target.

ZLALLhas16--495scorable groups per leaf(median44.5). Its9negative leaves are
f2,f4,f8,f10,f18,f22,f30,f32,f44. UNSEEN_WHOLEhas2--117groups per leaf(median15);
f2,f18,f30are negative, with3,7,22groups respectively. All outcomes stay in the
artifact; no leaf was removed to meet the gates and sparse leaves are not hidden.

Unseen means the COMPLETE original whole was absent on that reader's odd leaves.
A post-result scope count finds that629/1358ZLunseen-whole events already have a
known trimmed interior, while729have a new interior. Corresponding ITcounts are
749/819andRF645/745. No separate score or success claim was computed for the new-
interior-only subset. Thus43/46must not be presented as a new-interior-only result.
The counting illustration is reproducible with src/scope_diagnostic.py; it was
not part of selecting the partition or the primary validator's gate outcome.

Three familiar examples illustrate why the rule is probabilistic:

| Whole | Interior | Classes | Crossings | Bag expectation |
|---|---|---|---:|---:|
| qokeedy | o k e e d |0 1 0 0 1|3|12/5|
| daldy | a l d |0 0 1|1|4/3|
| daiin | a i i |0 1 1|1|4/3|

qokeedy contributes positive excess, while daldy/daiin contribute negative excess.
No exception is repaired and the e-e repetition already violates strict alternation.
Examples were named after the result for explanation; exact sourceIDs and raw-unit
sequences are preserved in the post-result scope diagnostic. No meanings assigned.

## What this establishes and what remains open
The earlier Markov work already established portable local word structure. The
new contribution is a particular compact binary contrast with the shown transfer,
not discovery that words are nonrandom.1263's fixed-rank sort failure remains:
alternation permits going back and forth between classes, unlike monotone sorting.

The exact-bag comparator does NOT preserve detailed within-interior positional
frequencies. Even after trimming the outermost units, position-specific templates
can produce this effect. This test does not establish an incremental interaction
beyond the previous5-position model, a two-stage pen movement, syllable boundaries,
productive morphology, unique parsing or reading direction. The statistic is
unchanged by reversing each whole interior. There is no new source language.
A future writing hypothesis can retain the binary preference as one constraint;
it must still carry content and account for the negative and unclassified cases.
No third class, changed split, extra smoothing or glyph-role assignment is selected.

## Reproduction and verification
Run src/run.py train, then src/run.py evaluate, then src/validate.py. Training
compiles the source-bound C++Gray-code optimizer into an ignored .cache binary.
The independent validator imports no primary code. It rebuilds exact rational
weights by position pairs, verifies every one of the1,048,575binary assignments
using an independent vectorized enumeration, reconstructs all six cohorts and
20,364saved events, and checks every rational leaf effect and fixed gate. PASS.
Separate software implementations by root are not independent palaeography.
The producer's source-free expectation/cut proof read no data or optimizer output.

Source is the unchanged guarded1233whole-group cache. No rawTSV query, image,
new source corpus, f84/f84r, f116v or reserve access. Original working-unit/group
assumptions remain. Protocol/program hashes preceded training; TRAIN_LOCK precedes
evaluation. Native meaning count remains0. Inclusive17:27--18:02UTCbudget covers
selection through local closure; local4Octoberexception means no commit/push.

Timing qualification: the binary-partition direction was already under consideration
by the17:23UTCnavigation.17:27is the recorded formal decision-window start,
not a certified inclusive beginning of every preparatory thought. No exact
35minute total is claimed. The frozen scientific contract and all results remain
unchanged; no additional fit or control expansion was made after the result.
