# GDT1065 fixed pre-join decision

The decision and 20-minute total wall-time budget were written in
[IDEA643 precheck](../../../research_registry/decisions/idea643_same_record_capacity_20260928.md)
before the first grid-to-record join. This package was scaffolded **after**
an initial read-only diagnostic produced the count. The diagnostic and the
later packaged run used the same 13 GDT791 record IDs, 24 GDT735 bodies and
strict first-record-token/later-line-internal gate. The result is therefore
an exploratory capacity screen, not a blinded confirmation.

The fixed outcomes were: no strict pair → no capacity in this frame; strict
pair → only a possible future complete-record semantic test, with a separate
property binding still required. Nonopening pairs and H1/H4 profile similarity
receive no semantic credit. GDT737's failed held body-affinity transfer
remains a counterexample.
