# RBR001 f67r2 red-over-brown retracing method

Status: **FROZEN_THREE_TARGET_REGIONS_UNOPENED**

## Worth and source-only selection

The f67r2 outer ring is explicitly described as red, and the human source
contains several local comments comparing red retracing with brown under-ink.
This is worth a bounded panel inspection because ink colour supplies a visible
layer discriminator. Earlier f67r2 work analyzed diagram structure, lunar
colour assignments, and formal sequences, but did not inspect these outer-ring
glyphs for recoverable red-over-brown shape states.

Within `f67r2.T1`, select a locus if its immediately preceding comment block
satisfies either frozen textual rule:

1. it contains `red retracing` and either `became` or `made the left side`; or
2. it contains both `looks like @a in red` and `visible in brown`.

This selects exactly:

- `f67r2.3` at 11:30: circles, s-plume start, and y-tail geometry said to be
  altered by red retracing;
- `f67r2.7` at 03:30: a y-side said to be made angular and a final glyph made
  question-mark-like by retracing;
- `f67r2.10` at 06:30: a red a-like ending over a faint brown y-plume.

Exclude `f67r2.6` (“unrecognizable; must have been d”) and `f67r2.11`
(“unreadable”): neither comment claims a directly visible recoverable
before-state. Alternate ZL/IT/RF readings are localization witnesses, never
replications or adjudicators of the visual state.

## Bound image

- Yale canvas: `1006194` (f67r1 and f67r2)
- URL: `https://collections.library.yale.edu/iiif/2/1006194/full/full/0/default.jpg`
- SHA-256: `0518312a566ee713a46c9887d8b8b9d7141d14095e360661789c1dad9b5c0d1c`
- dimensions: 4972 × 3738

Freeze and validate this method before opening any source-native target region.

## Per-locus outcomes and gates

Allowed outcomes:

1. `RECOVERABLE_RED_OVER_BROWN_SHAPE_CHANGE`
2. `VISIBLE_LAYERING_NO_RECOVERABLE_SHAPE_PAIR`
3. `UNRESOLVED_SOURCE_IMAGE`

Outcome 1 requires all five gates:

- the registered T1 sector, locus, and described target glyph are securely
  localized;
- red and brown manuscript ink are visually separable at the target;
- a bounded brown under-stroke geometry is independently traceable;
- a bounded red retracing geometry visibly diverges from that brown geometry;
- overlap, continuity, or ink boundary supports the red stroke lying over or
  after the brown stroke rather than being an adjacent glyph, drawing line,
  stain, bleedthrough, wash, or compression artifact.

## Panel decision

`PASS_MULTIPLE_RECOVERABLE_RED_OVER_BROWN_SHAPE_STATES` requires at least two of
the three loci to satisfy all five per-locus gates. One positive is a fragile
lead only. Zero positives or unresolved localization stops the panel.

Use direct native inspection of official pixels and source-native IIIF
regions/rotation only. No enhancement, OCR, CLIP, embedding, automated image
recognition, or batch feature extraction is permitted.

A panel pass establishes only that multiple glyph shapes in this red ring
retain visually recoverable brown under-writing and divergent red retracing.
It does not establish correction intent, correct transcription, character
identity or equivalence, sound, morphology, word, language, cipher, plaintext,
meaning, or translation.
