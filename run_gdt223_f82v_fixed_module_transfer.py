#!/usr/bin/env python3
"""Score frozen GDT223 f82v module predictions."""
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent
MAN=R/'gdt223_f82v_assembly_prediction.tsv'; MOD=R/'gdt222_module_manifest.tsv'
LABELS=R/'gdt012_annotated_core_inventory.tsv'; GROUPS=R/'gdt016_group_state_inventory.tsv'
FREEZE=R/'gdt223_prediction_freeze.json'; FV=R/'gdt223_freeze_validation.json'
METHOD=R/'GDT223_F82V_FIXED_MODULE_TRANSFER_FREEZE_METHOD.md'; REPORT=R/'GDT223_F82V_FIXED_MODULE_TRANSFER_REPORT.md'
INV=R/'gdt223_f82v_module_inventory.tsv'; SCORE=R/'gdt223_f82v_assignment_score.tsv'
CORR=R/'gdt223_f82v_module_correspondence.tsv'; LOMO=R/'gdt223_f82v_leave_one_module_out.tsv'
COUNTER=R/'gdt223_counterexamples.tsv'; RESULT=R/'gdt223_result.json'
FREEZE_COMMIT='dc266ccfdb70e2cb7ba7c8bb681c1c6727f27fc8'
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with p.open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def jac(a,b):return len(a&b)/len(a|b) if a|b else 0.0
def main():
 modules=[r['module'] for r in read(MOD)];assert modules==['ar','ol','dal','dar','sy','te','tee','dy']
 freeze=json.loads(FREEZE.read_text());assert freeze['status']=='FROZEN_BEFORE_TARGET_MODULE_REVEAL'
 man=read(MAN);assert len(man)==2 and {r['page'] for r in man}=={'f82v'}
 ll={x for r in man for x in r['label_loci'].split(',')};pl={x for r in man for x in r['prose_loci'].split(',')}
 labels=defaultdict(list)
 with LABELS.open(encoding='utf8',newline='')as h:
  for r in csv.DictReader(h,delimiter='\t'):
   assert not r['page'].startswith('f84')
   if r['locus'] in ll:labels[r['locus']].append(r['token'])
 prose=defaultdict(list);counts={}
 with GROUPS.open(encoding='utf8',newline='')as h:
  for r in csv.DictReader(h,delimiter='\t'):
   if r['page'].startswith('f84'):continue
   if r['locus'] in pl:prose[r['locus']].append(r['token']);counts[r['locus']]=int(r['group_count'])
 assert set(labels)==ll and set(prose)==pl and all(len(prose[l])==counts[l] for l in pl)
 def toks(row,key,src):return [t for l in row[key].split(',') for t in src[l]]
 def present(ts,exclude=None):return {m for m in modules if m!=exclude and any(m in t for t in ts)}
 sets={};inv=[]
 for row in man:
  side=row['assembly'];lt=toks(row,'label_loci',labels);pt=toks(row,'prose_loci',prose)
  sets['L'+side[0]]=present(lt);sets['P'+side[0]]=present(pt)
  for role,ts,ms in [('LABEL',lt,sets['L'+side[0]]),('PROSE',pt,sets['P'+side[0]])]:inv.append({'page':'f82v','assembly':side,'role':role,'token_count':len(ts),'tokens':'|'.join(ts),'modules':'|'.join(m for m in modules if m in ms) or 'NONE'})
 tt=jac(sets['LT'],sets['PT']);tb=jac(sets['LT'],sets['PB']);bt=jac(sets['LB'],sets['PT']);bb=jac(sets['LB'],sets['PB']);lead=tt+bb-tb-bt
 score=[{'page':'f82v','top_to_top':f'{tt:.12g}','top_to_bottom':f'{tb:.12g}','bottom_to_top':f'{bt:.12g}','bottom_to_bottom':f'{bb:.12g}','correct_assignment_lead':f'{lead:.12g}','exact_swap_worlds':2,'directional_p':'0.5','prediction_hit':int(lead>0)}]
 corr=[]
 for m in modules:
  lp=(int(m in sets['LT']),int(m in sets['LB']));pp=(int(m in sets['PT']),int(m in sets['PB']));hit=int(lp[0]!=lp[1] and pp[0]!=pp[1] and lp==pp)
  corr.append({'module':m,'label_top':lp[0],'label_bottom':lp[1],'prose_top':pp[0],'prose_bottom':pp[1],'discriminating_pattern_match':hit,'frozen_named_prediction':int(m=='ar'),'prediction_hit':int(m=='ar' and hit)})
 lomo=[]
 for m in modules:
  s={k:v-{m} for k,v in sets.items()};x=jac(s['LT'],s['PT'])+jac(s['LB'],s['PB'])-jac(s['LT'],s['PB'])-jac(s['LB'],s['PT']);lomo.append({'excluded_module':m,'assignment_lead':f'{x:.12g}','positive':int(x>0)})
 write(INV,inv);write(SCORE,score);write(CORR,corr);write(LOMO,lomo)
 counter=[
  {'counterexample':'AR_PREDICTION_FAILED','value':'LABEL_0_OF_2_PROSE_2_OF_2','detail':'ar is absent from both label assemblies and present in both prose assemblies; it has no local discriminating side.'},
  {'counterexample':'DAL_POSTREVEAL_CONCENTRATION','value':'ONLY_DISCRIMINATING_MODULE','detail':'dal alone matches top label and prose presence; removing it reverses the total lead to -0.183333.'},
  {'counterexample':'SMALL_EFFECT','value':f'{lead:.12g}','detail':'The correct module-set assignment exceeds the swap by only 0.057143 Jaccard units.'},
  {'counterexample':'ONE_PAGE_NULL','value':'2_WORLDS_P_POINT5','detail':'Prospective direction on one page cannot distinguish the result from chance assignment.'},
  {'counterexample':'PROXIMITY_NOT_OWNERSHIP','value':'8_LABELS','detail':'Human top/bottom placement does not establish that a label names its neighboring figure or channel.'},
 ]
 write(COUNTER,counter)
 arhit=bool(next(int(x['discriminating_pattern_match']) for x in corr if x['module']=='ar'));dalhit=bool(next(int(x['discriminating_pattern_match']) for x in corr if x['module']=='dal'))
 status='MODULE_SET_DIRECTION_HIT_AR_LOCAL_ADDRESS_TRANSFER_FAILED'
 r={'schema':'GDT223_F82V_FIXED_MODULE_TRANSFER_RESULT_V1','status':status,'freeze_commit':FREEZE_COMMIT,'page':'f82v','physical_folio':'f82','modules':modules,'selected_labels':len(ll),'selected_complete_prose_lines':len(pl),'prediction_results':{'positive_assignment_lead':lead>0,'assignment_lead':lead,'exact_swap_worlds':2,'directional_p':.5,'ar_discriminates_exactly_one_matching_side':arhit,'postreveal_dal_discriminates_exactly_one_matching_side':dalhit},'interpretation':'The generic module-set direction transfers weakly, but the frozen ar local-address prediction fails; dal is the post-reveal driver.','claim_ceiling':'One-page prospective formal component-assignment result only; no segmentation role word sound language plaintext or translation.','f84':{'accessed':False,'retained':False,'joined':False,'scored':False},'inputs':{p.name:sha(p) for p in (MAN,MOD,LABELS,GROUPS,FREEZE,FV)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{p.name:sha(p) for p in (INV,SCORE,CORR,LOMO,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}}
 r['result_content_sha256']=csha(r);RESULT.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'lead':lead,'ar_hit':arhit,'dal_hit':dalhit},sort_keys=True))
if __name__=='__main__':main()
