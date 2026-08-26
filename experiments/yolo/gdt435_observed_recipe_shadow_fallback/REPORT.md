# GDT435 — the card reader needs state, not guesswork

## The useful correction

The 49-card deck survives unchanged. The first command around it did not.

GDT434 correctly matched exact component recipes, but for an already observed
recipe it printed the first clause found in the requested register. That is too
eager. The same card can inherit a different active verb or object from its
left-hand context.

Across 4,576 events there are 1,766 recipe+register keys. Of these, 276 keys
covering 2,162 events have more than one full clause. Blindly choosing the first
one would print the wrong known clause for 1,401 events.

The repair is small. Recipe + register + inherited action + inherited argument
forms 2,465 state keys, and every one selects exactly one clause. The pictured
owner is not required to choose the wording; it remains the local referent.

The new `context_safe_read_recipe.py` therefore behaves as follows:

- with a known event ID, it replays the exact clause;
- with inherited action and argument, it selects the exact known-state clause;
- when a recipe/register group has only one clause, it may print it directly;
- otherwise it prints only the safe component phrase and requests state.

For bare `AIIN` in Herbal, for example, it now returns “Arbeitswert” and says
that context is required instead of silently choosing one of seven sentence
variants.

## Exact order is indispensable

The full 1,563-key catalog contains only 1,423 different short German phrases.
There are 121 collision groups containing 261 recipes, with groups as large as
five. This does not damage the reader because phrases are never keys.

The reversal control says the same thing from another direction. Reversing the
49 main-card recipes yields 36 stops, seven already observed recipes, three
narrow recipes and three other strong recipes. Thus twelve genuinely reversed
orders and one palindrome still land on valid catalog entries. Order cannot be
discarded after translation.

## How much fallback exists?

Deleting one occurrence leaves an exact T0 recipe for 3,740/4,576 events. The
remaining 836 are singleton recipes. If the one-root rule is regenerated after
deletion, only one reaches high rank, thirteen strong rank and 36 narrow rank;
105 have one neighbour and 681 have none.

This is not a failure of the fixed deck: its predicted cards are deliberately
disjoint from observed cards. It is a boundary. The 49 cards are a precise
future gap list, not a self-healing dictionary for arbitrary missing recipes.

## What is now ready

All 35 checks pass. The current intake stack can safely identify exact recipes,
keep component order, and refuse a full sentence when its inherited state is
missing. No meaning, surface, or page changed.

The next useful closed-page step is to drive the two inherited state fields
left-to-right from the event stream, so the corrected reader receives them
automatically rather than through an oracle argument.
