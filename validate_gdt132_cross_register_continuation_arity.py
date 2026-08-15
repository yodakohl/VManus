#!/usr/bin/env python3
"""Independent source-selection and accounting validator for GDT132."""
from __future__ import annotations
import csv,hashlib,json,re
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'gdt016_group_state_inventory.tsv'
FRAMES=ROOT/'gdt046_line_frames.tsv'
RESULT=ROOT/'gdt132_result.json'
INVENTORY=ROOT/'gdt132_continuation_arity_inventory.tsv'
PRED=ROOT/'gdt132_continuation_arity_predictions.tsv'
FOLDS=ROOT/'gdt132_continuation_arity_folds.tsv'
SCORES=ROOT/'gdt132_continuation_arity_scores.tsv'
NULL=ROOT/'gdt132_continuation_arity_null.tsv'
OUT=ROOT/'gdt132_validation.json'
SECTIONS={'H','B','P','T','C'}
Q20={'f104','f105','f106','f107','f112','f113','f114','f115'}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def numeric(loc):
 m=re.match(r'^(.*)\.(\d+)$',loc);return (m.group(1),int(m.group(2))) if m else None
def close(a,b,tol=2e-10):return abs(float(a)-float(b))<=tol
def source_pairs():
 by=defaultdict(list)
 for r in read(SOURCE):
  if r['section'] in SECTIONS and r['physical_folio'] not in Q20 and not r['page'].startswith('f84r') and not r['locus'].startswith('f84r'):by[r['locus']].append(r)
 complete={}
 for loc,z in by.items():
  z.sort(key=lambda r:int(r['group_index']));n=int(z[0]['group_count'])
  if len(z)==n and [int(x['group_index']) for x in z]==list(range(1,n+1)):complete[loc]=z
 frame={r['locus']:r for r in read(FRAMES)}
 out={}
 for loc,z in complete.items():
  if frame.get(loc,{}).get('paragraph_start')!='1':continue
  p=numeric(loc)
  if not p:continue
  nxt=f'{p[0]}.{p[1]+1}'
  if nxt not in complete or frame.get(nxt,{}).get('paragraph_start')!='0':continue
  a=z;b=complete[nxt]
  fs=[];cur=[]
  for x in a:
   cur.append(x)
   if x['dy_closure']=='1':fs.append(cur);cur=[]
  if cur:fs.append(cur)
  first=[]
  for x in b:
   first.append(x)
   if x['dy_closure']=='1':break
  out[(loc,nxt)]={'page':z[0]['page'],'physical_folio':z[0]['physical_folio'],'section':z[0]['section'],'currier':z[0]['currier'],'hand':z[0]['hand'],'source_group_count':len(a),'source_member_count':sum(len(x['family_surface']) for x in a),'last_field_group_count':len(fs[-1]),'last_field_tokens':'|'.join(x['token'] for x in fs[-1]),'next_first_field_group_count':len(first),'next_first_field_tokens':'|'.join(x['token'] for x in first)}
 return out

def main():
 result=json.loads(RESULT.read_text());checks=[]
 def ck(name,value):
  checks.append({'check':name,'pass':bool(value)});assert value,name
 ck('schema',result['schema']=='GDT132_CROSS_REGISTER_CONTINUATION_ARITY_RESULT_V1')
 ck('status',result['status']=='Q20_CONTINUATION_ARITY_DOES_NOT_TRANSFER_OUTSIDE_SECTION_S')
 freeze=json.loads((ROOT/'gdt132_prediction.json').read_text())
 ck('freeze_status',freeze['status']=='FROZEN_BEFORE_EXTERNAL_TARGET_PAIR_ENUMERATION')
 ck('freeze_hash_bound',result['inputs']['gdt132_prediction.json']==sha(ROOT/'gdt132_prediction.json'))
 src=source_pairs();inv=read(INVENTORY);ik={(r['locus'],r['next_locus']):r for r in inv}
 ck('independent_pair_keys',set(src)==set(ik))
 ck('pair_count',len(inv)==result['target_pairs']==31)
 ck('folio_count',len({r['physical_folio'] for r in inv})==result['physical_folios']==24)
 ck('section_set',sorted({r['section'] for r in inv})==result['sections']==['B','C','H','P'])
 for key,r in ik.items():
  s=src[key]
  ck('source_row_'+r['locus'],all(str(s[k])==r[k] for k in s))
 ck('selection_state',all(r['selection_state']=='MECHANICAL_POST_FREEZE' for r in inv))
 ck('no_q20_target',not any(r['physical_folio'] in Q20 or r['section']=='S' for r in inv))
 ck('actual_inputs_have_no_f84',all(not any(r.get('page','').startswith('f84r') or r.get('locus','').startswith('f84r') for r in read(p)) for p in (SOURCE,FRAMES)))
 ck('outputs_have_no_f84',not any('f84r' in p.read_text(errors='ignore') for p in (INVENTORY,PRED,FOLDS,SCORES,NULL,ROOT/'gdt132_continuation_arity_counterexamples.tsv')))
 f84=result['f84r'];ck('f84_provenance',f84['audit_subagent_limited_payload_exposure'] is True and f84['exposure_used_for_selection_or_model'] is False and f84['actual_final_tabular_inputs_contain_rows'] is False and f84['further_access_authorized'] is False and all(f84[k] is False for k in ('retained','joined','scored','targeted')))
 preds=read(PRED);folds=read(FOLDS);scores=read(SCORES);nulls={r['model']:r for r in read(NULL)};rscore={r['model']:r for r in result['scores']}
 ck('prediction_rows',len(preds)==62 and {r['model'] for r in preds}==set(rscore))
 ck('fold_rows',len(folds)==48)
 for model in sorted(rscore):
  p=[r for r in preds if r['model']==model];f=[r for r in folds if r['model']==model];s=next(r for r in scores if r['model']==model);j=rscore[model];n=nulls[model]
  ck('prediction_count_'+model,len(p)==31)
  ck('top1_'+model,int(s['reference_top1'])==sum(int(r['reference_hit']) for r in p)==j['reference_top1'] and int(s['model_top1'])==sum(int(r['model_hit']) for r in p)==j['model_top1'])
  ck('top3_'+model,int(s['reference_top3'])==sum(int(r['reference_top3_hit']) for r in p)==j['reference_top3'] and int(s['model_top3'])==sum(int(r['model_top3_hit']) for r in p)==j['model_top3'])
  ck('fold_gain_'+model,close(sum(float(r['gain_bits']) for r in f),j['gain_bits']))
  ck('positive_folios_'+model,sum(int(r['positive_gain']) for r in f)==j['positive_folios'])
  ck('score_result_'+model,all(close(s[k],j[k]) for k in ('gain_bits','null_mean_bits','local_p','max_two_p')))
  ck('null_result_'+model,close(n['true_gain_bits'],j['gain_bits']) and close(n['null_mean_bits'],j['null_mean_bits']) and close(n['local_p'],j['local_p']) and close(n['max_two_p'],j['max_two_p']))
 cap=[]
 for level in range(4):
  strata=defaultdict(list)
  for i,r in enumerate(inv):
   key=[r['section'],r['currier'],r['hand'],r['source_group_count'] if int(r['source_group_count'])<10 else '10PLUS']
   if level>=1:key.append(r['last_field_group_count'])
   if level>=2:key.append(str(sum(len(x) for x in r['last_field_hosts'].split('|'))))
   if level>=3:key.append(str(sum(len(x) for x in r['last_field_tokens'].split('|'))))
   strata[tuple(key)].append(i)
  cap.append(sum(len(v) for v in strata.values() if len(v)>1))
 ck('opportunity_capacity',cap==[20,15,4,0] and list(result['null_opportunity_capacity'].values())==cap)
 correction=json.loads((ROOT/'gdt132_source_seal_correction.json').read_text())
 ck('source_seal_correction',correction['status']=='POST_EXPOSURE_INPUT_SEAL_CORRECTION_BEFORE_FINAL_RESCORING' and correction['superseded_prepublication_run']['target_pairs']==32 and result['source_seal_correction']['post_exposure'] is True and result['source_seal_correction']['sha256']==sha(ROOT/'gdt132_source_seal_correction.json'))
 zc=dict(correction);hc=zc.pop('correction_content_sha256');ck('correction_content_hash',csha(zc)==hc)
 ck('correction_replacement_hashes',all(sha(ROOT/n)==h for n,h in correction['replacement_inputs'].items()) and all(v==0 for v in correction['replacement_f84r_rows'].values()))
 ck('correction_original_freeze',correction['original_prediction_sha256']==sha(ROOT/'gdt132_prediction.json'))
 host=rscore['LAST_HOST_CHAR3_HASH32'];raw=rscore['LAST_RAW_CHAR3_HASH32']
 gates={'host_gain_positive':host['gain_bits']>0,'host_beats_raw':host['gain_bits']>raw['gain_bits'],'majority_folios_positive':host['positive_folios']>host['physical_folios']/2,'max_two_p_le_005':host['max_two_p']<=.05}
 ck('gates',gates==result['gates']=={'host_gain_positive':False,'host_beats_raw':False,'majority_folios_positive':False,'max_two_p_le_005':False})
 ck('input_hashes',all(sha(ROOT/n)==h for n,h in result['inputs'].items()))
 ck('implementation_hashes',all(sha(ROOT/n)==h for n,h in result['implementation'].items()))
 ck('output_hashes',all(sha(ROOT/n)==h for n,h in result['outputs'].items()))
 ck('document_hashes',all(sha(ROOT/n)==h for n,h in result['documents'].items()))
 z=dict(result);h=z.pop('result_content_sha256');ck('content_hash',csha(z)==h)
 validation={'schema':'GDT132_CROSS_REGISTER_CONTINUATION_ARITY_VALIDATION_V1','status':'PASS_INDEPENDENT_SELECTION_AND_ACCOUNTING','checks':len(checks),'passed':sum(r['pass'] for r in checks),'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__)),'scope':'Independent source-pair selection, inventory reconstruction, output accounting, gates, hashes, and f84 exclusion; retained numeric model coefficients and permutation worlds are not refit.','check_rows':checks}
 OUT.write_text(json.dumps(validation,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':validation['status'],'checks':validation['checks']},sort_keys=True))
if __name__=='__main__':main()
