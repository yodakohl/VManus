# GDT321 — two-rule renderer sufficiency

Reuse the complete frozen GDT318 panel without selecting another event. Fit
only the two renderer effects that transferred prospectively on disjoint exact
surfaces:

- add one shared coefficient to class `s` at physical line start;
- add one shared coefficient to class `q` immediately after a DY-closed
  physical group.

All other wrapper-class/context coefficients are fixed to zero. Compare this
`ROBUST_TWO_RULE` model with the exact-cell Jeffreys baseline and with the
unrestricted 16-coefficient GDT318 anchor in leave-one-physical-folio-out
folds. Cell counts and coefficients are learned only inside training folds.
Use Dirichlet-1/2 cell counts and ridge 10.

Charge each model by `k/2 × log2(5607)` bits plus a `log2(3)` model selector:
`k=2` for the robust model and `k=16` for the unrestricted anchor. Report held
gain, charged gain, fraction of unrestricted raw gain retained, section and
wrapper contributions, and an 8,192-world fixed-crossfit max-two
cell/register alignment diagnostic. The diagnostic is not an exact retrained
null.

Call `TWO_RULE_RENDERER_SUFFICIENT` only if the robust model has positive
charged gain, retains at least half of the unrestricted raw gain, has positive
gain in at least two of B/H/S, has positive `s` and `q` coefficients in at
least 75/91 folds each, and max-two diagnostic p is at most .05.

This is a post-exposure architectural compression of GDT318, not an
independent manuscript discovery. It predicts wrapper choice only after an
opaque compatible cell is known and assigns no prefix, morpheme, POS, meaning,
sound, language, plaintext, or translation. No f84 row may be opened, parsed,
retained, joined, or scored.
