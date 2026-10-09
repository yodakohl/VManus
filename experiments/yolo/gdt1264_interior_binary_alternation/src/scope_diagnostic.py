"""Post-result scope illustration; no new score, gate or fitted parameter."""
import collections,gzip,json,re
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
s=json.loads((B/'src/SPEC.json').read_text());data=json.loads(gzip.decompress((R/s['source']).read_bytes()));events=json.loads(gzip.decompress((B/'artifacts/EVENTS.json.gz').read_bytes()));detail={'status':'POSTRESULT_SCOPE_DIAGNOSTIC_NO_NEW_GATE','body_novelty':[],'examples':[],'unsupported':[]}
for reader in s['readers']:
 known={tuple(r['units'][1:-1]) for r in data[reader] if int(re.match(r'f(\d+)',r['page'])[1])%2 and len(r['units'])-2>=s['minimum_interior_units']}
 es=[e for e in events if e['reader']==reader and e['cohort']=='UNSEEN_WHOLE' and e['status']=='SCORED'];counts=collections.Counter('seen_interior' if tuple(e['units']) in known else 'unseen_interior' for e in es);detail['body_novelty'].append({'reader':reader,'unseen_whole_scorable_tokens':len(es),**dict(counts)})
for word in ['qokeedy','daldy','daiin']:
 matches=[e for e in events if e['reader']=='ZL3b' and e['cohort']=='ALL' and e['status']=='SCORED' and ''.join(e['whole_units'])==word]
 if matches:detail['examples'].append({'whole_form':word,'illustrative_case':min(matches,key=lambda e:e['id']),'selection':'Post-result named familiar form, no new test or meaning; full cohort remains.'})
for e in events:
 if e['status']=='UNSEEN_TRAIN_UNIT' and e['cohort']=='ALL':detail['unsupported'].append(next(r for r in data[e['reader']] if r['id']==e['id']))
(B/'artifacts/POSTRESULT_SCOPE_DIAGNOSTIC.json').write_text(json.dumps(detail,indent=2)+'\n')
