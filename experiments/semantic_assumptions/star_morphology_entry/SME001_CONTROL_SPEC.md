# SME001 synthetic control specification

Status: **FROZEN_BEFORE_CONTROL_RUN**

These controls exercise the SME001 production statistic without parsing or
joining the real morphology binding to the real feature matrix. The real
target files may be read only as uninterpreted bytes for SHA-256 checks.

## Synthetic panel

Use 12 length-12 pages in this order:

`s01r,s01v,s02r,s02v,s03r,s04r,s05r,s05v,s06r,s06v,s07r,s07v`.

The page suffix gives the side and deleting it gives one of seven physical
folios. Unit IDs are `page.SNN`, with one-based two-digit ordinals.

The ray sequence on every page is
`7,8,8,7,7,8,7,8,8,7,8,7`. Replace `s01r` ordinal 5 by rare state `6` and
`s02v` ordinal 11 by rare state `9`.

Only pages `s01r,s01v,s02r,s03r,s04r,s05r,s06r,s06v` vary in tail state.
Assign their two-tail positions, respectively, as:

1. `1,4,7,10`
2. `1,6,8,11`
3. `2,5,7,12`
4. `3,4,9,10`
5. `1,2,8,9`
6. `3,6,7,12`
7. `2,3,10,11`
8. `4,5,8,9`

All other positions have one tail, except `s07r` ordinal 12, which has the
explicit ignored state `-`.

## Synthetic feature family

Use all three reading slots and these 14 columns:

1. `PARA_WORD_COUNT`
2. `FORMAL_PLANTED_RAY`
3. `ROOT_ATOM_RATE__PLANTED_TAIL`
4. `NULL_A`
5. `NULL_B`
6. `NULL_C`
7. `PARITY_ONLY_RAY`
8. `EARLY_ONLY_RAY`
9. `PAGE_CONSTANT`
10. `BIFOLIO_CONSTANT`
11. `ONE_FOLIO_RAY`
12. `READING_DISAGREEMENT_RAY`
13. `ROOT_ATOM_RATE__LENGTH_ONLY`
14. `CONSTANT`

Let ray and tail scores be `-1/+1` for the registered low/high states and zero
for ignored states. Deterministic noise is obtained from the first eight bytes
of SHA-256 on `SME001_CONTROL_NOISE_V1|feature|reading|unit`, mapped uniformly
from unsigned 64-bit integer to `[-1,1]`.

- word count is `40 + 8*ray_score + ordinal%3 + reading_index`;
- planted ray is `ray_score + .03*noise`;
- planted tail is `.15 + .08*tail_score + .003*noise`;
- each null is `.5 + .1*its_noise`;
- parity-only and early-only equal ray score only in their named half and zero
  elsewhere;
- page and bifolio constants are their one-based indices;
- one-folio ray equals ray score on `s01`; elsewhere it uses a deterministic
  varying nuisance that is centered separately in each ray group on each page,
  making its physical ray contrast exactly zero;
- reading disagreement multiplies ray score by `+1,-1,+1`;
- length-only is exactly `log1p(PARA_WORD_COUNT)/10`; and
- constant is one.

## Registered controls

The primary control run uses 65,536 assignments including the physical row.
It must show:

- the ray/formal and tail/root planted pairs pass every statistical gate;
- all three null features produce no statistical pass;
- parity-only and early-only fail their named robustness gates;
- page, bifolio, and constant features fail within-page eligibility;
- the one-folio signal fails deletion and common-folio support;
- reading disagreement fails the common reading direction;
- the length-only root fails the root-length residual gate while retaining the
  other intended association gates.

A 16,384-assignment one-target/one-feature run must prove that globally
complementing the feature, or reversing the target contrast, reverses every
raw reading effect while preserving the robust statistic and Monte Carlo
tails.

The runner must additionally test exact deterministic rotation reproduction;
inclusive ties; rare-state counts; cyclic adjacent-pair preservation; an
example of linear-cut relocation; exact-row acceptance; rejection of duplicate,
missing, extra, reordered, page, folio, ordinal, locus, nonfinite, negative
word-count, and constant cases; frozen real-file hashes; and absence of all
predeclared target result artifacts.

No synthetic control result is evidence about the manuscript.
