# Workspace continuity instructions

Before any Voynich action, read `VOYNICH_CURRENT_ROUTE.md`, then use
`experiments/EXPERIMENT_INDEX.tsv` to locate only the primary reports needed for
the active experiment. The current-route file is the compact authoritative
routing snapshot. `VOYNICH_ACTIVE_STATE.md` and
`experiments/semantic_assumptions/ACTIVE_EXPERIMENT_LEDGER.tsv` remain the full
claim registry and append-only material history; read targeted rows or sections
when auditing a claim, correcting the route, or checking for duplicate work,
not on every turn. `VOYNICH_HANDOFF.md`, `VOYNICH_WORKLOG.md`, and the older
experiment log/README are recovery archives and may contain superseded claims.

Use `./vmanus-work lookup GDT811` (or the relevant IDs) for compact index
pointers instead of dumping entire index rows. The efficient operating guide is
`docs/WORKFLOW.md`. Keep the current route short; replace current summaries
instead of appending an ever-growing chronology. Add workflow conveniences
outside hash-bound legacy tools so past experiments remain reproducible.

- Use subagents only when the user explicitly authorizes them; preserve task
  independence where blinding is part of an experiment.
- The user explicitly requests a pipelined idea producer during active research.
  Keep one bounded subagent maintaining `docs/IDEA_BACKLOG.md` while root tests
  the current candidate; do not wait for each test to finish before replenishing.
  Preserve ownership and blinding; this is not unattended between-turn execution.
- Publish every material finding promptly to the public GitHub repository,
  together with the experiment source, preregistration, validator, and compact
  result artifacts needed to reproduce it. Direct pushes to `main` are
  authorized. Before every push, scan the exact staged tree for credentials,
  private keys, private machine metadata, absolute local paths, and private or
  unrelated files; never publish any such material.
- Prefer cached transcription/features and up to 32 CPU workers; avoid repeated
  OCR/image decoding.
- Inspect mixed sealed/unsealed TSV sources through `./vmanus-exp query-tsv`
  with explicit selector allow-values and output columns. Do not parse a full
  row and filter afterward; the guarded command rejects `f84*` from the raw
  selector field before materializing the remainder.
- Run `./vmanus-exp check-edge-packet PACKET [--null-candidates NULLS]` on new
  relation evidence. A packet is not score-ready until the executable GDT388
  capacity, held-folio, provenance, and mobile-null gates all pass.
- Keep structural tags distinct from English word translations.
- Treat ZL3b/IT2a/RF1b as alternate readings of one manuscript.
- After every material pass, failure, correction, or provisional lead, add one
  short row to `ACTIVE_EXPERIMENT_LEDGER.tsv`; update `VOYNICH_ACTIVE_STATE.md`
  only when the live interpretation or next route changes. Do not routinely
  grow the archived prose logs.
- Do not rerun a failed route unless there is new data or a genuinely different
  predeclared falsifier.
- Before substantial control, decoder, or infrastructure work, write a short
  decision note in the existing route/proposal: what is genuinely unknown after
  checking primary predecessors, which Voynich research decision each plausible
  outcome changes, the smallest adequate test, and a wall-time budget including
  preparation, implementation, validation, and publication. See docs/WORKFLOW.md.
  If outcomes leave the same research decision unchanged, do not start a large
  implementation. At the budget limit, stop expansion and reassess; no automatic
  chain of decoder repairs or new control corpora. Preserve scientific gates.
  Separate manuscript findings, control findings, and engineering work in updates;
  do not present a known failure mode or test count as new decipherment progress.
- Before proposing a new route, use `./vmanus-exp route-check QUERY` as a fast
  duplicate screen, then inspect only the returned primary reports and closed
  family rows. Its lexical ranking is navigation help, not a scientific gate.
- Keep GDT001--GDT336 byte-frozen in the legacy repository-root layout. Starting
  with GDT337, create every new experiment under
  `experiments/yolo/gdtNNN_short_slug/` using `tools/new_yolo_experiment.py`;
  every such directory must contain a valid `experiment.json` manifest.
  Starting with GDT394, manifests must seal both `f84` and `f84r` explicitly.
  `./vmanus-exp check` enforces the layout, manifest, index, sealed-data, and
  staged-tree privacy gates.
