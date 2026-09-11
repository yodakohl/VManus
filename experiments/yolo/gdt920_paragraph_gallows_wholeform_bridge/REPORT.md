# GDT920 — paragraph whole-form bridge

**Result: BRIDGE_NOT_ESTABLISHED.** Both fixed maps have negative own-paragraph residuals in all three readings. Adequate comparison capacity exists; matching examples do not support a general p/f-to-k/t paragraph bridge. No lexical identity or word meaning is established.

Registered publicly in c9dcd82b before execution of this contrast. All six source caches were already exposed to the project: this is not independent confirmation. See METHOD.md for the fixed scoring rule.

| Reading | Map | Anchor types | Exchangeable leaves | Movable leaves | Own matching tokens | Own rate T | Conditional expectation | Residual |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| ZL3b | A | 634 | 87 | 46 | 53 | 0.00103488 | 0.00132581 | -0.00029094 |
| ZL3b | B | 634 | 87 | 46 | 32 | 0.00131431 | 0.00149735 | -0.00018304 |
| IT2a | A | 719 | 87 | 53 | 59 | 0.00100065 | 0.00135271 | -0.00035206 |
| IT2a | B | 719 | 87 | 56 | 51 | 0.00137511 | 0.00147806 | -0.00010295 |
| RF1b | A | 646 | 87 | 46 | 53 | 0.00132325 | 0.00151244 | -0.00018918 |
| RF1b | B | 646 | 87 | 48 | 36 | 0.00140105 | 0.00171546 | -0.00031441 |

A preserves the complete word except p→k or f→t; B uses p→t or f→k. Each header word is one prediction per paragraph, including all zeroes. Rates normalize each compared body by its eligible token count; leaves have equal weight. Counts are dependent anchor-body matches, not independent trials.

The primary ZL maximum residual is -0.00018304; 883/1024 jointly permuted two-map maxima are at least as large (tie-inclusive rank fraction 0.86243902). This controls the two registered mappings, not the project search. No significance claim is made.

659 complete all-P ZL frames survive the frame rule. IT aligns 658 with one zero-body-opportunity exclusion; RF aligns 659. There are 2,112 ZL, 2,466 IT and 2,068 RF prediction rows across both maps, including nonexchangeable rows explicitly labelled. The ZL score contains 1,052 anchor/paragraph cases per map, over 634 distinct forms; 87 physical leaves supply exchanges. Different readings of this manuscript are not replications.

## Complete auditable output

- artifacts/PREDICTIONS.tsv: every candidate/paragraph/map, zeroes, observed counts, expected rate and witness loci.
- artifacts/CENSUS_*.json: all original anchor occurrences, every body word and every alternative paragraph opportunity, matrices and exclusions.
- artifacts/FRAME_BOUNDARIES.json: all retained source frames and frame exclusions.
- artifacts/WORLDS.json: all 1,024 conditional comparisons.
- artifacts/VALIDATION.json: independent reconstruction status.

## Decision and limitations

Close this fixed own-paragraph bridge. Do not merge p/f and k/t, relabel them as uppercase/lowercase, change the maps, shorten words, or select only a successful pair. The result does not show that allography is impossible: lexical repetition is not compulsory and this test concerns a specific proposed association. Even a positive association would leave distinct topical words as a rival. There are zero fresh confirmation leaves and zero independently established meanings. No image or new page was opened; f84/f84r remain sealed.

Independent validation PASS: complete six-cache reconstruction, all frames/predictions/matrices and all1,024 worlds agree within1e-13; seven synthetic checks pass. Validator SHA256: `79539c72b22b07d81cde74b7b90be30924b60e96acea03f5674eced3ed12bea5`. The machine field `anchor_paragraphs` counts anchor–paragraph pairs, not distinct paragraphs.
