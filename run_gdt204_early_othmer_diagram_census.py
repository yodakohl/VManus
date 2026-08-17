#!/usr/bin/env python3
"""Summarize the frozen institutional-catalogue diagram census."""
import csv, hashlib, json
from pathlib import Path

R=Path(__file__).resolve().parent
MAN=R/'gdt204_early_othmer_diagram_census.tsv'; PARENT=R/'gdt203_result.json'
METHOD=R/'GDT204_EARLY_OTHMER_DIAGRAM_CENSUS_METHOD.md'; REPORT=R/'GDT204_EARLY_OTHMER_DIAGRAM_CENSUS_REPORT.md'; RESULT=R/'gdt204_result.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def main():
 with MAN.open(encoding='utf8',newline='') as h: rows=list(csv.DictReader(h,delimiter='\t'))
 manuscripts=sorted(set(r['shelfmark'] for r in rows)); exact=sum(r['exact_f77_homolog']=='1' for r in rows)
 readable=[r for r in rows if r['catalogue_readable_values'] not in {'NONE_CATALOGUED','LETTER_VALUES_NOT_EXPANDED'}]
 operations=[r for r in rows if r['catalogue_status']=='READABLE_OPERATION_GROUP']
 assert manuscripts==[f'Othmer MS {i}' for i in range(1,8)] and len(rows)==24 and exact==0 and len(operations)==3
 status='READABLE_ALCHEMICAL_DIAGRAM_ECOLOGY_EXPANDED_EXACT_F77_HOMOLOG_ABSENT'
 result={'schema':'GDT204_EARLY_OTHMER_DIAGRAM_CENSUS_RESULT_V1','status':status,'counts':{'manuscripts_screened':7,'catalogue_records_retained':24,'records_with_readable_values':len(readable),'readable_operation_triplets':3,'exact_f77_homologs':0},'operation_triplets':[r['catalogue_readable_values'].split(';') for r in operations],'interpretation':'Institutionally catalogued near-contemporary apparatus and operation taxonomy strengthens broad alchemical context but supplies no exact readable f77 topology.','claim_ceiling':'External historical vocabulary and source-family context only; no Voynich group, process state, word, plaintext, meaning, or translation.','f84r':{'opened':False,'queried':False,'retained':False,'joined':False,'scored':False},'inputs':{MAN.name:sha(MAN),PARENT.name:sha(PARENT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}}
 result['result_content_sha256']=csha(result); RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8'); print(json.dumps({'status':status,**result['counts']},sort_keys=True))
if __name__=='__main__': main()
