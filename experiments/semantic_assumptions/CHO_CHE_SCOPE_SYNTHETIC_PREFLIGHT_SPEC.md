# `cho/che` paragraph-scope synthetic preflight

Status before execution: **REGISTERED_TARGET_UNOPENED**

## Distinct question

Test whether the formal `o/e` choice at one strict `ch/sh+o/e` site has local
persistence inside the ZL-editor-marked paragraph span beyond collapsed page,
exact masked template, line position, and generic sequence order.

This is not IL018/IL019's universal paragraph-ordinal profile test and does not
reuse their formal/root features. It is not the Parisel page-state/template
inventory. It uses a binary site hidden from the frozen masked geometry and a
proper leave-one-event-out prediction contrast.

This preflight may read only:

- `results/cho_che_scope_masked_events.tsv`, SHA-256
  `41f8b517419d2215a97db9ce245c5639f383b11c41d8c1377a245dea8e37abf3`;
- `results/cho_che_scope_masked_universe_validation.json`, SHA-256
  `e7d37a23ca199e421946fab0c42f4547aade0a5fa27579b1e9e69518c0d376ec`;
- `cho_che_scope_core.py`, SHA-256
  `fc57f5b96ea49fc380aabc1fbed81273111a6d3981f1fd46bbbb0aeff05891e4`;
- this specification and the preflight runner itself.

It must only existence-test, never open, the future target runner/result/report
and the source alignment containing the selected-site value. NumPy, OpenBLAS,
OMP, and MKL are pinned to one thread before NumPy import. The world grid is
distributed over 32 forked workers.

## Frozen panels

For each reading separately, use all masked events. A primary query is one of
the 501 already frozen quartile-conditioned queries. Its same predictor uses
every other event with the same collapsed page, exact masked template, line
quartile, and marked paragraph. Its comparison predictor uses every event with
the same page/template/quartile but another marked paragraph.

For binary outcome `y`, use Jeffreys probabilities

`p = (sum(y_support)+0.5)/(n_support+1)`

and query gain

`y log(p_same/p_other) + (1-y) log((1-p_same)/(1-p_other))`.

Average equally in this order: queries within marked paragraph, marked
paragraphs within collapsed page, collapsed sides within physical folio, then
physical folios. This is `LOCAL_T`.

The stricter boundary diagnostic forms every pair sharing collapsed page and
exact masked template at exact ZL line distance 1 through 12. Within each exact
`page + template + line-distance` stratum, retain the stratum only if both
same-marked-paragraph and different-marked-paragraph pairs exist. Compute mean
binary agreement of the former minus the latter. Average strata to page, page
to physical folio, then folios equally. This is `BOUNDARY_T`. It deliberately
controls exact distance; it does not claim the editorial boundary is
authorial.

## Frozen nulls

For each `(collapsed page, masked template, line quartile)` sequence sorted by
line index, group index, and event ID, rotate the complete outcome sequence as
`new[j] = old[(j-shift) mod n]`. This preserves the stratum's outcome count and
generic cyclic sequence pattern.

Use assignments 1 through 511 and plus-one p-values. Two ensembles are gated:

- `INDEPENDENT_STRATUM`: SplitMix64 gives a separate `shift mod n` for every
  stratum;
- `COUPLED_PAGE`: every stratum on one collapsed page receives the same
  SplitMix64 integer clock, reduced `mod n` separately.

The seed domain is the exact frozen world-family/amplitude/world identifier.
ZL is the primary because both the line coordinate and marked paragraphs are
ZL editorial scaffolds. IT and RF are alternate-reading direction and
concentration guards, never independent replications.

## Frozen gates

`LOCAL_PASS` requires:

- ZL `LOCAL_T >= 0.10`, both p-values `<=0.05`, minimum leave-one-folio-out
  effect `>=0.05`, at least 21/35 positive folios, and maximum absolute folio
  contribution fraction `<=0.15`;
- IT and RF each have `LOCAL_T >=0.05`, positive minimum leave-one-folio-out,
  and maximum absolute contribution fraction `<=0.18`.

`BOUNDARY_PASS` requires:

- ZL `BOUNDARY_T >=0.10`, both p-values `<=0.05`, minimum leave-one-folio-out
  effect `>=0.05`, at least 27/45 positive folios, and maximum absolute folio
  contribution fraction `<=0.15`;
- IT and RF each have `BOUNDARY_T >=0.05`, positive minimum
  leave-one-folio-out, and maximum absolute contribution fraction `<=0.18`.

The synthetic grid is fixed:

- 64 `NULL` worlds with page, template, and continuous-position propensities;
- eight `PARAGRAPH` worlds at logit amplitude 2.0 for local power;
- eight `PARAGRAPH` worlds at logit amplitude 3.5 for boundary power;
- eight `ONE_FOLIO` worlds at amplitude 4.0;
- eight `SEQUENTIAL` worlds with 0.9 copy probability across the full ordered
  page/template/quartile sequence, ignoring marked boundaries.

The preflight passes only with no more than 3/64 null passes for either gate,
at least 7/8 local-power `LOCAL_PASS`, at least 7/8 boundary-power
`BOUNDARY_PASS`, zero gate passes in both one-folio families, zero gate passes
in both sequential families, complement invariance to `1-y` within `1e-12`,
exact label-multiset preservation by both rotation ensembles, exact capacity,
finite scores, mutation rejection, input/hash isolation, and target absence.

## Future one-time target decision

Only a validated preflight may authorize a separately frozen target runner
using 8,191 assignments per ensemble. `LOCAL_PASS` would establish only that
the formal choice has marked-span-aligned local persistence beyond the frozen
controls. `BOUNDARY_PASS` may add a distance-controlled editorial-boundary
association. A failure is a frozen nonconfirmation; no retuning, alternate
position bin, reading selection, threshold change, or second target run.

Neither result identifies an authorial paragraph, vowel, consonant, sound,
word, language, cipher operation, topic, meaning, plaintext, or translation.
