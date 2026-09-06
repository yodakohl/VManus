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

## Require information gain before substantial work

User correction, 2026-09-06: the user reported six hours for the work culminating
in GDT837 and judged its return inadequate. The assistant accepts the poor
prioritization. GDT837 supplied no new manuscript reading. It found no added
wholeword-constraint benefit on one new control and localized a wrong suffix
value. Wrong candidates outranking truth was already known from GDT834; presenting
that general observation as a new discovery overstated the gain. High synthetic
accuracy, more restarts and independent software checks do not bridge this gap.
The duration is user-reported, not an instrumented breakdown of those six hours.

Before substantial work, put one short decision note in the existing route or
proposal, not a new administrative experiment or another reporting framework:

- State the unresolved question and what the primary predecessor reports already
  establish. Name the new discriminator rather than merely a new source or bug.
- State the concrete Voynich research decision that success, failure and an
  inconclusive result would change. For a control, identify its necessary link
  to that decision; improved decoder accuracy alone is insufficient justification.
- Choose the smallest scientifically adequate test using existing data/code first.
  Budget total wall time, including source work, programming, checks and publishing;
  set a checkpoint before major implementation and an explicit stopping condition.
- At the checkpoint or budget limit, report the actual new evidence and reassess
  value before expanding. If the decision does not change, close or defer the work.
  A failed control must not automatically trigger the next decoder repair, suffix
  rule, corpus search or larger restart panel. Any successor must justify itself.

This is a prioritization rule, not a new permission requirement. Continue
independently within existing authorization. Preserve preregistration, blinding,
sealed-data and publication checks; reduce experimental scope instead of weakening
those checks. Reuse validators and avoid repeated checks without a changed input
or concrete unresolved concern. Report manuscript evidence, control evidence and
engineering deliverables separately, including what was already known. Honest
negative findings remain useful when they actually change a research decision.

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
