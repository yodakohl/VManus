# GDT1382 — No homophonic cost exclusion from local identity alone

Status: **ALL_18_HOMOPHONIC_BOUNDS_INCONCLUSIVE**.

## Question and result

Can fixed same-sign identity, including its appearances in the two-character
context and the next event, exclude every many-to-one consonantal key without
assuming any positive reverse-channel cost? The new bound is valid but all18
reader/model comparisons are inconclusive. It provides no new excluded language
or writing family, no candidate key and no translated word.

The exact registered [contract](PREREGISTRATION.md) retains all1380data/model
choices and allows different signs to share a target. Each row is minimized
independently; reverse ambiguity cost is optimistically bounded by0. This is a
lower bound, never an actual complete likelihood or successful reading.

Paid lower cost minus matched KT upper, in bits (negative means inconclusive):

| Fixed pack | ZL3b | IT2a | RF1b |
|---|---:|---:|---:|
| latin | -48,694.872321 | -111,013.427502 | -40,524.676680 |
| medieval_czech | -28,200.495222 | -62,971.513615 | -24,800.139886 |
| middle_french | -49,666.499414 | -114,190.116362 | -41,652.021157 |
| middle_high_german | -38,647.457834 | -87,513.617080 | -32,776.535386 |
| old_hungarian | -38,766.817917 | -89,686.281176 | -33,406.395599 |
| old_italian_tuscan | -37,950.327483 | -87,197.912017 | -32,348.920952 |

Readers are alternate readings of one manuscript and have different eligible
corpora; these are not independent replications or comparable language rankings.
The smallest magnitude negative margin still exceeds24,800bits. Exact ticks,
all4,404row certificates and KT intervals are in [RESULT.json](artifacts/RESULT.json).
No near-zero numerical ambiguity is involved. No comparison was selected away.

## What this does and does not change

GDT1381's six IT2a injective certificates remain valid for their fixed family.
They cannot be transferred to this many-to-one family: a free successor can reuse
a context target, and distinct context signs can collide. The formerly empty
ZL3b/RF1b injective families now have legal maps, so their matched KT intervals
were computed from unchanged1380context counts. The IT2a interval equals1380.

This test establishes that this particular relaxation is insufficient, not that
an affordable global key exists. Different rows' minimizing maps need not agree,
and the reverse channel would generally cost more than0. Those relaxed constraints
explain why an optimistic bound can be far below KT without yielding a reading.
No claim is made about how much each relaxation contributes on these native data.
GDT194's old local-search failure remains a local failure on its historical scope.

## Validation and chronology

Source-free exhaustive maps checked before native execution: primary1,920local
map cases plus8global maps; independent controls include a normalized repeated
identity counterexample, collision advantage, reuse of context images,3source
signs into2targets and fixedSPACE/BOS. These validate the method, not the manuscript.

The registration lock bound both programs, protocol, proofreviews and all inputs
before native execution. Its manually entered `registered_utc`14:46:30Z label is
erroneous: the first post-execution clock reading was14:45:53Z. This is retained
as a metadata error, not presented as a trusted chronology certificate. Tool
execution order established the hash lock before the native command; no scientific
input, program, rule or hash was changed after native results. The independent
replay checks the frozen hashes and complete result. See VALIDATION.json and
RESULT_REVIEW.json for its outcome.

## Decision and dependencies

Stop this bound branch as preregistered. Do not automatically add row coupling,
partition search, an entropy penalty or a different reverse channel. A further
homophonic test would need a separately motivated, explicit human writing rule
and a new decision-changing falsifier, checked against known counterexamples.
The variant choice must be explained for a full probabilistic model; its global
IID Dirichlet form in194 is an assumption, not a historical fact.

Dependencies:1380lossyASCIIrepresentation and admitted complete loci; fixed21target
consonants, six prepared order2models, fixedSPACE/BOS, mlog2(21)key and log2(6)selector;
no word meanings or phonemic values assumed. No new transcription, source text,
image, reserve or sealed-data access. No general phonetic, abjad or language ban.
