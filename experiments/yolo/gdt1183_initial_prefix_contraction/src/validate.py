from pathlib import Path
import hashlib,json,math,re
import codec as c,run
D=Path(__file__).resolve().parents[1];A=D/'artifacts'
PAT=re.compile(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]')
def signs(w):
 gs=PAT.findall(w);assert ''.join(gs)==w;return gs

def readcheck(filename,codec,recipes):
 blocks=(A/filename).read_text().strip().split('\n\n');assert len(blocks)==len(recipes);lines=[]
 for block,recipe in zip(blocks,recipes):
  ws=block.split();decoded=codec.decode([signs(w) for w in ws]);assert decoded==recipe['words'];assert codec.encode(decoded)==ws;lines.extend(line.split() for line in block.splitlines())
 return run.m.measure(lines),len(recipes)
def near(a,b):
 if isinstance(a,float):assert math.isclose(a,b,rel_tol=0,abs_tol=1e-12),(a,b)
 elif isinstance(a,dict):
  assert set(a)==set(b)
  for k in a:near(a[k],b[k])
 elif isinstance(a,list):
  assert len(a)==len(b)
  for x,y in zip(a,b):near(x,y)
 else:assert a==b,(a,b)

def main():
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((run.ROOT/p).read_bytes()).hexdigest()==h,p
 source=json.loads(run.SOURCE.read_text());targets=json.loads(run.TARGET.read_text())['targets'];tables=json.loads((A/'TABLES.json').read_text());assert tables==c.train(source);result=json.loads((A/'RESULT.json').read_text());total=0
 for model,entry in result['stage_A'].items():
  codec=c.Codec(model,tables);assert codec.K==entry['actual_frontier'];ok=True
  for col in ['b4','w1']:
   met,n=readcheck(f'A_{model}_{col}.txt',codec,source[col]);total+=n
   for ed,t in targets.items():
    comparison=run.m.compare(met,t);checks={k:comparison['diagnostics'][k] for k in run.NECESSARY};near(checks,entry['books'][col]['necessary_checks'][ed]);ok=ok and all(x['within'] for x in checks.values())
  assert ok==entry['necessary_pass'];assert entry['offered_capacity_possible']==(codec.K>=13)
  assert codec.encode(['in','dem'])!=codec.encode(['indem'])
  try:codec.decode([[codec.permutation[codec.K],c.FINAL['E'][0]]])
  except (AssertionError,ValueError):pass
  else:raise AssertionError('Unused initial accepted')
 for model,design in result['design'].items():
  codec=c.Codec(model,tables,design['permutation']);assert len(set(codec.permutation[:codec.K])|set(c.MEDIAL+c.FINAL['E']+c.FINAL['C']))==22;ok=True
  for col in ['b4','w1']:
   met,n=readcheck(f'B_{model}_{col}.txt',codec,source[col]);total+=n;near(met,design['metrics'][col]);comparison={ed:run.m.compare(met,t) for ed,t in targets.items()};near(comparison,design['comparison'][col]);ok=ok and all(x['joint_screen'] for x in comparison.values())
  assert ok==design['full_design_pass'] and design['optimization']['proposals']==5000
 passers=[model for model,d in result['design'].items() if d['full_design_pass']]
 if result['selected'] is None:
  assert not passers and not result['transfer_scored'] and result['status']=='STOP_NO_DESIGN_WRITER';assert not (A/'SELECTION_LOCK.json').exists()
 else:
  selected=min(passers,key=lambda x:(result['design'][x]['table_entries'],result['design'][x]['frontier'],result['design'][x]['optimization']['best_objective'],x));assert selected==result['selected'];choice=json.loads((A/'SELECTION_LOCK.json').read_text());assert choice['model']==selected and choice['table_sha256']==hashlib.sha256((A/'TABLES.json').read_bytes()).hexdigest();codec=c.Codec(selected,tables,choice['permutation']);ok=True
  for col,rs in source.items():
   met,n=readcheck(f'SELECTED_{col}.txt',codec,rs);total+=n;near(met,result['metrics'][col]);comparison={ed:run.m.compare(met,t) for ed,t in targets.items()};near(comparison,result['comparison'][col]);ok=ok and all(x['joint_screen'] for x in comparison.values())
  assert result['status']==('FULL_BASIC_SCREEN_PASS' if ok else 'SELECTED_WRITER_FAILS_TRANSFER')
 out={'status':'PASS','scope':'Frozen dependencies, exact public tables, persisted complete recipe decode/rewrite, inherited gates, capacity and selection rules','complete_recipe_roundtrips':total,'scientific_result':result['status'],'selected':result['selected']};(A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
