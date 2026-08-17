#!/usr/bin/env python3
"""Independent accounting/integrity validation of GDT278 magnitude calibration."""
import csv,hashlib,json,math,statistics
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent
SCORE=R/'gdt278_magnitude_scores.tsv';NULL=R/'gdt278_null_results.tsv';FOLD=R/'gdt278_folio_scores.tsv';CAP=R/'gdt278_control_capacity.tsv';MATCH=R/'gdt278_matched_event_inventory.tsv';NATIVE=R/'gdt278_native_event_inventory.tsv';RESULT=R/'gdt278_result.json';OUT=R/'gdt278_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
c=[]
def ck(n,v):c.append({'check':n,'pass':bool(v)});assert v,n
def close(a,b,t=2e-8):return math.isclose(float(a),float(b),rel_tol=0,abs_tol=t)
def main():
 d=json.loads((R/'gdt278_magnitude_design.json').read_text());df=json.loads((R/'gdt278_control_source_freeze.json').read_text());r=json.loads(RESULT.read_text());scores=rows(SCORE);nulls=rows(NULL);folds=rows(FOLD);caps=rows(CAP);mm=rows(MATCH);nn=rows(NATIVE);refs={x['view']:x for x in rows(R/'gdt278_reference_magnitude.tsv')};manifest=rows(R/'gdt278_control_manifest.tsv')
 ck('endpoint_was_frozen',d['status']=='FROZEN_BEFORE_EXPANDED_CONTROL_ADMISSION_OR_SCORING' and df['status']=='CONTROL_PANEL_FROZEN_BEFORE_GDT278_SCORING')
 fm=rows(R/'gdt278_gdt277_freeze_manifest.tsv');ck('gdt277_immutable',len(fm)==21 and all(sha(R/x['artifact'])==x['frozen_sha256'] for x in fm) and r['gdt277_immutable'])
 ck('fifteen_controls',len(manifest)==15==r['controls_admitted'])
 ck('source_bindings',all(sha(R/x['observation_artifact'])==x['observation_sha256'] and sha(R/x['architecture_evidence_artifact'])==x['architecture_evidence_sha256'] for x in manifest))
 ck('capacity_views',len(caps)==32 and Counter(x['view'] for x in caps)=={'LENGTH_MATCHED_OVERLAY':16,'NATIVE_ORDER':16})
 matched_ids={x['control_id'] for x in caps if x['view']=='LENGTH_MATCHED_OVERLAY' and x['eligible']=='1'};native_ids={x['control_id'] for x in caps if x['view']=='NATIVE_ORDER' and x['eligible']=='1'}
 ck('panel_count',len(matched_ids)+len(native_ids)==r['score_panels'])
 ck('inventory_counts',len(mm)==sum(int(x['selected_events']) for x in caps if x['view']=='LENGTH_MATCHED_OVERLAY' and x['eligible']=='1') and len(nn)==sum(int(x['selected_events']) for x in caps if x['view']=='NATIVE_ORDER' and x['eligible']=='1'))
 def inv_id(cid):return 'VOYNICH_MATCHED_REFERENCE' if cid=='VOYNICH_REFERENCE' else cid
 ck('matched_exact_4476',all(sum(x['control_id']==inv_id(cid) for x in mm)==4476 for cid in matched_ids))
 ck('native_caps',all(int(x['selected_events'])<=8448 for x in caps if x['view']=='NATIVE_ORDER'))
 ck('no_f84_inventory',not any(x.get('page','').startswith('f84') or x.get('locus','').startswith('f84') for x in mm+nn))
 ck('two_representations',all(sum(x['control_id']==cid and x['view']==view for x in scores)==2 for view,ids in [('LENGTH_MATCHED_OVERLAY',matched_ids),('NATIVE_ORDER',native_ids)] for cid in ids))
 bynull=defaultdict(list)
 for x in nulls:bynull[(x['control_id'],x['view'],x['representation'])].append(float(x['held_bits']))
 ck('null_64_each',all(len(v)==64 for v in bynull.values()) and len(bynull)==len(scores))
 for x in scores:
  key=(x['control_id'],x['view'],x['representation']);v=bynull[key];mean=statistics.mean(v);sd=statistics.pstdev(v);saving=mean-float(x['observed_bits']);event=saving/int(x['events']);z=saving/sd if sd else float('-inf');ref=refs[x['view']]
  ck('score_arithmetic_'+':'.join(key),close(x['null_mean_bits'],mean) and close(x['null_sd_bits'],sd) and close(x['saving_bits'],saving) and close(x['saving_bits_per_event'],event) and (x['null_z']=='NA' if not math.isfinite(z) else close(x['null_z'],z)) and close(x['ratio_s_event_to_voynich'],event/float(ref['saving_bits_per_event'])))
  powered=x['view']=='LENGTH_MATCHED_OVERLAY' or int(x['events'])>=.8*8448;repro=powered and event>=float(ref['saving_bits_per_event']) and z>=float(ref['null_z'])
  ck('decision_'+':'.join(key),int(x['powered_for_gate'])==int(powered) and int(x['reproduces_voynich_magnitude'])==int(repro))
 byfold=defaultdict(float)
 for x in folds:byfold[(x['control_id'],x['view'],x['representation'])]+=float(x['held_bits'])
 ck('fold_sums',all(close(x['observed_bits'],byfold[(x['control_id'],x['view'],x['representation'])]) for x in scores))
 for k,z in defaultdict(list,{}).items():pass
 grouped=defaultdict(list)
 for x in scores:grouped[(x['view'],x['representation'])].append(x)
 ck('ranks',all([int(x['rank_by_saving_bits_per_event']) for x in sorted(v,key=lambda q:-float(q['saving_bits_per_event']))]==list(range(1,len(v)+1)) for v in grouped.values()))
 old={x['control_id']:x for x in rows(R/'gdt277_world_scores.tsv') if x['model']=='ABBREVIATION_HEAVY_LANGUAGE'}
 for cid in ('ORDINARY_NATURAL_LANGUAGE','ABBREVIATION_HEAVY_MEDIEVAL','ARBITRARY_LOCAL_CODEBOOK','COMPOSITIONAL_TECHNICAL_NOTATION','HYBRID_SHORTHAND'):
  x=next(q for q in scores if q['control_id']==cid and q['view']=='LENGTH_MATCHED_OVERLAY' and q['representation']=='PUBLISHED_FULL_INVENTORY');ck('gdt277_anchor_'+cid,close(x['saving_bits'],old[cid]['matched_savings_bits']))
 v=next(x for x in scores if x['control_id']=='VOYNICH_REFERENCE' and x['view']=='NATIVE_ORDER' and x['representation']=='PUBLISHED_FULL_INVENTORY');ck('gdt276_native_anchor',close(v['saving_bits'],3080.522234827527))
 safe=[x for x in scores if x['representation']=='LOFO_SAFE' and x['control_id']!='VOYNICH_REFERENCE'];rob=[]
 for cid in {x['control_id'] for x in safe}:
  z={x['view']:x for x in safe if x['control_id']==cid}
  if len(z)==2 and all(int(x['reproduces_voynich_magnitude']) for x in z.values()):rob.append(cid)
 ck('robust_set',sorted(rob)==sorted(r['robust_reproductions']))
 ck('status_logic',r['status']==('VOYNICH_MAGNITUDE_REPRODUCED_BY_KNOWN_ARCHITECTURE' if rob else 'VOYNICH_MAGNITUDE_ORDER_OR_MATCHING_SENSITIVE' if r['matched_safe_reproductions'] or r['native_safe_reproductions'] else 'VOYNICH_MAGNITUDE_OUTSIDE_CURRENT_GROUND_TRUTH_ENVELOPE'))
 ck('no_semantics_or_mining',r['hpr1_semantics_used']==r['voynich_substrings_mined']==r['semantic_assignments']==r['oracle_fields_scored']==0)
 ck('f84_false',r['f84']['input_files']==0 and not any(v for k,v in r['f84'].items() if k!='input_files'))
 ck('input_hashes',all(sha(R/p)==h for p,h in r['inputs'].items()));ck('output_hashes',all(sha(R/p)==h for p,h in r['outputs'].items()));ck('document_hashes',all(sha(R/p)==h for p,h in r['documents'].items()));ck('implementation_hash',all(sha(R/p)==h for p,h in r['implementation'].items()))
 q=dict(r);h=q.pop('content_sha256');ck('result_content_hash',hashlib.sha256(json.dumps(q,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()==h)
 out={'schema':'GDT278_MAGNITUDE_CALIBRATION_VALIDATION_V1','status':'PASS','checks_passed':len(c),'checks_total':len(c),'checks':c,'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__))};out['content_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True,separators=(',',':')).encode()).hexdigest();OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(c)}))
if __name__=='__main__':main()
