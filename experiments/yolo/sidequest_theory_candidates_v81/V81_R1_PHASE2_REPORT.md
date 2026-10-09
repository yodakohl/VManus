# V81 R1 Phase-2 atomic portable-vocabulary audit

## Result

**No new portable word survives.** All 30 centrally revealed cards are rejected for a new lexical default. There are zero `PROMOTE` decisions and zero `NEAR` decisions, so the V80 working dictionary and all 94 supplied affected statements remain unchanged.

The best attempted new mapping is `T008 → HIER`; it fails both the historical semantic-category gate and the invariant replacement gate. The strongest apparent rival is `T002 → UND`, but that is already completely explained by the silent `FORMAL_LINK_OR_SLOT` control with optional master gloss `ET?`, and the frozen source row `Que` is not a semantic attestation of “and.”

## Frozen inputs and phase boundary

R1 used only the frozen Phase-1 artifacts, the central V81 protocol, and the four authorized target artifacts. The source freeze remained byte-identical:

- R1 inventory SHA-256: `9ef4d4e265aa2d39042773b2ffa91a82e01787dfcff93e1a5ab88fc189eeb549`
- R1 source report SHA-256: `0eed2a082f791ba78cc7b2f7d09239bae93b7009aafd568e707303bb9ed41ebe`
- R1 source-freeze SHA-256: `fe42fec87f56e88c381e29443abad2654898e350744668c2fde717f0cb497e2a`

The central target-freeze SHA-256 is `76b102a61f30ca9aa507a6c42b5315f6c43e75628d19c0ebe10ef835ec44a06d`. Its bound target hashes all matched: manifest `c2c2ad1bd6418ed7a332d6ed948192f469ce8fd64e6cd4c5c5c87e33b76e2b04`, occurrence packet `b6cc5afd9421a64aaec6644f095160a42f8e7999bd63ea3151a05860dd9896ee`, and affected statements `8a0b627902605ca59a7f25f1d148d1fdc0b00f63e53a1f5617409e0af25ca2b7`.

The revealed panel has 30 cards, 217 visible occurrences, 216 independent source positions, and 94 affected statements. No surface spelling or component coordinate was revealed or used.

## Historical-source control

All six Phase-1 rows are genuine exact entry↔code pairs. That does not make all six semantic word attestations. In Meister's printed key they form an orthographic block: `Q`, `Que`, `Qui`, `Quo`, `e duplicatum`, and `s duplicatum`, adjacent to the excluded `Qua`, `che`, cipher alphabets, and null signs. Their exact historical role is therefore letter/cluster encoding and doubled-letter handling.

The controls are disclosed as follows:

- `R1-MO1-001 Q → 4` supplies no ordinary German word category and was not assigned to a card.
- Treating `Que` as Latin enclitic `-que = UND`, `Qui` as Italian `HIER`, or `Quo` as Latin `WOHIN` would import presumed-language semantics not stated by the historical row.
- Treating `e duplicatum` or `s duplicatum` as generic `DOPPELT` or `WIEDERHOLEN` broadens a specific orthographic instruction into an operational word.

These are valid historical controls but not semantic licenses. No target was chosen by code-string, Voynich surface, substring, sound, shape, coordinate, picture, or PAGE_HOST resemblance.

## Five complete stress tests

Although the historical semantic gate already fails, R1 audited every occurrence of the five strongest possible overreadings. The occurrence audit contains all 48 relevant visible occurrences.

| Candidate | Occurrences | Occurrence result | Fatal reason | Strongest rival |
| --- | ---: | --- | --- | --- |
| `Que / T002 → UND` | 19 | Optional `ET?` is contextually compatible everywhere | `Que` is an orthographic cluster, not a semantic enclitic attestation; no new statement content is added | silent `FORMAL_LINK_OR_SLOT` |
| `Qui / T008 → HIER` | 10 | Locative modification is possible, but nine occurrences still require “führen” and one requires a skin-location argument | presumed Italian semantics plus an omitted action/argument | local station/owner slot and exemplar value |
| `e duplicatum / T010 → DOPPELT` | 9 visible, 8 independent | Only E180 is a visible copy; it contributes zero and explicitly must not be spoken twice | the other eight occurrences are relation entries | `FORMAL_RELATION_OR_ENTRY`, optional `PER?`, and catchword copy |
| `s duplicatum / T014 → WIEDERHOLEN` | 7 | Only E034 explicitly describes a repeated note; other occurrences assign fresh, first, salve, second, or continued preparations | specific doubled `s` is broadened, while the card's action changes by record | exemplar-copy/continuation |
| `Quo / T026 → WOHIN` | 3 | All occurrences are direction-related, but an interrogative does not replace “lower outlet” | presumed Latin semantics and deletion of the goal argument | directional exemplar/owner slot; no drawn arrow |

None is `NEAR`: each has a fatal historical semantic failure, and each would also require either silent formal content to become spoken or occurrence-specific arguments to be supplied. Those are category changes, not small repairs.

## Complete 30-card decision

The 30-row decision table publishes every gate and repair cost. Four pre-existing formal controls remain unchanged:

- `T001`: `FORMAL_PARAMETER_CHANNEL__NOT_A_WORD`;
- `T002`: `FORMAL_LINK_OR_SLOT`, optional `ET?` only;
- `T010`: `FORMAL_RELATION_OR_ENTRY`, optional `PER?` only, with one zero-contribution visible copy;
- `T016`: `FORMAL_RELATION_SLOT_CHANNEL__NOT_A_WORD`.

The other 26 cards retain `EXEMPLAR_VALUE_UNKNOWN`. Several have strikingly repeated master-memorized exemplar expansions—readiness/close (`T004`), rinse (`T009`), drain (`T011`), temper (`T012`), measured share (`T013`, `T028`), settle (`T023`), heat once (`T025`), strain once (`T029`), and gentle heat (`T030`). Repetition alone cannot pass the exact historical-entry gate. Other cards also fail invariance directly: `T003`, `T005`, `T006`, `T007`, `T014`, `T015`, `T017`, `T019`, `T021`, and `T027` require materially different occurrence values.

`T019` additionally fails the two-record requirement: its four positions all belong to one formal record. Every other card meets the mechanical two-record count, but no card passes the complete admission conjunction.

## Statements and controls

No promoted or near-promoted candidate exists, so the affected-statement revision TSV correctly has zero data rows. This is not missing coverage: the validator checks that the decision table has no `PROMOTE` or `NEAR` status and therefore requires an empty revision set. All 94 centrally supplied statements retain their existing continuous readings.

The silent formal-role, frequency, position, Close/terminal, owner, and exemplar-copy explanations are explicitly compared in the full decision table. `EXEMPLAR_VALUE_UNKNOWN`, `FORMAL_LINK_OR_SLOT`, and `FORMAL_RELATION_OR_ENTRY` remain preferable controls.

## Blinding and seals

R1 did not read any sibling V81 output, manuscript page or image, transcription, or V80 artifact directly. The supplied target surface remained withheld. `f84` and `f84r` remained sealed. No files were committed or pushed.

Final conclusion: `NEW_PORTABLE_WORD_SURVIVES=false`.
