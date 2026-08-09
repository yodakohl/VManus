# SME001 target-free null and power calibration

## Decision

**FAIL — 2 calibration gates failed; target access remains forbidden.**

Using 32 CPU workers, the registered engine scored 64 complete 84-feature null worlds and 96 target/strength worlds under both 8,192-assignment phase ensembles. 0/64 null worlds contained any joint passing pair.

Joint signal pass counts by requested material level:

- ray: {'0.100': 0, '0.149': 0, '0.151': 0, '0.200': 0, '0.300': 0, '0.500': 5}
- tail: {'0.100': 0, '0.149': 0, '0.151': 0, '0.200': 0, '0.300': 0, '0.500': 0}

Failures: ray_high_power, tail_high_power.

This calibration measures only synthetic error and power behavior. It supplies no manuscript association, function, meaning, lexeme, plaintext, language, or translation.

## Reproduction

```bash
OPENBLAS_NUM_THREADS=1 ./vpy experiments/semantic_assumptions/star_morphology_entry/run_sme001_calibration.py
```
