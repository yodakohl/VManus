from pathlib import Path
from collections import Counter
import json,re,math,hashlib
import run,codec as c
D=Path(__file__).resolve().parents[1];A=D/'artifacts'
PAT=re.compile(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]')
def signs(word):
 gs=PAT.findall(word);assert ''.join(gs)==word;return gs

def main():
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((run.ROOT/p).read_bytes()).hexdigest()==h,p
 source=json.loads(run.SOURCE.read_text());tables=json.loads((A/'TABLES.json').read_text());assert tables==c.train(source);result=json.loads((A/'RESULT.json').read_text());targets=json.loads(run.TARGET.read_text())['targets'];passing=[];total=0
 for model in c.MODELS:
  codec=c.Codec(model,tables);ok=True
  for col,rs in source.items():
   blocks=(A/f'{model}_{col}.txt').read_text().strip().split('\n\n');assert len(blocks)==len(rs);segments=[]
   for block,r in zip(blocks,rs):
    printed=block.split();decoded=codec.decode([signs(x) for x in printed]);assert decoded==r['words'];assert codec.encode(decoded)==printed;segments.extend(line.split() for line in block.splitlines());total+=1
   measured=run.m.measure(segments);reported=result['metrics'][model][col]
   for k,v in measured.items():
    if isinstance(v,float):assert math.isclose(v,reported[k],abs_tol=1e-12,rel_tol=0),(model,col,k)
    else:assert v==reported[k]
   flat=[x for line in segments for x in line][:8000];co=Counter(flat)
   assert len(co)==reported['types'] and sum(sorted(co.values(),reverse=True)[:10])/8000==reported['top10_share']
   comparison={ed:run.m.compare(measured,t) for ed,t in targets.items()}
   for ed,v in comparison.items():assert v['joint_screen']==result['comparison'][model][col][ed]['joint_screen'] and v['passed']==result['comparison'][model][col][ed]['passed']
   ok=ok and all(v['joint_screen'] for v in comparison.values())
  if ok:passing.append(model)
 assert passing==result['passing_models']
 for model in c.MODELS:
  codec=c.Codec(model,tables);code=codec.encode(['salz','salz','salz']);assert code[0]==code[1]==code[2];assert codec.decode([signs(x) for x in code])==['salz']*3
  paths=[tuple(p) for p in tables['models'][model]['codes'].values()]+[tuple(p) for p in tables['models'][model]['dummy_paths']];assert len(paths)==len(set(paths))
  for path in paths:
   assert all(path[:i] not in set(paths) for i in range(1,len(path)))
 out={'status':'PASS','scope':'Persisted complete text reversal and rewrite; exact tables and counts; alphabet, decisions and fixed hashes','complete_recipe_roundtrips':total,'scientific_result':result['status'],'passing_models':passing};(A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
