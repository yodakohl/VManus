import json,hashlib
from pathlib import Path
E=Path(__file__).resolve().parents[1]
spec=json.loads((E/'src/SPEC.json').read_text());obs=json.loads((E/'artifacts/OBSERVATIONS.json').read_text());sources=json.loads((E/'artifacts/SOURCES.json').read_text())
assert sorted(obs)==sorted(spec['pages'])==sorted(x['page'] for x in sources['images'])
summary={}
for p,rows in obs.items():
    assert [r['line'] for r in rows]==list(range(1,len(rows)+1))
    assert all(a['y']<b['y'] for a,b in zip(rows,rows[1:]))
    i=spec['targets'][p]-1; a,b,c=rows[i-1:i+2]
    summary[p]={'target':i+1,'x_delta_from_neighbour_mean':b['x']-(a['x']+c['x'])/2,'gap_above':b['y']-a['y'],'gap_below':c['y']-b['y']}
for s in sources['images']:
    p=E/'runtime'/f"{s['page']}.jpg"
    if p.exists(): assert hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256']
(E/'artifacts/VALIDATION.json').write_text(json.dumps({'status':'PASS_INVENTORY_AND_ARITHMETIC_ONLY','geometry':summary},indent=2)+'\n')
print(json.dumps(summary))
