# GDT309 — opaque-host operation-license prediction

## Question

Can the sparse GDT303/GDT308 operation compatibility table be compressed, or
is it an opaque host exception list?

## Frozen universe and labels

Use f84-free `VOYNICH_REFERENCE` events on lines with at least two groups.
The host universe contains every opaque `PAGE_HOST` having at least two exact
surface forms, where each form has at least five events on at least three
physical folios.  For each host, the three binary labels are presence of a
published GDT303 pair for `ch->s`, `d->s`, and `NONE->q`.

## Predictors

Exact host identity, host glyphs/substrings, wrapper values/counts, and exact
surface identities are forbidden predictors.  Freeze host-level summaries:

- `FREQUENCY`: log event and folio count;
- `LAYOUT`: frequency plus physical line role, HPR2 field boundary,
  record-1, and normalized line-position summaries;
- `COMPILER`: frequency plus inner-D, local O/OT frame, right presence, DY,
  B3, line-close, and paragraph-close rates;
- `REGISTER`: frequency plus section/register/Currier/hand proportions;
- `FULL`: the union of all allowed features.

## Frozen score and null

Use one fixed ridge-10 linear-probability model and analytic leave-one-host-out
predictions, clipped to `[0.01, 0.99]` before every Brier/AUC/AP score.  For each operation and each of
`LAYOUT`, `COMPILER`, `REGISTER`, and `FULL`, report Brier improvement over
`FREQUENCY`, ROC AUC, and average precision.

The null permutes operation-license labels within frozen host-event-count
quartiles, refits all twelve tests, and uses 8,192 worlds with max-12
correction.  An operation license is `STRUCTURALLY_PREDICTABLE` only when FULL
Brier gain is positive, FULL AUC is at least .65, and FULL max-12 p is at most
.05.  Otherwise it is `OPAQUE_OR_UNRESOLVED_LICENSE`.

## Claim ceiling

At most this identifies a low-complexity structural ecology for operation
licensing.  It does not establish a lexical class, morpheme, grammar category,
meaning, sound, language, plaintext, or translation.  No f84 row may be
opened, parsed, retained, joined, or scored.
