# GDT373 administrative manifest migration

GDT373's original validator binds two append-only live-state inputs at their
2026-08-18 experiment-time hashes:

* `VOYNICH_ACTIVE_STATE.md` — `305e9e64fd2861bceab9efdce306bee3410dc5baf94a759b709dd37092bd5938`
* `experiments/semantic_assumptions/ACTIVE_EXPERIMENT_LEDGER.tsv` —
  `c41421d138145b9600420479c86459c430e064bcbc5b485d889c50bccb0cd167`

Both paths legitimately advanced after GDT373. The original result preserves
their historical hashes, but rerunning the original validator against today's
append-only files necessarily fails. The structured-manifest validator checks
that these are the only allowed live-path advances, verifies every immutable
input, output, implementation hash, result content hash, historical validation
artifact, status, and f84 flag, and makes no scientific change.
