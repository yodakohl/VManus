"""Frozen joint-state visual-word prediction; no word meanings."""
import collections,csv,gzip,hashlib,itertools,json,math,os,random
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np
def expit(x): return np.exp(-np.logaddexp(0.,-x))
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
FEATURES=['HORIZONTAL_BEADS','BASAL_SWOLLEN_BRANCHES','RADIATE_HEAD','SPINY_ROUND_HEAD','BROAD_PETAL_FLOWER','MULTI_UNIT_SPIKE']
BETAS=np.array([-4,-2,-1,-.5,-.25,0,.25,.5,1,2,4],float)
BETA_PREF=sorted(range(11),key=lambda i:(BETAS[i]!=0,abs(BETAS[i]),BETAS[i]))
STATES=np.array(list(itertools.product([0,1],repeat=6)),float)
COUNTS=STATES.sum(axis=1).astype(int);COUNT_ONEHOT=np.eye(7)[COUNTS]
PAYLOAD=None

def dump(n,x):
 data=(json.dumps(x,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
 if n in ['NULL_RESULTS.json','OBSERVED_FOLDS.json']:
  (A/(n+'.gz')).write_bytes(gzip.compress(data,mtime=0))
 else:(A/n).write_bytes(data)
def table(p):
 with p.open() as f:return list(csv.DictReader(f,delimiter='\t'))
def digest(x):return hashlib.sha256(json.dumps(x,separators=(',',':')).encode()).hexdigest()
def mean(x):return float(np.mean(x))
def consensus(raw):
 return np.where((raw[:,:,0]==raw[:,:,1])&(raw[:,:,0]!='UNKNOWN'),np.where(raw[:,:,0]=='YES',1,0),-1).astype(int)
def choose_beta(objective):
 best=objective.max(axis=0);ix=np.zeros(len(best),int);unassigned=np.ones(len(best),bool)
 for k in BETA_PREF:
  take=unassigned&(objective[k]>=best-1e-12);ix[take]=k;unassigned[take]=False
 assert not unassigned.any()
 return ix,objective[ix,np.arange(len(best))]

def arm(p,distribution,z,y,train,enable=True):
 """11 beta x words x pages, integrating the exact latent marginal."""
 nw=len(p);npages=len(y);ntrain=len(train);offset=np.log(p)-np.log1p(-p)
 logits=offset[None,:,None]+BETAS[:,None,None]*z[None,None,:]
 yes=np.einsum('bws,ps->bwp',expit(logits),distribution,optimize=False)
 no=np.einsum('bws,ps->bwp',expit(-logits),distribution,optimize=False)
 yes[5]=p[:,None];no[5]=1-p[:,None]
 with np.errstate(divide='ignore'):
  ll=np.where(y[train].T[None,:,:]>0,np.log(yes[:,:,train]),np.log(no[:,:,train])).sum(axis=2)-BETAS[:,None]**2/2
 if not enable:ll[np.arange(11)!=5]=-np.inf
 bi,objective=choose_beta(ll);idx=np.arange(nw)
 return bi,objective,yes[bi,idx,:],no[bi,idx,:]

def pipeline(raw,details=False):
 D=PAYLOAD;pages=D['pages'];leaves=D['leaves'];leaf_ids=D['leaf_ids'];y=D['y'];nw=y.shape[1];n=len(pages)
 mask=consensus(raw);full=(mask>=0).all(axis=1);compat=((mask[:,None,:]<0)|(mask[:,None,:]==STATES[None,:,:])).all(axis=2)
 yf=np.array([y[leaf_ids==leaf].max(axis=0) for leaf in leaves]);yes_leaf=np.array([(mask[leaf_ids==leaf]==1).any(axis=0) for leaf in leaves]);no_leaf=np.array([(mask[leaf_ids==leaf]==0).any(axis=0) for leaf in leaves]);positive_unique=np.zeros((nw,6),int);gainbg=[];gaincount=[];folds=[]
 for fi,leaf in enumerate(leaves):
  train=np.where(leaf_ids!=leaf)[0];test=np.where(leaf_ids==leaf)[0];counts=y[train].sum(axis=0);g=(counts+.5)/(len(train)+1);p=(counts+10*g)/(len(train)+10)
  assert np.all((p>0)&(p<1));wordcap=(yf.sum(axis=0)-yf[fi])>=2
  fyes=yes_leaf.sum(axis=0)-yes_leaf[fi];fno=no_leaf.sum(axis=0)-no_leaf[fi];eligible=(fyes>=2)&(fno>=2)
  prior=np.full(64,1/64)
  for i in train:
   if full[i]:prior[np.where((STATES==mask[i]).all(axis=1))[0][0]]+=1
  posterior=compat*prior;posterior/=posterior.sum(axis=1,keepdims=True)
  featureprob=posterior@STATES;countprob=posterior@COUNT_ONEHOT
  em=np.r_[featureprob[train].mean(axis=0),np.mean(countprob[train]@np.arange(7))]
  ev=np.r_[featureprob[train].mean(axis=0),np.mean(countprob[train]@(np.arange(7)**2))]-em**2
  bgll=(y[train]*np.log(p)+(1-y[train])*np.log1p(-p)).sum(axis=0)
  scores=np.full((7,nw),-np.inf);scores[6]=bgll
  chosenbeta=np.zeros((6,nw));yesmodels=np.broadcast_to(p[None,:,None],(7,nw,n)).copy();nomodels=1-yesmodels
  featurefits=[]
  for j in range(6):
   if not eligible[j]:
    if details:featurefits.append({'feature':FEATURES[j],'eligible':False})
    continue
   z=(np.array([0.,1.])-em[j])/math.sqrt(ev[j]) if ev[j]>1e-12 else np.array([0.,0.])
   distribution=np.column_stack((1-featureprob[:,j],featureprob[:,j]))
   bi,obj,yp,npred=arm(p,distribution,z,y,train,ev[j]>1e-12)
   scores[j]=np.where(wordcap,obj,-np.inf);chosenbeta[j]=BETAS[bi];yesmodels[j]=yp;nomodels[j]=npred
   if details:featurefits.append({'feature':FEATURES[j],'eligible':True,'beta':BETAS[bi].tolist(),'objective':obj.tolist()})
  best=scores.max(axis=0);ties=scores>=best[None,:]-1e-12
  assert ties.any(axis=0).all()
  visualyes=np.sum(yesmodels*ties[:,:,None],axis=0)/ties.sum(axis=0)[:,None]
  visualno=np.sum(nomodels*ties[:,:,None],axis=0)/ties.sum(axis=0)[:,None]
  z=(np.arange(7)-em[6])/math.sqrt(ev[6]) if ev[6]>1e-12 else np.zeros(7)
  cbi,cobj,cyes,cno=arm(p,countprob,z,y,train,ev[6]>1e-12)
  cbi=np.where(wordcap,cbi,5);cyes=np.where(wordcap[:,None],cyes,p[:,None]);cno=np.where(wordcap[:,None],cno,1-p[:,None]);cobj=np.where(wordcap,cobj,bgll)
  unique=ties.sum(axis=0)==1
  for j in range(6):positive_unique[:,j]+=unique&ties[j]&(chosenbeta[j]>0)&wordcap
  observedvisual=np.where(y[test].T,visualyes[:,test],visualno[:,test]);observedbg=np.where(y[test].T,p[:,None],1-p[:,None]);observedcount=np.where(y[test].T,cyes[:,test],cno[:,test])
  gb=np.log2(observedvisual/observedbg).mean(axis=1);gc=np.log2(observedvisual/observedcount).mean(axis=1);gainbg.append(gb);gaincount.append(gc)
  if details:
   labels=FEATURES+['BACKGROUND'];folds.append({'held_leaf':int(leaf),'train_pages':[pages[i] for i in train],'test_pages':[pages[i] for i in test],'train_word_counts':counts.astype(int).tolist(),'train_positive_leaf_counts':(yf.sum(axis=0)-yf[fi]).astype(int).tolist(),'baseline_global':g.tolist(),'baseline_stratum':p.tolist(),'word_capacity':wordcap.tolist(),'feature_definite_yes_leaves':fyes.tolist(),'feature_definite_no_leaves':fno.tolist(),'feature_eligible':eligible.tolist(),'joint_state_prior_mass':prior.tolist(),'conditional_state_probabilities':posterior.tolist(),'training_means':em.tolist(),'training_variances':ev.tolist(),'feature_fits':featurefits,'background_objective':bgll.tolist(),'selected_models':[[labels[j] for j in range(7) if ties[j,w]] for w in range(nw)],'selected_positive_unique_feature':[FEATURES[int(np.where(ties[:,w])[0][0])] if unique[w] and not ties[6,w] and chosenbeta[int(np.where(ties[:,w])[0][0]),w]>0 else None for w in range(nw)],'count_beta':BETAS[cbi].tolist(),'count_objective':cobj.tolist(),'predictions':{'visual_p_yes':visualyes[:,test].T.tolist(),'count_p_yes':cyes[:,test].T.tolist(),'background_p_yes':np.broadcast_to(p,(len(test),nw)).tolist()},'gain_over_background':gb.tolist(),'gain_over_count':gc.tolist()})
 gb=np.mean(gainbg,axis=0);gc=np.mean(gaincount,axis=0);joint=np.array([[sum(bool(np.any((y[leaf_ids==leaf,w]>0)&(mask[leaf_ids==leaf,j]==1))) for leaf in leaves) for j in range(6)] for w in range(nw)])
 featurepasses=(positive_unique/len(leaves)>=.8)&(joint>=3);passed=(gb>=.01)&(gc>=.01)&featurepasses.any(axis=1);t=np.minimum(gb,gc);rows=[]
 for w,word in enumerate(D['words']):
  gate=[]
  if gb[w]<.01:gate.append('BACKGROUND_GAIN_BELOW_0_01')
  if gc[w]<.01:gate.append('COUNT_GAIN_BELOW_0_01')
  if not np.any(positive_unique[w]/len(leaves)>=.8):gate.append('NO_FEATURE_80_PERCENT_UNIQUE_POSITIVE_FOLDS')
  if not featurepasses[w].any():gate.append('NO_SAME_FEATURE_STABILITY_AND_THREE_JOINT_YES_LEAVES')
  rows.append({'word':word,'gain_over_background':float(gb[w]),'gain_over_count':float(gc[w]),'positive_unique_fold_counts':positive_unique[w].tolist(),'joint_word_definite_yes_leaves':joint[w].tolist(),'qualifying_features':[FEATURES[j] for j in range(6) if featurepasses[w,j]],'gates_pass':bool(passed[w]),'T':float(t[w]) if passed[w] else None,'failure_reasons':gate})
 return {'candidates':rows,'maximum':float(t[passed].max()) if passed.any() else 0.,'folds':folds}

def init(d):
 global PAYLOAD
 PAYLOAD=d

def null_job(job):
 rep,mapping=job;raw=PAYLOAD['raw'][mapping];x=pipeline(raw);return {'replicate':rep,'maximum':x['maximum'],'candidates':x['candidates'],'raw_world_hash':digest(raw.tolist()),'observable_world_hash':digest(consensus(raw).tolist()),'page_donor_indices':mapping}

def main():
 pins=json.loads((E/'PREREG_LOCK.json').read_text())['files']
 for p,h in pins.items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 src=json.loads((E/'src/SOURCE.json').read_text());meta=json.loads((E/'src/METADATA.json').read_text());pages=sorted(r['folio'] for r in table(R/src['image_roster']));assert len(pages)==38 and len(set(pages))==38
 allow=set(json.loads((R/'experiments/yolo/gdt915_terminal_lr_phrase_transfer/src/SPEC.json').read_text())['allowed_selectors']);assert set(pages)<=allow and not any(p.startswith('f84') or p=='f116v' for p in pages)
 readers=[{r['folio']:r for r in table(R/p)} for p in src['observer_codes']];assert all(set(x)==set(pages) for x in readers)
 raw=np.array([[[x[p][f] for x in readers] for f in FEATURES] for p in pages]);assert set(raw.ravel())<={'YES','NO','UNKNOWN'}
 wordsrows=sorted(table(R/src['word_presence']['file']),key=lambda x:x['word']);words=[r['word'] for r in wordsrows];assert len(words)==169 and len(set(words))==169
 presences=[set(r['image_folio_ids'].split(';')) for r in wordsrows];assert all(s<=set(pages) for s in presences);y=np.array([[int(p in s) for s in presences] for p in pages],int)
 leaf_ids=np.array([int(p[1:-1]) for p in pages]);leaves=sorted(set(leaf_ids.tolist()));assert len({(meta[p]['hand'],meta[p]['currier']) for p in pages})==1,'Frozen metadata homogeneity changed'
 d={'pages':pages,'words':words,'raw':raw,'y':y,'leaf_ids':leaf_ids,'leaves':leaves};init(d)
 groups=collections.defaultdict(list)
 for leaf in leaves:
  pp=sorted([p for p,l in zip(pages,leaf_ids) if l==leaf],key=lambda p:p[-1]);sig=tuple((p[-1],meta[p]['hand'],meta[p]['currier']) for p in pp);groups[sig].append(leaf)
 index={p:i for i,p in enumerate(pages)};blocks=[];orbit=1;mobile=0;mask=consensus(raw)
 for sig,ls in sorted(groups.items()):
  positions={leaf:[index[f'f{leaf}{face}'] for face,hand,currier in sig] for leaf in sorted(ls)};bundle=[json.dumps(mask[positions[leaf]].tolist()) for leaf in sorted(ls)];counts=collections.Counter(bundle);blockorbit=math.factorial(len(ls))//math.prod(math.factorial(c) for c in counts.values());orbit*=blockorbit;blockmobile=len(ls) if len(counts)>1 else 0;mobile+=blockmobile
  blocks.append({'signature':sig,'leaves':sorted(ls),'positions':positions,'observable_bundle_multiplicities':dict(counts),'observable_orbit':blockorbit,'mobile_leaves':blockmobile})
 capacity=mobile>=12 and orbit>=100
 cap={'leaf_count':len(leaves),'mobile_leaves':mobile,'observable_orbit':orbit,'capacity':capacity,'blocks':blocks}
 dump('CAPACITY.json',cap)
 inp={'pages':pages,'words':words,'features':FEATURES,'beta_grid':BETAS.tolist(),'metadata':meta,'leaf_ids':leaf_ids.tolist(),'codes_A_B':raw.tolist(),'consensus':mask.tolist(),'word_presence':y.tolist(),'representation':'ZL3b'};dump('INPUT.json',inp)
 observed=pipeline(raw,True);dump('OBSERVED_FOLDS.json',observed['folds'])
 rng=random.Random(1157);jobs=[]
 for rep in range(1,200):
  mapping=list(range(len(pages)))
  for block in blocks:
   ls=block['leaves'];donors=list(ls);rng.shuffle(donors)
   for target,donor in zip(ls,donors):
    for a,b in zip(block['positions'][target],block['positions'][donor]):mapping[a]=b
  jobs.append((rep,mapping))
 with ProcessPoolExecutor(max_workers=min(16,os.cpu_count() or 1),initializer=init,initargs=(d,)) as pool:nulls=list(pool.map(null_job,jobs))
 dump('NULL_RESULTS.json',nulls)
 for row in observed['candidates']:
  rank=(1+sum(n['maximum']>=row['T']-1e-12 for n in nulls))/200 if row['T'] is not None else None
  row['search_reference_rank']=rank;row['nominated']=bool(capacity and row['gates_pass'] and rank<=.05)
 dump('CANDIDATES.json',observed['candidates'])
 aliases=[{'features':[FEATURES[i],FEATURES[j]],'relationship':'IDENTICAL_CONSENSUS_TERNARY_MASKS'} for i,j in itertools.combinations(range(6),2) if np.array_equal(mask[:,i],mask[:,j])]
 dump('ALIASES.json',{'exact_observed_mask_aliases':aliases,'fold_aliases_location':'OBSERVED_FOLDS.json.gz selected_models preserves every objective tie','semantic_unidentifiability':'Distinct predictor preference does not identify an authorial word owner or meaning; correlated visual properties and generic content remain unmeasured alternatives.'})
 nominees=[r for r in observed['candidates'] if r['nominated']];result={'status':'NO_CAPACITY' if not capacity else 'FEATURE_COMPATIBLE_WORD_LEADS' if nominees else 'NO_SUPPORTED_VISUAL_WORD_LEAD','capacity':capacity,'pages':len(pages),'leaves':len(leaves),'words':len(words),'features':FEATURES,'mobile_leaves':mobile,'observable_orbit':orbit,'observed_gate_pass_words':[r['word'] for r in observed['candidates'] if r['gates_pass']],'nominees':nominees,'null_draws':199,'null_positive_maxima':sum(n['maximum']>0 for n in nulls),'unique_raw_worlds':len({n['raw_world_hash'] for n in nulls}),'unique_observable_worlds':len({n['observable_world_hash'] for n in nulls}),'meanings':0,'authorial_owner_claim':False,'project_wide_significance_claim':False,'independent_confirmation':False,'pins_verified':True}
 dump('RESULT.json',result)
 text=['# GDT1157 all169 fixed whole-word candidates','','Columns preserve failures; no word meanings assigned. Full fold and null data are linked in artifacts.','','|Whole form|Gain vs background|Gain vs COUNT|Maximum positive unique folds|Joint-feature gate|T|Search rank|Nominated|','|---|---:|---:|---:|---|---:|---:|---|']
 for r in observed['candidates']:text.append('|'+ '|'.join([r['word'].replace('|','&#124;'),f"{r['gain_over_background']:.9f}",f"{r['gain_over_count']:.9f}",str(max(r['positive_unique_fold_counts']))+'/ '+str(len(leaves)),','.join(r['qualifying_features']) or 'NONE',str(r['T']),str(r['search_reference_rank']),str(r['nominated'])])+'|')
 (E/'CANDIDATE_TABLE.md').write_text('\n'.join(text)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
