from pathlib import Path
import collections,csv,gzip,hashlib,itertools,json,math,random,re
from fractions import Fraction
B=Path(__file__).resolve().parents[1];R=B.parents[2]
A=sorted('a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split(),key=lambda x:(-len(x),x));PAT=re.compile('|'.join(A))
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def eq(a,b):assert abs(a-b)<1e-10,(a,b)
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');saved=read(B/'artifacts/CELLS.json');res=read(B/'artifacts/RESULT.json');nulls=read(B/'artifacts/NULL_SCORES.json');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};joins=0;totalcells=0;draws=0
 for ed,rows in sorted(data.items()):
  byid={r['id']:r for r in rows};seen=set();cells=collections.defaultdict(list)
  for ph in ('DISCOVERY','EVALUATION'):
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{ph}_{ed}.json')['lines']:
    m=line['metadata']
    for g in line['groups']:
     if g[0] not in byid:continue
     r=byid[g[0]];assert g[0] not in seen;seen.add(g[0]);assert m['edition']==ed and m['kind']==r['kind']=='P' and m['page']==r['page'] and m['locus']==r['locus'];assert r['page'] in allow and not r['page'].startswith('f84') and r['page'] not in ('f1r','f116v');assert g[2]==r['ivtff_group_raw']==''.join(r['units']);assert int(g[1])==int(r['source_group_index']) and g[3]==g[4]==r['left_separator']==r['right_separator']=='DEFINITE_SPACE';joins+=1
     u=PAT.findall(g[2]);assert u==r['units'];source=[];runs=[]
     for unit,group in itertools.groupby(u):
      group=list(group)
      if unit in ('e','i'):runs.append((len(source),unit,len(group)));source.append(unit)
      else:source.extend(group)
     for slot,family,length in runs:cells[(m['page'],tuple(source),slot,family)].append({'id':g[0],'length':length})
  assert seen==set(byid)
  for family in ('e','i'):
   key=ed+'_'+family;allkeys=sorted(k for k in cells if k[3]==family);keys=[k for k in allkeys if len(cells[k])>=2 and sum(x['length'] for x in cells[k])-len(cells[k])>=2];actual=saved[key];assert len(actual)==len(keys);totalcells+=len(keys);perleaf=collections.Counter(int(re.match(r'f(\d+)',k[0])[1]) for k in keys);leafvalues=collections.defaultdict(list);count=sum(len(cells[k]) for k in keys);capacity=len(keys)>=20 and count>=100 and len(perleaf)>=10;rng=random.Random(1328);scores=[0.0]*1999
   for k,out in zip(keys,actual):
    page,word,slot,f=k;leaf=int(re.match(r'f(\d+)',page)[1]);events=sorted(cells[k],key=lambda x:x['id']);lengths=[x['length'] for x in events];n=len(lengths);s=sum(lengths);e=s-n;a=s//n;b=s%n;minimum=(n-b)*a*(a-1)+b*a*(a+1);maximum=e*(e+1);mu=Fraction(2*s*e,n+1);d=sum(x*x-x for x in lengths);score=Fraction(d-mu,maximum-minimum)
    assert {x:out[x] for x in ['page','leaf','source','slot','family','events','n','sum','observed_D','D_min','D_max']}=={'page':page,'leaf':leaf,'source':list(word),'slot':slot,'family':f,'events':events,'n':n,'sum':s,'observed_D':d,'D_min':minimum,'D_max':maximum};eq(out['expected_D'],float(mu));eq(out['score'],float(score));leafvalues[leaf].append(score)
    if capacity:
     for j in range(1999):
      selected=sorted(rng.sample(range(1,s),n-1));last=0;v=0
      for stop in selected+[s]:length=stop-last;v+=length*length-length;last=stop
      scores[j]+=float(Fraction(v-mu,maximum-minimum))/len(perleaf)/perleaf[leaf]
   leaves={str(l):float(sum(v,Fraction(0))/len(v)) for l,v in sorted(leafvalues.items())};obs=math.fsum(leaves.values())/len(leaves) if leaves else None;r=res['cases'][key];assert r['all_cells']==len(allkeys) and r['mobile_cells']==len(keys) and r['mobile_occurrences']==count and r['physical_leaves']==len(leaves) and set(r['leaf_scores'])==set(leaves)
   for l,v in leaves.items():eq(r['leaf_scores'][l],v)
   if obs is not None:eq(r['score'],obs)
   if capacity:
    assert len(nulls[key])==1999
    for x,y in zip(scores,nulls[key]):eq(x,y)
    draws+=1999;p=(1+sum(abs(v)>=abs(obs)-1e-12 for v in scores))/2000;eq(r['p_two_sided'],p);eq(r['null_min'],min(scores));eq(r['null_max'],max(scores));mobile=max(scores)-min(scores)>1e-12
   else:assert nulls[key]==[] and r['p_two_sided'] is None;p=None;mobile=False
   agree=sum(v*obs>0 for v in leaves.values()) if leaves else 0;passed=capacity and mobile and abs(obs)>=.02 and agree*3>=2*len(leaves) and p<=.05/6;assert r['same_direction_leaves']==agree and r['null_mobile']==mobile and r['status']==('NO_CAPACITY' if not capacity else 'GEOMETRIC_ELONGATION_REJECTED' if passed else 'NOT_REJECTED_BY_FIXED_TEST')
 # Independent weak-composition recursion verifies exact conditional geometric law.
 def weak(e,n):
  if n==1:yield(e,);return
  for first in range(e+1):
   for rest in weak(e-first,n-1):yield(first,)+rest
 nc=0;tot=0
 for n in range(1,6):
  for e in range(7):
   ds=[];weights=[]
   for xs in weak(e,n):
    ls=[x+1 for x in xs];ds.append(sum(x*(x-1) for x in ls));weights.append(Fraction(2,3)**n*Fraction(1,3)**e);tot+=1
   assert len(set(weights))==1;assert Fraction(sum(ds),len(ds))==Fraction(2*(n+e)*e,n+1);assert (len(set(ds))>1)==(n>=2 and e>=2);nc+=1
 assert res['fixtures']['small_cells']==nc and res['fixtures']['positive_compositions']==tot
 assert res['status']==('GEOMETRIC_ELONGATION_REJECTED_ALL_CASES' if all(r['status']=='GEOMETRIC_ELONGATION_REJECTED' for r in res['cases'].values()) else 'CASE_SPECIFIC_GEOMETRIC_RESULT')
 out={'status':'PASS','source_joins':joins,'mobile_cells':totalcells,'null_scores_reproduced':draws,'exact_small_cells':nc,'exact_compositions':tot,'method':'Independent raw-unit extraction, original915source joins, rational moments, scalar conditional samples and recursive weak compositions; no runner imported.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
