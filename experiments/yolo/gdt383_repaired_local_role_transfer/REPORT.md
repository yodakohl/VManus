# GDT383 Stage A report

## Decision

`STAGE_A_FAILED_STOP_BEFORE_VOYNICH`

The repaired comparator instrument did not satisfy its predeclared positive-
control gate.  Stage B was therefore not created or run.  No Voynich target
row, GDT381 target membership, or f84 material was read.

## What worked

The multi-resolution, domain-local hierarchy materially repaired two failures
identified by GDT382.  It passed the complete role-recovery gate for two of six
hidden endpoints:

| hidden positive-control endpoint | hierarchy AUC | held gain (bits) | exact-joint AUC | universal AUC | role gate |
|---|---:|---:|---:|---:|---|
| FUNCTION_WORD | 0.8101 | +26,173.21 | 0.6868 | 0.3884 | PASS |
| ALTERNATIVE_OR | 0.7783 | +284.73 | 0.6704 | 0.4541 | FAIL: AUC |
| POLARITY_EXCLUSION | 0.8205 | -532.53 | 0.5645 | 0.4492 | FAIL: codelength |
| UNTIL_STATE_GATE | 0.8485 | -514.75 | 0.5767 | 0.3355 | FAIL: codelength |
| COORDINATOR | 0.8907 | +18,472.15 | 0.7101 | 0.4556 | PASS |
| REF_ANAPHORA | 0.7797 | +5,675.85 | 0.6389 | 0.5696 | FAIL: AUC |

All 42 hidden role-by-realization positive controls passed (`minimum AUC =
1.0`; minimum held gain `+4,580.17` bits).  This includes free, prefix,
suffix, wrapper, boundary, positional, and zero/suppletive realization modes.
The result is useful: composite encoding does not inherently hide the roles or
their bound realizations from the repaired local hierarchy.

The automatically conditioned-nuisance treatment was decisively harmful.  It
produced negative held codelength for all six roles, including approximately
`-338,298` bits for COORDINATOR and `-195,767` bits for FUNCTION_WORD.  This
reconfirms GDT382's warning that frequency, position, boundary, and recurrence
can be part of the grammar channel rather than removable nuisance.

## What failed

The strict disjoint-prediction requirement failed.  Development selected the
eligible downstream event `POST_WRAPPER_CHANGE_3` for all six roles, under
different channel treatments.  None passed the jointly charged confirmation
null:

| endpoint | Harleian gain | Quinte gain | total gain | max-family p | downstream gate |
|---|---:|---:|---:|---:|---|
| FUNCTION_WORD | +231.46 | +128.13 | +359.58 | 1.0000 | FAIL |
| ALTERNATIVE_OR | +249.37 | -118.25 | +131.11 | 1.0000 | FAIL |
| POLARITY_EXCLUSION | -5.60 | -72.51 | -78.11 | 1.0000 | FAIL |
| UNTIL_STATE_GATE | +314.05 | -224.08 | +89.98 | 1.0000 | FAIL |
| COORDINATOR | +414.60 | +99.79 | +514.39 | 0.3587 | FAIL |
| REF_ANAPHORA | +165.69 | -479.84 | -314.16 | 1.0000 | FAIL |

COORDINATOR was directionally positive in both untouched confirmation domains,
but its corrected `p = 0.3587`; it is not promotable.  The source-overlap audit
also rejected boundary/terminus outcomes whose membership was too predictable
from source-side structure.  The selected wrapper-change outcome passed that
leakage audit, so its failure cannot be repaired by choosing a more overlapping
definition.

## Methodological conclusion

GDT383 separates two questions that earlier instruments mixed:

1. Can a local hierarchy recover a hidden role from heterogeneous composite
   realizations? **Often yes.**
2. Does that inferred role predict a separately defined future transformation
   across untouched domains? **Not with the frozen outcome family.**

The next defensible step is not a Voynich operator search and not lower gates.
It is a new comparator-only calibration in which readable corpora provide
authorially grounded downstream event graphs or annotations, rather than the
current generic three-event geometry.  Any such experiment must be frozen
before its outcomes are evaluated and must retain the same source/outcome
separation.

## Claim ceiling

This is a comparator positive-control result only.  It does not establish a
Voynich role, operator, semantic class, POS, language, plaintext, or
translation.  Stage B remains unauthorized, F1 and the closed routes remain
closed, and f84 remains sealed.
