# GDT137 — Herbal page text-to-visible-feature transfer

Status: `FROZEN_ARCHIVE_WIDE_PAGE_TEST_BEFORE_FORMAL_SCORING`

## Question and novelty

Does the formal inventory of a complete Herbal page predict independently
human-described visible plant features after controlling Currier, hand,
catalogue illustration profile, page size, and paragraph layout?

GDT033 searched individual additional-field hosts on 32 Herbal-B pages.
GDT034/035 tested one selected CKHY gloss. GDT068 and GDT109 tested label-
level annotation panels. No prior experiment applies whole-page HPR2/PAGE_HOST
representations to the complete Herbal A+B page atlas. The human descriptions
and feature rules are already public and exposed, so this is exploratory
hypothesis generation rather than fresh visual confirmation.

## Frozen external panel

Use all 127 f84-free pages in `gdt031_herbal_page_architecture.tsv`: 95 Currier
A and 32 Currier B pages on 63 physical folios. Join only their whitelisted
rows from the existing human page-annotation table. Do not open images or use
tentative plant identifications.

Reuse exactly the 12 primitive `VISIBLE_PLANT_FEATURE` rules published by
GDT033:

- DAISY_CUP, BROAD_CALYX, GRASS, ROOT_PLATFORM, LEAVES_ONE_SIDE,
  FUSED_PARALLEL_LEAVES;
- BULB_OR_TUBER_ROOT, LARGE_OR_EXTENSIVE_ROOT, MULTIPLE_PLANTS,
  BLUE_FLOWERS_OR_BUDS, FINGERED_OR_FRILLED_LEAVES,
  MULTIPLE_STEMS_OR_STALKS.

Exclude GDT033's post-hoc FLOWER_HEAD_ARCHITECTURE union and its three text-
layout outcomes. The primary capacity panel is fixed mechanically at features
with at least eight positive and eight negative pages. A cross-Currier
sensitivity keeps features with at least two positives in each Currier value.

## Frozen formal representations

Reject every `f84*` source row before HPR2 fields are retained. Aggregate all
available source-native groups on each page into exactly four representations:

1. `PAGE_HOST_IDENTITY` — frequency bag of exact PAGE_HOSTs;
2. `PAGE_HOST_CHAR3` — character trigrams inside parsed PAGE_HOSTs;
3. `RAW_CHAR3` — character trigrams inside source display groups;
4. `COMPILER_SIGNATURE` — wrapper, inner-D, O/OT frame, right family, DY and
   B3 tuple counts.

These are structural features, not words or meanings. PAGE_HOST identity is
the primary content-address hypothesis; the other three are mandatory
string/compiler controls.

## Frozen evaluation

Leave out an entire physical folio. A seven-nearest-neighbor nuisance code
uses only Currier, hand, illustration profile, paragraph starts, page line
count, page group count, catalogue prose-line count, and label-presence state.
For each representation, rerank the same eligible training pages using
nuisance plus weighted-Jaccard representation distance and shrink toward the
nuisance prediction by eight effective neighbors.

Score held binary log loss for every frozen feature, the eight-feature primary
capacity panel, and the cross-Currier sensitivity. Report per-feature,
per-folio, leave-one-Currier, and alternate-reading robustness where available.
ZL/IT/RF are readings of one manuscript, not replications.

In 10,000 shared worlds, permute each complete 12-feature vector within
`Currier × hand × illustration_profile`. Recompute the nuisance and model
predictions from permuted training labels. Report local, max-four-model, and
max-feature-by-model inclusive p-values. The null controls the fixed library;
it cannot make the archived human vocabulary fresh.

## Frozen gates and ceiling

A page-content lead requires one PAGE_HOST representation to have positive
four-model-selector-paid gain on the primary capacity panel, beat RAW and
COMPILER controls, be positive on at least six of eight primary features and
at least 35 of 63 held folios, remain positive on the cross-Currier panel, and
have max-four `p<=.05`. Failure localizes no visual content in the tested page
bags; it does not prove that the text is unrelated to the drawing.

Even a pass establishes only page-level association with visible feature
classes. It does not name any PAGE_HOST or assign a semantic role, gloss,
word, morpheme, POS, sound, language, plaintext, meaning, plant identity, or
translation. No new f84 access is authorized.
