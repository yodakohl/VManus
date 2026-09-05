# Efficient Voynich work

Read VOYNICH_CURRENT_ROUTE.md first. It gives the live position and scope, not
the full history. Detailed claims stay in the active registry and primary reports.

## Start narrowly

    ./vmanus-work lookup GDT811 GDT809
    ./vmanus-work lookup GDT734 --json

Lookup reads only EXPERIMENT_INDEX.tsv metadata. It returns a question, status,
primary report and a few usable entry points, without dumping every artifact
path. It does not open those paths or authorize access to any manuscript page.
For a new research direction, keep using vmanus-exp route-check first.

Do not reload the giant active registry, ledger, complete experiment rows or
archived logs on every turn. Follow one relevant pointer at a time. Update the
current-route summaries in place; put history in its existing registry.

## Keep computation and administration proportional

- Reuse a completed experiment's admitted reader or compact artifact when it
  contains the needed information. Obtain any new mixed-table projection through
  the existing selector-first query-tsv guard; never broaden admission implicitly.
- Share one precise input packet across independent subtasks. State the question,
  source paths, allowed scope and output ownership; ask for interpretations as
  well as checks. Avoid multiple agents repeatedly locating the same files.
- Group related exploratory probes into one material pass. Source scripts and
  tests should verify the actual claim; repetitive plumbing checks are not
  translation progress. Keep one useful report, a compact result, and reproducible
  inputs/implementation rather than duplicating the same narrative everywhere.
- Software/workflow maintenance is not a new semantic experiment and does not
  need a new GDT number. Record it as maintenance with source and targeted tests.
- No cached interpretation, successful test, hash or polished German phrase is
  independent evidence for a word's meaning.

## Publish the exact task, with explicit limits

The old vmanus-exp and its implementation are hash-bound inputs of historical
experiments. Keep them unchanged when adding conveniences; vmanus-work is an
additive companion, not a replacement decoder or weakened scientific checker.

After staging only the task's intended files, use:

    ./vmanus-work check-staged --experiment GDT811

Declare additional exact global paths individually with --include. For an
infrastructure-only change, use --include for every intended path. The helper
checks the exact staged content and selected experiment bindings; its output
states that the global worktree was not checked. It never commits or pushes.
See --help for the precise supported scope.

Continue to run the unchanged full audit separately:

    ./vmanus-exp check --all

An unrelated unfinished experiment can fail that full audit. Report it as
existing worktree debt, not as fixed or as a passing global check. The focused
check covers staged secrets, selected experiment bindings and manifests,
and undeclared deletions or out-of-scope files. Reverse dependencies in unselected
experiments still need the full audit. Do not auto-stage, auto-delete, or
modify someone else's unfinished work to silence a warning.

## Maintenance verification

Run the workflow/navigation/preflight unit tests and the existing infrastructure
tests. They use synthetic manuscript fixtures, not newly admitted pages. Compare
context/output sizes as engineering measurements, not semantic successes.

The pre-compaction route remains recoverable from Git:

    git show ca1da15c:VOYNICH_CURRENT_ROUTE.md

No experiment, dictionary, source image, transcript, claim registry or untracked
research directory was removed by the September 2026 workflow cleanup.
