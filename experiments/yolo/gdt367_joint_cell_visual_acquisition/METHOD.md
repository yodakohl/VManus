# GDT367 co-observed Pharma geometry acquisition

Status: **POSTEXPOSURE YOLO ACQUISITION FROZEN BEFORE NEW VISUAL CALLS**.

## Purpose

GDT363–366 showed that the existing annotation atlas does not contain enough
visual axes on the same exact cells for a joint grounding model. GDT367 adds
new, conservative geometry observations to the complete 27-locus Pharma
CONTACT/GAP panel already localized by GDT002. It does not select loci or
formal features from Voynich text.

The panel is exactly:

- all three frozen f89r2/L4 loci from the first CONTACT/GAP acquisition;
- all 24 loci in the four complete f99v/f100r/f100v replication arrays.

Inherited and newly reviewed CONTACT/GAP calls remain unchanged. The old
capacity gates remain historical failures; one-sided arrays are observations,
not failures, in this exploratory pass.

## Nearest-component rule

Review the existing source-aware context box for each target. Among visible
non-writing contour clusters in that box, select the cluster with the smallest
visible distance to the localized inscription. This is a geometric reference,
not an assertion that the inscription names or owns the cluster. If two
clusters cannot be distinguished, the relevant geometry is clipped, or the
writing/component distinction is insecure, record `UNCERTAIN_COMPONENT` and
set all three new axes to `UNCERTAIN`.

## Frozen axes

Each axis has states `PRESENT`, `ABSENT`, and `UNCERTAIN`.

1. `BROAD_CLOSED_FORM`: the selected component contains at least one visibly
   closed, broad lobe/oval/blade-like outline. This is geometry only; it is not
   called a leaf, fruit, root, or vessel.
2. `FORK_OR_BRANCH`: one continuous selected component visibly divides into at
   least two arms within the context box.
3. `COLORED_FILL`: colored wash or fill is visibly present inside/on the
   selected component, beyond dark outline ink alone.

`ABSENT` is permitted only when the context is sufficient to see the selected
component and the stated feature is visibly absent. Otherwise use
`UNCERTAIN`. Record a short neutral observation note and confidence.

## Evidence and access policy

All new calls are `AI_DIRECT_VISUAL_OBSERVATION`. They are source-aware,
single-observer, postexposure YOLO observations made from the already cached,
hash-bound official images and existing GDT002 localization boxes. No OCR,
object detector, segmentation, embedding, classifier, image similarity, or
automatic captioning is used. Prior image and CONTACT/GAP exposure is disclosed;
this is not blinded validation.

No source-native formal row may be joined or inspected for GDT367 until the
complete 27-row visual observation file is frozen. `UNCERTAIN` is retained as
missing/soft evidence and never coerced. The subsequent capacity audit must
report state mobility by array and folio before any formal search.

## Claim ceiling

At most this acquisition supplies co-observed anonymous visible geometry on
the same localized Pharma cells for exploratory formal association. It cannot
establish object ownership, a plant part, role, word, sound, language,
plaintext, meaning, or translation. No f84 row or image is eligible.
