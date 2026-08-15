#!/usr/bin/env python3
"""Score frozen tentative-identification tokens against Herbal page form."""
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent; SOURCE=R/'gdt062_right_family_inventory.tsv'; INVENTORY=R/'gdt139_identification_token_inventory.tsv'; FREEZE=R/'gdt139_prediction.json'; METHOD=R/'GDT139_HERBAL_IDENTIFICATION_TOKEN_TRANSFER_METHOD.md'; REPORT=R/'GDT139_HERBAL_IDENTIFICATION_TOKEN_TRANSFER_REPORT.md'; SCORE=R/'gdt139_panel_scores.tsv'; TOKEN=R/'gdt139_token_scores.tsv'; FOLD=R/'gdt139_folio_scores.tsv'; PAGE=R/'gdt139_page_predictions.tsv'; CROSS=R/'gdt139_cross_source_scores.tsv'; NULL=R/'gdt139_null_results.tsv'; COUNTER=R/'gdt139_counterexamples.tsv'; VARIANT=R/'gdt139_variant_log.tsv'; RESULT=R/'gdt139_result.json'
REPS=('PAGE_HOST_IDENTITY','PAGE_HOST_CHAR3','RAW_CHAR3','COMPILER_SIGNATURE');K=7;SHRINK=8.;WORLDS=10000;SEED=139001
VIS=('DAISY_CUP','BROAD_CALYX','GRASS','ROOT_PLATFORM','LEAVES_ONE_SIDE','FUSED_PARALLEL_LEAVES','BULB_OR_TUBER_ROOT','LARGE_OR_EXTENSIVE_ROOT','MULTIPLE_PLANTS','BLUE_FLOWERS_OR_BUDS','FINGERED_OR_FRILLED_LEAVES','MULTIPLE_STEMS_OR_STALKS')
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def clean(rows):return [{k:f'{v:.12g}' if isinstance(v,float) else v for k,v in x.items()} for x in rows]
def add3(c,s):
 s='^'+s+'$'
 for i in range(max(1,len(s)-2)):c[s[i:i+3]]+=1.
def dist(a,b):
 keys=set(a)|set(b); den=sum(max(a[k],b[k]) for k in keys)
 return 1-sum(min(a[k],b[k]) for k in keys)/den if den else 0.
def loss(y,p):p=np.clip(p,1e-12,1-1e-12);return -np.log2(np.where(y>0,p,1-p))
def main():
 freeze=json.loads(FREEZE.read_text()); rows=read(INVENTORY); assert len(rows)==173 and not any(x['page'].startswith('f84') for x in rows)
 pages=sorted({x['page'] for x in rows}); source=[]
 with SOURCE.open(encoding='utf8',newline='') as h:
  for x in csv.DictReader(h,delimiter='\t'):
   if x['page'].startswith('f84'):continue
   if x['page'] in pages:source.append(x)
 assert set(x['page'] for x in source)==set(pages)
 bypage=defaultdict(list)
 for x in source:bypage[x['page']].append(x)
 formal={}; nuisance={}; maxv={k:max(float(x[k] or 0) for x in rows) or 1 for k in ('catalogue_prose_lines','paragraph_starts','formal_lines','formal_groups')}
 for p in pages:
  z=sorted(bypage[p],key=lambda x:(x['locus'],int(x['group_index']))); b={rep:Counter() for rep in REPS}
  for x in z:
   b['PAGE_HOST_IDENTITY']['H='+x['page_host']]+=1;add3(b['PAGE_HOST_CHAR3'],x['page_host']);add3(b['RAW_CHAR3'],x['token']);b['COMPILER_SIGNATURE']['|'.join((x['wrapper'],x['inner_d'],x['local_frame'],x['right_family'],x['dy_closure'],x['b3']))]+=1
  formal[p]=b
 for x in rows:
  n=Counter({'CUR='+x['currier']:1.,'HAND='+x['hand']:1.,'PROFILE='+x['illustration_profile']:1.,'LABEL='+x['catalogue_label_presence']:1.})
  for k in maxv:n[k]=float(x[k] or 0)/maxv[k]
  for k in VIS:n['VIS='+k]=float(x['VIS_'+k])
  nuisance[x['panel'],x['page']]=n
 score_rows=[];token_rows=[];fold_rows=[];page_rows=[];panel_cache={};obs={};tobs={}
 for panel in ('ELV','THP'):
  pr=[x for x in rows if x['panel']==panel]; names=[f'{panel}_{t.upper()}' for t in freeze['eligible_tokens'][panel]]; y=np.array([[int(x[n]) for n in names] for x in pr],float); n=len(pr); folios=sorted({x['physical_folio'] for x in pr});fi={f:np.array([i for i,x in enumerate(pr) if x['physical_folio']==f],int) for f in folios}
  def weights(rep=None,train_rows=None):
   train_rows=train_rows or pr; m=np.zeros((n,len(train_rows)))
   for i,t in enumerate(pr):
    ranked=[]
    for j,s in enumerate(train_rows):
     if s['physical_folio']==t['physical_folio']:continue
     d=dist(nuisance[panel,t['page']],nuisance[s['panel'],s['page']])+(dist(formal[t['page']][rep],formal[s['page']][rep]) if rep else 0);ranked.append((d,s['page'],j))
    for d,_,j in sorted(ranked)[:K]:m[i,j]=1/(.1+d)
   return m
  bw=weights(); bp=(bw@y+.5)/(bw.sum(1)[:,None]+1);bl=loss(y,bp);rw={rep:weights(rep) for rep in REPS};pred={rep:(rw[rep]@y+SHRINK*bp)/(rw[rep].sum(1)[:,None]+SHRINK) for rep in REPS};ml={rep:loss(y,pred[rep]) for rep in REPS};panel_cache[panel]=(pr,names,y,bw,rw,bl,ml,bp,pred,fi)
  for rep in REPS:
   for j,name in enumerate(names):
    gains=bl[:,j]-ml[rep][:,j];token_rows.append({'panel':panel,'token':name.split('_',1)[1].lower(),'representation':rep,'positive_pages':int(y[:,j].sum()),'physical_folios':len({pr[i]['physical_folio'] for i in np.where(y[:,j]>0)[0]}),'gain_bits':float(gains.sum()),'positive_gain_folios':sum(float(gains[idx].sum())>0 for idx in fi.values()),'local_permutation_p':'PENDING','max_token_model_p':'PENDING'});tobs[panel,name,rep]=float(gains.sum())
   gain=float((bl-ml[rep]).sum());fg=[]
   for f,idx in fi.items():v=float((bl[idx]-ml[rep][idx]).sum());fg.append(v);fold_rows.append({'panel':panel,'representation':rep,'physical_folio':f,'pages':len(idx),'gain_bits':v})
   score_rows.append({'panel':panel,'representation':rep,'pages':n,'physical_folios':len(folios),'tokens':len(names),'positive_cells':int(y.sum()),'baseline_bits':float(bl.sum()),'held_bits':float(ml[rep].sum()),'gain_bits':gain,'selector_paid_gain_bits':gain-math.log2(8),'positive_gain_tokens':sum(tobs[panel,name,rep]>0 for name in names),'positive_gain_folios':sum(v>0 for v in fg),'local_permutation_p':'PENDING','max_four_panel_p':'PENDING','max_eight_global_p':'PENDING','max_token_model_p':'PENDING'});obs[panel,rep]=gain
   for i,x in enumerate(pr):
    for j,name in enumerate(names):page_rows.append({'panel':panel,'page':x['page'],'physical_folio':x['physical_folio'],'currier':x['currier'],'token':name.split('_',1)[1].lower(),'representation':rep,'observed':int(y[i,j]),'nuisance_probability':float(bp[i,j]),'model_probability':float(pred[rep][i,j]),'gain_bits':float(bl[i,j]-ml[rep][i,j])})
 # Fixed cross-source sensitivity for the three exact shared tokens.
 shared=sorted(set(freeze['eligible_tokens']['ELV'])&set(freeze['eligible_tokens']['THP']));assert shared==['polygonum','primula','scabiosa'];cross_rows=[]
 for target,train in (('ELV','THP'),('THP','ELV')):
  pr,names,y,_,_,_,_,_,_,_=panel_cache[target];tr=[x for x in rows if x['panel']==train];tn=[f'{train}_{t.upper()}' for t in freeze['eligible_tokens'][train]];ty=np.array([[int(x[n]) for n in tn] for x in tr],float)
  for rep in REPS:
   predcols=[];basecols=[];obscols=[]
   for token in shared:
    j=[x.split('_',1)[1].lower() for x in names].index(token);k=[x.split('_',1)[1].lower() for x in tn].index(token);w=np.zeros((len(pr),len(tr)));b=np.zeros_like(w)
    for i,t in enumerate(pr):
     z=[]
     for q,s in enumerate(tr):
      if s['physical_folio']==t['physical_folio']:continue
      dn=dist(nuisance[target,t['page']],nuisance[train,s['page']]);z.append((dn+dist(formal[t['page']][rep],formal[s['page']][rep]),s['page'],q,dn))
     for d,_,q,_ in sorted(z)[:K]:w[i,q]=1/(.1+d)
     for _,_,q,d in sorted(z,key=lambda a:(a[3],a[1]))[:K]:b[i,q]=1/(.1+d)
    base=(b@ty[:,k]+.5)/(b.sum(1)+1);q=(w@ty[:,k]+SHRINK*base)/(w.sum(1)+SHRINK);basecols.append(base);predcols.append(q);obscols.append(y[:,j])
   yy=np.array(obscols).T;bb=np.array(basecols).T;qq=np.array(predcols).T;cross_rows.append({'target_panel':target,'training_panel':train,'representation':rep,'tokens':'|'.join(shared),'pages':len(pr),'baseline_bits':float(loss(yy,bb).sum()),'held_bits':float(loss(yy,qq).sum()),'gain_bits':float((loss(yy,bb)-loss(yy,qq)).sum())})
 # Complete-vector null, panel-specific strata; one shared max over all panels/models/tokens.
 local=Counter();max4=Counter();glob=0;tlocal=Counter();tmax=0;rng=np.random.default_rng(SEED)
 for world in range(WORLDS):
  wg={};wt=[]
  for panel in ('ELV','THP'):
   pr,names,y,bw,rw,_,_,_,_,_=panel_cache[panel];py=y.copy();strata=defaultdict(list)
   for i,x in enumerate(pr):strata[x['currier'],x['hand'],x['illustration_profile']].append(i)
   for idx in strata.values():idx=np.array(idx,int);py[idx]=py[rng.permutation(idx)]
   bp=(bw@py+.5)/(bw.sum(1)[:,None]+1);bl=loss(py,bp)
   for rep in REPS:
    q=(rw[rep]@py+SHRINK*bp)/(rw[rep].sum(1)[:,None]+SHRINK);m=loss(py,q);g=float((bl-m).sum());wg[panel,rep]=g;local[panel,rep]+=g>=obs[panel,rep]-1e-12
    for j,name in enumerate(names):v=float((bl[:,j]-m[:,j]).sum());tlocal[panel,name,rep]+=v>=tobs[panel,name,rep]-1e-12;wt.append(v)
  for panel in ('ELV','THP'):max4[panel]+=max(wg[panel,r] for r in REPS)>=max(obs[panel,r] for r in REPS)-1e-12
  glob+=max(wg.values())>=max(obs.values())-1e-12;tmax+=max(wt)>=max(tobs.values())-1e-12
 null_rows=[];gp=(glob+1)/(WORLDS+1);tp=(tmax+1)/(WORLDS+1)
 for panel in ('ELV','THP'):
  for rep in REPS:null_rows.append({'panel':panel,'representation':rep,'worlds':WORLDS,'seed':SEED,'observed_gain_bits':obs[panel,rep],'local_inclusive_p':(local[panel,rep]+1)/(WORLDS+1),'max_four_panel_inclusive_p':(max4[panel]+1)/(WORLDS+1),'max_eight_global_inclusive_p':gp,'max_token_model_inclusive_p':tp,'preserves':'SOURCE_PANEL;CURRIER;HAND;ILLUSTRATION_PROFILE;COMPLETE_TOKEN_VECTOR'})
 nm={(x['panel'],x['representation']):x for x in null_rows}
 for x in score_rows:z=nm[x['panel'],x['representation']];x.update({'local_permutation_p':z['local_inclusive_p'],'max_four_panel_p':z['max_four_panel_inclusive_p'],'max_eight_global_p':z['max_eight_global_inclusive_p'],'max_token_model_p':z['max_token_model_inclusive_p']})
 for x in token_rows:x['local_permutation_p']=(tlocal[x['panel'],x['panel']+'_'+x['token'].upper(),x['representation']]+1)/(WORLDS+1);x['max_token_model_p']=tp
 best={p:max((x for x in score_rows if x['panel']==p and x['representation'].startswith('PAGE_HOST')),key=lambda x:float(x['gain_bits'])) for p in ('ELV','THP')};allbest=max(score_rows,key=lambda x:float(x['gain_bits']));top=sorted(token_rows,key=lambda x:-float(x['gain_bits']))
 status='IDENTIFICATION_TOKEN_PAGE_HOST_ASSOCIATION_INTERESTING_EXPLORATORY' if any(float(x['selector_paid_gain_bits'])>0 and float(x['max_eight_global_p'])<=.1 for x in best.values()) else 'IDENTIFICATION_TOKEN_ASSOCIATION_WEAK_OR_CONFOUNDED'
 counter=[]
 for x in top[:10]:counter.append({'type':'TOP_TOKEN_LEAD','panel':x['panel'],'item':x['token'],'representation':x['representation'],'gain_bits':x['gain_bits'],'detail':'POSTSELECTED_NOISY_IDENTIFICATION_TOKEN'})
 for x in sorted(fold_rows,key=lambda x:float(x['gain_bits']))[:12]:counter.append({'type':'WORST_HELD_FOLIO','panel':x['panel'],'item':x['physical_folio'],'representation':x['representation'],'gain_bits':x['gain_bits'],'detail':'HELD_FOLIO_COUNTEREXAMPLE'})
 counter.extend([{'type':'SOURCE_DISAGREEMENT','panel':'ELV_VS_THP','item':'SHARED_THREE_TOKEN_SENSITIVITY','representation':'ALL','gain_bits':'SEE_CROSS_SOURCE','detail':'ELV and ThP are noisy nonindependent proposal systems; cross-source transfer is a sensitivity, not replication.'},{'type':'ABSENCE_CAVEAT','panel':'ALL','item':'ZERO_ENDPOINT','representation':'ALL','gain_bits':'NA','detail':'A zero means another head token was proposed, not botanical exclusion.'},{'type':'ALTERNATE_READING_SCOPE','panel':'ALL','item':'GDT062_HPR2_VIEW','representation':'ALL','gain_bits':'NA','detail':'One derived source-display view; no alternate-reading replication.'}])
 for x in cross_rows:
  if x['representation']=='PAGE_HOST_CHAR3':counter.append({'type':'CROSS_SOURCE_NONTRANSFER','panel':x['target_panel'],'item':x['tokens'],'representation':x['representation'],'gain_bits':x['gain_bits'],'detail':'Training on the other tentative-identification source does not reproduce the within-ELV PAGE_HOST lead.'})
 variants=[{'variant_id':'V00','status':'PRIMARY','description':'ELV and ThP panels separately; exact recurring head tokens only.'},{'variant_id':'V01','status':'RUN','description':'Exact PAGE_HOST and PAGE_HOST-char3 models.'},{'variant_id':'V02','status':'RUN_CONTROLS','description':'Raw-char3 and compiler-signature models.'},{'variant_id':'V03','status':'RUN_SENSITIVITY','description':'Three exact shared tokens trained across source panels.'},{'variant_id':'V04','status':'NOT_RUN','description':'No synonym merging, taxonomy repair, plant ID, English gloss, f84, language or translation search.'}]
 write(SCORE,clean(score_rows));write(TOKEN,clean(token_rows));write(FOLD,clean(fold_rows));write(PAGE,clean(page_rows));write(CROSS,clean(cross_rows));write(NULL,clean(null_rows));write(COUNTER,clean(counter));write(VARIANT,variants)
 REPORT.write_text(f"""# GDT139 — Herbal identification-token transfer\n\n## Outcome\n\n**{status}**\n\nThe frozen archive panel contains 81 ELV page rows with six recurring tokens and 92 ThP rows with thirteen.  ELV and ThP are separate noisy proposal systems, not replications.\n\nBest PAGE_HOST scores are ELV `{best['ELV']['representation']}` {float(best['ELV']['gain_bits']):+.3f} bits (selector-paid {float(best['ELV']['selector_paid_gain_bits']):+.3f}, local/max-panel/max-global p {float(best['ELV']['local_permutation_p']):.4f}/{float(best['ELV']['max_four_panel_p']):.4f}/{float(best['ELV']['max_eight_global_p']):.4f}) and ThP `{best['THP']['representation']}` {float(best['THP']['gain_bits']):+.3f} bits (selector-paid {float(best['THP']['selector_paid_gain_bits']):+.3f}, p {float(best['THP']['local_permutation_p']):.4f}/{float(best['THP']['max_four_panel_p']):.4f}/{float(best['THP']['max_eight_global_p']):.4f}). The complete family is led by `{allbest['panel']} / {allbest['representation']}` at {float(allbest['gain_bits']):+.3f} bits.\n\nStrongest token/model diagnostics are {', '.join(x['panel']+':'+x['token']+' '+format(float(x['gain_bits']),'+.2f') for x in top[:5])}. They are postselected hypotheses with a shared max-token/model p of {float(top[0]['max_token_model_p']):.4f}, not plant-name readings. The three exact shared tokens (`polygonum`, `primula`, `scabiosa`) fail to transfer across source panels: PAGE_HOST-char3 gains are {float(next(x for x in cross_rows if x['target_panel']=='ELV' and x['representation']=='PAGE_HOST_CHAR3')['gain_bits']):+.3f} bits into ELV and {float(next(x for x in cross_rows if x['target_panel']=='THP' and x['representation']=='PAGE_HOST_CHAR3')['gain_bits']):+.3f} into ThP.\n\nNuisance matching includes the twelve inherited visible-feature tags, Currier, hand, illustration profile, and page layout. Thus any remaining lead asks whether formal texture adds information beyond those coarse visible descriptions; it cannot repair erroneous or correlated catalogue guesses. A zero endpoint is not a botanical negative. The GDT062 inventory is one derived source-display view, so no ZL/IT/RF replication is claimed. All f84 rows were rejected before retention and no new f84r access occurred. No plant identification, semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation is assigned.\n""",encoding='utf8')
 result={'schema':'GDT139_HERBAL_IDENTIFICATION_TOKEN_TRANSFER_RESULT_V1','status':status,'panels':freeze['panels'],'eligible_tokens':freeze['eligible_tokens'],'best_page_host_by_panel':best,'family_best':allbest,'strongest_token_diagnostics':top[:10],'shared_cross_source_tokens':shared,'cross_source_scores':cross_rows,'outcome_caveat':freeze['outcome_caveat'],'alternate_reading_sensitivity':'NOT_AVAILABLE_FOR_DERIVED_GDT062_HPR2_PAGE_BAGS;NO_REPLICATION_CLAIM','interpretation':'Noisy published identification-head tokens versus whole-page formal inventories after visible-feature and metadata nuisance control.','claim_ceiling':freeze['claim_ceiling'],'f84':{'all_rows_rejected_before_retention':True,'new_f84r_access':False},'inputs':{p.name:sha(p) for p in (SOURCE,INVENTORY,FREEZE,R/'gdt137_result.json')},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{p.name:sha(p) for p in (SCORE,TOKEN,FOLD,PAGE,CROSS,NULL,COUNTER,VARIANT)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8');print(json.dumps({'status':status,'best':{k:(v['representation'],v['gain_bits']) for k,v in best.items()},'family_best':(allbest['panel'],allbest['representation'],allbest['gain_bits'])},sort_keys=True))
if __name__=='__main__':main()
