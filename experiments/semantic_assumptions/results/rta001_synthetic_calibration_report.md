# RTA001 synthetic calibration

Status: **PASS**. Backend: `CUDA`.

The calibration used no manuscript strings. It tested unrelated, transferred, local-only, one-panel-only, confounded, compositional, cycle-violating, and symmetry-varied artificial worlds.

## Gates

- `null_false_positive_at_most_1_of_32`: **PASS**
- `local_or_one_panel_positive_holdouts_at_most_2`: **PASS**
- `transferred_recovery_at_least_28_of_32`: **PASS**
- `cycle_residual_strictly_distinguishes_violation`: **PASS**

## Summary

- `null_false_positive_count`: 0
- `max_local_or_one_panel_positive_holdouts`: 1
- `transferred_pass_count`: 29
- `true_composition_mean_cycle_residual_bits`: 0.0
- `cycle_violation_mean_cycle_residual_bits`: 320.0

This calibration licenses only the frozen formal held-out test; it assigns no meaning or translation.
