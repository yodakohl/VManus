from pathlib import Path
import json,hashlib,re,math
import codec as c,run
D=Path(__file__).resolve().parents[1];A=D/'artifacts'
PAT=re.compile(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]')
def signs(w):
 gs=PAT.findall(w);assert ''.join(gs)==w;return gs

def near(a,b):
 if isinstance(a,float):assert math.isclose(a,b,abs_tol=1e-12,rel_tol=0)
 elif isinstance(a,dict):
  assert set(a)==set(b)
  for k in a:near(a[k],b[k])
 elif isinstance(a,list):
  assert len(a)==len(b)
  for x,y in zip(a,b):near(x,y)
 else:assert a==b

def readcheck(name,codec,recipes):
 blocks=(A/name).read_text().strip().split('\n\n');assert len(blocks)==len(recipes);segments=[]
 for block,r in zip(blocks,recipes):
  printed=block.split();decoded=codec.decode([signs(w) for w in printed]);assert decoded==r['words'];assert codec.encode(decoded)==printed;segments.extend(line.split() for line in block.splitlines())
 return run.m.measure(segments)
def main():
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((run.ROOT/p).read_bytes()).hexdigest()==h,p
 source=json.loads(run.SOURCE.read_text());targets=json.loads(run.TARGET.read_text())['targets'];tables=json.loads((A/'TABLES.json').read_text());assert tables==json.loads(run.TABLES.read_text());result=json.loads((A/'RESULT.json').read_text());total=0
 for model,entry in result['stage_A'].items():
  codec=c.Codec(model,tables);ok=True
  for col in ['b4','w1']:
   met=readcheck(f'A_{model}_{col}.txt',codec,source[col]);total+=len(source[col])
   for ed,t in targets.items():
    co=run.m.compare(met,t);checks={k:co['diagnostics'][k] for k in run.NECESSARY};near(checks,entry['books'][col]['necessary_checks'][ed]);ok=ok and all(z['within'] for z in checks.values())
  assert ok==entry['necessary_pass']
 for model,design in result['design'].items():
  assert len(design['restarts'])==4 and all(x['optimization']['proposals']==4000 for x in design['restarts']);best=min(range(4),key=lambda i:design['restarts'][i]['optimization']['best_objective']);assert best==design['chosen_restart'] and design['alphabets']==design['restarts'][best]['alphabets'];assert run.coverage(design['alphabets']);codec=c.Codec(model,tables,design['alphabets']);ok=True
  for col in ['b4','w1']:
   met=readcheck(f'B_{model}_{col}.txt',codec,source[col]);total+=len(source[col]);near(met,design['metrics'][col]);co={ed:run.m.compare(met,t) for ed,t in targets.items()};near(co,design['comparison'][col]);ok=ok and all(z['joint_screen'] for z in co.values())
  assert ok==design['full_design_pass']
  assert codec.encode(['in','dem'])!=codec.encode(['indem']);example=['nicht','salzen.','zauberknolle'];encoded=codec.encode(example);assert codec.decode([signs(x) for x in encoded])==example
  wrong=[signs(encoded[0])];wrong[0][0]=codec.permutation[0]
  try:codec.decode(wrong)
  except (AssertionError,ValueError):pass
  else:raise AssertionError('Wrong initial style accepted')
 lock=json.loads((A/'DESIGN_LOCK.json').read_text());assert lock['designs']==result['design'];assert lock['table_sha256']==hashlib.sha256((A/'TABLES.json').read_bytes()).hexdigest()
 assert set(result['transfer'])=={m for m,d in result['design'].items() if d['full_design_pass']}
 for model,transfer in result['transfer'].items():
  codec=c.Codec(model,tables,result['design'][model]['alphabets']);ok=True
  for col,rs in source.items():
   met=readcheck(f'T_{model}_{col}.txt',codec,rs);total+=len(rs);near(met,transfer['metrics'][col]);co={ed:run.m.compare(met,t) for ed,t in targets.items()};near(co,transfer['comparison'][col]);ok=ok and all(z['joint_screen'] for z in co.values())
  assert ok==transfer['full_pass']
 assert result['passing_models']==[model for model,t in result['transfer'].items() if t['full_pass']]
 out={'status':'PASS','scope':'Frozen inputs, persisted complete source decoding/reencoding, public style and counter, offered alphabet, necessary/full gates and frozen design selection','scientific_result':result['status'],'complete_recipe_roundtrips':total,'passing_models':result['passing_models']};(A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
