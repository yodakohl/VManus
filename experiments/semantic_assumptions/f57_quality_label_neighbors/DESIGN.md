# F57 quality-position cross-page label-neighbour design

## Status and exposure

This is a **post-hoc descriptive candidate inventory**, not a significance
test. The f57v.8/f77v.3 resemblance and a pilot edit-distance ranking were
already visible before this design was written. No p-value, confirmation, or
English word gloss may be produced from this pass.

## Fixed source rows

Use the four f57v N1 labels at the independently mapped Harley MS 3099 /
Walters W.73 page-role positions:

| Role position | Locus |
|---|---|
| HOT | `f57v.6` |
| MOIST | `f57v.7` |
| COLD | `f57v.8` |
| DRY | `f57v.9` |

The English terms name source-homology positions, not Voynich words.

The candidate universe is every other-page locus classified `kind=L` in the
cached manual interlinear and present in ZL3b, IT2a, and RF1b. Spaces are
retained as a separate diagnostic but removed for character comparison.
Alternate readings are corresponding observations of one manuscript, never
replicates.

## Frozen descriptive measurements

For each target-candidate pair and each corresponding edition calculate:

1. normalized character Levenshtein similarity;
2. character-bigram Jaccard similarity;
3. longest-common-contiguous-substring coverage of the target;
4. normalized Levenshtein similarity of parsed root-component sequences.

For each measurement retain the minimum and arithmetic mean over the three
readings. The primary descriptive order is decreasing minimum surface
similarity, then decreasing mean surface similarity, then locus ID. Report the
top 20 per role and tie-aware ranks for `f77v.3`. Also count edition-specific
and all-reading exact surface matches.

Human annotation fields may describe the returned candidates but cannot turn
proximity into ownership. No visual/OCR/neural evidence enters.

## Decision ceiling

- A high rank can nominate a cross-page form for source acquisition.
- Heterogeneous owners among the four neighbour lists favour a label/register
  explanation over an English-quality reading.
- No result assigns HOT, MOIST, COLD, DRY, person, star, plant, container,
  tube, or outlet as a lexeme.
- A semantic transfer still requires an independently owned readable value
  fixed before its Voynich string.
