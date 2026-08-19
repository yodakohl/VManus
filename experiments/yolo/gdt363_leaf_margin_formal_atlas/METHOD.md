# GDT363 leaf-margin / source-family atlas method

Status: **EXPLORATORY PANEL FROZEN BEFORE GDT363 FORMAL AGGREGATION**.

## Why this is new

LM001/LM001X/LM001Y acquired a complete source-selected Herbal visual panel.
The resulting 44 folios contain 29 SMOOTH, 13 TOOTHED, and 2 UNCERTAIN leaf
margin calls. LM002 authorized a narrow target but stopped at a synthetic
calibration gate without opening the real formal table. That historical stop
is preserved. GDT363 asks a different YOLO discovery question: what anonymous
source-native formal distributions, if any, covary with the already frozen
visual axis?

No new image or catalogue is opened. The two UNCERTAIN pages remain in the
inventory but are missing from the binary score. Calibration pages used to
develop the visual rubric are excluded, exactly as in the final 44-folio
capacity panel.

## Frozen formal representation

Use source-native all-reading family-consensus groups only. Do not use EVA,
surface strings, member identities, roots, PAGE_HOST substrings, joint-tuple
identities, or meanings. For each page, aggregate state-blind rates/counts of:

- family-component presence within a source group;
- within-group family bigrams and trigrams (never across a source separator);
- first-group prefix and last-group suffix classes of length 1-3;
- source-group count, family-symbol count, and synchronized boundary classes;
- line/label kind and line-entry/exit structure as nuisance/descriptive
  construction features.

A candidate must occur on at least five panel pages and be absent on at least
five before the visual labels are consulted. Exact family expressions and raw
glyph/member strings are excluded. Every retained feature definition is logged.

## Exploratory ranking

For each page-rate feature, compare a fixed ridge-logistic model against the
same nuisance-only model under leave-one-physical-folio-out prediction. Nuisance
includes Currier/hand jointly, folio-rank quartile, quire, page side, line count,
and source-group count. Standardization and coefficients are learned in each
training fold. Report held codelength gain, AUC, per-Currier direction, and
leave-one-quire/leave-one-Currier sensitivities.

Use 4,096 deterministic visual-state permutations within Currier × quartile
cells. Report inclusive local and complete-library maxT tails. This is an
exploratory control, not an exact opportunity-matched semantic test: quire,
page side, and text volume are modelled, not all exactly permuted. Log every
retained feature and do not replace the top feature after inspection.

Labels:

- `INTERESTING_EXPLORATORY`: positive held gain, same direction in both
  Currier strata, at least eight feature-present pages, and maxT <= .20;
- `LIKELY_REGISTER_OR_LAYOUT_CONFOUND`: positive nominal signal without
  cross-Currier direction stability or with leave-one-quire sign failure;
- `WEAK`: positive held gain but no adjusted support;
- `NO_SIGNAL`: nonpositive held gain.

These ranks prioritize hypotheses. They are not automatic kill gates and do
not assign a leaf word.

## Seal and claim ceiling

All f84 rows are rejected before formal parsing. GDT363 may identify only an
exploratory association between a page-level visible leaf-margin class and an
anonymous source-family distribution. It cannot identify a plant, leaf,
lexeme, morpheme, POS, sound, language, plaintext, meaning, or translation.
