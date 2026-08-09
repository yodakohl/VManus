# Exact-position-controlled within-group transition increment

Status: **REGISTERED_TARGET_UNOPENED**

## Confound correction

The confirmed coarse-bin Markov increment legitimately establishes dependency
beyond five position bins, but its START context can isolate the exact first
family inside a multi-symbol bin. It therefore does not yet prove that a real
previous-family context adds information beyond every exact ordinal position.

This new test removes that loophole. Use only positions `j>=1`, so every scored
symbol has an observed previous family. Both baseline and full model condition
on Currier, exact complete-group length, and exact zero-based ordinal position.
The full model alone additionally conditions on family at `j-1`. Symmetric
Dirichlet alpha is .5.

The frozen panel yields 10,513 TRAIN / 5,412 CAL / 5,521 TEST groups of length
at least two and 32,773 / 17,105 / 17,435 scored transition symbols on
47/23/24 physical folios. Groups of length one contribute no fit or score.

## Gate

Fit TRAIN. Require positive CAL full-minus-baseline gain. On TEST require exact
capacity; equal-folio gain >=.005 nat/transition-symbol; >=18 positive folios;
sign p<=.01; positive minimum deletion; max contribution <=.15; at least 500
exact complete sequences unseen in TRAIN with gain >=.003 and positive minimum
deletion; and both Currier registers with gain >=.002, positive minimum
deletion, and >=65% positive folios. Both manuscript and fully reversed group
orders must independently pass.

## Target-free controls

On masked geometry run, in both orientations, 64 exact-ordinal
`POSITION_ONLY` worlds, eight manuscript-wide `MARKOV` worlds at strength .45,
and eight each B-only `CURRIER_ONE`, `ONE_FOLIO`, and independently mapped
`FOLIO_RANDOM` worlds. Require <=1/64 false passes, >=7/8 Markov passes, zero
adversarial passes, all 96 reversal decisions identical, 24-label invariance
within 1e-10, finite values, exact capacity, mutation rejection, target
isolation, and absent target outputs.

Frozen inputs are the masked panel
`16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5`
and capacity validation
`2a95ce3183b72540f39a8ef0f68129d1f7ccf2e688683a9f2989360f84c20007`.
The model core is frozen as
`269d0167fb13930386eaba2398a47578c54a897bcb74f0b9b1da8c57f4d1a892`.

A pass establishes only first-order dependency beyond exact ordinal position,
length, Currier, and folio. It does not establish syntax, morphology, sound,
word, language, cipher operation, meaning, plaintext, or translation.
