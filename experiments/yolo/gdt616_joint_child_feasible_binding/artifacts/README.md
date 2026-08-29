# Artifacts

`REGISTERED_SEARCH.json` is the prospective, deterministic machine-readable
contract. It binds the exact GDT608/GDT614/GDT615 sources, recursive X/Z model,
access boundary, objective order, and terminal outcomes without containing a
candidate mapping or score.

`stage_a/PRIMARY_RESULT.json` and `stage_a/INDEPENDENT_RESULT.json` are the two
exact terminal UNSAT results. `stage_a/COMPARISON.json` binds their hashes and
agreement. `stage_a/UNSAT_CORE_DIAGNOSTIC.json` is the corrected 23-group
post-terminal diagnosis; `src/diagnose_unsat_core.py --check` reconstructs and
byte-checks it. `stage_a/RELAXATION_DIAGNOSTIC.json` records complete rank
sweeps at one through four paid-child TRAIN-gate breaks and one representative
minimum-four witness; `src/diagnose_relaxation.py --self-test` checks the local
encoding without rerunning the expensive sweep. `stage_a/VALIDATION.json`
checks the fixed strict-result hashes, both strict solver-source hashes, both
diagnostic artifact/source pairs, their exact boundary/core/witness structure,
scope, and closed access flags. Both diagnostics explain failure boundaries
without changing the strict decision.

No strict mapping, selected paid assignment, W0/W1/W2 world, Held score, target
value, or meaning exists under GDT616. The relaxation file contains only a
post-terminal diagnostic witness under a deliberately weakened child gate; it
is not a selected key. Transient solver work and nondeterministic statistics
are not canonical artifacts.
