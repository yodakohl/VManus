from pathlib import Path
import csv,json,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
s=json.loads(Path('experiments/yolo/gdt929_fixed_four_form_context_square/src/SPEC.json').read_text());expected=[]
allow=set(json.loads(Path(s['allow_source']).read_text())['allowed_selectors'])
for p in s['sources']:
 assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==s['hashes'][p]
 d=json.loads(Path(p).read_text())
 for l in d['lines']:
  assert l['metadata']['page'] in allow and not l['metadata']['page'].startswith('f84')
  g=[dict(zip(d['group_columns'],x)) for x in l['groups']]
  for i,x in enumerate(g):
   if x['ivtff_group_raw']!='sheckhy':continue
   n=g[i+1] if i+1<len(g) else None
   expected.append((x['source_group_id'],n['ivtff_group_raw'] if n else None,bool(n and x['right_separator']==n['left_separator']=='DEFINITE_SPACE' and int(n['source_group_index'])==int(x['source_group_index'])+1)))
o=json.loads((D/'OCCURRENCES.json').read_text());assert expected==[(r['id'],r['right'],r['right_definite']) for r in o]
base=[r for r in csv.DictReader((D.parent/'W61/ALIGNMENT.tsv').open(),delimiter='\t') if r['model']=='R'];rs=list(csv.DictReader((D/'ALIGNMENT.tsv').open(),delimiter='\t'));assert len(rs)==496
for m,v in [('N','Mischung'),('A','vermische')]:
 rows=[r for r in rs if r['model']==m];assert [(r['at'],r['word']) for r in rows]==[(r['at'],r['word']) for r in base]
 for r,b in zip(rows,base):assert r['hypothesis']==(v if b['word']=='sheckhy' else b['hypothesis'])
v=dict(status='PASS',scope='all92occurrences and all496declared full-reading positions',meaning_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
