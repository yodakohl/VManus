# GDT350 method — external 28-member binary-presentation specificity

Date: 2026-08-19

Status: `FROZEN_EXTERNAL_PANEL_BEFORE_DIRECT_FACSIMILE_REVIEW`

## Question

KART001 retained one unresolved cultural-specificity question: A-65 has an
ordered 28-night schedule whose odd entries are red and even entries black,
while f69v has 28 radial entries with exact LONG/SHORT alternation. Does exact
two-state alternation recur in an independently transmitted, non-Georgian
28-member medieval system, or is the A-65 presentation presently unique in the
audited comparator frame?

This is an **external-only specificity audit**. It does not rescore f69v, open
Voynich strings, align any slot, or map LONG/SHORT to manuscript colour.

## Frozen panel

`artifacts/gdt350_source_panel.tsv` was selected from official catalogues and
scholarly sources before direct review of the two newly selected Vatican
facsimiles. Core witnesses must be pre-1501, have a source-supported ordered
28-member lunar series, and have enough presentation evidence to classify or
explicitly leave unresolved. One contextual control shows an ordered 30-member
medieval lunar rota, but it never enters the 28-member denominator.

The panel is complete for the six frozen rows. No witness may be removed after
review because its presentation is inconvenient.

## Fixed presentation rubric

Each core witness receives exactly one state:

- `EXACT_BINARY_ALTERNATION_SOURCE_ASSERTED`: a reputable source explicitly
  states that consecutive members alternate between two presentation classes;
- `EXACT_BINARY_ALTERNATION_DIRECT`: direct facsimile review establishes a
  complete ABAB pattern over all 28 members;
- `COMPLETE_NONALTERNATING`: all 28 members are visible/readable enough and no
  strict two-state ABAB presentation spans the complete series;
- `UNRESOLVED_INCOMPLETE_OR_AMBIGUOUS`: count, order, or presentation cannot be
  classified conservatively.

The two classes may be colour, background, length, or another visible layout
state, but the axis must be fixed by the source or be unambiguous over the
complete sequence. Decorative variation with more than two states is not
collapsed post hoc. No textual content is read for meaning.

Direct review may use official full-page images and manual zoom/crops. OCR,
computer vision, embeddings, automatic colour measurement, and batch image
classification are forbidden. New visual judgments are
`AI_DIRECT_VISUAL_OBSERVATION`; catalogue statements remain
`EXTERNAL_HUMAN_SOURCE_ASSERTION`.

## Decision rules

The primary falsifier is deliberately simple:

1. If no independent non-Georgian core witness has exact alternation, retain
   `A65_BINARY_SPECIFICITY_UNRESOLVED`.
2. If at least one independent non-Georgian core witness has source-asserted or
   directly complete exact alternation, report
   `A65_28_BINARY_HAS_NON_GEORGIAN_COUNTEREXAMPLE`.
3. Only a powered, prospectively sampled prevalence panel could estimate how
   common the device is. This audit must not convert one counterexample into a
   population frequency.

The British Library catalogue statement that every other Add MS 25435
miniature has a gold ground was encountered during source selection and is
therefore explicitly source-known, not a blinded discovery. It is nevertheless
an independent non-Georgian counterexample if the catalogue statement and
28-member ownership both survive exact audit.

## Seal and claim ceiling

All `f84*` material is forbidden. The producer and validator operate only on
the experiment-local external-source table. No Voynich source table, image,
surface, family, tuple, PAGE_HOST, or formal payload may be loaded.

GDT350 may establish only whether A-65's exact alternating presentation has an
independent non-Georgian 28-member counterexample in the declared external
panel. It cannot estimate historical prevalence from this small purposive
sample; identify f69v as lunar; establish Georgian provenance, language, or
authorship; align a slot; assign a number, word, sound, meaning, plaintext, or
translation.
