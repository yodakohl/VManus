# Workflow maintenance, 2026-09-05

Outcome: smaller mandatory startup, metadata-only experiment navigation and an
explicit exact-staged publication check. No semantic experiment, new page,
dictionary change or translation claim. No GDT number allocated.

## Scope and design

The user requested cleanup for efficient long-running work. The main avoidable
cost was repeated context/navigation and manual publication coordination, not
CPU-heavy manuscript processing. This pass therefore adds small companion tools
instead of rewriting old experiment pipelines or building another decoder.

- VOYNICH_CURRENT_ROUTE.md now contains the current position, admissions,
  critical corrections, duplicate traps and report pointers. Detailed claims
  remain in their existing registry/reports. The old route is recoverable at
  commit ca1da15c, with no duplicate archive added.
- `vmanus-work lookup` opens only EXPERIMENT_INDEX.tsv metadata and returns
  bounded pointers. It does not open a listed report, raw source or image.
- `vmanus-work check-staged` checks all staged privacy/scope and selected
  experiment manifests, seals, bound bytes and direct dependency existence/order.
  It reads captured Git index object IDs, so an unstaged worktree replacement
  cannot disguise the bytes about to be committed. Deletions and rename sources
  remain in scope. No automatic stage, commit, push or deletion is performed.
- AGENTS.md links the companion and docs/WORKFLOW.md. Future summaries should
  replace the current route, not accumulate an ever-longer chronology. Related
  research probes should share inputs and one material question.

The historical CLI, preflight and manifest implementation stay byte-unchanged;
old manifests bind some of those tools by hash. This is an additive convenience,
not a mass rewrite of historical reproducibility records.

## Measured result

| Measurement | Before | After |
|---|---:|---:|
| Mandatory route, UTF-8 bytes | 24,631 | 8,402 |
| Mandatory route, whitespace-separated words | 3,017 | 1,108 |
| GDT811 full index row versus compact text card, bytes | 3,153 | 916 |

The route is 65.9% smaller by bytes. This measures context volume, not tokenizer
usage, translation progress or a demonstrated end-to-end runtime speedup.
An independent comparison of the old/new snapshot retained the substantive
scope boundaries and restored two near-term duplicate-routing warnings.

## Verification and limits

56 unit tests pass: 12 metadata lookup, 23 exact-staged preflight, four workflow
integration/compactness, and 17 existing infrastructure tests. Synthetic
fixtures cover sealed-selector rejection, missing/duplicate lookup IDs, partial
staging, privacy even outside scope, deletion/rename scope, frozen paths, absent
or altered bindings, malformed results, seals and direct dependencies.

The unchanged global `vmanus-exp check --all` still fails with exactly seven
pre-existing unbound reproducibility files in the unfinished GDT600 worktree:
METHOD.md, PREREGISTRATION.md, README.md, REPORT.md, src/model.py, src/run.py and
src/validate.py. They were not fixed, staged, deleted or hidden.

The task checker explicitly does not certify the global worktree/index rebuild,
unselected historical or recursive/reverse dependency hashes, validator execution
or manuscript meaning. It supplements the global audit; it does not clear those
seven errors. Selected experiments still need their own actual validators.

No source image, transcription, experiment, dictionary, claim registry or
unrelated unfinished work was removed. No real mixed manuscript table was
queried during this maintenance pass. Published files contain repository-relative
pointers; local-machine paths are not needed in the artifacts.

## Reproduce

```sh
git show ca1da15c:VOYNICH_CURRENT_ROUTE.md | wc -l -w -c
wc -l -w -c VOYNICH_CURRENT_ROUTE.md
./vmanus-work lookup GDT811
./vmanus-work lookup GDT809 --json
python3 -m unittest tests.test_experiment_lookup tests.test_work_preflight tests.test_workflow_docs tests.test_repository_infrastructure
./vmanus-exp check --all
```

Run `vmanus-work check-staged` only after staging the intended task files; pass
each infrastructure file as an exact --include, or select a structured experiment
with --experiment. An empty index or implicit scope fails intentionally.

Implementation: tools/experiment_lookup.py, tools/work_preflight.py,
tools/work_cli.py and the vmanus-work entry point. The three new test modules
above exercise those additions without changing historical tests.
