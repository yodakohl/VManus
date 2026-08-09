# `cho/che` scope preflight v1 rotation audit

Status: **CONFIRMED_UNSIGNED_UNDERFLOW_INVALIDATES_V1_ROTATIONS**

The frozen multiset control found **2079** violations in the first
16 assignments. V1 subtracts unsigned indices before taking modulo `n`; when
the subtraction is negative it wraps at `2^64`, so some rows duplicate one
source position and omit another. The first failure is assignment
**7**, INDEPENDENT_STRATUM stratum **4**
of size **3**, with **0** observed
ones instead of **1**.

All v1 null and power scores are invalid and confer no target authorization.
The target remained absent and zero manuscript outcomes or scores were opened.
The only admissible repair is a versioned `(j+n-shift) mod n` implementation
followed by a synthetic-only rerun under unchanged scientific gates.
