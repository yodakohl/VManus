# GDT323 — register-conditioned renderer magnitude

This is a post-exposure architectural decomposition of the already exposed
GDT318 panel. It does not select another wrapper rule. The only effects are the
two independently transferable GDT321 rules:

- `s × LINE_START`;
- `q × PREV_DY`.

Compare four fixed models in leave-one-physical-folio-out folds:

1. `CELL`: exact opaque-cell Dirichlet-1/2 counts;
2. `GLOBAL_TWO_RULE`: one shared coefficient for each rule;
3. `CURRIER_TWO_RULE`: separate A/B coefficients for each rule;
4. `REGISTER_TWO_RULE`: separate coefficients for the five already frozen
   registers `HERBAL_A`, `HERBAL_B`, `OTHER_A`, `OTHER_B`, and
   `STARS_RECIPE_B`.

Cell counts and coefficients are learned only from training folios. Use ridge
10. Charge each nonbaseline model by `k/2 × log2(5607)` plus a `log2(4)` model
selector, with `k=2,4,10`. Prefer the model with the shortest charged held code.
No section-specific model, coefficient, exception, or threshold may be added.

Report total, register, section, and folio gains; all fold-specific
coefficients; and an 8,192-world fixed-crossfit max-three cell/register label
alignment diagnostic. This diagnostic reuses fitted predictions rather than
retraining each world and is therefore descriptive, not an exact conditional
permutation test.

Call a conditioned model preferred only when it has shorter charged held code
than both simpler models and every one of its fitted mean `s` and `q`
coefficients is positive. Otherwise retain the simplest shorter-code model or
report mixed conditioning.

The panel and the register contrast are fully exposed. This experiment can
only decide how to parameterize an opaque-cell renderer. It assigns no prefix,
morpheme, POS, meaning, sound, language, plaintext, or translation and does not
predict unseen cell licenses. No f84 row may be opened, parsed, retained,
joined, or scored.
