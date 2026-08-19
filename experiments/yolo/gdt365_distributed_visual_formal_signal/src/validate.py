#!/usr/bin/env python3
"""Integrity/source/retained-score validator for GDT365."""
from __future__ import annotations
import csv,hashlib,importlib.util,json,sys
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from tools.vmanus_experiment import GuardedTSV,canonical_json_bytes,sha256_file  # noqa:E402
EXP=ROOT/'experiments/yolo/gdt365_distributed_visual_formal_signal';ART=EXP/'artifacts';RESULT=ART/'gdt365_result.json';VALIDATION=ART/'gdt365_validation.json';FORMAL=ROOT/'experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv';LEAF=ROOT/'experiments/yolo/gdt363_leaf_margin_formal_atlas/artifacts/gdt363_panel.tsv';REPRO=ROOT/'experiments/yolo/gdt364_reproductive_structure_joint_atlas/artifacts/gdt364_panel.tsv';HELPER=ROOT/'experiments/yolo/gdt363_leaf_margin_formal_atlas/src/run.py'
def read(p):
 with p.open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 checks=[]
 def ck(n,v,d=''):
  checks.append({'name':n,'pass':bool(v),'detail':d});assert v,(n,d)
 lp=read(LEAF);rp=read(REPRO);allowed={r['page'] for r in lp+rp};ck('union_66',len(allowed)==66,len(allowed));ck('leaf_scored_42',sum(r['score_eligible']=='1' for r in lp)==42);ck('repro_34',len(rp)==34)
 reader=GuardedTSV(FORMAL,selector_column='page',allowed_values=allowed,forbidden_prefixes=('f84',),forbidden_action='skip');source=list(reader);ck('source_4402',len(source)==4402,len(source));ck('source_pages',set(r['page'] for r in source)==allowed);ck('source_no_f84',not any(r['page'].startswith('f84') for r in source))
 spec=importlib.util.spec_from_file_location('gdt363_frozen_validator',HELPER);assert spec and spec.loader;m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);by=defaultdict(list)
 for r in source:by[r['page']].append(r)
 vals={p:m.family_events(by[p])[0] for p in allowed};names=sorted(n for n in {k for v in vals.values() for k in v} if sum(vals[p].get(n,0)>0 for p in allowed)>=8 and sum(vals[p].get(n,0)==0 for p in allowed)>=8);manifest=read(ART/'gdt365_feature_manifest.tsv');ck('features_227',len(names)==227,len(names));ck('feature_manifest',[r['formal_feature'] for r in manifest]==names)
 scores=read(ART/'gdt365_scores.tsv');folds=read(ART/'gdt365_folds.tsv');ck('six_models',len(scores)==6);ck('dimensions',{int(r['pca_dimensions']) for r in scores}=={2,4,8});ck('endpoints',{r['endpoint'] for r in scores}=={'LEAF_MARGIN_BINARY','REPRODUCTIVE_THREE_CLASS'});ck('fold_rows_267',len(folds)==267,len(folds))
 bykey=defaultdict(list)
 for r in folds:bykey[(r['endpoint'],int(r['dimension']),r['hold_scope'])].append(r)
 arithmetic=True;positive=True;counts=True
 for r in scores:
  key=(r['endpoint'],int(r['pca_dimensions']))
  for scope,prefix in [('FOLIO','folio'),('QUIRE','quire')]:
   rows=bykey[key+(scope,)];arithmetic &= abs(sum(float(x['gain_bits']) for x in rows)-float(r[prefix+'_gain_bits']))<5e-8;positive &= sum(float(x['gain_bits'])>0 for x in rows)==int(r[prefix+'_positive_folds']);counts &= len(rows)==int(r[prefix+'_folds'])
 ck('gain_arithmetic',arithmetic);ck('positive_folds',positive);ck('fold_counts',counts)
 ck('p_grid',all(abs(float(r[k])*1025-round(float(r[k])*1025))<1e-8 for r in scores for k in ('local_p','max_six_p')))
 best=max(scores,key=lambda r:float(r['folio_gain_bits']));ck('best_repro4',best['endpoint']=='REPRODUCTIVE_THREE_CLASS' and best['pca_dimensions']=='4');ck('best_values',abs(float(best['folio_gain_bits'])-2.520568140477)<1e-10 and abs(float(best['quire_gain_bits'])+9.274759986873)<1e-10 and abs(float(best['max_six_p'])-.082926829268)<1e-10)
 ck('no_interesting',not any(r['status']=='DISTRIBUTED_SIGNAL_INTERESTING_EXPLORATORY' for r in scores));ck('leaf_all_negative',all(float(r['folio_gain_bits'])<0 for r in scores if r['endpoint']=='LEAF_MARGIN_BINARY'));ck('repro_positive_fails_quire',all(float(r['quire_gain_bits'])<0 for r in scores if r['endpoint']=='REPRODUCTIVE_THREE_CLASS' and float(r['folio_gain_bits'])>0))
 result=json.loads(RESULT.read_text());q=dict(result);d=q.pop('content_hash');ck('content_hash',hashlib.sha256(canonical_json_bytes(q)).hexdigest()==d);ck('result_best',result['best_model']['endpoint']==best['endpoint'] and int(result['best_model']['pca_dimensions'])==4);ck('input_hashes',all(sha256_file(ROOT/k)==v for k,v in result['inputs'].items()));ck('implementation_hashes',all(sha256_file(ROOT/k)==v for k,v in result['implementation'].items()));ck('output_hashes',all(sha256_file(ROOT/k)==v for k,v in result['outputs'].items()))
 report=(EXP/'REPORT.md').read_text();ck('report_local',"loses 9.27 bits" not in report or 'held-quire' in report);ck('report_ceiling','assigns no plant, visual-state word' in report);ck('report_f84','No f84 row was retained, parsed, joined, displayed, or scored' in report)
 payload={'schema':'GDT365_VALIDATION_V1','status':'PASS','checks':checks,'pass_count':sum(x['pass'] for x in checks),'check_count':len(checks),'scope':'INDEPENDENT_GUARDED_SOURCE_AND_FEATURE_LIBRARY_RECONSTRUCTION_PLUS_RETAINED_FOLD_ARITHMETIC;MODEL_AND_NULL_NOT_INDEPENDENTLY_REFIT','result_sha256':sha256_file(RESULT),'validator_sha256':sha256_file(Path(__file__)),'documents':{str(p.relative_to(ROOT)):sha256_file(p) for p in (EXP/'METHOD.md',EXP/'REPORT.md')},'f84_accessed':False};payload['content_hash']=hashlib.sha256(canonical_json_bytes(payload)).hexdigest();VALIDATION.write_bytes(canonical_json_bytes(payload));print(f"PASS {payload['pass_count']}/{payload['check_count']}")
if __name__=='__main__':main()
