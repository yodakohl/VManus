# CRP001 correction-recovery panel method

Status: **FROZEN_BEFORE_TARGET_IMAGE_ACCESS**

## Question and complete selection

Can the public human-transcription comments that explicitly combine a
correction claim with darker ink or erasure expose two separately traceable
physical states? This is a source-capacity question, not a decipherment.

Scan `transcription/sources/Stolfi_text25e1-52.evt` in source order. Associate
each contiguous preceding comment block with the next locus row. Select a
locus when its comment block contains both:

- `correction` (case-insensitive); and
- either `darker ink` or `erasure` (case-insensitive).

Exclude only loci already target-inspected in a named published native-visual
experiment. The scan yields four loci. `f81v.19` was already inspected in
PIP001, leaving the complete residual panel `f18r.3`, `f19r.2`, and `f26v.5`.
No filler, formal family, parser root/role, or target pixel enters selection.
ZL3b, IT2a, and RF1b remain alternate descriptions of each physical locus.

## Official source binding

Use Yale IIIF manifest `2002046`, SHA-256
`317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309`.
The selected canvases are fixed by labels 18r, 19r, and 26v. The selection
builder may read manifest metadata but must not fetch or inspect image bodies.

## Per-target outcomes and gates

Allowed outcomes:

1. `RECOVERABLE_TWO_STATE_CORRECTION`
2. `INTERVENTION_VISIBLE_BEFORE_STATE_NOT_RECOVERABLE`
3. `CURRENT_GLYPH_ONLY`
4. `UNRESOLVED_SOURCE_IMAGE`

Outcome 1 requires all five gates:

- the source-commented target is unambiguously localized;
- a materially different ink/edge state exists at the claimed feature;
- an earlier or lower contour is independently traceable;
- a later or upper intervention is independently traceable at the same place;
- overlap, interruption, or an edge/ink boundary supports their physical
  chronology rather than a single continuous stroke or ordinary pooling.

Different density without a separately traceable earlier contour is outcome
2, not outcome 1. A panel capacity pass requires outcome 1 at at least two of
the three targets on at least two physical folios. Otherwise stop this route.

## Access and claim ceiling

After publication of the frozen selection, inspect official source pixels
directly. Cropping and rotation are permitted; enhancement, OCR, CLIP,
embeddings, automated recognition, and batch image features are prohibited.

A panel pass would establish only recurrent recoverable physical intervention
states in these human-flagged loci and could authorize a separately frozen
identity-comparison stage. It would not establish correction intent, character
equivalence, sound, morphology, word, language, cipher, plaintext, meaning, or
translation.
