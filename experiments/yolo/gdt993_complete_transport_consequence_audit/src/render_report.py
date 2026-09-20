"""Render retained results; no fitting, source access or case selection."""
import json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
result=read(A/'RESULT.json');cases=read(A/'CASES.json');diagnostic=read(A/'DIAGNOSTICS.json')
draft=read(R/read(E/'src/SPEC.json')['source_draft'])
groups={identifier:i+1 for i,g in enumerate(result['equivalence_classes']) for identifier in g}
lines=['# GDT993 — a complete conditional reading survives, with substantial ambiguity',
'',
'**Decision: retain the four internally consistent ZL variants as one consequence class; no translated word is confirmed.** All32 registered full readings were executed after public registration and checked by a separately implemented parser/replayer. Four survive;28 contradict their own physical, safety or final-goal conditions. No outcome repairs were made.',
'',
'This establishes executable internal coherence of a deliberately constructed reading of all63 groups, not an independently discovered source match. Its47 whole-word meanings include41 newly assigned values,36 of them singletons. Six inherited animal/agent/boat/return guesses remain assumptions. The historical source solution and manually written trace were known before registration. Productive word composition, supported by the structural baseline, is not explained by this whole-gloss construction.',
'',
'Registration commit: `'+result['publication_commit']+'`. Target execution: `'+result['started_utc']+'` to `'+result['completed_utc']+'`. [Independent implementation validation](artifacts/VALIDATION.json): PASS,32cases,3reader parses,14diagnostics. Both implementations have the same root author; implementation agreement is not independent semantic evidence. Six synthetic checks preceded registration. The original08:25 preparation checkpoint was missed before registration; the disclosed resumed checkpoint was13:00UTC. The intervening timestamp gap is not claimed as active research.',
'',
'## Entire proposed passage and concrete consequences',
'',
'All meanings below are hypotheses. M=attendant, B=boat, W=wolf, G=goat, C=cabbage are the frozen source labels. L/R are the two banks. The boat initially co-located with M is an explicit first-trip presupposition, not another translated word. The parser received the complete stream and fixed productions, not these predicted clause boundaries. It returned one parse under that finite grammar; all63 predicted position ownerships matched. This is not historical parsing uniqueness.',
'',
'| Clause / source groups | Complete literal text | Assumed reading | Declared consequence |',
'|---|---|---|---|']
for c in draft['clauses']:
    lines.append('| '+f"{c['id']} {c['locus']}:{c['first_group']}-{c['last_group']}"+' | '+c['raw']+' | '+c['reading']+' | '+c['consequence']+' |')
lines+=['','The surviving execution contains precisely the following seven voyages. Declarations, explanation and result clauses create no additional movement. All initial/final obligations and all intermediate safety conditions pass.','',
'| Voyage / clause | Cargo | M and boat after voyage | W | G | C |','|---|---|---|---|---|---|']
for i,t in enumerate(cases[0]['paths'][0]['trace'][1:],1):
    s=t['positions'];lines.append(f"| {i} / {t['clause']} | {t['load'] or 'empty'} | {s['M']} | {s['W']} | {s['G']} | {s['C']} |")
lines+=['','## Every registered candidate',
'',
'The five settings below completely specify each variant together with the preceding fixed full reading. `exclude` changes cheeety (EXCLUDING/WITH followingCargo); `first` changes saiin (FIRST/RECENT distinct priorCargo); `other` changes otchedy (unique OTHER outside the pair/FIRST priorCargo); `there` changes otaiin (GOAL bank/CURRENT agent bank); `copy` changes schedair (replace FIRST/SECOND argument). Every other whole meaning and production is unchanged.',
'',
'Each variant had exactly one executable path or stopped prefix. A physical failure stops execution; later assertions are not counted as examined. C/G/W in the safety column identify unattended pairs in that retained prefix. Goal “unreached” is reported only after complete physical execution; “unexecuted” follows a stopped illegal move. E1–E8 group identical checked consequences. Independent confirmation capacity is0 for **every** row.',
'',
'| ID | exclude | first | other | there | copy | Observed result / contradictions | Class | Independent capacity |',
'|---|---|---|---|---|---|---|---|---|']
for c in cases:
    v=c['variant'];p=c['paths'][0];parts=[]
    if p['consistent']:parts.append('7voyages;all goals/assertions/safety pass')
    else:
        f=p['physical_failure']
        if f:parts.append(f["clause"]+': '+','.join(f['reasons'])+'('+str(f['attempted_load'])+');goal unexecuted')
        elif not p['goal_reached']:parts.append('7legal voyages;W remains L;goal unreached')
        else:parts.append('7legal voyages;goal reached')
        if p['assertions']:parts.append('assertions '+','.join(x['clause']+':'+x['reason'] for x in p['assertions']))
        if p['safety_violations']:parts.append('unsafe '+','.join(x['after']+':'+''.join(x['pair'])+'@'+x['bank'] for x in p['safety_violations']))
    lines.append('| '+c['id']+' | '+' | '.join(v.values())+' | '+'; '.join(parts)+f" | E{groups[c['id']]} | 0 |")
lines+=['','[Machine-readable candidate table](artifacts/CANDIDATES.tsv); [all parses, resolved references, states and violations](artifacts/CASES.json). No matching location or favorable state was selected for the result.',
'','## What distinguishes the variants, and what does not',
'',
'The four survivors are V00,V02,V04,V06. Within this stipulated32-case family, they require cheeety=return EXCLUDING G, saiin=FIRST priorCargo W, and schedair=copy replacing argument1. A recent-Cargo reference requests G from the opposite bank at S08; WITH-G plus FIRST-W requests nonlocal G at S09. WITH-G plus RECENT-G completes seven legal trips but never transports W, contradicting the result and conclusion. These are conditional deductions, not recovered dictionary values.',
'',
'Safety contributes an additional distinction:8variants satisfy physical availability and final assertions when hazards are disabled; only4 satisfy the written safety interpretation. Replacing argument2 yields the C-W danger pair, violated after S05 and S15 even on the otherwise correct trip sequence. The disabled-safety run is a diagnostic, not a full alternative reading of the safety clauses.',
'',
'All32 cases collapse into8 consequence classes of4. otchedy=OTHER and FIRST both refer to W here. otaiin=GOAL and CURRENT both resolve to R where actually evaluated. No candidate can choose between these meanings. Instructions versus a reported plan, bank renaming, and the synonymous truth conditions assigned to TAKE_OUT/CONVEY_OUT remain unseparated. Illegal early prefixes do not test later there-references. The four survivors supply no probability, uniqueness or restart-agreement argument.',
'',
'On the fixed surviving trace,4/8 undirected danger graphs are safe: no edges, W-G alone, G-C alone, or both. Therefore a safe trace alone does not recover either asserted danger edge. The model gets those edges from guessed safety clauses. With the source wolf/goat/cabbage dietary relations assumed,2/6 name permutations survive: W=wolf/G=goat/C=cabbage and W=cabbage/G=goat/C=wolf. G being central is conditional on that external source choice; wolf versus cabbage is still exchangeable. These14 rows are assumption diagnostics, not additional manuscript readings or evidence of identified animals. [All diagnostic outcomes](artifacts/DIAGNOSTICS.json).',
'','## Source uncertainty and confirmation capacity','',
'| Reading | Entire selected raw source | Observed coverage | Interpretation |','|---|---|---|---|']
for edition,r in result['reader_results'].items():
    unknown=', '.join(x['raw'] for x in r['unknown_groups']) or 'none'
    lines.append(f"| {edition} | {r['groups']}groups | {r['parse_count']}complete parses;unknowns: {unknown} | {r['status']};strict anchor={r['strict_anchor_eligible']} |")
lines+=['',
'The ZL sol/chedy seam at f83r.21:4–5 is explicitly uncertain. GDT928 strict anchor eligibility remainsfalse. IT has definite spaces but pdal shdy versus pdalshdy, qokedal versus qokedol and sor versus sar; the unchanged lexicon yields no full IT reading. No spelling/spacing fix is licensed. RF retains raw entities and different joins, and has no whole-paragraph contract. Its missing capacity is not a semantic contradiction. ZL/IT/RF are alternate readings of the same manuscript, never three independent confirmations.',
'',
'The entire physical leaf83 was already exposed. Selection and extra confirmation cannot be separated onto independent physical leaves in this experiment: capacity0. Native inspection before selection did not establish an independently identified wolf, goat, cabbage or seven-voyage scene. The associated picture supplies no animal-name support; because a literal text-picture identity was not asserted, absence alone is not a refutation of accompanying prose. f84/f84r, all reserves and unadmitted f116v remain closed. No outside contact.',
'',
'## Research decision',
'',
'Retain the four coherent full-passage hypotheses as one unresolved class and close this finite audit. The gain is a complete reproducible candidate whose reference, physical and safety consequences can now be stated precisely. It is not evidence that the passage actually tells this story. Do not improve its success by changing failed variants, splitting words or adding exceptions. No whole-search control, likelihood model or independent meaning test supports a significance claim.',
'',
'The next useful question is whether the unchanged whole meanings and stated constructions constrain a complete additional already-exposed passage, with all conflicting inherited readings retained. Review the separately supplied adjacent weaving draft as a rival, not confirmation: its inherited qokedy=cloth conflicts with this candidate qokedy=goat under the single-meaning contract. A shared reading would need an explicit new scientific proposal and a distinct falsifier; neither a generic polysemy excuse nor opening reserves follows from this one coherent paragraph. New data or a separately declared meaning-bearing consequence is required before reopening the closed variants.',
'',
'Confirmed words:0. Independent meaning confirmation:0. Significance:false. GDT888/913, W91, GDT344 and all previous registered failures remain unchanged.',
'',
'Reproduce with `python3 experiments/yolo/gdt993_complete_transport_consequence_audit/src/run.py` and then `src/validate.py` at the same experiment path. The public registration receipt and scientific hashes are checked. `src/render_report.py` only renders retained outputs; it was added after execution and is not a scientific input.',
'']
(E/'REPORT.md').write_text('\n'.join(lines))
print('Rendered REPORT.md; all32candidate rows and18complete clauses.')
