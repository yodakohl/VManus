import json
from pathlib import Path
E=Path(__file__).resolve().parents[1];A=E/'artifacts'
dom=json.loads((A/'WORD_DOMAINS.json').read_text());candidates=json.loads((A/'CANDIDATES.json').read_text());packet=json.loads((A/'SOURCE_PACKET.json').read_text())
names={0:'A→A;B→A',1:'A→A;B→B',2:'A→A;B→undef',3:'A→B;B→A',4:'A→B;B→B',5:'A→B;B→undef',6:'A→undef;B→A',7:'A→undef;B→B',8:'A→undef;B→undef'}
lines=['# Complete raw context and conditional effect obligations','', 'No function table is a translated word. All raw groups retained; separators/flags and source IDs remain in SOURCE_PACKET.json. A/B are hypothetical locations of the same hypothetical portion.','']
for ed,rows in packet['raw'].items():
 lines += [f'## {ed}','']
 for r in rows:lines += [r['metadata']['locus']+': `'+ ' | '.join(g['ivtff_group_raw'] for g in r['groups'])+'`','']
lines += ['## Every unknown whole and both entry states','','Codes are defined below. Domains are marginals: arbitrary choices from different rows need not form one joint solution. Complete joint witnesses are in QUERIES.json.','','| Whole | Enter from A | Enter from B |','|---|---|---|']
for w in sorted({d['word'] for d in dom}):
 ds=[next(d for d in dom if d['word']==w and d['start']==s) for s in [0,1]]
 lines.append('| '+w+' | '+' | '.join(', '.join(map(str,d['possible_codes'])) for d in ds)+' |')
lines += ['','## Exact code definitions','']
lines += [f'- {n}: {label}' for n,label in names.items()]
lines += ['','## All inherited candidates','', '| Reading | Candidate | New status | sheolo tables | Final places |', '|---|---|---|---|---|']
for r in candidates:lines.append('| '+' | '.join([r['edition'],r['candidate'],r['status'],str(r.get('sheolo_codes','—')),str(r.get('final_states','—'))])+' |')
(A/'READING_OBLIGATIONS.md').write_text('\n'.join(lines)+'\n')
with (A/'CANDIDATE_TABLE.tsv').open('w') as f:
 f.write('edition\tcandidate\tstatus\tinherited_status\tinitial\tfinal_states\tsheolo_codes\tindependent_confirmation\n')
 for r in candidates:f.write('\t'.join(str(r.get(k,'')) for k in ['edition','candidate','status','inherited_status','initial','final_states','sheolo_codes','independent_confirmation'])+'\n')
# Algebraic obligations that can be read directly without either solver.
proof={'bridge':{'source_locus':'f75v.41','source_position_one_based':14,'source_word':'or','intervening_word':'sheolo','destination_locus':'f75v.42','destination_position_one_based':1,'destination_word':'ol'},'necessary_table_component':'F_sheolo(B)=A','remaining_codes':{str(n):names[n] for n in [0,3,6]},'other_forced_component':'F_shey(A)=A from ol shey ol at f75v41.6-8','global_whole_reading_identified':False,'semantic_binding_independent':False}
# Check raw IT positions, not merely the registered claim.
it={r['metadata']['locus']:[g['ivtff_group_raw'] for g in r['groups']] for r in packet['raw']['IT2a']}
assert it['f75v.41'][13:]==['or','sheolo'] and it['f75v.42'][0]=='ol'
assert it['f75v.41'][5:8]==['ol','shey','ol']
assert all(d['possible_codes']==[0,3,6] for d in dom if d['word']=='sheolo')
assert all(d['possible_codes']==[0,1,2] for d in dom if d['word']=='shey')
(A/'DIRECT_OBLIGATIONS.json').write_text(json.dumps(proof,indent=2,ensure_ascii=False)+'\n')
print('COMPLETE_TABLES_AND_DIRECT_OBLIGATIONS_CHECKED')
