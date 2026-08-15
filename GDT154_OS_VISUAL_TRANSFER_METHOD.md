# GDT154 — exact `os` dark-leaf/light-root visual transfer

## Frozen question

GDT089 found two independently annotated pharmaceutical plant-label loci,
`chos` on f100v and `cheosdy` on f88v, which both reduce to HPR2 PAGE_HOST
`os`; both human descriptions mention a dark leaf and light roots. GDT090
showed that broad exact-host visual-bundle stability is not supported, so this
one descriptor conjunction remains only a weak, postselected seed.

Before opening the new target images, GDT154 freezes one exact gloss test:

> exact PAGE_HOST `os` predicts a visible dark-leaf / light-root contrast.

No alternative `os` meaning may be searched if this prediction fails.

## Mechanical target selection

From `gdt062_right_family_inventory.tsv`, retain Herbal rows with:

- exact PAGE_HOST `os`;
- exact display form `chos`;
- wrapper `ch`, no right family, no DY, and no B3;
- page not used by either GDT089 seed;
- page not beginning `f84`.

Five rows remain. To cap hypothesis-aware image review at two pages, sort by
numeric physical folio and retain the first two: f15r.9 and f27r.4 (ahead of
f29r.4, f33r.7, and f90v2.5). The rule matches the f100v `chos` surface while
testing new physical folios. It was selected from formal metadata, not
target-image geometry.

The occurrences are running text rather than singularly owned labels.
Therefore the prediction is deliberately page-level: the visible plant set on
each page is the evaluation unit. That weak ownership is a predeclared
limitation, not something to repair after review.

## Frozen visible rule

Score two components from the official full-page image:

1. `DARK_LEAF`: at least one author-visible leaf surface is conspicuously
   darker in fill/tone than another leaf surface in the same page's plant set;
   outline thickness, scan shadow, holes, stains, and flower/bud color do not
   count.
2. `LIGHT_ROOT`: the root surfaces are predominantly unfilled or visibly
   lighter than the qualifying dark leaf; bare parchment around an outline is
   not by itself a positive unless it is clearly the depicted root interior.

The frozen joint prediction is positive only when both components are
positive. Ambiguity is `UNCERTAIN`, not positive. Test both pages and preserve
counterexamples.

Direct native AI inspection is permitted in this YOLO branch after the public
freeze. It is hypothesis-aware and not independent human confirmation. No OCR,
CLIP, embeddings, object detector, segmentation, automatic captioning, or
batch computer vision is allowed.

## Decision and ceiling

- 2/2 joint positives: retain the exact gloss as a provisional semantic lead.
- 1/2: unstable/local only.
- 0/2, or any page contradicting the required component: reject this exact
  gloss.

Failure rejects only the frozen `os` dark-leaf/light-root gloss, not `os` as a
formal PAGE_HOST. Success cannot establish a word, morpheme, POS, sound,
language, plaintext, plant identity, meaning, or translation. f84r remains
sealed and is not a target.
