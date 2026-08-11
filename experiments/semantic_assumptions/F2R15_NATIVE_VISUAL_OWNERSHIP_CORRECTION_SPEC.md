# f2r.15 native-visual ownership correction

Date: 2026-08-11

## Purpose

Reinspect the sole Voynich-script colour-note candidate after source-bound
native visual inspection became permitted. The existing acquisition packet
classifies `f2r.15` as `DIRECT_ENCLOSURE_UNDER_PAINT`, based on a human local
comment saying `Within leaf.` This check asks only whether the official
ordinary-light image supports that exact physical relation.

The manual ZL3b/RF1b reading `ios an on` is retained as source transcription;
the image is not used to reread glyphs.

## Fixed sources

- Human exact-locus annotations:
  `results/existing_human_exact_locus_annotations.tsv`, SHA-256
  `79c7f06e91f90054aff4cdf27f098a5977d820acdf91f239a14c6ddf553a7f61`.
- Translation-anchor packet:
  `results/translation_anchor_human_review_panel_v1.tsv`, SHA-256
  `20134182f439a742a3de825858aae4f879faab8f5f17f28a676f48b318a7d563`.
- Official Yale manifest:
  `https://collections.library.yale.edu/manifests/2002046`.
- Official Yale f2r image:
  `https://collections.library.yale.edu/iiif/2/1006078/full/full/0/default.jpg`,
  2691 x 3770 pixels, SHA-256
  `826533a0760798acf5a4caa01ac29fe95eb1ed13a9fb26ac82900a8aea11d53f`.
- Source-native IIIF detail region:
  `https://collections.library.yale.edu/iiif/2/1006078/1750,900,900,900/1800,/0/default.jpg`,
  1800 x 1800 pixels, SHA-256
  `636335ce1c65c614a78578bbbcf571fcd78f2403d9624dacdd86d6b4c342914c`.

The detail region is a deterministic rendering of the same official canvas;
it adds no independent witness.

## Fixed questions

1. Is the complete physical record wholly enclosed by the painted leaf?
2. Does any part of the record overlap the pale green leaf-tip area?
3. Does the record cross from the leaf-tip area onto bare parchment?
4. Can ordinary-light pixels establish ink-before-paint rather than
   ink-after-paint or transparent overlap?
5. Does the image supply a second independently readable colour value or a
   repeated Voynich-script colour record?

## Decision rule

Retain `DIRECT_ENCLOSURE_UNDER_PAINT` only if the complete record is visibly
inside the leaf and ordinary-light evidence establishes the layer order.
Otherwise replace it with the strongest relation directly visible in the
source image. A boundary overlap may support a local leaf association, but
it is not an enclosed under-paint instruction.

## Exclusions and claim ceiling

No OCR, automated transcription, enhancement-derived reading, CLIP,
embedding, image-similarity score, automated segmentation, glyph classifier,
plant identification, decoder claim, or English gloss is used. The visual
observations are machine-authored native inspection, not literal human
annotation.

The strongest permitted positive result is a physical relation grade. It
cannot assign GREEN, pigment, action, a word, sound, language, cipher,
plaintext, meaning, or translation.
