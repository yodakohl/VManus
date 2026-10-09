from pathlib import Path
from itertools import product,permutations
import json,sys,hashlib,importlib.util
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
spec=importlib.util.spec_from_file_location('capacity',D/'src/run.py');cap=importlib.util.module_from_spec(spec);spec.loader.exec_module(cap)
def dp(a,b):
 row=list(range(len(b)+1))
 for i,x in enumerate(a,1):
  nxt=[i]
  for j,y in enumerate(b,1):nxt.append(min(nxt[-1]+1,row[j]+1,row[j-1]+(x!=y)))
  row=nxt
 return row[-1]
def main():
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 r=json.loads((A/'RESULT.json').read_text());source=json.loads(cap.old.SOURCE.read_text());tables=json.loads((ROOT/'experiments/yolo/gdt1184_contextual_initial_styles/artifacts/TABLES.json').read_text());count=0
 for model,entry in r['models'].items():
  sets={}
  for key,limit in [('I',21),('F',6)]:
   gainpairs=set()
   for p in product(range(limit+1),repeat=3):
    used=[x for x in p if x<limit]
    if len(used)!=len(set(used)) or (key=='I' and p.count(limit)>1):continue
    gainpairs.add(tuple(sum(entry['profiles'][b][key][v][j] for j,v in enumerate(p) if v<limit) for b in cap.BOOKS))
   stored=json.loads((A/(model+'_ATTAINABLE.json')).read_text())[key]
   assert gainpairs=={tuple(x['gains']) for x in stored}
   sets[key]=gainpairs
  for i,b in enumerate(cap.BOOKS):assert entry['individual_max_counts'][b]==entry['profiles'][b]['fixed']+max(x[i] for x in sets['I'])+max(x[i] for x in sets['F'])
  feasible=any(all(entry['intervals'][b][0]<=entry['profiles'][b]['fixed']+x[i]+y[i]<=entry['intervals'][b][1] for i,b in enumerate(cap.BOOKS)) for x in sets['I'] for y in sets['F'])
  assert feasible==entry['joint_feasible']
  if feasible:
   witness=entry['witness'];codec=cap.c.Codec(model,tables,witness['alphabets']);mapping=codec.alphabets['initial']+codec.alphabets['medial'][:3]+codec.alphabets['final'][:6]
   for book in cap.BOOKS:
    lines=cap.numeric_lines(codec,source[book]);pairs=[(a,b) for line in lines for a,b in zip(line,line[1:])]
    observed=sum(dp([mapping[x] for x in a],[mapping[x] for x in b])==1 for a,b in pairs)
    assert observed==witness['counts'][book];count+=len(pairs)
 assert r['status']==('EDIT_ONE_CAPACITY_EXISTS' if any(e['joint_feasible'] for e in r['models'].values()) else 'FIXED_ROLE_ALPHABET_FAMILY_IMPOSSIBLE')
 (A/'VALIDATION.json').write_text(json.dumps({'status':'PASS','independent_matching_reenumeration':True,'independent_DP_witness_pair_checks':count,'runner_random_map_book_checks':sum(e['random_map_book_checks'] for e in r['models'].values()),'scientific_status':r['status']},indent=2)+'\n');print((A/'VALIDATION.json').read_text())
if __name__=='__main__':main()
