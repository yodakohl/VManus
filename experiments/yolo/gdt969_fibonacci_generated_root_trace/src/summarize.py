"""Compact complete candidate table; does not modify the registered evaluation."""
from pathlib import Path
import csv,json,collections
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
result=json.loads((A/'RESULT.json').read_text());targets=json.loads((A/'TARGET.json').read_text())
cap=json.loads((R/'research_registry/work_batches/ten_hours_20260915/ROOT_TRACE_CAPACITY.json').read_text())
counts=collections.defaultdict(collections.Counter)
with (A/'CASE_CONSEQUENCES.tsv').open() as f:
    for r in csv.DictReader(f,delimiter='\t'):counts[r['edition'],r['paragraph']][r['status']+'@'+r['first_failed_position']]+=1
with (A/'CANDIDATE_PREDICTION_TABLE.tsv').open('w') as f:
    w=csv.writer(f,delimiter='\t',lineterminator='\n')
    w.writerow(['edition','paragraph','leaf','eligible','prediction','cases','observed','contradictions','remaining_ambiguity','independent_meaning_confirmation'])
    for ed,p in cap['panels'].items():
        actual={r['paragraph']:r for r in result['panels'][ed]['records']}
        for r in p['candidate_rows']:
            a=actual.get(r['id'])
            w.writerow([ed,r['id'],r['leaf'],r['eligible'],
                'complete23-step root/proof; all n100..9999; global13opcode and10digit code',
                a['tested_cases'] if a else 0,a['status'] if a else 'INELIGIBLE_UNKNOWN',
                json.dumps(dict(counts[ed,r['id']]),sort_keys=True) if a else 'unchanged line eligibility: '+','.join(r['ineligible_lines']),
                '0 exact candidates under this code; other meanings not evaluated' if a else 'transcription/segmentation or one-group-line scope not tested',0])
lines=['# GDT969 — the fixed root-calculation writing model is contradicted','',
       'All three eligible IT2a paragraphs contradict the registered notation. The single',
       'eligible ZL3b paragraph also contradicts it and is the same physical text as one',
       'IT2a case. RF1b supplies no complete boundary-marked paragraph. **No calculation',
       'reading or word was recovered.**','',
       'The contradictions occur at INPUT or HIGH, before later arithmetic or proof',
       'fields can be interpreted. This is an exact failure of the fixed writing',
       'contract, not evidence that the manuscript contains no mathematics.','',
       '## Complete candidate and prediction table','',
       'Each row predicts one full23-step programme for every input100..9999, using',
       'the same injective decimal digits and13global opcode strings. Every feasible',
       'digit width is tested; all four frames have width upper bound1. The complete',
       '9900 source predictions were published before fitting in SOURCE_PROGRAMMES.tsv.','',
       '| Edition | Complete paragraph | Leaf | Cases | Observed first contradictions | Exact candidates |',
       '|---|---|---:|---:|---|---:|']
for ed,p in result['panels'].items():
    for r in p['records']:
        desc='; '.join(f'{n}: {name}' for name,n in sorted(counts[ed,r['paragraph']].items()))
        lines.append(f"| {ed} | {r['paragraph'].replace('|',' / ')} | {r['leaf']} | {r['tested_cases']} | {desc} | {len(r['candidates'])} |")
lines += ['',
    'The all-scope table [CANDIDATE_PREDICTION_TABLE.tsv](artifacts/CANDIDATE_PREDICTION_TABLE.tsv)',
    'also retains all ten ineligible23-group frames. Their exact line-level reasons',
    'are in the independent capacity review: nonliteral groups, indefinite seams,',
    'or a one-group line under the unchanged parent rule. They remain unknown for',
    'this channel. All other lengths and boundary failures remain in the bound',
    'preflight accounting. No favorable substring or individual matching step was',
    'selected. The [full39,600-row certificate](artifacts/CASE_CONSEQUENCES.tsv)',
    'records every input/width result and its first failing position.','',
    '## Why the contradiction is independent of the chosen input','',
    'All inputs contain three or four decimal digits. HIGH must reproduce the',
    'first one or two input digits under the same global digit code. After fixing',
    'width1, the following observed strings make that impossible:','',
    '| Physical text | INPUT / HIGH groups | Required shared leading-code consequence | Observed |',
    '|---|---|---|---|',
    '| f103v | `sal` / `sheal` | At least3 digit characters plus a nonempty INPUT opcode | `sal` has only3 characters |',
    '| f114v, both editions | `pshedy` / `qopcheos` | For3 digits: INPUT leading code = HIGH final code; for4: first2 = final2 | `e` versus `s`; `he` versus `os` |',
    '| f24v | `tochol` / `chor` | The same3/4-digit requirement | `h` versus `r`; `ch` versus `or` |','',
    'Some candidate inputs already fail within INPUT because a repeated decimal',
    'digit would need different written codes. For each f114v/f24v edition case,',
    '4716 inputs fail there and the other5184 fail at HIGH. All9900 f103v inputs',
    'fail the nonempty-prefix length requirement. These are exhaustive necessary',
    'contradictions; no later target step has been claimed as decoded or tested.',
    'The generated source traces themselves satisfy all declared arithmetic.','',
    '## Joint result, ambiguity and independent capacity','',
    'There are zero single-frame candidates, hence no compatible triple to join.',
    'No restart, optimization choice or arbitrary missing-digit completion selects',
    'a preferred answer. Within this exact code model no reading survives. Outside',
    'it, variable numeral notation, other semantic content and other paragraph',
    'organizations remain untested. They are not automatically selected repairs.',
    'The identical f114v spelling in ZL3b and IT2a is not a second independent text.',
    'IT2a had the minimum three-leaf capacity; ZL3b had one leaf and RF1b none.',
    'All are previously exposed. Independent meaning-confirmation capacity is0.',
    'All reserves, f84/f84r and f116v stayed closed. No significance claim is made.',
    'No historical numeral, opcode, source identification or plant name is confirmed.','',
    '## Validation and decision','',
    'Independent source and synthetic checks preceded target execution. The actual',
    'validator reconstructs full target groups/source IDs from the six original',
    'guarded caches and recomputes every finite case independently. See',
    '[VALIDATION.json](artifacts/VALIDATION.json) and',
    '[VALIDATOR_REVIEW.md](src/VALIDATOR_REVIEW.md) for its final receipt and limits.',
    'Synthetic positive cases exercise complete calculations and shared-key joins;',
    'the real manuscript cases exercise only early contradictions. No target timeout.',
    'Source consistency or validator agreement is not semantic confirmation.','',
    'Decision: park the fixed23-group generated result-trace format. Do not change',
    'digit widths, phase counts, skipped steps, boundaries or per-record spellings',
    'to rescue it. A future route needs a separately justified content/writing',
    'hypothesis and different predeclared consequences. GDT902/GDT909 and the earlier',
    'latitude-format stop remain unchanged. No near-complete reading exists that',
    'would justify opening reserved pages.','',
    'Registration750f7d478 was confirmed public at12:08:59UTC on2026-09-15.',
    'The result was recorded at12:09:17UTC; run time0.373s. The original decision',
    'mistakenly estimated its selection minute as11:59; its separately bound timing',
    'correction records the actual decision-then-preflight sequence at11:55:14.',
    'The inclusive preparation/implementation/validation/publication checkpoint',
    'was13:00UTC, with source investigation from11:43UTC. Final publication time',
    'and elapsed work are recorded in the session dossier.']
(E/'REPORT.md').write_text('\n'.join(lines)+'\n')
print('Complete14-row table and report written')
