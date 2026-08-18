#!/usr/bin/env python3
"""Validate the GDT308 synthesis against bound prior results."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;MODEL=R/'gdt308_operational_grammar.json';RESULT=R/'gdt308_result.json';OUT=R/'gdt308_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def main():
 checks=[]
 def ck(n,v):
  if not v:raise AssertionError(n)
  checks.append(n)
 m=json.loads(MODEL.read_text());stored=m.pop('content_sha256');ck('model_content_hash',stored==can(m));ck('model_status',m['status']=='SPARSE_OPERATION_LEXICALIZED_HYBRID_GRAMMAR');ck('three_operations',len(m['shared_operations'])==3);ck('operation_classes',{x['operation']:x['domain_stability'] for x in m['shared_operations']}=={'wrapper:ch>s':'DOMAIN_STABLE','wrapper:d>s':'DOMAIN_STABLE','wrapper:NONE>q':'DOMAIN_MIXED_OR_UNSTABLE'});ck('semantic_zero',m['semantic_assignments']==0);ck('f84_forbidden',m['f84_authorized'] is False);r=json.loads(RESULT.read_text());content=r.pop('content_sha256');ck('result_content_hash',content==can(r));ck('result_status',r['status']==m['status']);ck('input_hashes',all(r['inputs'][n]==sha(R/n) for n in r['inputs']));ck('output_hashes',all(r['outputs'][n]==sha(R/n) for n in r['outputs']));ck('implementation_hash',all(r['implementation'][n]==sha(R/n) for n in r['implementation']));ck('f84_flags',not any(r['f84'].values()));v={'schema':'GDT308_SPARSE_OPERATION_GRAMMAR_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks':checks,'result_sha256':sha(RESULT),'f84_rows':0};v['content_sha256']=can(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
