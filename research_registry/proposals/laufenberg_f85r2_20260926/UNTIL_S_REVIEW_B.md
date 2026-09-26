# Independent review B: frozen whole-S UNTIL draft

2026-09-26, 20:48 UTC. Review of the frozen authoring packet, not a semantic execution or a new manuscript observation. Original files are unchanged. No new images, sources, target surfaces, or reserve material were accessed. The only target-file inspection was the already-owned GDT1042 f85r2 projection needed to check literal coverage and the declared input discrepancy.

**Finding:** the draft gives every ZL S group a declared role and supplies two written participant introductions. It preserves the three raw550 seed meanings and the repeated `or` reference. Its full temporal and argument interpretation remains **incomplete**: the type labels and prose attachments do not yet specify event identity, ordered argument composition, event modality, or interval extent sufficiently for a mathematical main-versus-AFTER verdict. This is neither a demonstrated type contradiction nor a demonstrated consistent complete model. In particular, the packet does not establish two formal contradictions for AFTER.

## Frozen documents and input equivalence

Reviewed [selection decision](UNTIL_S_EXPLORATION_DECISION.md), [raw550](ideas/20_event_boundary_until.json), [freeze receipt](until_s_draft/FREEZE_RECEIPT.json), [draft](until_s_draft/DRAFT.json), [occurrence inventory](until_s_draft/ASSIGNED_OCCURRENCES.tsv), and the **nested** [author report](until_s_draft/UNTIL_S_DRAFT_REPORT.md). Receipt hashes match:

| Frozen file | SHA256 |
|---|---|
| DRAFT.json | `f72399c29226bd673cdfa9b858a4219554fb96cfe378577ba6858e69cee32b19` |
| ASSIGNED_OCCURRENCES.tsv | `a9377152845a870e70fc733e856b6f6ad9b758068be2c2368f55a9cac9851161` |
| UNTIL_S_DRAFT_REPORT.md | `e10352da9fdbb036614c6be7de1455179173bbac79eeeffbae81435a45e1afb4` |

The selection decision names GDT1042 `artifacts/native_groups.tsv`, SHA256 `e50307f834b04ff2ce17a97f14fd2c7b3f24b4818bc7fda3f57c372afc6b9d3c`. The author instead names `artifacts/guarded_projection.tsv`, SHA256 `489c3960116c88f76de39187eef3d2f9d3dd68d3c2e514f54abe7a2294d185e9`. This is a declared-artifact deviation, but **not a change to the actual target rows or boundaries**. Both have 473 rows, identical group identities, and identical shared edition, locus, group index/count, paragraph-start/end, separator, and literal raw-string fields. The comparison was a document-integrity check, not a semantic test; no validator or decoder was authored.

## Literal ownership and alternatives

The five authored units account for all 26 ZL groups in order:

| Loci | Groups | Written ownership proposed by the author |
|---|---:|---|
| .12 | 4 | `otchs` introduces nutrient x; `shedor` introduces recipient r; `chey sorain` supplies the first guard and boundary. |
| .13 | 5 | `or` resumes x; `shedy` supplies the adhesion predicate; `tedy sodaiiin` locates it at r; `chy` coordinates the next clause. |
| .14 | 4 | `ytedar` relates presentation to adhesion; `chz[s:r]` and `aiin` resume x/r; `arody` supplies presentation. |
| .15 | 5 | `ypshedy` supplies departure; `dar chedy or` supplies its proposed participant/source phrase; `am` supplies the prevention claim. |
| .16–17 | 8 | `oteey qodaiin odain an` supplies attracting faculty, process, x and destination r; `chey orar oldar ain` supplies the second boundary phrase. |

All 24 ZL types have an entry: three fixed seed meanings and 21 newly assigned whole-form meanings, with no subword derivations. Raw550's `orar` is arrival/presentation to the bound recipient; the draft retains this rather than assigning a different event. The selection note's compressed wording about arrival completion does not erase the original entry or resolve the separate `oldar` contribution.

The inventory contains all and only the 125 exact matches of those 24 forms in the owned projection. Their dictionary meanings/types and full literal locus contexts agree with the draft. They are alternate transcription counts, not 125 independent manuscript observations:

| Reader | All assigned positions | Assigned positions within S | Unassigned S positions | Assigned positions outside S |
|---|---:|---:|---:|---:|
| ZL3b | 45 | 26 | 0 | 19 |
| IT2a | 41 | 24 | 2 | 17 |
| RF1b | 39 | 23 | 3 | 16 |

Each reader has 26 S groups and 24 S types. The literal unassigned alternatives are IT .14/G002 `ch?s`, .16/G002 `qodain`; RF .13/G002 `{ch'}edy`, .14/G002 `ch@152;s`, .15/G001 `yfshe@152;y`. They receive no aliases. Consequently IT lacks the assigned final attraction predicate and RF lacks the assigned first adhesion predicate, among other gaps. The ZL construction is not a complete parse of either alternative reader.

The 52 assigned positions outside S are inventoried, not interpreted in complete clauses. Their same-value entries are retained, but references there have not acquired a written local binder merely by appearing in this table. For example, the N.2 context `sain or or aiin opchdy` contains two x references and an r reference before the S introductions. Paragraph-S binding does not by itself provide their cross-paragraph or cataphoric scope. This is an unresolved transfer obligation, not a contradiction inferred from an unparsed passage.

## What is concretely bound, and what is still missing

The nutrient and recipient are genuinely represented by two initial written forms in the hypothesis. Later x/r references need no image-selected person or unmentioned portion. The two S occurrences of `or` retain exactly the same SubstanceRef denotation, in the adhesion clause and departure phrase. The deictic relation entries `chedy`, `an`, and `ain` openly contain r; they are costly assigned meanings but are not silently inserted participants.

Participant identity does not settle event identity. `arody` is a presentation predicate; `orar` names arrival/presentation; `ytedar` references an adhesion event. The packet never supplies an event binder or a unique-episode rule identifying their instances. Repeated x/r can undergo several presentation episodes. The intended single sequence is reasonable as an explicit extra hypothesis, but it is not already forced by two participant binders.

The claimed “complete typed parse” is a complete group-to-role rendering rather than a fully specified typed derivation:

1. `Predicate`, `EventPredicate`, `EventNoun`, `EventModifier`, and the relation labels do not give argument signatures or ordered application rules. In .15, `dar` must associate with the later `or` across `chedy`. The English ordering does not supply that construction.
2. `am` packs prevention plus **two distinct prohibited outcomes**, adhesion and complete assimilation. It might become a predicate taking a departure condition, rather than a nullary sentence macro, but its event/participant arguments and reference to the earlier stages are not specified. It cannot be counted as an unanalysed primitive PREVENT while its two outcome meanings go uncounted.
3. `ypshedy` names continued withdrawal without specifying whether it introduces an actual departure event, a kind of event, or a hypothetical condition in a general law. This matters: a generic departure-prevention law can coexist with the asserted adherence. Treating withdrawal as actual and prevention as categorical could instead conflict. The frozen grammar has not chosen between these readings, so this review does not declare the draft inconsistent.
4. `sorain` already denotes completion of assimilation; `chey` refers to completion of its supplied Event. In the second phrase, `oldar` contributes completion to `orar`, followed by `ain`. An endpoint interpretation may make these expressions coherent, but no typed application or point/process convention specifies the composition. Dropping `oldar`, silently treating completion as idempotent, or converting an endpoint to an ongoing event would be an added rule.
5. Both guards take following event expressions, but their **host attachment** differs: the first guard precedes `shedy` across a line; the second follows `qodaiin`. The report's shared “forward scope” description is accurate for their operands, not a complete uniform rule for locating the guarded process. These explicit attachment choices are assumptions, not independently recovered syntax.

The declared three grammar constructions therefore remain an author count, not an audited exhaustive grammar. Ordinary clause composition, the discontinuous source phrase, event references, and modality have not been reduced to a fixed set of productions. Likewise, the 21 whole-form entries do not constitute a count of only 21 elementary semantic choices: `am` is visibly compound, several words duplicate participant references, and `shedy` joins adherence with remaining attached. These costs should stay separate from the accurate 21-form count.

The English display repeats adhesion in its opening two sentences; there is only one written `shedy`. I treat this as a repeated display of the same proposed assertion, not as a second written event or independent condition.

## Manual temporal assessment and source boundary

No numerical trace or semantic executor is warranted by the present type contract. The intended distinction is nonetheless identifiable: main chey imposes cessation at an assimilation boundary for adhesion and at a presentation boundary for attraction; AFTER places the respective guarded activity later. These are consequences of guessed values and attachments, not observed temporal relations in Voynich.

For a conditional first contrast, let m be assimilation completion and a the start of the **same** adhesion episode. If the source-order premise requires a < m and AFTER requires a > m, those inequalities conflict. The episode identity, relation of stage occurrence to state duration, and meaning of “after” must all be fixed before this is a proof about the draft. `shedy`'s adhesion/remaining-attached wording currently leaves those distinctions open. This review does not infer an interval model merely from its English predicate label.

The proposed second contradiction is weaker. Galen III.1 calls presentation the end/goal of attraction; a teleological goal alone does **not** say every attraction activity ceases exactly at presentation, nor does it formally exclude later attraction. An additional episode/causal or cessation premise would be needed. That premise is not supplied by quoting “goal.” The frozen report's claim that AFTER conflicts with both boundaries should therefore remain an unproved model claim, not a two-case formal result.

The source and target also must not exchange omissions. Complete Galen III.1 distinguishes presentation, adhesion and assimilation, discusses time and continuing departure, argues for a resident retentive faculty, and makes its final inference conditional on purposeful Nature. The draft honestly lists omissions: alteration/general nutritive faculty, proper juice, duration, other recipients/repeated position changes, the resident retentive faculty and its necessity, and the theological/teleological inference. Its strict cessation at assimilation is an extra premise; the source does not explicitly state it. No adjacent uterine example from III.2–3 is admitted as a repair. Source completeness has therefore not been achieved, though a deliberately condensed hypothetical S reading is allowed.

## Disposition

Retain the frozen packet as a complete **literal ZL allocation and prose hypothesis**, with real written participant introductions and two intended chey applications. Retain its known alternative-reader gaps and outside-S reference obligations. Stop short of a complete formal fit, semantic consistency PASS, source identification, or rejection of AFTER. The decision-changing next requirement is a fixed ordered argument/event/reference contract addressing the specific gaps above, not further synonym filling or a simulator implementing the current English by fiat. No such repair is supplied here. Confirmed translated words remain zero.
