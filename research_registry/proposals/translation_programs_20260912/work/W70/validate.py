from pathlib import Path
import csv,json,hashlib,collections,itertools
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
src=list(csv.DictReader((D.parent/'W69/EVENTS.tsv').open(),delimiter='\t'));out=list(csv.DictReader((D/'COMPARISON.tsv').open(),delimiter='\t'));ps=json.loads((D.parent/'W63/PARAGRAPHS.json').read_text())
idx=collections.defaultdict(dict)
for r in src:idx[(r['edition'],r['paragraph'],r['at'])][r['model']]=r
assert len(idx)==len(out)==78
fields=['word','hypothesis','kind','polarity','patient','patient_hypothesis']
expected_order=[]
for p in ps:
 assert not p['page'].startswith('f84')
 for l in p['lines']:
  assert l['locus']+' `'+ ' '.join(l['words'])+'`' in (D/'READING.md').read_text()
  expected_order.extend((p['edition'],p['id'],sid) for sid in l['source_ids'] if (p['edition'],p['id'],sid) in idx)
assert expected_order==[(r['edition'],r['paragraph'],r['at']) for r in out]
for r in out:
 pair=idx[(r['edition'],r['paragraph'],r['at'])];a=pair.get('NRC');b=pair.get('AMV');diff=[k for k in fields if a and b and a[k]!=b[k]]
 status='NRC_ONLY' if b is None else 'AMV_ONLY' if a is None else 'DIFFERENT' if diff else 'SHARED_BOUND' if a['patient'] else 'SHARED_UNBOUND'
 assert r['status']==status and r['differences']==';'.join(diff)
 assert r['shared_patient']==(a['patient'] if status=='SHARED_BOUND' else '')
chains=[]
for p in ps:
 rr=[r for r in out if r['edition']==p['edition'] and r['paragraph']==p['id']]
 for key,gg in itertools.groupby(rr,key=lambda r:r['shared_patient'] if r['status']=='SHARED_BOUND' else None):
  g=list(gg)
  if key and len(g)>=2:chains.append((p['edition'],p['id'],key,[r['at'] for r in g]))
actual=json.loads((D/'CHAINS.json').read_text());assert chains==[(c['edition'],c['paragraph'],c['patient'],c['events']) for c in actual] and len(chains)==5
v=dict(status='PASS',source_events=135,union_positions=78,chains=5,meaning_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
