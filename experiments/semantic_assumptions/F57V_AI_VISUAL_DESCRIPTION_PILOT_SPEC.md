# f57v AI visual-description pilot

Date: 2026-08-11

The user authorizes one narrow exception to the automated-vision exclusion:
direct AI visual inspection of the official Yale f57v canvas for a qualitative
description of visible page geometry.  This does not authorize OCR, CLIP,
embeddings, image similarity, object naming, glyph transcription, historical
source transfer, or semantic inference.

## Frozen source

- Manifest: `https://collections.library.yale.edu/manifests/2002046`
- Canvas: `https://collections.library.yale.edu/manifests/oid/2002046/canvas/1006187`
- Image: `https://collections.library.yale.edu/iiif/2/1006187/full/full/0/default.jpg`
- Expected dimensions: 3028 x 3769 pixels
- Expected image SHA-256:
  `2bf46dbeaaaab4a97075f46f503582da0eef2b352eb92277d7a3b6db1a3a0b8c`

## Permitted observations

Describe visible circles, writing zones, figures, labels, radial placement,
connectors, enclosures, page marks, and color washes.  Rotations and official
IIIF crops may be used to prevent orientation mistakes.  Every observation is
machine-derived and must retain uncertainty.

## Decision rule

Only an explicit drawn leader, bracket, enclosure, or otherwise unambiguous
graphic relation may upgrade a text item from proximity to owned.  Mere
nearness, angular alignment, or a plausible historical interpretation does not
establish ownership.  The pilot cannot assign a word, role value, language,
cipher operation, plaintext, or translation.
