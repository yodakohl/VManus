from pathlib import Path
import collections,csv,gzip,hashlib,itertools,json,math,random,re
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(n,v):(B/'artifacts'/n).write_text(json.dumps(v,indent=2)+'\n')
def collapse(u):
 out=[];runs=[];i=0
 while i<len(u):
  g=u[i];j=i+1
  if g in ('e','i'):
   while j<len(u) and u[j]==g:j+=1
   runs.append((len(out),g,j-i))
  out.append(g);i=j
 return out,runs
def moments(n,s):
 e=s-n;b,r=divmod(s,n);lo=(n-r)*b*(b-1)+r*b*(b+1);hi=e*(e+1)
 return 2*s*e/(n+1),lo,hi

def fixtures():
 cases=0;comps=0
 for n in range(1,6):
  for e in range(7):
   s=n+e;ds=[]
   for bars in itertools.combinations(range(1,s),n-1):
    edges=(0,)+bars+(s,);ls=[b-a for a,b in zip(edges,edges[1:])];ds.append(sum(l*(l-1) for l in ls));comps+=1
   mean,lo,hi=moments(n,s);assert math.isclose(sum(ds)/len(ds),mean) and min(ds)==lo and max(ds)==hi and (hi>lo)==(n>=2 and e>=2);cases+=1
 base=['q','o','k','e','d','i','n'];roundtrips=0
 for le,li in itertools.product(range(1,6),repeat=2):
  written=base[:3]+['e']*le+['d']+['i']*li+['n'];assert collapse(written)[0]==base;roundtrips+=1
 assert moments(2,4)==(16/3,4,6) # observed[2,2] still mobile: [1,3],[3,1].
 return {'status':'PASS','small_cells':cases,'positive_compositions':comps,'roundtrips':roundtrips,'constant_observed_lengths_can_be_mobile':True}

def evaluate(cells):
 mobile=[c for c in cells if len(c['events'])>=2 and sum(e['length'] for e in c['events'])-len(c['events'])>=2];leafcounts=collections.Counter(c['leaf'] for c in mobile);leafscores=collections.defaultdict(list);null=[0.0]*1999;rng=random.Random(1328);counts=sum(len(c['events']) for c in mobile);capacity=len(mobile)>=20 and counts>=100 and len(leafcounts)>=10
 for c in mobile:
  lengths=[e['length'] for e in c['events']];n=len(lengths);s=sum(lengths);mean,lo,hi=moments(n,s);d=sum(l*(l-1) for l in lengths);score=(d-mean)/(hi-lo);leafscores[c['leaf']].append(score);c.update({'n':n,'sum':s,'observed_D':d,'expected_D':mean,'D_min':lo,'D_max':hi,'score':score})
  if capacity:
   weight=1/(len(leafcounts)*leafcounts[c['leaf']])
   for rep in range(1999):
    bars=[0]+sorted(rng.sample(range(1,s),n-1))+[s];draw=sum((b-a)*(b-a-1) for a,b in zip(bars,bars[1:]));null[rep]+=weight*(draw-mean)/(hi-lo)
 ls={str(leaf):math.fsum(xs)/len(xs) for leaf,xs in sorted(leafscores.items())};obs=math.fsum(ls.values())/len(ls) if ls else None;p=(1+sum(abs(v)>=abs(obs)-1e-12 for v in null))/2000 if capacity else None;agree=sum(v*obs>0 for v in ls.values()) if ls else 0;nullmobile=capacity and max(null)-min(null)>1e-12;passed=capacity and nullmobile and abs(obs)>=.02 and agree*3>=2*len(ls) and p<=.05/6
 result={'status':'NO_CAPACITY' if not capacity else 'GEOMETRIC_ELONGATION_REJECTED' if passed else 'NOT_REJECTED_BY_FIXED_TEST','all_cells':len(cells),'mobile_cells':len(mobile),'mobile_occurrences':counts,'physical_leaves':len(ls),'score':obs,'same_direction_leaves':agree,'p_two_sided':p,'null_mobile':nullmobile,'null_min':min(null) if capacity else None,'null_max':max(null) if capacity else None,'leaf_scores':ls}
 return result,mobile,null if capacity else []
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 fx=fixtures();groups=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};results={};saved={};nulls={}
 for ed,rows in sorted(groups.items()):
  allcells=collections.defaultdict(list)
  for r in rows:
   assert r['page'] in allow and not r['page'].startswith('f84') and r['page'] not in ('f1r','f116v');assert r['kind']=='P' and r['left_separator']==r['right_separator']=='DEFINITE_SPACE';source,runs=collapse(r['units'])
   for slot,family,length in runs:allcells[(r['page'],tuple(source),slot,family)].append({'id':r['id'],'length':length})
  for family in ('e','i'):
   key=ed+'_'+family;cells=[{'page':p,'leaf':int(re.match(r'f(\d+)',p)[1]),'source':list(w),'slot':slot,'family':f,'events':sorted(v,key=lambda x:x['id'])} for (p,w,slot,f),v in sorted(allcells.items()) if f==family];result,mobile,null=evaluate(cells);results[key]=result;saved[key]=mobile;nulls[key]=null;print(key,{k:v for k,v in result.items() if k!='leaf_scores'},flush=True)
 save('CELLS.json',saved);save('NULL_SCORES.json',nulls);save('RESULT.json',{'status':'GEOMETRIC_ELONGATION_REJECTED_ALL_CASES' if all(r['status']=='GEOMETRIC_ELONGATION_REJECTED' for r in results.values()) else 'CASE_SPECIFIC_GEOMETRIC_RESULT','cases':results,'fixtures':fx})
if __name__=='__main__':main()
