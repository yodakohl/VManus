# F69C001 target implementation freeze

Status: **TARGET BOUND — SCORES UNOPENED**

This addendum fixes implementation details left implicit by
`METHOD_FREEZE.md`. It changes no registered model, threshold, or claim. It is
committed before any target score is calculated.

## Manual target binding

The existing human clock-position annotations define this clockwise cycle:

| Indexing slot | Locus | Position | ZL3b | IT2a | RF1b |
|---:|---|---|---|---|---|
| 1 | f69r.45 | 11:30 | `d` | `d` | `d` |
| 2 | f69r.46 | 01:00 | `o` | `o` | `o` |
| 3 | f69r.47 | 03:00 | `l` | `l` | `l` |
| 4 | f69r.48 | 04:30 | `s` | `s` | `s` |
| 5 | f69r.49 | 07:30 | `ed` | `em` | `ed` |
| 6 | f69r.44 | 10:30 | `y` | `y` | `y` |

Slot 1 is only a reproducible array index. Because rotations and reversals are
quotiented, it is not a proposed start or orientation. ZL3b/RF1b and IT2a
retain their alternate readings in the same physical slot.

The bindings must be read directly from the three cached manual source files,
and each locus must contain exactly one lowercase word equal to this table.
The human annotation table must independently supply the listed clock order.
Any mismatch stops the target without a score.

## Score details

- Use the registered fixed alphabet, add-0.5 order-2 model, prose-only corpus,
  f69 exclusion, and complete candidate-surface exclusion.
- Within a reading, standardize the 720 orientation scores by their arithmetic
  mean and population standard deviation. The sample/population choice cannot
  change a rank here because every reading has the same 720 orientations, but
  population standard deviation is fixed for exact reproducibility.
- Combine a common labeled orientation by the minimum of its ZL3b, IT2a, and
  RF1b z-scores. The corresponding orbit score is the maximum of its 12
  orientations. Use the registered tie-inclusive rank.
- Do not emit a preferred orientation or candidate joined surface. Only orbit
  ranks, score digests, gates, and the exact input binding may be published.

## Leave-one-chunk-out tests

For each of the six physical slots, delete that slot in all readings and retain
the clockwise order of the five survivors. Score all `5! = 120` assignments,
quotient them into 12 dihedral orbits of 10 orientations, standardize within
reading, and combine by minimum z-score then maximum orientation exactly as in
the primary test. Candidate-surface exclusion is recomputed for that deletion.
The registered gate remains: at least five target ranks at most 2 of 12 and no
rank worse than 4 of 12.

## Frozen negative fixtures

1. **Misaligned-reading fixture:** cyclically assign the IT2a surface from
   physical slot `i+1 mod 6` to slot `i`, while leaving ZL3b and RF1b fixed.
   Recompute all IT2a scores and the three-reading combined orbit table. The
   fixture rejects only if the physical target orbit has inclusive rank worse
   than 1 of 60.
2. **Deterministic non-target-orbit fixture:** sort all 60 canonical six-slot
   orbits lexicographically, remove the physical target orbit, and select index
   `SHA256("F69C001|random-orbit-fixture|v1")[0:8] mod 59`. It rejects only if
   that selected orbit has inclusive rank worse than 1 in the actual combined
   target table.

Both fixtures must reject. They are veto controls, not alternative targets.

## Decision and validation

The first target runner may report only `COMPUTATIONAL_GATES_PASS_PENDING_`
`VALIDATION` or `TARGET_NONCONFIRMATION`. It must write exactly one target JSON
artifact and a compact report. A separate nonimporting implementation must
reparse the manual sources and annotations and reproduce source hashes,
bindings, all primary and deletion scores, orbit ranks, fixtures, gates, and
decision. Only a complete independent pass may upgrade the first status to a
provisional structural result.

No outcome establishes a start, handedness, sound, word, root, lexeme,
language, plaintext, direction name, or translation.
