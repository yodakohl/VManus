# Stable immediate stopping at a repeated boundary sign

Let s be the entire state before reading a sign x. Let F(s,x) be the updated
state and T(s,x) the decision that this sign ends the current nonempty word.
The reader must place a gap immediately when T is true and cannot place one
when it is false. The decision uses current state and sign, without lookahead.
Written gaps do not change the state or supply a new reset.

The tested additional condition is stop stability:

    T(s,x) implies T(F(s,x),x).

If a word ends with x, T(s,x) is true. The state after it is F(s,x). A next
word starting with the same x therefore ends after that first sign. Hence
no longer next word may start with x. This proof allows arbitrary state size,
arbitrary behavior on other signs, and noninvertible updates. It does not
assume a common word-end state or a first-sign entry table.

The retained same-line pair `saino ol` violates the consequence: o ends the
first complete group, and the next complete group begins with o but continues
with l. Under the fixed group/sign premises, at least one of mandatory
immediate stopping, stop stability, boundary-state continuity or the causal
reading contract must be abandoned. The observation does not decide which.

For the concrete IDEA1065 writer, k nonempty containers give 4k MOVE actions
followed by WAIT and ROTATE at ranks 4k and 4k+1. Both terminal actions preserve
k, so the same rank remains terminal afterward. They satisfy the stability
premise under every glyph-to-rank bijection. No key search is needed.

The ten possible terminal ranks are 4,5,8,9,12,13,16,17,20,21. Only the first
eight can also occur as MOVE ranks in a state with more nonempty containers.
GDT1319's existing active-end inventories 18/19/19 already exceed ten. This is
a separate capacity corollary of that old count; it does not reuse its distinct
entry/exit equality-table theorem.

The original IDEA1054 writer permits externally supplied phases, so it does
not satisfy mandatory termination at WAIT/ROTATE. GDT1326 assumes the same
reset state at every word; no such reset is assumed here. Nonstable stopping,
real boundary updates, externally supplied/source-chosen boundaries that
override the mandatory T rule, and lookahead remain outside the excluded class. Scope controls make these distinctions
executable without adopting any as a new native hypothesis.
