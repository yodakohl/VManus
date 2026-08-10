# LRG005 target-blind joint calibration

Status: `FROZEN_TARGET_FREE_CALIBRATION_V1`

## Future target scores

For a retained exact member-sequence triplet `S` on held physical folio `f`,
future target code will compute from strict confirmed prose outside `f`:

1. `D1_BARE = log((n(D1+S)+0.5)/(n(S)+0.5))`;
2. `D1_OTHER = log((n(D1+S)+0.5)/(n(any one-member extension of S other than D1)+0.5))`.

Both channels must pass.  The second makes generic extendability an explicit
falsifier.  All counts use the complete exact ZL3b/IT2a/RF1b member triplet;
the readings are not replications.  The target remains unopened here.

## Statistic and null

Use the 536-row masked capacity geometry and the exact 68 per-cell role quotas.
For each score channel, calculate label-minus-prose mean within each refined
cell, average cells equally inside each physical folio, then average the 13
folios equally.  Generate 8,192 deterministic assignments by independently
selecting the fixed label quota inside every cell.  The upper p-value is
`(1 + count(null >= observed))/(8192+1)` and null SD is population SD.

Each channel passes only with p <= .01, z >= 3, effect >= .10, at least 10/13
positive folios, B and P equal-folio effects each >= .05, odd and even folio
effects each >= .05, every one-folio deletion >= .05, and maximum absolute
folio contribution <= .25.  LRG005 passes only if both channels pass.

## Synthetic calibration

Use no source group, member sequence, row role, target score, or LRG004 target
row.  Synthetic labels preserve every masked cell quota.  Frozen deterministic
standard-normal score noise is used in 64 null worlds and eight worlds each of:

- `DISTRIBUTED_FULL` and `DISTRIBUTED_HALF`: both channels aligned everywhere;
- `ONE_FOLIO`, `ONE_SECTION`, `ONE_PARITY`: concentrated signal;
- `FOLIO_RANDOM`: independent folio signs;
- `ONE_CHANNEL`: only D1_BARE aligned;
- `OPPOSITE_CHANNEL`: D1_BARE aligned and D1_OTHER reversed;
- `CELL_CONSTANT`: label-blind constants within cells.

Full and half plants must pass 8/8. Null and every adversarial family must pass
0 worlds.  Missing/duplicate rows, quota drift, mixed folio/section cells,
nonfinite values, or changed counts hard-stop.

## Ceiling

A passing calibration may authorize a separately committed/frozen target only
after independent reconstruction.  A target pass could establish an exact
D1-specific cross-register marked/bare construction relation.  It could not
establish a prefix, classifier, morpheme, word, part of speech, sound,
language, cipher operation, English meaning, plaintext, or translation.
