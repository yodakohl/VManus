#!/usr/bin/env python3
"""Integrity and claim validation for the GDT288 abductive synthesis."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;MODEL=R/'gdt288_operational_grammar.json';REPORT=R/'GDT288_OPERATIONAL_GENERATIVE_GRAMMAR_REPORT.md';RESULT=R/'gdt288_result.json';OUT=R/'gdt288_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def main():
 c=[]
 def ck(n,v):c.append({'check':n,'pass':bool(v)});assert v,n
 m=json.loads(MODEL.read_text());r=json.loads(RESULT.read_text());text=REPORT.read_text();ck('status',m['status']==r['status']=='HYBRID_RECORD_SHORTHAND_LEADING_GENERATIVE_THEORY');ck('epistemic',m['epistemic_status']=='YOLO_ABDUCTIVE_HYPOTHESIS_NOT_CONFIRMATION' and 'not a confirmation claim' in text);ck('worlds',len(m['alternatives'])==3 and sum(x['rank']=='LEADING' for x in m['alternatives'])==1);ck('order',len(m['generation_order'])==9 and m['generation_order'][4]=='PAGE_HOST_GRAPHEMATIC_KERNEL' and m['generation_order'][5]=='HOST_BY_SLOT_OUTER_WRAPPER');ck('no_semantics',m['semantic_assignments']==m['lexical_glosses']==m['page_host_substrings_mined']==0 and r['semantic_assignments']==r['lexical_glosses']==r['page_host_substrings_mined']==0);ck('f84',not any(m['f84'].values()) and not any(r['f84'].values()) and 'f84 remains sealed' in text);ck('inputs',all(sha(R/k)==v for k,v in r['inputs'].items()));ck('docs',r['documents'][REPORT.name]==sha(REPORT) and r['documents'][MODEL.name]==sha(MODEL));ck('impl',all(sha(R/k)==v for k,v in r['implementation'].items()));ck('content',r['content_sha256']==csha(r))
 z={'schema':'GDT288_OPERATIONAL_GENERATIVE_GRAMMAR_VALIDATION_V1','status':'PASS','validation_scope':'INTEGRITY_CLAIM_CEILING_AND_EVIDENCE_BINDING','checks_passed':len(c),'checks_total':len(c),'checks':c,'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};z['content_sha256']=csha(z);OUT.write_text(json.dumps(z,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(c)},sort_keys=True))
if __name__=='__main__':main()
