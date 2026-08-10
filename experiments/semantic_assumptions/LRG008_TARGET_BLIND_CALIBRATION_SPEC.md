# LRG008 target-blind diagram-role calibration

Status: `FROZEN_TARGET_BLIND_SYNTHETIC_V1`.

The real source-native sequences, reconstructed LRG001 profiles, and their
scores on the LRG008 panel remain unopened. Calibration expands only the 40
capacity-cell metadata records and their fixed label quotas.

## Statistic

For a supplied scalar score, assign average ranks from 0 to 1 separately
inside each exact `(page, symbol_count)` cell. Ties receive their mean rank.
Within a cell compute mean rank in the designated label state minus mean rank
in the diagram state. Average cells within pages, pages within physical
folios, and folios equally.

Use 8,192 deterministic unique fixed-quota assignments generated with NumPy
PCG64 seed `80082026`. Each assignment independently selects the frozen number
of label states inside every cell. The one-sided plus-one p-value is
`(1 + count(null >= observed - 1e-15)) / 8193`. Population null SD defines
`z = (observed - mean(null)) / SD(null)`.

Also compute equal-hierarchy effects by diagnostic role (`C` and `R`), section
(`A`, `C`, `Z`), and target-folio parity; six equal-folio effects; every
leave-one-folio-out mean; and maximum absolute folio concentration.

All target gates are fixed now:

- effect >= .15, p <= .01, and z >= 3;
- both diagnostic-role effects >= .10;
- every section effect >= .08;
- both parity effects >= .08;
- at least five of six folio effects are positive;
- every leave-one-folio-out effect >= .10; and
- concentration <= .35.

## Synthetic worlds

Every world uses an independently randomized exact-quota label vector and
Gaussian noise. Positive scores add `amplitude * (2*label-1)` everywhere:
eight `DISTRIBUTED_FULL` worlds at amplitude .60 and eight
`DISTRIBUTED_REDUCED` worlds at .35. The calibration must pass all sixteen.

It must pass none of 64 `NULL` worlds and none of eight worlds in each of:
`ONE_FOLIO`, `ONE_ROLE`, `ONE_SECTION`, `ONE_PARITY`, `ONE_PAGE`,
`FOLIO_RANDOM_SIGN`, `PAGE_ONLY`, `LENGTH_ONLY`, and `REVERSED`. Adversarial
signal amplitude is .60 except metadata-only controls, which use offsets plus
noise. World seeds and exact generation are frozen in the runner and must be
independently reconstructed.

Malformed quota, nonfinite score, reordered geometry, duplicate assignment,
and score-constant controls must hard fail. Positive affine score transforms
and row serialization followed by exact ID restoration must preserve every
rank, statistic, gate, and decision.

Calibration passes only with 0/64 null, 8/8 in both positive families, 0/8 in
all nine negative families, every integrity/invariance control, and target
absence before and after. A pass authorizes a separately committed and
hash-frozen one-time aggregate projection only. It supplies no manuscript
association, identifier, name, noun, owner, object, word, sound, language,
meaning, plaintext, or translation.
