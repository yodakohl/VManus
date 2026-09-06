# GDT857 — a deterministic cyclic-pool bound

Contract under test: each whole raw group is one codeword; codewords belong
to disjoint fixed plaintext-unit pools. Each pool visits every distinct member
once before refill, in any permutation per cycle. Initial phase is arbitrary;
there is no reset within a physical prose line. Every pool draw is output
exactly once unchanged: no hidden/skipped draws, no distinct pool members
with the same visible surface, and no copying/transcription error inside
the model. These are explicit model assumptions, not automatic rescue routes. This is a restricted mechanism,
not homophony generally and not an inferred historical cipher.

Proof: a nonsingleton pool can supply adjacent A A only across one cycle
boundary: A is last in one cycle and first in the next. A third A would
require another cycle boundary immediately after the second A, implying a
one-member cycle. Hence a run A A A forces A's pool to be singleton under
this contract. Disjoint fixed pools matter: A cannot silently switch pools.
One proper triple contradicts the subclass requiring every pool size>=2.
Arbitrary initial phase does not change this local argument. Singleton pools
permit arbitrary repeated A. No finite toy enumeration is offered as proof.

Frozen input: the three published GDT851 SOURCE JSON caches and their179
selector scope, without new data or images. Treat readings separately.
Only kind exactly P. For each within-line stored three-group window, require
consecutive1-based source indices, three identical raw strings matching
[a-z]+, and both internal separators DEFINITE_SPACE on both adjacent fields.
First.left_separator must be DEFINITE_SPACE unless its source index is1;
last.right_separator must be DEFINITE_SPACE unless its source index equals
metadata.source_group_count. No normalization, uncertain raw interpretation,
uncertain seam, index-gap bridge, cross-line or non-P inclusion.

Denominators: every stored length3window in P is a candidate; eligible plain
windows meet all structural/plainness requirements before equality; hits
add exact triple equality. Retain every qualifying hit, including overlaps,
with original strings, source IDs, indices, metadata and full source line.
Counts, unique repeated forms and physical folios are separate by reading.
All-reader concordance is the strict intersection of (locus,start_index,raw)
coordinates. It is not three independent manuscripts or image adjudication. Observations stay
transcription-bound, without native visual adjudication.

Any retained hit is a counterexample conditional on the reading and whole-
group codeword assumptions. Zero means no counterexample under this scope,
not acceptance. No held scoring, null model, p value, decoding, gloss or
self-synchronization study. A singleton-forcing result does not reject
homophony with some singleton pools, sampling with replacement, resets,
contextual pool switching, or finer-than-group codewords.

Pre-data controls: BAAB is allowed for a2-member pool across a refill;
AAA is impossible for size2 but possible for a singleton; arbitrary phase
is allowed. Enumerate three permutation cycles for sizes2and3 as a software
check of max run2, not a proof. Independent extraction fixtures reject raw
uncertainty, either uncertain internal/outer seam, index gaps, cross-line and
non-P cases. Independent validator re-enumerates actual sources and directly
verifies witnesses. --check must reproduce outputs byte-identically.

Root publicly registers before manuscript cache loading. f84/f84r explicitly
sealed; no data-scope enlargement. Preparation budget6min; root owns final
registration, registry and publication. This is a bounded deterministic test.
