# GDT385 source and capacity audit

Date frozen: 2026-08-19.

## Sources

The observation layer is the already frozen GDT382 CoReMA Voynichification:

`experiments/yolo/gdt382_voynichification_methodology_audit/artifacts/gdt382_voynichified_observation_layer.tsv.gz`

It contains 27,349 CoReMA elements.  The scorer may use only its oracle-blind
surface/composite fields.  In particular, `semantic_state` and
`encoder_used_oracle` are forbidden predictors.

The hidden evaluation layer is:

`gdt176_corema_role_oracle.tsv`

It contains 27,568 editor-aligned elements from six independent CoReMA
collections.  `role`, `annotation_flags`, and `parent_instruction_ordinal`
are hidden outcomes.  `editor_english_label` and `concept_id` are never used.

The GDT383 role definitions and multi-resolution observation model are
inherited from its published method/result.  GDT385 does not change GDT383's
failed common-future result or lower any earlier gate.

## Mechanical capacity, inspected before scoring

After joining observable elements, requiring at least one earlier observable
element, and excluding every positive parent link whose target is unavailable,
the parent-link panel has 26,169 pivots and 11,415 valid backward links.  Link
distance in physical element order ranges from 1 to 13.

The four predeclared role families have the following visible exact-link
capacity:

| anonymous route | hidden comparator definition | total role rows | parented | visible strict backward links | collections |
|---|---|---:|---:|---:|---:|
| CMP_PARENT_01 | `REF` | 113 | 99 | 97 | 6 |
| CMP_PARENT_02 | `TIME` | 275 | 240 | 237 | 6 |
| CMP_PARENT_03 | `ALTERNATIVE` | 503 | 340 | 324 | 6 |
| CMP_PARENT_04 | `annotation_flags=exclusion` | 231 | 202 | 201 | 6 |

The editor parent target is an `INSTRUCTION` ordinal within the recipe.  That
hidden instruction label is used only to construct the answer key.  Candidate
prediction is expressed as `NONE` or the exact backward element distance; no
instruction/POS/concept/meaning field is exposed to the model.

## Novelty and deduplication

GDT384 tested parse-derived sibling homology and found that its source
construction already predicted the relation above the frozen leakage ceiling.
GDT385 instead uses an editor parent pointer not contained in the composite
source representation.  It is not another local future window, exact-tuple
identity atlas, PAGE_HOST substring test, or GDT345–347 transition manifold.

Capacity enumeration is not a result.  No parent-link predictive score was
computed before the method freeze.
