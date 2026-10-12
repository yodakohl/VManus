# GDT1350 — Independent phonetic subclass transfer from contexts

## Decision before scores

1347 recovers known binary phone classes but its two reversible nonphonetic
sources pass the same alternation gate. 1279 already finds exact-symbol residual
beyond the native binary class; do not repeat it. 1348 supplies no native units.
The independently supplied cmudict.phones taxonomy offers a different test:
can context similarity transfer seven named nonvowel categories when the target
phone's category is withheld? Source controls only, no native classifier.

IDEA001026 motivates the question. Its raw next-context prediction estimator is
NOT executed here: select a fixed nearest-profile category classifier instead,
with this difference recorded before scoring. The other RAW remains untested.
No generic phonetic-origin claim follows from classification in one dictionary.

Unknown: whether this fixed richer known-label transfer works and distinguishes
these same three negative controls. PASS retains this conditional measurement
bridge; FAIL prevents its use as a calibrated native category detector. Neither
outcome provides native labels, establishes their units or rescues1347specificity.
Smallest test uses only1347's existing four packets and official category table.
No new sources, optimizer, word meanings, images or sealed/reserved material.
Budget30minutes from first recorded08:29:14UTC, including remaining preparation,
implementation, validation and publication. Initial retrieval preceded that clock
and is not assigned an invented exact duration. No automatic repair chain.

## Fixed design

CMU and SHUFFLED:24nonvowel phones, seven official categories including singleton
HH/aspirate. HH cannot be predicted correctly by an other-phone nearest neighbor;
retain that unavoidable miss in all denominators. PROCEDURAL_STRICT/VARIABLE:
24address units (truth0 in oldpacket). Assign the SAME seven class sizes using
sorted CMU consonant-name taxonomy list and a SHA256 order of opaque address IDs,
seed prefix1350procedural|. These arbitrary subclasses are not phonetic truth.

Use old8192TRAIN and8192TEST records unchanged. Strict internal target positions
1..n-2 have both neighbors. For every symbol make39-component left and right
count vectors. Add0.5 to each cell and normalize each side separately. Concatenate
with equal side weights; squared Hellinger ranking equals the sum over both sides
of squared differences of square-root probabilities (constant factor irrelevant).

For each of24TEST target profiles choose the nearest TRAIN consonant/address
profile, excluding that same symbol's own prototype. Resolve exact distance ties
by smaller opaque integerID. Predict the chosen prototype's supplied category.
No target category or phone names enter counts, distances or neighbor selection.
Coarse nonvowel/address membership is also supplied. Prototype categories ARE supplied: this is leave-target-label-out transfer, not
unsupervised recovery of seven unnamed categories or unseen-symbol discovery.
All units already occur in TRAIN; target's TRAIN profile is excluded as prototype
but its tokens can occur in other profiles' context dimensions. Test record
contexts are needed to estimate the target profile. No token-level decoder.

Report24-phone type accuracy and macroaccuracy across all7categories, including
HH=0. Report every target, neighbor, distances, counts and category errors.
All24targets must have>=20internal occurrences separately inTRAIN andTEST;
otherwise mark capacity insufficient, keep descriptive scores, do not change cap.

4096fixed random permutations of the24category assignments preserve category
sizes. Each permutation uses ONE shared table for prototype labels AND target
truth, not independently shuffled train/test labels. Fixed nearest-neighbor graph
is reused; labels never change distances. Seed=SHA256('1350perm|'+corpus+'|'+index).
Report plus-one tail fraction (1 + permuted macro>=observed)/(4097), not universal
significance or protection from the project's accumulated hypothesis selection.

Frozen joint gate: adequate capacity in all4corpora; CMU macro>=0.40 AND type
accuracy>=0.50 AND permutation fraction<=0.01; CMU macro exceeds EACH of the two
procedural and the within-word shuffled controls by>=0.15. All conditions must
pass. No pooling, label merging, singleton removal, metric or threshold changes.
Failure is this estimator/control contract, not all phonetics or all manner cues.

## Validation and limits

Independent validator imports no runner. Rebuild source counts, normalized
profiles, distances, nearest choices, all category/permutation scores and gate.
Verify original source hashes and code/protocol lock. Toy cases check self
exclusion, deterministic ties, normalization, all-one-category scoring and a
cyclic known-neighbor permutation count. Retain source provenance and1347limits.
Modern English dictionary types are not medieval connected speech; morphological
relatives may cross old split. Supplied units, spaces and prototype category
names are strong support absent in Voynich. Distinguishing these fixed controls
never excludes structured nonphonetic mechanisms in general. Zero new native
sounds or words; no interpretation of EVA letter names as actual sounds.
