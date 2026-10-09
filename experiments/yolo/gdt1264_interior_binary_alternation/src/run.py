import collections,datetime,gzip,hashlib,itertools,json,math,re,subprocess,sys
from fractions import Fraction
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def save(name,obj): (B/('artifacts/'+name+'.json')).write_text(json.dumps(obj,indent=2)+'\n')
def fraction(x):return [x.numerator,x.denominator]
def leaf(row):return int(re.match(r'f(\d+)',row['page'])[1])
def weights(words,vertices):
 observed=collections.Counter();expected=collections.defaultdict(Fraction)
 for word in words:
  n=len(word);counts=collections.Counter(word)
  for a,b in zip(word,word[1:]):
   if a!=b:observed[tuple(sorted([a,b]))]+=1
  for a,b in itertools.combinations(sorted(counts),2):expected[(a,b)]+=Fraction(2*counts[a]*counts[b],n)
 return {(a,b):Fraction(observed[(a,b)])-expected[(a,b)] for a,b in itertools.combinations(vertices,2)}
def compile_solver():
 binary=R/'.cache/interior_binary_cut_solver';subprocess.run(['g++','-O2','-std=c++17',str(B.relative_to(R)/'src/cut.cpp'),'-o',str(binary.relative_to(R))],cwd=R,check=True,capture_output=True,text=True);return binary

def solve(binary,matrix):
 text=str(len(matrix))+'\n'+'\n'.join(' '.join(map(str,row)) for row in matrix)+'\n';return json.loads(subprocess.run([str(binary)],input=text,text=True,capture_output=True,check=True).stdout)
def controls(binary):
 for mat in [[[0,1,1],[1,0,-1],[1,-1,0]],[[0,0,0],[0,0,0],[0,0,0]],[[0,-1,-1],[-1,0,-1],[-1,-1,0]]]:
  n=len(mat);vals={m:sum(mat[i][j] for i in range(n) for j in range(i+1,n) if ((m>>i)^(m>>j))&1) for m in range(2,1<<n,2)};best=max(vals.values());got=solve(binary,mat);assert got['best_score']==best and got['best_mask']==min(m for m,v in vals.items() if v==best) and got['ties']==sum(v==best for v in vals.values())
 assert weights([list('abab'),list('baba')],['a','b'])[('a','b')]==2
 assert weights(sorted(set(itertools.permutations('aabb'))),['a','b'])[('a','b')]==0
 return {'optimizer_matrices':3,'bag_fixtures':2,'status':'PASS'}
def setup():
 s=json.loads((B/'src/SPEC.json').read_text())
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
 for x in s['inputs']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
 data=json.loads(gzip.decompress((R/s['source']).read_bytes()))
 for reader in s['readers']:
  assert all(not r['page'].startswith('f84') and r['page']!='f116v' for r in data[reader])
 return s,data

def train():
 s,data=setup();rows=[r for r in data[s['primary']] if leaf(r)%2==s['train_parity'] and len(r['units'])-2>=s['minimum_interior_units']];words=[r['units'][1:-1] for r in rows];vertices=sorted({u for w in words for u in w});assert 2<=len(vertices)<=22
 exact=weights(words,vertices);matrix=[[0]*len(vertices) for _ in vertices];records=[]
 for (a,b),v in exact.items():
  i,j=vertices.index(a),vertices.index(b);q=round(v*s['weight_scale']);matrix[i][j]=matrix[j][i]=q;records.append({'a':a,'b':b,'exact':fraction(v),'quantized':q})
 assert sum(abs(v) for row in matrix for v in row)<(1<<62)
 binary=compile_solver();test=controls(binary);opt=solve(binary,matrix);labels={v:(opt['best_mask']>>i)&1 for i,v in enumerate(vertices)};chosen=sum(v for (a,b),v in exact.items() if labels[a]!=labels[b])
 out={'reader':s['primary'],'groups':len(rows),'physical_leaves':len({leaf(r) for r in rows}),'active_units':vertices,'labels':labels,'weights':records,'matrix':matrix,'optimizer':opt,'exact_selected_score':fraction(chosen),'controls':test,'source_ids':[r['id'] for r in rows]}
 save('TRAIN',out);save('TRAIN_LOCK',{'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'train_sha256':hashlib.sha256((B/'artifacts/TRAIN.json').read_bytes()).hexdigest()});print(json.dumps({k:out[k] for k in ['groups','physical_leaves','active_units','labels','optimizer','exact_selected_score']},indent=2))
def evaluate():
 s,data=setup();fit=json.loads((B/'artifacts/TRAIN.json').read_text());lock=json.loads((B/'artifacts/TRAIN_LOCK.json').read_text());assert hashlib.sha256((B/'artifacts/TRAIN.json').read_bytes()).hexdigest()==lock['train_sha256'];labels=fit['labels'];reports=[];all_events=[]
 for reader in s['readers']:
  seen={tuple(r['units']) for r in data[reader] if leaf(r)%2==s['train_parity']};test=[r for r in data[reader] if leaf(r)%2==s['test_parity']]
  for cohort in s['cohorts']:
   chosen=[r for r in test if cohort=='ALL' or tuple(r['units']) not in seen];counts=collections.Counter();sums=collections.defaultdict(lambda: {'groups':0,'edges':0,'observed':0,'expected':Fraction(0)})
   for r in chosen:
    word=r['units'][1:-1];counts['source_groups']+=1
    if len(word)<s['minimum_interior_units']:counts['too_short']+=1;continue
    counts['eligible_groups']+=1
    if not set(word)<=set(labels):counts['unknown_unit_groups']+=1;all_events.append({'reader':reader,'cohort':cohort,'id':r['id'],'status':'UNSEEN_TRAIN_UNIT','units':word});continue
    y=[labels[u] for u in word];a=y.count(0);b=y.count(1);n=len(y);observed=sum(x!=z for x,z in zip(y,y[1:]));expected=Fraction(2*a*b,n);q=sums[leaf(r)];q['groups']+=1;q['edges']+=n-1;q['observed']+=observed;q['expected']+=expected;counts['scorable_groups']+=1
    all_events.append({'reader':reader,'cohort':cohort,'id':r['id'],'page':r['page'],'leaf':leaf(r),'whole_units':r['units'],'units':word,'classes':y,'observed':observed,'expected':fraction(expected),'status':'SCORED'})
   leafrows=[]
   for folio,q in sorted(sums.items()):
    excess=Fraction(q['observed'])-q['expected'];effect=excess/q['edges'];leafrows.append({'leaf':folio,'groups':q['groups'],'edges':q['edges'],'observed':q['observed'],'expected':fraction(q['expected']),'excess':fraction(excess),'effect':fraction(effect),'effect_float':float(effect)})
   mean=sum((Fraction(*q['effect']) for q in leafrows),Fraction(0))/len(leafrows) if leafrows else Fraction(0);positive=sum(Fraction(*q['effect'])>0 for q in leafrows);pfrac=Fraction(positive,len(leafrows)) if leafrows else Fraction(0)
   passed=len(leafrows)>=s['minimum_leaves'] and pfrac>=Fraction(*s['minimum_positive_leaf_fraction']) and mean>=Fraction(*s['minimum_mean_excess'])
   reports.append({'reader':reader,'cohort':cohort,'counts':dict(counts),'scorable_leaves':len(leafrows),'positive_leaves':positive,'zero_leaves':sum(Fraction(*q['effect'])==0 for q in leafrows),'mean_effect':fraction(mean),'mean_effect_float':float(mean),'positive_fraction':fraction(pfrac),'gate_pass':passed,'leaves':leafrows})
 primary=[x for x in reports if x['reader']==s['primary']];out={'status':'BINARY_INTERIOR_ORDER_LEAD' if all(x['gate_pass'] for x in primary) else 'FIXED_BINARY_INTERIOR_LEAD_NOT_ESTABLISHED','train_labels':labels,'reports':reports,'claim_ceiling':'Exploratory fixed binary alternation beyond exact interior bags; no phonetics, semantic values, independent confirmation, H2 fraction or increment beyond position controls.'}
 save('RESULT',out);(B/'artifacts/EVENTS.json.gz').write_bytes(gzip.compress(json.dumps(all_events,separators=(',',':')).encode(),mtime=0));print(json.dumps({'status':out['status'],'reports':[{k:v for k,v in x.items() if k!='leaves'} for x in reports]},indent=2))
if __name__=='__main__':
 if sys.argv[1]=='train':train()
 elif sys.argv[1]=='evaluate':evaluate()
 else:raise SystemExit('train or evaluate')
