import collections, hashlib, json
from pathlib import Path
BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]

def summarize(events, fields):
    buckets = collections.defaultdict(list)
    for e in events:
        key = tuple(e['cell_key']) + tuple(e[f] for f in fields)
        buckets[key].append(e)
    conflicts = []
    for key, rows in sorted(buckets.items()):
        if len({e['label'] for e in rows}) > 1:
            conflicts.append({'key': list(key), 'events': rows})
    return {'keys': len(buckets), 'repeated_keys': sum(len(v)>1 for v in buckets.values()),
            'events_in_repeated_keys': sum(len(v) for v in buckets.values() if len(v)>1),
            'conflict_keys': len(conflicts), 'conflicts': conflicts}

def main():
    lock = json.loads((BASE/'src/REGISTRATION_LOCK.json').read_text())
    for p,h in lock['hashes'].items():
        assert hashlib.sha256((BASE/p).read_bytes()).hexdigest()==h
    spec = json.loads((BASE/'src/SPEC.json').read_text())
    raw = (ROOT/spec['source']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==spec['sha256']
    events=json.loads(raw)
    assert len(events)==spec['expected_events'] and len({e['id'] for e in events})==len(events)
    assert all(e['cell_key'][1] not in ('f84','f84r') and e['id'].startswith('ZL3b|') for e in events)
    f=[{'cell_key':[1],'left':'a','right':'b','label':'OUTER'},
       {'cell_key':[1],'left':'c','right':'b','label':'INNER'}]
    assert summarize(f,['right'])['conflict_keys']==1
    assert summarize(f,['left','right'])['conflict_keys']==0
    result={'source_sha256':spec['sha256'],'events':len(events),
            'models':{name:summarize(events,fields) for name,fields in spec['models'].items()},
            'scope':'Exposed ZL3b deterministic logical contradictions only; no predictive score or native meaning.'}
    (BASE/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:{a:b for a,b in v.items() if a!='conflicts'} for k,v in result['models'].items()},indent=2))
if __name__=='__main__':main()
