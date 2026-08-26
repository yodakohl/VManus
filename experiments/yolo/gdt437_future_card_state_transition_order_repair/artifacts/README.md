# GDT437 artifacts

- `gdt437_12005_state_transition_matrix.tsv`: every future card in every
  reachable state and register, before and after the order repair.
- `gdt437_245_baseline_collision_cells.tsv`: the complete baseline collision
  inventory.
- `gdt437_49_transition_signatures.tsv`: one repaired transition signature per
  card.
- `gdt437_1176_pairwise_signature_audit.tsv`: exhaustive card-pair comparison.
- `gdt437_68_current_order_repairs.tsv`: current event clauses whose word order
  changes.
- `gdt437_59_current_statement_order_repairs.tsv`: affected full statements.
- `gdt437_result.json` and `gdt437_validation.json`: compact result and checks.

The 12,005-row matrix is retained because it is the direct executable evidence
that the repaired deck is collision-free across the full reachable state
space, rather than only in a few examples.
