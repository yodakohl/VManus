# GDT396 qualification result execution correction

Status: `AUTHORITATIVE_POST_QUALIFICATION_PUBLIC_PATH`.

Independent result audit found that the legacy public runner still dispatched
the superseded qualifier and that the legacy public validator checked only
artifact presence/schema.  The scientific result itself reconstructed exactly
and remains unchanged.

`src/run_v2.py` is now the public orchestration entry point.  It authenticates
the append-only V2 correction lineage before scoring or qualifying.  The
separate `src/validate_qualification_result.py` independently reconstructs the
route gates, representation choices, decoder suite, qualified routes, and
confirmation panels from the exact metric table, and checks result/content,
correction, matrix, report, and seal bindings.

This is a reproducibility correction after qualification, not a new analysis.
No decoder, claim, metric, score, threshold, property decision rule, world,
surface, seed, or confirmation gate is changed.  Confirmation remains absent.
No Voynich corpus, `f84`, or `f84r` access is authorized.
