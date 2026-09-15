# Validator correction receipt

The first independent validator output was FAIL and is preserved in
artifacts/INITIAL_VALIDATION.json. src/validate_initial_draft.py preserves the
intermediate checker immediately before root took over; it is not asserted to
be the exact version which generated every field of the initial receipt.

The checker initially reconstructed a window identifier/output order, source
class order and required-row table representation differently, and initially
kept impossible zero-capacity candidates in its reported domains. These are
checker errors against the published contract. A later individual-marginal
query exceeded a three-second checker timeout; it was not counted as UNSAT.

The completed checker rereads all raw group IDs and all 22 full windows,
reextracts both source rosters with the frozen aliases, reconstructs lower
assignment counts, and uses an independently implemented integer variable per
plant plus Distinct and row capacities instead of the runner Boolean model.
Real words with the same known mask and identical eligibility across every
plant are exact permutation orbits: forcing one representative validates all
members because the global word-name swap preserves every constraint. Fresh
unknown plant words are never merged into these orbits. All 17116 published
marginal statuses, including 332 UNSAT statuses, are checked by these exact
orbits. Saved joint witnesses and both candidate/prediction tables are checked.

The final executable returns PASS. Root completed the independent implementation;
this is not a claim of blind interpretation or an external expert review.
The frozen source, boundaries, predictions, runner scientific predicates and
60-contradiction/28-unknown-only result did not change. No data discrepancy was
found. The correction is validation engineering, not decipherment progress.
