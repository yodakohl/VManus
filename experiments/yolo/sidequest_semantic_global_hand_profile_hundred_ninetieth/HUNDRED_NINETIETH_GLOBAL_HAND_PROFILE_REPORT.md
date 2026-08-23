# Hundred-ninetieth pass: five Hand-C rules on all prose

## What I tried

I treated the first registered surface of each of the 173 exact cards as the
master-shop spelling, then applied the five short Hand-C rules from the previous
round to all 381 observed prose events. Field position was read as ONLY,
INITIAL, MEDIAL or FINAL from the already selected 135-field parse. This is a
workshop reconstruction: the question is whether a small apprentice rule card
can reproduce real surface choices, not whether one spelling is linguistically
original.

## Result

The bare master spelling reproduces 235/381 observed surfaces (61.7%). The five
rules reproduce 258/381 (67.7%), a net gain of 23 exact events. Every generated
surface is already registered for the same exact card, so no new glyph string
was invented.

| rule | triggers | exact | wrong | net over master |
|---|---:|---:|---:|---:|
| q-frame on taught active OK/OT cards | 8 | 7 | 1 | +6 |
| medial/final `daiin` | 14 | 9 | 5 | +7 |
| medial bare `al` | 3 | 1 | 2 | 0 |
| boundary reduction `chor→or`, `cheol→ol` | 3 | 2 | 1 | +2 |
| final s-close `dchedy→schedy`, `cheedy→shedy` | 10 | 9 | 1 | +8 |

Thus four rules transfer positively. The bare-`al` rule remains a valid choice
for the generated Hand C but is not yet a global workshop rule.

## What the 123 residual events say

The residuals form 73 exact transformation-and-position patterns. The largest
are already visibly structured:

- `cheol→ol` medial: 7 events;
- `chdy→chedy` medial: 6, plus 3 initial;
- `okaiin→qokaiin` initial: 6;
- `chey→dy` medial: 4 and `chey→chy` medial: 3;
- `aiin→saiin` initial: 3;
- `cheol→chol` medial and `cheol→sol` initial: 3 each;
- several additional initial q-forms (`qokain`, `qokeey`, `qokal`) recur.

This looks like a second renderer layer with at least three mechanisms: wider
initial q-framing, position-dependent removal or replacement of the che-frame,
and e-grade expansion inside a stable exact card. It does not look like 123 new
words.

## Working decision

Keep the five-rule profile as a useful first apprentice hand, but replace
`BARE_TARGET_MEDIAL` with a more conditional AL rule in the next edition. Next
build a second, still compact layer from the recurrent residual families and
require every added rule to improve the full 381-event reconstruction rather
than merely the 73-token exercise.

Files in this directory bind every event, all five rule audits, all 173 card
accuracies, every residual transformation, the builder and the validator.
