# Workspace continuity instructions

Before any Voynich action, read `VOYNICH_ACTIVE_STATE.md`, then
`experiments/semantic_assumptions/ACTIVE_EXPERIMENT_LEDGER.tsv`. They are the
compact authoritative claim registry and routing index. Read only the named
primary reports needed for the active experiment. `VOYNICH_HANDOFF.md`,
`VOYNICH_WORKLOG.md`, and the older experiment log/README are recovery archives
and may contain superseded claims.

- Use subagents only when the user explicitly authorizes them; preserve task
  independence where blinding is part of an experiment.
- Publish every material finding promptly to the public GitHub repository,
  together with the experiment source, preregistration, validator, and compact
  result artifacts needed to reproduce it. Direct pushes to `main` are
  authorized. Before every push, scan the exact staged tree for credentials,
  private keys, private machine metadata, absolute local paths, and private or
  unrelated files; never publish any such material.
- Prefer cached transcription/features and up to 32 CPU workers; avoid repeated
  OCR/image decoding.
- Keep structural tags distinct from English word translations.
- Treat ZL3b/IT2a/RF1b as alternate readings of one manuscript.
- After every material pass, failure, correction, or provisional lead, add one
  short row to `ACTIVE_EXPERIMENT_LEDGER.tsv`; update `VOYNICH_ACTIVE_STATE.md`
  only when the live interpretation or next route changes. Do not routinely
  grow the archived prose logs.
- Do not rerun a failed route unless there is new data or a genuinely different
  predeclared falsifier.
- Keep GDT001--GDT336 byte-frozen in the legacy repository-root layout. Starting
  with GDT337, create every new experiment under
  `experiments/yolo/gdtNNN_short_slug/` using `tools/new_yolo_experiment.py`;
  `tools/build_experiment_index.py --check` enforces this boundary.
