#!/usr/bin/env python3
"""Post-observation independent accounting, never a perception validator."""
import argparse
import collections
import hashlib
import itertools
import json
from datetime import datetime
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
ART = EXP / 'artifacts'
CEILING = 'Qualitative informedAIjudgments ofoneownedphotograph; accountingPASSdoesnotvalidateperception, phonemes, semanticwordboundaries ormeaning.'
STATUSES = ['LOCAL_GRAPHIC_REPEAT_SUPPORTED','PREMISE_REVIEW_REQUIRED','UNRESOLVED']

def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def utc(s):
    if s.endswith(' UTC'):
        s = s[:-4].replace(' ', 'T') + '+00:00'
    return datetime.fromisoformat(s.replace('Z','+00:00'))

def check_pins(lock):
    for name, expected in lock['files'].items():
        assert not Path(name).is_absolute()
        assert sha(ROOT / name) == expected, name

def assess(a,b,seams=None):
    if 'CLEAR_DIFFERENCE' in (a,b):
        return 'PREMISE_REVIEW_REQUIRED'
    if a == b == 'SIMILAR_SEQUENCE' and (seams is None or all(x == 'SPACE_LIKE' for x in seams)):
        return 'LOCAL_GRAPHIC_REPEAT_SUPPORTED'
    return 'UNRESOLVED'

def controls(spec):
    checks = 0
    # Independent declarative truth sets rather than duplicating branch order.
    pairs = list(itertools.product(spec['judgments'], repeat=2))
    negatives = {p for p in pairs if p.count('CLEAR_DIFFERENCE') > 0}
    for pair in pairs:
        expected = 'PREMISE_REVIEW_REQUIRED' if pair in negatives else ('LOCAL_GRAPHIC_REPEAT_SUPPORTED' if pair == ('SIMILAR_SEQUENCE',)*2 else 'UNRESOLVED')
        assert assess(*pair) == expected
        checks += 1
        for seam in itertools.product(spec['separator_judgments'],repeat=2):
            supported = pair == ('SIMILAR_SEQUENCE',)*2 and seam == ('SPACE_LIKE',)*2
            expected = 'PREMISE_REVIEW_REQUIRED' if pair in negatives else ('LOCAL_GRAPHIC_REPEAT_SUPPORTED' if supported else 'UNRESOLVED')
            assert assess(*pair,seams=seam) == expected
            checks += 1
    return {'status':'PASS','finite_truth_table_checks':checks}

def validate():
    view = read(EXP/'VIEW_LOCK.json')
    code = read(EXP/'CODE_LOCK.json')
    check_pins(view)
    check_pins(code)
    assert len(view['files']) == 8
    assert code['programs_authored_after_both_frozen_observations'] is True
    assert view['new_views_before_lock'] == 0
    assert view['programs_authored_after_observation'] is True
    for name,value in view['files'].items():
        assert code['files'][name] == value
    required = [EXP/'VIEW_LOCK.json', ART/'A_SEAL.json', ART/'VIEWER_A.json',ART/'VIEWER_B.json',EXP/'src/run.py',Path(__file__),EXP/'reproduce.py']
    for path in required:
        assert code['files'][path.relative_to(ROOT).as_posix()] == sha(path)
    spec = read(EXP/'src/SPEC.json')
    a,b = [read(ART/f'VIEWER_{letter}.json') for letter in 'AB']
    seal = read(ART/'A_SEAL.json')
    assert seal['viewer_a_path'] == (ART/'VIEWER_A.json').relative_to(ROOT).as_posix()
    assert seal['viewer_a_sha256'] == sha(ART/'VIEWER_A.json')
    assert seal['view_protocol_sha256'] == sha(EXP/'VIEW_LOCK.json')
    assert seal['observerB_assigned_before_seal'] is False
    assert utc(view['locked_utc']) < utc(a['recorded_utc']) <= utc(seal['sealed_utc']) < utc(b['recorded_utc']) < utc(code['locked_utc'])
    assert a['presentation']['original_image_view_calls'] == 1
    assert a['presentation']['detail'] == 'original'
    assert a['presentation']['crop_enhancement_rotation_ocr'] is False
    assert b['presentation']['views_this_task'] == 1
    image_path = ROOT/spec['source_path']
    assert sha(image_path) == spec['source_sha256']
    # Header metadata only: no image.load(), crop, pixel array or visual display.
    with Image.open(image_path) as im:
        assert list(im.size) == spec['dimensions']
        assert len(im.getexif()) == 0
        image_format = im.format
    assert b['presentation']['dimensions'] == spec['dimensions']
    assert b['presentation']['image'] == spec['source_path']
    for observer in [a,b]:
        assert observer['image_sha256'] == spec['source_sha256']
        assert observer['adjacent_separator']['target'] == 'P5'
        assert observer['adjacent_separator']['judgment'] in spec['separator_judgments']
        assert len(observer['comparisons']) == 5
        assert observer['source_awareness'] and observer['location_note'] and observer['limits']
        for declared, actual in zip(spec['comparisons'],observer['comparisons']):
            assert all(actual[k] == declared[k] for k in ['id','left','right'])
            assert actual['judgment'] in spec['judgments']
            assert actual.get('observation',actual.get('basis')) and actual['confidence']
    # Locations verified against unchanged original source wrapper, not visual truth.
    worksheet_names = [x for x in view['files'] if x.endswith('/LEXICAL_WORKSHEET_CONTEXT_20261016.json')]
    assert len(worksheet_names) == 1
    unit = read(ROOT/worksheet_names[0])['source_original_wrapper']['source_unit']
    rows = {line['metadata']['locus']:line['groups'] for line in unit['lines']}
    assert sum(map(len,rows.values())) == 77
    columns = unit['group_columns']
    raw_col, ordinal_col = columns.index('ivtff_group_raw'), columns.index('source_group_index')
    locations = []
    for pair in spec['comparisons']:
        members = []
        for side in ['left','right']:
            locus, ordinal = pair[side]
            group = rows[locus][ordinal-1]
            assert int(group[ordinal_col]) == ordinal
            members.append(group)
        assert members[0][raw_col] == members[1][raw_col]
        locations.append({'id':pair['id'],'original_groups':members})
    result = read(ART/'RESULT.json')
    expected_pairs = []
    counter = {s:0 for s in STATUSES}
    seam_a, seam_b = a['adjacent_separator']['judgment'],b['adjacent_separator']['judgment']
    for target, ca, cb in zip(spec['comparisons'],a['comparisons'],b['comparisons']):
        assessment = assess(ca['judgment'],cb['judgment'],(seam_a,seam_b) if target['id']=='P5' else None)
        counter[assessment] += 1
        expected_pairs.append(dict(target,viewer_a=ca['judgment'],viewer_b=cb['judgment'],assessment=assessment))
    assert result == {'experiment_id':'GDT1411','status':'QUALIFIED_GRAPHIC_REPEAT_CHECK_COMPLETE',
                      'pair_results':expected_pairs,'counts':counter,
                      'p5_separator':{'viewer_a':seam_a,'viewer_b':seam_b},
                      'word_meanings_assigned':0,'claim_ceiling':CEILING}
    receipt = {'experiment_id':'GDT1411','status':'PASS_NOT_PERCEPTION',
               'controls':controls(spec),'pair_counts':counter,
               'view_lock_sha256':sha(EXP/'VIEW_LOCK.json'),'code_lock_sha256':sha(EXP/'CODE_LOCK.json'),
               'a_seal_sha256':sha(ART/'A_SEAL.json'),'viewer_a_sha256':sha(ART/'VIEWER_A.json'),
               'viewer_b_sha256':sha(ART/'VIEWER_B.json'),'result_sha256':sha(ART/'RESULT.json'),
               'checked_code_pins':code['files'],'fixed_source_locations':locations,
               'image_metadata':{'sha256':spec['source_sha256'],'dimensions':spec['dimensions'],'format':image_format,'exif_entries':0},
               'limits':['Declared view chronology and byte identities checked, not externally attested view behavior.',
                         'No pixels viewed or perceptual judgments independently repeated.',
                         'Original source locators checked; actual physical localization remains manual.',
                         CEILING]}
    out = ART/'VALIDATION.json'
    if out.exists():
        assert read(out) == receipt
    else:
        out.write_text(json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':receipt['status'],'pair_counts':counter},sort_keys=True))

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--validate',action='store_true')
    p.parse_args()
    validate()
