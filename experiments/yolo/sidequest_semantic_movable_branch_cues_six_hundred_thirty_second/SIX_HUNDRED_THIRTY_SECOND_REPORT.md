# Sidequest Pass 632: movable branch cues versus process order

## Result

The five branch cues are not all the same kind of word. Moving each one through
positions 1--5 of its six-card exercise leaves the case selector correct in all
25 variants, but only 11 variants retain a sensible workshop order.

This gives the working grammar a useful distinction:

- a state/check card can behave like a movable rubric;
- a work compartment or ingredient can move only within the early address zone;
- an irreversible operation or ordered quantity remains bound to its place in
  the process.

## Mobility map

| Case | Cue | Working value | Licensed positions | Reading |
|---|---|---|---|---|
| C1 | `os` | ARBEITSFACH | 1, 2 | The compartment may head the strip or follow the amount, but must precede washing. |
| C2 | `cthy` | BEREIT | 1--5 | A readiness check may occur anywhere before the full close. |
| C3 | `cfhy` | AUSWRINGEN | 1 only | Wringing must precede pouring into the next vessel. |
| C4 | `ykan` | NACHPORTION | 3 only | The subsequent portion must follow the first portion and precede the target. |
| C5 | `cho` | ZUTAT | 1, 2 | The first ingredient may precede or follow its amount, but must precede the further stock ingredient. |

The original five Pass-631 orders account for five of the eleven licensed
variants. Six additional orders are generated without a new word, card, or
surface: one each for C1 and C5 and four alternate placements of the C2 ready
check.

## Why all 25 still select correctly

The selector reads a branch signature, not the full syntax. Every cue remains
inside the first five cards. C2 retains three distinct `CTH`-bearing cards even
when bare `cthy` moves. Therefore the branch remains recognizable even in a
badly ordered exercise.

That is a plausible teaching feature: an apprentice can choose the right form
but still put a step in the wrong place. The master can diagnose those as two
different errors.

## Process constraints exposed by the bad variants

- C3 becomes physically backwards when `cfhy` follows `cphy`: it says to pour
  the item in before wringing it out.
- C4 loses the quantity chain when `ykan` precedes `qokain`, and it becomes a
  late addition when placed after the target or fastening step.
- C5 becomes anaphorically odd when the first ingredient follows the explicitly
  further ingredient.
- C1 loses its early compartment address when `os` follows the wash operation.
- C2 remains workable because `cthy` is a state checkpoint rather than a
  material transformation.

These are creative workshop readings, but they are more disciplined than
allowing every card order to mean anything.

## Counts

- Cases: 5.
- Cue-position variants: 25.
- Exact backward-read steps: 150/150.
- Correct case selections: 25/25.
- Semantically licensed variants: 11/25.
- Newly licensed orders beyond Pass 631: 6.
- Six-card variants found verbatim in the source: 0/25.
- New words, cards, surfaces, pages, or Astro labels: 0.

## Revised apprentice rule

Read the strip in two passes:

1. Choose the case from the early branch signature.
2. Check irreversible precedence: source before further source, portion before
   subsequent portion, extraction before transfer, and work address before the
   addressed operation.

Only then execute dose/address/operation/state/close. This turns the current
deck into a small fault-detecting teaching system rather than a bag of flexible
glosses.

## Next move

Compress the eleven licensed variants into an explicit finite construction
grammar and use it to enumerate all legal six-step apprentice orders from the
same cards. Keep the inventory fixed. The useful question is how many distinct
instructions the present deck generates before meanings become incoherent.

## Files

- `SIX_HUNDRED_THIRTY_SECOND_25_CUE_POSITION_VARIANTS.tsv`
- `SIX_HUNDRED_THIRTY_SECOND_150_STEP_BACKWARD_READ.tsv`
- `SIX_HUNDRED_THIRTY_SECOND_5_CUE_MOBILITY_SUMMARY.tsv`
- `SIX_HUNDRED_THIRTY_SECOND_MOVABLE_CUE_EXERCISE.md`
- `SIX_HUNDRED_THIRTY_SECOND_BUILD_SUMMARY.json`
- `build_six_hundred_thirty_second.py`
- `validate_six_hundred_thirty_second.py`
