# GDT340 comparator report — complete-record event schemas

Status: **COMPARATOR_RECORD_SCHEMA_RECOVERABLE**.

The ontology and instrument were derived from 1,136 complete records in six readable medieval recipe collections before any Voynich tuple value was retained or scored. Forms, language, order, and local token context were hidden from the model.

## Held-collection recovery

| event axis | positive / negative records | gain vs prevalence (bits) | positive folds | mean AUC | max-ten p | recoverable |
|---|---:|---:|---:|---:|---:|---|
| MATERIAL | 1134 / 2 | +17.779 | 6/6 | 0.667 | 1.0000 | NO |
| OPERATION | 1135 / 1 | -6.393 | 5/6 | 0.417 | 1.0000 | NO |
| INTERMEDIATE_STATE | 207 / 929 | +124.694 | 6/6 | 0.778 | 0.0002 | YES |
| APPLICATION | 282 / 854 | +41.360 | 5/6 | 0.684 | 1.0000 | NO |
| RESULT_CONDITION | 599 / 537 | +32.159 | 5/6 | 0.658 | 1.0000 | NO |

## Interpretation

The three-witness fake-morel preparation and the two stuffed-apple records show qualitatively that MATERIAL→OPERATION→intermediate/result/application event structure survives wording, abbreviation, and layout variation even when individual optional events differ.

Quantitative recoverability is stricter: only axes marked YES may enter the blind Voynich diagnostic. MATERIAL and OPERATION cannot support the decision by themselves because they are nearly universal. Failure of an optional axis means the present anonymous topology does not recover it across collections; it does not erase the readable ontology.

No Voynich field or tuple has been assigned an event class. f84 was not accessed.
