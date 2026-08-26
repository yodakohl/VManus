# GDT439 method

## Question

Does GDT437's order-safe distinction extend from the 49-card main deck to all
1,563 exact keys in the observed, predictive and narrow intake catalog?

## Inputs

- GDT434's complete disjoint exact-key catalog;
- the 49 action/argument states actually reached by GDT436;
- GDT437's transition engine and order-safe renderer.

## Method

Execute every recipe in every reachable state and all five registers: 382,935
cells. Hash the complete vector of outgoing action, outgoing argument and
clause, then verify exact vector equality inside each hash collision group.
Separately compare every catalog pair with the same atom multiset, summarize
tiers, and isolate collisions touching the 49-card main deck.

## Decision rule and claim ceiling

The main deck is internally safe only if no collision group contains two main
cards. Full-catalog collisions are retained rather than repaired here. Equal
local controls with the same working value are not promoted into new meanings;
same-multiset order collapses become the next explicit repair queue. Exact
component keys remain authoritative. No surface or page is predicted.
