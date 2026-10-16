"""Locked blind controls. Truth directory must be supplied explicitly."""
import argparse,hashlib,itertools,json,math,os,random,secrets
from pathlib import Path
import numpy as np
from prepare import B,R,load,save,sha

def backward(shape,key,mod=27):
 A=len(key); L=shape['L']; tables={}; zlen=np.zeros((L+1,mod)); weights=np.asarray(key)
 for n in range(1,L+1):
  b=np.zeros((n+1,A,mod)); b[n,:,0]=1
  for i in range(n-1,0,-1):
   t=np.asarray(shape['transition'][n][i-1]); shifted=np.asarray([np.roll(b[i+1,j],int(weights[j])) for j in range(A)])
   b[i]=t@shifted
  for j in range(A): zlen[n]+=shape['initial'][n][j]*np.roll(b[1,j],int(weights[j]))
  tables[n]=b
 z=np.asarray(shape['p_len'])@zlen
 assert abs(float(z.sum())-1)<1e-10 and np.all(z>=0)
 return tables,zlen,z

def choose(rng,masses):
 total=math.fsum(float(x) for x in masses); assert total>0 and all(x>=0 for x in masses)
 t=rng.random()*total; acc=0.
 for i,p in enumerate(masses):
  acc+=float(p)
  if t<acc: return i
 return max(i for i,x in enumerate(masses) if x>0)

def sample(shape,key,state,rng,prepared,mod=27):
 tables,zlen,z=prepared; assert z[state]>0
 n=choose(rng,[shape['p_len'][j]*zlen[j,state] for j in range(shape['L']+1)]); assert n>0
 b=tables[n]; remaining=state; out=[]
 for i in range(n):
  probs=shape['initial'][n] if i==0 else shape['transition'][n][i-1][out[-1]]
  masses=[probs[j]*b[i+1,j,(remaining-key[j])%mod] for j in range(len(key))]
  j=choose(rng,masses); out.append(j); remaining=(remaining-key[j])%mod
 assert remaining==0
 return out

def controls():
 shape={'L':3,'p_len':[0,.2,.3,.5],'initial':[[0,0]]+[[.3,.7]]*3,'transition':[[],[],[[[.2,.8],[.6,.4]]],[[[.2,.8],[.6,.4]],[[.7,.3],[.1,.9]]]]}
 checks=0
 for key in itertools.product(range(3),repeat=2):
  prep=backward(shape,key,3); exact=np.zeros(3)
  for n in range(1,4):
   for word in itertools.product(range(2),repeat=n):
    p=shape['p_len'][n]*shape['initial'][n][word[0]]
    for i in range(1,n): p*=shape['transition'][n][i-1][word[i-1]][word[i]]
    exact[sum(key[j] for j in word)%3]+=p
  assert np.max(np.abs(exact-prep[2]))<1e-12
  for state in range(3):
   if prep[2][state]>0:
    for rep in range(10):
     w=sample(shape,key,state,random.Random(rep),prep,3); assert sum(key[j] for j in w)%3==state; checks+=1
 # Complete recurrence including first packet and nonzero offset.
 for b in range(3):
  s=0
  for c in [0,1,2,2,0]:
   nxt=(s+c-b)%3; assert (nxt-s+b)%3==c; s=nxt
 return {'status':'PASS','exhaustive_keys':9,'sampler_state_checks':checks,'state_recurrence':True}

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--controls',action='store_true'); ap.add_argument('--secret-dir'); ap.add_argument('--lock'); ap.add_argument('--replay-truth'); ap.add_argument('--output-dir'); args=ap.parse_args()
 if args.controls: print(json.dumps(controls())); return
 assert args.lock and ((args.secret_dir and not args.replay_truth and not args.output_dir) or (args.replay_truth and args.output_dir and not args.secret_dir)), 'Choose blind secret directory or replay truth plus fresh output directory, with root lock'
 lockpath=Path(args.lock); lock=load(lockpath)
 bound={}
 for path,digest in lock['hashes'].items():
  assert sha(R/path)==digest,path; bound[path]=digest
 meta=load(B/'artifacts/MODELS.json')
 required=[str(Path(__file__).resolve().relative_to(R)),str((B/'src/prepare.py').relative_to(R)),str((B/'artifacts/MODELS.json').relative_to(R)),meta['shape']['path']]+[m['path'] for m in meta['models']]
 assert all(p in bound for p in required)
 for item in [meta['shape'],*meta['models'],meta['manifest']]: assert sha(R/item['path'])==item['sha256']
 replay=load(Path(args.replay_truth)) if args.replay_truth else None
 output=Path(args.output_dir) if replay is not None else B/'artifacts'
 if replay is not None:
  assert not output.exists() or not any(output.iterdir()), 'Replay output must be fresh or empty'
  output.mkdir(parents=True,exist_ok=True)
 secret=output if replay is not None else Path(args.secret_dir); secret.mkdir(mode=0o700,parents=True,exist_ok=True); os.chmod(secret,0o700); truthpath=secret/'TRUTH.json'; assert not truthpath.exists() and not (output/'CASES.json').exists()
 seed=replay['seed'] if replay is not None else secrets.randbits(256); rng=random.Random(seed); shape=load(R/meta['shape']['path']); allcases=[]
 for model in meta['models']:
  src=R/model['source_path']; assert sha(src)==model['source_sha256']; text=' '.join(src.read_text().split()); assert hashlib.sha256(text.encode()).hexdigest()==model['collapsed_sha256']
  split=model['split_index']; selected=[]
  for n in [77,120]:
   starts=[i for i in range(split,len(text)-n+1) if (i==0 or text[i-1]==' ') and text[i]!=' ' and all(i+n<=a or i>=e for a,e in selected)]
   assert starts; start=starts[rng.randrange(len(starts))]; selected.append((start,start+n)); fragment=text[start:start+n]
   while True:
    key=[rng.randrange(27) for _ in shape['signs']]
    if any(k%3 for k in key): break
   offset=rng.randrange(27); prep=backward(shape,key); assert np.all(prep[2]>0)
   def encode(message):
    state=0; units=[]
    for ch in message:
     code=0 if ch==' ' else ord(ch)-96; state=(state+code-offset)%27; units.append(sample(shape,key,state,rng,prep))
    return units
   record={'kind':'POSITIVE','language':model['language'],'length':n,'text':fragment,'weights':key,'b':offset,'fragment_start':start,'fragment_end':start+n,'split_index':split,'source_sha256':model['source_sha256'],'collapsed_sha256':model['collapsed_sha256'],'units':encode(fragment),'tag':model['language']+'_'+str(n)}; allcases.append(record)
   if n==77:
    perm=list(range(n)); rng.shuffle(perm); negative=''.join(fragment[i] for i in perm)
    allcases.append({'kind':'NEGATIVE','language':model['language'],'length':n,'text':negative,'weights':key,'b':offset,'permutation':perm,'parent_tag':record['tag'],'units':encode(negative),'tag':model['language']+'_negative'})
 rng.shuffle(allcases)
 for i,case in enumerate(allcases): case['id']=f'C{i:02d}'
 tagids={c['tag']:c['id'] for c in allcases}
 for c in allcases:
  if 'parent_tag' in c: c['parent_id']=tagids[c['parent_tag']]
 truth={'seed':seed,'algorithm':'Python random.Random; exact backward residue DP','model_manifest_sha256':sha(B/'artifacts/MODELS.json'),'generation_lock_sha256':sha(lockpath),'cases':allcases}
 if replay is not None:
  assert truth==replay, 'Replay differs from released truth'
 fd=os.open(truthpath,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as f: json.dump(truth,f,separators=(',',':')); f.write('\n')
 save(output/'CASES.json',{'cases':[{'id':c['id'],'units':c['units']} for c in allcases]})
 print(json.dumps({'status':'GENERATED','cases':18,'cases_sha256':sha(output/'CASES.json'),'truth_written_privately':True}))
if __name__=='__main__': main()
