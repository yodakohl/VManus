#!/usr/bin/env python3
"""GDT133: post-hoc decomposition of GDT132 raw-minus-PAGE_HOST transfer."""
from __future__ import annotations
import csv,hashlib,json,random
from collections import defaultdict
from pathlib import Path
import numpy as np
import run_gdt114_q20_record_template_linkage as h
import run_gdt131_q20_cross_line_field_onset as q
import run_gdt132_cross_register_continuation_arity as g

ROOT=Path(__file__).resolve().parent;METHOD=ROOT/'GDT133_RAW_SURFACE_TRANSFER_DECOMPOSITION_METHOD.md';REPORT=ROOT/'GDT133_RAW_SURFACE_TRANSFER_DECOMPOSITION_REPORT.md'
SCORES=ROOT/'gdt133_transfer_decomposition_scores.tsv';FOLDS=ROOT/'gdt133_transfer_decomposition_folds.tsv';SECTIONS=ROOT/'gdt133_transfer_decomposition_sections.tsv';NESTED=ROOT/'gdt133_transfer_decomposition_nested.tsv';BLOCKS=ROOT/'gdt133_transfer_decomposition_blocks.tsv';NULL=ROOT/'gdt133_transfer_decomposition_null.tsv';VARIANTS=ROOT/'gdt133_variant_log.tsv';COUNTER=ROOT/'gdt133_transfer_decomposition_counterexamples.tsv';RESULT=ROOT/'gdt133_result.json'
MODES=('HOST_CHAR3','RAW_CHAR3','COMPILER12','EDGE29','FACTORED','FACTORED_PLUS_RAW');WORLDS=4096
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def seed(*v):return int(hashlib.sha256('|'.join(map(str,v)).encode()).hexdigest()[:16],16)
def write(p,rows):
 keys=[]
 for r in rows:
  for k in r:
   if k not in keys:keys.append(k)
 with Path(p).open('w',encoding='utf-8',newline='') as out:w=csv.DictWriter(out,fieldnames=keys,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def cells(last):return [(x['wrapper'],x['frame'],x['right'],x['inner_d'],x['dy'],x['b3']) for x in last]
def primitive(last):
 host=q.hvec([x['page_host'] for x in last]);raw=q.hvec([x['token'] for x in last]);compiler=q.compiler(cells(last));edge=h.edge_vec(last)
 return {'HOST_CHAR3':host,'RAW_CHAR3':raw,'COMPILER12':compiler,'EDGE29':edge,'FACTORED':np.r_[host,compiler,edge],'FACTORED_PLUS_RAW':np.r_[host,compiler,edge,raw]}
def training():
 rows=[r for r in q.load() if r['edition']=='ZL3b'];atlas=q.read(q.FIELDS);X0=[];Y=[];R={m:[] for m in MODES}
 for r in rows:
  inv=[x for x in atlas if x['edition']=='ZL3b' and x['page']==r['page'] and int(x['star_ordinal'])==r['star_ordinal'] and x['record_scope']=='OPEN'];inv.sort(key=lambda x:(int(x['line_depth']),int(x['field_index'])));groups=[]
  for f in inv:
   cs=q.parse_cells(f);ts=f['group_tokens'].split('|');hs=f['page_hosts'].split('|');groups.extend({'token':t,'page_host':p,'wrapper':c[0],'frame':c[1],'right':c[2],'inner_d':c[3],'dy':c[4],'b3':c[5]} for c,t,p in zip(cs,ts,hs))
  last=g.fields(groups)[-1];X0.append(g.ref(groups,last,r['open_member_count']));Y.append(g.count_vec(len(r['first_cells'])));z=primitive(last)
  for m in MODES:R[m].append(z[m])
 return np.vstack(X0),np.vstack(Y),{m:np.vstack(v) for m,v in R.items()}
def main():
 base=json.loads((ROOT/'gdt132_result.json').read_text());assert base['target_pairs']==31;X,Y,R=training();target=g.external();assert len(target)==31 and not any('f84r' in json.dumps(r) for r in target)
 T0=np.vstack([g.ref(r['groups'],r['last'],r['member_count']) for r in target]);TY=np.vstack([g.count_vec(len(r['target'])) for r in target]);rows=[primitive(r['last']) for r in target];TR={m:np.vstack([z[m] for z in rows]) for m in MODES}
 x,tx,xmu,xsd=q.standardize(X,T0);y,ty,ymu,ysd=q.standardize(Y,TY);b0=q.fit(x,y);p0=q.predict(tx,b0);models={};pred={};testrep={}
 for m in MODES:
  a,ta,mu,sd=q.standardize(R[m],TR[m]);models[m]=(q.fit(np.c_[x,a],y),mu,sd);testrep[m]=ta;pred[m]=q.predict(np.c_[tx,ta],models[m][0])
 actual=np.argmax(TY,axis=1);rank0=np.argsort(-(p0*ysd+ymu),axis=1);scores=[];folds=[];sects=[]
 for m in MODES:
  rank=np.argsort(-(pred[m]*ysd+ymu),axis=1);gain=q.bits(ty,p0,pred[m])
  for f in sorted({r['physical_folio'] for r in target}):
   ix=[i for i,r in enumerate(target) if r['physical_folio']==f];z=q.bits(ty[ix],p0[ix],pred[m][ix]);folds.append({'model':m,'physical_folio':f,'pairs':len(ix),'gain_bits':z,'positive':int(z>0)})
  for s in sorted({r['section'] for r in target}):
   ix=[i for i,r in enumerate(target) if r['section']==s];sects.append({'model':m,'scope':'SECTION','held_or_scored_section':s,'pairs':len(ix),'gain_bits':q.bits(ty[ix],p0[ix],pred[m][ix])})
   ix=[i for i,r in enumerate(target) if r['section']!=s];sects.append({'model':m,'scope':'LEAVE_SECTION_OUT','held_or_scored_section':s,'pairs':len(ix),'gain_bits':q.bits(ty[ix],p0[ix],pred[m][ix])})
  scores.append({'model':m,'gain_bits':gain,'positive_folios':sum(r['positive'] for r in folds if r['model']==m),'physical_folios':24,'reference_top1':sum(actual[i] in rank0[i,:1] for i in range(31)),'model_top1':sum(actual[i] in rank[i,:1] for i in range(31)),'reference_top3':sum(actual[i] in rank0[i,:3] for i in range(31)),'model_top3':sum(actual[i] in rank[i,:3] for i in range(31))})
 nested=[{'contrast':'COMPILER12_MINUS_REFERENCE','gain_bits':q.bits(ty,p0,pred['COMPILER12'])},{'contrast':'EDGE29_MINUS_REFERENCE','gain_bits':q.bits(ty,p0,pred['EDGE29'])},{'contrast':'FACTORED_MINUS_HOST_CHAR3','gain_bits':q.bits(ty,pred['HOST_CHAR3'],pred['FACTORED'])},{'contrast':'FACTORED_PLUS_RAW_MINUS_FACTORED','gain_bits':q.bits(ty,pred['FACTORED'],pred['FACTORED_PLUS_RAW'])},{'contrast':'RAW_CHAR3_MINUS_REFERENCE','gain_bits':q.bits(ty,p0,pred['RAW_CHAR3'])}]
 bc=models['COMPILER12'][0];ta=testrep['COMPILER12'];blocks=[]
 for name,ix in {'WRAPPER7':range(0,7),'FRAME2':range(7,9),'RENDERER3':range(9,12)}.items():
  zero=ta.copy();zero[:,list(ix)]=0;pp=q.predict(np.c_[tx,zero],bc);blocks.append({'block':name,'full_minus_block_zeroed_bits':q.bits(ty,pp,pred['COMPILER12']),'interpretation':'DESCRIPTIVE_Q20_MEAN_ZEROING_NOT_SEPARATE_TEST'})
 strata=defaultdict(list)
 for i,r in enumerate(target):strata[(r['section'],r['currier'],r['hand'],str(len(r['groups'])) if len(r['groups'])<10 else '10PLUS')].append(i)
 rng=random.Random(seed('GDT133','NULL'));world={m:[] for m in MODES};mx=[]
 for _ in range(WORLDS):
  a=list(range(31))
  for ids in strata.values():
   if len(ids)>1:
    z=ids[:];rng.shuffle(z)
    for i,j in zip(ids,z):a[i]=j
  vals={}
  for m in MODES:
   b,mu,sd=models[m];pp=q.predict(np.c_[tx,(TR[m][a]-mu)/sd],b);vals[m]=q.bits(ty,p0,pp);world[m].append(vals[m])
  mx.append(max(vals.values()))
 null=[];smap={r['model']:r for r in scores}
 for m in MODES:
  t=smap[m]['gain_bits'];lp=(1+sum(v>=t-1e-12 for v in world[m]))/(WORLDS+1);mp=(1+sum(v>=t-1e-12 for v in mx))/(WORLDS+1);smap[m].update({'local_p':lp,'max_six_p':mp,'null_mean_bits':float(np.mean(world[m]))});null.append({'model':m,'worlds':WORLDS,'true_gain_bits':t,'null_mean_bits':float(np.mean(world[m])),'local_p':lp,'max_six_p':mp})
 best=max(scores,key=lambda r:r['gain_bits']);status='RAW_CONTROL_POSTHOC_RESIDUAL_SURFACE_LEAD_ONLY' if best['model']=='RAW_CHAR3' and best['gain_bits']>0 else 'RAW_CONTROL_NOT_STABLE_UNDER_FACTORED_DECOMPOSITION'
 initial={'HOST_CHAR3':-4.153103496116,'RAW_CHAR3':1.292807288838,'COMPILER12_WITH_LENGTH':0.654319334518,'ORDERED_COMPILER_HASH32':2.667738850086,'AFFIX_SIGNATURE_HASH32':0.682786015744,'RAW_EDGE_HASH32':0.601261244591,'HOST_EDGE_HASH32':-1.373469974429};variants=[{'variant_id':'INITIAL_'+m,'status':'SUPERSEDED_POSTHOC_DIAGNOSTIC','observed_gain_bits':v,'detail':'First pass invented edge/ordered signatures after exposure; retained only as tried-variant disclosure.'} for m,v in initial.items()]+[{'variant_id':'REVISED_'+m,'status':'RUN_AFTER_INDEPENDENT_DESIGN_AUDIT','observed_gain_bits':smap[m]['gain_bits'],'detail':'Inherited/factored fixed decomposition in final result.'} for m in MODES]
 counter=[{'counterexample':'PAGE_HOST_TRANSFER','detail':f"{smap['HOST_CHAR3']['gain_bits']:+.6f} bits"},{'counterexample':'RAW_TOP1','detail':f"{smap['RAW_CHAR3']['model_top1']} versus reference {smap['RAW_CHAR3']['reference_top1']}"},{'counterexample':'TARGET_BIN_SKEW','detail':'24/31 targets are 4+; H is 19/20 4+, C is 2/2 two, P is 1/1 one.'},{'counterexample':'OPPORTUNITY_MATCHED_NULL','detail':'GDT132 capacity 20/15/4/0; max-six p is coarse and post-hoc.'},{'counterexample':'F84_PROVENANCE','detail':'Limited audit-only exposure disclosed by GDT132; zero final input rows and no further access.'}]
 fmt=lambda rows:[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in r.items()} for r in rows];write(SCORES,fmt(scores));write(FOLDS,fmt(folds));write(SECTIONS,fmt(sects));write(NESTED,fmt(nested));write(BLOCKS,fmt(blocks));write(NULL,fmt(null));write(VARIANTS,variants);write(COUNTER,counter)
 lines=['# GDT133 — raw-surface transfer decomposition','','Status: **'+status+'**','','This is a post-hoc decomposition of the exposed corrected GDT132 panel, not a replication. All tried variants are logged.','','| representation | gain bits | positive folios | top-1 | top-3 | local p | max-6 p |','|---|---:|---:|---:|---:|---:|---:|']
 for r in sorted(scores,key=lambda z:-z['gain_bits']):lines.append(f"| `{r['model']}` | {r['gain_bits']:+.3f} | {r['positive_folios']}/24 | {r['model_top1']}/31 | {r['model_top3']}/31 | {r['local_p']:.4f} | {r['max_six_p']:.4f} |")
 lines+=['',f"The largest fixed decomposition remains raw token trigrams at {best['gain_bits']:+.3f} bits (max-six p={best['max_six_p']:.4f}), but top-1 is unchanged and only {best['positive_folios']}/{best['physical_folios']} folios are positive. COMPILER12 is {next(x['gain_bits'] for x in nested if x['contrast']=='COMPILER12_MINUS_REFERENCE'):+.3f} bits with no corrected lead; FACTORED minus HOST is {next(x['gain_bits'] for x in nested if x['contrast']=='FACTORED_MINUS_HOST_CHAR3'):+.3f}; adding RAW after FACTORED is {next(x['gain_bits'] for x in nested if x['contrast']=='FACTORED_PLUS_RAW_MINUS_FACTORED'):+.3f}, yet FACTORED_PLUS_RAW remains negative overall. The exposed trace therefore localizes only to uninterpreted residual source-string texture, not to an HPR2 compiler or PAGE_HOST edge layer. Its p-value is coarse, post-hoc, and not opportunity-length matched.",'','No heading, recipe, transferable record semantics, content-bearing layer, semantic role, word, morpheme, POS, sound, language, plaintext, meaning, or translation is inferred. Limited f84 audit exposure remains disclosed; all final GDT133 inputs are f84-free and no further f84 access occurred.'];REPORT.write_text('\n'.join(lines)+'\n')
 result={'schema':'GDT133_RAW_SURFACE_TRANSFER_DECOMPOSITION_RESULT_V1','status':status,'panel':'PUBLIC_CORRECTED_GDT132_31_PAIRS','scores':scores,'nested_contrasts':nested,'compiler_blocks':blocks,'best_model':best['model'],'interpretation':'Post-hoc decomposition leaves only a small uninterpreted residual raw-string lead; HPR2 compiler and PAGE_HOST-edge blocks do not explain it transferably.','claim_ceiling':'Formal transfer texture only; no heading, recipe, transferable record semantics, content-bearing layer, semantic role, word, morpheme, POS, sound, language, plaintext, meaning, or translation.','f84r':{'new_access':False,'actual_inputs_contain_rows':False,'prior_limited_audit_exposure_inherited':True},'inputs':{n:sha(ROOT/n) for n in ('gdt132_result.json','gdt132_source_seal_correction.json','gdt132_continuation_arity_inventory.tsv','gdt016_group_state_inventory.tsv','gdt046_line_frames.tsv','gdt127_q20_field_inventory.tsv','q20ob001_source_panel.tsv')},'implementation':{Path(__file__).name:sha(Path(__file__)),'run_gdt132_cross_register_continuation_arity.py':sha(ROOT/'run_gdt132_cross_register_continuation_arity.py'),'run_gdt131_q20_cross_line_field_onset.py':sha(ROOT/'run_gdt131_q20_cross_line_field_onset.py'),'run_gdt114_q20_record_template_linkage.py':sha(ROOT/'run_gdt114_q20_record_template_linkage.py')},'outputs':{p.name:sha(p) for p in (SCORES,FOLDS,SECTIONS,NESTED,BLOCKS,NULL,VARIANTS,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'best':best,'nested':nested},sort_keys=True))
if __name__=='__main__':main()
