"""Acquire the registered complete two-position grid; no query at import."""
import argparse,importlib.util,itertools,json,math,re
from collections import Counter
from pathlib import Path
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]
def encode(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def aggregate(hits,s):
 words={p+'e'*a+k+'e'*b+'y':(p,k,a,b) for p,k,a,b in itertools.product(s['prefixes'],s['kernels'],s['e_lengths'],s['e_lengths'])}
 count=Counter((r['edition'],r['ivtff_group_raw']) for r in hits);cells=[]
 for word,(p,k,a,b) in sorted(words.items()):
  cells.append(dict(word=word,prefix=p,kernel=k,outer_e=a,inner_e=b,counts={ed:count[ed,word] for ed in s['editions']},folios={ed:sorted({re.match(r'f[0-9]+',r['page']).group() for r in hits if r['edition']==ed and r['ivtff_group_raw']==word}) for ed in s['editions']}))
 strata=[]
 for ed,p,k in itertools.product(s['editions'],s['prefixes'],s['kernels']):
  matrix=[[count[ed,p+'e'*a+k+'e'*b+'y'] for b in s['e_lengths']] for a in s['e_lengths']]
  rows=[sum(r) for r in matrix];cols=[sum(matrix[a][b] for a in range(3)) for b in range(3)];n=sum(rows)
  exp=[[rows[a]*cols[b]/n if n else 0. for b in range(3)] for a in range(3)]
  mi=sum(matrix[a][b]/n*math.log(matrix[a][b]/exp[a][b]) for a in range(3) for b in range(3) if matrix[a][b])
  strata.append(dict(edition=ed,prefix=p,kernel=k,n=n,matrix=matrix,expected=exp,outer_levels=sum(x>0 for x in rows),inner_levels=sum(x>0 for x in cols),both_margins_vary=sum(x>0 for x in rows)>1 and sum(x>0 for x in cols)>1,mutual_information_nats=mi))
 summary={}
 for ed in s['editions']:
  ss=[r for r in strata if r['edition']==ed];n=sum(r['n'] for r in ss)
  summary[ed]=dict(n=n,occupied=sum(c['counts'][ed]>0 for c in cells),joint_variation_strata=sum(r['both_margins_vary'] for r in ss),conditional_mutual_information_nats=sum(r['n']*r['mutual_information_nats'] for r in ss)/n if n else 0.)
 return cells,dict(status='DESCRIPTIVE_GRID_COMPLETE_NO_CONFIRMATORY_TEST',cells=36,hit_rows=len(hits),summary=summary,strata=strata)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args();s=json.loads((E/'src/SPEC.json').read_text())
 if a.check:hits=json.loads((E/'artifacts/HITS.json').read_text())
 else:
  path=ROOT/'experiments/yolo/gdt829_repeated_passage_reflow_capacity/src/run.py';sp=importlib.util.spec_from_file_location('source_reader',path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
  rows,guard=m.query(s);words={p+'e'*x+k+'e'*y+'y' for p,k,x,y in itertools.product(s['prefixes'],s['kernels'],s['e_lengths'],s['e_lengths'])};hits=[r for r in rows if r['ivtff_group_raw'] in words]
  (E/'artifacts/HITS.json').write_text(encode(hits));(E/'artifacts/GUARD.json').write_text(encode(guard))
 cells,result=aggregate(hits,s)
 for name,value in [('CELLS.json',cells),('RESULT.json',result)]:
  path=E/'artifacts'/name
  if a.check:assert path.read_text()==encode(value),name
  else:path.write_text(encode(value))
 print(encode(result))
if __name__=='__main__':main()
