# Thirty proposed reading programs — 2026-09-12

The operative German handoff is [docs/TRANSLATION_PROGRAMS_30.md](../../../docs/TRANSLATION_PROGRAMS_30.md). These are untested hypotheses, not executed experiments, preregistrations or confirmed translations.

- `PROGRAMS.json`: all30 programs plus exact exposed work packages and current user policy.
- `P01.json` through `P30.json`: original proposals added sequentially with `vmanus-work ideas add`; identities IDEA000144–IDEA000173 are mapped in `INDEX.tsv`.
- `PREDECESSOR_SCREEN.json`: bounded navigation before registry insertion, with exact proposal hashes. No exhaustive novelty claim. The nearest scientific predecessors remain to be checked at selection.
- `VALIDATION.json` and `validate.py`: reproducible documentation consistency checks only. The validator opens proposal/documentation files and checks source-path existence; it never opens manuscript payloads or the registry JSONL.

Run from the repository root:

```bash
python research_registry/proposals/translation_programs_20260912/validate.py
./vmanus-work ideas check
```

Do not add the30 proposals again: use the existing registry IDs. Follow-up readings belong in versioned `work/Pxx/` folders; actual new registered empirical experiments use the established GDT scaffold. No reserved page was opened, no human contacted, and no new page admitted for this delivery.
