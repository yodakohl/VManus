# GDT434 — executable 49-card intake reader

## Result

The future deck is now a working reader rather than a stack of prediction
tables. One exact component recipe goes in; one explicitly ranked result comes
out.

The complete intake catalog has 1,563 different recipe keys:

- 1,268 already observed recipes;
- four high-priority future cards;
- 43 strong future cards;
- two weaker second-ring Amber-II cards;
- 246 narrow lookup cards.

Only the middle 49 belong to the main future deck. Their five-register pocket
sheet has 245 readings. The 246 narrow recipes remain a separate appendix and
cannot be accepted automatically.

## What the command does

For `AL+AIN` in the Biological register, the reader returns the high-priority
card and the local phrase “An der Zielstation: Stationsanteil.” For the weaker
`AIR+AIN`, it returns the second-ring reading “Entlang der Positionsbahn:
Sektoranteil.” For narrow `AIR+OR`, it warns that only the exact recipe key
licenses the lookup. For an unlisted composition such as `AIIN+AIN+S+Y`, it
shows the known atom trace and stops: known pieces do not automatically make a
known card.

Observed recipes always win over predictions. When the requested register has
a real observed clause, the reader returns that clause. When the recipe exists
elsewhere but not in that register, it says plainly that the local wording is
only a counterfactual expansion.

## Why exact matching matters

Four collision groups—eight recipes total—in the narrow appendix produce the
same short German wording despite different component order. Examples include
`CH+OT+AIIN` versus `OT+CH+AIIN` and `L+T+Y` versus `Y+T+L`. This is useful: it
proves that fluent wording is not a safe identifier. The matcher therefore
never searches by translation and never silently swaps component order.

## Validation

All 27 checks pass. The tier counts are exact and pairwise disjoint, every main
card has five register readings, all 49 generic main phrases and all 245
register-local main phrases are collision-free, and eight end-to-end tests hit
their intended tiers. Both T5 probes stop. A deterministic rebuild is
byte-identical.

## Boundary

This tool reads an already segmented component recipe. It does not discover
the segmentation of a new surface, invent a Voynich spelling, add a component
meaning, or open another page. It is the intake gate to use when later pages
are eventually admitted.
