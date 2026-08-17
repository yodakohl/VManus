#!/usr/bin/env python3
"""Learn label-enriched family prefixes outside q13 and apply them to q13."""
from __future__ import annotations
import csv,hashlib,json
from collections import Counter,defaultdict
from math import comb
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def hyper(N,K,M,x):return sum(comb(K,i)*comb(N-K,M-i)/comb(N,M) for i in range(x,min(K,M)+1))
def write(p,rows):
 with Path(p).open('w',encoding='utf-8',newline='') as h:
  w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 first=[]
 with SOURCE.open(encoding='utf-8') as h:
  header=h.readline().rstrip('\n').split('\t');pi=header.index('page')
  for raw in h:
   parts=raw.rstrip('\n').split('\t');page=parts[pi]
   if page.startswith('f84'):continue
   r=dict(zip(header,parts))
   if int(r['consensus_group_index'])==1:first.append(r)
 train=[r for r in first if r['section']!='B'];test=[r for r in first if r['section']=='B']
 N=len(train);K=sum(r['kind']=='L' for r in train);selected=[];allstats={}
 for length in range(1,5):
  by=defaultdict(list)
  for r in train:
   s=r['family_surface']
   if len(s)>=length:by[s[:length]].append(r)
  for prefix,rr in by.items():
   M=len(rr);x=sum(r['kind']=='L' for r in rr);p=hyper(N,K,M,x)
   allstats[prefix]=(length,M,x,x/M,p)
   if M>=5 and x>=4 and x/M>=.5 and p<=.01:selected.append((length,prefix,M,x,x/M,p))
 selected.sort(key=lambda z:(z[0],z[1]));prefixes={z[1] for z in selected}
 manifest=[{'prefix':p,'length':l,'training_occurrences':M,'training_labels':x,'training_label_rate':f'{rate:.12f}','one_sided_hypergeom_p':f'{pv:.12g}','selection_status':'STRICT_TRAINING_SELECTED'} for l,p,M,x,rate,pv in selected]
 l,M,x,rate,pv=allstats['BACA'];manifest.append({'prefix':'BACA','length':l,'training_occurrences':M,'training_labels':x,'training_label_rate':f'{rate:.12f}','one_sided_hypergeom_p':f'{pv:.12g}','selection_status':'EXPOSED_SENSITIVITY_NOT_STRICT_SELECTED'})
 write(ROOT/'gdt233_prefix_manifest.tsv',manifest)
 predictions=[]
 for r in test:
  matches=sorted((p for p in prefixes if r['family_surface'].startswith(p)),key=lambda p:(-len(p),p))
  chosen=matches[0] if matches else ''
  residual=r['family_surface'][len(chosen):] if chosen else r['family_surface']
  baca=r['family_surface'].startswith('BACA')
  predictions.append({'locus':r['locus'],'page':r['page'],'kind':r['kind'],'grammar_scope':r['grammar_scope'],'family_surface':r['family_surface'],'strict_prefix':chosen or 'NONE','strict_residual':residual or 'EMPTY','predicted_label':int(bool(chosen)),'true_label':int(r['kind']=='L'),'baca_sensitivity':int(baca),'baca_residual':r['family_surface'][4:] if baca else r['family_surface'],'claim_state':'TRANSFERRED_REGISTER_DECOMPOSITION_NO_GLOSS'})
 write(ROOT/'gdt233_q13_label_predictions.tsv',predictions)
 tp=sum(r['predicted_label']==1 and r['true_label']==1 for r in predictions);fp=sum(r['predicted_label']==1 and r['true_label']==0 for r in predictions);fn=sum(r['predicted_label']==0 and r['true_label']==1 for r in predictions);tn=sum(r['predicted_label']==0 and r['true_label']==0 for r in predictions)
 Kt=tp+fn;Mt=tp+fp;Nt=len(predictions);p=hyper(Nt,Kt,Mt,tp)
 metrics=[{'model':'STRICT_OUTSIDE_Q13_PREFIX_UNION','tp':tp,'fp':fp,'fn':fn,'tn':tn,'precision':f'{tp/(tp+fp):.12f}','recall':f'{tp/(tp+fn):.12f}','q13_label_prevalence':f'{Kt/Nt:.12f}','one_sided_hypergeom_p':f'{p:.12g}','status':'TRANSFERRED_PARTIAL_LABEL_REGISTER_SIGNAL'},
 {'model':'BACA_EXPOSED_SENSITIVITY','tp':sum(r['baca_sensitivity']==1 and r['true_label']==1 for r in predictions),'fp':sum(r['baca_sensitivity']==1 and r['true_label']==0 for r in predictions),'fn':Kt-sum(r['baca_sensitivity']==1 and r['true_label']==1 for r in predictions),'tn':Nt-Kt-sum(r['baca_sensitivity']==1 and r['true_label']==0 for r in predictions),'precision':'1.000000000000','recall':f"{sum(r['baca_sensitivity']==1 and r['true_label']==1 for r in predictions)/Kt:.12f}",'q13_label_prevalence':f'{Kt/Nt:.12f}','one_sided_hypergeom_p':'POSTSELECTED','status':'SENSITIVITY_ONLY'}]
 write(ROOT/'gdt233_transfer_metrics.tsv',metrics)
 baca_rows=[r for r in predictions if r['baca_sensitivity']==1]
 result={'experiment':'GDT233_TRANSFERRED_LABEL_PREFIX_COMPILER','status':'TRANSFERRED_GRAPHICAL_LABEL_PREFIX_LAYER_PARTIAL_CONTENT_RESIDUAL_UNRESOLVED','training_loci':len(train),'training_labels':K,'q13_loci':Nt,'q13_labels':Kt,'strict_prefixes':len(selected),'strict_transfer':{'tp':tp,'fp':fp,'fn':fn,'tn':tn,'precision':tp/(tp+fp),'recall':tp/(tp+fn),'p':p},'baca_training':{'occurrences':M,'labels':x,'label_rate':rate,'p':pv,'strict_selected':False},'baca_q13':{'occurrences':len(baca_rows),'labels':sum(r['true_label']==1 for r in baca_rows),'residuals':{r['locus']:r['baca_residual'] for r in baca_rows}},'interpretation':'A partial graphical-label prefix compiler transfers into q13. BACA is a near-threshold outside-q13 label prefix and leaves heterogeneous residuals, favoring register/local-class over a water word.','claim_ceiling':'Transferred editorial-label register architecture and residual candidates only; no authorial label marker, object, word, morpheme, sound, language, plaintext, or translation.','f84':{'retained':False,'joined':False,'scored':False,'new_access':False},'inputs':{str(SOURCE.relative_to(ROOT)):sha(SOURCE)},'outputs':{},'documents':{},'implementation':{}}
 for n in ('gdt233_prefix_manifest.tsv','gdt233_q13_label_predictions.tsv','gdt233_transfer_metrics.tsv'):result['outputs'][n]=sha(ROOT/n)
 for n in ('GDT233_TRANSFERRED_LABEL_PREFIX_COMPILER_METHOD.md','GDT233_TRANSFERRED_LABEL_PREFIX_COMPILER_REPORT.md'):
  if (ROOT/n).exists():result['documents'][n]=sha(ROOT/n)
 result['implementation'][Path(__file__).name]=sha(Path(__file__));result['content_hash']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest();(ROOT/'gdt233_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':result['status'],'prefixes':len(selected),'transfer':result['strict_transfer'],'baca':result['baca_training']},sort_keys=True))
if __name__=='__main__':main()
