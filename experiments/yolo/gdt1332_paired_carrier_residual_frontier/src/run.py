from pathlib import Path
from fractions import Fraction
import collections,gzip,hashlib,itertools,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
U=sorted('a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split())
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(name,obj):(B/'artifacts'/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def accepts(w,h):
 i=0
 while i<len(w):i+=2 if w[i] in h else 1
 return i==len(w)
def ratio(row):return Fraction(row['head_free'],row['parsable'])
def budgets(n):
 out={}
 for k in (0,1,2,5,10,20,50,100):out.setdefault(k,[]).append('count:'+str(k))
 for a,b in ((1,1000),(5,1000),(1,100),(2,100),(5,100),(1,10)):out.setdefault(n*a//b,[]).append('fraction:'+str(a)+'/'+str(b))
 return out
def summaries(table,n):
 frontier=[];best=None
 for cost in sorted({r['unparsed'] for r in table}):
  candidates=[r for r in table if r['unparsed']==cost];low=min(map(ratio,candidates))
  if best is None or low<best:
   ties=[r['heads'] for r in candidates if ratio(r)==low];frontier.append({'unparsed':cost,'lower_bound':[low.numerator,low.denominator],'heads':ties});best=low
 selected=[]
 for budget,labels in sorted(budgets(n).items()):
  candidates=[r for r in table if r['unparsed']<=budget];low=min(map(ratio,candidates)) if candidates else None;ties=[r for r in candidates if ratio(r)==low]
  selected.append({'budget':budget,'labels':labels,'lower_bound':[low.numerator,low.denominator] if low is not None else None,'heads':[r['heads'] for r in ties],'selected':ties[0] if ties else None})
 return frontier,selected
def fixtures():
 cases=0
 for h in (set(),{'x'},{'y'},{'x','y'}):
  code=[(c,) for c in 'xy' if c not in h]+[(c,t) for c in h for t in 'xy']
  for n in range(7):
   for w in itertools.product('xy',repeat=n):
    p=[True]+[False]*n
    for end in range(1,n+1):p[end]=any(end>=len(c) and p[end-len(c)] and w[end-len(c):end]==c for c in code)
    assert accepts(w,h)==p[-1]
    if not h.intersection(w):assert p[-1]
    cases+=1
 toy=[{'heads':[x],'unparsed':m,'parsable':10-m,'head_free':d} for x,m,d in [('a',0,5),('b',1,5),('c',2,2),('d',2,2),('e',3,2)]]
 f,s=summaries(toy,10);assert [r['unparsed'] for r in f]==[0,2];assert f[1]['heads']==[['c'],['d']];assert f[1]['lower_bound']==[1,4];assert ratio(toy[0])<ratio(toy[1]);return {'status':'PASS','prefix_cases':cases,'ratio_denominators_and_ties':True}
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 tests=fixtures();data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');tables={};results={};witnesses={}
 for ed,rows in sorted(data.items()):
  groups={}
  for row in rows:groups.setdefault(tuple(row['units']),[]).append(row)
  table=[];n=len(rows)
  for head in itertools.combinations(U,3):
   h=set(head);failed=[w for w in groups if not accepts(w,h)];bad=[r for w in failed for r in groups[w]];d=sum(len(rs) for w,rs in groups.items() if not h.intersection(w));m=len(bad);assert n>m
   table.append({'heads':list(head),'unparsed':m,'unparsed_types':len(failed),'unparsed_selectors':len({r['page'] for r in bad}),'parsable':n-m,'head_free':d,'bound_among_parsable':[d,n-m],'share_original_panel':[d,n]})
  f,s=summaries(table,n);selected={tuple(x['selected']['heads']) for x in s if x['selected']};witnesses[ed]=[{'heads':list(h),'unparsed_rows':sorted([r for w,rs in groups.items() if not accepts(w,set(h)) for r in rs],key=lambda r:r['id'])} for h in sorted(selected)];tables[ed]=table;results[ed]={'groups':n,'head_sets':len(table),'frontier':f,'budgets':s}
 save('ALL_HEAD_COUNTS.json',tables);save('RESIDUAL_WITNESSES.json',witnesses);save('RESULT.json',{'status':'DESCRIPTIVE_DISCREPANCY_FRONTIERS','fixtures':tests,'readers':results})
 for ed,r in results.items():print(ed,json.dumps([{'budget':x['budget'],'selected':x['selected']} for x in r['budgets']],indent=2))
if __name__=='__main__':main()
