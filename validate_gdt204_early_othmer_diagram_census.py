#!/usr/bin/env python3
"""Validate GDT204 catalogue coverage, labels, decision, and bindings."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent; RESULT=R/'gdt204_result.json'; MAN=R/'gdt204_early_othmer_diagram_census.tsv'; OUT=R/'gdt204_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def main():
 q=json.loads(RESULT.read_text()); rows=list(csv.DictReader(MAN.open(encoding='utf8'),delimiter='\t')); checks=[]
 def ck(k,x):checks.append((k,bool(x)))
 ck('schema',q['schema']=='GDT204_EARLY_OTHMER_DIAGRAM_CENSUS_RESULT_V1'); ck('status',q['status']=='READABLE_ALCHEMICAL_DIAGRAM_ECOLOGY_EXPANDED_EXACT_F77_HOMOLOG_ABSENT'); ck('rows24',len(rows)==24); ck('seven_manuscripts',set(r['shelfmark'] for r in rows)=={f'Othmer MS {i}' for i in range(1,8)}); ck('unique_ids',len(set(r['record_id'] for r in rows))==24); ck('institutional_urls',all(r['catalogue_url'].startswith('https://openn.library.upenn.edu/Data/0025/html/OthmerMS') for r in rows)); ck('zero_exact',not any(r['exact_f77_homolog']=='1' for r in rows)); ck('three_triplets',sum(r['catalogue_status']=='READABLE_OPERATION_GROUP' for r in rows)==3); ck('operation_values',{r['catalogue_readable_values'] for r in rows if r['catalogue_status']=='READABLE_OPERATION_GROUP'}=={'liquefaccio;elementatio;diuisio','inhumatio;distillacio;calcinacio','inceratio;congelatio;sublimatio'}); readable=sum(r['catalogue_readable_values'] not in {'NONE_CATALOGUED','LETTER_VALUES_NOT_EXPANDED'} for r in rows); ck('counts',q['counts']=={'manuscripts_screened':7,'catalogue_records_retained':24,'records_with_readable_values':readable,'readable_operation_triplets':3,'exact_f77_homologs':0}); ck('no_f84',not any(q['f84r'].values()) and not any('f84' in ' '.join(r.values()).lower() for r in rows))
 for sec in ('inputs','implementation','documents'):
  for f,h in q[sec].items():ck('hash:'+f,sha(R/f)==h)
 z=dict(q); s=z.pop('result_content_sha256');ck('content_hash',csha(z)==s);bad=[k for k,x in checks if not x];o={'schema':'GDT204_VALIDATION_V1','status':'PASS' if not bad else 'FAIL','checks_passed':sum(x for _,x in checks),'checks_total':len(checks),'failed':bad,'result_sha256':sha(RESULT),'scope':'Independent catalogue-row, manuscript-coverage, readable-operation, exact-topology, seal-flag, and hash validation; no Voynich value is inferred.'};OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(json.dumps(o,sort_keys=True));raise SystemExit(bool(bad))
if __name__=='__main__':main()
