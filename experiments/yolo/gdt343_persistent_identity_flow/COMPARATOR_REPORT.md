# GDT343 comparator report — persistent identity plus flow

Status: **PERSISTENT_IDENTITY_FLOW_NOT_CALIBRATED**.

The comparator contains 688 wording-distinct eligible records and 657 cross-collection parallel pairs. Concept identities are globally consistent opaque hashes; no names or source IDs are exported.

| model | top-1 | top-5 | MRR@100 | positive folds C>B | inclusive p |
|---|---:|---:|---:|---:|---:|
| RAW_OPAQUE_WORD_IDENTITY | 538/688 (78.2%) | 578/688 (84.0%) | 0.8075 | NA | NA |
| GLOBAL_ANON_CONCEPT_IDENTITY | 570/688 (82.8%) | 644/688 (93.6%) | 0.8755 | NA | NA |
| GLOBAL_ANON_IDENTITY_PLUS_FLOW | 568/688 (82.6%) | 644/688 (93.6%) | 0.8736 | 4 | 0.994874298 |

The nested comparison is C minus B: -0.001971 MRR, with C positive in 4/6 held collections and inclusive p=0.994874298.

Persistent identity itself is valuable in this readable calibration: B gains
32 top-1 hits and 0.0680 MRR over the diplomatic-word control A. The additional
flow features do not improve that identity signal. Their four positive folds
are tiny; the `gr1` fold reverses materially (MRR 0.6460 to 0.6327), leaving C
two top-1 hits and 0.0020 MRR below B in aggregate. The null result is in the
wrong direction (`p=0.994874298`).

C therefore failed its nested gate over B. This does not show that ordered
process structure is absent from recipes. It shows that this frozen
identity-specific path/edge/order/closure representation adds no transferable
parallel-recipe retrieval value once persistent normalized entity identity is
already known.

GDT327 remains unopened and Stage B is not run. Consequently no claim is made
about whether exact Voynich joint tuples behave as persistent entities or
whether grammar-derived flow adds value in Recipe/Stars or Pharma.

No concept name, concept ID, source form, semantic role, or word was exported as a graph feature. No Voynich role, meaning, language, plaintext, or translation follows. f84 was not accessed.

Independent validation reconstructs the 1,136-record source census, all 688
raw-word ranks, all 688 global-identity ranks, score/null arithmetic, hashes,
and the stop decision (`PASS 1458/1458`). It does not independently reimplement
the flow graph similarity, which is explicitly bounded in the validation
scope.
