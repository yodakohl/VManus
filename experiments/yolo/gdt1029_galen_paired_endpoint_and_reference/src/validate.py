from collections import Counter
from fractions import Fraction
from common import *
from independent import compile_reverse,prediction,validate_graph,validate_output
check_lock();s=source();cfg=spec();lex=lexicon(s);old=parent_source()
assert sha(E/'src/SOURCE.json')=='f433f72f5e45f2f428d4e62d836cf937201c195f9b30d1628c4f40e32303d907'
for b in s['scope_receipts']:assert sha(R/b['path'])==b['sha256'] and (R/b['path']).stat().st_size==b['bytes']
packet=read(R/s['selection_receipt']['packet_path']);oldtypes={e['form'] for e in old['lexicon']};tiers={'lkar':[],'kedy':[]}
for p in packet['ZL3b']:
    if p['leaf'] in [84,107] or p['page']=='f116v':continue
    cc=Counter(w for l in p['lines'] for w in l['words']);n=sum(cc.values());known=set(cc)&oldtypes;fresh=set(cc)-oldtypes
    if not (45<=n<=90 and len(known)>=8 and len(fresh)<=50):continue
    row=dict(id=p['id'],groups=n,types=len(cc),old_positions=sum(cc[w] for w in known),old_types=len(known),new_types=len(fresh),uncertain_lines=[l['locus'] for l in p['lines'] if not l['anchor_eligible']])
    for k in tiers:
        if k in cc:tiers[k].append(row)
for rs in tiers.values():rs.sort(key=lambda x:(-Fraction(x['old_positions'],x['groups']),-Fraction(x['old_types'],x['types']),x['id']))
assert tiers==s['selection_receipt']['census'] and [len(tiers[k]) for k in ['lkar','kedy']]==[5,4]
for r in s['first_three_records']:
    assert [p for p in packet['ZL3b'] if p['id']==r['whole_record']['id']]==[r['whole_record']]
    for rd,rr in r['alternatives'].items():assert [p for p in packet[rd] if p['id']==r['whole_record']['id']]==rr
lines=old['target_choice']['whole_record']['lines'];nl=s['first_three_records'][0]['whole_record']['lines']
assert compile_reverse(lines,nl,lex,s)=='COMPLETE_POSITION_GRAPH'
assert compile_reverse(old['target_choice']['alternative_reader_records']['IT2a']['lines'],nl,lex,s)=='UNBOUND_FORMS'
assert compile_reverse(lines,s['first_three_records'][0]['alternatives']['IT2a'][0]['lines'],lex,s)=='UNBOUND_FORMS'
obs=read_table(A/'CASES.tsv');pred=read_table(A/'PREDICTIONS.tsv');assert obs==pred and len(obs)==87
cmap={c['id']:c for c in cfg['candidates']};fmap={f['name']:f for f in cases()};graphs={g['candidate']['id']:g for g in read(A/'GRAPHS.json')};outs=read(A/'OUTPUTS.json')
assert len(graphs)==9 and len(outs)==87;seen=set()
for g in graphs.values():validate_graph(g,s)
for out in outs:
    key=out['candidate'],out['case'];assert key not in seen;seen.add(key)
    validate_output(graphs[out['candidate']],fmap.get(out['case']),out['output'])
for c in cfg['candidates']:
    rs=[r for r in obs if r['candidate']==c['id']]
    expected=cfg['case_names'] if c['kind']=='SEMANTIC' else ['STATIC_WHOLE_GRAPH']
    assert [r['case'] for r in rs]==expected
    for r in rs:assert r=={k:str(v) for k,v in prediction(c,r['case']).items()}
parent_rows=read_table(A/'PARENT_REPLAY.tsv');assert parent_rows==read_table(P/'artifacts/CASES.tsv')==read_table(P/'artifacts/PREDICTIONS.tsv')
assert len(parent_rows)==228 and read(A/'PARENT_REPLAY.json')['generalized_no_original_capability_instantiations']==204
positions=read_table(A/'ALL_POSITIONS.tsv');assert len(positions)==95 and [int(r['position']) for r in positions]==list(range(1,96))
assert [r['word'] for r in positions]==[w for l in lines+nl for w in l['words']]
assert sum(r['value_status']=='BROADENED_QOKY' for r in positions)==2
assert len(set(r['word'] for r in positions))==67
rr=read(A/'RESULT.json');assert rr['facts_compatible']==sum(r['status']=='COMPATIBLE_WITH_HYPOTHETICAL_FACTS' for r in obs)
for c in rr['candidates']:
    rs=[r for r in obs if r['candidate']==c['candidate']]
    assert c['checked_rows']==len(rs) and c['facts_compatible']==sum(r['status']=='COMPATIBLE_WITH_HYPOTHETICAL_FACTS' for r in rs)
    assert c['norm_conformant']==sum(r['norm_conformant']=='1' for r in rs)
eq=read(A/'EQUIVALENCE.json');assert len(eq['old_physical_trace_projection'])==1 and len(eq['old_physical_trace_projection'][0])==6
out=dict(status='PASS',utc=now(),implementation_independence='separate same-author declarative/tag/trace validator, not independent semantic evidence',new_complete_rows=87,parent_rows_reproduced=228,parent_artifacts_unchanged=True,whole_positions=95,literal_parent_entries=35,one_broadening='qoky',independent_meaning_capacity=0,confirmed_words=0)
write(A/'VALIDATION.json',out);print(json.dumps(out))
