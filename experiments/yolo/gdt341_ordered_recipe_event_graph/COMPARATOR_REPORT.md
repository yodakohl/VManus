# GDT341 comparator report — ordered anonymous recipe graphs

Status: **NO_COMPARATOR_GRAPH_CALIBRATION**.

The source-only census contains 688 wording-distinct eligible records and 657 cross-collection parallel pairs. Titles, concepts, roles, and source forms were hidden during ranking.

| model | top-1 | top-5 | MRR@100 | positive folds vs both controls | max-two p | hidden transition Jaccard |
|---|---:|---:|---:|---:|---:|---:|
| SIZE_ONLY | 78/688 (11.3%) | 203/688 (29.5%) | 0.2046 | NA | NA | 0.514 |
| UNORDERED_GRAPH | 295/688 (42.9%) | 392/688 (57.0%) | 0.4960 | NA | NA | 0.684 |
| ORDERED_FIELD_GRAPH | 256/688 (37.2%) | 302/688 (43.9%) | 0.4137 | 1 | 1.000000000 | 0.664 |
| ORDERED_REPEAT_GRAPH | 284/688 (41.3%) | 356/688 (51.7%) | 0.4682 | 2 | 1.000000000 | 0.657 |
| GLOBAL_OPAQUE_ID_CEILING | 561/688 (81.5%) | 612/688 (89.0%) | 0.8501 | NA | NA | 0.792 |

Selected representation: **ORDERED_REPEAT_GRAPH**.

A successful result means that order/equality topology recovers known external parallels better than record size and an unordered graph. Hidden event-transition agreement is a post-ranking calibration, not a graph input.

No Voynich record or tuple value was read or scored in Stage A. No semantic role, word, language, plaintext, or translation follows; f84 was not accessed.
