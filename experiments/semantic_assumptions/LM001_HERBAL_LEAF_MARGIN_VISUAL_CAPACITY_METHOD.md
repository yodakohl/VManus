# LM001 herbal leaf-margin visual capacity method

## Purpose

Build a prospective, text-blind source-bound visual panel for one coarse
author-visible botanical trait on whole herbal pages: visibly toothed versus
smooth leaf margins.  This is an annotation/capacity experiment only.  It does
not open, score, or select any Voynich string, formal root, role, or grammar
feature.

This is distinct from the completed BERRY001 and FLOWER001 experiments:
LM001 concerns leaf-edge morphology, not reproductive structures, and the
first pass asks only whether a balanced visual panel exists.

## Deterministic source panel

Inputs are the public Voynich.nu page-annotation TSV, ZL3b page metadata, and
the official Yale IIIF manifest `2002046`.

1. Retain pages tagged `SOURCE_HERBAL_PAGE` that have ZL3b metadata and a
   numeric physical folio.
2. Keep one page per physical folio: the page with the lowest SHA-256 of
   `LM001_PAGE|<page>`.
3. Separately within Currier A and B, sort eligible folios by numeric folio and
   divide ranks into four cells with `quartile = floor(4*i/n)+1`.
4. In each Currier-by-quartile cell, select the four pages with the lowest
   SHA-256 of `LM001_PAGE|<page>`.
5. Within every four-page cell, sort by SHA-256 of `LM001_PHASE|<page>`; the
   first two pages are calibration and the last two held.
6. Opaque page ID is `LM` plus the first eight uppercase hex characters of
   SHA-256 `LM001_OPAQUE|<page>`.

This yields exactly 32 pages on 32 physical folios: 16 Currier A, 16 Currier
B, 16 calibration, and 16 held, with two calibration and two held pages in
each of the eight Currier-by-quartile cells.

## Frozen visual rubric

Inspect only the exact official Yale canvas for each selected page.  Do not
read, transcribe, OCR, or interpret any Voynich writing.

- `TOOTHED`: at least two clearly resolved leaves show repeated, deliberate
  projections from the leaf margin, or one exceptionally clear large leaf
  shows at least four such projections on a margin.
- `SMOOTH`: at least two clearly resolved leaves have uninterrupted margins
  and no leaf on the plant meets the `TOOTHED` definition.
- `UNCERTAIN`: neither criterion is met, image damage/paint prevents a secure
  judgment, or the drawing mixes qualifying toothed and qualifying smooth
  leaf systems.

Large lobes, separate leaflets, stem branches, teeth on roots or fruits,
hairs, paint bleed, parchment damage, and decorative dots do not count as
leaf-margin teeth.

Calibration pages are inspected first.  Any rubric correction must be
published before a held image is opened; otherwise the rubric above remains
fixed.  Held pages receive one judgment only.

## Capacity gates

The route may proceed to a separate text-blind design only if the held panel
has all of:

1. at least six `TOOTHED` and six `SMOOTH` pages;
2. both states on at least three held Currier-A and three held Currier-B pages;
3. both states in at least three of the four folio-rank quartiles;
4. no more than four `UNCERTAIN` pages;
5. no single quire contributes more than 25% of either admitted state.

Failure stops before every Voynich text feature.  A pass licenses only a
separate preregistration controlling Currier, folio-rank quartile, quire, hand,
text length, and flower/fruit tags already used by prior experiments.

## Claim ceiling

At most, LM001 can establish a reproducible source-bound visual classification
and capacity for a future formal association test.  It cannot identify a
plant, establish that the prose describes leaf margins, assign a word or
morpheme, name a language or cipher, supply plaintext, or translate the
manuscript.
