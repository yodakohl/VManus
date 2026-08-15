# GDT150 — prospective KOR/root-geometry transfer

## Purpose

GDT150 is a one-shot YOLO visual falsifier for the exact semantic seed produced
by GDT149.  It tests only:

> Exact PAGE_HOST `kor` predicts a conspicuous thickened, segmented, or
> bulb-like root architecture on otherwise visually unresolved Herbal pages.

Failure rejects this concrete visual gloss only.  It does not reject `kor` as
a formal PAGE_HOST or the broader HPR2 architecture.  No alternative KOR
meaning may be substituted during this test.

## Frozen target rule

Before any target image is opened, select every f84-free Herbal page that:

1. contains exact PAGE_HOST `kor` in the published GDT149 occurrence table;
2. is not either MHI007 discovery page (`f90r1`, `f3v`); and
3. has no positive feature among the twelve frozen GDT137 page features.

This mechanically yields `f22r` and `f37r`.  Both receive the same binary
prediction: `POSITIVE`.

## Visual rule

Inspect the exact official full-page manuscript image without OCR, automated
vision, embeddings, segmentation, or text reading.  Call:

- `POSITIVE` if the drawn root system visibly contains at least one repeated
  rounded/thickened/tuber-like chamber or a serial telescoping segment clearly
  distinct from thin tapering roots and the central stem;
- `NEGATIVE` if the root system is visible enough to judge and consists only
  of ordinary thin/tapering or unsegmented root strokes;
- `UNCERTAIN` if damage, crop, paint, or geometry prevents the distinction.

The call concerns visible root geometry only, not botanical identity.

## Decision

`KOR_ROOT_GEOMETRY_GLOSS_TRANSFERS` requires both pages `POSITIVE`.
Any `NEGATIVE` gives `KOR_ROOT_GEOMETRY_GLOSS_REJECTED`.  Otherwise the result
is `KOR_ROOT_GEOMETRY_GLOSS_UNRESOLVED`.

The reviewer is the current AI investigator and is necessarily aware that the
pages were selected by KOR.  The result is prospective with respect to the two
image calls, but not blinded to the hypothesis and not human confirmation.

## Seal

f84r is not a target and must not be opened, queried, retained, joined, or
scored.  The frozen inputs are already-published f84-free GDT137/GDT149
artifacts.
