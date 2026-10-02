#!/usr/bin/env python3
"""Numerical crop/receipt audit; deliberately does not adjudicate pixels."""
import hashlib,json,sys
from datetime import datetime
from pathlib import Path
from PIL import Image
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1];REPO=BASE.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def utc(s):
    d=datetime.fromisoformat(s.replace('Z','+00:00'))
    assert d.tzinfo is not None
    return d

def local(path):
    p=Path(path)
    if p.is_absolute() or '..' in p.parts:raise ValueError('receipt paths must be scoped relative paths')
    return BASE/p

def statuses(obs):
    return {k:v['status'] if isinstance(v,dict) else v for k,v in obs['seams'].items()}
def location_status(obs):return obs['location'].split(':',1)[0].strip()

def main():
    checks=[]
    def check(name,ok,detail=None):checks.append({'name':name,'pass':bool(ok),**({'detail':detail} if detail is not None else {})})
    source=read(BASE/'src/SOURCE.json');lock=read(BASE/'src/PREREG_LOCK.json');display=read(BASE/'artifacts/DISPLAY.json')
    required=['METHOD.md','PREREGISTRATION.md','src/SOURCE.json','src/PREREG_LOCK.json','src/run.py','artifacts/DISPLAY.json','artifacts/RESULT.json',
      'artifacts/OBSERVER_A.json','artifacts/OBSERVER_A_FREEZE.json','artifacts/OBSERVER_B.json','artifacts/OBSERVER_B_FREEZE.json']
    for receipt in ['COMPARISON_RECEIPT.json','PROTOCOL_ORDER.json']:
        if (BASE/'artifacts'/receipt).exists():required.append('artifacts/'+receipt)
    paths=[BASE/p for p in required]+[local(display['source']),local(display['crop_path'])]+[REPO/p['path'] for p in source['inputs']]
    pins={str(p.relative_to(REPO)):sha(p) for p in paths}
    check('registered_method_prereg_source_exact_pins',all(sha(BASE/p)==h for p,h in lock['hashes'].items()))
    check('four_access_and_predecessor_pins',all(sha(REPO/p['path'])==p['sha256'] for p in source['inputs']))
    original=local(display['source']);crop_path=local(display['crop_path'])
    check('original_image_byte_identity',sha(original)==source['image']['sha256']==display['source_sha256'])
    check('display_crop_byte_identity',sha(crop_path)==display['crop_sha256'])
    box=display['crop_box_xyxy']
    validbox=isinstance(box,list) and len(box)==4 and all(type(v)==int for v in box) and 0<=box[0]<box[2]<=source['image']['width'] and 0<=box[1]<box[3]<=source['image']['height']
    check('crop_coordinates_inside_registered_original',validbox)
    with Image.open(original) as im,Image.open(crop_path) as crop:
        source_size=list(im.size);crop_size=list(crop.size);modes=[im.mode,crop.mode];formats=[im.format,crop.format]
        expected=im.crop(tuple(box))
        check('registered_original_and_display_dimensions',source_size==[source['image']['width'],source['image']['height']]==display['source_size'])
        pixelmatch=bool(validbox and crop.size==expected.size and crop.mode==expected.mode and crop.tobytes()==expected.tobytes() and crop.format=='PNG')
        check('lossless_display_crop_exact_pixel_match',pixelmatch)
    observations={};freezes={};times={};registered=utc(lock['registered_utc'])
    keys={'motif1_to_motif2','motif2_to_motif3','motif3_to_minims'};allowed={'SPACE_LIKE','INTERNAL_LIKE','UNRESOLVED'}
    for who in ['A','B']:
        obs=read(BASE/f'artifacts/OBSERVER_{who}.json');freeze=read(BASE/f'artifacts/OBSERVER_{who}_FREEZE.json');observations[who]=obs;freezes[who]=freeze
        check(who+'_observation_freeze_byte_identity',all(local(freeze[k])==BASE/f'artifacts/OBSERVER_{who}.json' for k in ['file','artifact'] if k in freeze) and any(k in freeze for k in ['file','artifact']) and sha(BASE/f'artifacts/OBSERVER_{who}.json')==freeze['sha256'])
        check(who+'_complete_frozen_rating_fields',location_status(obs) in {'LOCATED','UNRESOLVED_LOCATION'} and set(obs['seams'])==keys and all(statuses(obs)[k] in allowed for k in keys) and all(k in obs and bool(obs[k]) for k in ['relative_ordering','legibility','limitations']))
        check(who+'_registered_source_image_and_declared_line_scope',obs['image_sha256']==source['image']['sha256'] and isinstance(obs['line'],str) and bool(obs['line']) and (who=='B' or obs['line']=='f81r.5'))
        check(who+'_declared_freeze_source_crop_identity',all(freeze[k]==expected for k,expected in [('source_sha256',source['image']['sha256']),('context_sha256',display['crop_sha256'])] if k in freeze))
        observed=utc(obs['observed_utc']);frozen=utc(freeze['frozen_utc']);times[who]={'observed_utc':obs['observed_utc'],'frozen_utc':freeze['frozen_utc']}
        check(who+'_recorded_registration_observation_freeze_order',registered<=observed<=frozen)
    check('recorded_A_freeze_before_B_observation_and_freeze',utc(freezes['A']['frozen_utc'])<=utc(observations['B']['observed_utc'])<=utc(freezes['B']['frozen_utc']))
    rating=[statuses(observations[k])['motif3_to_minims'] for k in ['A','B']]
    decision='NATIVE_SEAM_UNRESOLVED' if any(location_status(observations[k])!='LOCATED' for k in ['A','B']) or any(r=='UNRESOLVED' for r in rating) or len(set(rating))!=1 else {'SPACE_LIKE':'LOCAL_SEPARATION_SUPPORTED','INTERNAL_LIKE':'LOCAL_JOIN_SUPPORTED'}[rating[0]]
    result=read(BASE/'artifacts/RESULT.json')
    check('fixed_two_observer_decision_no_averaging',result['decision']==decision)
    check('result_exact_rating_and_source_account',result['observer_seams']=={k:statuses(o) for k,o in observations.items()} and result['source_image_sha256']==source['image']['sha256'] and result['experiment']=='GDT1152')
    check('result_retains_old_refutation_and_zero_meaning_capacity',result['GDT1151']=='UNCHANGED_REFUTED_FIXED_PAIRED_FIELD_SCOPE' and result['confirmed_words']==0 and result['independent_meaning_confirmation_capacity']==0 and result['significance']=='NOT_CLAIMED')
    comparison=None
    receipt_path=BASE/'artifacts/COMPARISON_RECEIPT.json'
    if receipt_path.exists():
        comparison=read(receipt_path)
        check('recorded_successful_result_after_both_freezes',all(utc(comparison['successful_result_recorded_utc'])>=utc(f['frozen_utc']) for f in freezes.values()))
        check('comparison_receipt_result_hash',comparison['result_sha256']==sha(BASE/'artifacts/RESULT.json'))
    protocol=read(BASE/'artifacts/PROTOCOL_ORDER.json') if (BASE/'artifacts/PROTOCOL_ORDER.json').exists() else None
    if protocol is not None:
        check('protocol_order_record_explicitly_not_exact_delivery_clock',protocol['kind']=='ROOT_PROTOCOL_ORDER_ATTESTATION_NOT_INDEPENDENT_CLOCK_PROOF' and protocol['B_task_exact_delivery_utc'] is None)
    check('all_registered_observation_image_runner_and_result_bytes_unchanged',all(sha(REPO/p)==h for p,h in pins.items()))
    out={'experiment':'GDT1152','accounting_pass':all(c['pass'] for c in checks),'checks':checks,'independently_reconstructed_decision':decision,
      'observer_rating_summary':{k:{'location_status':location_status(o),'original_location':o['location'],'seams':statuses(o)} for k,o in observations.items()},
      'image_numeric_audit':{'source_size':source_size,'crop_box_xyxy':box,'crop_size':crop_size,'modes':modes,'formats':formats,'pixel_identity_verified':pixelmatch,'image_visually_viewed_by_validator':False},
      'recorded_chronology':{'registered_utc':lock['registered_utc'],'observers':times,'comparison_receipt':comparison,'protocol_order_attestation':protocol},
      'schema_adapter':'B detailed seam objects use their explicit status field; LOCATED colon description supplies explicit location label; B artifact key and A file key identify their respective frozen observation paths. Original observations remain unchanged.',
      'unverified_protocol_edges':['B line field is a descriptive native-row locator rather than a transcription ID; matching the actual manuscript row and seam remains visual/manual.', 'Exact first unsuccessful score invocation time was not recorded; comparison clock is the successful result recording time.','Exact B-task delivery time was not recorded. Root reports tool-call order A write/freeze completed before B task dispatch; this audit does not independently certify delivery time or secrecy.'],
      'validator_sha256':sha(Path(__file__)),'bound_hashes':pins,
      'limits':['Accounting PASS and pixel identity do not certify visual spacing judgments or correct native line/seam identification.','B has limited rating independence; prior exposure and the mandatory live route preclude perfect research blinding.','Matching ratings are not independent manuscript witnesses or semantic confirmation.','Outcome supports only the disputed local physical seam description; no word identity, general parser, meaning, significance or revised GDT1151 result.']}
    (BASE/'artifacts/VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'accounting_pass':out['accounting_pass'],'checks':len(checks),'failed':[c['name'] for c in checks if not c['pass']],'decision':decision}))
    return 0 if out['accounting_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
