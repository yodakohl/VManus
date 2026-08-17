#!/usr/bin/env python3
import csv,hashlib,json
from collections import defaultdict
from math import comb
from pathlib import Path
R=Path(__file__).resolve().parent
SRC=R/'experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv'
OUTS=['gdt237_section_folds.tsv','gdt237_prefix_stability.tsv','gdt237_predictions.tsv']
DOCS=['GDT237_LABEL_PREFIX_LEAVE_SECTION_METHOD.md','GDT237_LABEL_PREFIX_LEAVE_SECTION_REPORT.md']
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def hyper(N,K,M,x):
 return sum(comb(K,i)*comb(N-K,M-i)/comb(N,M) for i in range(x,min(K,M)+1)) if M else 1.0
def write(n,rows,header):
 with (R/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=header,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 rows=[]
 with SRC.open(encoding='utf-8') as f:
  head=f.readline().rstrip('\n').split('\t'); pi=head.index('page')
  for raw in f:
   a=raw.rstrip('\n').split('\t'); page=a[pi]
   if page.startswith('f84'):continue
   d=dict(zip(head,a))
   if int(d['consensus_group_index'])==1:rows.append(d)
 sections=sorted({x['section'] for x in rows}); folds=[]; preds=[]; chosen_by={}
 for hold in sections:
  tr=[x for x in rows if x['section']!=hold]; te=[x for x in rows if x['section']==hold]
  N=len(tr);K=sum(x['kind']=='L' for x in tr); selected=[]
  for L in range(1,5):
   by=defaultdict(list)
   for x in tr:
    s=x['family_surface']
    if len(s)>=L:by[s[:L]].append(x)
   for p,rr in by.items():
    M=len(rr); z=sum(x['kind']=='L' for x in rr); pv=hyper(N,K,M,z)
    if M>=5 and z>=4 and z/M>=.5 and pv<=.01:selected.append((L,p,M,z,z/M,pv))
  selected.sort(); ps={x[1] for x in selected};chosen_by[hold]=ps
  tp=fp=fn=tn=0
  for x in te:
   matches=sorted((p for p in ps if x['family_surface'].startswith(p)),key=lambda p:(-len(p),p)); p=matches[0] if matches else ''
   y=x['kind']=='L'; yh=bool(p); tp+=y and yh; fp+=(not y) and yh; fn+=y and not yh;tn+=(not y) and not yh
   preds.append({'held_section':hold,'locus':x['locus'],'page':x['page'],'kind':x['kind'],'family_surface':x['family_surface'],'matched_prefix':p or 'NONE','predicted_label':int(yh),'true_label':int(y)})
  M=tp+fp; labels=tp+fn; precision=tp/M if M else 0; prev=labels/len(te); pv=hyper(len(te),labels,M,tp)
  folds.append({'held_section':hold,'training_rows':N,'training_labels':K,'selected_prefixes':len(ps),'test_rows':len(te),'test_labels':labels,'tp':tp,'fp':fp,'fn':fn,'tn':tn,'predicted_positive':M,'precision':f'{precision:.12f}','label_prevalence':f'{prev:.12f}','precision_lift':f'{precision-prev:.12f}','recall':f'{tp/labels if labels else 0:.12f}','one_sided_hypergeom_p':f'{pv:.12g}'})
 write(OUTS[0],folds,list(folds[0]));write(OUTS[2],preds,list(preds[0]))
 universe=sorted(set().union(*chosen_by.values())); stable=[]
 for p in universe:
  hs=[s for s in sections if p in chosen_by[s]]
  stable.append({'prefix':p,'selected_folds':len(hs),'held_sections_selected':','.join(hs),'all_folds':int(len(hs)==len(sections))})
 write(OUTS[1],stable,list(stable[0]))
 tp=sum(int(x['tp']) for x in folds);fp=sum(int(x['fp']) for x in folds);fn=sum(int(x['fn']) for x in folds);tn=sum(int(x['tn']) for x in folds)
 positive=[x['held_section'] for x in folds if float(x['precision_lift'])>0 and int(x['tp'])>0]
 sig=[x['held_section'] for x in folds if float(x['one_sided_hypergeom_p'])<=.05]
 result={'experiment':'GDT237_LABEL_PREFIX_LEAVE_SECTION_TRANSFER','status':'',
 'rows':len(rows),'sections':sections,'labels':sum(x['kind']=='L' for x in rows),
 'pooled':{'tp':tp,'fp':fp,'fn':fn,'tn':tn,'precision':tp/(tp+fp),'recall':tp/(tp+fn),'prevalence':(tp+fn)/len(rows)},
 'positive_lift_sections':positive,'nominal_significant_sections':sig,'stable_prefixes_all_folds':sum(x['all_folds'] for x in stable),
 'f84':{'retained':False,'joined':False,'scored':False,'new_access':False},
 'claim_ceiling':'Cross-section prediction of editorial label kind only; no authorial label marker, ownership, object, word, morpheme, language, plaintext, or translation.',
 'inputs':{str(SRC.relative_to(R)):sha(str(SRC.relative_to(R)))},'outputs':{},'documents':{},'implementation':{}}
 result['status']='GRAPHICAL_LABEL_PREFIX_COMPILER_CROSS_SECTION_PARTIAL' if len(positive)>=3 and len(sig)>=2 else 'GRAPHICAL_LABEL_PREFIX_COMPILER_SECTION_DEPENDENT'
 for p in OUTS:result['outputs'][p]=sha(p)
 for p in DOCS:
  if (R/p).exists():result['documents'][p]=sha(p)
 result['implementation'][Path(__file__).name]=sha(Path(__file__).name)
 core=dict(result);result['content_hash']=hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 (R/'gdt237_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':result['status'],'positive':positive,'significant':sig,'pooled':result['pooled']},sort_keys=True))
if __name__=='__main__':main()
