# GDT273 — q13 field-sequence grammar

Status: **Q13_FIELD_ORDER_NOT_PREDICTIVE_BEYOND_POSITION_AND_RECORD_SIZE**.

## Held-folio result

| view | states | held gain bits | +/− folios | gain z | max-4 gain p | same-state count | repeat z | max-4 repeat p |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SIZE2 | 2 | -7.290 | 3/6 | +0.502 | 0.7061 | 386 | +1.531 | 0.3493 |
| SIZE4 | 4 | -41.991 | 2/7 | -0.097 | 0.9153 | 247 | +3.153 | 0.0068 |
| END2 | 2 | -7.190 | 3/6 | +0.236 | 0.8165 | 385 | -3.054 | 0.0081 |
| JOINT4 | 4 | -9.916 | 4/5 | +1.942 | 0.1008 | 251 | +0.686 | 0.8897 |

No representation improves held-folio prediction beyond record-size and target-position baselines. The joint state is much less poor than its shuffled null, but its held gain remains negative; it cannot be called a predictive syntax.

The clearest ordering fact is END2 alternation: 385 same-endpoint adjacencies versus null mean 414.1, z=-3.05. This is expected to reflect the construction of DY-delimited fields and physical-line endpoints, not semantic sentence order.

## Consequence

The current sentence-level grammar remains hierarchical but weakly ordered: physical line reset, fields separated by DY, and optional B3-like closure are reproducible; coarse field size/endpoint classes do not form a portable first-order Markov syntax across q13 folios. A content-dependent or higher-order grammar remains possible.

No field role, word, language, plaintext, meaning, or translation is assigned. No f84r material was opened, retained, queried, joined, or scored.
