# GDT167 — register-conditioned opaque host codebooks

Decision: **NO_STABLE_REGISTER_CODEBOOK_OR_ALIGNMENT**.

## Within-register held-folio prediction

| stratum | context | gain bits | bits/focal | positive folios | null excess | local/max10 p | geometry corr/max5 p |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `HERBAL_A` | `WINDOW_PM2` | -1830.099 | -0.46818 | 0/47 | +0.00551 | 0.1795/0.8663 | +0.1938/0.6390 |
| `HERBAL_A` | `WHOLE_LINE` | -1639.910 | -0.41952 | 0/47 | +0.00931 | 0.0195/0.4985 | +0.1938/0.6390 |
| `HERBAL_B` | `WINDOW_PM2` | -401.411 | -0.30341 | 0/16 | +0.01176 | 0.0556/0.3102 | +0.0948/0.3463 |
| `HERBAL_B` | `WHOLE_LINE` | -344.228 | -0.26019 | 0/16 | +0.01387 | 0.0010/0.1893 | +0.0948/0.3463 |
| `STARS_RECIPE_B` | `WINDOW_PM2` | -2026.587 | -0.41751 | 0/12 | +0.06407 | 0.0010/0.0010 | +0.2163/0.6605 |
| `STARS_RECIPE_B` | `WHOLE_LINE` | -1784.428 | -0.36762 | 0/12 | +0.02769 | 0.0010/0.0039 | +0.2163/0.6605 |
| `PHARMA_A` | `WINDOW_PM2` | -135.132 | -0.20790 | 0/6 | +0.01252 | 0.1054/0.2546 | -0.0914/1.0000 |
| `PHARMA_A` | `WHOLE_LINE` | -135.715 | -0.20879 | 0/6 | +0.00121 | 0.4302/0.9980 | -0.0914/1.0000 |
| `BIOLOGICAL_B` | `WINDOW_PM2` | -1255.606 | -0.39823 | 0/9 | +0.01949 | 0.0029/0.0351 | +0.0452/0.6507 |
| `BIOLOGICAL_B` | `WHOLE_LINE` | -1001.246 | -0.31755 | 0/9 | +0.01359 | 0.0039/0.2049 | +0.0452/0.6507 |


Predictive codebook strata: `[]`.  Geometry-stable
strata: `[]`.  Herbal-B held-hand scores are
reported in the machine tables and are sensitivities, not independent samples.

## Glyph-blind cross-register alignment

| register pair | held geometry correlation | null excess | local/max10 p |
| --- | ---: | ---: | ---: |
| `HERBAL_A <-> HERBAL_B` | -0.0102 | -0.0031 | 0.5288/1.0000 |
| `HERBAL_A <-> STARS_RECIPE_B` | -0.0411 | +0.0114 | 0.4400/0.9990 |
| `HERBAL_A <-> PHARMA_A` | -0.0947 | -0.0443 | 0.6946/1.0000 |
| `HERBAL_A <-> BIOLOGICAL_B` | -0.0266 | -0.0145 | 0.5512/1.0000 |
| `HERBAL_B <-> STARS_RECIPE_B` | +0.1432 | +0.0829 | 0.2322/0.8859 |
| `HERBAL_B <-> PHARMA_A` | -0.0456 | -0.0304 | 0.5668/1.0000 |
| `HERBAL_B <-> BIOLOGICAL_B` | -0.0546 | -0.0731 | 0.8468/1.0000 |
| `STARS_RECIPE_B <-> PHARMA_A` | +0.0750 | +0.0442 | 0.3229/0.9776 |
| `STARS_RECIPE_B <-> BIOLOGICAL_B` | -0.0308 | -0.0301 | 0.6215/1.0000 |
| `PHARMA_A <-> BIOLOGICAL_B` | -0.0191 | -0.0147 | 0.5678/1.0000 |


Overall ten-pair mean correlation is -0.0104, with global
p=0.595122.  The common re-bound compiler gate is
`FAIL`.

Mappings were fitted only from anonymous marginal frequency, entropy,
concentration, self-context, position and line-size signatures.  Host strings,
shared identities and glyph similarity were unavailable.  Held targets were
separate-folio-half host--host co-occurrence geometries.

## Interpretation

This result distinguishes predictive exact-host codebooks, internally stable
register geometry, and cross-register anonymous geometry alignment.  None is a
word or semantic identification.  Correlated whole-line contexts are weighted
descriptive evidence, not independent linguistic tokens.

All f84-prefix rows were rejected before retention.  No f84r material was
opened, queried, retained, joined, or scored.
