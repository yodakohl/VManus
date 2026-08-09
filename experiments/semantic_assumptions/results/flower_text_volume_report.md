# FLOWERVOL001 recovered text-volume report

## Result

**Validated recovered nonconfirmation; production target artifact lost.**

The registered production invocation completed its three scores but failed
while JSON tried to serialize a NumPy boolean. No `TARGET_RESULT.json` was
written. The production scorer was not rerun or modified. The already frozen
nonimporting matrix implementation recovered the result, and a separate
scalar enumeration validated the recovered artifact in 14 checks.

| Measure | flower-minus-explicit-negative effect | exact familywise p | directional blocks | Result |
|---|---:|---:|---:|---|
| physical lines | -2.642857 in every reading | 0.469593049840 | 4/7 minimum | fail |
| stored tokens | -18.143 / -17.571 / -17.857 IT/RF/ZL | 0.325560128029 | 4/7 minimum | fail |
| tokens per line | mixed signs | 1.000000000000 | 0 | fail |

Line and token differences exceed their material-size thresholds and survive
each block deletion, but they are common under the exact 2,187-way null and
miss the frozen five-of-seven block gate. Packing density has no consistent
direction. Zero measure passes.

## Interpretation and scope

There is no evidence in this panel that side-view-flower pages contain more
text, less text, or a different line density than explicitly fruit/flower-free
pages. The negative raw direction is descriptive, not a finding. This weakens
only the simple whole-page volume/packing version of an illustration-
description model; it does not show that the text is unrelated to the plants
or that flower information is absent.

Because the production artifact was lost, production-versus-independent
target parity is unavailable and the result is explicitly recovered rather
than a normal final production result. It supplies no flower line, FLOWER,
FRUIT, NO, plant name, language, plaintext, or translation.

## Reproduction

Do not rerun the failed registered production target. Reproduce the preserved
recovery and its validator:

```text
./vpy experiments/semantic_assumptions/flower_text_volume/recover_flower_text_volume_target.py --output experiments/semantic_assumptions/flower_text_volume/RECOVERED_TARGET_RESULT.json
./vpy experiments/semantic_assumptions/flower_text_volume/validate_recovered_flower_text_volume.py --output experiments/semantic_assumptions/flower_text_volume/RECOVERED_TARGET_VALIDATION.json
```
