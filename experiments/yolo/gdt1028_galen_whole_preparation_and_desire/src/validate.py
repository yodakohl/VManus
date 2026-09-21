from collections import Counter
from common import *
from independent import compile_reverse,validate_output,observe

check_lock();s=source();cfg=spec();fs=cases();lex={x['form']:x for x in s['lexicon']}
assert sha(E/'src/SOURCE.json')=='de31c91a90662287c011ee1356e02ce08ba0a617edd197c7be2b920183fb8f39'
for b in s['scope_receipts']:
    assert sha(R/b['path'])==b['sha256'] and (R/b['path']).stat().st_size==b['bytes'],b['path']
packet=read(R/s['candidate_coverage']['packet'])
target=s['target_choice']['whole_record'];alternatives=s['target_choice']['alternative_reader_records']
assert [p for p in packet['ZL3b'] if p['id']==target['id']]==[target]
assert [p for p in packet['IT2a'] if p['id']==target['id']]==[alternatives['IT2a']]
assert [p for p in packet['RF1b'] if p['id']==target['id']]==alternatives['RF1b']==[]
rankings={k:[] for k in ['preferred','fallback']}
for p in packet['ZL3b']:
    if p['leaf']==84 or p['page']=='f116v':continue
    ct=Counter(w for l in p['lines'] for w in l['words']);n=sum(ct.values());t=len(ct)
    row=dict(id=p['id'],groups=n,types=t,repeat_positions=n-t,recurrent_forms=sum(v>1 for v in ct.values()),uncertain_lines=[l['locus'] for l in p['lines'] if not l['anchor_eligible']])
    if n>=30 and t<=30:rankings['preferred'].append(row)
    if n>=40 and 31<=t<=36:rankings['fallback'].append(row)
for k,rr in rankings.items():
    rr.sort(key=lambda x:(-x['repeat_positions'],-x['recurrent_forms'],x['id']))
    assert rr==s['candidate_coverage']['ranking_arithmetic_only'][k]
assert [len(rankings[k]) for k in ['preferred','fallback']]==[70,25]
assert compile_reverse(target['lines'],lex,s['whole_paragraph_productions'])=='COMPLETE_GRAPH'
assert compile_reverse(alternatives['IT2a']['lines'],lex,s['whole_paragraph_productions'])=='UNBOUND_FORMS'
def rows(path):
    with path.open() as f:return list(csv.DictReader(f,delimiter='\t'))
pred=rows(A/'PREDICTIONS.tsv');obs=rows(A/'CASES.tsv')
assert len(pred)==len(obs)==228 and obs==pred
graphs={g['candidate']['id']:g for g in read(A/'GRAPHS.json')};outs=read(A/'OUTPUTS.json')
cmap={c['id']:c for c in cfg['candidates']};fmap={f['name']:f for f in fs}
assert len(graphs)==len(cmap)==36
seen=set();byid={c['id']:[] for c in cfg['candidates']}
for o in outs:
    key=o['candidate'],o['case'];assert key not in seen;seen.add(key)
    c=cmap[o['candidate']];f=fmap.get(o['case'],dict(name='STATIC_WHOLE_GRAPH'))
    validate_output(c,f,graphs[c['id']],o['output']);byid[c['id']].append(observe(c,o['case'],o['output']))
assert len(outs)==228
for c in cfg['candidates']:
    expected=cfg['case_names'] if c['syntax']=='QUOTED_FOOD_TRANSFER' else ['STATIC_WHOLE_GRAPH']
    assert [r['case'] for r in byid[c['id']]]==expected
positions=rows(A/'ALL_POSITIONS.tsv')
assert len(positions)==49 and [p['word'] for p in positions]==[w for l in target['lines'] for w in l['words']]
assert [int(p['position']) for p in positions]==list(range(1,50))
assert [p['value'] for p in positions]==[r['value'] for r in s['token_receipt']]
result=read(A/'RESULT.json')
assert result['case_rows']==228 and result['confirmed_words']==result['independent_meaning_capacity']==0
for r in result['candidates']:
    rr=byid[r['candidate']]
    assert r['coherent']==sum(x['status']=='COHERENT_CONDITIONAL_CONTENT' for x in rr)
    assert r['source_complete_and_coherent']==sum(x['source_complete'] and x['status']=='COHERENT_CONDITIONAL_CONTENT' for x in rr)
eq=read(A/'EQUIVALENCE.json')
assert len(eq['dry_physical_trace_only'])==1 and len(eq['dry_physical_trace_only'][0])==12
assert sorted(x for g in eq['whole_declared_fixture_projection'] for x in g)==sorted(cmap)
out=dict(status='PASS',utc=now(),implementation_independence='same-author separate declarative validator, no model import',complete_rows=228,whole_graphs=36,source_receipts=11,selector_candidates=[70,25],exact_target_positions=49,independent_meaning_capacity=0,confirmed_words=0)
write(A/'VALIDATION.json',out);print(json.dumps(out))
