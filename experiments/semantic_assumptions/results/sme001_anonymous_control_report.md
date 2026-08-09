# SME001 target-free production controls

## Decision

**PASS — all synthetic production controls passed; the real target remains unjoined.**

The runner evaluated exactly 84 synthetic features against two targets under 65,536 independent-page and coupled-folio assignments. It performed 926 deterministic checks. Real source files were read only as opaque bytes for frozen SHA-256 identities; no morphology row was parsed or joined to a feature value.

Failures: none.

This is an implementation control, not evidence about the manuscript. It supplies no marker association, function, meaning, lexeme, plaintext, language, or translation.

## Reproduction

```bash
./vpy experiments/semantic_assumptions/star_morphology_entry/run_sme001_anonymous_controls.py
```
