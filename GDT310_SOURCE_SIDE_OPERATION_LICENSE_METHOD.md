# GDT310 — source-side-only operation-license prediction

## Correction target

GDT309 classified complete observed host ecologies, which included occurrences
of the target q/s wrappers.  GDT310 makes the causal question literal: can an
operation's target alternant be predicted using only occurrences of its source
wrapper?

## Frozen panels

Start from the same 58 opaque hosts and GDT303 license labels.  For each
operation, construct predictors only from events with its source wrapper:

- `NONE->q`: `NONE` events;
- `ch->s`: `ch` events;
- `d->s`: `d` events.

Require at least five source-wrapper events on at least three physical folios.
This score-blind threshold retains 52 hosts (31 licensed) for `NONE->q`, 25
(7) for `ch->s`, and 16 (8) for `d->s`.

Use the same frequency, layout, non-wrapper compiler, register, and FULL
feature definitions as GDT309.  Target-wrapper events, wrapper counts, host
identity, host glyphs/substrings, and exact surface identities are forbidden.

## Frozen scorer

Reuse ridge 10, analytic leave-one-host-out prediction, `[.01,.99]` clipping,
and Brier/AUC/AP.  Compare four feature blocks with the source-frequency
baseline.  Permute licenses inside operation-specific source-event-count
quartiles for 8,192 worlds and max-12 correction.

Classify an operation `TARGET_BLIND_LICENSE_PREDICTABLE` only when FULL Brier
gain is positive, FULL AUC is at least .65, and FULL max-12 p is at most .05.

## Claim ceiling

At most this predicts availability of a formal target alternant from source-
side structural ecology.  It does not identify a lexical class, morpheme,
grammar category, meaning, sound, language, plaintext, or translation.  No
f84 row may be opened, parsed, retained, joined, or scored.
