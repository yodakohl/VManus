# RCD001 Rosettes dot-addition native-visual method

Status: **FROZEN_TARGET_REGION_UNOPENED**

## Source-only selection

The source is the hash-bound human exact-locus annotation table. Select the
unique unhedged row whose local comment explicitly claims both an **old glyph**
and a **new dot**. The selected locus is `fRos.116` (`f85v2.X7.51`), described
as the radial label below the Southwest rosette at 06:30, reading towards the
rosette. The annotation says that the letter after `@f` is not `@o` but an old
`@e` with a new dot.

This is a worth screen, not a corpus-wide correction claim. The earlier
processed-correction audit inspected four different instances at f16r.2,
f24v.6, and f26r.1 and did not inspect this Rosettes locus.

## Bound image

- Yale canvas: `1006231`
- full image URL:
  `https://collections.library.yale.edu/iiif/2/1006231/full/full/0/default.jpg`
- full image SHA-256:
  `4b08afeee514691b0a511099ca299aed544d6fd1782b7dee8df163dfc06354ed`
- dimensions: 7925 × 7268

The full foldout was previously opened for a different geometric question,
but the targeted `fRos.116` glyph region has not been inspected for this
question. Freeze this method and validate the source-only selection before
opening a source-native IIIF region containing the locus.

## Allowed visual outcomes

1. `TWO_STATE_BASE_PLUS_LATER_DOT_VISIBLE`
2. `CURRENT_COMPLEX_GLYPH_ONLY`
3. `UNRESOLVED_SOURCE_IMAGE`

The first outcome requires all of the following on the official source image:

- the selected label and target glyph are locally identifiable from the
  registered Southwest-rosette position;
- an independently continuous base form remains visible without treating the
  alleged dot as part of that base;
- the dot is a bounded authorial ink mark rather than wash, stain, bleedthrough,
  compression, or a neighboring stroke;
- physical appearance supports a later intervention (for example a distinct
  overlap, ink boundary, or clearly superposed mark), not merely two components
  of one current glyph;
- the base can be described as e-like and the completed form as o-like only at
  the source-transcription glyph level; no sound or plaintext value is assigned.

If the current source shows only one complex glyph, choose outcome 2. If the
target cannot be located or the temporal/physical distinction is not visible,
choose outcome 3.

## Access and ceiling

Use direct native inspection of the official canvas and source-native IIIF
regions only. Rotation is permitted for legibility; no enhancement, OCR, CLIP,
embedding, automated recognition, or batch image processing is permitted.

A positive result would establish only a visible physical dot addition at one
glyph: an e-like base was modified into an o-like current form in source
transcription terminology. It would not establish whether the change is a
correction, abbreviation, scribal completion, phonetic contrast, character
equivalence, word, language, cipher, plaintext, meaning, or translation.
