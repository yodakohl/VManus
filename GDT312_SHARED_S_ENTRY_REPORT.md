# GDT312 — shared `s` entry-rule compression

Status: **SHARED_S_LINE_ENTRY_RULE_POSTHOC**.

This is an explicitly post-hoc decomposition of the exposed GDT311 result. Seven exact `ch/d/s` triads are represented once each; shared `s` events are not duplicated.

The exact-triad baseline costs 0.574358 held bits/event. Adding physical line start plus preceding DY lowers this to 0.513878, a gain of +0.060480 bits/event (null-centered +0.045485; max-three p 0.000122055413).

On held folios, `s` occurs in 43.3% of line-start events versus 7.6% elsewhere; the exact triad/register-matched delta is +0.284. The corresponding preceding-DY delta is -0.062.

The compact rule is therefore `licensed {ch,d,s} triad + physical line entry -> increased probability of s`. It is not a deterministic rewrite and does not generalize the triad license.

## Claim ceiling

A post-hoc stochastic physical-entry renderer on seven known exact triads only; no morpheme POS meaning sound language plaintext translation or f84 result.
