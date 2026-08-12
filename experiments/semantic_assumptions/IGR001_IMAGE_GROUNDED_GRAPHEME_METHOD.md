# IGR001 — image-grounded recurrent disagreement panel

Status before image access: **FROZEN_SELECTION; TARGET IMAGES UNOPENED**.

## Question

LTG001 shows that the three manual readings are not improved by a small global
latent suffix channel at current STA resolution. IGR001 therefore asks the
more physical prerequisite: when recurrent manual-code disagreement patterns
are inspected directly in the official manuscript image, do they correspond
to a reproducible visible shape class, or do the same code triplets collapse
different physical geometries?

This is not OCR and not a glyph classifier. Selection uses source coordinates
and code counts only. Image inspection is a bounded native-vision judgment
recorded under a small neutral rubric.

## Frozen selection

From strict zero-alternative aligned positions, rank exact ordered
`(family,ZL,IT,RF)` disagreement triplets by descending frequency then UTF-8
tuple order. Retain the first eight triplet types, each already represented on
at least 35 physical folios. For each type, rank occurrences by

```text
SHA256("IGR001_PANEL_V1|" + family + "|" + ZL + "|" + IT + "|" + RF
       + "|" + locus + "|" + symbol_index_1based)
```

and retain the first occurrence on each of three distinct physical folios.
This yields 24 target positions across at least 16 folios. The selection is
fixed before any target image is opened. The dominant `(B1,B1,Ba)` pattern is
one of eight reference types, not the experiment by itself.

## Inspection rubric

For each target, inspect only a bounded region around its source locus on the
official Yale canvas. The target position must first be localized within the
manual-transcription group. Record one state:

* `ONE_CLEAR_VISIBLE_UNIT` — one bounded ink unit can be identified;
* `LIGATED_OR_COMPOSITE_UNIT` — the position is visibly fused with a neighbor;
* `DAMAGED_RETRACED_OR_AMBIGUOUS` — physical state prevents a stable unit call;
* `LOCALIZATION_UNRESOLVED` — the source position cannot be located securely.

For resolved units, assign a neutral shape signature using only these visible
properties: number of main vertical stems (0/1/2+), closed loop (none/one/2+),
left extension, right extension, descender, and separated dot. No Voynich/EVA/
STA name is used in the shape signature.

## Capacity and interpretation

Proceed to a later image-grounded grapheme atlas only if at least six of eight
triplet types have all three targets localized, at least five types have two of
three matching neutral shape signatures, and at least four non-dominant types
meet both conditions. Otherwise stop at visible-light localization capacity.

A pass may establish only stable visible shape classes behind recurrent manual
reading disagreements. It cannot decide the correct transcription, name an
authorial grapheme, establish allography, sound, alphabet, word, language,
cipher, plaintext, meaning, or translation.
