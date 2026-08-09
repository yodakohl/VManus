# F67v1 dual-topology transfer falsifier

## Exposure and fixed rule

This is a post-hoc transfer falsifier run after the f77r construction was
known. Before inspecting the f67v1 radial state sequence, the rule was fixed:

> If the f77r relation “graphical output exists iff adjacent f57-derived
> states differ” is universal under the natural boundary/sector dual, every
> star-bearing f67v1 sector must lie between different radial-text states.

The human source orders 17 outward radial texts clockwise from the double ray.
Every intervening sector contains at least one star. Treat each complete radial
text as one boundary state using the unchanged f57 bits `starts-ot,terminal-y`.
The last radial text is cyclically adjacent to the first. Do not use the exact
1–4 star counts, tune a threshold, rotate the source order, select a subset, or
reinterpret a multiword line after seeing its state.

## Decision

The universal dual-topology rule passes only if all 17 cyclic adjacent pairs
differ in ZL3b, IT2a, and RF1b. Failure rejects that universal extension but
does not refute the narrower f77r short-label/segment construction.
