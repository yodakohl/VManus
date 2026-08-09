# Source-native within-group local-transition increment

Status: **REGISTERED_TARGET_UNOPENED**

## Distinct question

The source-boundary pair model predicts separator support, the edge grammar
predicts first versus last source groups in a locus, and the latest stage tests
measure marginal family distributions by relative position. None asks whether
one family predicts the next *inside the same complete source group* after the
confirmed positional distribution is already fixed.

Use the 21,899-row complete-group masked panel and its frozen physical-folio
TRAIN/CAL/TEST split. The target remains the official complete STA-family
sequence; no legacy word, root, role, or member code is used.

## Models

Both models condition on Currier, exact complete-group length 1--11, and the
fixed five-bin position `min(4,floor(5*j/L))`, with symmetric Dirichlet alpha
.5.

- `POSITION_5`: family distribution by `(Currier,length,bin)`.
- `POSITION_5_PLUS_PREVIOUS`: additionally condition on the immediately
  previous family, using a separate START state at position zero.

Fit on 10,753 TRAIN groups. CAL is used only as a required direction check:
the transition model must have positive total CAL log gain per symbol. Score
the unchanged transition-minus-position gain on 5,630 TEST groups.

## Frozen target gate

Aggregate each group gain by physical folio per symbol, then weight folios
equally. `MARKOV_INCREMENT_PASS` requires:

- positive CAL gain; exact 5,630 TEST groups / 24 folios;
- TEST equal-folio gain >=.01 nat/symbol, >=18 positive folios, sign p<=.01,
  positive minimum deletion, and maximum contribution <=.15;
- at least 500 exact `(Currier,length,complete sequence)` surfaces unseen in
  TRAIN, with gain >=.005 and positive minimum deletion;
- Currier A and B each gain >=.003, have positive minimum deletion, and >=65%
  positive folios.

The target must pass in manuscript and completely reversed group order.

## Target-free calibration

Masked geometry generates 64 strong `POSITION_ONLY` worlds, eight
manuscript-wide `MARKOV` worlds at strength .45, and eight each of B-only
`CURRIER_ONE`, `ONE_FOLIO`, and independently mapped `FOLIO_RANDOM` controls.
Every world is scored forward and reversed. Require <=1/64 position-only false
passes in each direction; >=7/8 Markov passes; zero passes for every adversary;
identical 96-world reversal decisions; 24-label relabeling invariance within
1e-10; finite values; exact capacity; mutations; target isolation; and absent
target outputs. Use 32 workers and one numeric thread per process.

Frozen inputs:

- masked panel `16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5`;
- capacity validation `2a95ce3183b72540f39a8ef0f68129d1f7ccf2e688683a9f2989360f84c20007`;
- model core `8bc3020e69bea9f50854fd1b512a327bb9322a513000e13f267bb65315fd787e`.

A pass establishes only a transferable first-order family dependency inside
complete source groups beyond length, position, Currier, and folio. It does not
identify syntax, a prefix, root, suffix, sound, word, part of speech, language,
cipher operation, meaning, plaintext, or translation.
