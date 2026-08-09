# F67v1 dual-topology transition transfer

## Result

**FINAL post-hoc nonconfirmation of a universal transition rule.**

The human source fixes 17 outward radial texts clockwise from the double ray.
Each of the 17 cyclic sectors between consecutive radial texts contains at
least one star. Before calculating their states, the direct dual of the f77r
rule was fixed: if graphical output universally occurs exactly when adjacent
f57-derived states differ, all 17 star-bearing sectors must lie between
different radial states.

The unchanged complete-line `starts-ot,terminal-y` states give:

| Reading | Changed adjacent states | Unchanged adjacent states | Universal gate |
|---|---:|---:|---|
| ZL3b | 10 | 7 | fail |
| IT2a | 9 | 8 | fail |
| RF1b | 8 | 9 | fail |

The test deliberately did not use the exact 1–4 star counts, tune a threshold,
rotate the human order, or select a subset. A nonimporting implementation
reconstructs the source bindings, cyclic sequences, counts, and decision in 19
checks; two runs are byte-identical.

## Interpretation

Reject a manuscript-wide rule that any graphical output is licensed by a
change in the f57-derived state under a generic boundary/sector dual. This
does **not** refute the narrower f77r finding: f67v1 uses long radial texts on
sector boundaries, whereas f77r uses short labels inside tube segments and
emissions at their boundaries. A valid confirmation must match that same
construction orientation rather than merely being another segmented diagram.

No star count, quality, element, `ot`, terminal-`y`, lexeme, plaintext, or
translation follows.

## Reproduction

```text
./vpy experiments/semantic_assumptions/f77r_quality_transition_bridge/audit_f67v1_dual_transition_transfer.py --output experiments/semantic_assumptions/results/f67v1_dual_transition_transfer.json
./vpy experiments/semantic_assumptions/f77r_quality_transition_bridge/validate_f67v1_dual_transition_transfer.py --output experiments/semantic_assumptions/results/f67v1_dual_transition_transfer_validation.json
```
