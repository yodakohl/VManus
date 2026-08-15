# GDT125 — Q20 OPEN incremental record-selector test

## Question

Does the compiler profile of a star-defined record's first physical line
(`OPEN`) predict the later BODY after the first BODY line is already known?
This is a sharper discriminator than GDT115: a record selector should retain an
incremental relation to later lines, whereas a shared local texture may be
captured as well or better by the adjacent first BODY line.

## Frozen inventory and splits

- Reuse the 170 Q20 star-defined records and source-native HPR2 parse used by
  GDT114–GDT118.
- Keep only records with at least two BODY lines. This yields 135 records on
  eight physical folios in each alternate reading.
- Hold out one physical folio at a time. ZL3b is primary; IT2a and RF1b are
  alternate readings of the same manuscript, not replications.
- Reject f84r before formal retention. It remains unopened, unqueried,
  unjoined, unscored, untargeted, and unpredicted.

## Models

The target is the anonymous 12-cell compiler distribution of BODY lines two
and later. Every baseline knows record shape, side/order, and the
leave-one-record-out mean target profile of other records on the held page.
Ridge penalty 1000 is inherited from GDT116 and is not tuned here.

The six fixed comparisons are:

1. OPEN compiler added after BODY-line-1 compiler (primary);
2. BODY-line-1 compiler added after OPEN compiler;
3. OPEN raw character trigrams added after BODY-line-1 compiler;
4. BODY-line-1 raw trigrams added after OPEN compiler;
5. OPEN host-edge profile added after BODY-line-1 compiler;
6. BODY-line-1 host-edge profile added after OPEN compiler.

Pseudo-bits are standardized Gaussian squared-error improvements, consistent
with GDT114–GDT121. Complexity is charged by `log2(6)`.

## Controls

For each held fold, permute only the added source profile among records with
the same page and source group count, leaving the baseline channel and target
fixed. Use 4,096 deterministic worlds and a max-six statistic. Report every
held folio and both directions; do not discard one-sided pages or negative
folds.

## Decisions

- `Q20_OPEN_RETAINS_INCREMENTAL_RECORD_SELECTOR_SIGNAL` requires the primary
  model to have positive selector-paid gain, positive gain on at least six of
  eight folios, max-six p <= .05, and positive gain in all three readings.
- `Q20_FIRST_BODY_EXPLAINS_RECORD_SETPOINT` applies when BODY-line-1 is stronger
  and the primary OPEN increment misses those gates.
- Otherwise report `Q20_OPEN_INCREMENTAL_SIGNAL_WEAK_OR_UNSTABLE`.

Even a positive result licenses only a probabilistic record-selector analogy.
It does not make OPEN a title, recipe heading, semantic role, word, morpheme,
POS, sound, language, plaintext, meaning, or translation.
