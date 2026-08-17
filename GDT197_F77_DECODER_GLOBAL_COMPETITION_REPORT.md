# GDT197 — the exposed `ot` + terminal-`y` decoder does not win globally

## Outcome

**TERMINAL_Y_SEQUENCE_SIGNAL_NOT_UNIQUE_OT_AXIS_NOT_SELECTED**

The complete non-`f84*` strict corpus supplies **1,169 complete
physical lines**, **8,641 groups**, and **91 physical folios**.
Each of the three decoder pairs that perfectly fit the exposed f57 N1 labels
was evaluated under identical whole-folio holdout and 4,096 within-line order
worlds.

| decoder | predicates | held gain | bits/group | z | local p | max-three p | z rank | positive folios |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `AL_Y` | `HAS2:al` + `END1:y` | +113.383 | +0.01312 | +6.556 | 0.00024 | 0.00024 | 1 | 68/91 |
| `AL_OT` | `HAS2:al` + `START2:ot` | +50.557 | +0.00585 | +5.491 | 0.00024 | 0.00024 | 3 | 59/91 |
| `Y_OT` | `END1:y` + `START2:ot` | +106.062 | +0.01227 | +6.438 | 0.00024 | 0.00024 | 2 | 62/91 |


The selected `Y_OT` pair is rank **2/3**.  The winner is
`AL_Y`, which replaces the chosen `ot` axis with the equally
perfect local `al` predicate.  The exact numerical order signal is real only
as anonymous surface-state regularity; it does not choose the f77 quality
decoder.  The standardized lead of `AL_Y` over `Y_OT` is only
+0.118; its paired two-sided shuffle tail is **p=0.8943**.
Thus the ranking itself is not a stable preference for `al`; the decisive fact
is that the globally strong order signal fails to distinguish the two.

## Consequence

Terminal `y` remains an unusually useful formal axis because both strongest
global pairs contain it.  What fails is the stronger claim that initial `ot`
is selected as the complementary state coordinate.  The GDT179/GDT180
COLD/DRY/HOT/MOIST display remains an economical local narrative, but global
record ordering does not disambiguate it from the alternative shallow
decoder already exposed by GDT182.

No state is assigned a quality, word, sound, language, plaintext value, or
meaning.  `f84r` and all other `f84*` rows were rejected before retention and
scoring.
