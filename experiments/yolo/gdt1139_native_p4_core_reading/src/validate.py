#!/usr/bin/env python3
"""GDT1139 protocol/source/pixel identity checks, never visual adjudication.
Images are decoded only for byte-level pixel equality, never displayed/changed.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime
import hashlib,json
from PIL import Image
BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[2]
ART=BASE/'artifacts'
PLAN_SHA='d897b35aa1662cd7eecf8c4b3b4be5e368e6adbdfce7ac6c7e61dcd2d279ec5d'
METHOD_SHA='36117d6b65555cd1cf54f021c12112af5216976e06f73926c0797fffd2348771'
OLD_METHOD_SHA='eb2f289b72787a17b379ef95fafd82fa670b7e71197d495102ec5a0d3625add5'
FINAL_PINS={
'src/SOURCE.json':'d46d42f7f30a9846a224bb039f30ef05afb7a1dc977e9788330463a61ccb5540',
'artifacts/CROP_RECEIPT.json':'2520d11f07ab60f7d59fd84a769d3adfad790787e5e32b9ff4bbc09f182a5622',
'artifacts/REGISTRATION_RECEIPT.json':'e10be4753fc674f42b1c9f782d9a880299d4e9915de14428f43bb00188315489',
'artifacts/ROOT_NATIVE.json':'e9f0ae305aff4605b1ee35a89e78b50d38fbec662ef7a188822ba65a0eff877e',
'artifacts/ROOT_NATIVE.md':'8f9a46dfae98b44ec43eebf6ac0f7f0217d0ef77318eb69e8fc1b4b5eb7cbb40',
'artifacts/OBSERVER_NATIVE.json':'7a7fac805c116ebf658334b205a10b4f0cd5b1e3bc3448a9d3d8f391f1aef769',
'artifacts/OBSERVER_NATIVE.md':'b83e412ed27843ab6162f92572f2e85712a7fa2f97beb587eb557141a2a5237e',
'artifacts/ROOT_FREEZE.json':'c3565618aadbb0a0b12f6a3401ab581eacf5908e8c377a26ea34694ae31b2648',
'artifacts/RESULT.json':'024647d48a91e72aa73543e4b0bc448182748621aacc39a295ea9981cb9dbcce',
'artifacts/COMPARISON_FREEZE.json':'d5efeff6e828d7a235f6c22557c5187fbcfc4724e8092301bfee5270baed0ad0',
'artifacts/TIMESTAMP_CORRECTION.json':'2188d2b67ce1d5593ba858dc11fd3ea097e9447e596a1ed1406e7056c4d9ae55',
'REPORT.md':'f5a846f488969010ce0b7930d971787d61721a7b97559402cb2d7a115308894c'}
OLD1137={'src/core.py':'592e070b934c54ff7e5965ed7a4ee1cd6789b14cd4d59de216a40d229e54ec02','src/CORE_FREEZE.json':'b59b793c6a5e7c811e70cfb5c6af5a8b186598858d219a95295931cf6bd74cb0','src/author.py':'7cc3c8c1562cfc1e5440f7e4ca0bf5e13dcaa3bb341e52388660af4896c10c96','artifacts/AUTHOR_ACCOUNT.json':'77a12a678693e5630bd4506d5c59419917507a58373a2913615a9298137e6785','AUTHOR_READING.md':'2f7bc029c318ddbcd12b5fb264d41ca25515b30a8c43fda636665902c4333eff','AUTHOR_RECEIPT.json':'84e93e3230ba6621a391b005f1eee678ee96f50105ed80229f0ce4cf9c6f26b8','artifacts/NATIVE_SOURCE.json':'40fab9cdfced7433f9b250d811bdcc654b3e5c17370eeb43d156f9bc474d6b2d','experiment.json':'88f96f902f836328dd3fc0b093727fb741a45bf4c3c52c61e94f1accbe688b2e'}
FOCAL=[('f83r.25',4,'qokedy'),('f83r.25',5,'chedy'),('f83r.26',5,'shedy'),('f83r.27',2,'chedy'),('f83r.28',3,'sheey'),('f83r.28',4,'qokedy'),('f83r.28',5,'shedy'),('f83r.29',1,'solchedy'),('f83r.29',2,'cheey'),('f83r.29',3,'qody')]
CONTROLS=[('f83r.25',6,'otal'),('f83r.26',4,'tol')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
def repo(path):
 p=Path(path)
 if p.is_absolute() or '..' in p.parts:raise ValueError('Unsafe receipt path')
 return ROOT/p

def stamp(s):return datetime.fromisoformat(s.replace('Z','+00:00'))
def packed(obj):return (json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
def main():
 source=load(BASE/'src/SOURCE.json');reg=load(ART/'REGISTRATION_RECEIPT.json');crops=load(ART/'CROP_RECEIPT.json');root=load(ART/'ROOT_NATIVE.json');fresh=load(ART/'OBSERVER_NATIVE.json');freeze=load(ART/'ROOT_FREEZE.json');comparison=load(ART/'COMPARISON_FREEZE.json');result=load(ART/'RESULT.json');correction=load(ART/'TIMESTAMP_CORRECTION.json');manifest=load(BASE/'experiment.json')
 input_before={p:sha(BASE/p) for p in FINAL_PINS};finalpins={p:input_before[p]==v for p,v in FINAL_PINS.items()}
 checks={'release_file_pins':all(finalpins.values()),'frozen_validation_plan':sha(ART/'VALIDATION_PLAN.md')==PLAN_SHA,
 'registered_method_preregistration':sha(BASE/'METHOD.md')==sha(BASE/'PREREGISTRATION.md')==METHOD_SHA==reg['method_sha256'],
 'source_image_pin':sha(repo(source['image']['path']))==source['image']['sha256'],
 'source_native_pin':sha(repo(source['native_packet']['path']))==source['native_packet']['sha256']}
 olddir=ROOT/'experiments/yolo/gdt1137_material_process_type_return';oldchecks={p:sha(olddir/p)==v for p,v in OLD1137.items()};checks['old1137_frozen_pins']=all(oldchecks.values())
 owned={str((BASE/n).relative_to(ROOT)) for n in ['src/validate.py','artifacts/VALIDATION.json','artifacts/VALIDATION.md']}
 registered={x['path']:sha(repo(x['path']))==x['sha256'] for x in manifest['inputs']+manifest['outputs'] if x['path'] not in owned};checks['registered_tree_pins_except_owned_validation_outputs']=all(registered.values())
 prefix='# GDT1139 method\n\n## Question\n\nTODO\n\n## Inputs\n\nTODO\n\n## Method\n\nTODO\n\n## Decision rule and claim ceiling\n\nTODO\n'
 checks['method_snapshot_only_template_cleanup']=digest(prefix.encode()+(BASE/'METHOD.md').read_bytes())==OLD_METHOD_SHA==reg['plan_method_snapshot_sha256']
 checks['registration_retains_original_plan']=reg['validation_plan_sha256']==PLAN_SHA and reg['pixels_viewed'] is False
 native=load(repo(source['native_packet']['path']));retained=load(ART/'NATIVE_SOURCE.json');rows=native['rows'];ids=[r['source_group_id'] for r in rows];counts=Counter(r['edition'] for r in rows)
 checks['all97_native_bytes_fields_order']= (ART/'NATIVE_SOURCE.json').read_bytes()==repo(source['native_packet']['path']).read_bytes() and retained==native and len(rows)==len(set(ids))==97
 checks['reader_counts_and_scope']=dict(counts)=={'ZL3b':33,'IT2a':32,'RF1b':32} and {r['locus'] for r in rows}=={f'f83r.{n}' for n in range(25,31)} and {r['page'] for r in rows}=={'f83r'}
 it={(r['locus'],int(r['source_group_index'])):r for r in rows if r['edition']=='IT2a'}
 checks['exact_source_focal_inventory']=[(r['locus'],r['IT_group'],r['literal']) for r in source['focal_positions']]==FOCAL
 checks['all_seven_core_form_occurrences_included']= [(r['locus'],int(r['source_group_index']),r['ivtff_group_raw']) for r in rows if r['edition']=='IT2a' and r['ivtff_group_raw'] in {f[2] for f in FOCAL}]==FOCAL
 checks['two_registered_controls_exact']=[(r['locus'],r['IT_group'],r['literal']) for r in source['controls']]==CONTROLS and all(it[l,i]['ivtff_group_raw']==w for l,i,w in CONTROLS)
 image=Image.open(repo(source['image']['path']));image.load();pixelchecks=[]
 checks['original_dimensions_and_crop_provenance']=list(image.size)==source['image']['dimensions']==crops['original_size'] and crops['original']==source['image']['path']
 names=['P4_UNIT.png','P4_ROW25.png','P4_ROW28.png','P4_ROW29.png'];checks['four_fixed_crop_inventory']=[Path(c['path']).name for c in crops['crops']]==names
 for item in crops['crops']:
  box=item['box'];valid=len(box)==4 and all(type(x) is int for x in box) and 0<=box[0]<box[2]<=image.width and 0<=box[1]<box[3]<=image.height
  crop=Image.open(repo(item['path']));crop.load();expected=image.crop(box) if valid else None
  pixelchecks.append({'path':item['path'],'box':box,'in_bounds_integer':valid,'hash_matches':sha(repo(item['path']))==item['sha256'],'mode':crop.mode,'dimensions':list(crop.size),'exact_original_pixels':valid and crop.mode==expected.mode and crop.size==expected.size and crop.tobytes()==expected.tobytes()})
 checks['all_crops_exact_original_pixels']=all(p['in_bounds_integer'] and p['hash_matches'] and p['exact_original_pixels'] for p in pixelchecks)
 paths=[source['image']['path']]+[c['path'] for c in crops['crops']]
 checks['fresh_declared_view_inventory']=fresh['view_count']==5 and [v['path'] for v in fresh['view_inventory']]==paths and all(v['view_count']==1 and sha(repo(v['path']))==v['sha256'] for v in fresh['view_inventory'])
 checks['root_declared_view_inventory']=root['view_inventory']==['original full-page once']+[n+' once' for n in names]
 observations=dict(result['observation_hashes']);checks['all_observation_freeze_hashes']=all(sha(repo(p))==v for p,v in {**freeze['hashes'],**observations,**comparison['hashes']}.items()) and all(observations[p]==v for p,v in freeze['hashes'].items())
 checks['root_preexchange_declarations']=freeze['fresh_observer_read'] is False and root['fresh_observer_record_read'] is False and root['frozen_utc']==freeze['utc']
 times={'registered_receipt':reg['utc'],'crop_created':crops['created_utc'],'root_frozen':freeze['utc'],'fresh_frozen':fresh['frozen_at_utc'],'comparison_record_written':comparison['utc'],'timestamp_correction':correction['utc']}
 checks['documented_chronological_order']=list(map(stamp,times.values()))==sorted(map(stamp,times.values())) and comparison['utc']==result['comparison_recorded_utc']
 commits=[crops['registration_commit'],fresh['release_registration_commit'],result['registration_commit']];checks['same_registration_commit_receipts']=len(set(commits))==1 and commits[0]=='119fb6484321abcdec85a0997209595b2918c7be'
 old_result={}
 for k,v in result.items():
  if k in ['comparison_recorded_utc','first_observer_record_open_time']:continue
  old_result[k]=v
  if k=='status':old_result['first_comparison_utc']=result['comparison_recorded_utc']
 checks['timestamp_correction_preserves_other_result_bytes']=digest(packed(old_result))==correction['old_result_sha256']
 old_freeze={k:v for k,v in comparison.items() if k!='timestamp_meaning'};old_freeze['hashes']=dict(old_freeze['hashes']);old_freeze['hashes'][str((ART/'RESULT.json').relative_to(ROOT))]=correction['old_result_sha256']
 checks['timestamp_correction_old_comparison_reconstructible']=digest(packed(old_freeze))==correction['old_comparison_freeze_sha256']
 checks['no_exact_first_open_time_claimed']='first_comparison_utc' not in result and 'Not separately clocked' in result['first_observer_record_open_time']
 observer_rows={r['row']:r for r in fresh['rows']};observer_counts={str(n):len(r['groups']) for n,r in observer_rows.items()};checks['fresh_all_six_rows_and33_apparent_groups']=set(observer_rows)==set(range(25,31)) and list(observer_counts.values())==[6,7,5,6,5,4] and sum(observer_counts.values())==33==result['fresh_apparent_groups'] and all([g['n'] for g in r['groups']]==list(range(1,len(r['groups'])+1)) and r['tentative'] and all(g['reading'] and g['shapes'] for g in r['groups']) for r in fresh['rows'])
 checks['root_all_six_context_rows']=len(root['full_context'])==6
 checks['root_fixed_control_records']=[(c['position'],c['literal']) for c in root['controls']]==[('.25G006','otal'),('.26G004','tol')]
 rootmap={(r['locus'],r['IT_group']):r for r in root['positions']};positions=result['positions'];checks['all_ten_root_and_comparison_rows_exact']=[(r['locus'],r['IT_group'],r['literal']) for r in root['positions']]==FOCAL and [(r['locus'],r['IT_group'],r['required_literal']) for r in positions]==FOCAL
 copied=[];aggregations=[]
 for p in positions:
  loc,i=p['locus'],p['IT_group'];g=observer_rows[int(loc.split('.')[-1])]['groups'][i-1];r=rootmap[loc,i]
  expected_variants=[{k:s[k] for k in ['edition','locus','source_group_index','ivtff_group_raw']} for s in rows if s['locus']==loc and int(s['source_group_index'])==i]
  copied.append(p['root_status']==r['status'] and p['root_reason']==r['visible_reason'] and p['fresh_reading']==g['reading'] and p['fresh_alternatives']==g['alternatives'] and p['fresh_shapes']==g['shapes'] and p['native_variants']==expected_variants and bool(p['reason']) and bool(p['confidence']))
  uncertain=r['status']=='UNRESOLVED' or p['fresh_status']=='UNRESOLVED' or r['status']!=p['fresh_status']
  rule=(p['status']=='UNRESOLVED') if uncertain else p['status']==r['status']==p['fresh_status']
  aggregations.append({'locus':loc,'IT_group':i,'status':p['status'],'root_status':r['status'],'fresh_status_assigned_in_comparison':p['fresh_status'],'conservative_status_rule':rule,'visible_truth_checked':False})
 checks['observation_fields_and_native_variants_uncensored']=all(copied)
 checks['conservative_aggregation_no_majority_override']=all(a['conservative_status_rule'] for a in aggregations)
 finalcounts=Counter(p['status'] for p in positions);checks['reported1_9_0_counts']=dict(finalcounts)=={'UNRESOLVED':9,'SUPPORTED_COMPATIBLE':1} and result['counts']=={'SUPPORTED_COMPATIBLE':1,'UNRESOLVED':9,'INCOMPATIBLE':0}
 checks['only_qody_compatible_sol_whole_unresolved']=[(p['locus'],p['IT_group']) for p in positions if p['status']=='SUPPORTED_COMPATIBLE']==[('f83r.29',3)] and next(p for p in positions if p['required_literal']=='solchedy')['status']=='UNRESOLVED'
 checks['registered_result_decision_and_ceilings']=result['status']=='RETAIN_WITH_UNRESOLVED_SOURCE_PREMISES' and result['confirmed_words']==result['independent_confirmation_capacity']==0 and result['meaning_selection'] is False and result['old_GDT1137_changed'] is False
 checks['crop_limitation_retained']='clip' in root['crop_limitations'] and any('clipped' in x for x in fresh['limitations']) and 'clipped' in result['cropping_limitation']
 input_after={p:sha(BASE/p)==v for p,v in input_before.items()};checks['review_did_not_change_released_files']=all(input_after.values())
 out={'status':('PROTOCOL_ACCOUNTING_AND_PIXEL_IDENTITY_PASS_VISUAL_TRUTH_UNVERIFIED' if all(checks.values()) else 'PROTOCOL_CHECK_FAILURE_VISUAL_TRUTH_UNVERIFIED'),'validator_sha256':sha(Path(__file__)),'plan_sha256':PLAN_SHA,'checks':checks,'released_pins_match':finalpins,'old1137_pins_match':oldchecks,'registered_pins_match_except_owned_validation_outputs':registered,'released_files_unchanged':input_after,'pixel_checks':pixelchecks,'image_dimensions':list(image.size),'native_context':{'rows':97,'fields_per_row':len(rows[0]),'reader_counts':dict(counts),'byte_identical':checks['all97_native_bytes_fields_order'],'fresh_row_apparent_groups':observer_counts,'fresh33_not_IT32_or_ZL33_normalization':True},'chronology':{'documented_times':times,'public_registration_commit':commits[0],'independent_publication_or_first_view_history_verified':False,'first_fresh_record_open':'Not separately clocked; declared interval after fresh freeze10:02:31 and before comparison writing10:04:37.976761','timestamp_correction_matches_original_except_disclosed_metadata':checks['timestamp_correction_preserves_other_result_bytes']},'aggregation_checks':aggregations,'final_counts':result['counts'],'native_status_adjudicated_by_validator':False,'scientific_or_meaning_PASS':False,'limitations':{'declared_control_completeness':'PARTIAL: upper OTAL control ascender clipped in unit/detail, no replacement view; whole page declared available. Numeric pixel identity does not certify visible whole-glyph completeness.','view_inventory_and_blindness':'Declared inventory meets bounds; actual unlogged access, exact first viewing/opening chronology and secrecy are independently UNVERIFIABLE.','visual_statuses':'Fresh status labels belong to root comparison, not a fresh observer ten-position vote. Their copied tentative evidence and conservative propagation are checked; glyph correctness, localization and confidence truth are UNVERIFIABLE here.','meaning':'No unique transcription, morpheme, English sense, source, batch, significance, independent confirmation or reserve capacity is established.'},'criteria':{'1':'PASS byte/receipt pins; documented chronology; secrecy/publication history UNVERIFIABLE','2':'PASS exact registered original RGB crop identity and bounds; inventory declarations only','3':'PASS full97 source bytes/fields/raw uncertainties/order conserved','4':'PASS ten occurrences/seven forms exact census and complete-return requirement','5':'PARTIAL control quality: full six-line record and fixed2 control inventory present; clipped OTAL ascender retained','6':'PASS documented separation and preserved freezes; actual blind access UNVERIFIABLE','7':'PASS copied evidence and conservative1/9/0 aggregation; visual truth UNVERIFIABLE','8':'PASS retain unresolved premises, unchanged1137 hashes and0 meanings','9':'PASS source/visual/meaning ceilings; no incident-hit expansion or new views by validator'},'no_images_displayed':True,'no_images_or_observer_files_modified':True}
 (ART/'VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 md=['# GDT1139 independent protocol validation','', '**Receipt, source-conservation and exact-pixel checks pass. Visual truth is not adjudicated. The retained result is1 compatible,9 unresolved,0 incompatible.**','',
 'The bound2753×3745 RGB original matches its registered SHA256. Unit and all three detail PNGs numerically equal the specified original-pixel rectangles, with identical modes/dimensions and no resampling. No image was displayed, redrawn or changed. Declared inventories meet one page/one unit/three details per observer; actual unlogged views cannot be independently excluded.','',
 'The complete97-row native packet is byte-identical to GDT1137, preserving all19 fields/order (ZL33/IT32/RF32). All10 focal occurrences and both fixed controls are represented. Fresh observation retains33 apparent groups with row counts6/7/5/6/5/4; row26 end split is preserved, without normalization to native counts. The informed root supplies all six row contexts and10 focal records. All compared tentative strings, alternatives, shapes, root reasons and alternate native spellings are copied exactly.','',
 'Every unclear/disagreeing focal observation remains UNRESOLVED; there is no majority override. Only QODY .29G003 is classed compatible. Whole SOLCHEDY remains unresolved; a plausible tail does not supply SOL. This checks consistency of the comparison with its recorded evidence and declared statuses, not whether any glyph/status/confidence is visually correct. Fresh focal status labels were assigned in the informed comparison, not separately voted by the fresh observer.','',
 'Control quality remains partial: the OTAL upper ascender is reported clipped in the unit/detail, and neither observer repairs it. The full page was declared available. Fixed control coverage is present, but complete visible control interpretation is not certified. Numeric exact-pixel identity does not establish sufficient source quality or correct localization.','',
 'Documented times are registration09:56:00, crops09:56:40.199504, root freeze09:58:42.890983, fresh freeze10:02:31 and comparison write10:04:37.976761UTC. First fresh-record open was not separately clocked; it is only declared between the latter two times. The timestamp correction at10:05:59.967324 is preserved; reconstructing the old RESULT metadata yields its exact prior hash, proving other result bytes unchanged. This is receipt chronology, not independently certified secrecy, publication/view history or expert independence.','',
 'The plan stays unchanged. Reattaching only the documented removed generator TODO prefix to final METHOD reconstructs its earlier snapshot hash exactly. Registered final METHOD/PREREGISTRATION/source/observer-plan pins match. GDT1137 core, freeze, author, account, reading, receipt, source and expected manifest all remain pinned unchanged.','',
 '| Frozen criterion | Outcome |','|---|---|']
 md.extend('| '+k+' | '+v+' |' for k,v in out['criteria'].items())
 md+=['','Reproduce: `python experiments/yolo/gdt1139_native_p4_core_reading/src/validate.py`. It performs only hash, numerical pixel, native field and recorded-protocol comparisons, writing its own validation files. No new target query or pixel viewing.','', 'Validator SHA256: `'+out['validator_sha256']+'`. Frozen plan SHA256: `'+PLAN_SHA+'`.','']
 if not all(checks.values()):md[2]='**Protocol checks failed: '+', '.join(k for k,v in checks.items() if not v)+'. Visual truth remains unverified.**'
 (ART/'VALIDATION.md').write_text('\n'.join(md))
 print(json.dumps({'status':out['status'],'checks':checks,'validator_sha256':out['validator_sha256']},indent=2))
 return 0 if all(checks.values()) else 1
if __name__=='__main__':raise SystemExit(main())
