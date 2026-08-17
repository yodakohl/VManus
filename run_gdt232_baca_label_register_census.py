#!/usr/bin/env python3
"""Census the postselected BACA family prefix outside every f84 page."""
from __future__ import annotations
import csv,hashlib,json
from collections import Counter
from math import comb
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,rows):
 with Path(p).open('w',encoding='utf-8',newline='') as h:
  w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def hyper(N,K,M,x):return sum(comb(K,i)*comb(N-K,M-i)/comb(N,M) for i in range(x,min(K,M)+1))
def main():
 all_first=[]
 with SOURCE.open(encoding='utf-8') as h:
  header=h.readline().rstrip('\n').split('\t'); pi=header.index('page')
  for raw in h:
   parts=raw.rstrip('\n').split('\t');page=parts[pi]
   if page.startswith('f84'):continue
   r=dict(zip(header,parts))
   if int(r['consensus_group_index'])==1:all_first.append(r)
 baca=[r for r in all_first if r['family_surface'].startswith('BACA')]
 assert len(all_first)==3857 and len(baca)==19
 census=[]
 for r in baca:
  census.append({'locus':r['locus'],'page':r['page'],'section':r['section'],'currier':r['currier'],'hand':r['hand'],'kind':r['kind'],'grammar_scope':r['grammar_scope'],'family_surface':r['family_surface'],'strict_zero_alternative':r['strict_zero_alternative'],'claim_state':'POSTSELECTED_FAMILY_PREFIX_REGISTER_CENSUS_NO_GLOSS'})
 write(ROOT/'gdt232_baca_occurrence_census.tsv',census)
 strata=Counter((r['section'],r['kind']) for r in baca)
 summary=[{'section':s,'kind':k,'occurrences':n} for (s,k),n in sorted(strata.items())]
 write(ROOT/'gdt232_baca_register_summary.tsv',summary)
 total_labels=sum(r['kind']=='L' for r in all_first);baca_labels=sum(r['kind']=='L' for r in baca)
 bp=[r for r in baca if r['section'] in {'B','P'}];bp_labels=sum(r['kind']=='L' for r in bp)
 stats=[
  {'test':'BACA_LABEL_ENRICHMENT_GLOBAL','N':len(all_first),'K_labels':total_labels,'M_baca':len(baca),'x_baca_labels':baca_labels,'one_sided_hypergeom_p':f"{hyper(len(all_first),total_labels,len(baca),baca_labels):.12g}",'status':'POSTSELECTED_DESCRIPTIVE'},
  {'test':'B_OR_P_WITHIN_BACA_LABEL_ENRICHMENT','N':len(baca),'K_labels':baca_labels,'M_baca':len(bp),'x_baca_labels':bp_labels,'one_sided_hypergeom_p':f"{hyper(len(baca),baca_labels,len(bp),bp_labels):.12g}",'status':'POSTSELECTED_DESCRIPTIVE'},
 ]
 write(ROOT/'gdt232_register_tests.tsv',stats)
 result={'experiment':'GDT232_BACA_LABEL_REGISTER_CENSUS','status':'BACA_PREFIX_LABEL_REGISTER_ENRICHED_CONTENT_GLOSS_WEAKENED','non_f84_first_group_loci':len(all_first),'baca_occurrences':len(baca),'baca_labels':baca_labels,'baca_sections':dict(sorted(Counter(r['section'] for r in baca).items())),'baca_section_kind':{f'{s}:{k}':n for (s,k),n in sorted(strata.items())},'q13_baca':{'occurrences':sum(r['section']=='B' for r in baca),'labels':sum(r['section']=='B' and r['kind']=='L' for r in baca)},'pharma_baca':{'occurrences':sum(r['section']=='P' for r in baca),'labels':sum(r['section']=='P' and r['kind']=='L' for r in baca)},'interpretation':'BACA is best treated as a q13/Pharma graphical-label-register family candidate; its f82r pairing may still encode a local class, but water/flow lexical force is weakened.','claim_ceiling':'Postselected family-register census only; no label morpheme, object class, water, flow, word, sound, language, plaintext, or translation.','f84':{'retained':False,'joined':False,'scored':False,'new_access':False},'inputs':{str(SOURCE.relative_to(ROOT)):sha(SOURCE)},'outputs':{},'documents':{},'implementation':{}}
 for n in ('gdt232_baca_occurrence_census.tsv','gdt232_baca_register_summary.tsv','gdt232_register_tests.tsv'):result['outputs'][n]=sha(ROOT/n)
 for n in ('GDT232_BACA_LABEL_REGISTER_CENSUS_METHOD.md','GDT232_BACA_LABEL_REGISTER_CENSUS_REPORT.md'):
  if (ROOT/n).exists():result['documents'][n]=sha(ROOT/n)
 result['implementation'][Path(__file__).name]=sha(Path(__file__))
 result['content_hash']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest();(ROOT/'gdt232_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':result['status'],'total':len(baca),'labels':baca_labels,'sections':result['baca_section_kind']},sort_keys=True))
if __name__=='__main__':main()
