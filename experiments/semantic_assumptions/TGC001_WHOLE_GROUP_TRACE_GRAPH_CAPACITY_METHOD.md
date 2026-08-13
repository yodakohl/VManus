# TGC001 — whole-group trace-graph transcription-channel capacity

Status: **SCORE-BLIND CAPACITY METHOD**.

## Question

IGR002 failed to preserve the proposed coarse per-symbol visible signatures and
also exposed a more basic problem: mapping a manual character index to a small
physical unit is often not secure. TGC001 therefore asks a strictly earlier
question. Can complete, source-separated manuscript groups be localized and
represented as unsegmented physical trace graphs densely enough to support a
later held-folio transcription-channel test?

This is not another shape classifier. It does not isolate a manual symbol,
assign a glyph class, choose ZL/IT/RF, or compare an image to a prototype.

## Source-only universe

Use the hash-bound `source_sta_family_consensus_groups.tsv`. Retain a group
exactly when:

1. `strict_zero_alternative == 1`;
2. `grammar_scope == CONFIRMED_PROSE`;
3. `1 <= symbol_count <= 8`; and
4. the three complete ordered strings `zl_sta_codes`, `it_sta_codes`, and
   `rf_sta_codes` are not all identical.

The full ordered member strings are retained for later private scoring but do
not enter image localization or trace annotation. Treat ZL, IT, and RF as
alternate readings of one manuscript, never as independent samples.

Define the exact controlled cell as

```text
(family_surface, currier-or-BLANK, hand-or-BLANK)
```

and the exact ordered triplet as

```text
(zl_sta_codes, it_sta_codes, rf_sta_codes).
```

A candidate is nonduplicate only if every disagreement position has a
`(family,ZL,IT,RF)` quadruple outside all eight IGR001-selected types carried
into IGR002, including the dominant `(B,B1,B1,Ba)` convention. Mixed groups
containing any of those patterns are excluded. A controlled cell qualifies
only if these nonduplicate candidates
cover at least six physical folios. This filter prevents a whole-group crop
from reopening IGR002 merely because it also contains surrounding ink.

Rank qualifying cells by descending physical-folio count, descending group
count, then UTF-8 byte order of the three cell fields. Retain up to the first
12. The current source supplies five; that exact geometry proceeds only to the
target-free calibration below.
Within each retained cell, rank groups by

```text
SHA256("TGC001_GROUP_V1|" + consensus_group_id)
```

and retain the first occurrence on each of the first six distinct physical
folios encountered. The frozen panel therefore contains 30 groups in five
cells. Selection
uses no manuscript image, surface similarity outside the exact cell, visual
feature, or later trace.

## Public commitment and sealed binding

The current panel is a calibration-geometry inventory only and is permanently
ineligible for manuscript image review. It may be published to make the
capacity arithmetic reproducible. If synthetic calibration passes, a new
nonce-keyed private image panel must be selected from the same five cells after
excluding all 30 published geometry rows. Before any target image is opened,
publish only the method, a registration envelope, source-only capacity counts,
and SHA-256 commitments to that new private selection, locator sheet, builder,
validator, and random annotation nonce.
The private locator sheet may expose source coordinates to the localizer, but
not to the trace reviewer.

For every target, the localizer must contemporaneously write a sealed row that
binds:

```text
opaque_target_id
crop_id
canvas_id
full_image_sha256
crop rectangle
crop_sha256
localization state
```

Before delivery to a reviewer, a second sealed manifest must bind a fresh
random `review_id` to the exact delivered crop SHA-256. Reviewers return the
same `review_id`. Both sealed manifests are hash-committed before any review is
accepted. TGC001 may not reconstruct these joins from conversational order or
an embedded list after unblinding.

## Capacity inspection

The localizer sees the source group coordinate and boxes the entire
source-separated group, never an internal symbol. The trace reviewer sees only
a randomly named whole-group crop and the outer group box—no folio, locus,
manual transcription, family shell, cell, selection, previous experiment, or
prototype.

The reviewer records present ink as a small explicit trace graph. Nodes are
stroke endpoints, junctions, crossings with unresolved over/under order, and
points needed to represent a cycle. Edges are continuous visible ink traces.
The reviewer also records isolated ink components, closed cycles, ambiguous
connections, possible pen lifts, retracing, damage, and crop clipping. No node
or edge receives a glyph, letter, sound, or manual-character label. The graph
is serialized in a versioned DSL and independently rendered/reconstructed by
deterministic CPU code; no OCR, image segmentation, CLIP, embedding, automatic
tracing, or image classifier is permitted.

The source audit yields only five nonduplicate controlled cells with six
physical folios each, for a 30-row panel. This is not by itself a proof of
underpower. Before any manuscript image access, a target-free calibration must
test the exact five-cell/six-folio geometry on synthetic trace graphs and
readout bundles. Only if that geometry reliably recovers distributed planted
channels while rejecting null, folio-only, cell-only, closed-type, and graph-
complexity worlds may a fresh nonce-keyed 30-row image panel with the same
five-cell/six-folio geometry, excluding all published rows, proceed as a
feasibility experiment.
The present artifact contains no graph topology and no joined score.

## Later experiment, not authorized by a capacity pass alone

Only after a future capacity pass based on genuinely new data and independent
validation may a separate frozen
experiment fit an explicit latent fragment-and-boundary DSL that jointly
encodes the trace graph and the three edition readouts. Its primary statistic
will be whole-physical-folio held-out description-length gain per trace edge
over the strongest cell-conditioned trace/code-independent baseline. Its null
must permute complete trace graphs against complete three-reading bundles
within exact controlled cells, use 8,191 registered nonidentity maps plus the
identity, and preserve physical-folio panels. Synthetic null, transferable,
family-only, folio-only, edition-policy-only, arbitrary-segmentation, and graph
complexity-confounded worlds must pass before the manuscript score opens.

## Interpretation ceiling

A capacity pass establishes only that a prospectively selected whole-group
physical trace panel is localizable and annotatable. A later model pass could
establish only reusable anonymous trace fragments and edition-readout channels
that transfer to held physical folios. Neither result chooses a preferred
reading or establishes a glyph identity, allograph, sound, alphabet, word,
language, cipher, plaintext, meaning, or translation.
