#!/usr/bin/env python3
"""Independent source/crop/chronology accounting, not perceptual adjudication."""
from collections import Counter,defaultdict
from datetime import datetime,timezone
import gzip
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'


def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def digest(raw):return hashlib.sha256(raw).hexdigest()

def time_value(text):
    if text.endswith(' UTC'):return datetime.strptime(text,'%Y-%m-%d %H:%M:%S UTC').replace(tzinfo=timezone.utc)
    value=datetime.fromisoformat(text.replace('Z','+00:00'));assert value.tzinfo is not None
    return value.astimezone(timezone.utc)


def check_lock(name):
    data=read(A/name)
    for relative,expected in data['hashes'].items():
        assert not Path(relative).is_absolute()
        assert sha(ROOT/relative)==expected,relative
    return data


def source_accounting(spec):
    prior=ROOT/'experiments/yolo/gdt1342_qoky_written_predecessor/artifacts/SOURCE.json.gz'
    old=read(prior)
    chosen=[row for row in old if row['page']=='f83r' and row['locus'] in ('f83r.2','f83r.5','f83r.8')]
    packet=read(ROOT/spec['source_packet']);assert sorted(packet,key=lambda row:row['id'])==sorted(chosen,key=lambda row:row['id']) and len(packet)==81
    assert len({row['id'] for row in packet})==81
    assert {row['edition'] for row in packet}=={'ZL3b','IT2a','RF1b'}
    lines=defaultdict(list)
    for row in packet:lines[(row['edition'],row['locus'])].append(row)
    assert len(lines)==9
    for key,rows in lines.items():
        assert sorted(int(row['index']) for row in rows)==list(range(1,len(rows)+1))
        assert all(int(row['count'])==len(rows) for row in rows)
    byid={row['id']:row for row in packet}
    expected_prototypes={'REF_LOW':'ZL3b|f83r.2|G002','REF_A':'ZL3b|f83r.2|G007','REF_B':'ZL3b|f83r.2|G003'}
    expected_targets={'TARGET_X':'ZL3b|f83r.8|G003','TARGET_Y':'ZL3b|f83r.5|G003'}
    assert spec['prototype_ids']==expected_prototypes and spec['target_ids']==expected_targets
    assert all(gid in byid for gid in [*expected_prototypes.values(),*expected_targets.values()])
    assert spec['expected_high_template']=={'TARGET_X':'REF_A','TARGET_Y':'REF_B'}
    # These identify source-string classes only, not visual segmentation or meanings.
    expected_raw={'REF_LOW':'cheey','REF_A':'qoteedy','REF_B':'qokaiin','TARGET_X':'shecthedchy','TARGET_Y':'checkhy'}
    for tag,gid in {**expected_prototypes,**expected_targets}.items():assert byid[gid]['raw']==expected_raw[tag]
    old_targets={'ZL3b|f83r.21|G009','ZL3b|f83r.23|G006','ZL3b|f83r.23|G007'}
    assert set(spec['old_target_ids_not_reused'])==old_targets and old_targets.isdisjoint(expected_targets.values())
    old_packet_path=ROOT/'experiments/yolo/gdt1348_graphic_component_check/artifacts/SOURCE_PACKET.json'
    old_rows=read(old_packet_path)['rows'];assert old_targets<={row['id'] for row in old_rows}
    return {'rows':81,'source_lines':9,'readers':3,'old_source_sha256':sha(prior),
            'old1348packet_sha256':sha(old_packet_path),'new_target_ids_distinct':True,
            'source_class_map_verified':True,'actual_pixel_to_word_localization':'MANUAL_ONLY_NOT_ESTABLISHED_BY_THIS_ACCOUNTING'}


def pixel_accounting(spec):
    source_path=ROOT/spec['source_image'];receipts=read(A/'IMAGE_RECEIPTS.json')
    assert sha(source_path)==spec['source_image_sha256']==receipts['source_sha256']
    assert receipts['source_url']==spec['source_url']
    checks=[]
    with Image.open(source_path) as source:
        source.load();assert list(source.size)==spec['source_size']==receipts['source_dimensions']==[2753,3745]
        native=np.asarray(source);icc=source.info.get('icc_profile')
        assert isinstance(icc,bytes) and icc
        entries=list(receipts['crops'])
        assert {entry['id'] for entry in entries}=={'REF_LOW','REF_A','REF_B','TARGET_X','TARGET_Y'} and len(entries)==5
        entries.append({'id':'LOCALIZER_STRIP','path':str((E/'source/LOCALIZER_STRIP.png').relative_to(ROOT)),
                        'box_xyxy':receipts['localizer_strip_box'],'sha256':receipts['localizer_strip_sha256']})
        for entry in entries:
            path=ROOT/entry['path'];assert not Path(entry['path']).is_absolute()
            assert sha(path)==entry['sha256']
            x0,y0,x1,y1=entry['box_xyxy']
            assert all(type(v) is int for v in (x0,y0,x1,y1))
            assert 0<=x0<x1<=source.width and 0<=y0<y1<=source.height
            with Image.open(path) as crop:
                crop.load();assert crop.mode==source.mode and crop.size==(x1-x0,y1-y0)
                if 'dimensions' in entry:assert entry['dimensions']==list(crop.size)
                assert np.array_equal(np.asarray(crop),native[y0:y1,x0:x1])
                assert crop.info.get('icc_profile')==icc
                checks.append({'id':entry['id'],'box_xyxy':entry['box_xyxy'],
                               'dimensions':list(crop.size),'same_native_pixels':True,'icc_preserved':True,'sha256':sha(path)})
    return {'source_sha256':sha(source_path),'dimensions':[2753,3745],'icc_bytes':len(icc),
            'icc_sha256':digest(icc),'crops':checks,'localization_verified_by_pixels':False}


def observer_accounting(spec,registration,crop_lock,analysis_lock):
    a=read(A/'STAGE_A.json');a_lock=read(A/'STAGE_A_LOCK.json');delivery=read(A/'DELIVERY_RECEIPTS.json')
    assert sha(A/'STAGE_A.json')==a_lock['sha256']==delivery['stage_a_sha256']
    reg_t=time_value(registration['utc']);crop_t=time_value(crop_lock['utc']);a_t=time_value(a['utc']);a_lock_t=time_value(a_lock['utc'])
    view_interval=list(map(time_value,delivery['root_full_image_view']['time_interval_utc']))
    refs_interval=list(map(time_value,delivery['reference_delivery']['time_interval_utc']))
    assert reg_t<=view_interval[0]<=view_interval[1]<=crop_t
    assert crop_t<=refs_interval[0]<=refs_interval[1]<=a_t<=a_lock_t
    assert {view['file'] for view in a['views']}=={'source/REF_LOW.png','source/REF_A.png','source/REF_B.png'}
    assert all(view['detail']=='original' for view in a['views'])
    features=a['discriminating_features'];assert isinstance(features,list)
    full_flags=(a['low']['complete_visible'],a['high_A']['full_upper_visible'],a['high_B']['full_upper_visible'])
    assert all(type(flag) is bool for flag in full_flags) and type(a['complete_and_discriminating']) is bool
    if a['complete_and_discriminating']:
        assert all(full_flags) and features and all(isinstance(f,str) and f for f in features)
    cases=[]
    if not a['complete_and_discriminating']:
        assert not (A/'STAGE_B.json').exists()
        status='REFERENCE_OR_TARGET_CAPACITY_STOP'
    else:
        target_time=time_value(delivery['target_delivery']['utc'])
        assert a_lock_t<=time_value(analysis_lock['utc'])<=target_time
        assert set(delivery['target_delivery']['files'])=={'source/TARGET_X.png','source/TARGET_Y.png'}
        b=read(A/'STAGE_B.json')
        assert target_time<=time_value(b['utc']) and b['stage_a_sha256']==sha(A/'STAGE_A.json')
        assert b['observer']==a['observer']
        assert {case['target'] for case in b['cases']}==set(spec['target_ids']) and len(b['cases'])==2
        assert all(view['detail']=='original' for view in b['views'])
        assert {view['file'] for view in b['views']}=={'source/TARGET_X.png','source/TARGET_Y.png'}
        for c in b['cases']:
            assert c['localization'] in ('SUFFICIENT','UNRESOLVED')
            expected=spec['expected_high_template'][c['target']];other='REF_B' if expected=='REF_A' else 'REF_A'
            for component in ('low_motif','high_A','high_B'):
                assert c[component]['status'] in ('COMPATIBLE','INCOMPATIBLE','UNRESOLVED')
                assert isinstance(c[component]['reason'],str) and c[component]['reason']
            low=c['low_motif']['status'];high=c['high_'+expected[-1]]['status'];wrong=c['high_'+other[-1]]['status']
            localized=c['localization']=='SUFFICIENT'
            decision='CONTRADICTED' if localized and (low=='INCOMPATIBLE' or high=='INCOMPATIBLE') else 'CROSSED_COMPATIBLE' if localized and low==high=='COMPATIBLE' and wrong=='INCOMPATIBLE' else 'UNSCORABLE'
            cases.append({'target':c['target'],'source_id':spec['target_ids'][c['target']],
                          'expected_template':expected,'wrong_template':other,'low_status':low,
                          'expected_high_status':high,'wrong_high_status':wrong,
                          'localization_sufficient':localized,'fixed_case_decision':decision})
        status='FIXED_GRAPHIC_COMPOSITION_CONTRADICTED' if any(c['fixed_case_decision']=='CONTRADICTED' for c in cases) else 'CROSSED_GRAPHIC_COMPATIBILITY_BOTH_TARGETS' if all(c['fixed_case_decision']=='CROSSED_COMPATIBLE' for c in cases) else 'REFERENCE_OR_TARGET_CAPACITY_STOP'
    result=read(A/'RESULT.json')
    assert result['status']==status and result['cases']==cases
    assert result['source_physical_leaves']==result['observer_count']==1
    assert result['native_linguistic_units_identified']==result['confirmed_word_meanings']==0
    assert result['old1348decision']=='UNCHANGED_TEMPLATE_CAPACITY_STOP' and result['claim_ceiling']==spec['claim_ceiling']
    assert 'not external attestation' in result['chronology_limit']
    return {'status':status,'reference_gate':a['complete_and_discriminating'],'cases':cases,
            'stage_a_hash_unchanged':True,'recorded_stage_order_valid':True,
            'chronology_evidence':'Declared workflow receipts plus hash locks; no external observation/view attestation.',
            'perceptual_status':'Observer judgments preserved and logically accounted, not independently confirmed.'}


def main():
    registration=check_lock('REGISTRATION_LOCK.json');crop_lock=check_lock('CROP_LOCK.json');analysis_lock=check_lock('ANALYSIS_CODE_LOCK.json')
    spec=read(E/'src/SPEC.json')
    source=source_accounting(spec);pixels=pixel_accounting(spec)
    observer=observer_accounting(spec,registration,crop_lock,analysis_lock)
    old_result=ROOT/'experiments/yolo/gdt1348_graphic_component_check/artifacts/RESULT.json'
    assert read(old_result)['status']=='TEMPLATE_CAPACITY_STOP__INFORMED_GRAPHIC_COMPATIBILITY'
    paths=[E/'src/validate.py',E/'src/SPEC.json',A/'REGISTRATION_LOCK.json',A/'CROP_LOCK.json',A/'ANALYSIS_CODE_LOCK.json',
           A/'IMAGE_RECEIPTS.json',A/'SOURCE_PACKET.json',A/'STAGE_A.json',A/'STAGE_A_LOCK.json',A/'DELIVERY_RECEIPTS.json',A/'RESULT.json',old_result]
    if (A/'STAGE_B.json').exists():paths.append(A/'STAGE_B.json')
    receipt={'experiment':'GDT1402','status':'PASS_INDEPENDENT_ACCOUNTING_ONLY','recorded_graphic_result':observer['status'],
             'source':source,'pixels':pixels,'observer_record':observer,
             'pins':{str(path.relative_to(ROOT)):sha(path) for path in paths},
             'limits':['No perceptual truth, actual target localization, stroke order or linguistic units are proved by this validator.',
                       'One image source and one observer; alternate readers and repeated crops are not independent manuscripts.',
                       'Unresolved observations cannot produce a forced compatibility pass; all fixed targets and both competing templates remain in accounting.',
                       'No source meanings, glyph sounds or translated words; original1348capacity stop unchanged.']}
    path=A/'VALIDATION.json';serialized=json.dumps(receipt,indent=2,sort_keys=True)+'\n'
    if path.exists():assert path.read_text()==serialized
    else:path.write_text(serialized)
    print(json.dumps({'status':receipt['status'],'recorded_graphic_result':observer['status'],'source_rows':81,'pixel_crops_checked':6},sort_keys=True))

if __name__=='__main__':main()
