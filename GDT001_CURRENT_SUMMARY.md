# GDT001 current exploratory summary

Runs retained: **3,364**; converged: **3,360**.

## Current leaders

| rank | run | class | system | bits/source symbol | total bits |
|---:|---|---|---|---:|---:|
| 1 | `sourcenull_juz` | NONSEMANTIC_GENERATOR | SOURCE_SELECTED_DELETION | 3.046666 | 592,040.3 |
| 2 | `sourceclass_k20` | NONSEMANTIC_GENERATOR | CONTEXTUAL_SOURCE_CLASSES | 3.046787 | 592,063.9 |
| 3 | `sourcenull_bjz` | NONSEMANTIC_GENERATOR | SOURCE_SELECTED_DELETION | 3.046939 | 592,093.3 |
| 4 | `sourcenull_bju` | NONSEMANTIC_GENERATOR | SOURCE_SELECTED_DELETION | 3.046944 | 592,094.4 |
| 5 | `sourcenull_buz` | NONSEMANTIC_GENERATOR | SOURCE_SELECTED_DELETION | 3.046964 | 592,098.2 |
| 6 | `sourcenull_juv` | NONSEMANTIC_GENERATOR | SOURCE_SELECTED_DELETION | 3.047004 | 592,105.9 |
| 7 | `sourcenull_jvz` | NONSEMANTIC_GENERATOR | SOURCE_SELECTED_DELETION | 3.047012 | 592,107.5 |
| 8 | `sourcenull_uvz` | NONSEMANTIC_GENERATOR | SOURCE_SELECTED_DELETION | 3.047023 | 592,109.7 |
| 9 | `sourcenull_bjv` | NONSEMANTIC_GENERATOR | SOURCE_SELECTED_DELETION | 3.047288 | 592,161.3 |
| 10 | `sourcenull_buv` | NONSEMANTIC_GENERATOR | SOURCE_SELECTED_DELETION | 3.047300 | 592,163.5 |
| 11 | `sourcenull_bvz` | NONSEMANTIC_GENERATOR | SOURCE_SELECTED_DELETION | 3.047308 | 592,165.0 |
| 12 | `sourcenull_jxz` | NONSEMANTIC_GENERATOR | SOURCE_SELECTED_DELETION | 3.047311 | 592,165.7 |
| 13 | `sourcenull_jux` | NONSEMANTIC_GENERATOR | SOURCE_SELECTED_DELETION | 3.047321 | 592,167.6 |
| 14 | `sourcenull_uxz` | NONSEMANTIC_GENERATOR | SOURCE_SELECTED_DELETION | 3.047340 | 592,171.3 |
| 15 | `sourcenull_bjx` | NONSEMANTIC_GENERATOR | SOURCE_SELECTED_DELETION | 3.047586 | 592,219.2 |
| 16 | `sourcenull_bxz` | NONSEMANTIC_GENERATOR | SOURCE_SELECTED_DELETION | 3.047606 | 592,222.9 |
| 17 | `sourcenull_bux` | NONSEMANTIC_GENERATOR | SOURCE_SELECTED_DELETION | 3.047615 | 592,224.8 |
| 18 | `sourcenull_jvx` | NONSEMANTIC_GENERATOR | SOURCE_SELECTED_DELETION | 3.047666 | 592,234.7 |
| 19 | `sourcenull_uvx` | NONSEMANTIC_GENERATOR | SOURCE_SELECTED_DELETION | 3.047681 | 592,237.5 |
| 20 | `sourcenull_gjz` | NONSEMANTIC_GENERATOR | SOURCE_SELECTED_DELETION | 3.047683 | 592,238.0 |

## Result

The current winner is an explicit nonsemantic source model. It treats the seven total occurrences of `j`, `u`, and `z` as a separately coded rare-event/deletion channel and uses the same second-order line-reset source model for the remaining symbols. It scores **3.046666 bits/source symbol**, 1,343 bits better than the original character null. A separately learned contextual-class model independently selected a 20-class alphabet and achieved nearly the same improvement, showing that the gain is rare-sign handling rather than semantic decoding.

Every language/cipher/notation candidate remains worse than an appropriate source-only baseline. Direct character, positional, context-conditioned, Currier-specific, periodic, fixed-block, learned-multigraph, whole-group character, whole-word nomenclator, null-symbol, STA-family/member, morphology, slot, differential-record, carrier/payload, and reading-order systems were tested. A stable 8-word Middle High German mapping was frequency-plausible but lost its exact matched source null; it is not retained as a reading.

No candidate met the freeze requirements. **No translation has been obtained.** No confirmation branch is recommended.

All results are exploratory and branch-local.
