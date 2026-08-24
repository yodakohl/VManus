# Sidequest Pass 639: combined apprentice examination

## Result

The complete handbook successfully diagnoses and corrects two categorically
different errors:

- a prose process inversion that preserves case identity;
- an Astro copy-order inversion whose labels have no decoded word values.

No new inventory is used.

## Examination A: a new C3 short-hold job

The master dictates:

> After setting the prescribed amount and target, wring out the active extract,
> pour it into the receiver, hold briefly, settle, and close.

The correct six-card strip is:

```text
qokaiin qokal cfhy cphy tshey shedy
```

Back-reading:

| Surface | Card | Short reading |
|---|---|---|
| `qokaiin` | PROC038 | set prescribed amount |
| `qokal` | PROC048 | set target |
| `cfhy` | PROC028 | wring out active item |
| `cphy` | PROC030 | pour active item in |
| `tshey` | PROC122 | hold active item briefly |
| `shedy` | PROC078 | settle; close |

The full order occurs zero times in the source. It is the legal C3 partial order
`M-T-W-P-H-C` with the short-hold substitution.

### Apprentice error

```text
qokaiin qokal cphy cfhy tshey shedy
```

The C3 cue `CFH` is still present in the first five cards, so case selection is
correct. But the work order says pour before wringing. The master swaps only
`cphy cfhy` back to `cfhy cphy`. This demonstrates why case recognition and
process syntax must be checked separately.

## Examination B: f69 left radial slot 28

The registered local label at f69v.31 is:

```text
oar alys
```

The apprentice copies:

```text
alys oar
```

Both whole labels belong to the local celestial exemplar, but both occupy the
wrong registered position. The master restores `oar alys`. No attempt is made
to translate either group as a planet, body part, day, or operation.

## Error taxonomy

| Error | What remains correct | What fails | Correction |
|---|---|---|---|
| prose process inversion | card identities and C3 branch | physical precedence `CFH < P` | reorder two cards |
| Astro copy inversion | namespace, locus, and two local identities | within-locus group order | copy master order |

This is a credible workshop teaching distinction around 1420: one error is a
wrong instruction, the other a wrong exemplar copy.

## Counts

- Prose steps: 6/6 existing cards and surfaces.
- Complete prose source occurrences: 0.
- Branch after injected error: still C3.
- Process error detected: yes.
- Astro groups: 2.
- Wrong Astro positions: 2/2.
- Corrected Astro positions: 2/2.
- New words, cards, surfaces, pages, or Astro labels: 0.

## Next move

Give the same correct C3 instruction to the preparation, bath, and station
desks. Render each card with the currently licensed desk/allograph habits and
measure which differences are merely scribal surface variation. This directly
tests the small multi-scribe workshop premise.

## Files

- `SIX_HUNDRED_THIRTY_NINTH_6_STEP_C3_EXAM.tsv`
- `SIX_HUNDRED_THIRTY_NINTH_3_STAGE_PROSE_CORRECTION.tsv`
- `SIX_HUNDRED_THIRTY_NINTH_6_ROW_ASTRO_COPY_CORRECTION.tsv`
- `SIX_HUNDRED_THIRTY_NINTH_APPRENTICE_EXAM.md`
- `SIX_HUNDRED_THIRTY_NINTH_BUILD_SUMMARY.json`
- `build_six_hundred_thirty_ninth.py`
- `validate_six_hundred_thirty_ninth.py`
