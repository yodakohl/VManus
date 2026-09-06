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

For an exact non-GDT ID omitted from that index, use
`./vmanus-work locate DIC001`. This searches only tracked Markdown filenames,
with an exact case-insensitive ID boundary; it opens no report or manuscript
contents. It also finds correction/specification files. Listed paths are
navigation pointers, not a claim that a report is current or an authorization to
open sealed data. Consult the current route and relevant corrections before
using an old result. A missing route-check hit is not evidence of novelty:
DIC001 is an observed example outside its two source registries.

Do not reload the giant active registry, ledger, complete experiment rows or
archived logs on every turn. Follow one relevant pointer at a time. Update the
current-route summaries in place; put history in its existing registry.

## Keep computation and administration proportional

- Reuse a completed experiment's admitted reader or compact artifact when it
  contains the needed information. Obtain any new mixed-table projection through
  the existing selector-first query-tsv guard; never broaden admission implicitly.
  Repeat `--allow` for each page, e.g. `--allow f1r --allow f2v`; do not join
  allow-values with commas. Only `--columns page,locus` takes a comma list.
  An unexpected zero-row projection is an input failure, not missing evidence.
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

## Pipelined idea supply and execution

Explicit user request, 2026-09-06: keep an additional agent generating ideas in
parallel and saving a list, so root does not restart ideation after each test.

- One producer owns `docs/IDEA_BACKLOG.md`; root continues the current scientific
  task. On active turns, resume the producer with a bounded replenishment task
  when the queue is thin. User update: maintain substantially more ideas than we
  execute, roughly20–30 raw candidates spanning at least six mechanism families.
  This is a replenishment target, not a quota of scientific novelty. Keep a
  shortlist of about five for review; producer work must not block a current test.
- Raw ideas may be speculative and unreviewed: mark them RAW_UNSCREENED, identify
  the proposed discriminator, required source, smallest test and principal risk.
  REVIEW_PRIORITY means selected for scrutiny, not ready to run. Keep these
  compact; do not turn every sketch into an experiment or a long provenance audit.
- Before experimental selection, review primary predecessors and duplicate-screen.
  Record the new discriminator, actual data availability, total wall-time budget
  and which research decision each outcome changes. Known failed routes stay
  closed unless their stated new-evidence condition is met.
- Rank candidates by how sharply outcomes separate plausible mechanisms, whether
  needed observations are available independently of our working translations,
  and expected information gain per total effort. Preserve diversity in the
  shortlist; include ambitious data-dependent proposals but separate them from
  executable tests. Ease, a likely positive result and lexical search rank are
  not evidence of research value. No invented numerical success probabilities.
- Selection correction after IP014/009/018/021/022/033/036: seven preferred
  sketches produced no executable contrast in the cited-source reviews. Keep
  the broad raw pool, but select consumer work from a concrete source example
  plus a proposed discriminator, not from a mechanism name and generic report
  pointer. Producer should seek that starting observation before more sketches.
  This is not a demand for an already proven semantic anchor: a preregistered
  exploratory observation may discover structure and generate a hypothesis.
  Do not spend successive turns restating missing prerequisites or repeatedly
  auditing the same dependency. Batch cheap reviews; retain source-specific stops.
- Root chooses at most one next experiment after checking the candidate. Hand
  off queue edits explicitly: producer lists proposals; root supplies acceptance,
  IN_PROGRESS and result decisions. Keep rejected and completed entries with a
  short reason/report link. Never silently recycle a failed route.
- A separate bounded reviewer may check novelty or independent validation when
  useful. Keep data packets and outputs disjoint where experimental blinding
  requires it; the producer does not read held target data to invent its tests.
- Queueing is research planning, not preregistration or scientific success.
  Preregister selected tests/discovery scope, preserve all outcomes and publish
  one compact reproducible result. Reuse readers and protect sealed data.
- The agent runs during assigned active tasks; no persistent background service
  or unattended work between turns has been started. Reuse the same agent with
  followup tasks where available. Root owns checks, global records and publication.

### Measured correction after GDT839

The 02:02:40–02:11:13 UTC turn took8m33s. First extraction started about02:09:53:
7m13s (84%) elapsed before data execution. Extraction, pair audit and replay took
only a few seconds; the remaining roughly80s covered reporting and publication.
These are tool/turn timestamps, not a profiler breakdown of thinking, context
recovery, worker time or programming. Git commits independently timestamp public
registration at02:09:48 and the result commit at02:11:07. More CPU/GPU workers
would not address the dominant measured delay.

The screen also duplicated METHOD.md and PREREGISTRATION.md byte for byte.
Its occurrence JSON uses103439 lines/1356648 bytes; identical compact JSON would
use715968 bytes. These are engineering measurements, not manuscript findings.
Leave the registered GDT839 bytes frozen. For future small passes:

- Root immediately inspects one concrete existing manuscript example while the
  producer fills the next-candidate queue. Add a novelty reviewer only for a
  bounded independent question. Do not spend the whole round merely screening.
- Within90s decide whether a discriminating question exists. State what is known
  and what a new observation could distinguish. Do not manufacture novelty by
  requiring rare exact collisions with no observed motivating instance.
- Use one authoritative protocol, short pointers in required companion files,
  compact machine artifacts and reused source readers. Target a first data
  observation within2min and a complete small pass within5min, including checks
  and publication. These are effort targets, not promises of scientific success.
- Permit explicitly labelled discovery before selecting a confirmatory hypothesis:
  preregister its source scope, exploratory purpose, output and stopping budget;
  disclose motivating examples. Reserve unseen data for later confirmation.
  Do not represent discovery-selected patterns as predeclared successes.
- Build on positive evidence by seeking an unresolved contrasting prediction,
  not by recounting known hits. Keep all tested outcomes and existing null/held
  gates; neither looser post-result criteria nor familiar findings count as gains.

The anchor review found that okal's label/prose identity already has follow-ups
GDT793/794/798. Do not restart its immediate ownership or position tests.
GDT811 retains a narrower, still-unidentified ofaldo/ofal lead: f88r.25 label,
f88r.30 prose and f108r.14 prose. Existing texts place ofal after chetchy and
opchdy respectively; next forms are dar across the f88r line break and shor on
f108r. The contexts therefore do not supply an identical immediate formula.
This is a comparison of already published examples, not a new inventory, suffix
finding or name identification. A productive do operation and a shared referent
remain unproved; a new experiment requires a specific additional prediction.
Primary: experiments/yolo/gdt811_four_page_content_synthesis/REPORT.md and its
artifacts/FOUR_PAGES_FULL_TEXT.md. No new scientific experiment is selected by
this workflow audit, and no positive decipherment result is claimed.

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
