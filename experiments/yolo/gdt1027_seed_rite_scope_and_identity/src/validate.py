from collections import Counter
from common import *
from independent import compile_reverse,fact_violations,validate_trace,independent_worlds
check_lock();s=source();cfg=spec();lex=s['all_30_new_lexical_entries']
assert sha(E/'src/SOURCE.json')=='1ae949e75da7a31de9ad1782d7abbcebf532d14ac5a49f83e0a7e58ee8548898'
for b in s['source_bindings']:
    assert sha(R/b['path'])==b['sha256']; assert (R/b['path']).stat().st_size==b['bytes']
packet=read(R/s['source_bindings'][2]['path'])
for rd,key in [('ZL3b','complete_raw_record'),('IT2a','IT2a_complete_alternative')]:
    assert [p for p in packet[rd] if p['id']==s['target']['id']]==[s['target'][key]]
selection=[]
for p in packet['ZL3b']:
    c=Counter(w for l in p['lines'] for w in l['words'])
    if p['leaf'] in [83,84] or p['page']=='f116v' or sum(c.values())<30 or len(c)>30:continue
    selection.append(dict(id=p['id'],groups=sum(c.values()),types=len(c),recurrent_types=sum(n>1 for n in c.values()),ineligible=[l['locus'] for l in p['lines'] if not l['anchor_eligible']]))
selection.sort(key=lambda x:(-x['groups'],-x['recurrent_types'],x['id']))
assert len(selection)==69 and selection[:12]==s['selection_and_first_unfinished_attempt']['first_twelve']
ws=independent_worlds();assert ws==read(A/'WORLDS.json');wmap={w['id']:w for w in ws}
assert sum(w['actor']==w['recipient'] for w in ws)==16
with (A/'CASES.tsv').open() as f:rows=list(csv.DictReader(f,delimiter='\t'))
assert len(rows)==15232; observed={c['id']:[] for c in cfg['candidates']}
seen=set();cmap={c['id']:c for c in cfg['candidates']}
for row in rows:
    c=cmap[row['candidate']];n=int(row['seed_case']);w=wmap[row['world']]
    key=(c['id'],n,w['id']);assert key not in seen;seen.add(key)
    violations=fact_violations(c,cfg['seed_cases'][n],w)
    assert int(row['coherent'])==int(not violations)
    assert row['all_violations']==('|'.join(violations) or '[]')
    if violations:
        assert set(row['first_violations'].split('|'))<=set(violations)
        expected=1 if any(x.startswith('QUANTITY') or x=='EMPTY_RAISIN_SET' for x in violations) else 4
        assert int(row['first_failure_step'])==expected and int(row['completed_actions'])==expected-1
    else:assert int(row['first_failure_step'])==0 and int(row['completed_actions'])==5
    observed[c['id']].append(row)
for c in cfg['candidates']:
    assert compile_reverse(s['target']['complete_raw_record']['lines'],lex,c)=='COMPLETE'
    assert compile_reverse(s['target']['IT2a_complete_alternative']['lines'],lex,c)=='UNBOUND_FORMS'
    assert len(observed[c['id']])==1904
with (A/'PREDICTIONS.tsv').open() as f:pred=list(csv.DictReader(f,delimiter='\t'))
for p in pred:
    rs=observed[p['candidate']]
    assert sum(int(r['coherent']) for r in rs)==int(p['predicted_coherent'])
    assert sum(int(r['coherent']) for r in rs if wmap[r['world']]['actor']==wmap[r['world']]['recipient'])==int(p['predicted_self_coherent'])
traces=read(A/'TRACES.json');assert len(traces)==60
for t in traces:
    mode=t['case'] if t['case'] in cfg['countercases'] else 'NONE'
    validate_trace(cmap[t['candidate']],t['counts'],t['world'],t['output'],mode)
    assert t['output']['coherent']==(t['case'] not in cfg['countercases'])
with (A/'ALL_POSITIONS.tsv').open() as f:positions=list(csv.DictReader(f,delimiter='\t'))
assert [x['word'] for x in positions]==[w for l in s['target']['complete_raw_record']['lines'] for w in l['words']]
assert [int(x['position']) for x in positions]==list(range(1,38))
graphs=read(A/'GRAPHS.json')
for g in graphs:
    assert g['consumed']==37
    assert [r['position'] for r in g['seed_references']]==[5,13,23]
    assert [r['position'] for r in g['actor_references']]==[9,18,35]
    assert [a['op'] for a in g['actions']]==['TAKE','EXTRACT','PLACE','BIND','CLAIM']
assert sum(int(r['coherent']) for r in rows)==660
out=dict(status='PASS',utc=now(),scope='same-author independent implementation, not independent meanings',complete_case_rows=15232,complete_trace_replays=60,source_hashes=6,selection_candidates=69,whole_positions=37,independent_meaning_capacity=0,confirmed_words=0)
write(A/'VALIDATION.json',out);print(json.dumps(out))
