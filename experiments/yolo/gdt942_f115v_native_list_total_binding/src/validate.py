#!/usr/bin/env python3
"""Check provenance, crop pixels, full fixed coverage and decision consistency."""
import csv
import hashlib
from datetime import datetime
from PIL import Image
from run import EXP, ROOT, check_locks, read, write


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    check_locks()
    source = read(EXP / 'src/SOURCE.json')
    receipt = read(EXP / 'artifacts/SOURCE_RECEIPT.json')
    obs = read(EXP / 'artifacts/OBSERVATIONS.json')
    result = read(EXP / 'artifacts/RESULT.json')
    assert source['page'] == 'f115v' and '/1006275/' in source['image_url']
    assert source['image_url'] == receipt['source_url']
    assert sha(ROOT / receipt['path']) == receipt['sha256'] == obs['source_sha256']
    assert (ROOT / receipt['path']).stat().st_size == receipt['bytes']
    times = [read(EXP / 'PREREG_LOCK.json')['registered_utc'], receipt['recorded_utc'],
             obs['observed_utc'], read(EXP / 'OBSERVATION_LOCK.json')['frozen_utc']]
    assert list(map(datetime.fromisoformat, times)) == sorted(map(datetime.fromisoformat, times))
    original = Image.open(ROOT / receipt['path'])
    assert original.size == (2676, 3697) and original.format == 'JPEG'
    crops = read(EXP / 'artifacts/CROPS.json')
    for crop in crops:
        target = EXP / crop['crop']
        assert crop['source'] == 'artifacts/SOURCE_F115V.jpg'
        assert sha(target) == crop['sha256']
        expected = original.crop(crop['box_xyxy'])
        actual = Image.open(target)
        assert actual.size == expected.size and actual.tobytes() == expected.tobytes()
    assert set(obs['viewed']) == {'artifacts/SOURCE_F115V.jpg'} | {c['crop'] for c in crops}
    for f in obs['fields']:
        assert f['status'] in {'PRESENT', 'ABSENT', 'UNRESOLVED'}
        assert f['observation'] and f['limitation']
        x0,y0,x1,y1 = f['box_xyxy']
        assert 0 <= x0 < x1 <= 2676 and 0 <= y0 < y1 <= 3697
    expected = read(EXP / 'src/EXPECTED.json')
    cols = list(next(iter(expected.values()))[0])
    primary = ROOT / 'experiments/yolo/gdt941_explicit_lkchey_comparison_context/artifacts/WORKING_ALIGNMENT.tsv'
    # This bound artifact contains only the already admitted working paragraphs.
    with primary.open() as f:
        inherited = [{k:r[k] for k in cols} for r in csv.DictReader(f, delimiter='\t')
                     if r['candidate'] == 'R_C' and r['page'] == 'f115v']
    flat = [x for v in expected.values() for x in v]
    key = lambda x: x['source_group_id']
    assert sorted(inherited, key=key) == sorted(flat, key=key)
    with (EXP / 'artifacts/EXPECTED_GROUPS.tsv').open() as f:
        assert list(csv.DictReader(f, delimiter='\t')) == flat
    assert {k:len(v) for k,v in expected.items()} == {'ZL3b':39,'IT2a':34,'RF1b':37}
    assert len(flat) == 110 and len({x['source_group_id'] for x in flat}) == 110
    assert all({x['locus'] for x in v} == {f'f115v.{n}' for n in range(37,41)} for v in expected.values())
    statuses = {f['id']: f['status'] for f in obs['fields']}
    assert set(statuses) == {'localization','member_delimitation','list_value_binding','physical_target_span','parallel_list_layout'}
    # Audit this actual outcome, without importing the runner's decision function.
    assert statuses['localization'] == 'PRESENT'
    assert statuses['member_delimitation'] == statuses['list_value_binding'] == 'ABSENT'
    assert result['decision'] == 'NO_VISUAL_LIST_TOTAL_BINDING'
    assert result['fields'] == statuses and result['total_recorded_groups'] == 110
    with (EXP / 'artifacts/CANDIDATE_DECISIONS.tsv').open() as f:
        cases = list(csv.DictReader(f, delimiter='\t'))
    assert {x['candidate'] for x in cases} == {'LIST_TOTAL','DOSE_PER_ITEM','DEGREE_OR_SINGLE_COMPOUND'}
    assert all(x['selected_meaning'] == 'False' and x['independent_confirmation_capacity_this_test'] == '0' for x in cases)
    assert result['independence'] == obs['independence']
    assert not result['numeric_test_performed'] and not result['significance_claim']
    assert result['confirmed_translated_words'] == 0 and obs['no_transcription_edits']
    write(EXP / 'artifacts/VALIDATION.json', dict(status='PASS', registered_hashes=14,
        exact_original=True, pixel_identical_crops=len(crops), fixed_groups=110,
        candidate_rows=3, actual_decision_consistent=True,
        limitation='Source and mechanical consistency checks; not an independent visual or semantic confirmation.'))
    print('PASS: source, registration, crop pixels, complete coverage, decision consistency')


if __name__ == '__main__':
    main()
