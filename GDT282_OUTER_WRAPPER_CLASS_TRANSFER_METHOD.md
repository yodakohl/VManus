# GDT282 — outer-wrapper class transfer

## Question

GDT281 established a collision-free profile distinction: authentic diplomatic
Latin is `RIGHT_FAMILY`-led, while Voynich is `OUTER_WRAPPER`-led.  GDT282 asks
whether that Voynich direction is a reusable wrapper-class channel across
folios, sections and hands, or merely wrapper presence, q frequency, or one
register.

This is a formal character-prediction test.  It assigns no wrapper function,
sound, word, morphology, language, meaning, plaintext, or translation.

## Frozen data and base

Freeze GDT281 byte-for-byte.  Use only its f84-free native panels for:

- `VOYNICH_REFERENCE` (primary);
- the three native-positive Latin panels (calibration only).

The exact-context base contains opportunity, closure/boundary, local frame,
right family and display renderer.  It excludes wrapper and q.  The target is
PAGE_HOST character form under the unchanged hierarchical predictor.

## Frozen wrapper models

Score exactly these five categorical contexts:

1. `BASE_NO_WRAPPER`;
2. `WRAPPER_PRESENCE` (`NONE` versus any wrapper);
3. `Q_BINARY` (`q` versus all other states);
4. `FULL_WRAPPER_IDENTITY` (the frozen wrapper class);
5. `FULL_WRAPPER_PLUS_Q_REDUNDANCY`.

In the frozen Voynich parser, `q_flag=1` if and only if `wrapper=q`.
Consequently model 5 must be exactly equivalent to model 4 under exact tuple
keys.  This is an integrity check and means q cannot be credited as an
independent dimension merely because it appeared twice in the old hashed key.

For each of the eight wrapper classes, also score a fixed ablation that merges
that class into `OTHER_WRAPPER` while preserving `NONE`.  Ablations are
descriptive and nonadditive.

## Transfer

Use the same exact categorical character scorer in three fixed regimes:

- held physical folio, with the parser/alphabet relearned without that folio;
- held section (`B,C,H,P,S,T`) on the published frozen representation;
- held powered hand (`1,2,3,5`; hand `@` is descriptive because it has fewer
  than 100 events).

Each regime compares wrapper models against its own no-wrapper base.  Report
total bits/event, every held-stratum contribution, and signs.  A q-only model
is a diagnostic, not a claim that q has a linguistic function.

The 64 inherited GDT276 permutations are reused for the published native
overall score.  Wrapper states are permuted by the inherited source indices;
the base fields remain attached to their observed events.  These nulls quantify
the exposed association and are not new independent evidence.

## Frozen decision

Report `OUTER_WRAPPER_IDENTITY_TRANSFERS_ACROSS_REGISTERS` only if all are true:

1. `FULL_WRAPPER_IDENTITY` improves over base in held-folio, held-section and
   held-powered-hand totals;
2. it improves over `WRAPPER_PRESENCE` in all three regimes;
3. at least four of six held sections and three of four powered hands have
   positive full-wrapper gains;
4. the exact `FULL_WRAPPER_PLUS_Q_REDUNDANCY` score equals full wrapper within
   `1e-10` bits in every published and safe folio score.

Otherwise report `OUTER_WRAPPER_SIGNAL_REGISTER_LOCAL_OR_NONIDENTIFIABLE`.
This decision ranks a formal channel only; it does not promote a semantic or
linguistic wrapper interpretation.

## Seal

No PAGE_HOST substring is mined.  No new corpus, annotation, threshold, or
semantic field is added.  No f84 row may be opened, parsed, retained, joined,
or scored.
