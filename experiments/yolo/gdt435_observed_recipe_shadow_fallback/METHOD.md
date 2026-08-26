# GDT435 method

## Question

Does the exact-key reader preserve every observed event, and what additional
left-to-right context is actually required before it may print a full sentence?

## Inputs

- GDT416's 4,576 event clauses and inherited action/argument states.
- GDT430's complete observed/absent one-root candidate density.
- GDT434's 1,563-key intake catalog.

## Method

1. Replay every event through its exact GDT434 recipe tier.
2. Group observed occurrences by recipe+register and compare their full
   clauses. Record what a naive “take the first clause” reader would get wrong.
3. Add the smallest available context fields and require clause uniqueness.
4. Simulate deletion of one event and deletion of a whole recipe. Keep the
   frozen reader distinct from a counterfactual regeneration of GDT430's
   neighbour rule.
5. Reverse all 49 main-card recipes and audit the entire 1,563-card catalog for
   natural-phrase collisions.
6. Publish a context-safe reader that never emits an arbitrary observed clause.

## Decision rule and claim ceiling

A whole sentence is emitted only if its observed clause is unique in the
available scope, if a known event ID is supplied, or if recipe+register+
inherited action+inherited argument selects one clause. Otherwise the reader
returns only the safe component phrase and asks for context. This changes no
card, component value, surface prediction, or page.
