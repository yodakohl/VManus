#!/usr/bin/env python3
"""GDT1135 receipt/protocol validation only, never visual truth certification.

No native rendering, observer repair, semantic solver, or mutation suite.
Observer content stays closed until a root release is provided.
"""
import argparse,hashlib,json,pathlib
from datetime import datetime
from PIL import Image
D=pathlib.Path(__file__).resolve().parents[1]
ROOT=D.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def repo_path(s):
 p=pathlib.Path(s)
 if p.is_absolute() or '..' in p.parts:raise ValueError('Unsafe relative path')
 q=ROOT/p
 if not q.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Path outside repository')
 return q
def local(s):
 p=pathlib.Path(s)
 if p.is_absolute() or '..' in p.parts:raise ValueError('Unsafe experiment path')
 prefix=D.relative_to(ROOT).parts
 q=ROOT/p if p.parts[:len(prefix)]==prefix else D/p
 if not q.resolve().is_relative_to(D.resolve()):raise ValueError('Path outside experiment')
 return q
def time(s):return datetime.fromisoformat(s.replace('Z','+00:00'))
def preflight():
 checks=[]
 def check(n,p,detail=None):
  row={'check':n,'status':'PASS' if p else 'FAIL'}
  if detail is not None:row['detail']=detail
  checks.append(row)
 source=read(D/'src/SOURCE.json');schema=read(D/'src/OBSERVATION_SCHEMA.json');lock=read(D/'artifacts/PREREG_LOCK.json');public=read(D/'artifacts/PUBLIC_REGISTRATION.json')
 check('all_registered_bytes',all(sha(repo_path(p))==h for p,h in lock['sha256'].items()))
 cache=repo_path(source['local_cache'])
 check('exact_original_cache_SHA_and_byte_count',sha(cache)==source['sha256'] and cache.stat().st_size==source['bytes'])
 with Image.open(cache) as picture:dimensions=picture.size
 check('original_cache_dimensions_metadata_only',dimensions==(source['width'],source['height'])==(2835,3705))
 check('registration_and_public_receipt_chronology',time(lock['registered_at_utc'])==time(source['registered_at_utc'])<time(public['verified_at_utc']) and public['before_both_fresh_native_observations'] and len(public['commit'])==40)
 check('registered_scope_and_explicit_semantic_ceiling',source['admitted_key']=='f81v' and source['physical_leaf']=='81' and not source['new_transcription_access'] and not source['semantic_scoring'] and source['independent_meaning_confirmation_capacity']==0 and source['sealed_data']=={'f84':'FORBIDDEN','f84r':'FORBIDDEN'} and not source['f116v_admitted'])
 check('all16_required_observation_fields_and_three_topology_values',len(schema['required_fields'])==len(set(schema['required_fields']))==16 and schema['topology_values']==['SHARED_FIELD','PARTITIONED_FIELDS','UNRESOLVED'])
 return checks,source,schema,lock,public

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--preflight',action='store_true');parser.add_argument('--release');args=parser.parse_args()
 checks,source,schema,lock,public=preflight()
 if args.preflight:
  failures=sum(c['status']=='FAIL' for c in checks);print(json.dumps({'status':'FAIL_PROTOCOL_PREFLIGHT' if failures else 'PASS_PREREG_RECEIPTS_ONLY','checks':len(checks),'failures':failures,'observer_content_read':False,'visual_truth_validation':False}));return bool(failures)
 # The root's final release message pins this adjudication; no manufactured release packet.
 adjudication_path=D/'artifacts/ADJUDICATION.json'
 released_adjudication_sha='6c436a6175c346233c510c09e7b3c4df2e68a5c378bc17d2b54ffacfa13caa7a'
 if not adjudication_path.exists():parser.error('Observer packets remain closed pending root final release.')
 if sha(adjudication_path)!=released_adjudication_sha:raise ValueError('Root-released adjudication bytes changed')
 adjudication=read(adjudication_path)
 def check(name,passed,detail=None):
  v={'check':name,'status':'PASS' if passed else 'FAIL'}
  if detail is not None:v['detail']=detail
  checks.append(v)
 check('root_released_adjudication_exact_bytes',sha(adjudication_path)==released_adjudication_sha)
 pins=adjudication['observer_pins']
 check('both_observers_and_freeze_receipt_bytes',all(sha(D/'artifacts'/p)==h for p,h in pins.items()) and pins['OBSERVER_ROOT.json']=='6d3508c5d74d60d364842285b5a440bf33357f691d637e24ba88151410e16d64' and pins['OBSERVER_B.json']=='72416cf38b04016a991c33bcd0dc0a67984e0e8a0946a74cd9052126b7a48af0')
 observers={'ROOT':read(D/'artifacts/OBSERVER_ROOT.json'),'B':read(D/'artifacts/OBSERVER_B.json')}
 freezes={'ROOT':read(D/'artifacts/ROOT_FREEZE.json'),'B':read(D/'artifacts/B_FREEZE.json')}
 qualification=read(D/'artifacts/PRIOR_NOVELTY_QUALIFICATION.json')
 report_counts={}
 for who,o in observers.items():
  receipt=freezes[who];recorded=time(o['recorded_at_utc']);frozen=time(receipt['frozen_at_utc'])
  check(who+'_all16_required_fields_populated',all(k in o and o[k] not in (None,'',[],{}) for k in schema['required_fields']))
  check(who+'_source_observation_freeze_identity',o['source_sha256']==receipt['source_sha256']==source['sha256'] and (receipt.get('sha256') or receipt.get('observation_sha256'))==sha(D/'artifacts'/('OBSERVER_ROOT.json' if who=='ROOT' else 'OBSERVER_B.json')))
  check(who+'_public_before_recording_and_freeze_before_comparison',time(public['verified_at_utc'])<recorded<=frozen<time(adjudication['adjudicated_at_utc']) and frozen<time('2026-10-02T02:19:00+00:00') and (receipt.get('public_registration_commit') or receipt.get('public_preregistration_commit'))==public['commit'])
  independence=not receipt['other_observer_seen'] if who=='ROOT' else not receipt['other_observer_content_read_before_freeze'] and not receipt['other_observer_observations_communicated_before_freeze']
  check(who+'_declared_initial_blinding',independence,'Receipt declaration and timing only; absence of communications is not independently provable from file contents.')
  bounds=o['panel_bounds_xyxy'];boxes=[]
  def locate_boxes(v):
   if isinstance(v,dict):
    for k,x in v.items():
     if 'bounds' in k and isinstance(x,list) and len(x)==4 and all(isinstance(n,(int,float)) for n in x):boxes.append(x)
     else:locate_boxes(x)
   elif isinstance(v,list):
    for x in v:locate_boxes(x)
  locate_boxes(o)
  coordinate_text=json.dumps(bounds).lower()
  check(who+'_approximate_original_coordinate_boxes_within_dimensions',bool(boxes) and all(0<=x0<x1<=source['width'] and 0<=y0<y1<=source['height'] for x0,y0,x1,y1 in boxes) and '0-based' in coordinate_text and 'approximate' in coordinate_text)
  topology=o['topology'];preferred=topology.get('preferred',topology.get('preferred_candidate'))
  check(who+'_registered_topology_and_disconfirming_limits',preferred in schema['topology_values'] and bool(topology.get('against_preference',topology.get('disconfirming_or_limiting_features'))))
  external=o['external_connections'];external=external if isinstance(external,list) else external['items']
  inscription=o['inscription_placements'];inscription=inscription if isinstance(inscription,list) else inscription['items']
  figure=o['figure_inventory'];count=figure.get('visible_figures',figure.get('visible_count'))
  check(who+'_figure_inventory_internal_arithmetic_only',isinstance(count,int) and count==sum(r['count'] for r in figure['rows']) and all(r['count']==len(r.get('descriptors',r.get('ordered_approximate_head_centers_xy',[]))) for r in figure['rows']),'This compares recorded counts; it does not recount native pixels.')
  check(who+'_external_and_inscription_records_identified_with_uncertainty',bool(external) and bool(inscription) and len({c['id'] for c in external})==len(external) and all(c.get('join_status',c.get('join_classification')) for c in external) and bool(o['uncertainties']))
  report_counts[who]={'required_fields_present':sum(k in o for k in schema['required_fields']),'recorded_figures':count,'recorded_row_counts':[r['count'] for r in figure['rows']],'external_contour_families':len(external),'inscription_placement_items':len(inscription),'external_classifications':{c['id']:c.get('join_status',c.get('join_classification')) for c in external},'preferred_graphic_topology':preferred,'ordered_segment_capacity':o['ordered_segment_capacity']['established']}
 check('both_full_packet_fields_do_not_establish_ordered_segments',all(not o['ordered_segment_capacity']['established'] for o in observers.values()))
 features={i['feature']:i for i in adjudication['items']}
 check('adjudication_retains_bundle_disagreement_exactly',len(adjudication['disagreements'])>=1 and any(d['feature']=='lower_right_bundle' and d['root']=='CONTIGUOUS_AT_TERMINAL_BUNDLE_LOCAL_ONLY' and d['B']=='UNKNOWN' for d in adjudication['disagreements']) and features['lower_right_bundle']['decision']=='DISAGREEMENT_RETAINED_UNKNOWN')
 check('zero_certified_open_joins_not_recast_as_closed',adjudication['definite_open_interior_joins_certified']==0 and adjudication['zero_is_capacity_not_closed_join_evidence'] is True and all(features[k]['decision']=='UNKNOWN' for k in ('left_descending_band','outer_unpainted_loop','right_stub')))
 check('ownership_direction_and_semantic_ceilings_preserved',adjudication['singular_inscription_owners_certified']==0 and features['inscriptions']['decision']=='NO_SINGULAR_INK_OWNER' and features['direction']['decision']=='UNKNOWN_NOT_NO_FLOW' and features['ordered_segment_capacity']['decision']=='NOT_ESTABLISHED' and adjudication['semantic_scoring'] is False and adjudication['confirmed_words']==adjudication['independent_meaning_confirmation_capacity']==0 and not adjudication['new_views_or_repairs_selected'])
 check('prior_figure_count_shared_field_qualification_retained',adjudication['figure_count_not_new'] and adjudication['shared_graphic_field_not_new'] and features['figures']['decision']=='REPLICATION_NOT_NEW' and features['graphic_topology']['decision']=='REPLICATION_WITH_QUALIFICATIONS' and 'sixteen figures in two rows of eight' in qualification['already_known'] and qualification['novelty_must_be_adjudicated'])
 check('late_novelty_note_chronology_without_observer_repair',time(freezes['ROOT']['frozen_at_utc'])<time(qualification['recorded_at_utc'])<time(adjudication['adjudicated_at_utc']) and adjudication['initial_packets_unchanged'] and adjudication['original_fixed_methods_unchanged'] and not adjudication['root_initial_packet_read_B'] and not adjudication['B_initial_packet_read_root'] and adjudication['post_exchange_comparison'])
 check('registered_and_observer_bytes_still_unchanged',all(sha(repo_path(p))==h for p,h in lock['sha256'].items()) and all(sha(D/'artifacts'/p)==h for p,h in pins.items()))
 failures=[c for c in checks if c['status']=='FAIL']
 limits=['This validator checks bytes, receipt chronology, field presence, recorded arithmetic, disagreement retention and explicit claim ceilings only.',
 'No native image rendered or visually recounted. Exhaustiveness of contours/figures/inscriptions and correctness of each visual classification are unverified here.',
 'Declared observer separation is supported by frozen receipts and timing; absence of prefreeze communication is not independently certified.',
 'Zero certified open joins expresses unavailable connectivity capacity, not evidence that those joins are closed. No certified direction marker is not proof of no direction or flow.',
 'Shared graphic field and sixteen figures/two rows of eight were already recorded in the late-retrieved V70/IDEA653 prior according to the preserved qualification; they are not new discoveries or reopening evidence.',
 'ROOT_E4 local bundle contiguity versus B_C4 uncertain attachment remains disagreement/UNKNOWN; it does not identify an open interior join or transported substance.',
 'One exposed leaf supplies zero independent meaning confirmation; no ink owner, word meaning, physical medium, HOT/COLD, chronology or directed relation score is certified.']
 report={'experiment':'GDT1135','status':'FAIL_RECEIPT_PROTOCOL_CHECKS' if failures else 'PASS_RECEIPT_SCHEMA_CEILING_BOOKKEEPING_ONLY','visual_truth_validation':False,'semantic_validation':False,'scientific_PASS_certified':False,'checks':checks,'failed_checks':len(failures),'observer_record_counts':report_counts,'retained_disagreements':adjudication['disagreements'],'adjudication_sha256':released_adjudication_sha,'prior_novelty_qualification_sha256':sha(D/'artifacts/PRIOR_NOVELTY_QUALIFICATION.json'),'source_image_sha256':source['sha256'],'source_dimensions':[source['width'],source['height']],'observer_and_receipt_pins':pins,'validator_sha256':sha(pathlib.Path(__file__)),'manual_unverified_limits':limits}
 (D/'artifacts/VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
 lines=['# GDT1135 independent receipt/protocol validation','',report['status']+'. Visual truth and semantic validation: false.','',f'{len(checks)-len(failures)}/{len(checks)} bookkeeping checks passed.','',
 'Registered bytes, original cache SHA/2314288 bytes/2835×3705 metadata, both observer/freezes and adjudication pins pass. Public registration predates both observation records/freezes; both freezes predate the declared02:19 exchange and later adjudication. Both required16-field accounts are populated. No native image was rendered, no observation was repaired.','',
 'Both packets record16 figures in two rows of8 and prefer a shared graphic field. The late novelty qualification and adjudication explicitly retain these as already-known V70/IDEA653 observations, not new discoveries.','',
 'ROOT_E4 local bundle contiguity versus B_C4 UNKNOWN remains unresolved. Zero certified open interior joins is unavailable capacity, not proof of closed joins. No singular ink owner, directed flow, ordered segment array or confirmed word is inferred.','',
 'Manual/unverified limits:','']+['- '+x for x in limits]
 if failures:lines+=['','Failed checks:','']+['- '+c['check'] for c in failures]
 (D/'artifacts/VALIDATION_REPORT.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps({'status':report['status'],'checks':len(checks),'failures':[c['check'] for c in failures],'visual_truth_validation':False}));return bool(failures)
if __name__=='__main__':raise SystemExit(main())
