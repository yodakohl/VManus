# SME003 target-blind cross-folio preflight

**PASS_TARGET_BLIND_CROSS_FOLIO_PREFLIGHT**

The frozen anonymous matrix retains 83/84 features: 33 formal and 50 root-rate features. The seven physical folios, 12 pages, 156 units, 468 alternate-reading rows, and every input hash match the freeze.

Across the 21 held-folio/reading transforms, analytic shrinkage ranges from 0.488717 to 0.526530; shrunk covariance condition numbers range from 5.560822 to 7.162502.

Every standardized matrix, covariance, and inverse is finite and positive definite. No ray, tail, core, color, or other morphology row was opened or joined, and every target artifact remained absent. This authorizes only a separately frozen synthetic calibration of cross-folio concordance. It supplies no association, meaning, lexeme, plaintext, language, or translation.

## Reproduction

```bash
./vpy experiments/semantic_assumptions/star_morphology_entry/build_sme003_cross_folio_preflight.py
```
