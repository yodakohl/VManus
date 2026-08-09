# SCP001 target implementation freeze

Frozen before target invocation on 2026-08-09.

## Bound artifacts

- target runner:
  `0f495ac904f7ff2cbabdbc63645376ad4c13fb403f194b8f983aa5437d76d59c`
- source phase binding:
  `535e34dcbef6ce3f34b61d8f8d990ce02152c844a8ef4acbfd3dd5063b13697e`
- anonymous feature matrix:
  `e6f7a83cc6816d2c811e27753cca92b2257c35b919e38e55e377501ea4bd5204`
- anonymous control result:
  `614bde4a4a145b345337b105daa62a069a9392e7386127048eedfe733b56495c`
- independent prescore audit:
  `9dc70b8fc4df1b867e9ec255612767ceef2576f0d08c2499375d7d7ce377620e`
- frozen scoring engine:
  `670530f4b2a144ea35cb1b9eeafd37677ef3a458e712ed330be82a10cd88d615`

The target runner hard-fails on any change to all five input/engine hashes.
It also requires the 19/19 anonymous-control pass, the 21/21 independent
prescore pass, and absence of both target artifacts.

## Single authorized invocation

The runner may read only the frozen `first_color` page phase and invoke the
already registered exact 512-assignment score once. It must emit all 15
eligible feature rows, exact raw and family tails, normal- and reversed-phase
effects, all physical-folio deletions, the family-orbit digest, final gates,
and the result decision. A separate nonimporting validator is mandatory.

No retry, threshold change, feature change, page change, phase change,
alternate weighting, subset, reading selection, or null change is permitted.

Any outcome is limited to a marker-color-conditioned formal construction on
this panel. No color meaning, recipe class, number, word, lexeme, plaintext,
language, or translation follows.
