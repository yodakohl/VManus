# GDT436 method

## Question

Can the two context fields required by GDT435 be generated left-to-right from
the visible component recipes and owner addresses, without using event IDs or
precomputed inherited-state columns?

## Inputs

- GDT415's ordered 4,576 events and 715 statements, which contain no inherited
  action or argument fields.
- GDT416's action/argument sets and clause renderer; its published clauses are
  used only as the comparison target.
- GDT434's exact 1,563-key tier catalog and 49-card main deck.

## Method

Maintain one state bank for every `(physical page, visible owner)` pair. Each
bank stores only the last explicit action and last explicit argument. A card's
last explicit value updates its slot; a card lacking that value may inherit it.
A pure `DY` card inherits neither. Switching owner selects another bank;
returning to an old owner restores its bank. Physical statement boundaries do
not erase owner state.

Stream all GDT415 events without consulting their IDs for state. Render each
clause, rebuild all 715 statements, and only then compare with GDT416. Finally,
classify the 49 future cards by whether they explicitly carry an action and an
argument.

## Decision rule and claim ceiling

The driver passes only if every state field, event clause and statement matches
the current edition. This is an executable integration result, not independent
evidence for the meanings used by that edition. Unknown atoms or unlicensed
recipes stop without changing the state bank. No surface or page is predicted.
