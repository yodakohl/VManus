# F77r same-orientation source-capacity audit

## Result

**Stop: zero second human-annotated same-orientation apparatus.**

The complete local exact-locus annotation atlas contains eleven broad
apparatus/water-associated units with at least five human-described labels.
The source-only audit opened no Voynich surfaces, roots, grammar features,
pixels, OCR, or automated-vision output.

The already exposed `f77r/V1` unit reconstructs as the sole pass: six labels,
every one described between successive tube openings, five contiguous side
branches, and a separate human page description reporting that four of the
openings eject material. Excluding that target leaves **0 of 10** broad units
with the same information orientation.

| Page/unit | Loci | Comments saying “between” | Internal boundaries | Reported emitters | Result |
|---|---:|---:|---:|---:|---|
| f75r/N1 | 7 | 0 | — | — | fail |
| f75v/N1 | 20 | 0 | — | — | fail |
| f77r/V1 | 6 | 6 | 5 | 4 | exposed control pass |
| f77v/N1 | 5 | 0 | — | — | fail |
| f78r/X1 | 6 | 0 | — | — | fail |
| f80r/N1 | 10 | 5 | — | — | fail |
| f82r/N1 | 10 | 1 | — | — | fail |
| f82v/X2 | 5 | 1 | — | — | fail |
| f84r/N1 | 9 | 0 | — | — | fail |
| f84v/N1 | 10 | 0 | — | — | fail |
| f85v2/X1 | 9 | 7 | — | — | fail |

The near-misses are still useful. The existing human descriptions classify
them as labels in/near an island, nymph rows, scattered illustrations, ponds,
curved channels, or rosette roads/connections. None supplies a complete
one-label-per-successive-segment array and an independent mixed active/inactive
boundary contrast. In particular, “between figures” or “between channels” is
not treated as ownership or as equivalent to “between successive apparatus
boundaries.”

The legacy exact-locus page ID `f85v2` has no literal page-atlas row because
its current loci belong to the compound `fRos` foldout. The first run stopped
before output on that mismatch. The correction keeps the unit in the broad
table with page-level output evidence unavailable; it neither invents an alias
nor drops the near-match.

## Bounded public-source review

A targeted live review found no missing independent annotation layer:

- the [voynich.nu Q13 catalogue](https://www.voynich.nu/q13/index.html) is the
  page-description source already imported into the atlas;
- [Stolfi's collected labels](https://www.ic.unicamp.br/~stolfi/EXPORT/projects/voynich/00-EXPORT/98-02-01-lotsa-labels/labels-t.html)
  is the legacy label layer already represented locally;
- the [VIB f82v record](https://vib.tamagothi.de/index.php?id=f82v&show=page)
  repeats the Grove/Stolfi units and supplies no mixed-output segment panel;
- a [discussion of what counts as a Q13 label](https://www.voynich.ninja/thread-3376.html)
  underscores that label status itself is disputed but supplies no exact
  successive-segment panel;
- one search hit asserted active/non-active anatomical ducts as part of its own
  decipherment. It was excluded because an interpretation-dependent gloss is
  not independent author-visible annotation.

This is a bounded lead audit, not a claim that no relevant description can
ever exist on the internet.

## Validation and ceiling

A standalone implementation imports no audit code and reconstructs all four
input hashes, the annotation-only schema, eleven broad candidates, every gate
component, the `6/5/4` f77r positive control, the foldout caveat, five source
leads, and zero second passes in 21 checks.

The current public annotation layer cannot confirm the f77r bridge. Retain the
bridge only as a provisional post-hoc structural lead. Reopen this exact route
only if a new provenance-clean human source explicitly provides successive
apparatus segments and both active and inactive boundaries. Generic proximity,
circles, pools, figures, paths, tubes, or speculative decipherments cannot
substitute and establish no quality, element, word, plaintext, language, or
translation.

## Reproduction

```text
./vpy experiments/semantic_assumptions/f77r_same_orientation_capacity/audit_f77r_same_orientation_capacity.py --output experiments/semantic_assumptions/results/f77r_same_orientation_capacity.json
./vpy experiments/semantic_assumptions/f77r_same_orientation_capacity/validate_f77r_same_orientation_capacity.py --output experiments/semantic_assumptions/results/f77r_same_orientation_capacity_validation.json
```
