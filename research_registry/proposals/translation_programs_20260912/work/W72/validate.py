from pathlib import Path
import csv,json,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
src=list(csv.DictReader((D.parent/'W69/EVENTS.tsv').open(),delimiter='\t'));rr=list(csv.DictReader((D/'QUALITIES.tsv').open(),delimiter='\t'));ps=json.loads((D.parent/'W63/PARAGRAPHS.json').read_text());fx=json.loads((D.parent/'W09/SPEC.json').read_text())['effects'];ff={f['form']:f for f in json.loads((D.parent/'W03/SPEC.json').read_text())['features'] if f['kind']=='STANDALONE'}
key=lambda r:(r['model'],r['edition'],r['paragraph'],r['at'])
assert {key(r) for r in rr}=={key(r) for r in src if r['kind']=='QUALITY'} and len(rr)==18
for r in rr:
 p=next(p for p in ps if p['edition']==r['edition'] and p['id']==r['paragraph']);assert not p['page'].startswith('f84')
 flat=[(sid,w) for l in p['lines'] for sid,w in zip(l['source_ids'],l['words'])];pos={a:i for i,(a,w) in enumerate(flat)}
 e=next(e for e in src if key(e)==key(r));assert r['patient']==e['patient'] and r['polarity']==e['polarity']
 aa=[a for a in src if a['model']==r['model'] and a['edition']==r['edition'] and a['paragraph']==r['paragraph'] and a['kind']=='ACTION' and a['polarity']=='POSITIVE' and a['patient'] and a['patient']==r['patient'] and fx.get(a['word'],{}).get('axis')=='thermal']
 pre=sorted([a for a in aa if pos[a['at']]<pos[r['at']]],key=lambda a:pos[a['at']]);post=sorted([a for a in aa if pos[a['at']]>pos[r['at']]],key=lambda a:pos[a['at']])
 assert r['prior_action']==(pre[-1]['at'] if pre else '') and r['next_action']==(post[0]['at'] if post else '')
 f=ff.get(r['word']);status='NO_STANDALONE_FEATURE' if not f else 'NONTHERMAL_FEATURE' if f['axis']!='thermal' else 'MISSING_PATIENT' if not r['patient'] else 'NO_PRIOR_THERMAL_ACTION' if not pre else 'WRITTEN_ENDPOINT_CANDIDATE';assert r['status']==status
assert not any(r['status']=='WRITTEN_ENDPOINT_CANDIDATE' for r in rr)
v=dict(status='PASS',all_quality_rows=18,endpoint_candidates=0,meaning_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
