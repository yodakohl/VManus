# GDT1351 — A reversible phone renderer makes phase the unique optimum

**PAIRED_PHONE_CLASSES_STRICTLY_SUBOPTIMAL__PHASE_GLOBAL_OPTIMUM.** Changing only
the written representation of the same16,384CMU phone sequences reverses the
interpretation of the binary alternation objective. On the two-component channel,
the first/second component partition is the unique global optimum up to label
swap, separately in TRAIN and TEST and under both endpoint conventions. Every
inherited binary phone partition is strictly worse on every selected word.

This is a source-control theorem and paired demonstration, not new native
manuscript evidence. The exact effect was derived before scores. It does not
identify how Voynich was written or reject phonetic content: these controls are
known phone sequences before AND after reversible encoding.

## Same source, different written units

Take exactly GDT1347's8192TRAIN and8192TEST CMU phone sequences, with their word
boundaries and official vowel/nonvowel labels unchanged. Replace each phoneu by
two different signs L_u,R_u. All78signs are distinct and receive opaque IDs from
a fixed hash order; labels do not select the code. Every complete encoded word
inverts exactly to its original phone sequence (16,384checks).

The true phone class remains expressible on the component alphabet: BOTH halves
inherit the same vowel or consonant label. The competing phase classification
instead separates the first half of EVERY phone from its second half. Thus this
is not a case where sound membership was made mathematically undefinable.

The78signs, doubled lengths and paired layout are intentionally constructed and
change together. This is not an attested medieval script or a22signVoynich model.
No source language was chosen for Voynich. Known inverse checks do not constitute
blind segmentation/code recovery. No optimizer or native decoder was built.

## Scores on the same held source words

Values below are32-block mean bag-adjusted switch excess per written adjacency,
using the old256records per block. Positive means more switches than expected
from the same word's binary inventory; it is not a language probability.

| Representation and endpoint convention | True inherited C/V | First/second component phase |
|---|---:|---:|
| Atomic phones; remove outer phones |+0.193617466|not applicable|
| Render complete word, then remove outer signs |−0.085265560|+0.454737890|
| Remove outer phones, then render |−0.174385655|+0.444723239|

The atomic result exactly equals the recorded GDT1347 baseline. Its inherited
class score is positive in32/32blocks; both rendered arms have0/32positive
inherited blocks. All four rendered TRAIN/TEST graphs contain78active signs and
one connected component. Consequently each has exactly two maximizing binary
assignments, which are complements of the same phase partition. The TRAINphase
partition also realizes the optimum in TEST. This is a theorem-backed optimum,
not a heuristic search result or a claim that atomic1347global optimality was
proved retroactively.

Minimum phase-minus-inherited exact unnormalized score on any record is3 when
rendering before trimming and2 when trimming before rendering. Every record is
retained, including repetitions inside words. Matching endpoint removal at the
phone level therefore does not remove the effect. This does not isolate all
other aspects of representation: sign inventory and sequence length also change.

## Why this is inevitable for the fixed criterion

For an even-length binary sequence of lengthM≥4, with minority countm andSswitches,
the score is Q=S−2m(M−m)/M. A balanced alternating sequence achieves M/2−1.
Every other sequence scores less: for an unbalanced sequence S≤2m, implying
Q≤2m²/M≤M/2−2+2/M; for a balanced nonalternating sequence S≤M−2.

The phase partition attains the upper bound on every rendered word at once.
For ANY inherited phone partition, consecutive halves of a phone stay together.
Each minority source phone supplies at most as many switches as its emitted
minority components, so S≤m and Q≤m(2m/M−1)≤0. Phase wins strictly for the selected
n≥5phone words. This proof covers all binary phone label assignments, not merely
the official C/V table. It is a statement about this renderer and score, not all
possible phonetic tests.

Every aggregate maximum must alternate along every observed adjacency. A connected
union graph forces all sign classes once one sign's class is chosen, giving
uniqueness up to swap. The code computes connectivity rather than assuming it.
The exact loss for any nonmaximizing cut is at least3/4or2/3 in the two arms.
Rounding each aggregate pair weight to10⁻⁶, as in the earlier implementation,
can change a difference between two cuts by at most3003/(2×10⁶)=0.0015015.
That is too small to change the optimum. No larger solver, more restarts or more
precise search can turn the inherited phone classes into the optimum here.

For intuition, take a toy source class pattern C V C V C. Its trimmed atomic
pattern V C V scores2/3. Doubling each class and then trimming leaves
C V V C C V V C, whose inherited score is0; component phase scores3.
Trimming the source before doubling leaves V V C C V V with inherited score−2/3;
phase scores2. This is a source-free illustration, not a guessed Voynich reading.

An additional analytic consequence: phase assigns opposite labels to a phone's
two halves, while inherited C/V assigns the same label to both. Under either
label orientation, exactly one half per complete pair agrees:39/78component types
and50%of complete-word component tokens. This is not a directly comparable
phone-level decoding accuracy or a newly fitted classifier score; denominators
and units differ from the old39phone recovery benchmark.

## Decision and relation to prior failures

IDEA001027's representation objection is established for this fixed control.
Require an explicit unit/representation argument before reading a binary cut as
native phonetics. Do not treat a failed raw-component sound classification as
proof that underlying content cannot be speech. The paired control strengthens
that measurement boundary; it does not supply Voynich units itself.

GDT1347's known-phone binary recovery and nonphonetic-origin countercontrols
remain. GDT1350's finer manner joint failure remains. This does not explain
GDT1346's historical-spelling failure solely by digraphs, because its writing
system was not this constructed code. GDT1348's graphic unit question remains
unresolved. GDT1264/1265native structure remains positive. GDT1269's native
pair-code capacity bound is a different contract on22working units, not rescored.

No historical writer reconstruction, native sound, word meaning or new language
exclusion. No reserved data, image, web source or raw transcription accessed.
A known control inverse does not authorize automatic native pair grouping,
new segmentation algorithms, or another chain of classifier repairs. Next work
must independently review a concrete unit-evidence proposal; no such proposal
is selected by this result alone.

## Validation

Protocol, scripts and fixed sources were hash-locked before source calculation.
A separate source-free peer verified both extremal arguments, endpoint handling,
connectivity criterion and rounding bound. The independent validator imports no
runner and recomputes expectations by ordered unequal-position counts. All16,384
inverses,81,920record scores, four graphs and aggregate/block statistics pass.
Exhaustive fixtures check21,844binary strings of even length2..14 and1,008inherited
renderings of source patterns of length3..8; the length2tie exception is retained.
Arithmetic and proof checks are not independent palaeographic confirmation.
