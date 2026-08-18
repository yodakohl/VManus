#!/usr/bin/env python3
"""Compose frozen GDT284 and GDT286 held codelengths."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;METHOD=R/'GDT287_JOINT_WRAPPER_HOST_FACTORIZATION_METHOD.md';REPORT=R/'GDT287_JOINT_WRAPPER_HOST_FACTORIZATION_REPORT.md';OUT=R/'gdt287_joint_scores.tsv';COUNTER=R/'gdt287_counterexamples.tsv';RESULT=R/'gdt287_result.json';MODELS=('INDEPENDENT','WRAPPER_FIRST','HOST_FIRST_STABLE','HOST_FIRST_CONTEXTUAL')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rcsha(v):q=dict(v);q.pop('content_sha256',None);return csha(q)
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rr):
 ff=[]
 for r in rr:
  for k in r:
   if k not in ff:ff.append(k)
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,ff,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rr)
def main():
 a=rows(R/'gdt284_component_scores.tsv');b=rows(R/'gdt286_panel_scores.tsv');manifest={x['control_id']:x for x in rows(R/'gdt278_control_manifest.tsv')};panels=sorted({x['control_id'] for x in b});out=[];summary=[]
 for p in panels:
  hb=sum(float(x['base_bits']) for x in a if x['control_id']==p and x['mode']=='STANDARD_HELD_FOLIO');hw=sum(float(x['wrapper_bits']) for x in a if x['control_id']==p and x['mode']=='STANDARD_HELD_FOLIO');wb={x['model']:float(x['bits']) for x in b if x['control_id']==p};assert len(wb)==3
  bits={'INDEPENDENT':hb+wb['SHAPE_CONTEXT']+2,'WRAPPER_FIRST':hw+wb['SHAPE_CONTEXT']+2,'HOST_FIRST_STABLE':hb+wb['EXACT_HOST']+2,'HOST_FIRST_CONTEXTUAL':hb+wb['EXACT_HOST_X_POSITION']+2};order=sorted(MODELS,key=lambda m:(bits[m],m));cat='UNKNOWN_VOYNICH_ARCHITECTURE' if p=='VOYNICH_REFERENCE' else manifest[p]['architecture_category']
  for m in MODELS:out.append({'control_id':p,'architecture_category':cat,'model':m,'events':8448,'selector_bits':2,'joint_bits':f'{bits[m]:.12f}','joint_bits_per_event':f'{bits[m]/8448:.12f}','saving_vs_independent_bits_per_event':f'{(bits["INDEPENDENT"]-bits[m])/8448:.12f}','rank':order.index(m)+1})
  summary.append({'control_id':p,'architecture_category':cat,'winner':order[0],'runner_up':order[1],'winner_bits_per_event':f'{bits[order[0]]/8448:.12f}','runner_up_bits_per_event':f'{bits[order[1]]/8448:.12f}','winner_margin_bits_per_event':f'{(bits[order[1]]-bits[order[0]])/8448:.12f}'})
 write(OUT,out);v=next(x for x in summary if x['control_id']=='VOYNICH_REFERENCE');counts={m:sum(x['winner']==m for x in summary if x['control_id']!='VOYNICH_REFERENCE') for m in MODELS};counter=[{'counterexample':'BEST_OPERATIONAL_FACTORING_PROVES_CAUSAL_ORDER','evidence':'all component scores use exposed fixed hierarchical estimators','impact':'ranking is descriptive compression synthesis'}, {'counterexample':'VOYNICH_WINNER_IS_UNIQUE_TO_VOYNICH','evidence':f"control winner counts {json.dumps(counts,sort_keys=True,separators=(',',':'))}",'impact':'shared winners limit architectural specificity'}, {'counterexample':'WINNER_MARGIN_IS_LARGE','evidence':f"Voynich winner margin {v['winner_margin_bits_per_event']} bits/event",'impact':'report magnitude without a posthoc threshold'}, {'counterexample':'F84_USED','evidence':'only f84-free published result tables are read','impact':'no f84 access'}];write(COUNTER,counter)
 report=['# GDT287 — joint wrapper/host factorization synthesis','','Status: **POSTHOC_JOINT_FACTORIZATION_SYNTHESIS**.','','| panel | architecture | winner | runner-up | margin bits/event |','|---|---|---|---|---:|']
 for x in summary:report.append(f"| {x['control_id']} | {x['architecture_category']} | {x['winner']} | {x['runner_up']} | {float(x['winner_margin_bits_per_event']):.4f} |")
 report +=['','Voynich is best encoded by `'+v['winner']+'`, ahead of `'+v['runner_up']+'` by '+f"{float(v['winner_margin_bits_per_event']):.4f}"+' bits/event. Control winner counts are `'+json.dumps(counts,sort_keys=True)+'`. This ranks the four frozen predictive factorizations; it does not identify causal order.','','## Claim ceiling','','No lexical unit, morphology, abbreviation, notation, language, meaning, plaintext, or translation follows. No f84 row was opened, parsed, retained, joined, or scored.'];REPORT.write_text('\n'.join(report)+'\n')
 inputs=['gdt284_result.json','gdt284_component_scores.tsv','gdt286_result.json','gdt286_panel_scores.tsv','gdt278_control_manifest.tsv'];outputs=[OUT,COUNTER,REPORT];res={'schema':'GDT287_JOINT_WRAPPER_HOST_FACTORIZATION_RESULT_V1','status':'POSTHOC_JOINT_FACTORIZATION_SYNTHESIS','models':list(MODELS),'panels':8,'selector_bits_each':2,'voynich':v,'control_winner_counts':counts,'new_scores_fit':0,'semantic_assignments':0,'page_host_substrings_mined':0,'claim_ceiling':'Operational joint factorization ranking only; no lexical class morphology language meaning plaintext or translation.','f84':{'input_files':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'inputs':{x:sha(R/x) for x in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{x.name:sha(x) for x in outputs}};res['content_sha256']=rcsha(res);RESULT.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({'winner':v['winner'],'runner_up':v['runner_up'],'margin':v['winner_margin_bits_per_event']},sort_keys=True))
if __name__=='__main__':main()
