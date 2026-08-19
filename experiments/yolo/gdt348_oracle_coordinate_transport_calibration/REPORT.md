# GDT348 oracle-coordinate transport calibration report

Status: **ORACLE_MANUSCRIPT_SPECIFIC_RETAINED**

GDT348 applies the exact three GDT347 pair tables and weights to authored oracle coordinates in the frozen synthetic controls. No Voynich model or score is changed.

## Panel results

| system | held events | raw gain (bits) | after topology cost | positive units | exact independent→graph | local p | max-3 p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| LEXICAL_A | 3103 | -82.185458841588314 | -91.015181576674365 | 0/5 | 2370→2370 | 0.060043934586282648 | 0.060043935 |
| FACTORIAL_B | 3103 | -1403.7025283047162 | -1412.5322510398023 | 0/5 | 1652→1652 | 0.26116670734683917 | 0.060043935 |
| HUMAN_GROWN_B2 | 3103 | -788.28571920503805 | -797.11544194012413 | 0/5 | 1942→1942 | 0.040273370759092021 | 0.060043935 |

## Edge decomposition

| system | edge | gain (bits) | non-neutral truth cells |
| --- | --- | ---: | ---: |
| LEXICAL_A | inner_d↔canonical_wrapper | -0.58246523875852119 | 3103/3103 |
| LEXICAL_A | dy_closure↔canonical_wrapper | -82.026536077154518 | 3103/3103 |
| LEXICAL_A | right_family↔dy_closure | -0.21786048915911177 | 3103/3103 |
| FACTORIAL_B | inner_d↔canonical_wrapper | -790.58508899333822 | 3103/3103 |
| FACTORIAL_B | dy_closure↔canonical_wrapper | -82.026536077153494 | 3103/3103 |
| FACTORIAL_B | right_family↔dy_closure | -521.79631943600964 | 3103/3103 |
| HUMAN_GROWN_B2 | inner_d↔canonical_wrapper | -370.35977137121449 | 3103/3103 |
| HUMAN_GROWN_B2 | dy_closure↔canonical_wrapper | -82.026536077151434 | 3103/3103 |
| HUMAN_GROWN_B2 | right_family↔dy_closure | -331.45296426148741 | 3103/3103 |

## Interpretation

All three fully comparable controls worsen held codelength, and every system is negative on all five held source units. Supplying the authored fields therefore does not rescue the GDT347 transport. B2's nominal local `p=.0403` is not positive evidence: its observed gain is −788.29 bits and only exceeds still more-negative coupling-destruction worlds. Exact next-state recovery is unchanged in every system.

This is an oracle ceiling. A positive result would show that a known authored system can reproduce the frozen Voynich coupling only after its true fields are supplied; it would not show that the blind VManus parser can recover those fields. The present negative result is stronger than GDT347 for the mapped inner-D, right, DY, wrapper, frame, and B3 analogues, but not for omitted field-marker, positional-right, literal, host, or B2-closure structure. The result retains a manuscript-specific formal convention within this coordinate definition; it does not establish a unique compiler.

No semantics, PAGE_HOST factorization, tuple merging, morphology, language, plaintext, translation, or f84 access occurred.
