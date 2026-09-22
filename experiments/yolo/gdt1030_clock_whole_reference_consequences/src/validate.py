from collections import Counter
from common import *
from independent import compile_reverse,prediction,validate_graph,validate_output
check_lock();s=source();cfg=spec()
assert sha(E/'src/SOURCE.json')=='70fec54332ab45655b4c7a134895d9c79349b8a217cfd9a7cca7b5f6caea4ddd'
for b in s['scope_receipts']:assert sha(R/b['path'])==b['sha256'],b['path']
parent=read(R/s['parent_binding']['path']);packet=read(R/parent['selection_receipt']['packet_path']);rank=[]
for p in packet['ZL3b']:
 if p['leaf'] in [84,107] or p['page']=='f116v':continue
 cc=Counter(w for l in p['lines'] for w in l['words']);n=sum(cc.values())
 if 40<=n<=80 and len(cc)<=45:rank.append(dict(id=p['id'],groups=n,types=len(cc),repeat_positions=n-len(cc),recurrent_types=sum(v>1 for v in cc.values())))
rank.sort(key=lambda x:(x['types'],-x['repeat_positions'],x['id']))
assert len(rank)==128 and rank==parent['selection_receipt']['ranking']
assert s['original_three_attempts']==parent['inspected_attempts']
rec=s['selected_target']['full_record'];assert [p for p in packet['ZL3b'] if p['id']==rec['id']]==[rec]
assert rec==parent['inspected_attempts'][2]['record']
assert s['selected_target']['alternatives']==parent['inspected_attempts'][2]['alternatives']
lex={e['form']:e for e in s['lexicon']};lines=rec['lines'];assert len(lex)==33
assert compile_reverse(lines,lex)=='COMPLETE_GRAPH'
assert compile_reverse(s['selected_target']['alternatives']['IT2a'][0]['lines'],lex)=='UNBOUND_FORMS'
positions=read_table(A/'ALL_POSITIONS.tsv');words=[w for l in lines for w in l['words']]
assert len(positions)==40 and [r['form'] for r in positions]==words
for e in s['lexicon']:assert e['positions']==[i+1 for i,w in enumerate(words) if w==e['form']]
assert sorted(p for c in s['whole_paragraph_productions'] for p in c['positions'])==list(range(1,41))
for c in s['whole_paragraph_productions']:assert c['value_sequence']==[lex[words[i-1]]['value'] for i in c['positions']]
assert len(s['binding_assumptions'])==20
assert s['complete_source']==parent['complete_selected_source']
assert sha(R/parent['parent_binding']['path'])==parent['parent_binding']['sha256']
rows=read_table(A/'CASES.tsv');assert rows==read_table(A/'PREDICTIONS.tsv') and len(rows)==216
cc={c['id']:c for c in cfg['candidates']};ff={f['name']:f for f in cases()};gg={g['candidate']['id']:g for g in read(A/'GRAPHS.json')};oo=read(A/'OUTPUTS.json')
assert len(gg)==9 and len(oo)==216 and len(ff)==24
for g in gg.values():validate_graph(g,s)
seen=set()
for o in oo:
 key=o['candidate'],o['case'];assert key not in seen;seen.add(key);validate_output(gg[o['candidate']],ff[o['case']],o['output'])
for r in rows:assert r=={k:str(v) for k,v in prediction(cc[r['candidate']],r['case']).items()}
for c in cc:assert {r['case'] for r in rows if r['candidate']==c}==set(ff)
for r in read(A/'RESULT.json')['candidates']:
 cr=[a for a in rows if a['candidate']==r['candidate']]
 assert r['unit_compatible']==sum(a['status']=='COMPATIBLE_IN_HYPOTHETICAL_WORLD' for a in cr)
 assert r['full_parent_compatible']==sum(a['full_parent_compatible']=='1' for a in cr)
assert not any(r['full_parent_compatible']=='1' for r in rows if r['candidate']=='EQUAL_DURATION')
write(A/'VALIDATION.json',dict(status='PASS',utc=now(),world_rows=216,whole_positions=40,selection_reconstructed=128,confirmed_words=0,independent_meaning_capacity=0,scope='separate same-author whole-tag, fixture, graph, proof and source validator; not external semantic confirmation'))
print('PASS all216 rows and128-candidate selection')
