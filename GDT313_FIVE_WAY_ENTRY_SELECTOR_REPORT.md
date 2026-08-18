# GDT313 — five-way entry-state selector

Status: **FIVE_WAY_ENTRY_STATE_SELECTOR_TRANSFERS**.

Two exact opaque cells contain every `{NONE,ch,d,s,q}` surface choice. The training-only model compares those choices directly without duplicating an `s` event.

The exact-cell prior costs 1.997650 held bits/event. Adding physical line start and preceding DY changes this by +0.067663 bits/event (null-centered +0.054717; max-three p 0.000122055413).

For `s × LINE_START`, the training logit coefficient is +0.315 and the held cell/register-matched delta is +0.297. For `q × PREV_DY`, they are +0.491 and +0.199.

The same opaque opportunities therefore choose `s` preferentially at physical line entry and `q` preferentially after a DY boundary. `NONE`, `ch`, and `d` remain the residual alternatives. This is probabilistic, not deterministic.

## Claim ceiling

Five-way stochastic formal selector in two known exact opaque cells only; no unseen cell morphology category meaning sound language plaintext or translation. No f84 row was opened, parsed, retained, joined, or scored.
