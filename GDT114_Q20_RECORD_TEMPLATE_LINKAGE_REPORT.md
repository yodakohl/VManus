# GDT114 — Q20 OPEN-to-BODY record-template linkage

Status: **Q20_OPEN_BODY_RECORD_TEMPLATE_LINKAGE_SUPPORTED**

This nested whole-folio test reused 170 clean star-delimited Q20 records on
eight physical folios. It predicts anonymous HPR2 BODY-template profiles, not
BODY strings or meanings. The nuisance baseline already knows record shape and
the leave-one-record-out mean BODY profile of the other records on the held
folio. ZL3b is primary; IT2a and RF1b are alternate-reading sensitivities.

## Held-folio result

| representation | ZL gain bits | selector-paid | positive folios | local p | max-five p | IT gain | RF gain |
|---|---:|---:|---:|---:|---:|---:|---:|
| `COMPILER_ONLY` | +20.290 | +17.968 | 6/8 | 0.0063 | 0.0564 | +25.892 | +28.701 |
| `EDGE_ONLY` | +4.554 | +2.232 | 4/8 | 0.1203 | 1.0000 | +18.189 | +10.037 |
| `FULL_HPR2` | +22.672 | +20.351 | 6/8 | 0.0127 | 0.0173 | +39.825 | +35.029 |
| `RAW_CHAR3_HASH32` | +14.828 | +12.506 | 8/8 | 0.1582 | 0.4801 | +14.365 | +6.116 |
| `HOST_CHAR3_HASH32` | -21.150 | -23.472 | 1/8 | 0.8470 | 1.0000 | -12.114 | -25.727 |

The exact-length pairing null has 124/170 primary
records with permutation capacity. `FULL_HPR2` beats
both hashed-string controls. Its registered gates are `{"all_readings_positive": true, "beats_both_string_controls": true, "max_five_p_le_005": true, "selector_paid_positive": true, "six_of_eight_positive_folios": true}`.

## Relation to Q20OB001 and GDT113

Q20OB001 remains a zero-gain result for literal OPEN member/family/group caches
above KT/string and other-BODY vocabulary baselines. GDT114 tests a genuinely
different mechanism: training-folio OPEN profiles predicting held-folio BODY
compiler/edge distributions. A positive exploratory score would localize
record linkage above literal copying; a negative score would further narrow
GDT113 to page codebook ecology rather than OPEN-controlled record templates.

No semantic role, recipe, heading, word, morpheme, POS, sound, language,
plaintext, meaning, or translation is inferred. f84r was rejected before
formal retention and was not opened, retained, queried, joined, scored,
targeted, or assigned a prediction.
