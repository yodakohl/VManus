import collections,functools,gzip,hashlib,itertools,json,math,re,sys
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2];GRID=[0,.25,.5,1,2]
SOURCE='experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'
LABELS='experiments/yolo/gdt1264_interior_binary_alternation/artifacts/TRAIN.json'
def save(name,obj):(B/('artifacts/'+name+'.json')).write_text(json.dumps(obj,indent=2)+'\n')
def leaf(row):return int(re.match(r'f(\d+)',row['page'])[1])
def logadd(a,b):
 if a==-math.inf:return b
 if b==-math.inf:return a
 return max(a,b)+math.log1p(math.exp(-abs(a-b)))
@functools.lru_cache(None)
def partitions(n,theta,beta):
 states={(0,-1):0.0}
 for i in range(n):
  nxt={}
  for (count,last),v in states.items():
   for bit in (0,1):
    key=(count+bit,bit);w=v+theta[5*i//n]*bit+beta*(last>=0 and last!=bit)
    nxt[key]=logadd(nxt.get(key,-math.inf),w)
  states=nxt
 return [logadd(states.get((k,0),-math.inf),states.get((k,1),-math.inf)) for k in range(n+1)]
def score(bits,theta,beta):return sum(theta[5*i//len(bits)]*x for i,x in enumerate(bits))+beta*sum(a!=b for a,b in zip(bits,bits[1:]))-partitions(len(bits),tuple(theta),beta)[sum(bits)]
def controls():
 count=0
 for n in range(3,9):
  for theta in [(0,)*5,(-1,.2,.7,-.4,.3)]:
   for beta in GRID:
    groups=collections.defaultdict(list)
    for x in itertools.product([0,1],repeat=n):groups[sum(x)].append(x)
    for k,words in groups.items():
     weights=[math.exp(sum(theta[5*i//n]*v for i,v in enumerate(x))+beta*sum(a!=b for a,b in zip(x,x[1:]))) for x in words]
     assert abs(partitions(n,theta,beta)[k]-math.log(sum(weights)))<1e-11
     assert abs(sum(math.exp(score(x,theta,beta)) for x in words)-1)<1e-11;count+=1
 return count

def setup():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=json.loads(gzip.decompress((R/SOURCE).read_bytes()));labels=json.loads((R/LABELS).read_text())['labels']
 for rows in data.values():assert all(not r['page'].startswith('f84') and r['page']!='f116v' for r in rows)
 return data,labels

def train():
 data,labels=setup();rows=[r for r in data['ZL3b'] if leaf(r)%2 and len(r['units'])>=5 and set(r['units'][1:-1])<=labels.keys()]
 words=[[labels[u] for u in r['units'][1:-1]] for r in rows];counts=[[0,0] for _ in range(5)]
 for x in words:
  for i,bit in enumerate(x):counts[5*i//len(x)][bit]+=1
 theta=[math.log((o+1)/(z+1)) for z,o in counts];grid=[{'beta':beta,'conditional_loglikelihood':sum(score(x,theta,beta) for x in words)} for beta in GRID]
 best=max(g['conditional_loglikelihood'] for g in grid);beta=min(g['beta'] for g in grid if best-g['conditional_loglikelihood']<=1e-10)
 model={'reader':'ZL3b','training_groups':len(rows),'training_leaves':len({leaf(r) for r in rows}),'position_counts_0_1':counts,'theta':theta,'beta_grid':grid,'selected_beta':beta,'controls_checked':controls()}
 save('MODEL',model);save('MODEL_LOCK',{'sha256':hashlib.sha256((B/'artifacts/MODEL.json').read_bytes()).hexdigest()});print(json.dumps(model,indent=2))

def evaluate():
 data,labels=setup();model=json.loads((B/'artifacts/MODEL.json').read_text());assert hashlib.sha256((B/'artifacts/MODEL.json').read_bytes()).hexdigest()==json.loads((B/'artifacts/MODEL_LOCK.json').read_text())['sha256']
 theta=model['theta'];beta=model['selected_beta'];out={};events=[]
 for reader,rows in data.items():
  seen_whole={tuple(r['units']) for r in rows if leaf(r)%2};seen_inner={tuple(r['units'][1:-1]) for r in rows if leaf(r)%2 and len(r['units'])>=5}
  cohorts={c:[] for c in ['ALL','UNSEEN_INTERIOR','UNSEEN_WHOLE']};census=collections.Counter()
  for row in rows:
   if leaf(row)%2:continue
   census['all_groups']+=1;inner=row['units'][1:-1]
   if len(inner)<3:census['too_short']+=1;continue
   if not set(inner)<=labels.keys():census['unknown_unit']+=1;events.append({'reader':reader,'id':row['id'],'status':'UNKNOWN_UNIT','units':inner});continue
   census['scorable']+=1;x=[labels[u] for u in inner];base=score(x,theta,0);aug=score(x,theta,beta);gain=(aug-base)/len(x)
   event={'reader':reader,'id':row['id'],'leaf':leaf(row),'n':len(x),'k':sum(x),'switches':sum(a!=b for a,b in zip(x,x[1:])),'logp_base':base,'logp_switch':aug,'gain_per_unit':gain,'unseen_interior':tuple(inner) not in seen_inner,'unseen_whole':tuple(row['units']) not in seen_whole};events.append(event);cohorts['ALL'].append(event)
   if event['unseen_interior']:cohorts['UNSEEN_INTERIOR'].append(event)
   if event['unseen_whole']:cohorts['UNSEEN_WHOLE'].append(event)
  summary={}
  for cohort,es in cohorts.items():
   leaves=collections.defaultdict(list)
   for e in es:leaves[e['leaf']].append(e['gain_per_unit'])
   means={str(k):sum(v)/len(v) for k,v in sorted(leaves.items())};avg=sum(means.values())/len(means) if means else 0;positive=sum(v>0 for v in means.values());capacity=len(es)>=100 and len(means)>=10
   passed=capacity and avg>=.01 and positive*3>=2*len(means)
   summary[cohort]={'groups':len(es),'leaves':len(means),'positive_leaves':positive,'equal_leaf_gain':avg,'event_mean_gain':sum(e['gain_per_unit'] for e in es)/len(es) if es else 0,'per_leaf':means,'status':'PASS' if passed else ('NONCONFIRMING' if capacity else 'CAPACITY_STOP')}
  out[reader]={'census':dict(census),'cohorts':summary}
 primary=[out['ZL3b']['cohorts'][c]['status'] for c in ['ALL','UNSEEN_INTERIOR']];status='PASS_BOTH' if primary==['PASS','PASS'] else ('CAPACITY_STOP' if 'CAPACITY_STOP' in primary else 'NO_JOINT_MATERIAL_PREDICTION')
 save('RESULT',{'status':status,'readers':out,'selected_beta':beta,'claim_ceiling':'Conditional binary order prediction given length/inventory only; no contentwriter, meanings, significance or independentheldoutsource.'});(B/'artifacts/EVENTS.json.gz').write_bytes(gzip.compress(json.dumps(events,separators=(',',':')).encode(),mtime=0));print(json.dumps({'status':status,'readers':{r:{c:{k:v for k,v in z.items() if k!='per_leaf'} for c,z in d['cohorts'].items()} for r,d in out.items()}},indent=2))
if __name__=='__main__':
 if sys.argv[1]=='controls':print(controls())
 elif sys.argv[1]=='train':train()
 elif sys.argv[1]=='evaluate':evaluate()
 elif sys.argv[1]=='all':train();evaluate()
