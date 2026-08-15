# GDT132 — cross-register continuation-arity transfer

Status: **Q20_CONTINUATION_ARITY_DOES_NOT_TRANSFER_OUTSIDE_SECTION_S**

The corrected post-freeze mechanical panel contains 31 paragraph-start -> immediate-next-line pairs on 24 physical folios outside section S and every Q20 training folio.

## Source-seal correction

The original prediction was public before target enumeration, but its declared whole-manuscript separator input contained sealed f84r rows. A first local 32-pair run parsed that table before filtering; the scorer displayed no f84 row. A later read-only audit subagent displayed limited rows while diagnosing the breach; no row entered target selection, features, fitting, permutation, or score. Before publication, `gdt132_source_seal_correction.json` replaced it with the pre-existing f84-free `gdt046_line_frames.tsv`. This post-exposure correction is not presented as a pristine second freeze. One pair, f78v.1 -> f78v.2, is absent from the replacement complete-line frame and was excluded, leaving 31 pairs. Both actual final source inputs contain zero f84r rows.

| model | gain bits | positive folios | top-1 vs reference | top-3 vs reference | local p | max-2 p |
|---|---:|---:|---:|---:|---:|---:|
| `LAST_HOST_CHAR3_HASH32` | -4.153 | 11/24 | 23/31 vs 24/31 | 27/31 vs 27/31 | 0.4594 | 1.0000 |
| `LAST_RAW_CHAR3_HASH32` | +1.293 | 12/24 | 24/31 vs 24/31 | 28/31 vs 27/31 | 0.0212 | 0.0212 |

Frozen gates: `{"host_beats_raw": false, "host_gain_positive": false, "majority_folios_positive": false, "max_two_p_le_005": false}`. The stripped PAGE_HOST lead does not transfer. The raw-string control changes the score by +1.293 bits, changes top-1 from 24 to 24 and top-3 from 27 to 28, is positive on 12/24 folios, and was not the frozen PAGE_HOST-layer prediction. It is a string-locality diagnostic, not a rescued PAGE_HOST transfer result.

The permutation null is deliberately coarse. It has 20 swappable pairs under the frozen section/Currier/hand/source-count strata, falling to 15, 4, and 0 after additionally matching final-field group count, PAGE_HOST length, and raw length. Its p-values are exploratory model-adjusted diagnostics, not exact opportunity-length-matched tests.

The test concerns formal continuation extent only. No heading, recipe, semantic role, object, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation is inferred. f84r did not enter the final analysis and is absent from every actual final tabular input and output. Limited audit-only exposure means the team-level seal was procedurally breached; no further f84r access is authorized.
