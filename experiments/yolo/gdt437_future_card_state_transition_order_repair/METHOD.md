# GDT437 method

## Question

Do the 49 main future-card recipes remain distinct when they are executed from
every state already reached by the current stream reader, or has the clause
renderer erased meaningful component order?

## Inputs

- GDT434's 49 high/strong/Amber-II future recipes and exact intake tiers.
- GDT436's 4,576-event stream, used to enumerate the 49 actually reachable
  `(active action, active argument)` states.
- GDT436's 715 statements, used only to propagate any wording repair through
  the current readable edition.
- GDT416's frozen root sets and clause renderer, plus GDT431's order-preserving
  safe phrase renderer.

## Method

Execute each of the 49 cards from each of the 49 reachable states in each of
five registers: 12,005 transition cells. A transition signature consists of
the outgoing action, outgoing argument and rendered clause. Compare all 1,176
unordered card pairs before and after an order-preserving render.

The repair is deliberately narrow. If a relation occurs before an argument,
render the relation first. If the relation follows the argument, retain the
old action/object-first clause. Action, argument, state update and every root
meaning remain unchanged. Replay the repaired renderer over the current 4,576
events and rebuild only statements whose word order changes.

## Decision rule and claim ceiling

Pass only if every baseline collision is enumerated, all repaired transition
signatures are unique, the rebuild is deterministic, and current changes are
limited to relation/argument order. This tests internal executable
distinctness. It does not confirm a component meaning, plaintext, language,
surface form or page prediction.
