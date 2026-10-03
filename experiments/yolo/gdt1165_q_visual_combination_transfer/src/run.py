"""Frozen held-combination visual operator assay; no meanings assigned."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import argparse,collections,gzip,hashlib,importlib.util,json,math,random
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
OLD=R/'experiments/yolo/gdt1157_cross_situational_visual_words/src/run.py'
sp=importlib.util.spec_from_file_location('frozen1157',OLD);old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old)
D=None
def digest(x):return hashlib.sha256(json.dumps(x,separators=(',',':'),sort_keys=True).encode()).hexdigest()
def save(name,x):
 data=(json.dumps(x,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
 (A/name).write_bytes(gzip.compress(data,mtime=0) if name.endswith('.gz') else data)
def logit(p):
 p=np.clip(p,1e-9,1-1e-9);return np.log(p)-np.log1p(-p)

def base_profiles(raw,held):
 """Unchanged1157 single-feature fits; retain predictions for all pages."""
 y=D['base'];lids=D['leaf_ids'];leaves=D['leaves'];n,nw=y.shape
 train=np.flatnonzero(lids!=held);mask=old.consensus(raw);full=(mask>=0).all(1)
 compat=((mask[:,None,:]<0)|(mask[:,None,:]==old.STATES[None,:,:])).all(2)
 counts=y[train].sum(0);g=(counts+.5)/(len(train)+1);p=(counts+10*g)/(len(train)+10)
 wordcap=np.array([y[lids==l].max(0) for l in leaves if l!=held]).sum(0)>=2
 fyes=np.array([(mask[lids==l]==1).any(0) for l in leaves if l!=held]).sum(0)
 fno=np.array([(mask[lids==l]==0).any(0) for l in leaves if l!=held]).sum(0)
 eligible=(fyes>=2)&(fno>=2);prior=np.full(64,1/64)
 for i in train:
  if full[i]:prior[np.flatnonzero((old.STATES==mask[i]).all(1))[0]]+=1
 posterior=compat*prior;posterior/=posterior.sum(1,keepdims=True)
 fp=posterior@old.STATES;mu=fp[train].mean(0);var=mu-mu**2
 bgll=(y[train]*np.log(p)+(1-y[train])*np.log1p(-p)).sum(0)
 scores=np.full((7,nw),-np.inf);scores[6]=bgll
 models=np.broadcast_to(p[None,:,None],(7,nw,n)).copy();betas=np.zeros((6,nw))
 for j in range(6):
  if not eligible[j]:continue
  z=(np.array([0.,1.])-mu[j])/math.sqrt(var[j]) if var[j]>1e-12 else np.zeros(2)
  bi,obj,yp,_=old.arm(p,np.column_stack((1-fp[:,j],fp[:,j])),z,y,train,var[j]>1e-12)
  scores[j]=np.where(wordcap,obj,-np.inf);models[j]=yp;betas[j]=old.BETAS[bi]
 ties=scores>=scores.max(0)[None,:]-1e-12
 visual=(models*ties[:,:,None]).sum(0)/ties.sum(0)[:,None]
 rawscore=logit(visual)-logit(p)[:,None];sm=rawscore[:,train].mean(1);sd=rawscore[:,train].std(1)
 zscore=np.divide(rawscore-sm[:,None],sd[:,None],out=np.zeros_like(rawscore),where=sd[:,None]>1e-12)
 return zscore,p,{'held_leaf':int(held),'background':p.tolist(),'visual_probability_all_pages':visual.tolist(),'score_mean':sm.tolist(),'score_sd':sd.tolist(),'selected_models':[[j for j in range(7) if ties[j,w]] for w in range(nw)],'feature_betas':betas.tolist(),'joint_state_prior':prior.tolist(),'word_capacity':wordcap.tolist(),'feature_capacity':eligible.tolist()}

def logistic(X,y,w):
 k=X.shape[1];b=np.zeros(k);pen=np.full(k,.05);pen[0]=0
 def objective(v):
  s=X@v;return float(w@(np.logaddexp(0,s)-y*s)+.5*np.dot(pen*v,v))
 converged=False;reason='MAX_ITERATIONS'
 for steps in range(101):
  z=X@b;p=old.expit(z);grad=X.T@(w*(p-y))+pen*b
  if np.max(np.abs(grad))<=1e-9:converged=True;reason='GRADIENT';break
  if steps==100:break
  H=X.T@((w*p*(1-p))[:,None]*X)+np.diag(pen)
  try:direction=np.linalg.solve(H,grad)
  except np.linalg.LinAlgError:reason='SINGULAR_HESSIAN';break
  before=objective(b);descent=float(grad@direction);alpha=1.
  for back in range(60):
   candidate=b-alpha*direction
   if objective(candidate)<=before-1e-4*alpha*descent:b=candidate;break
   alpha*=.5
  else:reason='BACKTRACKING_FAIL';break
 return b,{'converged':converged,'iterations':steps,'reason':reason,'max_abs_gradient':float(np.max(np.abs(grad))),'objective':objective(b)}

def event_weights(indices):
 f=D['event_family'][indices];l=D['event_leaf'][indices];w=np.zeros(len(indices));families=np.unique(f)
 for family in families:
  fl=np.unique(l[f==family])
  for leaf in fl:
   take=(f==family)&(l==leaf);w[take]=1/(len(families)*len(fl)*take.sum())
 return w

def pipeline(raw,details=False):
 nf=len(D['families']);loss={a:[[] for _ in range(nf)] for a in ['C','FULL','ID','INV']}
 folds=[];empty_folds=[];base_details=[];failures=[];negative=0;active=0
 for leaf in D['leaves']:
  visual,p,bd=base_profiles(raw,leaf)
  if details:base_details.append(bd)
  nuisance=np.column_stack((D['nuisance'],logit(p)[D['event_family']]))
  vs=visual[D['event_family'],D['event_page']]
  for family in range(nf):
   test=np.flatnonzero((D['event_family']==family)&(D['event_leaf']==leaf))
   if not len(test):
    empty_folds.append({'family_index':family,'held_leaf':int(leaf),'status':'EMPTY'})
    continue
   train=np.flatnonzero((D['event_family']!=family)&(D['event_leaf']!=leaf));w=event_weights(train)
   if len(np.unique(D['event_family'][train]))!=nf-1:raise ValueError('training family missing')
   means=w@nuisance[train,3:];sd=np.sqrt(w@((nuisance[train,3:]-means)**2))
   xn=nuisance.copy();xn[:,3:]=np.divide(xn[:,3:]-means,sd,out=np.zeros_like(xn[:,3:]),where=sd>1e-12)
   xc=np.column_stack((np.ones(len(xn)),xn));xf=np.column_stack((xc,vs));y=D['event_q']
   bc,dc=logistic(xc[train],y[train],w);bf,df=logistic(xf[train],y[train],w)
   for arm,d in [('C',dc),('FULL',df)]:
    if not d['converged']:failures.append({'family':family,'leaf':int(leaf),'arm':arm,**d})
   gamma=float(bf[-1]);active+=1;negative+=gamma< -1e-8
   pc=old.expit(xc[test]@bc);pf=old.expit(xf[test]@bf)
   preds={'C':pc,'FULL':pf,'ID':pf if gamma>0 else pc,'INV':pf if gamma<0 else pc}
   for arm,prob in preds.items():
    prob=np.clip(prob,1e-9,1-1e-9);ll=-(y[test]*np.log2(prob)+(1-y[test])*np.log2(1-prob));loss[arm][family].append(float(ll.mean()))
   if details:folds.append({'family_index':family,'held_leaf':int(leaf),'train_event_indices':train.tolist(),'train_weights':w.tolist(),'test_event_indices':test.tolist(),'continuous_mean':means.tolist(),'continuous_sd':sd.tolist(),'C_coefficients':bc.tolist(),'FULL_coefficients':bf.tolist(),'gamma':gamma,'C_fit':dc,'FULL_fit':df,'predictions':{a:v.tolist() for a,v in preds.items()},'observed_q':y[test].tolist(),'base_visual_score':vs[test].tolist(),'loss_bits':{a:loss[a][family][-1] for a in loss},'ID_uses':'FULL' if gamma>0 else 'C','INV_uses':'FULL' if gamma<0 else 'C'})
 fl={a:np.array([np.mean(v) if v else np.nan for v in fam]) for a,fam in loss.items()}
 if any(not np.isfinite(v).all() for v in fl.values()):raise ValueError('missing family scoring capacity')
 gc=fl['C']-fl['INV'];gi=fl['ID']-fl['INV'];T=float(min(gc.mean(),gi.mean()))
 candidates=[{'family_index':i,'family':D['families'][i],'active_leaves':len(loss['C'][i]),'loss_bits':{a:float(v[i]) for a,v in fl.items()},'INV_gain_C':float(gc[i]),'INV_gain_ID':float(gi[i]),'both_positive':bool(gc[i]>0 and gi[i]>0)} for i in range(nf)]
 return {'T':T,'mean_INV_gain_C':float(gc.mean()),'mean_INV_gain_ID':float(gi.mean()),'positive_families':int(((gc>0)&(gi>0)).sum()),'negative_gamma_folds':negative,'active_folds':active,'negative_fraction':negative/active,'pre_null_gates':bool(T>=.01 and ((gc>0)&(gi>0)).sum()>=8 and negative/active>=.8),'fit_failures':failures,'candidates':candidates,'folds':folds,'empty_folds':empty_folds,'base_folds':base_details}

def init(data):
 global D
 D=data
def null_job(job):
 rep,mapping=job;raw=D['raw'][mapping];out=pipeline(raw)
 out.pop('folds');out.pop('base_folds');out.update(replicate=rep,page_donor_indices=mapping,raw_world_hash=digest(raw.tolist()),observable_world_hash=digest(old.consensus(raw).tolist()))
 return out
def load_input():
 x=json.loads((E/'src/INPUT.json').read_text())
 if x.get('presence_mismatches'):raise ValueError('source presence mismatch')
 pages=x['pages'];events=x['q_events'];index={p:i for i,p in enumerate(pages)}
 lids=np.array(x['leaf_ids'],int)
 return {'pages':pages,'leaf_ids':lids,'leaves':sorted(set(lids.tolist())),'metadata':x['metadata'],'families':x['pairs'],'base':np.array(x['base_presence'],int),'raw':np.array(x['codes_A_B']),'event_family':np.array([v['family'] for v in events],int),'event_leaf':np.array([v['leaf'] for v in events],int),'event_page':np.array([index[v['page']] for v in events],int),'event_q':np.array([v['q'] for v in events],int),'nuisance':np.array([[v['prev_formal_DY'],v['prev_DY_unknown'],v['line_start'],v['relativepos'],math.log1p(v['page_n_groups'])] for v in events],float),'event_source_ids':[v['sourceid'] for v in events]}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--workers',type=int,default=32);args=parser.parse_args()
 lock=json.loads((E/'PREREG_LOCK.json').read_text())
 for path,h in lock['files'].items():
  if hashlib.sha256((R/path).read_bytes()).hexdigest()!=h:raise ValueError('registration hash mismatch '+path)
 data=load_input();init(data)
 groups=collections.defaultdict(list)
 for leaf in D['leaves']:
  idx=sorted(np.flatnonzero(D['leaf_ids']==leaf).tolist(),key=lambda i:D['pages'][i][-1])
  sig=tuple((D['pages'][i][-1],D['metadata'][D['pages'][i]]['hand'],D['metadata'][D['pages'][i]]['currier']) for i in idx)
  groups[sig].append((int(leaf),idx))
 mobile=0;orbit=1;blocks=[];mask=old.consensus(D['raw'])
 for sig,block in sorted(groups.items()):
  counts=collections.Counter(digest(mask[idx].tolist()) for _,idx in block)
  part=math.factorial(len(block))//math.prod(math.factorial(c) for c in counts.values());orbit*=part
  mobile+=len(block) if len(counts)>1 else 0
  blocks.append({'signature':sig,'leaves':[leaf for leaf,_ in sorted(block)],'observable_orbit':part})
 capacity={'mobile_leaves':mobile,'observable_orbit':orbit,'blocks':blocks,'pass':mobile>=12 and orbit>=100}
 save('CAPACITY.json',capacity)
 if not capacity['pass']:
  save('RESULT.json',{'status':'CAPACITY_FAIL','capacity':capacity,'confirmed_words':0});return
 observed=pipeline(D['raw'],True)
 save('OBSERVED_FOLDS.json.gz',observed['folds']);save('BASE_FOLDS.json.gz',observed['base_folds']);save('EMPTY_FOLDS.json',observed['empty_folds'])
 rng=random.Random(1165);jobs=[]
 for rep in range(1,200):
  mapping=list(range(len(D['pages'])))
  for sig,block in sorted(groups.items()):
   block=sorted(block);donors=block.copy();rng.shuffle(donors)
   for (_,target),(_,donor) in zip(block,donors):
    for a,b in zip(target,donor):mapping[a]=b
  jobs.append((rep,mapping))
 with ProcessPoolExecutor(max_workers=min(max(1,args.workers),32,os.cpu_count() or 1),initializer=init,initargs=(data,)) as pool:nulls=list(pool.map(null_job,jobs))
 save('NULL_RESULTS.json.gz',nulls)
 rank=(1+sum(n['T']>=observed['T']-1e-12 for n in nulls))/200
 result={k:v for k,v in observed.items() if k not in ['folds','base_folds']}
 result.update(null_rank=rank,null_draws=199,capacity=capacity,unique_raw_worlds=len({n['raw_world_hash'] for n in nulls}),unique_observable_worlds=len({n['observable_world_hash'] for n in nulls}),all_fits_converged=not observed['fit_failures'] and not any(n['fit_failures'] for n in nulls),confirmed_words=0,independent_confirmation=False)
 result['status']='NUMERICAL_FIT_FAIL' if not result['all_fits_converged'] else ('IMAGE_LINKED_INVERSE_COMBINATION_TRANSFER' if result['pre_null_gates'] and rank<=.05 else 'NO_SUPPORTED_INVERSE_COMBINATION_TRANSFER')
 save('CANDIDATES.json',observed['candidates']);save('RESULT.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
