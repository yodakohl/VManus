# F77r quality-state transition bridge design

## Exposure

This construction was discovered **post hoc** after the f57 quality-position
code, f77v cold-position form lead, and f77r top-tube strings were visible. It
is not a preregistered confirmation and receives no inferential p-value. The
exact nulls below measure combinatorial specificity only.

## Inputs fixed for reconstruction

The previously retained f57v N1 page-role rendering maps the two structural
bits `starts-ot,terminal-y` as follows:

| Bits | f57 page-role state |
|---|---|
| `10` | HOT |
| `01` | MOIST |
| `00` | COLD |
| `11` | DRY |

These are source-homology positions, not translations of `ot` or `y`.

Human annotations independently order six labels in the six tube segments
between the left end, five side openings, and right end of the f77r top tube.
The cached page annotation says four openings eject material. Human visual QC
against the official Yale witness fixes the four flanking side openings as
emitting and the central side opening as non-emitting. This QC records only
author-visible topology; it assigns no element or temperature.

## Fixed descriptive gates

1. All three manual readings must give the same six structural states.
2. Across all five internal boundaries, emission must occur if and only if
   the adjacent segment states differ.
3. The four emitting boundaries must instantiate exactly once each of the
   classical adjacent primary-quality pairs: COLD+DRY, DRY+HOT, HOT+MOIST,
   and MOIST+COLD.
4. The non-emitting central boundary must join identical states.

Enumerate all 4^6 state sequences and all distinct permutations of the
observed state multiset across the fixed six positions. Also audit every
stable consecutive six-label window in a human-annotated unit under both the
complete classical-pair gate and a broader control that requires only four
distinct changed-state pairs around the same non-changing centre. These are
prevalence controls, not semantic tests.

The cached human visual proposal that the four puffs run left-to-right AIR,
WATER, FIRE, EARTH must be reported as an external semantic cross-check, not
used to select or rotate the result.

## Decision ceiling

A pass retains only a provisional cross-page four-state transition
construction: f57-derived states explain f77r emission versus non-emission
topology and form the complete classical quality-pair cycle. It does not prove
that the labels name qualities, that the puffs name elements, or that `ot` and
`y` mean HOT/DRY/change. Confirmation requires a second independently
annotated segmented system frozen before opening its Voynich strings.
