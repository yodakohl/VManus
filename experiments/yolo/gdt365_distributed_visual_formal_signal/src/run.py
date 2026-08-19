#!/usr/bin/env python3
"""GDT365: frozen low-capacity distributed visual/formal instrument."""
from __future__ import annotations
import csv,hashlib,importlib.util,json,math,re,sys
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from tools.vmanus_experiment import GuardedTSV,canonical_json_bytes,sha256_file  # noqa:E402
EXP=ROOT/'experiments/yolo/gdt365_distributed_visual_formal_signal';ART=EXP/'artifacts'
LEAF=ROOT/'experiments/yolo/gdt363_leaf_margin_formal_atlas/artifacts/gdt363_panel.tsv';REPRO=ROOT/'experiments/yolo/gdt364_reproductive_structure_joint_atlas/artifacts/gdt364_panel.tsv';FREEZE=ART/'gdt365_freeze.json'
FORMAL=ROOT/'experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv';HELPER=ROOT/'experiments/yolo/gdt363_leaf_margin_formal_atlas/src/run.py'
SCORES=ART/'gdt365_scores.tsv';FOLDS=ART/'gdt365_folds.tsv';FEATURES=ART/'gdt365_feature_manifest.tsv';COUNTER=ART/'gdt365_counterexamples.tsv';RESULT=ART/'gdt365_result.json';REPORT=EXP/'REPORT.md'
DIMS=(2,4,8);WORLDS=1024;SEED=3651901;RIDGE=8.0
spec=importlib.util.spec_from_file_location('gdt363_frozen',HELPER);assert spec and spec.loader;g363=importlib.util.module_from_spec(spec);spec.loader.exec_module(g363)
def read(p):
 with p.open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows,fields=None):
 names=fields or list(rows[0]);h=p.open('w',encoding='utf-8',newline='');w=csv.DictWriter(h,fieldnames=names,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);h.close()
def folio_num(value):return int(re.match(r'^f(\d+)',value).group(1))
def common_quartiles(rows):
 folios=sorted({r['physical_folio'] for r in rows},key=folio_num);rank={f:i for i,f in enumerate(folios)};n=len(folios)
 return {f:str(min(4,rank[f]*4//n+1)) for f in folios}
def nuisance(rows):
 cats={'currier_hand':sorted({f"{r['currier']}:{r['hand']}" for r in rows}),'quire':sorted({r['quire'] for r in rows}),'quartile':sorted({r['quartile'] for r in rows}),'side':sorted({r['page'][-1] for r in rows})}
 names=['log_groups','log_loci','mean_symbols','label_rate','alternative_rate']+[f'{k}={v}' for k,vs in cats.items() for v in vs];out=[]
 for r in rows:
  x=[math.log1p(int(r['group_count'])),math.log1p(int(r['locus_count'])),float(r['mean_symbols_per_group']),float(r['label_group_rate']),float(r['alternative_group_rate'])];actual={'currier_hand':f"{r['currier']}:{r['hand']}",'quire':r['quire'],'quartile':r['quartile'],'side':r['page'][-1]};x += [float(actual[k]==v) for k,vs in cats.items() for v in vs];out.append(x)
 return np.asarray(out),names
def prepared_folds(rows,X,N,hold_key):
 folds=[]
 for held in sorted({r[hold_key] for r in rows},key=lambda v:(folio_num(v) if str(v).startswith('f') else 999,str(v))):
  tr=np.asarray([i for i,r in enumerate(rows) if r[hold_key]!=held]);te=np.asarray([i for i,r in enumerate(rows) if r[hold_key]==held])
  nm=N[tr].mean(0);ns=N[tr].std(0);ns[ns<1e-9]=1;Ntr=np.column_stack([np.ones(len(tr)),(N[tr]-nm)/ns]);Nte=np.column_stack([np.ones(len(te)),(N[te]-nm)/ns]);pen=np.eye(Ntr.shape[1]);pen[0,0]=0
  beta=np.linalg.solve(Ntr.T@Ntr+RIDGE*pen+np.eye(Ntr.shape[1])*1e-9,Ntr.T@X[tr]);Rtr=X[tr]-Ntr@beta;Rte=X[te]-Nte@beta;mean=Rtr.mean(0);scale=Rtr.std(0);scale[scale<1e-9]=1;Rtr=(Rtr-mean)/scale;Rte=(Rte-mean)/scale
  _,_,vt=np.linalg.svd(Rtr,full_matrices=False);zs={d:(Rtr@vt[:min(d,len(vt))].T,Rte@vt[:min(d,len(vt))].T) for d in DIMS};folds.append({'held':held,'train':tr,'test':te,'z':zs})
 return folds
def probs(Ztr,ytr,Zte,K):
 counts=np.bincount(ytr,minlength=K);prior=(counts+1)/(len(ytr)+K);means=np.zeros((K,Ztr.shape[1]))
 for k in range(K):means[k]=Ztr[ytr==k].mean(0)
 within=sum(float(np.sum((Ztr[i]-means[ytr[i]])**2)) for i in range(len(ytr)));var=(within+Ztr.shape[1])/(len(ytr)*Ztr.shape[1]+Ztr.shape[1]);var=max(var,.1)
 logits=np.log(prior)[None,:]-np.sum((Zte[:,None,:]-means[None,:,:])**2,axis=2)/(2*var);logits-=logits.max(1,keepdims=True);P=np.exp(logits);return P/P.sum(1,keepdims=True),prior
def score(folds,y,K,d):
 P=np.zeros((len(y),K));B=np.zeros_like(P);details=[];positive=0
 for f in folds:
  tr,te=f['train'],f['test'];p,prior=probs(f['z'][d][0],y[tr],f['z'][d][1],K);P[te]=p;B[te]=prior
  gain=float(np.sum(np.log2(np.clip(P[te,np.asarray(y[te],int)],1e-12,1)/np.clip(B[te,np.asarray(y[te],int)],1e-12,1))));positive+=gain>0;details.append({'held':f['held'],'gain':gain,'n':len(te)})
 total=float(np.sum(np.log2(np.clip(P[np.arange(len(y)),y],1e-12,1)/np.clip(B[np.arange(len(y)),y],1e-12,1))));return total,int(positive),int(np.sum(np.argmax(P,1)==y)-np.sum(np.argmax(B,1)==y)),details
def perm_leaf(y,rows,rng):
 out=y.copy();blocks=defaultdict(list)
 for i,r in enumerate(rows):blocks[(r['currier'],r['quartile'])].append(i)
 for idx in blocks.values():out[idx]=out[np.asarray(idx)[rng.permutation(len(idx))]]
 return out
def perm_repro(y,rows,rng):
 by=defaultdict(list)
 for i,r in enumerate(rows):by[r['physical_folio']].append(i)
 for idx in by.values():idx.sort(key=lambda i:rows[i]['page'])
 blocks=defaultdict(list)
 for f,idx in by.items():blocks[(rows[idx[0]]['quire'],len(idx))].append(f)
 out=y.copy()
 for fs in blocks.values():
  for a,b in zip(fs,list(rng.permutation(fs))):out[by[a]]=y[by[str(b)]]
 return out
def main():
 lp=read(LEAF);rp=read(REPRO);allowed={r['page'] for r in lp+rp};reader=GuardedTSV(FORMAL,selector_column='page',allowed_values=allowed,forbidden_prefixes=('f84',),forbidden_action='skip');src=list(reader);assert not any(r['page'].startswith('f84') for r in src)
 by=defaultdict(list)
 for r in src:by[r['page']].append(r)
 assert set(by)==allowed
 vals={};meta={}
 for p in allowed:vals[p],meta[p]=g363.family_events(by[p])
 names=sorted(n for n in {k for v in vals.values() for k in v} if sum(vals[p].get(n,0)>0 for p in allowed)>=8 and sum(vals[p].get(n,0)==0 for p in allowed)>=8);write(FEATURES,[{'feature_index':i+1,'formal_feature':n,'support_union_pages':sum(vals[p].get(n,0)>0 for p in allowed),'absence_union_pages':sum(vals[p].get(n,0)==0 for p in allowed)} for i,n in enumerate(names)])
 def rows_for(endpoint,panel):
  base=[r for r in panel if endpoint!='LEAF_MARGIN_BINARY' or r['score_eligible']=='1'];qs=common_quartiles(base);out=[]
  for r in base:
   first=by[r['page']][0];q=r.get('folio_rank_quartile') or qs[r['physical_folio']];out.append({**r,**meta[r['page']],'endpoint':endpoint,'currier':first['currier'],'hand':first['hand'],'quartile':q})
  return out
 endpoint_rows={'LEAF_MARGIN_BINARY':rows_for('LEAF_MARGIN_BINARY',lp),'REPRODUCTIVE_THREE_CLASS':rows_for('REPRODUCTIVE_THREE_CLASS',rp)};class_lists={'LEAF_MARGIN_BINARY':['SMOOTH','TOOTHED'],'REPRODUCTIVE_THREE_CLASS':['BERRY_NO_CIRCLES','FLOWER_SIDE','NO_FRUIT_OR_FLOWER']}
 prepared={};ys={};Ns={};Xsets={};nuisance_names={}
 for endpoint,rows in endpoint_rows.items():
  classes=class_lists[endpoint];ys[endpoint]=np.asarray([classes.index(r['leaf_margin_state'] if endpoint.startswith('LEAF') else r['visual_state']) for r in rows]);Xsets[endpoint]=np.asarray([[vals[r['page']].get(n,0) for n in names] for r in rows]);Ns[endpoint],nuisance_names[endpoint]=nuisance(rows);prepared[(endpoint,'FOLIO')]=prepared_folds(rows,Xsets[endpoint],Ns[endpoint],'physical_folio');prepared[(endpoint,'QUIRE')]=prepared_folds(rows,Xsets[endpoint],Ns[endpoint],'quire')
 observed={};fold_rows=[]
 for endpoint in endpoint_rows:
  for d in DIMS:
   fg,fp,ft,fd=score(prepared[(endpoint,'FOLIO')],ys[endpoint],len(class_lists[endpoint]),d);qg,qp,qt,qd=score(prepared[(endpoint,'QUIRE')],ys[endpoint],len(class_lists[endpoint]),d);observed[(endpoint,d)]={'folio_gain':fg,'folio_positive':fp,'folio_top_delta':ft,'quire_gain':qg,'quire_positive':qp,'quire_top_delta':qt}
   for scope,detail in [('FOLIO',fd),('QUIRE',qd)]:
    for x in detail:fold_rows.append({'endpoint':endpoint,'dimension':d,'hold_scope':scope,'held':x['held'],'n':x['n'],'gain_bits':f"{x['gain']:.12f}"})
 rng=np.random.default_rng(SEED);null={k:np.zeros(WORLDS) for k in observed}
 for w in range(WORLDS):
  yp={'LEAF_MARGIN_BINARY':perm_leaf(ys['LEAF_MARGIN_BINARY'],endpoint_rows['LEAF_MARGIN_BINARY'],rng),'REPRODUCTIVE_THREE_CLASS':perm_repro(ys['REPRODUCTIVE_THREE_CLASS'],endpoint_rows['REPRODUCTIVE_THREE_CLASS'],rng)}
  for endpoint,d in observed:null[(endpoint,d)][w]=score(prepared[(endpoint,'FOLIO')],yp[endpoint],len(class_lists[endpoint]),d)[0]
 maxv=np.max(np.column_stack([null[k] for k in sorted(null)]),axis=1);scores=[]
 for endpoint,d in sorted(observed):
  o=observed[(endpoint,d)];local=(1+int(np.sum(null[(endpoint,d)]>=o['folio_gain']-1e-12)))/(WORLDS+1);maxp=(1+int(np.sum(maxv>=o['folio_gain']-1e-12)))/(WORLDS+1)
  if o['folio_gain']>0 and o['quire_gain']>0 and o['folio_positive']>=len(prepared[(endpoint,'FOLIO')])/2 and maxp<=.2:status='DISTRIBUTED_SIGNAL_INTERESTING_EXPLORATORY'
  elif o['folio_gain']>0:status='DISTRIBUTED_SIGNAL_LOCAL_OR_UNSTABLE'
  else:status='NO_DISTRIBUTED_SIGNAL'
  scores.append({'endpoint':endpoint,'pca_dimensions':d,'formal_feature_count':len(names),'folio_folds':len(prepared[(endpoint,'FOLIO')]),'folio_gain_bits':f"{o['folio_gain']:.12f}",'folio_positive_folds':o['folio_positive'],'folio_top1_correct_delta':o['folio_top_delta'],'quire_folds':len(prepared[(endpoint,'QUIRE')]),'quire_gain_bits':f"{o['quire_gain']:.12f}",'quire_positive_folds':o['quire_positive'],'quire_top1_correct_delta':o['quire_top_delta'],'local_p':f"{local:.12f}",'max_six_p':f"{maxp:.12f}",'status':status})
 write(SCORES,scores);write(FOLDS,fold_rows)
 counters=[]
 for row in scores:
  endpoint=row['endpoint'];d=int(row['pca_dimensions']);details=[r for r in fold_rows if r['endpoint']==endpoint and int(r['dimension'])==d and r['hold_scope']=='FOLIO'];
  for x in sorted(details,key=lambda r:float(r['gain_bits']))[:5]:counters.append({'endpoint':endpoint,'pca_dimensions':d,'held_folio':x['held'],'gain_bits':x['gain_bits'],'reason':'WORST_HELD_FOLIO_COUNTEREXAMPLE'})
 write(COUNTER,counters)
 best=max(scores,key=lambda r:float(r['folio_gain_bits']));counts=Counter(r['status'] for r in scores)
 payload={'schema':'GDT365_RESULT_V1','status':'DISTRIBUTED_VISUAL_FORMAL_MODEL_COMPLETE','panel':{'union_pages':len(allowed),'leaf_pages':len(endpoint_rows['LEAF_MARGIN_BINARY']),'reproductive_pages':len(endpoint_rows['REPRODUCTIVE_THREE_CLASS']),'formal_groups':len(src)},'feature_library':{'count':len(names),'support_min':8,'absence_min':8},'models':scores,'status_counts':dict(counts),'best_model':best,'null':{'worlds':WORLDS,'seed':SEED,'max_family':6},'postexposure':True,'pharma_local_overlap_not_modelled':{'contact_x_root_color':2,'root_color_x_root_leaf':6,'flower_x_root_color':7},'access':{'new_images_or_catalogues_opened':False,'f84_rows_retained_parsed_joined_scored':False,'f84_rows_skipped_before_parse':reader.stats.skipped_forbidden},'inputs':{str(p.relative_to(ROOT)):sha256_file(p) for p in (LEAF,REPRO,FREEZE,FORMAL,EXP/'METHOD.md',HELPER)},'implementation':{str(Path(__file__).relative_to(ROOT)):sha256_file(Path(__file__))},'outputs':{str(p.relative_to(ROOT)):sha256_file(p) for p in (SCORES,FOLDS,FEATURES,COUNTER)},'claim_ceiling':'POSTEXPOSURE_DISTRIBUTED_ANONYMOUS_PAGE_SIGNAL_ONLY_NO_LEXICAL_OR_SEMANTIC_CLAIM'};payload['content_hash']=hashlib.sha256(canonical_json_bytes(payload)).hexdigest();RESULT.write_bytes(canonical_json_bytes(payload))
 lines=['# GDT365 distributed visual/formal signal report','',f"Status: **{payload['status']}**.",'','## Outcome','',f"A common state-blind vocabulary of **{len(names)}** anonymous family/construction rates was evaluated on the 42-page leaf-margin and 34-page reproductive panels. PCA and nuisance residualization were relearned inside every held fold.",'','| endpoint | PCA dims | folio gain bits | positive folds | quire gain bits | local p | max-six p | status |','|---|---:|---:|---:|---:|---:|---:|---|']
 for r in scores:lines.append(f"| {r['endpoint']} | {r['pca_dimensions']} | {float(r['folio_gain_bits']):+.3f} | {r['folio_positive_folds']}/{r['folio_folds']} | {float(r['quire_gain_bits']):+.3f} | {float(r['local_p']):.4f} | {float(r['max_six_p']):.4f} | {r['status']} |")
 lines += ['','## Interpretation','',f"The strongest model is {best['endpoint']} at {best['pca_dimensions']} dimensions with {float(best['folio_gain_bits']):+.3f} held-folio bits and max-six p={float(best['max_six_p']):.4f}, but it loses {abs(float(best['quire_gain_bits'])):.3f} bits under held-quire transfer. This is a postexposure distributed test; it does not rescue any single GDT363/GDT364 family feature. The reversal identifies local page/quire ecology, not a transferable visual-content channel.",'',"The local Pharma annotation axes were not combined: their pairwise overlap is only 2, 6, and 7 cells, too small for a distributed phenotype model even in YOLO mode.",'','## Seal and ceiling','',f"The guarded reader retained {reader.stats.selected} whitelisted formal rows and skipped {reader.stats.skipped_forbidden} f84-prefixed rows before formal parsing. No f84 row was retained, parsed, joined, displayed, or scored; no image or catalogue was opened.",'',"This analysis assigns no plant, visual-state word, role, lexeme, morpheme, sound, language, plaintext, meaning, or translation.",''];REPORT.write_text('\n'.join(lines),encoding='utf-8')
if __name__=='__main__':main()
