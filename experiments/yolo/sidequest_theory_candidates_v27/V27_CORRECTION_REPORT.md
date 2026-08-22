# V27 correction — source-class/confidence column swap

Date: 2026-08-22

Status: **metadata correction; no semantic result changed**.

During preparation of the clause-template audit, four exact-card revisions from
V20 appeared under numeric source classes `.52`, `.58`, `.55`, and `.42`.
Inspection found a tuple-unpacking error in
`build_v20_cross_register_bridge.py`: `source_class` and `confidence` were
assigned in reverse order during propagation.

| card | correct source class | correct confidence |
|---|---|---:|
| CHTY | PROCESS_CONDITION | .52 |
| QOKAIIN | ENTRY_INSTRUCTION | .58 |
| AL/DAL | APPLICATION_LOCATION | .55 |
| OTCHEY | FINAL_SHARE_INSTRUCTION | .42 |

The English defaults and all substantive V20–V26 conclusions are unchanged.
Twenty-three event rows and four lexicon rows receive corrected metadata.

The complete descendant chain was regenerated in dependency order: V20, V21,
V22, V23, V24, V25 and V26. V20 validation now requires every confidence to be
numeric in `[0,1]` and rejects numeric source-class labels. The independent V27
validator checks five complete 776-row descendant ledgers and finds zero bad
confidence or source-class values.

No f84 or f84r source was opened or queried.
