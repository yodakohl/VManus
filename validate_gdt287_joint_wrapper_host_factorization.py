#!/usr/bin/env python3
"""Independent arithmetic validation for GDT287."""
from __future__ import annotations
import csv,hashlib,json,math
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/'gdt287_result.json';OUT=R/'gdt287_validation.json';MODELS=('INDEPENDENT','WRAPPER_FIRST','HOST_FIRST_STABLE','HOST_FIRST_CONTEXTUAL')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):q=dict(v);q.pop('content_sha256',None);return hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def close(a,b):return math.isclose(float(a),float(b),rel_tol=0,abs_tol=2e-8)
def main():
 c=[]
 def ck(n,v):c.append({'check':n,'pass':bool(v)});assert v,n
 res=json.loads(RESULT.read_text());out=rows(R/'gdt287_joint_scores.tsv');a=rows(R/'gdt284_component_scores.tsv');b=rows(R/'gdt286_panel_scores.tsv');panels=sorted({x['control_id'] for x in b});ck('counts',len(out)==32 and len(panels)==8)
 winners={}
 for p in panels:
  hb=sum(float(x['base_bits']) for x in a if x['control_id']==p and x['mode']=='STANDARD_HELD_FOLIO');hw=sum(float(x['wrapper_bits']) for x in a if x['control_id']==p and x['mode']=='STANDARD_HELD_FOLIO');wb={x['model']:float(x['bits']) for x in b if x['control_id']==p};bits={'INDEPENDENT':hb+wb['SHAPE_CONTEXT']+2,'WRAPPER_FIRST':hw+wb['SHAPE_CONTEXT']+2,'HOST_FIRST_STABLE':hb+wb['EXACT_HOST']+2,'HOST_FIRST_CONTEXTUAL':hb+wb['EXACT_HOST_X_POSITION']+2};order=sorted(MODELS,key=lambda m:(bits[m],m));winners[p]=order[0]
  for m in MODELS:
   x=next(q for q in out if q['control_id']==p and q['model']==m);ck(p+':'+m,close(x['joint_bits'],bits[m]) and close(x['joint_bits_per_event'],bits[m]/8448) and close(x['saving_vs_independent_bits_per_event'],(bits['INDEPENDENT']-bits[m])/8448) and int(x['rank'])==order.index(m)+1)
 v=res['voynich'];vv=[x for x in out if x['control_id']=='VOYNICH_REFERENCE'];o=sorted(vv,key=lambda x:(float(x['joint_bits']),x['model']));ck('voynich',v['winner']==o[0]['model'] and v['runner_up']==o[1]['model'] and close(v['winner_margin_bits_per_event'],float(o[1]['joint_bits_per_event'])-float(o[0]['joint_bits_per_event'])));cnt={m:sum(x==m for p,x in winners.items() if p!='VOYNICH_REFERENCE') for m in MODELS};ck('controls',cnt==res['control_winner_counts']);ck('status',res['status']=='POSTHOC_JOINT_FACTORIZATION_SYNTHESIS' and res['new_scores_fit']==res['semantic_assignments']==res['page_host_substrings_mined']==0);ck('f84',res['f84']['input_files']==0 and not any(v for k,v in res['f84'].items() if k!='input_files'));ck('inputs',all(sha(R/k)==v for k,v in res['inputs'].items()));ck('docs',all(sha(R/k)==v for k,v in res['documents'].items()));ck('impl',all(sha(R/k)==v for k,v in res['implementation'].items()));ck('outputs',all(sha(R/k)==v for k,v in res['outputs'].items()));ck('content',res['content_sha256']==csha(res))
 z={'schema':'GDT287_JOINT_WRAPPER_HOST_FACTORIZATION_VALIDATION_V1','status':'PASS','validation_scope':'INDEPENDENT_CHAIN_RULE_ARITHMETIC_RANK_AND_HASH_RECONSTRUCTION','checks_passed':len(c),'checks_total':len(c),'checks':c,'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};z['content_sha256']=csha(z);OUT.write_text(json.dumps(z,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(c)},sort_keys=True))
if __name__=='__main__':main()
