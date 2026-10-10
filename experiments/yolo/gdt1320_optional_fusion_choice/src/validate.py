import collections,csv,gzip,hashlib,itertools,json,math,random,re
from fractions import Fraction
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 d=p.read_bytes();return json.loads(gzip.decompress(d) if p.suffix=='.gz' else d)
def tagged(u,order):
 source=[];tags=[]
 for i,g in enumerate(u):
  pair=['ch',g[1]] if g in ['ckh','cth','cph','cfh'] else [g]
  if len(pair)==2 and order=='HB':pair.reverse()
  source.extend(pair);tags.extend([i]*len(pair))
 ev=[]
 for j in range(len(source)-1):
  left,right=source[j:j+2]
  if order=='BH' and left=='ch' and right in ['k','t','p','f']:ev.append((j,right,int(tags[j]==tags[j+1])))
  if order=='HB' and right=='ch' and left in ['k','t','p','f']:ev.append((j,left,int(tags[j]==tags[j+1])))
 return source,ev

def estimate(es,ys,details=False):
 # Independent occurrence lists and exact rational probabilities.
 train=collections.defaultdict(list);words=collections.defaultdict(list)
 for e,y in zip(es,ys):
  if e['leaf']%2:train[e['c'],e['h']].append(y);words[e['c'],e['h'],tuple(e['source'])].append(y)
 leaf=collections.defaultdict(list);checks=[]
 for e,y in zip(es,ys):
  if e['leaf']%2:continue
  v=train[e['c'],e['h']];w=words[e['c'],e['h'],tuple(e['source'])];p=Fraction(2*sum(v)+1,2*len(v)+2);q=(sum(w)+2*p)/(len(w)+2);g=math.log(float(q if y else 1-q))-math.log(float(p if y else 1-p));leaf[e['leaf']].append(g);checks.append((float(p),float(q),g))
 value=sum(sum(v)/len(v) for v in leaf.values())/len(leaf) if leaf else 0
 return (value,checks) if details else value

def fixture():
 tested=0
 for order in ['BH','HB']:
  for n in range(5):
   for source in itertools.product(['ch','k','t','a'],repeat=n):
    pairs=[j for j in range(n-1) if (source[j]=='ch' and source[j+1] in ['k','t'])] if order=='BH' else [j for j in range(n-1) if source[j] in ['k','t'] and source[j+1]=='ch']
    mass=Fraction()
    for bits in itertools.product([0,1],repeat=len(pairs)):
     choices=dict(zip(pairs,bits));u=[];j=0;prob=Fraction(1)
     for y in bits:prob*=Fraction(1,3) if y else Fraction(2,3)
     mass+=prob
     while j<n:
      if choices.get(j)==1:u.append('c'+source[j+1 if order=='BH' else j]+'h');j+=2
      else:u.append(source[j]);j+=1
     back,ev=tagged(u,order);assert back==list(source);assert [e[2] for e in ev]==list(bits);tested+=1
    assert mass==1
 return tested

def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 fx=fixture();strict=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');stored=read(B/'artifacts/OPPORTUNITIES.json.gz');scores=read(B/'artifacts/HELD_SCORES.json.gz');result=read(B/'artifacts/RESULT.json');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};joins=0;checks=0;perms=0
 for ed,rows in strict.items():
  byid={row['id']:row for row in rows};metadata={};found=set()
  for phase in ['DISCOVERY','EVALUATION']:
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{ed}.json')['lines']:
    m=line['metadata']
    for g in line['groups']:
     if g[0] not in byid:continue
     row=byid[g[0]];assert row['page']==m['page'] and row['page'] in allow and not row['page'].startswith('f84') and row['page'] not in ['f1r','f116v'];assert row['locus']==m['locus'] and row['kind']==m['kind']=='P' and m['edition']==ed;assert g[2]==row['ivtff_group_raw']==''.join(row['units']);assert int(g[1])==int(row['source_group_index']);assert g[3]==g[4]==row['left_separator']==row['right_separator']=='DEFINITE_SPACE';assert g[0] not in found;found.add(g[0]);metadata[g[0]]=m;joins+=1
  assert len(found)==len(rows)
  for order in ['BH','HB']:
   key=ed+'_'+order;es=[]
   for row in rows:
    m=metadata[row['id']]
    if m['currier'] not in ['A','B']:continue
    source,ev=tagged(row['units'],order);leaf=int(re.match(r'f(\d+)',row['page'])[1])
    for pos,h,y in ev:es.append({'id':row['id'],'page':row['page'],'locus':row['locus'],'units':row['units'],'source':source,'position':pos,'h':h,'y':y,'c':m['currier'],'leaf':leaf,'train':bool(leaf%2)})
   assert es==stored[key];ys=[e['y'] for e in es];value,prob=estimate(es,ys,True);actual=result['cases'][key];assert math.isclose(value,actual['equal_leaf_gain'],abs_tol=1e-12);held=[e for e in es if not e['train']];assert len(prob)==len(scores[key])==len(held)
   for e,(p,q,g),s in zip(held,prob,scores[key]):
    assert all(s[k]==v for k,v in e.items());assert abs(s['baseline_p']-p)<1e-14 and abs(s['word_p']-q)<1e-14 and abs(s['gain']-g)<1e-12;checks+=1
   groups={k:[i for i,e in enumerate(es) if (e['c'],e['h'])==k] for k in sorted({(e['c'],e['h']) for e in es})};rng=random.Random(1320);null=[]
   for rep in range(199):
    z=ys.copy()
    for ix in groups.values():
     labels=[ys[i] for i in ix];rng.shuffle(labels)
     for i,y in zip(ix,labels):z[i]=y
     assert sum(z[i] for i in ix)==sum(ys[i] for i in ix)
    v=estimate(es,z);assert abs(v-actual['null_scores'][rep])<1e-12;null.append(v);perms+=1
   p=(1+sum(x>=value for x in null))/200;assert p==actual['monte_carlo_p'];leaf=collections.defaultdict(list)
   for e,(_,_,g) in zip(held,prob):leaf[e['leaf']].append(g)
   assert len(held)==actual['held_opportunities'] and len(leaf)==actual['leaves'];positive=sum(sum(v)/len(v)>0 for v in leaf.values());assert positive==actual['positive_leaves'];capacity=len(held)>=100 and len(leaf)>=10;lead=capacity and value>=.01 and positive*3>=2*len(leaf) and p<=.05/6;status='NO_CAPACITY' if not capacity else ('WORD_CONDITIONED_CHOICE_GAIN' if lead else 'NO_RETAINED_WORD_GAIN');assert status==actual['status']
 assert joins==result['source_joins'];receipt={'status':'PASS','source_joins':joins,'held_probabilities_checked':checks,'permutations_checked':perms,'toy_renderings_checked':fx,'scope':'Independent tagged-origin extraction and rational score validation; source fidelity, not native glyph or meaning validation.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
