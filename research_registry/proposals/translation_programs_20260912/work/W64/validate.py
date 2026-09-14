from pathlib import Path
import json,csv,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
ps=json.loads((D.parent/'W63/PARAGRAPHS.json').read_text());lex={r['form']:r for r in csv.DictReader((D.parent/'W02/LEXICON.tsv').open(),delimiter='\t')}
mat={w for w,r in lex.items() if r['role'] in ('MATERIAL','MATERIAL_DOSE')}|{'sheedy','shey','sheckhy'};act={w for w,r in lex.items() if r['role'] in ('ACTION','ACTION_TYPED','REPEAT_ACTION','REPEAT_COOL','MIX')}
occ=list(csv.DictReader((D/'ALL_QOKAIN.tsv').open(),delimiter='\t'));cs=list(csv.DictReader((D/'FOLLOWUPS.tsv').open(),delimiter='\t'));assert len(occ)==33 and len(cs)==6
for p in ps:
 flat=[(sid,w) for l in p['lines'] for sid,w in zip(l['source_ids'],l['words'])]
 assert [r['at'] for r in occ if r['edition']==p['edition'] and r['paragraph']==p['id']]==[sid for sid,w in flat if w=='qokain']
 for i,(sid,w) in enumerate(flat):
  if w!='qokain' or not i or flat[i-1][1]!='sheckhy':continue
  r=next(r for r in cs if r['at']==sid);j=next((j for j in range(i+1,len(flat)) if flat[j][1] in act),len(flat));mm=[(a,w) for a,w in flat[i+1:j] if w in mat]
  assert r['first_later_action']==(flat[j][0] if j<len(flat) else 'NONE')
  assert r['intervening_materials']==';'.join(a+':'+w for a,w in mm)
  assert r['full_future']==' '.join(w for _,w in flat[i+1:])
  assert r['capacity']==('NO_ACTION' if j==len(flat) else 'MATERIAL_REPLACED' if mm else 'POSSIBLE_UNDER_LEFT_RULE')
v=dict(status='PASS',scope='all33qokain and six first-known-action audits with full futures',meaning_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
