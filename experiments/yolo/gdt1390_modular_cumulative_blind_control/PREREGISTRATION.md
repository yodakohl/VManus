# GDT1390 — bounded blind recovery under a complete cumulative writer

Selected 2026-10-16 03:00 UTC, before control generation or recovery. This is a
control experiment, not a native reading or a new word meaning.

## Decision note

C1064 supplies a reversible 22-weight cumulative modulo-27 writer. GDT1324
established only tiny oracle-channel recovery; GDT602/604 retain the warning
that language-model pseudotext can outscore the true source. GDT1389 retains
bag preference and no positive conditional-order lead, not M1 sufficiency.
The unknown is whether a real 22-weight search can recover complete short
messages with a fully normalized choice law. Success permits a separate
native-pilot decision; failure stops this attack, without rejecting all
cumulative writers. No native pilot, reserve, dictionary repair or automatic
longer search is part of this experiment.

Inclusive budget: 90 minutes from 02:58 UTC (deadline 04:28 UTC), including
design, preparation, implementation, validation and publication. A runtime
gate must reserve at least 20 minutes for validation and publication. If the
fixed block will not fit, stop before recovery; do not shrink the sample or
increase the budget after inspecting outcomes.

## Complete spelling law

Use only IT2a, Currier B and the old GDT1308 odd-physical-leaf TRAIN selection,
joined exactly through GDT1233/GDT915/GDT631 caches. Fit missing lengths 1–3
with the same M1 add-0.5 smoothing; every length >=4 count must exactly equal
the corresponding frozen GDT1308 count. This completion and the length law
below are new assumptions, not inherited tested conclusions. No held native
group is used for fitting or scoring.

The 22 ordered working units are a o e i n d q y s r l m k t p f ch sh ckh cth
cph cfh. L=max(27,maximum TRAIN length). Give length n in 1..L mass
(count(n)+0.5)/(TRAIN_N+0.5*L). For each length, position and previous unit,
use M1; absent contexts are uniform over 22 units. Thus P(w)>0 for every
unit-string of lengths 1..L. Let h_K(w)=sum of its weights mod27 and
Z_K(r)=sum_{h_K(w)=r}P(w). Keys have at least one weight coprime to 3, hence
all 27 states have positive mass. Positivity does not guarantee practical
rejection sampling; generate by exact backward residue dynamic programming.

Source alphabet is SPACE=0 and a..z=1..26. Each complete control message starts
at s0=0. Update s_i=s_(i-1)+c_i-b mod27, then draw w_i from P(w)/Z_K(s_i)
on that state. Read c_i=h_K(w_i)-h_K(w_(i-1))+b, with initial previous state0.
No line resets, nulls, missing groups, arbitrary bank restrictions or free
per-word parameters. These working units and message framing remain assumed.

## Source law and independent controls

Use the six already cached GDT001 language packs, with pinned original hashes.
Collapse whitespace to single spaces and retain their existing ASCII a-z
projection. Split the resulting character stream at floor(0.8*N). Fit source
models solely on the prefix; select control fragments solely in the suffix.
The last boundary is not claimed to separate historical works. No phonetic
claim or native language choice is made.

Fit one add-0.5 character Markov model of order3 per pack. At each training
position count all available context lengths0..3; at inference use the longest
available history, length min(3,i). No hard word list or space restriction.
The source likelihood is the equally weighted mixture of six COMPLETE-message
likelihoods, not a per-character mixture. All candidate likelihoods are
logsumexp(source_LL)-log(6)+sum(log P(w_i)-log Z_K(h_K(w_i))).

Twelve positive controls: one 77-character and one 120-character suffix
fragment per source pack, starting at a word boundary, with no overlap. An
ending partial word is permitted. They are complete synthetic messages, not
historical paragraph claims. Each has an independently drawn uniform valid
22-weight key and uniform b. Six negative controls permute all 77 source
characters within each corresponding positive control, retain its key, and
draw fresh spellings. Permutations are not resampled for favorable properties.
The 18 anonymous cases are randomly ordered. Generator owns a private entropy
seed and truth file; seed and truth are released only after the recovery-output
hash is frozen. The optimizer receives spelling sequences, fixed models and
anonymous IDs only; each case is searched independently.

## Fixed search and gates

32 independent uniform valid-key starts per case, 256 single-coordinate
proposals per start. Select coordinate uniformly and replace it uniformly
with one of the other26 residues; reject keys without an invertible weight.
Evaluate exact Z and all18 invertible global scales times all27 offsets.
Retain the maximum complete-mixture likelihood in this orbit; ties use
lexicographic effective K then b. Metropolis acceptance with linearly falling
temperature 2.0 to0.1 over256 proposals; retain the highest score ever seen.
Root seed1390000, case/start-derived seeds fixed by the runner. No truth-key
starts, supplied rivals, beam repair, hand edits or stopping on plaintext.

First benchmark100 independent fixed random keys, including exact normalization
and full orbit/source scoring. Use at most32 CPU workers. Proceed with all18
cases only if a conservative extrapolation (2x measured total CPU cost divided
by worker count, plus startup) fits the remaining budget minus20 minutes.
No decoding outcomes enter this runtime decision.

Primary recovery gate: all12 positive messages recovered exactly. Report
character agreement, exact effective key equality, observed-message-equivalent
keys, and unobserved/linearly dependent weights separately; exact message
recovery does not establish a uniquely identified key. Negative controls
cannot count as readable evidence. A source-likelihood/character threshold
may not be learned from these controls and transferred to native text.

After all output hashes are frozen, compare each winner with its true-key
exact likelihood: worse score indicates search failure; a better wrong winner
indicates model mismatch/finite-message ambiguity, not a manuscript finding.
Any primary-gate failure ends this search route. Passing allows only a new
explicit pilot selection, with negative-control and identifiability review.

## Validation and access

Independent backward/forward DP implementations must agree on Z and the
18-scale symmetry, including a degenerate one-invertible-weight key. Exhaustive
small-alphabet fixtures check normalizations, sampler conditionals, state
updates and full source-mixture scores. Independently replay all generated
messages, check training/control split and frozen long-table equality, and
recompute all final/true scores after unblinding. Engineering corrections must
be recorded; outcome-driven scientific changes are prohibited.

No raw language-pack copies are published; retain pinned hashes, sampling
offsets, seed and reproducible model artifacts. No images or raw mixed-scope TSV
are opened. f84 and f84r stay sealed; f116v, f1r bodies, GDT327/GDT336 remain
unadmitted. This experiment produces no Voynich plaintext or meanings.
