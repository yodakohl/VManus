import hashlib,itertools,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[2]
spec=json.loads((BASE/'src/SPEC.json').read_text());raw=(ROOT/spec['source']).read_bytes()
assert hashlib.sha256(raw).hexdigest()==spec['sha256']
events=json.loads(raw);result=json.loads((BASE/'artifacts/RESULT.json').read_text())
assert result['events']==len(events)==146
for name,fields in spec['models'].items():
    def key(e):return json.dumps(e['cell_key']+[e[f] for f in fields])
    keys={key(e) for e in events}
    repeated={key(a) for a,b in itertools.combinations(events,2) if key(a)==key(b)}
    conflict={key(a) for a,b in itertools.combinations(events,2) if key(a)==key(b) and a['label']!=b['label']}
    r=result['models'][name]
    assert r['keys']==len(keys) and r['repeated_keys']==len(repeated)
    assert r['events_in_repeated_keys']==sum(key(e) in repeated for e in events)
    assert r['conflict_keys']==len(conflict)
    assert {json.dumps(c['key']) for c in r['conflicts']}==conflict
    for c in r['conflicts']:
        assert c['events']==[e for e in events if key(e)==json.dumps(c['key'])]
lock=json.loads((BASE/'src/REGISTRATION_LOCK.json').read_text())
for p,h in lock['hashes'].items():assert hashlib.sha256((BASE/p).read_bytes()).hexdigest()==h
out={'status':'PASS','independent_method':'all event pairs, separate key reconstruction; runner not imported',
     'checks':['source hash','registered text/spec hashes','event count','key counts','repeat support','all conflict membership'],
     'ceiling':'Software and literal event comparison, not paleography or semantics.'}
(BASE/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
