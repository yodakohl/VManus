# GDT1350 — Manner transfer is partial; the fixed joint gate fails

**MANNER_TRANSFER_JOINT_GATE_FAIL.** The fixed context-profile classifier transfers
an independently supplied category correctly for13of24CMU nonvowel phones.
Equal weighting of seven categories gives67/168=39.8810%. This is an association
with known phone metadata, but it misses the registered40%threshold and the
required15percentage-point separation from the strongest procedural control.
The shuffled control also lacks one occurrence required by the capacity gate.
No threshold, category or population was repaired after these outcomes.

| Corpus | Correct types | Seven-category macroaccuracy | Permutation tail | Capacity |
|---|---:|---:|---:|---|
| CMU phone sequences |13/24 (54.17%)|67/168 (39.88%)|6/4097 (0.00146)|PASS|
| Procedural fixed fields |10/24 (41.67%)|15/56 (26.79%)|25/4097 (0.00610)|PASS|
| Procedural variable fields |7/24 (29.17%)|11/56 (19.64%)|280/4097 (0.06834)|PASS|
| Shuffled CMU phone bags |9/24 (37.50%)|11/56 (19.64%)|233/4097 (0.05687)|INSUFFICIENT|

The CMU minus strict-procedural difference is22/168=13.0952percentage points,
below15. The CMU macro threshold miss is only0.1190percentage points: retain the
fixed decision without pretending this tiny numerical gap refutes phonetics.
The other limitations remain even if that small gap is ignored.
SHUFFLED DH has21TRAIN and19TEST internal occurrences, versus required20each.
Its descriptive score remains visible but cannot satisfy the adequate-control
condition. No missing phone is default-filled or omitted.

## What was actually predicted

Use the exact fourGDT1347packets,8192TRAIN and8192TEST records per source. For each
symbol, count its immediate left and right neighbors at strictly internal target
positions. Normalize both39-component vectors separately after adding0.5percell.
Choose the nearest TRAINprofile to each TESTprofile by squared Hellinger distance,
excluding that same symbol's own prototype; ties use the opaque integerID.
Transfer the other prototype's category to the target, then compare with the
withheld target category. No names or category labels enter the distance.

Coarse nonvowel/address membership and the other prototypes' named categories
ARE supplied. This is not unsupervised recovery of seven classes or a previously
unseen alphabet. All symbol identities occur in TRAIN; test contexts are needed
to estimate profiles, and target symbols may occur as context coordinates of
other symbols. We withhold the target's label, not its existence everywhere.
The old split can contain morphological relatives and is not independent speech.

The7CMU categories are official source metadata: stop, fricative, affricate,
nasal, liquid, semivowel, aspirate. Their phonetic usefulness is being tested;
the names are not inferred from Voynich glyphs. The procedural categories have
matching sizes but are fixed arbitrary address labels, not phonetic truth.
A single source/assignment pair cannot characterize all nonphonetic mechanisms.

## Manual inspection of retained errors and successes

| CMU category | Correct / total |
|---|---:|
| stop |5/6|
| fricative |5/8|
| affricate |1/2|
| nasal |1/3|
| liquid |1/2|
| semivowel |0/2|
| aspirate |0/1|

BchoosesP andPchoosesB; SHchoosesZH andZHchoosesSH. Those are correct category
transfers. However, DchoosesTH, VchoosesD, LchoosesN and NchoosesL, crossing the
supplied category boundaries. These are post-result illustrations, not a new
selected subset. They show why plausible individual pairings do not establish
a recovered phonetic taxonomy. No actual Voynich sign has received a sound.

HH is the only aspirate, so other-phone1-NN can never predict that category.
That known miss remains in both type and category denominators, as preregistered.
It was not discovered after results or used to justify removing a category.

## Why a small permutation tail does not rescue this

4096fixed permutations preserve all7category sizes and use one shared permuted
label table on both ends of each fixed neighbor link. Tail fractions compare the
observed grouping with random groupings on that same graph. CMU's observed
partition has a small tail fraction; so does the strictly nonphonetic source's
arbitrary partition (25/4097). Thus the tail number alone cannot license a sound
interpretation. It is not a global significance calculation accounting for all
historical research choices. The joint gate expressly retains the controls.

## Decision, predecessors and next boundary

The rawIDEA001026 suggested a held-predecessor next-context predictor. This test
selects a different1-NNcategory-transfer estimator within its broad question;
the distinction was frozen before execution. The raw predictor remains untested.
IDEA001027's paired rendering intervention is also raw, not executed here.

Retain a limited source-level category association; do not deploy this estimator
as a calibrated Voynich manner decoder. GDT1347's binary class recovery remains
positive, its origin-specificity gate remains failed. GDT1279's native exact-ID
increment remains positive and was not repeated. GDT1348's native unit question
and template stop remain. This is neither a phonetic-language exclusion nor a
justification for another automatic control/feature repair. Any next phonetic
proposal needs a distinct predeclared prediction and an explicit account of the
missing native unit/label bridge. No new source corpus, classifier tuning,
Voynich sounds, source language, word meanings or reserve use is selected here.

## Reproduction and validation

The source packet, official taxonomy, protocol and both programs were hash-locked
before any1350score. A source-free prospective peer checked self-exclusion,
normalization, coupled permutations and thresholds; one missing toy fixture was
added before the lock. An independent checker imports no runner and rebuilds
344260context events,2208distances,16384permutation scores, all24predictions per
source and the joint gate. Five source-free fixtures pass. Original packet
provenance and licensed upstream files remain inGDT1347; no external access or
native manuscript reading occurred. Arithmetic PASSdoes not convert the failed
research gate into a successful phonetic decoder.
