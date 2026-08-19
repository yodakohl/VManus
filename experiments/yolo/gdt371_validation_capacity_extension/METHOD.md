# GDT371 untouched-validation capacity extension

Status: **FROZEN BEFORE SIMULATION**.

GDT370 showed that enlarging discovery while keeping only two small untouched
folios yields reliable candidate selection but very low selector-paid
validation power. GDT371 varies the untouched validation capacity while
retaining GDT370's generator, 81-candidate search, coefficients, nuisance
heterogeneity, Jeffreys estimates, and `log2(81)` selector cost.

No Voynich source row, annotation, image, or f84 material is eligible.

## Frozen grid

- discovery folios: 4, 6, 8, 10, 12;
- untouched validation folios: 2, 4, 6, 8, 10;
- arrays per folio: 1 or 2;
- cells per array: 6, 9, or 12;
- 256 trials per design/scenario;
- scenarios: null, medium stable (`beta=.9`), medium reversing, and strong
  stable (`beta=1.3`);
- fixed seed: `37120260819`.

The selected predicate must have positive aggregate held gain after the
`log2(81)` selector cost. With more than two held folios, requiring every
single noisy fold to be positive becomes stricter merely because more folds
exist. The fixed transfer criterion is therefore positive raw gain on at least
`ceil(.75 * held_folios)` held folios and never fewer than two.

## Adequacy gate

The smallest adequate design must have:

- medium-stable successful detection at least .80;
- null any-pass rate at most .05; and
- medium-reversing any-pass rate at most .10.

Ties are resolved by total cells, total folios, held cells, arrays per folio,
and cells per array. No threshold may change after the run.

## Claim ceiling

Synthetic prospective acquisition capacity only. This cannot establish a
Voynich association, semantic role, object, word, language, plaintext,
meaning, or translation.
