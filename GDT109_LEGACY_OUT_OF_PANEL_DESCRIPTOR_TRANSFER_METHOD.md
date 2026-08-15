# GDT109 — legacy out-of-panel descriptor transfer

## Question

Does the HPR2 representation ranking learned on the 83-locus GDT095
pharmaceutical-label panel transfer to human annotations that were not present
in `gdt012_annotated_core_inventory.tsv`?

This is an exploratory archive-stratum transfer, not fresh visual validation.
The target descriptions and transcriptions have long been present in the
repository and may have influenced earlier work indirectly.

## Frozen target census

Take every current-locus crosswalk row satisfying all of:

- `primary_eligible = 1`;
- the source annotation has object class `P` and certainty `UNHEDGED`;
- the current locus is absent from the complete GDT012 annotated-core census;
- the locus is not on f84r.

No row is selected by its Voynich form or by an attractive description word.
The resulting target is expected to contain 44 loci on six physical folios.

## External endpoints

Reuse all 19 normalized descriptor tokens frozen by GDT095. The primary panel
scores all 19, including tokens absent from this target stratum. A disclosed
capacity sensitivity also scores tokens occurring on at least three positive
and three negative target loci. No token is chosen by its formal result.

## Formal uncertainty

ZL3b, IT2a, and RF1b are alternate observations of one manuscript. They are
never counted as independent examples. Primary target features average the
three edition-specific feature counters. ZL3b-only, IT2a-only, and RF1b-only
scores are retained as transcription sensitivities.

The target labels are outside the strict GDT016 prose inventory. HPR2 parsing
therefore uses the already frozen GDT012 layer stripping and GDT062 PAGE_HOST
parser on each edition's source-aligned nearest-basic display form. This is a
parser-extension sensitivity, not a claim that uncertain display forms are
source-native letters. STA-family character features are scored separately.

## Representations

The complete tried set is:

1. `RAW_CHAR3`
2. `RESIDUAL_HOST_CHAR3`
3. `PAGE_HOST_CHAR3`
4. `EDGE_STRIPPED_CHAR3`
5. `EDGE_ONLY`
6. `COMPILER_ACTIVE`
7. `PAGE_HOST_PLUS_COMPILER_ACTIVE`
8. `STA_FAMILY_CHAR3`

The main HPR2 prediction is that PAGE_HOST should outperform raw forms,
edge-stripped hosts, and compiler-only state. The recently discovered final
edge coupling predicts that full PAGE_HOST may outperform edge-stripped host.

## Prediction and controls

For every target locus, train only on GDT095 units from other physical folios.
Use the inherited five-neighbour weighted Jaccard model with shrinkage 4 and
the corrected positive-overlap rule: when a representation shares no feature
with any training unit, back off to the held-folio training prevalence.

Report held codelength, gain over prevalence, per-folio contributions, and a
three-bit selector charge over the eight representations. The null permutes
complete 19-token annotation vectors within target physical folio, preserving
folio ecology and descriptor co-occurrence, and records a max-over-eight
inclusive probability.

This experiment may rank a dirty lead; it cannot confirm a meaning. No semantic
role, gloss, word, morpheme, POS, sound, language, plaintext, or translation is
assigned.

## Holdout guard

f84r is excluded before any formal row is retained, parsed, joined, scored, or
targeted. The sealed f84r payload is not opened.
