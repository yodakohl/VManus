"""Exact source-only unknown-form graph assignment; gold-free fit interface."""
import base64,gzip,hashlib,itertools,json,os,time
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from pathlib import Path
import numpy as np
from extract import intake
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
# Map ID is base5, first form most significant, OTHER=0, concept slots1..4.
MAPS=np.array(list(itertools.product(range(5),repeat=7)),dtype=np.uint8)
MASKS=np.stack([((MAPS==c)*np.array([1<<i for i in range(7)])).sum(axis=1) for c in range(1,5)],axis=1).astype(np.uint8)
PAIRS=list(itertools.combinations(range(4),2));NMAP=5**7;PAYLOAD=None

def dump(name,x):
 b=(json.dumps(x,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
 if name.endswith('.gz'):(A/name).write_bytes(gzip.compress(b,mtime=0))
 else:(A/name).write_bytes(b)
def bitmap(mask):return base64.b64encode(np.packbits(mask,bitorder='little').tobytes()).decode()
def choices(mask):
 return [[int(v) for v in np.unique(MAPS[mask,j])] for j in range(7)]
def probabilities(mask):
 return np.array([np.bincount(MAPS[mask,j],minlength=5)/int(mask.sum()) for j in range(7)])

def fit(train_incidence,held_incidence):
 """Only numeric observed incidence matrices; no words, concepts or gold."""
 S=np.asarray(train_incidence,dtype=float);B=np.asarray(held_incidence,dtype=bool);n=len(B);ps=S.mean(axis=0);qs=(S.T@S)/len(S)
 rowcodes=(B*np.array([1<<i for i in range(7)],dtype=np.uint8)).sum(axis=1).astype(np.uint8)
 subset=((rowcodes[:,None]&np.arange(128,dtype=np.uint8)[None,:])!=0).astype(float)
 pt=subset.mean(axis=0);qt=(subset.T@subset)/n
 freq=((pt[MASKS]-ps[None,:])**2).mean(axis=1);graph=freq.copy()
 for a,b in PAIRS:graph+=(qt[MASKS[:,a],MASKS[:,b]]-qs[a,b])**2/6
 out={}
 for arm,score in [('F',freq),('G',graph)]:
  minimum=float(score.min());maximum=float(score.max());opt=score<=minimum+1e-12;threshold=minimum+.01*(maximum-minimum);envelope=score<=threshold+1e-12;ids=np.flatnonzero(opt)
  out[arm]={'minimum':minimum,'maximum':maximum,'optimum_count':int(opt.sum()),'optimum_bitmap_base64':bitmap(opt),'canonical_mapping_id':int(ids[0]),'canonical_mapping':MAPS[ids[0]].astype(int).tolist(),'optimum_label_probabilities':probabilities(opt).tolist(),'optimum_label_possibilities':choices(opt),'envelope_threshold':threshold,'envelope_count':int(envelope.sum()),'envelope_bitmap_base64':bitmap(envelope),'envelope_label_possibilities':choices(envelope)}
 return out

def gold_account(models,gold):
 rows=[];total=0;weighted={'F':0.,'G':0.};oovtotal=0;reject={'F':0.,'G':0.};concepts=gold['concepts'];exact_by_arm={'F':[],'G':[]};integer_label_counts={}
 for arm in ['F','G']:
  bits=np.unpackbits(np.frombuffer(base64.b64decode(models[arm]['optimum_bitmap_base64']),dtype=np.uint8),bitorder='little')[:NMAP].astype(bool)
  assert int(bits.sum())==models[arm]['optimum_count']
  integer_label_counts[arm]=[np.bincount(MAPS[bits,j],minlength=5) for j in range(7)]
 for j,f in enumerate(gold['forms']):
  n=f['occurrences'];counts=np.array([f['gold_counts'].get(c,0) for c in concepts],float);oov=n-counts.sum();oovtotal+=int(oov);total+=n;acc={};other={}
  for arm in ['F','G']:
   lc=integer_label_counts[arm][j];den=models[arm]['optimum_count'];exact=Fraction(sum(int(lc[k+1])*f['gold_counts'].get(c,0) for k,c in enumerate(concepts)),den*n);exact_by_arm[arm].append(exact)
   prob=lc/den;correct=float(exact*n);acc[arm]=float(exact);other[arm]=float(prob[0]);weighted[arm]+=correct;reject[arm]+=prob[0]*oov
  rows.append({'form_index':j,'surface':f['surface'],'occurrences':n,'gold_counts':f['gold_counts'],'gold_labels':f['gold_labels'],'in_inventory_occurrences':int(counts.sum()),'out_of_inventory_occurrences':int(oov),'oracle_single_label_named_upper_bound':float(counts.max()/n),'named_accuracy':acc,'OTHER_probability':other,'delta_G_minus_F':acc['G']-acc['F'],'contradictory_occurrence_counts_by_named_slot':{c:n-f['gold_counts'].get(c,0) for c in concepts}})
 em={arm:sum(exact_by_arm[arm],Fraction(0))/len(rows) for arm in ['F','G']};macro={arm:float(em[arm]) for arm in ['F','G']};delta=em['G']-em['F']
 return {'forms':rows,'named_macro':macro,'named_macro_exact':{arm:[em[arm].numerator,em[arm].denominator] for arm in ['F','G']},'delta':float(delta),'delta_exact':[delta.numerator,delta.denominator],'occurrence_weighted_named':{arm:weighted[arm]/total for arm in ['F','G']},'oov_occurrences':oovtotal,'correct_OTHER_rejection_rate':{arm:reject[arm]/oovtotal if oovtotal else None for arm in ['F','G']},'oracle_named_macro_upper_bound':float(np.mean([r['oracle_single_label_named_upper_bound'] for r in rows]))}

def curveball(B,seed):
 out=np.asarray(B,dtype=np.uint8).copy();rng=np.random.default_rng(seed);N=len(out);changed_trades=0
 for step in range(100*N):
  a,b=rng.choice(N,2,replace=False);diff=np.flatnonzero(out[a]!=out[b]);na=int(out[a,diff].sum())
  if na==0 or na==len(diff):continue
  chosen=diff[rng.choice(len(diff),size=na,replace=False)];old=out[a,diff].copy();out[a,diff]=0;out[b,diff]=1;out[a,chosen]=1;out[b,chosen]=0;changed_trades+=int(not np.array_equal(old,out[a,diff]))
 assert np.array_equal(out.sum(axis=0),np.asarray(B).sum(axis=0)) and np.array_equal(out.sum(axis=1),np.asarray(B).sum(axis=1))
 return out,changed_trades

def init(p):
 global PAYLOAD
 PAYLOAD=p

def null_job(task):
 fi,wi=task;d=PAYLOAD['predictors'][fi];seed=1159000+1000*fi+wi;B,changes=curveball(d['held_incidence'],seed);models=fit(d['train_incidence'],B);account=gold_account(models,PAYLOAD['gold'][fi])
 return {'fold_index':fi,'world_index':wi,'seed':seed,'changed_trades':changes,'changed_cells':int(np.count_nonzero(B!=np.asarray(d['held_incidence']))),'matrix_shape':list(B.shape),'matrix_bitmap_base64':base64.b64encode(np.packbits(B.reshape(-1),bitorder='little').tobytes()).decode(),'matrix_sha256':hashlib.sha256(B.tobytes()).hexdigest(),'row_sums':B.sum(axis=1).astype(int).tolist(),'column_sums':B.sum(axis=0).astype(int).tolist(),'models':models,'named_macro':account['named_macro'],'named_macro_exact':account['named_macro_exact'],'delta':account['delta'],'delta_exact':account['delta_exact'],'occurrence_weighted_named':account['occurrence_weighted_named'],'correct_OTHER_rejection_rate':account['correct_OTHER_rejection_rate']}

def write_candidates(observed,gold):
 text=['# GDT1159 all42 selected forms','','Known source gold evaluates hidden identity recovery; this is not Voynich decipherment. Accuracy averages all exact optima; OTHER contributes zero named accuracy. All spellings are retained.','','|Held collection|Original form|Gold Q counts|Editor English label counts|F named accuracy|G named accuracy|F alternatives|G alternatives|G 1% envelope|','|---|---|---|---|---:|---:|---|---|---|']
 for obs,g in zip(observed,gold):
  labels=['OTHER']+[q+' ('+'/'.join(g['concept_labels'][q])+')' for q in g['concepts']]
  for j,f in enumerate(obs['account']['forms']):
   vals=[g['held_collection'],f['surface'],json.dumps(f['gold_counts'],ensure_ascii=False),'; '.join(('/'.join(f['gold_labels'].get(q,[])) or '[unlabelled]')+': '+str(n) for q,n in f['gold_counts'].items()),f"{f['named_accuracy']['F']:.6f}",f"{f['named_accuracy']['G']:.6f}",'; '.join(labels[c] for c in obs['models']['F']['optimum_label_possibilities'][j]),'; '.join(labels[c] for c in obs['models']['G']['optimum_label_possibilities'][j]),'; '.join(labels[c] for c in obs['models']['G']['envelope_label_possibilities'][j])]
   text.append('|'+ '|'.join(v.replace('|','&#124;').replace('\n',' ') for v in vals)+'|')
 (E/'CANDIDATE_TABLE.md').write_text('\n'.join(text)+'\n')

def main():
 started=time.time();print(json.dumps({'stage':'START','pid':os.getpid()}),flush=True)
 lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
 for p,h in lock['files'].items():assert hashlib.sha256((E/p).read_bytes()).hexdigest()==h,p
 source=json.loads((E/'src/SOURCE.json').read_text());projection,predictors,gold=intake(R,source)
 dump('SOURCE_PROJECTION.json.gz',projection);dump('PREDICTOR_INPUTS.json',predictors);dump('GOLD.json',gold)
 dump('MAPPING_SCHEMA.json',{'count':NMAP,'digits':7,'base':5,'form0_most_significant':True,'OTHER':0,'source_concepts':[1,2,3,4],'bitmap_encoding':'base64 of numpy.packbits(mask,bitorder=little), first78125bits in mapping-ID order','score_tolerance':1e-12})
 observed=[]
 for d,g in zip(predictors,gold):
  if not d['capacity']:
   observed.append({'fold_index':d['fold_index'],'held_collection':d['held_collection'],'status':'NO_CAPACITY'});continue
  models=fit(d['train_incidence'],d['held_incidence']);account=gold_account(models,g);row={'fold_index':d['fold_index'],'held_collection':d['held_collection'],'status':'COMPLETE','models':models,'account':account};observed.append(row)
  print(json.dumps({'stage':'OBSERVED_FOLD','fold':d['held_collection'],'named_macro':account['named_macro'],'delta':account['delta'],'optima':{a:models[a]['optimum_count'] for a in ['F','G']}}),flush=True)
 dump('OBSERVED.json.gz',observed)
 if not all(d['capacity'] for d in predictors):
  dump('RESULT.json',{'status':'NO_CAPACITY','folds':observed});return
 payload={'predictors':predictors,'gold':gold};jobs=[(fi,wi) for fi in range(6) for wi in range(1,200)];byfold={fi:[] for fi in range(6)}
 with ProcessPoolExecutor(max_workers=min(24,os.cpu_count() or 1),initializer=init,initargs=(payload,)) as pool:
  for n,result in enumerate(pool.map(null_job,jobs,chunksize=2),1):
   byfold[result['fold_index']].append(result)
   if n%199==0:
    fi=result['fold_index'];dump(f'NULL_FOLD_{fi}.json.gz',byfold[fi]);print(json.dumps({'stage':'NULL_FOLD_COMPLETE','fold':fi,'worlds':len(byfold[fi]),'elapsed_seconds':round(time.time()-started,2)}),flush=True)
 nullagg=[]
 for wi in range(1,200):
  nd=sum((Fraction(*byfold[fi][wi-1]['delta_exact']) for fi in range(6)),Fraction(0))/6
  nullagg.append({'world_index':wi,'delta':float(nd),'delta_exact':[nd.numerator,nd.denominator],'fold_deltas':[byfold[fi][wi-1]['delta'] for fi in range(6)]})
 dump('NULL_AGGREGATE.json',nullagg)
 ep={a:sum((Fraction(*x['account']['named_macro_exact'][a]) for x in observed),Fraction(0))/6 for a in ['F','G']};ed=ep['G']-ep['F'];primary={a:float(ep[a]) for a in ['F','G']};delta=float(ed);positive=sum(Fraction(*x['account']['delta_exact'])>0 for x in observed);ge=sum(Fraction(*x['delta_exact'])>=ed for x in nullagg);rank=(1+ge)/200;passed=ed>=Fraction(1,20) and positive>=4 and Fraction(1+ge,200)<=Fraction(1,20)
 result={'status':'SUPPORTED_LIMITED_SOURCE_RECOVERY' if passed else 'NO_SUPPORTED_GRAPH_LEXICAL_INCREMENT','folds':6,'forms':42,'source_counts':projection['counts'],'named_macro':primary,'named_macro_exact':{a:[ep[a].numerator,ep[a].denominator] for a in ['F','G']},'delta':delta,'delta_exact':[ed.numerator,ed.denominator],'arithmetic_correction':'Uniform-optimum label counts and gold occurrence counts are evaluated as exact Fractions for primary gains and inclusive control ranks; fitted costs, optima, envelopes and null matrices unchanged.','positive_folds':positive,'null_worlds_per_fold':199,'null_aggregate_at_least_observed':ge,'conditional_control_rank':rank,'fold_results':[{'collection':x['held_collection'],**{k:x['account'][k] for k in ['named_macro','delta','occurrence_weighted_named','correct_OTHER_rejection_rate','oracle_named_macro_upper_bound']},'optimum_counts':{a:x['models'][a]['optimum_count'] for a in ['F','G']},'envelope_counts':{a:x['models'][a]['envelope_count'] for a in ['F','G']},'unique_null_matrices':len({n['matrix_sha256'] for n in byfold[x['fold_index']]}),'unchanged_null_worlds':sum(n['changed_cells']==0 for n in byfold[x['fold_index']])} for x in observed],'assignments_per_fit':NMAP,'fitted_worlds_including_observed':1200,'prediction_gold_interfaces_separate':True,'voynich_access':False,'voynich_meanings':0,'calibrated_probability_claim':False,'uniform_null_mixing_claim':False,'general_significance_claim':False}
 dump('RESULT.json',result)
 write_candidates(observed,gold);print(json.dumps({'stage':'COMPLETE',**result},indent=2),flush=True)
if __name__=='__main__':main()
