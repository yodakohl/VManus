# GDT264 — q13 within-page record fingerprint

Status: **Q13_RECORD_LOCAL_FINGERPRINT_EXPLORATORY**.

## Result

Each half-record had to retrieve its mate from the two eligible records on the same physical page. Page, section, hand, and broad illustration/register ecology are therefore fixed.

| representation | top-1 / 144 | accuracy | local p | max-six p | positive pages |
|---|---:|---:|---:|---:|---:|
| COMPILER_COARSE | 90 | 0.625 | 0.0012 | 0.0034 | 7/9 |
| RAW_CHAR3 | 86 | 0.597 | 0.0010 | 0.0495 | 8/9 |
| PAGE_HOST_CHAR3 | 86 | 0.597 | 0.0046 | 0.0495 | 7/9 |
| RAW_EXACT | 84 | 0.583 | 0.0273 | 0.1108 | 7/9 |
| PAGE_HOST_EXACT | 79 | 0.549 | 0.0854 | 0.4044 | 7/9 |
| STRUCTURE_ONLY | 72 | 0.500 | 0.5560 | 0.9563 | 4/9 |

The strongest representation is **COMPILER_COARSE** at 90/144 top-1 retrievals (max-six p=0.0034). PAGE_HOST exact identity scores 79/144 and raw exact groups 84/144.

## Post-hoc compiler decomposition

| compiler block | top-1 / 144 | local p | max-five p | positive pages |
|---|---:|---:|---:|---:|
| WRAPPER | 97 | 0.0022 | 0.0027 | 6/9 |
| RIGHT | 92 | 0.0024 | 0.0203 | 7/9 |
| JOINT_CELL | 92 | 0.0073 | 0.0203 | 7/9 |
| CLOSURE | 86 | 0.0249 | 0.1379 | 5/9 |
| FRAME_INNERD | 83 | 0.0769 | 0.2795 | 4/9 |

The post-hoc lead is **WRAPPER** at 97/144. Because this block search was nominated after seeing the primary compiler result, it localizes the descriptive mechanism but is not preregistered confirmation.

This is a prerequisite test for a latent topic/address scale. A positive record fingerprint means only that nonadjacent pieces of the same mechanical record share formal inventory beyond a random within-page mate assignment. It does not say what that inventory denotes. Raw strings and PAGE_HOST character texture both retrieve records, but exact PAGE_HOST identity is weak; the strongest signal lies in record rendering, especially wrapper ecology. That favors a record-template explanation over a simple paragraph-local dictionary.

## Limits

The panel contains nine pages and eighteen GDT227 mechanical records, not a complete authorial paragraph census. The split and feature family are exploratory and exposed. The test is within-page by design and cannot establish a global lexicon. All semantic values remain unassigned.

No f84r row was opened, queried, retained, or scored in this experiment. The earlier process-level transient-parse breach remains disclosed; no further f84r access was authorized or performed.
