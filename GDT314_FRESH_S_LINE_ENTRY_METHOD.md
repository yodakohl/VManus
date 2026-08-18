# GDT314 — fresh-surface `s` line-entry generalization

Exclude every exact surface used by a GDT303 `ch->s` or `d->s` pair.  On the
remaining corpus, freeze every exact opaque
`PAGE_HOST × frame × inner-D × right × DY × B3` cell with at least two `s`
and two non-`s` events, each class occurring on at least two physical folios.
This score-blind rule yields 15 cells, 344 events, 35 `s` choices, and 78
folios.  None of these surfaces contributed to GDT311--313.

In leave-one-physical-folio-out folds, compare ridge-10 logistic exact-cell
priors against exact cell plus the physical `LINE_START` indicator.  Report
held log2 loss, fold coefficient direction, folio and section contributions,
and a fixed-prediction cell/register label-alignment diagnostic over 8,192
worlds.  The latter is diagnostic rather than an exact retrained null because
cross-fitted predictions share training outcomes.

Call `S_LINE_ENTRY_EXTENDS_TO_FRESH_SURFACES` only if held gain is positive,
the held exact-cell/register-matched line-start delta is positive, at least 60
of 78 fold coefficients are positive, at least two of the three powered
sections B/H/S contribute positive held gain, and the alignment diagnostic is
at most .05.

At most this establishes an `s`-choice physical-line-entry tendency across
new exact formal cells.  It assigns no morpheme, POS, meaning, sound, language,
plaintext, or translation.  No f84 row may be opened, parsed, retained,
joined, or scored.
