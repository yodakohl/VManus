# F77r residual-form assignment result

## Result

**Final post-hoc nonconfirmation of residual lexical quality identity.**

The earlier f57-to-f77r bridge used two complete-surface features—leading
`ot` and terminal `y`—to place each form in one of four inherited f57
quality-position states. This analysis removed exactly those two features and
asked whether the remaining f77r spelling best matched the f57v exemplar at
the same state position.

It did not. Across all `4! = 24` possible assignments, the observed identity
assignment ranks **4th of 24** in the exact joint score: three assignments
score higher and no other assignment ties it. The unique joint optimum swaps
the HOT-position and MOIST-position exemplars while retaining COLD and DRY.
That optimum is a spelling diagnostic only; it is not an alternative semantic
assignment.

| Reading | Observed exact score | Inclusive rank | Best assignment |
|---|---:|---:|---|
| ZL3b | 629/2880 | 2/24 | swap HOT/MOIST |
| IT2a | 719/2880 | 5/24 | swap HOT/MOIST |
| RF1b | 71/320 | 7/24 | two-way maximum tie including HOT/MOIST swap |
| equal-reading joint | 1987/8640 | 4/24 | swap HOT/MOIST |

The score concatenates spaces, removes one leading `ot` and one terminal `y`,
uses normalized character Levenshtein similarity, averages labels within each
target state, averages the four states equally, and finally averages the three
alternate readings. ZL3b, IT2a, and RF1b are alternate readings of one
manuscript, not independent observations.

## Deletion diagnosis

HOT and COLD each occur twice on f77r, permitting four state-preserving
one-label deletions. The identity assignment is not a unique optimum under any
of them.

| Deleted label | Identity rank | Strictly higher assignments | Exact ties including identity |
|---|---:|---:|---:|
| `f77r.2` | 18/24 | 17 | 1 |
| `f77r.7` | 3/24 | 2 | 1 |
| `f77r.4` | 9/24 | 8 | 2 |
| `f77r.5` | 3/24 | 2 | 1 |

The strongest apparent support is therefore concentrated in `f77r.2`
`olkchs`, compared with the COLD-position f57 exemplar `olkeedal` in ZL and
`olkchdal` in IT/RF. Once that row is removed, the observed assignment falls
from fourth to eighteenth. This is compatible with one shared `ol+k…`
form-family resemblance; it is not evidence for a four-item quality lexicon.

## Validation and ceiling

A standalone validator imports no experiment code and reconstructs the exact
input bindings, 18 residual comparisons, all 24 assignments per reading and
jointly, all four deletion spaces, tie-aware ranks, and the decision in 21
checks. It reconstructs 480 assignment evaluations.

Retain the prior provisional f57-to-f77r **structural transition construction**
only. Reject independent residual lexical quality identity under this fixed
normalization and score. Do not translate the winning permutation, any label,
`ot`, terminal `y`, a quality, an element, an apparatus part, plaintext, or a
language. The next valid confirmation target remains a second independently
annotated same-orientation apparatus: short labels inside segments plus
independently visible active and inactive boundaries.

## Reproduction

```text
./vpy experiments/semantic_assumptions/f77r_quality_transition_bridge/audit_f77r_residual_form_assignment.py --output experiments/semantic_assumptions/results/f77r_residual_form_assignment.json
./vpy experiments/semantic_assumptions/f77r_quality_transition_bridge/validate_f77r_residual_form_assignment.py --output experiments/semantic_assumptions/results/f77r_residual_form_assignment_validation.json
```
