# Source-native structural reading edition v1

## Purpose

Render the complete validated source-native structural interlinear as a compact
human-readable line edition.  This supersedes the practical rendering role of
the archived abstract-line interpreter, whose formal parser is unavailable and
surface-incomplete.  It does not revive that interpreter's substitution
classes or semantic layers.

## Inputs

- `results/source_native_structural_interlinear_v1.tsv`, SHA-256
  `95a15329c61a11c1c4dc671b4df2b3482af9d25a1108eadac2f69b066d3785af`;
- `results/source_native_structural_interlinear_v1.json`, SHA-256
  `28283f57c516520cf7dff329573c9aea7a4cbaa301a77f974b97d2975a703747`;
- `results/source_native_structural_interlinear_v1_validation.json`, SHA-256
  `5cd938717d4465f285ab8b4d860261798ebfae59b32e8e9ec5cc03c308321a87`.

Keep all 23,281 rows and all 3,572 strict shared loci.  Preserve source row
order within a locus and natural numeric folio/page/locus order in the reading
edition.  ZL3b, IT2a, and RF1b remain alternate readings, never replications.

## Rendering

Each locus begins with its locus ID and page/section/Currier/hand/editorial
metadata.  Each group displays:

- factual position `F`, `C`, `L`, or `S`;
- complete consensus STA-family form;
- `fl=` exact-form first/last tendency: `FA`, `LA`, `U`, `I`, or `NA`;
- `ec=` exact-form edge/core tendency: `EA`, `CA`, `U`, `I`, or `NA`;
- nonempty opening/closing feature, favored/disfavored transition, favored
  path, and longest-path fields;
- `eva~=` nearest basic EVA convenience rendering, collapsed to one value only
  when all three readings agree.

An all-three definite space is rendered ` · ` and an all-three drawing
interruption ` ⟂ `.  Every other internal boundary prints its full
edition-specific profile and support.  These marks preserve manual IVTFF
separator evidence; they do not assert European words.

## Claim ceiling

This is a deterministic zero-gloss structural reading aid over already
validated layers.  `F/C/L/S`, `FA/LA`, `EA/CA`, feature and path labels are
structural annotations, not translated words, parts of speech, syntax roles,
sounds, morphemes, lexemes, plaintext, language, cipher, or translation.
`eva~` is explicitly lossy and must never replace the exact member codes in
the companion TSV.
