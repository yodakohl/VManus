#!/usr/bin/env python3
"""Independent integrity and evidence validation for the GDT298 synthesis."""
from __future__ import annotations
import csv,hashlib,json
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parent;RESULT=R/'gdt298_result.json';OUT=R/'gdt298_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ch(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rch(v):q=dict(v);q.pop('content_sha256',None);return ch(q)
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 checks=[]
 def ck(n,v):
  checks.append((n,bool(v)))
  if not v:raise AssertionError(n)
 r=json.loads(RESULT.read_text());ck('content',r['content_sha256']==rch(r));ck('status',r['status']=='LEXICALIZED_HYBRID_RECORD_SHORTHAND_LEADING_THEORY');ck('no_scores',r['new_manuscript_scores']==0);ck('prohibitions',r['semantic_assignments']==r['lexical_glosses']==r['page_host_substrings_mined']==0);ck('f84',not any(r['f84'].values()))
 for group in ('inputs','documents','implementation','outputs'):
  for name,digest in r[group].items():ck(f'{group}:{name}',sha(R/name)==digest)
 source={name:json.loads((R/name).read_text()) for name in r['inputs']};expected={'gdt165_result.json':'OPAQUE_HOST_RELATIONS_NOT_TRANSFERABLE','gdt169_result.json':'NO_REPLICATED_EXTERNAL_REFERENT_INVARIANCE','gdt276_result.json':'RESIDUAL_CHANNEL_QUANTIFIED_ABBREVIATION_HEAVY_LANGUAGE_MDL_LEAD_EXPLORATORY','gdt278_result.json':'VOYNICH_MAGNITUDE_ORDER_OR_MATCHING_SENSITIVE','gdt289_result.json':'HOST_POSITION_EFFECT_REQUIRES_HOST_SPECIFIC_TABLE','gdt290_result.json':'HOST_POSITION_RENDERING_REMAINS_LEXICALIZED_OR_HIGH_CAPACITY','gdt292_result.json':'RIGHT_FAMILY_CLOSURE_CHANNEL_WEAK_OR_LOCAL','gdt293_result.json':'EXACT_HOST_RENDERER_COMPLETION_SUPPORTED','gdt294_result.json':'HOST_POSITION_RENDERER_TUPLE_SUPPORTED','gdt295_result.json':'PAGE_LOCAL_RENDERER_ADAPTATION_WEAK_OR_LOCAL','gdt296_result.json':'OPAQUE_HOST_RENDERER_ATLAS_BUILT','gdt297_result.json':'EXACT_HOST_RENDERER_IS_WITHIN_HOST_SURFACE_ALIAS'}
 for name,status in expected.items():ck(f'source_status:{name}',source[name]['status']==status)
 ck('gdt293_value',abs(float(source['gdt293_result.json']['voynich_summary']['joint_gain_bits_per_event'])-1.414868109442)<1e-12);ck('gdt292_value',abs(float(source['gdt292_result.json']['voynich_summary']['right_gain_bits_per_event'])+0.007589851575)<1e-12);ck('gdt289_value',abs(float(source['gdt289_result.json']['voynich_summary']['transfer_gain_bits_per_event'])+0.179036631738)<1e-12);ck('gdt297_bijection',source['gdt297_result.json']['within_host_bijection_hosts']==59 and source['gdt297_result.json']['hosts']==59)
 p=rows(R/'gdt298_prediction_audit.tsv');c=rows(R/'gdt298_model_comparison.tsv');m=json.loads((R/'gdt298_operational_grammar_v2.json').read_text());ck('prediction_ids',[x['prediction_id'] for x in p]==[f'GDT288_P0{i}' for i in range(1,7)]);ck('prediction_outcomes',Counter(x['outcome'] for x in p)==Counter(r['prediction_outcomes']));ck('world_rank',[int(x['rank']) for x in c]==list(range(1,6)) and c[0]['world']=='LEXICALIZED_HYBRID_RECORD_SHORTHAND');ck('model',m['status']==r['status'] and m['leading_world']==r['leading_world']);ck('joint_state','JOINT_PAGE_HOST_PLUS_RENDERER_ALTERNANT' in m['generation_order'] and m['high_capacity_layer']['renderer_independence']=='NOT_ESTABLISHED');ck('model_prohibitions',m['semantic_assignments']==m['lexical_glosses']==m['page_host_substrings_mined']==0 and not any(m['f84'].values()));text=(R/'GDT298_LEXICALIZED_HYBRID_GRAMMAR_REVISION_REPORT.md').read_text();ck('report','high-capacity **joint form lexicon**' in text and 'No f84 material was accessed' in text)
 out={'schema':'GDT298_LEXICALIZED_HYBRID_GRAMMAR_REVISION_VALIDATION_V1','status':'PASS','scope':'INDEPENDENT_INPUT_STATUS_NUMERIC_EVIDENCE_AND_SYNTHESIS_INTEGRITY','checks_total':len(checks),'checks_passed':sum(v for n,v in checks),'check_categories':dict(sorted(Counter(n.split(':',1)[0] for n,v in checks).items())),'failed_checks':[n for n,v in checks if not v],'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};out['content_sha256']=rch(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
