# Sidequest Pass 634: compatible existing-card substitutions

## Result

One controlled semantic slot per case expands the five base jobs into eleven
distinct workshop jobs and 49 legal written orders. Every replacement is an
already attested surface that uniquely identifies an existing exact card.

This is the first capacity estimate that changes the requested work rather than
merely changing card order.

## Five controlled slots

| Case | Slot | Existing choices | Jobs | Written orders |
|---|---|---|---:|---:|
| C1 | open hold grade | `shey` long / `tshey` short | 2 | 16 |
| C2 | application-close grade | `qokedy` short / `qokeedy` long / `qokeeedy` full | 3 | 15 |
| C3 | open hold grade | `shey` long / `tshey` short | 2 | 12 |
| C4 | quantity opening | `qokaiin` prescribed amount / `qokain` portion | 2 | 2 |
| C5 | ingredient quantity | `qokaiin` prescribed amount / `qokain` portion | 2 | 4 |

The count is `2 + 3 + 2 + 2 + 2 = 11` semantic jobs. Applying the Pass-633
partial-order grammar gives `16 + 15 + 12 + 2 + 4 = 49` written orders.

## Six new minimal job contrasts

Relative to the five bases, the deck can now ask for:

1. a short rather than long C1 hold;
2. a long rather than full C2 application-close;
3. a short rather than full C2 application-close;
4. a short rather than long C3 hold;
5. a repeated portion sequence rather than prescribed amount plus portion in C4;
6. a portion rather than prescribed amount for the C5 ingredient.

Each contrast changes exactly one card family and preserves the branch cue and
all process arrows.

## The important low-confidence case

The C4 substitution produces:

```text
qokain qokain ykan qokal qokylddy talam
PORTION / PORTION / NACHPORTION / ZIEL / BEFESTIGEN-SCHLUSS / VERWAHREN
```

The current creative reading treats exact repetition as two set portions. It
does not infer a hidden numeral or grammatical dual. If workshop repetition is
only emphasis, C4-DOUBLE-PORTION is removed and capacity becomes ten jobs in 48
orders. All other substitutions remain unaffected.

## Counts

- Controlled slots: 5.
- Base jobs: 5.
- New job variants: 6.
- Total semantic jobs: 11.
- Legal written orders: 49, all distinct.
- Correct branch selections: 49/49.
- Complete source occurrences: 0/49.
- Exact backward readings: 294/294 cards.
- New words, cards, surfaces, pages, or Astro labels: 0.

## What this says about the writing system

The most economical current model has true small paradigms inside a larger
learned deck. An apprentice need not memorize three unrelated closure cards:

```text
qokedy    short application; close
qokeedy   long application; close
qokeeedy  full application; close
```

Likewise `tshey / shey` changes the open holding grade and `qokain / qokaiin`
changes portion versus prescribed amount. These are exactly the kinds of
predictable compositions the historical mixed-abbreviation/codebook analogy
was sought to explain.

## Next move

Extract every similarly clean two- or three-member paradigm from the existing
173-card deck. Keep only families in which one component changes one short
semantic dimension. That gives the apprentice a productive substitution table
and prevents sentence-sized whole-card glosses from returning.

## Files

- `SIX_HUNDRED_THIRTY_FOURTH_11_JOB_SUBSTITUTIONS.tsv`
- `SIX_HUNDRED_THIRTY_FOURTH_49_LEGAL_WRITTEN_ORDERS.tsv`
- `SIX_HUNDRED_THIRTY_FOURTH_294_STEP_BACKWARD_READ.tsv`
- `SIX_HUNDRED_THIRTY_FOURTH_SUBSTITUTION_EXERCISE.md`
- `SIX_HUNDRED_THIRTY_FOURTH_BUILD_SUMMARY.json`
- `build_six_hundred_thirty_fourth.py`
- `validate_six_hundred_thirty_fourth.py`
