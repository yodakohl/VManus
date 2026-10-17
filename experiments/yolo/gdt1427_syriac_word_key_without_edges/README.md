# GDT1427 — Syriac words under one common table

Status: DUAL_UNSAT_FIXED_VOCABULARY_CHANNEL. Both actual controls pass; both full59-group native searches exhaustively fail. See REPORT.md. See METHOD.md, PREREGISTRATION.md and src/SPEC.json. Reuses GDT1426 source/control/target exactly, removing only the external source-bigram condition.

After public registration: run src/run.py --gate then src/validate.py --gate. Only PASS permits src/run.py --native and src/validate.py --native. At control stop, run.py --native writes a zero-native stop. Static final replay: src/validate.py --validate. No automatic retries, source/normalization changes or cap increases.

The2133 Syriac written forms and source provenance are preserved in GDT1426 under the original HUNAYNNET CC BY-NC-SA4.0 license. See its SOURCE_NOTICE.txt. No source XML is reimported or relicensed here. No concrete native meanings are assigned.
