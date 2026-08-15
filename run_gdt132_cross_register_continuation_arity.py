#!/usr/bin/env python3
"""GDT132: transfer the Q20 continuation-arity lead outside section S."""
from __future__ import annotations
import csv,hashlib,json,math,random,re
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
import run_gdt131_q20_cross_line_field_onset as q
from run_gdt012_core_semantic_atlas import strip_layers
from run_gdt062_right_family_register_renderer import parser as hpr2_parser

ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/'gdt016_group_state_inventory.tsv';FRAMES=ROOT/'gdt046_line_frames.tsv';FREEZE=ROOT/'gdt132_prediction.json';CORRECTION=ROOT/'gdt132_source_seal_correction.json'
METHOD=ROOT/'GDT132_CROSS_REGISTER_CONTINUATION_ARITY_METHOD.md';REPORT=ROOT/'GDT132_CROSS_REGISTER_CONTINUATION_ARITY_REPORT.md';INVENTORY=ROOT/'gdt132_continuation_arity_inventory.tsv';PRED=ROOT/'gdt132_continuation_arity_predictions.tsv';FOLDS=ROOT/'gdt132_continuation_arity_folds.tsv';SCORES=ROOT/'gdt132_continuation_arity_scores.tsv';NULL=ROOT/'gdt132_continuation_arity_null.tsv';COUNTER=ROOT/'gdt132_continuation_arity_counterexamples.tsv';RESULT=ROOT/'gdt132_result.json'
MODES=('LAST_HOST_CHAR3_HASH32','LAST_RAW_CHAR3_HASH32');Q20_FOLIOS={'f104','f105','f106','f107','f112','f113','f114','f115'};SECTIONS={'H','B','P','T','C'};WORLDS=4096
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def plain(v):
 if isinstance(v,np.generic):return v.item()
 if isinstance(v,dict):return {k:plain(x) for k,x in v.items()}
 if isinstance(v,list):return [plain(x) for x in v]
 return v
def seed(*v):return int(hashlib.sha256('|'.join(map(str,v)).encode()).hexdigest()[:16],16)
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 keys=[]
 for r in rows:
  for k in r:
   if k not in keys:keys.append(k)
 with Path(p).open('w',encoding='utf-8',newline='') as h:w=csv.DictWriter(h,fieldnames=keys,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def count_vec(n):return np.array([n==1,n==2,n==3,n>=4],float)
def fields(groups):
 out=[];cur=[]
 for g in groups:
  cur.append(g)
  if g['dy']:out.append(cur);cur=[]
 if cur:out.append(cur)
 return out
def parsed(rows,parse):
 out=[]
 for r in rows:
  pref,resid,dy=strip_layers(r['token']);host,b3,right,inner,frame=parse({'residual_host':resid,'stripped_prefix':pref});assert int(dy)==int(r['dy_closure'])
  out.append({'token':r['token'],'page_host':host,'wrapper':pref,'frame':frame,'right':right,'inner_d':int(inner),'dy':int(dy),'b3':int(b3)})
 return out
def ref(groups,last,member_count):return np.r_[len(groups),member_count,len(last),sum(len(x['page_host']) for x in last),sum(len(x['token']) for x in last),q.compiler([(x['wrapper'],x['frame'],x['right'],x['inner_d'],x['dy'],x['b3']) for x in groups])]
def rep(last,mode):return q.hvec([x['page_host'] for x in last] if mode.startswith('LAST_HOST') else [x['token'] for x in last])
def numeric(loc):
 m=re.match(r'^(.*)\.(\d+)$',loc);return (m.group(1),int(m.group(2))) if m else None

def external():
 raw=read(SOURCE);parse,_=hpr2_parser(raw);by=defaultdict(list)
 for r in raw:
  if r['section'] not in SECTIONS or r['physical_folio'] in Q20_FOLIOS or r['page'].startswith('f84r') or r['locus'].startswith('f84r'):continue
  by[r['locus']].append(r)
 complete={}
 for loc,z in by.items():
  z.sort(key=lambda r:int(r['group_index']));n=int(z[0]['group_count'])
  if len(z)==n and [int(r['group_index']) for r in z]==list(range(1,n+1)):complete[loc]=z
 frame={r['locus']:r for r in read(FRAMES)}
 out=[]
 for loc,z in complete.items():
  if frame.get(loc,{}).get('paragraph_start')!='1':continue
  pos=numeric(loc)
  if not pos:continue
  nxt=f'{pos[0]}.{pos[1]+1}'
  if nxt not in complete or frame.get(nxt,{}).get('paragraph_start')!='0':continue
  a=parsed(z,parse);b=parsed(complete[nxt],parse);af=fields(a);bf=fields(b);assert af and bf
  member_count=sum(len(r['family_surface']) for r in z)
  out.append({'locus':loc,'next_locus':nxt,'page':z[0]['page'],'physical_folio':z[0]['physical_folio'],'section':z[0]['section'],'currier':z[0]['currier'],'hand':z[0]['hand'],'groups':a,'last':af[-1],'target':bf[0],'member_count':member_count})
 assert out and not any('f84r' in json.dumps(r) for r in out)
 return sorted(out,key=lambda r:(r['physical_folio'],r['page'],numeric(r['locus'])[1]))

def main():
 freeze=json.loads(FREEZE.read_text());assert freeze['status']=='FROZEN_BEFORE_EXTERNAL_TARGET_PAIR_ENUMERATION'
 correction=json.loads(CORRECTION.read_text());assert correction['status']=='POST_EXPOSURE_INPUT_SEAL_CORRECTION_BEFORE_FINAL_RESCORING'
 # Rebuild transferable Q20 features from the GDT131 source-bound records.
 tr=q.load();tr=[r for r in tr if r['edition']=='ZL3b'];X0=[];Xa={m:[] for m in MODES};Y=[]
 for r in tr:
  # The OPEN groups are recovered from the GDT127 atlas through q.load().
  inv=[x for x in q.read(q.FIELDS) if x['edition']=='ZL3b' and x['page']==r['page'] and int(x['star_ordinal'])==r['star_ordinal'] and x['record_scope']=='OPEN']
  inv.sort(key=lambda x:(int(x['line_depth']),int(x['field_index'])));allcells=[];allgroups=[]
  for f in inv:
   cells=q.parse_cells(f);tokens=f['group_tokens'].split('|');hosts=f['page_hosts'].split('|');assert len(cells)==len(tokens)==len(hosts)
   allgroups.extend({'token':t,'page_host':h,'wrapper':c[0],'frame':c[1],'right':c[2],'inner_d':c[3],'dy':c[4],'b3':c[5]} for c,t,h in zip(cells,tokens,hosts));allcells.extend(cells)
  last=fields(allgroups)[-1];X0.append(ref(allgroups,last,r['open_member_count']));Y.append(count_vec(len(r['first_cells'])))
  for m in MODES:Xa[m].append(rep(last,m))
 X0=np.vstack(X0);Y=np.vstack(Y);Xa={m:np.vstack(v) for m,v in Xa.items()};x0,_,xmu,xsd=q.standardize(X0,X0);yt,_,ymu,ysd=q.standardize(Y,Y);b0=q.fit(x0,yt);models={m:q.fit(np.c_[x0,q.standardize(Xa[m],Xa[m])[0]],yt) for m in MODES};amu={m:q.standardize(Xa[m],Xa[m])[2:] for m in MODES}
 target=external();T0=np.vstack([ref(r['groups'],r['last'],r['member_count']) for r in target]);TY=np.vstack([count_vec(len(r['target'])) for r in target]);tx=(T0-xmu)/xsd;ty=(TY-ymu)/ysd;p0=q.predict(tx,b0);TP={}
 for m in MODES:
  mu,sd=amu[m];TP[m]=q.predict(np.c_[tx,(np.vstack([rep(r['last'],m) for r in target])-mu)/sd],models[m])
 scores=[];predrows=[];folds=[];nullrows=[]
 for m in MODES:
  gain=q.bits(ty,p0,TP[m]);top0=np.argmax(p0*ysd+ymu,axis=1);top=np.argmax(TP[m]*ysd+ymu,axis=1);actual=np.argmax(TY,axis=1)
  rank0=np.argsort(-(p0*ysd+ymu),axis=1);rank=np.argsort(-(TP[m]*ysd+ymu),axis=1)
  for i,r in enumerate(target):predrows.append({'model':m,'locus':r['locus'],'next_locus':r['next_locus'],'page':r['page'],'physical_folio':r['physical_folio'],'section':r['section'],'currier':r['currier'],'hand':r['hand'],'source_group_count':len(r['groups']),'last_field_group_count':len(r['last']),'actual_next_field_count_bin':('1','2','3','4+')[actual[i]],'reference_predicted_bin':('1','2','3','4+')[top0[i]],'model_predicted_bin':('1','2','3','4+')[top[i]],'reference_hit':int(top0[i]==actual[i]),'model_hit':int(top[i]==actual[i]),'reference_top3_hit':int(actual[i] in rank0[i,:3]),'model_top3_hit':int(actual[i] in rank[i,:3])})
  for f in sorted({r['physical_folio'] for r in target}):
   ix=[i for i,r in enumerate(target) if r['physical_folio']==f];folds.append({'model':m,'physical_folio':f,'pairs':len(ix),'gain_bits':q.bits(ty[ix],p0[ix],TP[m][ix]),'positive_gain':int(q.bits(ty[ix],p0[ix],TP[m][ix])>0)})
  scores.append({'model':m,'target_pairs':len(target),'physical_folios':len({r['physical_folio'] for r in target}),'gain_bits':gain,'positive_folios':sum(int(r['positive_gain']) for r in folds if r['model']==m),'reference_top1':sum(top0==actual),'model_top1':sum(top==actual),'reference_top3':sum(actual[i] in rank0[i,:3] for i in range(len(target))),'model_top3':sum(actual[i] in rank[i,:3] for i in range(len(target)))})
 # Target-side fixed-model permutations.
 rng=random.Random(seed('GDT132','TARGET_NULL'));world={m:[] for m in MODES};mx=[];strata=defaultdict(list)
 for i,r in enumerate(target):strata[(r['section'],r['currier'],r['hand'],str(len(r['groups'])) if len(r['groups'])<10 else '10PLUS')].append(i)
 capacity=sum(len(v) for v in strata.values() if len(v)>1)
 opportunity_capacity=[]
 for level in range(4):
  matched=defaultdict(list)
  for i,r in enumerate(target):
   key=[r['section'],r['currier'],r['hand'],str(len(r['groups'])) if len(r['groups'])<10 else '10PLUS']
   if level>=1:key.append(len(r['last']))
   if level>=2:key.append(sum(len(x['page_host']) for x in r['last']))
   if level>=3:key.append(sum(len(x['token']) for x in r['last']))
   matched[tuple(key)].append(i)
  opportunity_capacity.append(sum(len(v) for v in matched.values() if len(v)>1))
 rawrep={m:np.vstack([rep(r['last'],m) for r in target]) for m in MODES}
 for _ in range(WORLDS):
  a=list(range(len(target)))
  for ids in strata.values():
   if len(ids)>1:
    z=ids[:];rng.shuffle(z)
    for i,j in zip(ids,z):a[i]=j
  vals={}
  for m in MODES:
   mu,sd=amu[m];p=q.predict(np.c_[tx,(rawrep[m][a]-mu)/sd],models[m]);vals[m]=q.bits(ty,p0,p);world[m].append(vals[m])
  mx.append(max(vals.values()))
 smap={r['model']:r for r in scores}
 for m in MODES:
  t=float(smap[m]['gain_bits']);local=(1+sum(x>=t-1e-12 for x in world[m]))/(WORLDS+1);maxp=(1+sum(x>=t-1e-12 for x in mx))/(WORLDS+1);smap[m].update({'swappable_pairs':capacity,'null_mean_bits':float(np.mean(world[m])),'local_p':local,'max_two_p':maxp});nullrows.append({'model':m,'worlds':WORLDS,'true_gain_bits':t,'null_mean_bits':float(np.mean(world[m])),'null_q95_bits':float(np.quantile(world[m],.95)),'local_p':local,'max_two_p':maxp})
 host=smap['LAST_HOST_CHAR3_HASH32'];raw=smap['LAST_RAW_CHAR3_HASH32'];gates={'host_gain_positive':host['gain_bits']>0,'host_beats_raw':host['gain_bits']>raw['gain_bits'],'majority_folios_positive':host['positive_folios']>host['physical_folios']/2,'max_two_p_le_005':host['max_two_p']<=.05};status='CROSS_REGISTER_CONTINUATION_ARITY_TRANSFER_SUPPORTED' if all(gates.values()) else 'Q20_CONTINUATION_ARITY_DOES_NOT_TRANSFER_OUTSIDE_SECTION_S'
 invrows=[{'locus':r['locus'],'next_locus':r['next_locus'],'page':r['page'],'physical_folio':r['physical_folio'],'section':r['section'],'currier':r['currier'],'hand':r['hand'],'source_group_count':len(r['groups']),'source_member_count':r['member_count'],'last_field_group_count':len(r['last']),'last_field_tokens':'|'.join(x['token'] for x in r['last']),'last_field_hosts':'|'.join(x['page_host'] for x in r['last']),'next_first_field_group_count':len(r['target']),'next_first_field_tokens':'|'.join(x['token'] for x in r['target']),'selection_state':'MECHANICAL_POST_FREEZE'} for r in target]
 counter=[{'counterexample':'RAW_STRING_CONTROL','detail':f"raw_gain={raw['gain_bits']:+.6f};host_gain={host['gain_bits']:+.6f}"},{'counterexample':'OPPORTUNITY_MATCHED_NULL_CAPACITY','detail':f"coarse={opportunity_capacity[0]};plus_field_groups={opportunity_capacity[1]};plus_host_length={opportunity_capacity[2]};plus_raw_length={opportunity_capacity[3]}"},{'counterexample':'WEAKEST_HOST_FOLIO','detail':min((r for r in folds if r['model']=='LAST_HOST_CHAR3_HASH32'),key=lambda r:float(r['gain_bits']))['physical_folio']},{'counterexample':'GDT131_EXACT_FORMULA_ZERO_HITS','detail':'20 held ZL exact predictions, zero hits.'}]
 write(INVENTORY,invrows);write(PRED,predrows);write(FOLDS,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in r.items()} for r in folds]);write(SCORES,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in r.items()} for r in scores]);write(NULL,[{k:(f'{v:.12f}' if isinstance(v,float) else v) for k,v in r.items()} for r in nullrows]);write(COUNTER,counter)
 report=f'''# GDT132 — cross-register continuation-arity transfer\n\nStatus: **{status}**\n\nThe corrected post-freeze mechanical panel contains {len(target)} paragraph-start -> immediate-next-line pairs on {host['physical_folios']} physical folios outside section S and every Q20 training folio.\n\n## Source-seal correction\n\nThe original prediction was public before target enumeration, but its declared whole-manuscript separator input contained sealed f84r rows. A first local 32-pair run parsed that table before filtering; no f84 row was printed, displayed to the analyst, retained, joined, or scored. Before publication, `gdt132_source_seal_correction.json` replaced it with the pre-existing f84-free `gdt046_line_frames.tsv`. This post-exposure correction is not presented as a pristine second freeze. One pair, f78v.1 -> f78v.2, is absent from the replacement complete-line frame and was excluded, leaving {len(target)} pairs. Both actual final source inputs contain zero f84r rows.\n\n| model | gain bits | positive folios | top-1 vs reference | top-3 vs reference | local p | max-2 p |\n|---|---:|---:|---:|---:|---:|---:|\n| `LAST_HOST_CHAR3_HASH32` | {host['gain_bits']:+.3f} | {host['positive_folios']}/{host['physical_folios']} | {host['model_top1']}/{len(target)} vs {host['reference_top1']}/{len(target)} | {host['model_top3']}/{len(target)} vs {host['reference_top3']}/{len(target)} | {host['local_p']:.4f} | {host['max_two_p']:.4f} |\n| `LAST_RAW_CHAR3_HASH32` | {raw['gain_bits']:+.3f} | {raw['positive_folios']}/{raw['physical_folios']} | {raw['model_top1']}/{len(target)} vs {raw['reference_top1']}/{len(target)} | {raw['model_top3']}/{len(target)} vs {raw['reference_top3']}/{len(target)} | {raw['local_p']:.4f} | {raw['max_two_p']:.4f} |\n\nFrozen gates: `{json.dumps(gates,sort_keys=True)}`. The stripped PAGE_HOST lead does not transfer. The raw-string control changes the score by {raw['gain_bits']:+.3f} bits, changes top-1 from {raw['reference_top1']} to {raw['model_top1']} and top-3 from {raw['reference_top3']} to {raw['model_top3']}, is positive on {raw['positive_folios']}/{raw['physical_folios']} folios, and was not the frozen semantic-layer prediction. It is a string-locality diagnostic, not a rescued PAGE_HOST transfer result.\n\nThe permutation null is deliberately coarse. It has {opportunity_capacity[0]} swappable pairs under the frozen section/Currier/hand/source-count strata, falling to {opportunity_capacity[1]}, {opportunity_capacity[2]}, and {opportunity_capacity[3]} after additionally matching final-field group count, PAGE_HOST length, and raw length. Its p-values are exploratory model-adjusted diagnostics, not exact opportunity-length-matched tests.\n\nThe test concerns formal continuation extent only. No heading, recipe, semantic role, object, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation is inferred. f84r remains analyst-sealed and is absent from every actual final input and output.\n''';REPORT.write_text(report,encoding='utf-8')
 result={'schema':'GDT132_CROSS_REGISTER_CONTINUATION_ARITY_RESULT_V1','status':status,'target_pairs':len(target),'physical_folios':host['physical_folios'],'sections':sorted({r['section'] for r in target}),'scores':scores,'gates':gates,'source_seal_correction':{'status':correction['status'],'sha256':sha(CORRECTION),'post_exposure':True,'superseded_target_pairs':correction['superseded_prepublication_run']['target_pairs'],'excluded_pair_after_replacement':'f78v.1->f78v.2'},'null_opportunity_capacity':{'coarse_frozen_strata':opportunity_capacity[0],'plus_final_field_group_count':opportunity_capacity[1],'plus_page_host_length':opportunity_capacity[2],'plus_raw_length':opportunity_capacity[3]},'interpretation':'Prospective Q20-trained final-field PAGE_HOST prediction of next-line first-field extent outside section S. The PAGE_HOST transfer failed; raw-string behavior remains an exploratory locality diagnostic only.','claim_ceiling':'Formal cross-register next-field extent only; no heading, recipe, semantic role, object, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.','f84r':{'analyst_payload_exposed':False,'retained':False,'joined':False,'scored':False,'targeted':False,'actual_final_inputs_contain_rows':False},'inputs':{SOURCE.name:sha(SOURCE),FRAMES.name:sha(FRAMES),FREEZE.name:sha(FREEZE),CORRECTION.name:sha(CORRECTION),'gdt131_result.json':sha(ROOT/'gdt131_result.json'),'gdt127_q20_field_inventory.tsv':sha(ROOT/'gdt127_q20_field_inventory.tsv'),'q20ob001_source_panel.tsv':sha(ROOT/'q20ob001_source_panel.tsv')},'implementation':{Path(__file__).name:sha(Path(__file__)),'run_gdt131_q20_cross_line_field_onset.py':sha(ROOT/'run_gdt131_q20_cross_line_field_onset.py'),'run_gdt012_core_semantic_atlas.py':sha(ROOT/'run_gdt012_core_semantic_atlas.py'),'run_gdt062_right_family_register_renderer.py':sha(ROOT/'run_gdt062_right_family_register_renderer.py')},'outputs':{p.name:sha(p) for p in (INVENTORY,PRED,FOLDS,SCORES,NULL,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result=plain(result);result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(plain({'status':status,'pairs':len(target),'folios':host['physical_folios'],'scores':scores,'gates':gates}),sort_keys=True))
 report=REPORT.read_text(encoding='utf-8').replace('no f84 row was printed, displayed to the analyst, retained, joined, or scored.','the scorer displayed no f84 row. A later read-only audit subagent displayed limited rows while diagnosing the breach; no row entered target selection, features, fitting, permutation, or score.').replace('frozen semantic-layer prediction','frozen PAGE_HOST-layer prediction').replace('f84r remains analyst-sealed and is absent from every actual final input and output.','f84r did not enter the final analysis and is absent from every actual final tabular input and output. Limited audit-only exposure means the team-level seal was procedurally breached; no further f84r access is authorized.')
 REPORT.write_text(report,encoding='utf-8')
 result['f84r']={'audit_subagent_limited_payload_exposure':True,'exposure_used_for_selection_or_model':False,'retained':False,'joined':False,'scored':False,'targeted':False,'actual_final_tabular_inputs_contain_rows':False,'further_access_authorized':False}
 result['implementation']['freeze_gdt132_source_seal_correction.py']=sha(ROOT/'freeze_gdt132_source_seal_correction.py')
 result['documents'][REPORT.name]=sha(REPORT)
 result.pop('result_content_sha256',None);result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
