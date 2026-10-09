# V81 R3 Phase 2 — atomic codebook vocabulary audit

Status: `COMPLETE__NO_NEW_PORTABLE_WORD`

NEW portable word: **NO**.

## Result

All 30 anonymous target cards were audited against all three exact Si1 source
entries. The complete panel comprises 217 central occurrences and therefore
651 source-category × occurrence decisions. Every decision is `REJECT`; there
are no `PROMOTE` or `NEAR` candidates and zero improved complete statements.

The V80 dictionary remains unchanged. `EXEMPLAR_VALUE_UNKNOWN`, the supplied
formal channels, and the optional `ET?`/`PER?` controls retain their existing
status.

## Frozen source panel

| Exact Si1 entry | Atomic default tested | Occurrences compatible | Statements improved | Decision |
|---|---|---:|---:|---|
| `Niccolo Fortibraccio` | `NICCOLO FORTIBRACCIO` | 0/217 | 0 | REJECT |
| `Duca di Milano` | `HERZOG VON MAILAND` | 0/217 | 0 | REJECT |
| `Serenissimus` | `HÖCHST DURCHLAUCHT` | 0/217 | 0 | REJECT |

The entries pass historical row identity and source granularity only. In the
supplied target contexts there is no named individual, Milanese duke or office,
or honorific addressee. Using any entry would add an external referent and
replace the supplied operational or formal context. Historical attestation
cannot license that repair.

## Complete admission-gate result

- Atomicity: pass at source-granularity level; each tested default has at most
  three words.
- Exact historical pairing: pass; three entries are represented by five exact
  raster-bound Si1 signs.
- Invariant default: fail for every card and every source entry; compatible
  candidate occurrences are 0/651.
- At least two formal records: 29 targets pass; T019 fails with one record.
- Usable in every occurrence: fail for all 30 targets.
- Improves two complete statements: fail; total improved statements are zero.
- Rival controls: win for every target without adding a word.
- Repair cost: every tested occurrence would require both an unlicensed
  person/title/honorific referent and a contextual override.

## Best mapping and strongest rivals

Best new atomic mapping: **NONE**.

The strongest target-side regularity is T004, not a source mapping. T004 occurs
12 times across three pages, four formal records, and 12 statements. All 12
occurrences are terminal and carry the same occurrence-bound readiness/ending
expansion. `Serenissimus` remains incompatible because none supplies an
honorific person or address slot. `CLOSE_OR_TERMINAL_OPERATION` explains the
regularity directly and is the stronger rival.

Across the full panel:

- T001, T002, T010, and T016 have explicit silent formal-channel rivals;
- T004, T007, T009, T011, T018, T022, T023, T025, and T029 are explained most
  strongly by CLOSE or terminal operation;
- the remaining 17 targets are better retained as owner-/record-local exemplar
  expansions or opaque exact cards;
- frequency explains why these cards entered the panel but cannot identify a
  word; position and repetition likewise supply no person, title, or honorific;
- no page owner or exemplar-copy context independently names a Si1 referent.

## Occurrence and statement coverage

Because no candidate reached `NEAR`, the occurrence audit includes every
tested candidate occurrence: 217 occurrences × three source categories = 651
rows. Each row carries the original autonomous readback, exemplar expansion,
terminal state, line crossing, packet contradiction, explicit rival, repair,
and rejection.

The statement-revision table carries all 94 centrally supplied affected
statements. With zero promoted or near candidates, every continuous reading
and formal order is byte-for-byte unchanged and marked
`UNCHANGED__NO_PROMOTED_OR_NEAR_CANDIDATE`.

## Independence advisory and seals

The Phase-1 disclosure remains prominent:
`DISCLOSED_OLD_V77_LINES__DOCUMENTARY_ELIGIBLE__STRICT_INDEPENDENCE_ADVISORY`.
The central target freeze separately accepts documentary source eligibility
while retaining this strict-independence advisory. No sibling V81 output, V80
file, manuscript page/image/transcription, surface spelling, component
coordinate, `f84`, or `f84r` was opened in this audit.

This result uses only the frozen R3 source artifacts, the central protocol, and
the four centrally frozen target artifacts authorized for Phase 2.

## Artifacts before validation

- `V81_R3_BUILD_PHASE2.py` —
  `aa64d7bf181ba02f16c0f77a348287130baf0992f5b76e1e39605832768c0fc7`
- `V81_R3_PHASE2_DECISIONS.tsv` —
  `49a0d805ab088a12bc88c8af57068979d092173a3a7d449c36bbe00aed1c210d`
- `V81_R3_PHASE2_OCCURRENCE_AUDIT.tsv` —
  `3eae7f762bf8b6fc0f7fd81876aa3c7d728a4c46554bfb5639c2bccbf65e9a0c`
- `V81_R3_PHASE2_STATEMENT_REVISIONS.tsv` —
  `681a41ff0f02fc8afe878dadd23b8768f7dee8bb21879937bcf02461525bd4e6`
- `V81_R3_VALIDATE_PHASE2.py` —
  `05e98668086383f984a9ad87f7dbaf2800897749c2febd67228cd7eace5603d9`

Preserved Phase-1 seals:

- source inventory SHA-256:
  `6ac100560aa5d0ebba24494cb513972e02a63b809e9d7fd0e2f251c2ae356ac2`;
- source freeze SHA-256:
  `89faaeb866ced5ac12da4c4e1b214470f81fa7bff5076faa16bf077f3c2376ff`;
- target freeze SHA-256:
  `76b102a61f30ca9aa507a6c42b5315f6c43e75628d19c0ebe10ef835ec44a06d`.

## Stop

R3 Phase 2 is complete. Do not add targets, open sibling results, or begin V82.
