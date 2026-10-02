#!/usr/bin/env python3
"""Source-only Greek word alignment receipt/accounting validator.

No image rendering, native recognition, target decoder, new corpus or mutations.
PASS here certifies bookkeeping only, never historical/visual/semantic truth.
"""
import hashlib,json,pathlib
from datetime import datetime
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[3]
def read(p):return json.loads(p.read_text())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def relative(base,p):
 q=pathlib.Path(p)
 if q.is_absolute() or '..' in q.parts:raise ValueError('Unsafe relative pin')
 v=base/q
 if not v.resolve().is_relative_to(base.resolve()):raise ValueError('Pin outside authorized base')
 return v
def time(s):return datetime.fromisoformat(s.replace('Z','+00:00'))
def main():
 checks=[]
 def check(name,passed,detail=None):
  c={'check':name,'status':'PASS' if passed else 'FAIL'}
  if detail is not None:c['detail']=detail
  checks.append(c)
 reg=read(D/'GD_GREEK_WORD_ALIGNMENT_REGISTRATION.json');result=read(D/'GD_GREEK_WORD_ALIGNMENT_RESULT.json')
 root=read(D/'GD_GREEK_265V_OBSERVER_ROOT.json');C=read(D/'GD_GREEK_265V_OBSERVER_C.json');B=read(D/'GD_GREEK_CARRIER_OBSERVER_B.json')
 print_packet=read(D/'GD_GREEK_PRINT_PARTIAL_CONSTRUCTION.json');post=read(D/'GD_GREEK_POSTFREEZE_VIEW.json')
 check('all_nine_result_bound_artifact_SHA_pins',len(result['artifacts'])==9 and all(sha(relative(D,p))==h for p,h in result['artifacts'].items()))
 check('registration_decision_bytes_and_bound_observer_registration',sha(D/'GD_GREEK_WORD_ALIGNMENT.md')==reg['decision_sha256']==B['registration_decision_sha256'])
 images=reg['source_images'];image_pins={i['exact_label']:i['sha256'] for i in images}
 check('all_three_registered_original_source_image_bytes',len(images)==3 and set(image_pins)=={'265v','219v','284r'} and all(sha(relative(ROOT,i['cache']))==i['sha256'] for i in images))
 check('all_C_input_and_B_source_bytes',all(sha(relative(ROOT,p['path']))==p['sha256'] for p in C['inputs']+B['sources']))
 check('observer_native_source_hashes_match_registered_images',root['native_image_sha256']==image_pins['265v'] and C['inputs'][0]['sha256']==image_pins['265v'] and B['sources'][0]['sha256']==image_pins['219v'] and post['native_source_sha256']==image_pins['265v'])
 expected=reg['source_words']
 for name,rows,index in [('ROOT',root['rows'],'position'),('C',C['words'],'index')]:
  check(name+'_all11_editorial_positions_exact',len(rows)==len(expected)==11 and [r[index] for r in rows]==list(range(1,12)) and [r['editorial_word'] for r in rows]==expected)
 categories={'ordinary_only':[1,2,6,7,9,10,11],'mixed_carrier_shorthand':[4],'article':[3],'kai_notes':[5,8]}
 check('7ordinary_1mixed_1article_2kai_complete_partition',sum(map(len,categories.values()))==11 and sorted(p for positions in categories.values() for p in positions)==list(range(1,12)) and all(root['rows'][i-1]['visual_status']=='CARRIER_SEQUENCE_LOCATED_NOT_FULLY_DECOMPOSED' for i in categories['ordinary_only']) and root['rows'][3]['visual_status']=='MIXED_CARRIER_AND_MARK_CLUSTER_UNRESOLVED' and root['rows'][2]['visual_status']=='ROUND_CARRIER_WITH_UPPER_MARKS' and all(root['rows'][i-1]['visual_status']=='VERTICAL_DOT_NOTE' for i in categories['kai_notes']))
 check('mixed_word_not_counted_as_wholly_literal',result['count_clarification'].startswith('7 ordinary-only positions + 1 mixed carrier/shorthand word + article + 2 kai notes =11.') and not root['full_independent_transcription'] and not root['source_writer_constructed'])
 times={'registered':reg['registered_utc'],'ROOT_frozen':root['frozen_utc'],'C_recorded':C['recorded_utc'],'B_frozen':B['frozen_at_utc'],'print_partial':print_packet['recorded_utc'],'post_exchange_view':post['recorded_utc'],'result_closed':result['closed_utc']}
 check('local_registration_before_all_initial_observer_records',all(time(reg['registered_utc'])<time(times[k]) for k in ('ROOT_frozen','C_recorded','B_frozen')))
 check('all_initial_packets_before_documented_postexchange_view_result',all(time(times[k])<time(post['recorded_utc'])<=time(result['closed_utc'])<=time(reg['checkpoint_utc']) for k in ('ROOT_frozen','C_recorded','B_frozen')) and post['after_observer_C_and_B_frozen'] and post['prior_root_packet_unchanged'])
 check('documented_prefreeze_nonexchange_claims_retained',not root['other_new_observer_packets_seen'] and not B['scope']['root_new_observation_read_before_freeze'] and 'Root new observations and Observer B not read' in C['exposure'],'Packet declarations only. No independent secrecy or communication chronology certification; public push was during first view, not a public-before-view claim.')
 check('print_assisted_construction_separate_from_initial_root_packet',time(root['frozen_utc'])<time(print_packet['recorded_utc'])<time(post['recorded_utc']) and print_packet['after_root_freeze'] and not print_packet['other_observer_packets_seen'] and print_packet['ordinary_abbreviations_expanded_by_editor'])
 cases=B['finite_partial_rule']['admitted_cases'];observations={o['id']:o for o in B['native_observations']};equations=[]
 for c,example in zip(cases,result['source_local_examples']):
  s=c['retained'];letter=c['letter'];gap=c['gap'];output=s[:gap]+letter+s[gap:];o=observations[c['case']]
  passed=letter in ('τ','μ') and isinstance(gap,int) and 0<=gap<=len(s) and output==c['unaccented_output']==example['output'] and s==example['retained']==o['literal_carrier'] and letter==example['insert']==o['editorial_supplied_letter'] and gap==example['gap']==o['insertion_gap'] and o['native_gap_uniquely_resolved']
  check(c['case']+'_registered_annotation_insertion_equation',passed)
  equations.append({'case':c['case'],'retained':s,'insert':letter,'gap':gap,'computed_output':output,'equation_consistent':passed,'native_reading_certified_by_validator':False})
 check('only_two_annotation_level_resolved_cases_not_total_writer',len(cases)==len(result['source_local_examples'])==result['source_local_annotation_cases']==2 and B['finite_partial_rule']['level']=='Annotated source-carrier strings, not pixels or a self-classifying glyph decoder')
 check('AUTOS_edition_assistance_preserved', 'Allen assistance' in observations['B_AUTOS']['ordinary_expansion'] and result['source_local_examples'][1]['dependency']=='αυ ligature reading is edition-assisted')
 check('TOIS_attachment_ambiguity_and_other_withheld_cases_preserved',observations['B_TOIS']['native_gap_uniquely_resolved'] is False and len(B['finite_partial_rule']['withheld_cases'])==3 and any('B_TOIS' in c for c in B['finite_partial_rule']['withheld_cases']) and any('B_DOUBLE_NOTE' in c for c in B['finite_partial_rule']['withheld_cases']))
 check('all_C_unknowns_and_editorial_locator_limits_preserved',all(w['editorial_word_is_locator_not_pixel_reading'] and w['box_is_measured_segmentation'] is False and w['exact_native_word_writer_status']=='UNRESOLVED' and bool(w['unknowns']) for w in C['words']) and not C['complete_sentence_decision']['all_11_exact_native_carrier_sequences_recovered'] and not C['complete_sentence_decision']['complete_finite_source_writer_demonstrated'])
 check('result_partial_disagreements_not_rule_contradiction',result['status']=='PARTIAL_SOURCE_INSERTIONS_FULL_NATIVE_WRITER_UNRESOLVED' and result['outcome_class']=='incomplete source recovery, not historical-rule contradiction' and len(result['disagreements_and_unknowns'])==4 and not result['full_independent_native_transcription'] and not result['full_writer_constructed'])
 check('source_only_unrun_transfer_target_and_zero_Voynich_meanings',result['source_only'] and result['selected_sentence_editorial_words']==11 and not result['nonseed_source_transfer_run'] and not result['target_fit_run'] and not result['new_voynich_access'] and not reg['voynich_access'] and not reg['target_key_selected'] and result['confirmed_voynich_words']==result['independent_semantic_confirmation_capacity']==root['confirmed_voynich_words']==C['confirmed_voynich_meanings']==0 and C['no_voynich_access'] and B['scope']['target_access'] is False)
 check('postfreeze_view_disclosed_without_total_recovery',post['status']=='SUPPLEMENTAL_VIEW_NO_TOTAL_WRITER' and post['after_observer_C_and_B_frozen'] and 'no second-sentence application' in post['decision'])
 check('all_original_bound_packets_unchanged_after_checks',all(sha(relative(D,p))==h for p,h in result['artifacts'].items()))
 failures=[c for c in checks if c['status']=='FAIL'];limits=['PASS certifies file/hash receipts, position accounting, annotation arithmetic and preserved claim limits only. Native shapes, carrier readings, mark multiplicity, visual completeness and historical letter values were not re-viewed or certified.',
 'Initial packet timestamps and declared nonexchange support the recorded protocol; absence of communications or secrecy is not independently established. Local registration preceded records; no public-before-view blindness barrier is claimed.',
 'Seven ordinary-only positions plus one mixed position, article and two kai notes total eleven. Eight recognizable-letter positions include the mixed word and are not eight wholly literal inputs.',
 'Two annotation insertion equations require supplied retained sequence, justified letter role and resolved insertion gap. αυ interpretation remains edition-assisted. TOIS span/gap and doubled-note lexical expansion stay withheld.',
 'Print-assisted partial construction and later native crop/display are disclosed post-root-freeze/source observations, not independently completed writer or nonseed transfer tests.',
 'No new images viewed by this validator, source fetch, solver/control corpus, Voynich fit, target access, semantic confirmation or confirmed Voynich word.']
 report={'task':'GD_GREEK_WORD_ALIGNMENT','status':'FAIL_RECEIPT_ACCOUNTING' if failures else 'PASS_SOURCE_RECEIPT_ACCOUNTING_ONLY','visual_truth_validation':False,'semantic_validation':False,'scientific_PASS_certified':False,'checks':checks,'failed_checks':len(failures),'editorial_words':expected,'editorial_position_categories':categories,'annotation_equations':equations,'documented_timestamps':times,'disagreements_and_unknowns':result['disagreements_and_unknowns'],'source_image_pins':image_pins,'result_json_sha256':sha(D/'GD_GREEK_WORD_ALIGNMENT_RESULT.json'),'result_md_sha256':sha(D/'GD_GREEK_WORD_ALIGNMENT_RESULT.md'),'validator_sha256':sha(pathlib.Path(__file__)),'manual_unverified_limits':limits}
 (D/'GD_GREEK_WORD_ALIGNMENT_VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 text=['# Greek word alignment independent receipt/accounting validation','',report['status']+'. Visual truth and semantic validation: false.','',f'{len(checks)-len(failures)}/{len(checks)} receipt/accounting checks passed.','',
 'All nine bound dossier artifacts and the three registered source-image hashes match. Both root/C tables preserve the same eleven registered editorial words and positions. Seven ordinary-only positions, one mixed carrier/shorthand word, the article and two kai notes total eleven; the mixed word is not counted as wholly literal.','',
 'The two supplied annotation equations are consistent: εν + μ at gap0 → μεν; αυος + τ at gap2 → αυτος. This checks arithmetic on declared strings, not native readings. αυ is edition-assisted; TOIS attachment, ordinary ligatures, mixed-word multiplicity and doubled-note lexical expansion remain unresolved.','',
 'Local registration predates all initial packets; initial records predate the documented postexchange view/result. Declared nonexchange is retained without independent secrecy certification. Public push during the first view is disclosed; no public-before-view claim is made.','',
 'Source recovery remains PARTIAL. No full writer, nonseed transfer, target fit, Voynich access or confirmed meaning follows.','',
 'Manual/unverified limits:','']+['- '+x for x in limits]
 if failures:text+=['','Failed checks:','']+['- '+c['check'] for c in failures]
 (D/'GD_GREEK_WORD_ALIGNMENT_VALIDATION.md').write_text('\n'.join(text)+'\n')
 print(json.dumps({'status':report['status'],'checks':len(checks),'failures':[c['check'] for c in failures],'visual_truth_validation':False}));return bool(failures)
if __name__=='__main__':raise SystemExit(main())
