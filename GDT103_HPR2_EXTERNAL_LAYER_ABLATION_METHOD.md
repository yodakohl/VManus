# GDT103 — HPR2 external-layer ablation

## Question

On the existing GDT068 whole-folio-held external panel, where does archived
object/relation signal concentrate when HPR2 compiler layers are added back to
PAGE_HOST one at a time?

This is hypothesis generation over already exposed annotations, never
confirmation. No semantic role or English gloss is assigned.

## Frozen panel

Reconstruct GDT068 exactly: 332 non-f84r annotated loci whose PAGE_HOSTs each
occur on at least two physical folios, eight archived object/relation axes,
K=5, shrinkage=4, and full physical-folio exclusion. Candidate pools first
match section and Currier, then relax section if capacity requires it.

f84r is rejected before analysis and is not opened, retained, queried, joined,
scored, or targeted.

## Representations

- raw source-group character trigrams;
- PAGE_HOST character trigrams;
- PAGE_HOST plus WRAPPER;
- PAGE_HOST plus O/OT local frame;
- PAGE_HOST plus RIGHT_FAMILY;
- PAGE_HOST plus DY;
- PAGE_HOST plus B3;
- PAGE_HOST plus all five compiler layers;
- compiler signature only.

Primary compiler additions use `ACTIVE_ONLY` encoding: default NONE/0 states
add no token. This prevents a ubiquitous zero token from changing weighted
Jaccard geometry without adding information.

The tried `CATEGORICAL_LEVEL` sensitivity includes NONE/0 tokens and is logged
in full. It was inspected during development and is not hidden; specifically,
it can make B3 look helpful merely by adding the common `B3=0` token.

## Scores

For each axis and representation, report held codelength gain versus the same
nuisance KNN baseline and incremental gain versus PAGE_HOST. Summed gains over
the eight correlated axes are descriptive. Selecting the best of PAGE_HOST
plus five single-layer additions pays `log2(6)` bits. This is not a calibrated
confirmation threshold because the axes and model family are archived and
postselected.

## Claim ceiling

Only localization of archived external-association signal among formal HPR2
layers. No word, morpheme, POS, sound, language, plaintext, semantic role,
gloss, meaning, or translation.
