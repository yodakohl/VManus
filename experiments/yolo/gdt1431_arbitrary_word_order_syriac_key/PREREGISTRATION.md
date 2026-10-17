# GDT1431 registration

Freeze METHOD, SPEC, both encodings and pinned inputs in LOCK before any actual
control or native search, then publish/verify the exact registration on main.
Run primary --gate; independent --gate (requires primary), stop if either is not
verified SAT. Only after GATE_VALIDATION PASS run primary --native and independent
--native once each on full59. Run independent --validate statically. All timeouts
are UNKNOWN. No caps, W, units, source normalizations, subsets or search repairs.
Final decision: verified SAT/UNSAT disagreement INVALID; any valid native SAT
means SAT_CAPACITY_UNASSESSED, both UNSAT DUAL_ENCODING_UNSAT_ARBITRARY_WORD_ORDER,
otherwise UNKNOWN_OPEN. Control failure stops native entirely. Same Z3 backend
for both encodings must be explicit.0 confirmed words for every outcome.
