# GDT993 — a complete conditional reading survives, with substantial ambiguity

**Decision: retain the four internally consistent ZL variants as one consequence class; no translated word is confirmed.** All32 registered full readings were executed after public registration and checked by a separately implemented parser/replayer. Four survive;28 contradict their own physical, safety or final-goal conditions. No outcome repairs were made.

This establishes executable internal coherence of a deliberately constructed reading of all63 groups, not an independently discovered source match. Its47 whole-word meanings include41 newly assigned values,36 of them singletons. Six inherited animal/agent/boat/return guesses remain assumptions. The historical source solution and manually written trace were known before registration. Productive word composition, supported by the structural baseline, is not explained by this whole-gloss construction.

Registration commit: `3d3b6f24adbe4175bfc1d3ec02624c8e3f2d5fe7`. Target execution: `2026-09-20T12:46:04.146316+00:00` to `2026-09-20T12:46:04.159107+00:00`. [Independent implementation validation](artifacts/VALIDATION.json): PASS,32cases,3reader parses,14diagnostics. Both implementations have the same root author; implementation agreement is not independent semantic evidence. Six synthetic checks preceded registration. The original08:25 preparation checkpoint was missed before registration; the disclosed resumed checkpoint was13:00UTC. The intervening timestamp gap is not claimed as active research.

## Entire proposed passage and concrete consequences

All meanings below are hypotheses. M=attendant, B=boat, W=wolf, G=goat, C=cabbage are the frozen source labels. L/R are the two banks. The boat initially co-located with M is an explicit first-trip presupposition, not another translated word. The parser received the complete stream and fixed productions, not these predicted clause boundaries. It returned one parse under that finite grammar; all63 predicted position ownerships matched. This is not historical parsing uniqueness.

| Clause / source groups | Complete literal text | Assumed reading | Declared consequence |
|---|---|---|---|
| S01 f83r.18:1-5 | pdalshdy shocphedy otor shedy opshedy | Initially the cargo are together with M at L. | Initial positions M=W=G=C=L. B is explicitly required at M by S05; no previous boat movement is supplied. |
| S02 f83r.18:6-9 | otshdy qokedol shdy soldy | That whole initial group must reach R without harm. | Goal only; no voyage. |
| S03 f83r.19:1-6 | sar shedaiin ockhey sain ched shedy | Unsafe cargo pairings are forbidden when the attendant is absent. | Requires each listed pair never to share a bank without M during the narrated plan. |
| S04 f83r.19:7-11 | qetal dal shedy shey lchedy | At most one cargo in addition to M; for example W. | Capacity is one Cargo plus M. EXAMPLE does not move W. |
| S05 f83r.20:1-4 | solkeedy qoteedy qokeey qokedy | With B, take G outward to R. | Voyage1: M+B+G, L to R. |
| S06 f83r.20:5-5 | sol | Then. | No voyage. |
| S07 f83r.20:6-7 | cheeety qokedy | Return to L without G. | Voyage2: M+B only, R to L. |
| S08 f83r.20:8-9 | qoky saiin | Ferry the first-named Cargo to the opposite bank. | Voyage3: M+B+W, L to R. |
| S09 f83r.21:1-3 | solkeedy qokedy otedy | With G, return to L. | Voyage4: M+B+G, R to L. |
| S10 f83r.21:4-4 | sol | Then. | No voyage. |
| S11 f83r.21:5-10 | chedy lkedy qokchedy qokedy chckhdy sar | C paired with G, unattended, would be unsafe. | Declares Unsafe(C,G) under absence of M; does not claim M is absent in the current actual state. |
| S12 f83r.22:1-2 | schedair otchedy | Likewise the other Cargo. | Declares Unsafe(W,G) under absence of M. OTHER is not resolved by consulting which return is needed. |
| S13 f83r.22:3-5 | qokeedy chedain chedy | Convey C outward next. | Voyage5: M+B+C, L to R. |
| S14 f83r.22:6-7 | qotedaiin otaiin | Leave that cargo there. | C remains at R through the following return. No second transport and no new cargo. |
| S15 f83r.22:8-9 | otedy ldy | Return alone to L. | Voyage6: M+B only, R to L. |
| S16 f83r.23:1-5 | tchedy qotedy qokal shedy qokedy | Finally, outward travel together M and G. | Voyage7: M+B+G, L to R; last voyage. |
| S17 f83r.23:6-9 | shecthedy shecthy otor chedy | Joining the remaining cargo, together with C. | Asserts co-location at the result bank. No eighth voyage. |
| S18 f83r.24:1-6 | soiiin checthy chety otaiin olsaly shedy | Thus all cargo are unharmed there, attended by M. | Claims the whole stated goal, including preserved identity and safe history; not just a noun inventory. |

The surviving execution contains precisely the following seven voyages. Declarations, explanation and result clauses create no additional movement. All initial/final obligations and all intermediate safety conditions pass.

| Voyage / clause | Cargo | M and boat after voyage | W | G | C |
|---|---|---|---|---|---|
| 1 / S05 | G | R | L | R | L |
| 2 / S07 | empty | L | L | R | L |
| 3 / S08 | W | R | R | R | L |
| 4 / S09 | G | L | R | L | L |
| 5 / S13 | C | R | R | L | R |
| 6 / S15 | empty | L | R | L | R |
| 7 / S16 | G | R | R | R | R |

## Every registered candidate

The five settings below completely specify each variant together with the preceding fixed full reading. `exclude` changes cheeety (EXCLUDING/WITH followingCargo); `first` changes saiin (FIRST/RECENT distinct priorCargo); `other` changes otchedy (unique OTHER outside the pair/FIRST priorCargo); `there` changes otaiin (GOAL bank/CURRENT agent bank); `copy` changes schedair (replace FIRST/SECOND argument). Every other whole meaning and production is unchanged.

Each variant had exactly one executable path or stopped prefix. A physical failure stops execution; later assertions are not counted as examined. C/G/W in the safety column identify unattended pairs in that retained prefix. Goal “unreached” is reported only after complete physical execution; “unexecuted” follows a stopped illegal move. E1–E8 group identical checked consequences. Independent confirmation capacity is0 for **every** row.

| ID | exclude | first | other | there | copy | Observed result / contradictions | Class | Independent capacity |
|---|---|---|---|---|---|---|---|---|
| ZL-P00-V00 | EXCLUDING | FIRST | OTHER | GOAL | FIRST | 7voyages;all goals/assertions/safety pass | E1 | 0 |
| ZL-P00-V01 | EXCLUDING | FIRST | OTHER | GOAL | SECOND | 7legal voyages;goal reached; unsafe S05:CW@L,S15:CW@R | E2 | 0 |
| ZL-P00-V02 | EXCLUDING | FIRST | OTHER | CURRENT | FIRST | 7voyages;all goals/assertions/safety pass | E1 | 0 |
| ZL-P00-V03 | EXCLUDING | FIRST | OTHER | CURRENT | SECOND | 7legal voyages;goal reached; unsafe S05:CW@L,S15:CW@R | E2 | 0 |
| ZL-P00-V04 | EXCLUDING | FIRST | FIRST | GOAL | FIRST | 7voyages;all goals/assertions/safety pass | E1 | 0 |
| ZL-P00-V05 | EXCLUDING | FIRST | FIRST | GOAL | SECOND | 7legal voyages;goal reached; unsafe S05:CW@L,S15:CW@R | E2 | 0 |
| ZL-P00-V06 | EXCLUDING | FIRST | FIRST | CURRENT | FIRST | 7voyages;all goals/assertions/safety pass | E1 | 0 |
| ZL-P00-V07 | EXCLUDING | FIRST | FIRST | CURRENT | SECOND | 7legal voyages;goal reached; unsafe S05:CW@L,S15:CW@R | E2 | 0 |
| ZL-P00-V08 | EXCLUDING | RECENT | OTHER | GOAL | FIRST | S08: CARGO_NOT_AT_AGENT(G);goal unexecuted | E3 | 0 |
| ZL-P00-V09 | EXCLUDING | RECENT | OTHER | GOAL | SECOND | S08: CARGO_NOT_AT_AGENT(G);goal unexecuted; unsafe S05:CW@L | E4 | 0 |
| ZL-P00-V10 | EXCLUDING | RECENT | OTHER | CURRENT | FIRST | S08: CARGO_NOT_AT_AGENT(G);goal unexecuted | E3 | 0 |
| ZL-P00-V11 | EXCLUDING | RECENT | OTHER | CURRENT | SECOND | S08: CARGO_NOT_AT_AGENT(G);goal unexecuted; unsafe S05:CW@L | E4 | 0 |
| ZL-P00-V12 | EXCLUDING | RECENT | FIRST | GOAL | FIRST | S08: CARGO_NOT_AT_AGENT(G);goal unexecuted | E3 | 0 |
| ZL-P00-V13 | EXCLUDING | RECENT | FIRST | GOAL | SECOND | S08: CARGO_NOT_AT_AGENT(G);goal unexecuted; unsafe S05:CW@L | E4 | 0 |
| ZL-P00-V14 | EXCLUDING | RECENT | FIRST | CURRENT | FIRST | S08: CARGO_NOT_AT_AGENT(G);goal unexecuted | E3 | 0 |
| ZL-P00-V15 | EXCLUDING | RECENT | FIRST | CURRENT | SECOND | S08: CARGO_NOT_AT_AGENT(G);goal unexecuted; unsafe S05:CW@L | E4 | 0 |
| ZL-P00-V16 | WITH | FIRST | OTHER | GOAL | FIRST | S09: CARGO_NOT_AT_AGENT(G);goal unexecuted; unsafe S08:CG@L | E5 | 0 |
| ZL-P00-V17 | WITH | FIRST | OTHER | GOAL | SECOND | S09: CARGO_NOT_AT_AGENT(G);goal unexecuted; unsafe S05:CW@L,S08:CG@L | E6 | 0 |
| ZL-P00-V18 | WITH | FIRST | OTHER | CURRENT | FIRST | S09: CARGO_NOT_AT_AGENT(G);goal unexecuted; unsafe S08:CG@L | E5 | 0 |
| ZL-P00-V19 | WITH | FIRST | OTHER | CURRENT | SECOND | S09: CARGO_NOT_AT_AGENT(G);goal unexecuted; unsafe S05:CW@L,S08:CG@L | E6 | 0 |
| ZL-P00-V20 | WITH | FIRST | FIRST | GOAL | FIRST | S09: CARGO_NOT_AT_AGENT(G);goal unexecuted; unsafe S08:CG@L | E5 | 0 |
| ZL-P00-V21 | WITH | FIRST | FIRST | GOAL | SECOND | S09: CARGO_NOT_AT_AGENT(G);goal unexecuted; unsafe S05:CW@L,S08:CG@L | E6 | 0 |
| ZL-P00-V22 | WITH | FIRST | FIRST | CURRENT | FIRST | S09: CARGO_NOT_AT_AGENT(G);goal unexecuted; unsafe S08:CG@L | E5 | 0 |
| ZL-P00-V23 | WITH | FIRST | FIRST | CURRENT | SECOND | S09: CARGO_NOT_AT_AGENT(G);goal unexecuted; unsafe S05:CW@L,S08:CG@L | E6 | 0 |
| ZL-P00-V24 | WITH | RECENT | OTHER | GOAL | FIRST | 7legal voyages;W remains L;goal unreached; assertions S17:JOINING_RESULT_FALSE,S18:FINAL_LOCAL_ASSERTION_FALSE; unsafe S13:GW@L | E7 | 0 |
| ZL-P00-V25 | WITH | RECENT | OTHER | GOAL | SECOND | 7legal voyages;W remains L;goal unreached; assertions S17:JOINING_RESULT_FALSE,S18:FINAL_LOCAL_ASSERTION_FALSE; unsafe S05:CW@L,S08:CW@L | E8 | 0 |
| ZL-P00-V26 | WITH | RECENT | OTHER | CURRENT | FIRST | 7legal voyages;W remains L;goal unreached; assertions S17:JOINING_RESULT_FALSE,S18:FINAL_LOCAL_ASSERTION_FALSE; unsafe S13:GW@L | E7 | 0 |
| ZL-P00-V27 | WITH | RECENT | OTHER | CURRENT | SECOND | 7legal voyages;W remains L;goal unreached; assertions S17:JOINING_RESULT_FALSE,S18:FINAL_LOCAL_ASSERTION_FALSE; unsafe S05:CW@L,S08:CW@L | E8 | 0 |
| ZL-P00-V28 | WITH | RECENT | FIRST | GOAL | FIRST | 7legal voyages;W remains L;goal unreached; assertions S17:JOINING_RESULT_FALSE,S18:FINAL_LOCAL_ASSERTION_FALSE; unsafe S13:GW@L | E7 | 0 |
| ZL-P00-V29 | WITH | RECENT | FIRST | GOAL | SECOND | 7legal voyages;W remains L;goal unreached; assertions S17:JOINING_RESULT_FALSE,S18:FINAL_LOCAL_ASSERTION_FALSE; unsafe S05:CW@L,S08:CW@L | E8 | 0 |
| ZL-P00-V30 | WITH | RECENT | FIRST | CURRENT | FIRST | 7legal voyages;W remains L;goal unreached; assertions S17:JOINING_RESULT_FALSE,S18:FINAL_LOCAL_ASSERTION_FALSE; unsafe S13:GW@L | E7 | 0 |
| ZL-P00-V31 | WITH | RECENT | FIRST | CURRENT | SECOND | 7legal voyages;W remains L;goal unreached; assertions S17:JOINING_RESULT_FALSE,S18:FINAL_LOCAL_ASSERTION_FALSE; unsafe S05:CW@L,S08:CW@L | E8 | 0 |

[Machine-readable candidate table](artifacts/CANDIDATES.tsv); [all parses, resolved references, states and violations](artifacts/CASES.json). No matching location or favorable state was selected for the result.

## What distinguishes the variants, and what does not

The four survivors are V00,V02,V04,V06. Within this stipulated32-case family, they require cheeety=return EXCLUDING G, saiin=FIRST priorCargo W, and schedair=copy replacing argument1. A recent-Cargo reference requests G from the opposite bank at S08; WITH-G plus FIRST-W requests nonlocal G at S09. WITH-G plus RECENT-G completes seven legal trips but never transports W, contradicting the result and conclusion. These are conditional deductions, not recovered dictionary values.

Safety contributes an additional distinction:8variants satisfy physical availability and final assertions when hazards are disabled; only4 satisfy the written safety interpretation. Replacing argument2 yields the C-W danger pair, violated after S05 and S15 even on the otherwise correct trip sequence. The disabled-safety run is a diagnostic, not a full alternative reading of the safety clauses.

All32 cases collapse into8 consequence classes of4. otchedy=OTHER and FIRST both refer to W here. otaiin=GOAL and CURRENT both resolve to R where actually evaluated. No candidate can choose between these meanings. Instructions versus a reported plan, bank renaming, and the synonymous truth conditions assigned to TAKE_OUT/CONVEY_OUT remain unseparated. Illegal early prefixes do not test later there-references. The four survivors supply no probability, uniqueness or restart-agreement argument.

On the fixed surviving trace,4/8 undirected danger graphs are safe: no edges, W-G alone, G-C alone, or both. Therefore a safe trace alone does not recover either asserted danger edge. The model gets those edges from guessed safety clauses. With the source wolf/goat/cabbage dietary relations assumed,2/6 name permutations survive: W=wolf/G=goat/C=cabbage and W=cabbage/G=goat/C=wolf. G being central is conditional on that external source choice; wolf versus cabbage is still exchangeable. These14 rows are assumption diagnostics, not additional manuscript readings or evidence of identified animals. [All diagnostic outcomes](artifacts/DIAGNOSTICS.json).

## Source uncertainty and confirmation capacity

| Reading | Entire selected raw source | Observed coverage | Interpretation |
|---|---|---|---|
| ZL3b | 63groups | 1complete parses;unknowns: none | PARSED_CONDITIONALLY;strict anchor=False |
| IT2a | 64groups | 0complete parses;unknowns: pdal, qokedal, sor | FROZEN_READING_NO_FULL_COVERAGE;strict anchor=True |
| RF1b | 63groups | 0complete parses;unknowns: qokedal, she@152;aiin, she@152;y, she@152;y, l, qoke@152;y, ote@152;y, solchedy, qote@152;aiin, ote@152;y, ot@221;r, che@152;y | NO_COMPLETE_PARAGRAPH_CONTRACT;strict anchor=False |

The ZL sol/chedy seam at f83r.21:4–5 is explicitly uncertain. GDT928 strict anchor eligibility remainsfalse. IT has definite spaces but pdal shdy versus pdalshdy, qokedal versus qokedol and sor versus sar; the unchanged lexicon yields no full IT reading. No spelling/spacing fix is licensed. RF retains raw entities and different joins, and has no whole-paragraph contract. Its missing capacity is not a semantic contradiction. ZL/IT/RF are alternate readings of the same manuscript, never three independent confirmations.

The entire physical leaf83 was already exposed. Selection and extra confirmation cannot be separated onto independent physical leaves in this experiment: capacity0. Native inspection before selection did not establish an independently identified wolf, goat, cabbage or seven-voyage scene. The associated picture supplies no animal-name support; because a literal text-picture identity was not asserted, absence alone is not a refutation of accompanying prose. f84/f84r, all reserves and unadmitted f116v remain closed. No outside contact.

## Research decision

Retain the four coherent full-passage hypotheses as one unresolved class and close this finite audit. The gain is a complete reproducible candidate whose reference, physical and safety consequences can now be stated precisely. It is not evidence that the passage actually tells this story. Do not improve its success by changing failed variants, splitting words or adding exceptions. No whole-search control, likelihood model or independent meaning test supports a significance claim.

The next useful question is whether the unchanged whole meanings and stated constructions constrain a complete additional already-exposed passage, with all conflicting inherited readings retained. Review the separately supplied adjacent weaving draft as a rival, not confirmation: its inherited qokedy=cloth conflicts with this candidate qokedy=goat under the single-meaning contract. A shared reading would need an explicit new scientific proposal and a distinct falsifier; neither a generic polysemy excuse nor opening reserves follows from this one coherent paragraph. New data or a separately declared meaning-bearing consequence is required before reopening the closed variants.

Confirmed words:0. Independent meaning confirmation:0. Significance:false. GDT888/913, W91, GDT344 and all previous registered failures remain unchanged.

Reproduce with `python3 experiments/yolo/gdt993_complete_transport_consequence_audit/src/run.py` and then `src/validate.py` at the same experiment path. The public registration receipt and scientific hashes are checked. `src/render_report.py` only renders retained outputs; it was added after execution and is not a scientific input.
