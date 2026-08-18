# GDT342 comparator report — anonymous entity-flow graphs

Status: **ANONYMOUS_ENTITY_FLOW_NOT_CALIBRATED**.

The comparator contains 688 wording-distinct eligible records and 657 cross-collection parallel pairs. Every concept identity was restarted and renamed inside each record before graph construction.

| model | top-1 | top-5 | MRR@100 | positive folds vs all controls | inclusive p |
|---|---:|---:|---:|---:|---:|
| SIZE_ONLY | 78/688 (11.3%) | 203/688 (29.5%) | 0.2046 | NA | NA |
| ORDER_ONLY | 261/688 (37.9%) | 315/688 (45.8%) | 0.4243 | NA | NA |
| UNORDERED_INCIDENCE | 245/688 (35.6%) | 360/688 (52.3%) | 0.4388 | NA | NA |
| RAW_OPAQUE_WORD_IDENTITY | 538/688 (78.2%) | 578/688 (84.0%) | 0.8075 | NA | NA |
| ANON_ENTITY_FLOW | 343/688 (49.9%) | 399/688 (58.0%) | 0.5401 | 0 | 1.000000000 |
| GLOBAL_CONCEPT_ID_CEILING | 565/688 (82.1%) | 636/688 (92.4%) | 0.8667 | NA | NA |

The entity-flow model was frozen before these scores. It must beat size, order-only, unordered incidence, and raw opaque-word identity simultaneously.

The flow topology contains real parallel-recipe signal: it improves top-1 from
261 for order-only and 245 for unordered incidence to 343. That gain is not the
requested abstraction, however. Exact diplomatic source-token identity reaches
538 top-1 and MRR .8075, versus flow MRR .5401. The global editor-concept
ceiling is only moderately higher at MRR .8667. The simplest account is that
cross-witness recipe identity remains heavily carried by recurring lexical or
entity identity; anonymous topology alone does not preserve enough of it.

An initial uncommitted dry run accidentally used CoReMA `commodity=Q...`
normalizations in the raw-word control. It was detected before target access or
publication, corrected to diplomatic source tokens without changing the
candidate graph, and independently reconstructed in validation. See
`CORRECTION.md`.

The readable comparator failed its gate. GDT327 remains unopened and Stage B is not run.

No concept name, concept ID, source form, semantic role, or word was exported as a graph feature. No Voynich role, meaning, language, plaintext, or translation follows. f84 was not accessed.
