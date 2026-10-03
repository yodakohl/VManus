#!/usr/bin/env python3
"""Independent GDT1165 bookkeeping, predictions and convex-fit audit.
No experimental runner imports; only the explicitly frozen legacy DY parser.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import argparse,collections,csv,gzip,hashlib,importlib.util,io,itertools,json,math,random,re,subprocess
from pathlib import Path
import numpy as np
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
CHECKS={};DETAIL={};FAIL=[]
def load(p):
 p=Path(p);return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(name,value):
 CHECKS[name]=bool(value)
 if not value:FAIL.append(name)
def near(a,b,tol=2e-10):return np.asarray(a).shape==np.asarray(b).shape and np.allclose(a,b,rtol=tol,atol=tol,equal_nan=False)
def sigmoid(z):return np.exp(-np.logaddexp(0.,-z))
def logit(p):
 p=np.clip(p,1e-9,1-1e-9);return np.log(p)-np.log1p(-p)
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def consensus(raw):return np.where((raw[:,:,0]==raw[:,:,1])&(raw[:,:,0]!='UNKNOWN'),(raw[:,:,0]=='YES').astype(int),-1)
def source_audit(x):
 s=load(A/'SOURCE_RECEIPT.json');old=load(R/'experiments/yolo/gdt1157_cross_situational_visual_words/artifacts/INPUT.json')
 check('bound_source_bytes',all(sha(R/p)==h for p,h in s['bindings'].items()))
 check('preparation_and_input_bytes',sha(E/'src/prepare.py')==s['prepare_sha256'] and sha(E/'src/INPUT.json')==s['input_sha256'])
 check('inherited_visual_packet',all(x[k]==old[k] for k in ['pages','leaf_ids','metadata','features','codes_A_B','consensus','representation']))
 pages=x['pages'];leaf=np.array(x['leaf_ids']);presence=np.array(old['word_presence']);pairs=[]
 for word in old['words']:
  if 'q'+word not in old['words']:continue
  good=True
  for w in [word,'q'+word]:
   v=presence[:,old['words'].index(w)];yes=sum(bool(v[leaf==l].any()) for l in set(leaf));good &= yes>=4 and len(set(leaf))-yes>=4
  if good:pairs.append({'base':word,'prefixed':'q'+word})
 check('literal_pair_capacity_without_selection',pairs==x['pairs'] and len(pairs)>=6)
 check('whole_scope',len(pages)==38 and len(set(leaf))==32 and all(not p.startswith('f84') and p!='f116v' for p in pages) and all(x['metadata'][p]=={'section':'H','hand':'1','currier':'A'} for p in pages))
 rows=[]
 for n,g in enumerate(s['guards']):
  cmd=g['command'];check('guard_command_'+str(n),cmd[:2]==['./vmanus-exp','query-tsv'] and cmd[3:5]==['--selector','page'] and cmd[5]=='--columns' and cmd[7:]==sum((['--allow',p] for p in pages),[]))
  out=subprocess.run(cmd,cwd=R,capture_output=True,check=True).stdout
  archived=gzip.decompress((E/g['projection']).read_bytes())
  check('selector_projection_exact_'+str(n),out==archived and sha(E/g['projection'])==g['projection_sha256'])
  rr=list(csv.DictReader(io.StringIO(out.decode()),delimiter='\t'));check('projection_scope_'+str(n),len(rr)==g['selected_rows'] and all(v['page'] in pages for v in rr));rows.append(rr)
 z=[v for v in rows[0] if v['edition']=='ZL3b'];groups={(v['locus'],int(v['source_group_index'])):v for v in z};legacy=collections.defaultdict(list)
 for v in rows[1]:legacy[(v['locus'],int(v['group_index']))].append(v)
 spec=importlib.util.spec_from_file_location('frozen_dy',R/'run_gdt012_core_semantic_atlas.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 comparisons=0;bad=0
 for v in z:
  raw=v['ivtff_group_raw']
  if not re.fullmatch('[a-z]+',raw):continue
  h=hashlib.sha256(raw.encode()).hexdigest()
  for d in legacy[(v['locus'],int(v['source_group_index']))]:
   if d['source_surface_sha256']==h:comparisons+=1;bad+=int(d['dy_closure'])!=m.strip_layers(raw)[2]
 check('frozen_pure_DY_legacy_agreement',bad==0 and comparisons==s['pure_vs_legacy_comparisons'])
 count=collections.Counter(v['page'] for v in z);pmap=dict(zip(pages,leaf.tolist()));lookup={w:(i,q) for i,p in enumerate(pairs) for q,w in enumerate([p['base'],p['prefixed']])};events=[];excluded=[]
 for v in z:
  raw=v['ivtff_group_raw']
  if raw not in lookup:continue
  if v['kind']!='P' or v['left_separator'] not in ['LINE_START','DEFINITE_SPACE','DRAWING_INTERRUPTION'] or v['right_separator'] not in ['DEFINITE_SPACE','LINE_END','DRAWING_INTERRUPTION']:excluded.append(v);continue
  i=int(v['source_group_index']);n=int(v['source_group_count']);prev=groups.get((v['locus'],i-1));pr=prev['ivtff_group_raw'] if prev else None;known=i==1 or (pr is not None and re.fullmatch('[a-z]+',pr) is not None)
  matches=[] if prev is None else [d for d in legacy[(v['locus'],i-1)] if d['source_surface_sha256']==hashlib.sha256(pr.encode()).hexdigest()]
  f,q=lookup[raw];events.append(dict(family=f,base=pairs[f]['base'],sourceid=f"ZL3b|{v['locus']}|{i}",page=v['page'],leaf=pmap[v['page']],locus=v['locus'],index=i,count=n,raw=raw,q=q,prev_formal_DY=0 if i==1 or not known else m.strip_layers(pr)[2],prev_DY_unknown=int(not known),line_start=int(i==1),relativepos=(i-1)/max(n-1,1),page_n_groups=count[v['page']],previous_raw=pr,previous_match_rows=len(matches)))
 check('every_event_all_fields_and_exclusions',events==x['q_events'] and excluded==x['scope_exclusions'] and len(groups)==len(z))
 hits={(v['page'],v['raw']) for v in events};mismatches=[(p,w) for j,p in enumerate(pages) for w in lookup if int((p,w) in hits)!=old['word_presence'][j][old['words'].index(w)]]
 check('all_912_presence_cells',not mismatches and len(pages)*len(lookup)==912)
 expected=[[row[old['words'].index(p['base'])] for p in pairs] for row in old['word_presence']]
 check('base_only_columns_and_full_group_counts',x['base_presence']==expected and x['page_n_groups']==[count[p] for p in pages])
 initial=load(A/'SOURCE_RECEIPT_initial.json');check('initial_failed_preparation_preserved',sha(E/'src/INPUT_initial.json')==initial['input_sha256'] and len(initial['presence_mismatches'])==9 and sha(E/'src/prepare_initial.py')==initial['prepare_sha256'] and all(sha(E/g['projection'].replace('.tsv.gz','_initial.tsv.gz'))==g['projection_sha256'] for g in initial['guards']))
 DETAIL['source']={'pages':len(pages),'leaves':len(set(leaf)),'families':len(pairs),'events':len(events),'scope_exclusions':len(excluded),'presence_cells':len(pages)*len(lookup),'DY_unknown':sum(v['prev_DY_unknown'] for v in events),'legacy_flag_comparisons':comparisons}
 return old
STATES=np.array(list(itertools.product([0,1],repeat=6)));BETAS=np.array([-4,-2,-1,-.5,-.25,0,.25,.5,1,2,4]);PREF=sorted(range(11),key=lambda k:(BETAS[k]!=0,abs(BETAS[k]),BETAS[k]))
def base(raw,held,x):
 y=np.array(x['base_presence']);leaf=np.array(x['leaf_ids']);tr=np.flatnonzero(leaf!=held);mask=consensus(raw);nw=y.shape[1];npages=len(y)
 counts=y[tr].sum(0);p=(counts+10*(counts+.5)/(len(tr)+1))/(len(tr)+10)
 wc=np.array([y[leaf==l].max(0) for l in sorted(set(leaf)) if l!=held]).sum(0)>=2
 fc=(np.array([(mask[leaf==l]==1).any(0) for l in sorted(set(leaf)) if l!=held]).sum(0)>=2)&(np.array([(mask[leaf==l]==0).any(0) for l in sorted(set(leaf)) if l!=held]).sum(0)>=2)
 prior=np.ones(64)/64
 for j in tr:
  if (mask[j]>=0).all():prior[np.flatnonzero((STATES==mask[j]).all(1))[0]]+=1
 post=((mask[:,None,:]<0)|(mask[:,None,:]==STATES[None,:,:])).all(2)*prior;post/=post.sum(1)[:,None]
 fp=post@STATES;mu=fp[tr].mean(0);var=mu-mu*mu;scores=np.full((7,nw),-np.inf);scores[6]=(y[tr]*np.log(p)+(1-y[tr])*np.log1p(-p)).sum(0);pred=np.broadcast_to(p[None,:,None],(7,nw,npages)).copy();chosen=np.zeros((6,nw))
 for j in range(6):
  if not fc[j]:continue
  z=(np.array([0,1])-mu[j])/np.sqrt(var[j]) if var[j]>1e-12 else np.zeros(2)
  yes=np.empty((11,nw,npages));no=np.empty_like(yes)
  for k,b in enumerate(BETAS):
   pp=sigmoid(logit(p)[:,None]+b*z[None,:]);yes[k]=pp[:,0,None]*(1-fp[:,j])[None,:]+pp[:,1,None]*fp[:,j][None,:];no[k]=(1-pp[:,0,None])*(1-fp[:,j])[None,:]+(1-pp[:,1,None])*fp[:,j][None,:]
  yes[5]=p[:,None];no[5]=1-p[:,None]
  obj=np.where(y[tr].T[None,:,:],np.log(yes[:,:,tr]),np.log(no[:,:,tr])).sum(2)-BETAS[:,None]**2/2
  if var[j]<=1e-12:obj[np.arange(11)!=5]=-np.inf
  for w in range(nw):
   k=next(k for k in PREF if obj[k,w]>=obj[:,w].max()-1e-12);chosen[j,w]=BETAS[k];scores[j,w]=obj[k,w] if wc[w] else -np.inf;pred[j,w]=yes[k,w]
 ties=scores>=scores.max(0)[None,:]-1e-12;v=(pred*ties[:,:,None]).sum(0)/ties.sum(0)[:,None];r=logit(v)-logit(p)[:,None];mean=r[:,tr].mean(1);sd=r[:,tr].std(1);s=np.divide(r-mean[:,None],sd[:,None],out=np.zeros_like(r),where=sd[:,None]>1e-12)
 detail=dict(held_leaf=int(held),background=p.tolist(),visual_probability_all_pages=v.tolist(),score_mean=mean.tolist(),score_sd=sd.tolist(),selected_models=[[j for j in range(7) if ties[j,w]] for w in range(nw)],feature_betas=chosen.tolist(),joint_state_prior=prior.tolist(),word_capacity=wc.tolist(),feature_capacity=fc.tolist())
 return s,p,detail

def weights(indices,f,l):
 counts=collections.Counter((int(f[i]),int(l[i])) for i in indices);families=set(f[indices]);leaves={a:{b for aa,b in counts if aa==a} for a in families}
 return np.array([1/(len(families)*len(leaves[int(f[i])])*counts[int(f[i]),int(l[i])]) for i in indices])
def objective(b,X,y,w):
 z=X@b;pen=.05*np.r_[0.,np.ones(len(b)-1)];val=w@(np.logaddexp(0,z)-y*z)+.5*np.dot(pen*b,b);g=X.T@(w*(sigmoid(z)-y))+pen*b;return float(val),g

def arithmetic(summary):
 cs=summary['candidates'];gc=np.array([r['loss_bits']['C']-r['loss_bits']['INV'] for r in cs]);gi=np.array([r['loss_bits']['ID']-r['loss_bits']['INV'] for r in cs]);T=min(gc.mean(),gi.mean());pos=int(((gc>0)&(gi>0)).sum());fraction=summary['negative_gamma_folds']/summary['active_folds']
 return len(cs)==12 and all(near([c['INV_gain_C'],c['INV_gain_ID']],[a,b]) and c['both_positive']==bool(a>0 and b>0) for c,a,b in zip(cs,gc,gi)) and near([summary['T'],summary['mean_INV_gain_C'],summary['mean_INV_gain_ID'],summary['negative_fraction']],[T,gc.mean(),gi.mean(),fraction]) and summary['positive_families']==pos and summary['pre_null_gates']==bool(T>=.01 and pos>=8 and fraction>=.8)

def outputs_audit(x,old):
 raw=np.array(x['codes_A_B']);lids=np.array(x['leaf_ids']);leaves=sorted(set(lids));B={l:base(raw,l,x) for l in leaves};bd=load(A/'BASE_FOLDS.json.gz');good=True;maxerr=0
 for d in bd:
  ref=B[d['held_leaf']][2]
  for k,v in ref.items():
   if k in ['selected_models','word_capacity','feature_capacity']:good &= v==d[k]
   else:good &= near(v,d[k]);maxerr=max(maxerr,float(np.max(np.abs(np.array(v)-np.array(d[k])))))
 check('every_base_fold_independent_equations',good and len(bd)==len(leaves));DETAIL['base_max_absolute_error']=maxerr
 oldfolds=load(R/'experiments/yolo/gdt1157_cross_situational_visual_words/artifacts/OBSERVED_FOLDS.json.gz');ix=[old['words'].index(v) for v in x['base_words']];good=True
 for d in oldfolds:
  test=[x['pages'].index(v) for v in d['test_pages']];good &= near(np.array(B[d['held_leaf']][2]['visual_probability_all_pages'])[:,test].T,np.array(d['predictions']['visual_p_yes'])[:,ix])
 check('unchanged_1157_base_column_numerical_equivalence',good)
 ev=x['q_events'];f=np.array([v['family'] for v in ev]);l=np.array([v['leaf'] for v in ev]);y=np.array([v['q'] for v in ev]);page=np.array([x['pages'].index(v['page']) for v in ev]);nuis=np.array([[v['prev_formal_DY'],v['prev_DY_unknown'],v['line_start'],v['relativepos'],math.log1p(v['page_n_groups'])] for v in ev]);folds=load(A/'OBSERVED_FOLDS.json.gz');expected={(int(a),int(b)) for a,b in zip(f,l)}
 check('active_fold_complete_unique',set((d['family_index'],d['held_leaf']) for d in folds)==expected and len(folds)==len(expected))
 empty=load(A/'EMPTY_FOLDS.json');check('all_empty_folds_retained',set((d['family_index'],d['held_leaf']) for d in empty)=={(a,int(b)) for a in range(12) for b in leaves}-expected)
 flags=collections.defaultdict(lambda:True);worstgrad=0.;worstprob=0.;scipy_checks=[];loss=collections.defaultdict(lambda:collections.defaultdict(list));ng=0
 try:from scipy.optimize import minimize
 except ImportError:minimize=None
 for j,d in enumerate(folds):
  a,b=d['family_index'],d['held_leaf'];tr=np.flatnonzero((f!=a)&(l!=b));te=np.flatnonzero((f==a)&(l==b));w=weights(tr,f,l);vs,p,_=B[b];n=np.column_stack((nuis,logit(p)[f]));mean=w@n[tr,3:];sd=np.sqrt(w@((n[tr,3:]-mean)**2));n[:,3:]=np.divide(n[:,3:]-mean,sd,out=np.zeros_like(n[:,3:]),where=sd>1e-12);C=np.column_stack((np.ones(len(y)),n));F=np.column_stack((C,vs[f,page]));bc=np.array(d['C_coefficients']);bf=np.array(d['FULL_coefficients']);gamma=bf[-1];ng+=gamma<-1e-8
  flags['two_axis_exclusion_and_weights'] &= d['train_event_indices']==tr.tolist() and d['test_event_indices']==te.tolist() and near(w,d['train_weights']) and len(set(f[tr]))==11 and near(w.sum(),1)
  flags['continuous_training_scales'] &= near(mean,d['continuous_mean']) and near(sd,d['continuous_sd']) and near(vs[f[te],page[te]],d['base_visual_score'])
  for arm,X,coef in [('C',C,bc),('FULL',F,bf)]:
   val,g=objective(coef,X[tr],y[tr],w);gn=float(abs(g).max());worstgrad=max(worstgrad,gn);flags['every_observed_fit_convex_optimality'] &= gn<=1e-9 and d[arm+'_fit']['converged']
   flags['observed_fit_diagnostics_honest'] &= d[arm+'_fit']['converged']==bool(gn<=1e-9) and near(val,d[arm+'_fit']['objective']) and abs(gn-d[arm+'_fit']['max_abs_gradient'])<1e-12
   if minimize and j in {0,len(folds)//2,len(folds)-1}:
    rr=minimize(lambda z:objective(z,X[tr],y[tr],w),np.zeros(X.shape[1]),jac=True,method='BFGS',options={'gtol':1e-10,'maxiter':1000});pv=sigmoid(X[te]@rr.x);err=float(abs(pv-sigmoid(X[te]@coef)).max());scipy_checks.append(dict(family=a,leaf=b,arm=arm,prediction_max_error=err,objective_difference=abs(rr.fun-val),optimizer_success=bool(rr.success),optimizer_message=str(rr.message),optimizer_gradient_max=float(abs(rr.jac).max())));flags['independent_scipy_optimizer_selected_fits'] &= err<2e-7 and abs(rr.fun-val)<1e-10
  pc=sigmoid(C[te]@bc);pf=sigmoid(F[te]@bf);preds=dict(C=pc,FULL=pf,ID=pf if gamma>0 else pc,INV=pf if gamma<0 else pc)
  flags['observed_labels_and_constrained_boundary'] &= d['observed_q']==y[te].tolist() and near(gamma,d['gamma']) and d['ID_uses']==('FULL' if gamma>0 else 'C') and d['INV_uses']==('FULL' if gamma<0 else 'C')
  for arm,prob in preds.items():
   worstprob=max(worstprob,float(abs(prob-np.array(d['predictions'][arm])).max()));flags['every_observed_prediction'] &= near(prob,d['predictions'][arm]);cl=np.clip(prob,1e-9,1-1e-9);ll=float(-(y[te]*np.log2(cl)+(1-y[te])*np.log2(1-cl)).mean());flags['every_observed_cell_loss'] &= near(ll,d['loss_bits'][arm]);loss[arm][a].append(ll)
 for name,v in flags.items():check(name,v)
 check('scipy_optimizer_available',minimize is not None);DETAIL.update(observed_folds=len(folds),worst_observed_gradient=worstgrad,worst_prediction_error=worstprob,scipy_selected_fits=scipy_checks)
 result=load(A/'RESULT.json');cand=load(A/'CANDIDATES.json');check('candidate_table_result_identity',cand==result['candidates'])
 observed_failures=[dict(family=d['family_index'],leaf=d['held_leaf'],arm=arm,**d[arm+'_fit']) for d in folds for arm in ['C','FULL'] if not d[arm+'_fit']['converged']]
 check('all_observed_failure_declarations_preserved',observed_failures==result['fit_failures'])
 table=list(csv.DictReader((A/'EVENT_PREDICTIONS.tsv').open(),delimiter='\t'));byid={r['sourceid']:r for r in table};good=len(table)==len(ev)==len(byid)
 for d in folds:
  for j,i in enumerate(d['test_event_indices']):
   e=ev[i];r=byid.get(e['sourceid'],{});good &= all(r.get(k)==str(e[k]) for k in ['sourceid','page','leaf','locus','index','raw','base','q']) and all(near(float(r['p_q_'+arm]),d['predictions'][arm][j]) for arm in ['C','ID','INV']) and near(float(r['gamma']),d['gamma']) and all(r[arm+'_converged']==str(d[arm+'_fit']['converged']) for arm in ['C','FULL'])
 check('all_217_exported_event_fields_probabilities_statuses',good)
 check('observed_family_equal_leaf_equal_aggregate',all(c['family']==x['pairs'][a] and c['active_leaves']==len(loss['C'][a]) and all(near(c['loss_bits'][arm],np.mean(loss[arm][a])) for arm in loss) for a,c in enumerate(cand)) and result['negative_gamma_folds']==ng and result['active_folds']==len(folds) and arithmetic(result))
 groups=collections.defaultdict(list)
 for leaf in leaves:
  pp=sorted(np.flatnonzero(lids==leaf).tolist(),key=lambda i:x['pages'][i][-1]);sig=tuple((x['pages'][i][-1],x['metadata'][x['pages'][i]]['hand'],x['metadata'][x['pages'][i]]['currier']) for i in pp);groups[sig].append((int(leaf),pp))
 orbit=1;mobile=0
 for sig,block in sorted(groups.items()):
  counts=collections.Counter(digest(consensus(raw)[p].tolist()) for _,p in block);orbit*=math.factorial(len(block))//math.prod(math.factorial(v) for v in counts.values());mobile+=len(block) if len(counts)>1 else 0
 cap=load(A/'CAPACITY.json');check('observable_mobility_and_orbit',cap['mobile_leaves']==mobile and cap['observable_orbit']==orbit and cap['pass']==(mobile>=12 and orbit>=100) and result['capacity']==cap)
 rng=random.Random(1165);nulls=load(A/'NULL_RESULTS.json.gz');good=len(nulls)==199
 for rep,d in enumerate(nulls,1):
  mapping=list(range(len(raw)))
  for sig,block in sorted(groups.items()):
   block=sorted(block);donors=block.copy();rng.shuffle(donors)
   for (_,target),(_,donor) in zip(block,donors):
    for i,j in zip(target,donor):mapping[i]=j
  world=raw[mapping];good &= d['replicate']==rep and mapping==d['page_donor_indices'] and d['raw_world_hash']==digest(world.tolist()) and d['observable_world_hash']==digest(consensus(world).tolist())
 check('all_199_joint_bundle_assignments_and_hashes',good)
 check('all_199_null_candidate_aggregate_arithmetic',all(arithmetic(d) and all(c['family']==x['pairs'][i] for i,c in enumerate(d['candidates'])) and sum(c['active_leaves'] for c in d['candidates'])==len(folds) for d in nulls))
 null_failure_count=sum(len(d['fit_failures']) for d in nulls)
 DETAIL['convergence_accounting']={'observed_failed':len(observed_failures),'observed_fits':2*len(folds),'null_failed_declared':null_failure_count,'null_fits':sum(2*d['active_folds'] for d in nulls),'null_gradients_independently_recomputed':False}
 check('null_failure_declarations_well_formed',all(v['arm'] in ['C','FULL'] and (v['family'],v['leaf']) in expected and not v['converged'] and v['max_abs_gradient']>1e-9 for d in nulls for v in d['fit_failures']))
 rank=(1+sum(d['T']>=result['T']-1e-12 for d in nulls))/200;converged=not result['fit_failures'] and not any(d['fit_failures'] for d in nulls)
 status='NUMERICAL_FIT_FAIL' if not converged else ('IMAGE_LINKED_INVERSE_COMBINATION_TRANSFER' if result['pre_null_gates'] and rank<=.05 else 'NO_SUPPORTED_INVERSE_COMBINATION_TRANSFER')
 check('fixed_rank_gates_and_final_decision',near(rank,result['null_rank']) and result['null_draws']==199 and result['status']==status and result['all_fits_converged']==converged and result['unique_raw_worlds']==len({d['raw_world_hash'] for d in nulls}) and result['unique_observable_worlds']==len({d['observable_world_hash'] for d in nulls}))
 check('no_meaning_or_confirmation_claim',result['confirmed_words']==0 and result['independent_confirmation'] is False)
 DETAIL['scientific_result']={k:result[k] for k in ['status','T','mean_INV_gain_C','mean_INV_gain_ID','positive_families','negative_fraction','null_rank']}

def main():
 fixture_X=np.array([[1.,-.5],[1.,.5],[1.,2.]]);fixture_y=np.array([0.,1.,1.]);fixture_w=np.array([.2,.3,.5]);fixture_b=np.array([.1,-.2]);_,fixture_g=objective(fixture_b,fixture_X,fixture_y,fixture_w);eps=1e-6
 fd=np.array([(objective(fixture_b+eps*np.eye(2)[i],fixture_X,fixture_y,fixture_w)[0]-objective(fixture_b-eps*np.eye(2)[i],fixture_X,fixture_y,fixture_w)[0])/(2*eps) for i in range(2)])
 check('independent_probability_and_gradient_fixtures',near(sigmoid(np.array([-2.,0.,2.])),1/(1+np.exp(-np.array([-2.,0.,2.])))) and near(logit(sigmoid(np.array([-2.,2.]))),[-2.,2.]) and near(fd,fixture_g,tol=1e-8))
 ap=argparse.ArgumentParser();ap.add_argument('--prepare',action='store_true');args=ap.parse_args();x=load(E/'src/INPUT.json');old=source_audit(x)
 if (E/'PREREG_LOCK.json').exists():
  lock=load(E/'PREREG_LOCK.json');check('registered_byte_pins',all(sha(R/p)==h for p,h in lock['files'].items()))
 else:DETAIL['registration']='Not yet available during preparation'
 if not args.prepare:outputs_audit(x,old)
 out=dict(experiment='GDT1165',scope='Independent accounting and numerical checks; no visual truth or word meaning validation',report_structure_note='The combined numerical check remains failed. Accounting is reported separately; the failed convergence criterion is retained unchanged in checks and failures.',phase='PREPARATION' if args.prepare else 'FINAL',accounting_pass=not [v for v in FAIL if v!='every_observed_fit_convex_optimality'],numerical_contract_pass=CHECKS.get('every_observed_fit_convex_optimality'),all_checks_pass=not FAIL,checks=CHECKS,failures=FAIL,details=DETAIL,limits=['Legacy strip_layers reused only for the expressly frozen formal DY definition.','All observed base and logistic predictions independently reconstructed; fitted coefficients checked by convex gradients.','All199 null mappings, hashes, candidate arithmetic and rank checked; their full underlying logistic fits are not independently refitted.','Selected independent SciPy solutions characterize numerical closeness only; precision-loss flags are retained and do not replace the registered fit or tolerance.','No images inspected, no source or author files changed, no semantic certification.'])
 (A/'VALIDATION.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
 text=['# GDT1165 independent validation','',f"Phase: {out['phase']}. Source/accounting: {'PASS' if out['accounting_pass'] else 'FAIL'}. Registered convergence criterion: {out['numerical_contract_pass']}. Checks satisfied: {sum(CHECKS.values())}/{len(CHECKS)}.",'',json.dumps(DETAIL,indent=2),'','The frozen NUMERICAL_FIT_FAIL is retained. Correct accounting does not convert the invalid numerical assay into a supported or refuted scientific outcome. Observed T and rank are descriptive diagnostics only.','','Failures: '+(', '.join(FAIL) or 'none'),'',*out['limits']]
 (A/'VALIDATION.md').write_text('\n'.join(text)+'\n');print(json.dumps({k:out[k] for k in ['phase','accounting_pass','failures']}));return 0 if out['accounting_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
