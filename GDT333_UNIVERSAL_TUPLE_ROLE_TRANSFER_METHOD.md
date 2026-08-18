# GDT333 — universal tuple structural-role transfer

GDT333 tests whether the 53 GDT332 joint tuples present in all five registers
carry a register-invariant abstract placement role.  Each complete register is
held out.  The four independent external placement components are physical
line entry, within-field position, field ordinal binned 1/2/3/4+, and physical
line quartile.  DY/B3, wrapper, frame, inner-D, right family, host glyphs, and
same-group contents are not targets.

For each component, a symmetric Dirichlet-1/2 code is trained on the other
four registers.  `GLOBAL` ignores the source symbol, `COORDINATE` conditions
on compiler coordinate, and `JOINT_TUPLE` conditions on the exact opaque tuple.
Scores are summed without fitting a weight.  Report aggregate and per-register
gain, plus the number of registers in which each tuple improves over its
coordinate baseline.

This exposed five-fold structural audit has no inferential p-value.  A
universal role candidate would need positive tuple gain in all five registers;
aggregate gain alone is insufficient.  No meanings or f84 data are used.
