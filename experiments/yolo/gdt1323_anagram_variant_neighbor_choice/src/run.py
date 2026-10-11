import collections,csv,gzip,hashlib,itertools,json,random,re
from fractions import Fraction
from pathlib import Path
import numpy as np
B=Path(__file__).resolve().parents[1];R=B.parents[2]
A='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
def read(p):
 d=p.read_bytes();return json.loads(gzip.decompress(d) if p.suffix=='.gz' else d)
def save(n,o):
 d=(json.dumps(o,indent=2)+'\n').encode();(B/'artifacts'/n).write_bytes(gzip.compress(d,mtime=0) if n.endswith('.gz') else d)
def fixture():
 words=['ab','ab','ba'];perms=list(itertools.permutations(range(3)));vals=[]
 for p in perms:
  out=[words[i] for i in p];vals.append(sum(x[-1]==y[0] for x,y in zip(out,out[1:])));assert (2**out.count('ab'))*(3**out.count('ba'))==12
  for a,b in itertools.product(range(3),repeat=2):assert all(sum({'a':a,'b':b}[g] for g in w)%3==(a+b)%3 for w in out)
 assert Fraction(sum(vals),len(vals))==Fraction(4,3)
 return {'occurrence_permutations':len(perms),'mean_echo':[4,3],'modular_keys':9}
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 fx=fixture();data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');allowed={x['page'] for x in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};results={}
 for ed,rr in sorted(data.items()):
  rows=sorted(rr,key=lambda x:x['id']);cells=collections.defaultdict(list);by={}
  for i,r in enumerate(rows):
   assert r['page'] in allowed and not r['page'].startswith(('f84','f116v','f1r'));assert r['kind']=='P' and r['left_separator']==r['right_separator']=='DEFINITE_SPACE';assert set(r['units'])<=set(A) and ''.join(r['units'])==r['ivtff_group_raw'];key=(r['locus'],int(r['source_group_index']));assert key not in by;by[key]=i;cells[(r['page'],tuple(sorted(r['units'])))].append(i)
  pools=[v for k,v in sorted(cells.items())];owner={i:j for j,pool in enumerate(pools) for i in pool};head=np.array([A.index(r['units'][0]) for r in rows]);tail=np.array([A.index(r['units'][-1]) for r in rows]);cfirst=[collections.Counter(int(head[i]) for i in p) for p in pools];clast=[collections.Counter(int(tail[i]) for i in p) for p in pools]
  pairs=[];mobile=[];expected={};leafn=collections.Counter()
  for (loc,pos),i in sorted(by.items()):
   if (loc,pos+1) not in by:continue
   j=by[(loc,pos+1)];pairs.append([rows[i]['id'],rows[j]['id']]);a,b=owner[i],owner[j];num=sum(clast[a][g]*cfirst[b][g] for g in range(22));den=len(pools[a])*len(pools[b])
   if a==b:num-=sum(tail[k]==head[k] for k in pools[a]);den=len(pools[a])*(len(pools[a])-1)
   p=Fraction(int(num),den);assert 0<=p<=1
   if 0<p<1:
    leaf=re.match(r'f(\d+)',rows[i]['page']).group(1);mobile.append({'left':i,'right':j,'leaf':leaf,'p':[p.numerator,p.denominator]});expected[leaf]=expected.get(leaf,Fraction())+p;leafn[leaf]+=1
  leaves=sorted(leafn,key=int);li={v:i for i,v in enumerate(leaves)};left=np.array([x['left'] for x in mobile],dtype=int);right=np.array([x['right'] for x in mobile],dtype=int);leafidx=np.array([li[x['leaf']] for x in mobile],dtype=int);denom=np.array([leafn[l] for l in leaves]);expect=np.array([float(expected[l]) for l in leaves]);base=np.arange(len(rows));obs=np.bincount(leafidx,weights=(tail[left]==head[right]).astype(int),minlength=len(leaves)).astype(int);effect=(obs-expect)/denom if leaves else np.array([]);T=float(np.mean(effect)) if leaves else 0.;capacity=len(mobile)>=100 and len(leaves)>=10;nullcounts=[];ts=[];rng=random.Random(1323)
  if capacity:
   for rep in range(1999):
    perm=base.copy()
    for pool in pools:
     if len(pool)>1:
      shuffled=pool.copy();rng.shuffle(shuffled);perm[pool]=shuffled
    scores=np.bincount(leafidx,weights=(tail[perm[left]]==head[perm[right]]).astype(int),minlength=len(leaves)).astype(int);nullcounts.append(scores.tolist());ts.append(float(np.mean((scores-expect)/denom)))
   pv=(1+sum(abs(t)>=abs(T)-1e-12 for t in ts))/2000;mobile_score=max(ts)-min(ts)>1e-12;consistent=sum(v*T>0 for v in effect);reject=mobile_score and pv<=.05/3 and abs(T)>=.01 and consistent*3>=2*len(leaves);status='INDEPENDENT_CHOICE_REJECTED' if reject else ('SCORE_IMMOBILE' if not mobile_score else 'NOT_REJECTED')
  else:pv=None;mobile_score=False;consistent=sum(v*T>0 for v in effect);status='NO_CAPACITY'
  result={'status':status,'groups':len(rows),'pairs':len(pairs),'cells':len(pools),'mobile_edges':len(mobile),'mobile_leaves':len(leaves),'T':T,'p_two_sided':pv,'direction_consistent_leaves':int(consistent),'score_mobile':mobile_score,'null_T_range':[min(ts),max(ts)] if ts else [],'leaf_results':[{'leaf':l,'n':leafn[l],'expected':[expected[l].numerator,expected[l].denominator],'observed':int(obs[li[l]]),'effect':float(effect[li[l]])} for l in leaves]};results[ed]=result
  save(ed+'_PANEL.json.gz',{'ids':[r['id'] for r in rows],'pairs':pairs,'pools':pools,'mobile':mobile,'leaves':leaves});save(ed+'_NULL_COUNTS.json.gz',nullcounts);print(ed,status,'mobile',len(mobile),'leaves',len(leaves),'T',T,'p',pv,flush=True)
 common=all(v['status']=='INDEPENDENT_CHOICE_REJECTED' for v in results.values());save('RESULT.json',{'status':'INDEPENDENT_ANAGRAM_CHOICE_REJECTED_ALL_READINGS' if common else 'NO_COMMON_ANAGRAM_CHOICE_REJECTION','fixtures':fx,'readers':results,'ceiling':'Necessary conditional spelling-choice consequence only; no key, meaning, general modular exclusion or independent replication.'})
if __name__=='__main__':main()
