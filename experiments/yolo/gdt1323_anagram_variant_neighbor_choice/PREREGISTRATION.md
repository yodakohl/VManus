# GDT1323: key-free anagram variant choice test

Decision note and preregistration, 11 October 2026, before native enumeration.
Inclusive budget 02:12–02:45 UTC: selection, implementation, validation and publication.
Stop at this single statistic/capacity result; no new endpoint metric, larger
conditioning scheme, source-language search or key search after outcomes.

Unknown: does the independent spelling-choice policy of GDT1322 survive a necessary
key-free consequence on the existing strict panel? GDT1322 has an exact abstract
inverse but no native bank/key/prior binding. Rather than fit that apparatus, use
an equality forced for EVERY modular additive key: identical working-unit multisets
have identical decoded characters. No meaning or actual homophony is asserted.

For any fixed source sequence prior, fixed bank B and positive spelling weights q,
conditional on the multiset at each position and the counts of each whole spelling
within each fixed selector/bag cell, every arrangement has the same likelihood.
The decoded source at each position and product q are preserved. A uniform shuffle
of occurrence labels is therefore an exact conditional null; identical labels have
equal permutation multiplicity. This remains true if q is selector-specific, so
we condition separately within each exact page selector. We do NOT require q to
factor over drawings or to give anagrams equal marginal frequency. The statistic
recomputes both endpoints after every shuffle. Joint/overlapping edges are not
independent samples. Fixed source length and greedy wrapping are preserved because
same-bag variants have the same unit count and same written character length.

Inputs are unchanged GDT1233 strict groups (unique22unit parses, definite outer
spaces) and previously independently verified GDT1319 pair packet for validation.
All current179selectors; no raw TSV, image or new admission. Readers separate.
Primary edges are ONLY original-index-consecutive groups at one exact source locus.
Never bridge omitted groups or line breaks. Page selector and original position
remain fixed. All data historically exposed: exploratory necessary-model test,
not reserved confirmation. Assumptions include valid22unit/group binding and
selection/transcription confidence independent of variant arrangement conditional
on retained masks. Violation can concern writing habit, segmentation or selection;
no claim that modular decoding in general is false.

Fixed statistic: echo when last unit of left word equals first unit of right word.
For each original edge compute its exact conditional echo probability from the
whole-variant pools. For distinct cells use independent endpoint count products;
for the same cell use ordered draws without replacement, subtracting self-pairs.
An edge is mobile iff this probability is strictly between zero and one. Keep ALL
mobile edges, no selected glyphs, word lengths or rare-form exclusions. Cells may
include retained groups that do not themselves participate in an edge.

Capacity: at least100mobile edges on at least10physical leaves per reading.
Physical leaf is numeric fN prefix, combining recto/verso and panel selectors.
On each mobile leaf compute (observed echo count - exact null expectation) divided
by its mobile-edge count. T is the equal-leaf mean. Condition on all cell counts
and draw1999permutations with Python random.Random(1323), reset per reading;
shuffle each nonsingleton cell in sorted (page, sorted-unit-tuple) order, original
rows sorted by id. Every replicate starts with original label order. Use the same
permutation for every edge involving a given slot. Record per-leaf count arrays.
Two-sided Monte Carlo p=(1 + number |T_null|>=|T_obs|)/2000; ties within1e-12
count as extreme. No fitted model, training split or learned score is involved.

Reject this exact independent spelling policy for a reading only if capacity
passes, permutation T has at least2distinct values, p<=0.05/3, |T|>=0.01 and at
least two thirds of mobile leaves have nonzero effects in T's direction. Report
all three readings; common rejection requires all three. Failure to reject is
not support or equivalence; inadequate capacity is a separate outcome. No automatic
repair using position-dependent q or hand fitting. Any later different policy
must be complete and independently motivated with its own distinct falsifier.

Source-free checks before native execution: exhaust occurrence permutations of
[ab,ab,ba] and compare endpoint expectations including same-cell exclusion;
for all9two-drawing weights modulo3 check each position's decoded value is invariant
under these permutations and the product q(ab)^2*q(ba) is unchanged. A separate
validator reconstructs edges from old1319pairs, computes expectations by explicit
weighted endpoint-type pairs rather than marginal dot products, rescores all
recorded draws and recreates the RNG permutations. No imports from runner.

Relevant primaries:1322construction/likelihood;1280preserves within-word endpoints
AND bigram counts and stopped for new-word control capacity (unchanged);1320tests
optional-fusion choice conditional on decoded whole-word identity, not anagram
choice by external neighbors;1319tests deterministic endpoint-state equality,
not stochastic choice. IP036's old proposal requires independently bound same-unit
realisations; here sameness is a necessary CONDITIONAL consequence of a complete
candidate, not an inferred linguistic identity. Existing negative decisions stand.
This creates no semantic/author-owned inscription relation packet; original text
adjacency is a statistical coordinate only, not a GDT388 meaning-bearing edge.
