# Structured manifest migration: legacy YOLO experiments 362–384

Date: 2026-08-20

Status: `ADMINISTRATIVE_ONLY_SCIENTIFIC_BYTES_UNCHANGED`

The repository-wide structured-experiment gate was blocked by 23 experiments
created before the current `experiment.json` schema was enforced. Eight
experiments (GDT362–GDT369) had no manifest; fifteen (GDT370–GDT384) had an old
or partially structured manifest.

The migration:

* creates or replaces only `experiment.json` wrappers;
* recovers unchanged scientific inputs from each compact result's hash map;
* hash-binds every retained file in each experiment directory;
* preserves each published status and claim ceiling;
* names the existing runner and validator entry points;
* adds no scientific observation, fit, null, score, or claim; and
* does not open or parse manuscript/transcription data, including f84.

All 23 migrated manifests pass the current schema and byte-binding check. The
original validators pass for GDT362–GDT372 and GDT374–GDT378. Two explicit
administrative exceptions are handled without changing the original results:

1. GDT373's result binds experiment-time versions of the append-only active
   state and ledger. Those live paths necessarily advanced. Its wrapper checks
   all immutable bytes and requires exactly those two historical advances.
2. GDT379–GDT384 result files bind their former ad-hoc `experiment.json` bytes.
   Their wrapper permits only that manifest replacement, verifies every other
   result-bound input/output/document/implementation byte, and requires the
   original validation artifact to remain `PASS`.

The migration is reproducible with
`tools/migrate_yolo_manifests_362_384.py`; the restricted historical wrapper is
`tools/validate_migrated_yolo_experiment.py`. After migration,
`./vmanus-exp check --all` returns `REPOSITORY_PREFLIGHT_PASS`.

This is repository maintenance only. It does not revise any GDT362–GDT384
scientific conclusion and licenses no semantic, linguistic, or plaintext claim.
