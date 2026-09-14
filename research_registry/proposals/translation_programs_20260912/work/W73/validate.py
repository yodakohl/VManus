from pathlib import Path
import json,csv,hashlib,itertools
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
ps=json.loads((D.parent/'W63/PARAGRAPHS.json').read_text());es=list(csv.DictReader((D.parent/'W69/EVENTS.tsv').open(),delimiter='\t'));base={r['form']:r['role'] for r in csv.DictReader((D.parent/'W02/LEXICON.tsv').open(),delimiter='\t')};mod=set(json.loads((D.parent/'W05/SPEC.json').read_text())['transparent_roles']);rr=list(csv.DictReader((D/'RUNS.tsv').open(),delimiter='\t'));expected=[]
for p in ps:
 assert not p['page'].startswith('f84')
 for m in ['NRC','AMV']:
  roles=dict(base,sheedy='MATERIAL',shey='MATERIAL',sheckhy='MATERIAL' if m=='NRC' else 'ACTION')
  if m=='AMV':roles.update(ol='MATERIAL',chey='NEGATION')
  acts={e['at'] for e in es if e['model']==m and e['edition']==p['edition'] and e['paragraph']==p['id'] and e['kind']=='ACTION'}
  for l in p['lines']:
   zipped=list(zip(l['source_ids'],l['words']));pos={a:i for i,(a,w) in enumerate(zipped)}
   for isact,g in itertools.groupby(zipped,key=lambda x:x[0] in acts):
    run=list(g)
    if not isact or len(run)<2:continue
    for v in ['J','M']:
     k=pos[run[-1][0]]+1
     if v=='M':
      while k<len(zipped) and roles.get(zipped[k][1],'OPEN') in mod:k+=1
     target=zipped[k][0] if k<len(zipped) and roles.get(zipped[k][1],'OPEN') in {'MATERIAL','MATERIAL_DOSE'} else ''
     status='SHARED_EXPLICIT_RIGHT' if target else 'LINE_END' if k==len(zipped) else 'BLOCKED_'+roles.get(zipped[k][1],'OPEN')
     expected.append((p['edition'],m,p['id'],v,';'.join(a for a,w in run),target,status))
assert expected==[(r['edition'],r['model'],r['paragraph'],r['variant'],r['operations'],r['target'],r['status']) for r in rr] and len(rr)==16
v=dict(status='PASS',all_run_variant_rows=16,explicit_shared_tails=0,meaning_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
