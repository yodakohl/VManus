# GDT1356 — Repeated sorted passes: certified capacity intervals

One fixed strict order on the supplied22working signs cannot generate every
strict whole group in three or fewer nondecreasing passes. At least four are
needed in each FULL transcription panel; explicit orders with five cover every
word. The certified minimum is therefore **[4,5]**, not an exact five.

For whole forms occurring on at least two physical leaves, the exact minimum is
three in IT2a and RF1b; ZL3b retains **[2,3]**. These are alternate readings of one
manuscript, not independent replications. GE2 is sensitivity, not a correction
of FULL or independent confirmation.

| Panel | Whole groups | Types | Certified lower | Replayed upper | Exact? |
|---|---:|---:|---:|---:|---|
| IT2a FULL | 22528 | 4272 | 4 | 5 | no |
| RF1b FULL | 19321 | 3818 | 4 | 5 | no |
| ZL3b FULL | 19332 | 3773 | 4 | 5 | no |
| IT2a GE2 | 19687 | 1466 | 3 | 3 | yes |
| RF1b GE2 | 16786 | 1315 | 3 | 3 | yes |
| ZL3b GE2 | 16865 | 1337 | 2 | 3 | no |

## A readable lower certificate

All three FULL panels contain exactly one `chkaidararal`, on f115v.37 G007,
one physical leaf. Its working units are
`ch k a i d a r a r a l`. The consecutive closed walks
`a i d a`, `a r a`, `a r a` occupy edge-disjoint intervals
[2,5], [5,7], [7,9] (zero-based positions). They share endpoints only.
Each return to the same sign after visiting a different sign requires at least
one decrease under EVERY strict total rank. Three forced decreases require at
least four passes. This is an arithmetic certificate conditional on that rare
reading and the supplied whole-word/unit contract, not a manuscript error
judgment or a word meaning.

The recurrent IT/RF lower witness is `dydydy`, two occurrences on leaves14and43:
f14v.6 G005/G006 respectively, and another occurrence on leaf43. Two disjoint
`d y d` walks already force three passes. Explicit global orders attain three
for ALL recurrent words in each of those panels. ZL's registered elementary
certificates reach only two; its three-pass witness does not prove optimality.
Full source rows, support counts and physical leaves are retained in RESULT.
No string embedded in a longer word is counted as a standalone occurrence.

## What was computed and verified

Frozen protocol: a pass is contiguous and nondecreasing under one global strict
rank; equal signs may repeat. Minimum passes under a fixed rank equal one plus
adjacent descents. Lower certificates comprise edge-disjoint nonconstant closed
walks, attested whole-word reverse pairs, and an all-type adjacent-edge bound.
The strongest retained lower certificates are the closed-walk witnesses above.

The bounded solver attempted only registered K values, stopping at its first
SAT rank. It reported UNSAT at FULL K4 and ZL GE2 K2; those diagnostic answers
are explicitly NOT accepted as lower proofs. The published intervals remain
[4,5] and [2,3]. No deeper optimization, new certificate search or timeout
extension followed. Explicit ranks in RESULT were replayed against every word.
Histograms and maximum-word segmentations describe those particular ranks;
they do not minimize average pass counts or identify original field boundaries.

Pre-native runner controls passed6552word/order cases and2925three-type
collections. An independently written validator, which did not read/import the
runner, passed6552word/order controls and220three-type collections, including
exhaustive short closed-interval packing. Native validation checked all61181
original groups,15981panel whole-type rank cases, support provenance, all lower
certificates, upper ranks, histograms and maximum-word segmentations. PASS is
arithmetic/source accounting, not validation of historical use. Code, protocols,
controls, fixed inputs and the prospective review were hash-locked before the
first native calculation (11:23:05UTC).

## Interpretation and next decision

This closes the capped family with at most three passes on FULL, conditional on
its rare witness and fixed units/boundaries. It also closes at most two passes
on recurrent IT/RF. A five-pass FULL or three-pass recurrent capacity remains
compatible; compatibility alone is weak because allowing many restarts can
accommodate arbitrary words. This is a construction constraint, not phonetic
origin evidence, a syllable analysis, plaintext or decipherment progress.

K1 failure was already known from1263. The new extension allows repeated
contiguous passes and reuses signs across them. It is distinct from1345sorted
disjoint classes with arbitrary interleaving,1321nonreturning blocks and1349
nested/circular fields; those old decisions and differing populations stand.
Reversing both words and rank preserves capacities, so direction is not inferred.
1355null limits,1354unit uncertainty and previous fixed phonetic-source failures
are unaffected. No new source, image, raw TSV or reserve was accessed.

Stop this capacity calculation at the registered bounds. A continuation needs a
source-bearing writer or an independently motivated rule for choosing restarts;
another optimizer to tighten4versus5 alone does not supply that missing link.
Review the existing producer queue and claim-bearing predecessors before any
new selection. No sounds, syllables, alphabet values or word meanings assigned.
