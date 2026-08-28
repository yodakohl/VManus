# GDT612 artifacts

The package records an invalidated developmental decoder, not a successful or
faithful FST34 test. `oracle_objective_audit.tsv` contains the exact
truth-versus-six-fitted-key ranking. `synthetic_truth_exposure.tsv` and
`synthetic_truth_collisions.tsv` expose the defective control.
`orientation_audit.tsv`, `candidate_pool_counts.tsv`, and
`top_token_injection.tsv` expose the unmatched control and injected-word
degeneracy. `METHOD_AUDIT.json` is their compact machine-readable verdict.

The corresponding generators are `src/oracle_objective_audit.py` and
`src/method_audit.py`; the compact validator recomputes their headline claims.
`reference_packs/` contains the exact normalized word and candidate inventories
needed for those checks.
`COMPACT_MANIFEST.tsv` hash-covers every compact file except itself, the mutable
experiment manifest and the validator's own deterministic result.

`RESULTS.json`, `CONCLUSION.json`, `language_summary.tsv` and
`held_run_metrics.tsv` contain the aggregate control and target results.
`carrier_stability.tsv`, `carrier_consensus.tsv`, `anchor_audit.tsv` and
`unanimous_structural_roles.tsv` expose every stability claim.

The `keys/` tree retains all six synthetic maps and all eighteen real-order
target maps. Together with `units.tsv`, `primitives.tsv`, the synthetic truth
and `synthetic_held.tsv`, these let `src/validate.py` independently reproduce
the 0/34, 0/98 and zero-span findings and the complete best paragraph.

The 27 large held decode tables are omitted. The normalized reference word and
candidate packs required by the post-run method audit are included.
`FULL_RUN_MANIFEST.tsv` preserves the path, byte count and SHA-256 of every one
of the original 286 full-run files; `FULL_REPRODUCTION.md` rebuilds them from
the hash-pinned public inputs. `REPRODUCTION_CHECK.json` records the successful
clean rerun and identical canonical target/control payload hashes.
