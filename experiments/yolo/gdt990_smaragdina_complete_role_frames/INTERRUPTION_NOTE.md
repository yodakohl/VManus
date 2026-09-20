# Interrupted execution: bounded recovery decision

Recorded 2026-09-20 05:21 UTC, after public preregistration 1735087bb.

The registered execution ended with exit 143 (termination signal). Its final
case files were not written. The source of that signal is unknown. The runner
held all individual solver results in memory, so none may be reconstructed from
the progress messages. In particular, those messages do not establish that all
completed jobs were unknown or that no satisfiable job occurred.

The retained console observations were:

```
prepared_cases=32376; solver_jobs=1980
UNKNOWN_SOURCE=19080
CONTRADICTED_NONEMPTY_LENGTH=7524
CONTRADICTED_INJECTIVE_LENGTH=3696
CONTRADICTED_WORD_BOUNDARIES=96
PENDING=1980
completed=32; of=1980; latest=UNKNOWN_SOLVER
completed=64; of=1980; latest=UNKNOWN_SOLVER
completed=96; of=1980; latest=UNKNOWN_SOLVER
```

This is an incomplete execution, not a scientific refutation of the remaining
equations. The aggregate progress does not identify the completed case IDs.

Recovery decision: spend at most 15 minutes, including validation and publication,
reconstructing only the registered deterministic necessary conditions on all
cases. The original independent validator's separate implementation must agree.
Every equation requiring solver work is recorded UNKNOWN_UNRETAINED_SOLVER_RESULT.
No solver is called, no queued job is retried, and no fixed source, writer,
preregistration, model, or original validator is changed. The original inclusive
experiment limit remains 06:24 UTC. If recovery fails, retain that failure and
do not expand the infrastructure work.

Either outcome changes the report from apparently running to interrupted. A
successful recovery additionally preserves the independently checkable necessary
contradictions and complete candidate inventory. It cannot provide a full code,
an equation-level negative result, a word meaning, or independent confirmation.
