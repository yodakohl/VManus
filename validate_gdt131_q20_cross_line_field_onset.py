#!/usr/bin/env python3
"""Independent inventory/accounting validator for GDT131."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent;RESULT=ROOT/'gdt131_result.json';OUT=ROOT/'gdt131_validation.json'
FIELDS=ROOT/'gdt127_q20_field_inventory.tsv';PANEL=ROOT/'q20ob001_source_panel.tsv';INV=ROOT/'gdt131_cross_line_field_inventory.tsv'
FOLDS=ROOT/'gdt131_cross_line_field_folds.tsv';SCORES=ROOT/'gdt131_cross_line_field_scores.tsv';PRED=ROOT/'gdt131_cross_line_field_predictions.tsv'
NULL=ROOT/'gdt131_cross_line_field_null.tsv';EXACT=ROOT/'gdt131_exact_formula_diagnostic.tsv';COMP=ROOT/'gdt131_cross_line_field_components.tsv';COUNTER=ROOT/'gdt131_cross_line_field_counterexamples.tsv'
METHOD=ROOT/'GDT131_Q20_CROSS_LINE_FIELD_ONSET_METHOD.md';REPORT=ROOT/'GDT131_Q20_CROSS_LINE_FIELD_ONSET_REPORT.md'
EDITIONS=('ZL3b','IT2a','RF1b');MODES=('LAST_COMPILER12','LAST_ORDERED_CELL_HASH32','LAST_HOST_CHAR3_HASH32','LAST_RAW_CHAR3_HASH32');BLOCKS=('FIRST_WRAPPER','FIRST_FRAME','FIRST_RENDERER','FIELD_COUNT','FIELD_CLOSURE')

def read(p):
 with Path(p).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
checks=[]
def ck(name,value,detail=''):
 checks.append({'check':name,'pass':bool(value),'detail':detail});
 if not value:raise AssertionError(name+': '+detail)
def arch(row):
 cells=json.loads(row['compiler_skeleton']);w,f,r,d,dy,b3=cells[0];n=len(cells);end='DY' if int(cells[-1][4]) else 'B3' if int(cells[-1][5]) else 'OPEN'
 return f"W={w};F={f};R={int(r!='NONE')};D={int(d)};DY={int(dy)};B3={int(b3)};N={'4+' if n>=4 else n};END={end}"

def main():
 result=json.loads(RESULT.read_text());inv=read(INV);folds=read(FOLDS);scores=read(SCORES);pred=read(PRED);null=read(NULL);exact=read(EXACT);comp=read(COMP)
 ck('schema',result['schema']=='GDT131_Q20_CROSS_LINE_FIELD_ONSET_RESULT_V1')
 ck('f84_flags',all(v is False for v in result['f84r'].values()))
 ck('inventory_shape',len(inv)==510 and all(sum(r['edition']==e for r in inv)==170 for e in EDITIONS))
 ck('no_f84_inventory',not any('f84r' in json.dumps(r) for r in inv))
 ck('unique_inventory_keys',len({(r['edition'],r['page'],r['star_ordinal']) for r in inv})==510)
 panel={(r['edition'],r['page'],r['star_ordinal']):r for r in read(PANEL) if r['edition'] in EDITIONS};ck('panel_shape',len(panel)==510)
 fields=defaultdict(list)
 for r in read(FIELDS):
  k=(r['edition'],r['page'],r['star_ordinal'])
  if k in panel:fields[k].append(r)
 rebuilt=[]
 source_complete=True
 for k in sorted(panel):
  rows=fields[k];op=sorted((r for r in rows if r['record_scope']=='OPEN'),key=lambda r:(int(r['line_depth']),int(r['field_index'])));body=sorted((r for r in rows if r['record_scope']=='BODY'),key=lambda r:(int(r['line_depth']),int(r['field_index'])))
  source_complete &= bool(op and body)
  if not op or not body:continue
  a,b=op[-1],body[0]
  rebuilt.append((k,a['field_id'],b['field_id'],a['group_tokens'],a['page_hosts'],a['template_id'],b['group_tokens'],b['page_hosts'],b['template_id'],arch(b)))
 ck('all_source_fields_present',source_complete and len(rebuilt)==510)
 got=sorted(((r['edition'],r['page'],r['star_ordinal']),r['last_open_field_id'],r['first_body_field_id'],r['last_open_tokens'],r['last_open_hosts'],r['last_open_template'],r['first_body_tokens'],r['first_body_hosts'],r['first_body_template'],r['first_body_architecture']) for r in inv)
 ck('inventory_exact_source_rebuild',rebuilt==got)
 zl=[r for r in inv if r['edition']=='ZL3b'];sur=Counter(r['first_body_tokens'] for r in zl);tmp=Counter(r['first_body_template'] for r in zl)
 ck('sparsity_exact',len(sur)==168 and sum(v==1 for v in sur.values())==166 and len(tmp)==150 and sum(v==1 for v in tmp.values())==144)
 ck('fold_shape',len(folds)==len(EDITIONS)*len(MODES)*8)
 ck('score_shape',len(scores)==len(EDITIONS)*len(MODES))
 smap={(r['edition'],r['model']):r for r in scores};ck('score_unique',len(smap)==12)
 for k,s in smap.items():
  q=[r for r in folds if (r['edition'],r['model'])==k]
  ck('fold_sum_'+('|'.join(k)),abs(sum(float(r['pseudo_gain_bits']) for r in q)-float(s['pseudo_gain_bits']))<2e-9)
  ck('fold_positive_'+('|'.join(k)),sum(int(r['positive_gain']) for r in q)==int(s['positive_folios']))
 ck('component_shape',len(comp)==len(EDITIONS)*len(MODES)*len(BLOCKS))
 for k,s in smap.items():
  q=[r for r in comp if (r['edition'],r['model'])==k]
  ck('component_names_'+('|'.join(k)),set(r['target_block'] for r in q)==set(BLOCKS))
  ck('component_sum_'+('|'.join(k)),abs(sum(float(r['incremental_gain_bits']) for r in q)-float(s['pseudo_gain_bits']))<2e-9)
 ck('prediction_shape',len(pred)==len(EDITIONS)*(len(MODES)+1)*170)
 for k,s in smap.items():
  q=[r for r in pred if (r['edition'],r['model'])==k]
  ck('prediction_counts_'+('|'.join(k)),len(q)==170 and sum(int(r['actual_seen_in_training']) for r in q)==int(s['architecture_seen']) and sum(int(r['top1_hit']) for r in q)==int(s['top1_hits']) and sum(int(r['top3_hit']) for r in q)==int(s['top3_hits']))
 for e in EDITIONS:
  q=[r for r in pred if r['edition']==e and r['model']=='REFERENCE_OPEN_COMPILER12'];z=result['reference_architecture'][e]
  ck('reference_predictions_'+e,len(q)==170 and sum(int(r['top1_hit']) for r in q)==z['top1_hits'] and sum(int(r['top3_hit']) for r in q)==z['top3_hits'])
 ck('null_shape',len(null)==12)
 for r in null:
  s=smap[(r['edition'],r['model'])];ck('null_score_'+r['edition']+'_'+r['model'],abs(float(r['true_gain_bits'])-float(s['pseudo_gain_bits']))<1e-10 and abs(float(r['local_p'])-float(s['local_p']))<1e-10 and abs(float(r['max_four_p'])-float(s['max_four_p']))<1e-10 and int(r['worlds'])==4096)
 # Independently recreate training-only unique exact lookups from the exported source-bound inventory.
 exp=[]
 for e in EDITIONS:
  rr=[r for r in inv if r['edition']==e]
  for held in sorted({r['physical_folio'] for r in rr}):
   tr=[r for r in rr if r['physical_folio']!=held];te=[r for r in rr if r['physical_folio']==held]
   for kind,col in (('TOKENS','last_open_tokens'),('HOSTS','last_open_hosts'),('TEMPLATE','last_open_template')):
    d=defaultdict(set)
    for r in tr:d[r[col]].add(r['first_body_tokens'])
    m={k:next(iter(v)) for k,v in d.items() if len(v)==1}
    for r in te:
     if r[col] in m:exp.append((e,held,r['unit_id'],kind,r[col],m[r[col]],r['first_body_tokens'],str(int(m[r[col]]==r['first_body_tokens']))))
 gotx=sorted((r['edition'],r['held_folio'],r['unit_id'],r['predictor'],r['last_field_key'],r['predicted_first_body_tokens'],r['actual_first_body_tokens'],r['exact_hit']) for r in exact)
 ck('exact_lookup_rebuild',sorted(exp)==gotx)
 ck('exact_zl_summary',sum(r['edition']=='ZL3b' for r in exact)==result['exact_formula_predictions_zl'] and sum(int(r['exact_hit']) for r in exact if r['edition']=='ZL3b')==result['exact_formula_hits_zl']==0)
 zlscore={m:smap[('ZL3b',m)] for m in MODES};lead=max(MODES,key=lambda m:float(zlscore[m]['pseudo_gain_bits']));ck('lead_model',lead==result['lead_model']=='LAST_HOST_CHAR3_HASH32')
 p=zlscore[lead];g={'selector_paid_positive':float(p['selector_paid_bits'])>0,'six_of_eight_positive':int(p['positive_folios'])>=6,'all_readings_positive':all(float(smap[(e,lead)]['pseudo_gain_bits'])>0 for e in EDITIONS),'max_four_p_le_005':float(p['max_four_p'])<=.05,'beats_both_string_controls':False}
 ck('gates',g==result['gates']);ck('status',result['status']=='Q20_LAST_OPEN_HOST_TO_FIRST_BODY_ARCHITECTURE_LEAD_WEAK_OR_FOLD_UNSTABLE')
 for name,h in result['inputs'].items():ck('input_hash_'+name,sha(ROOT/name)==h)
 for name,h in result['outputs'].items():ck('output_hash_'+name,sha(ROOT/name)==h)
 for name,h in result['documents'].items():ck('document_hash_'+name,sha(ROOT/name)==h)
 for name,h in result['implementation'].items():ck('implementation_hash_'+name,sha(ROOT/name)==h)
 x=dict(result);claimed=x.pop('result_content_sha256');ck('result_content_hash',csha(x)==claimed)
 text=METHOD.read_text()+REPORT.read_text();ck('claim_ceiling',all(term in text for term in ('f84r','No heading','No heading, recipe')) and 'weak cross-line content-address/texture lead' in REPORT.read_text())
 validation={'schema':'GDT131_Q20_CROSS_LINE_FIELD_ONSET_VALIDATION_V1','status':'PASS_INDEPENDENT_SOURCE_INVENTORY_AND_ACCOUNTING','checks':len(checks),'passed':sum(x['pass'] for x in checks),'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__)),'check_rows':checks}
 OUT.write_text(json.dumps(validation,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':validation['status'],'checks':validation['checks'],'passed':validation['passed']},sort_keys=True))

if __name__=='__main__':main()
