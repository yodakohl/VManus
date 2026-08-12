# RBR002 f67r2 complete outer-ring underlayer capacity method

Status: **FROZEN_NINE_NEW_SECTORS_UNOPENED_THREE_SECTORS_EXPOSED**

## Scope and exposure

Audit every one of the twelve `f67r2.T1` outer-ring records in fixed clock
order: 08:30 (`.12`), then 09:30 (`.1`) through 07:30 (`.11`). No record or
glyph may be selected by appearance. The official full canvas and the target
regions at 11:30 (`.3`), 03:30 (`.7`), and 06:30 (`.10`) were already exposed
during RBR001; the remaining nine sector regions were not inspected for
underlayer recovery. This is therefore an exposure-aware capacity audit, not a
held confirmation.

## Bound image

- Yale canvas: `1006194` (f67r1 and f67r2)
- URL: `https://collections.library.yale.edu/iiif/2/1006194/full/full/0/default.jpg`
- SHA-256: `0518312a566ee713a46c9887d8b8b9d7141d14095e360661789c1dad9b5c0d1c`
- dimensions: 4972 × 3738

Freeze and validate the complete twelve-sector inventory before inspecting the
nine unexamined sector regions.

## Per-record states

Classify each whole outer-ring record into exactly one source-only state:

1. `MULTIPLE_UNDERSTROKE_SHAPES_RECOVERABLE`: at least two different glyph
   positions retain bounded brown geometry that diverges from or extends
   beyond their red retracing;
2. `ONE_UNDERSTROKE_SHAPE_RECOVERABLE`: exactly one glyph position does;
3. `LAYERING_VISIBLE_SHAPES_NOT_RECOVERABLE`: red-over-brown layering is visible
   but no divergent brown glyph geometry can be traced independently;
4. `NO_VISIBLE_UNDERLAYER_OR_UNRESOLVED`: no defensible underlayer recovery.

A recoverable position requires visibly separable red and brown ink, a bounded
brown geometry attached to the same glyph position, a divergent bounded red
geometry, and overlap/continuity supporting red-after-brown chronology. Do not
name either geometry with EVA or another character identity.

## Capacity decision

`GO_PROSPECTIVE_CORRECTED_RING_TRANSCRIPTION_METHOD` requires:

- at least 8 of 12 records with one or more recoverable positions;
- at least 4 of the nine previously unexamined records with one or more
  recoverable positions;
- at least 3 records with multiple recoverable positions;
- no single exposed record needed to satisfy any threshold.

Otherwise stop RGB underlayer recovery as insufficiently complete. A GO would
authorize a new method that freezes position-by-position brown-geometry
transcription rules before assigning source-glyph classes. It would not itself
produce or validate corrected text.

Use direct native inspection of official pixels and source-native IIIF
regions/rotation only. No enhancement, OCR, CLIP, embedding, automated image
recognition, or batch feature extraction is permitted. Alternate readings may
localize whole records but may not define, name, or validate under-strokes.

No outcome establishes correction intent, correct transcription, character
identity or equivalence, sound, morphology, word, language, cipher, plaintext,
meaning, or translation.
