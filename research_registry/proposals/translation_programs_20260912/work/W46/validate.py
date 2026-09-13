import csv,json,hashlib
from pathlib import Path
D=Path(__file__).parent;s=json.loads((D/'SPEC.json').read_text())
for p,h in s['hashes'].items(): assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
ctx=json.loads(Path(s['context']).read_text());ef=json.loads(Path(s['effects']).read_text())['effects']
assert ef['ykeey']=={'axis':'thermal','value':'warm'} and ef['sheey']=={'axis':'moisture','value':'wet'} and 'ykeea' not in ef
expected={'ZL3b':['MATCH','CONFLICT','CONFLICT','MATCH','DIFFERENT_NOT_OPPOSED'],'IT2a':['MATCH','CONFLICT','UNKNOWN','UNKNOWN','UNKNOWN'],'RF1b':['NO_EXACT_TARGET']*5}
raw={'ZL3b':['ykeey','chor','sheey','ysheol'],'IT2a':['ykeea','chor','sheey','ysheol'],'RF1b':['ykee@222;','chor','sheey','@222;sheol']}
for l in ctx['same_locus_source_lines']:
 ed=l['metadata']['edition'];assert [g['ivtff_group_raw'] for g in l['groups'][:4]]==raw[ed]
 assert l['metadata']['locus']=='f21r.12'
rows=list(csv.DictReader((D/'PREDICTIONS.tsv').open(),delimiter='\t'))
assert len(rows)==15
for ed,ss in expected.items():
 for c,st in zip(['wet','dry','cold','warm','hot'],ss):
  rr=[r for r in rows if r['edition']==ed and r['candidate']==c];assert len(rr)==1 and rr[0]['status']==st
r=json.loads((D/'RESULT.json').read_text());assert r['conditional_priority']==['wet'] and r['independent_meaning_confirmations']==0
assert len(ctx['paragraphs'])==2
out=dict(status='PASS',predictions=15,physical_loci=1,bound_files=len(s['hashes']),independent_meaning_validation=False)
(D/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
