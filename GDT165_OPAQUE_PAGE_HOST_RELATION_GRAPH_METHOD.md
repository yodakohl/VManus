# GDT165 — opaque PAGE_HOST relation graph

Status: `METHOD_AND_ANALYSIS_FAMILY_FROZEN_BEFORE_SCORING`

## Question

Treat every exact HPR2 `PAGE_HOST` identity as an opaque candidate lexical or
code unit.  Does that identity predict the next physically adjacent host on an
unseen folio beyond section, Currier, hand, frequency, and line-position
effects?  Do directed host relations or host communities remain stable when a
section or hand is wholly excluded?

GDT165 does not use characters inside an identity.  It does not test glyph
substitution, edit distance, prefixes, suffixes, roots, phonology, morphology,
or semantics.

## Source and parser firewall

Input is `gdt062_right_family_inventory.tsv`, but each row is immediately
reduced to:

- opaque SHA256 identifier plus the exact PAGE_HOST display identity needed
  only for reproducible joins;
- physical locus and integer group index/count;
- physical folio, section, Currier, and hand.

Raw token, wrapper, inner-D, local frame, right family, DY, B3, and every other
same-group parser field are inaccessible to the model.  The primary edge is
`group i -> group i+1` only when both indices occur on the same physical line.
No cross-line or cross-page edge is invented.

Every row whose page or locus begins `f84` is rejected before retention.  No
f84r row, image, transcription, or formal payload may be opened, queried,
retained, joined, or scored.

## Fixed nuisance and exact-host models

The target alphabet is the frozen set of exact next-host identities.  ZL3b,
IT2a, and RF1b are alternate readings, not replications; this experiment uses
the already frozen HPR2 display view only.

For each source event, nuisance key is:

`(section, Currier, hand, global source-frequency bin,
  source-position quartile, physical-line group-count bin)`.

Frequency bins are `1`, `2--4`, `5--15`, `16--63`, and `64+`; line-count bins
are `2`, `3`, `4`, `5--7`, and `8+`.  These bins are fixed once from the
text-blind adjacency census.  For each of the six nuisance variables, form a
separate target-count distribution with concentration 32 toward the training
target unigram; the nuisance prediction is their equal-weight arithmetic
mixture.  Thus when a section or hand is wholly excluded, that unavailable
component backs off to the unigram while the other five controls remain
active.  No interaction or mixture weight is fitted.

The exact-host model adds the opaque source identity with concentration 16
toward the nuisance distribution.  It never sees any character, substring, or
same-group field.  Score held codelength gain in bits:

`nuisance_bits - exact_host_bits`.

Run three outer evaluations:

- leave one physical folio out;
- leave one section value out;
- leave one hand value out.

All model counts and probabilities are learned without the held unit.  Report
total and per-event gain, positive-fold fraction, coverage of source identities
seen in training, and target top-1/top-5 accuracy.  A target identity absent
from training receives the shared Jeffreys prior in both models.

## Community model

Freeze the 128 opaque identities with greatest full-panel endpoint frequency;
ties use SHA256 identity order.  This capacity-only selection never sees a
neighbor label.  It covers 94.6% of edge endpoints and 62.7% of edges at both
ends in the source audit.

For every training split, build an undirected symmetrization of its directed
adjacency counts on these identities.  Normalize by node degree, take the eight
largest eigenvectors, row-normalize, and apply deterministic farthest-first
eight-means.  Identity strings and glyph features never enter this fit.  Hosts
outside the 128-ID panel share `OTHER`.

The community model predicts the next-host distribution with concentration 16
toward the same nuisance model.  Compare its held gain with both nuisance and
exact identity.

For descriptive stability, compare full-graph community coassignment with
each held-section and held-hand graph using pairwise coassignment Jaccard.
Against each split, 1,024 label permutations preserve the split community
sizes.  Communities are stable only if median held-section and held-hand
Jaccard exceed their respective 95% permutation quantiles and the community
model has positive gain in all three outer evaluations.

K=8, the 128-node panel, normalization, initialization, smoothing, and all
thresholds are fixed before scoring.  No alternative K is searched.

## Directed-relation atlas and null

For each real directed pair, aggregate held-folio, held-section, and held-hand
log2 gain of exact host over nuisance.  A relation enters the stable atlas only
with at least eight occurrences on at least three physical folios.  It is
`STABLE_DIRECTED_RELATION` only if all three held gains are positive; otherwise
label it `LOCAL_OR_UNSTABLE` or `NO_GAIN`.

Primary null: in every held-folio test set, permute next-host identities within
the exact six-variable joint nuisance key while leaving trained models fixed.  This preserves
folio, section, Currier, hand, source-frequency bin, position, line length,
source identities, and the complete held target multiset.  Run 1,024
deterministic worlds.  Report an inclusive p-value for total exact-host gain
and maxT over eligible directed pairs.  This is a conditional held-test
alignment null, not a synthetic manuscript.

## Decisions

- `OPAQUE_HOST_RELATION_GRAPH_TRANSFER_SUPPORTED` requires positive exact-host
  gain in all three outer evaluations, held-folio p<=.05, at least one stable
  maxT-corrected directed relation, and stable/predictive communities.
- `EXACT_HOST_TRANSFER_WITHOUT_STABLE_COMMUNITIES` requires positive exact-host
  gain in all three evaluations and p<=.05 but fails the community gate.
- `OPAQUE_HOST_RELATIONS_LOCAL_ONLY` applies when held-folio gain is positive
  but section or hand transfer is nonpositive.
- `OPAQUE_HOST_RELATIONS_NOT_TRANSFERABLE` applies when held-folio exact-host
  gain is nonpositive.

## Claim ceiling

At most GDT165 can establish a transferable directed dependency between opaque
PAGE_HOST identities and/or a stable anonymous graph partition.  It cannot
establish a word, lexeme, code value, morpheme, POS, language, semantic role,
meaning, plaintext, or translation.
