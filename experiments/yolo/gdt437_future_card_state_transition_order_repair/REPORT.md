# GDT437 — written order now survives the reader

## Result

The state machine had exactly one universal blind spot. It treated these two
cards as the same instruction in all 49 reachable states and all five
registers:

- `AIR+Y`: route first, then current item;
- `Y+AIR`: current item first, then route.

That is 245 collapsed transition cells. No other pair among the 49 cards is a
universal collision.

The cause was simple: the old German clause builder gathered arguments and
relations into semantic buckets and printed the buckets in a fixed order. It
therefore discarded the order already present in the card.

## Repair

The reader now obeys the selected order rule:

- `AIR+Y`: “Entlang der Ringbahn: im laufenden Gang wähle den
  Positionsposten.”
- `Y+AIR`: “Im laufenden Gang wähle den Positionsposten; entlang der
  Ringbahn.”

The same contrast is produced with the Herbal, Biological, Pharma and source
register vocabulary. Nothing else changes: same action, same argument, same
incoming and outgoing state, same component meanings.

## Exhaustive transition check

- 49 cards × 49 reachable states × 5 registers = 12,005 cells;
- 1,176 unordered card-pair comparisons;
- baseline: 245 collision cells, all from `AIR+Y` versus `Y+AIR`;
- repaired: zero collision cells;
- 49 distinct repaired transition signatures.

Applying the same order repair to the current edition changes the wording of
68 events in 59 statements. These are not semantic revisions: the relation is
only moved to the position licensed by the written component order.

All 28 validation checks pass, including deterministic regeneration. The
practical consequence is important for the next-page test: two genuinely
different future cards can no longer be accepted as the same transition merely
because their components were printed in reverse order.
