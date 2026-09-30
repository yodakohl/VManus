"""Independent packet accounting; does not validate human ownership or meaning."""
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.word_profiles import ensure_cache

def main():
    source=HERE/'src/SOURCE.tsv'
    rows=list(csv.DictReader(source.open(),delimiter='\t'))
    model=json.loads((HERE/'src/MODEL.json').read_text())
    assert hashlib.sha256(source.read_bytes()).hexdigest()==model['source_sha256']
    conn=ensure_cache()
    fetched=conn.execute('''SELECT * FROM groups
        WHERE (page='f76r' AND CAST(substr(locus,instr(locus,'.')+1) AS INTEGER)<=38)
        OR (page='f75v' AND locus='f75v.51')
        ORDER BY edition,page,CAST(substr(locus,instr(locus,'.')+1) AS INTEGER),source_group_index''').fetchall()
    expected=[{key:str(value) for key,value in dict(r).items()} for r in fetched]
    conn.close()
    assert expected==rows
    assert all(r['page'] in ('f76r','f75v') for r in rows)
    ids={r['source_group_id']:r for r in rows}
    assert len(ids)==len(rows)
    result=json.loads((HERE/'artifacts/RESULT.json').read_text())
    events=json.loads((HERE/'artifacts/EVENTS.json').read_text())
    target=[r for r in rows if r['ivtff_group_raw'] in ('okeey','qokeey')]
    assert {e['id'] for e in events}=={r['source_group_id'] for r in target}
    assert len(events)==len(target)==result['target_events']
    reader=(HERE/'artifacts/FULL_READER.md').read_text().splitlines()
    for edition in ('ZL3b','IT2a','RF1b'):
        for loc in ('f75v.51',)+tuple(f'f76r.{i}' for i in range(1,39)):
            line=[r for r in rows if r['edition']==edition and r['locus']==loc]
            assert line
            assert len(line)==int(line[0]['source_group_count'])
            assert [int(r['source_group_index']) for r in line]==list(range(1,len(line)+1))
            assert f"- {edition} {loc} {line[0]['kind']}: "+' | '.join(r['ivtff_group_raw'] for r in line) in reader
            for candidate,mapping in model['candidates'].items():
                rendered=[mapping[r['ivtff_group_raw']]['gloss'] if r['ivtff_group_raw'] in mapping else 'UNKNOWN' for r in line]
                assert '  - '+candidate+': '+' | '.join(rendered) in reader
        all_lines={r['locus']:r['kind'] for r in rows if r['edition']==edition and r['page']=='f76r'}
        assert Counter(all_lines.values())=={'P':29,'L':9}
        labels=[r['ivtff_group_raw'] for r in rows if r['edition']==edition and r['locus']=='f75v.51']
        assert labels==['okeey','lol']
        counts=Counter(r['ivtff_group_raw'] for r in target if r['edition']==edition and r['kind']=='P')
        assert dict(counts)==result['P_target_counts'][edition]
    with (HERE/'artifacts/CANDIDATE_TABLE.tsv').open() as stream:
        table=list(csv.DictReader(stream,delimiter='\t'))
    assert len(table)==2*len(target)==result['candidate_rows']
    assert Counter((r['candidate'],r['id']) for r in table)==Counter((c,r['source_group_id']) for c in ('D','F') for r in target)
    for row in table:
        raw=ids[row['id']]
        spec=model['candidates'][row['candidate']][raw['ivtff_group_raw']]
        assert row['gloss']==spec['gloss'] and row['role']==spec['role']
        assert row['observed_meaning']=='UNIDENTIFIED'
        assert row['contradiction']=='NOT_EVALUABLE_FROM_UNKNOWN_NEIGHBOURS'
        neighbours=[r['source_group_id'] for r in rows if r['edition']==raw['edition'] and r['locus']==raw['locus'] and r['kind']=='P' and raw['kind']=='P' and abs(int(r['source_group_index'])-int(raw['source_group_index']))==1 and r['ivtff_group_raw']==('okeey' if raw['ivtff_group_raw']=='qokeey' else 'qokeey')]
        assert row['candidate_argument']==(','.join(neighbours) or 'UNBOUND')
    native=json.loads((HERE/'src/NATIVE_OBSERVATION.json').read_text())
    assert native['ownership']=='AMBIGUOUS'
    assert not native['visible_label_to_single_object_leader'] and not native['inside_single_bounded_object']
    image=ROOT/native['image']
    assert hashlib.sha256(image.read_bytes()).hexdigest()==native['image_sha256']
    validation={'status':'PASS','exact_guarded_source_reconstructed':True,
        'whole_loci':117,'candidate_rows':len(table),'verified_native_image_sha256':native['image_sha256'],
        'human_ownership_validated':False,'meaning_validated':False,
        'independence':'second implementation by same root; not independent semantic review'}
    (HERE/'artifacts/VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n')
    print(json.dumps(validation,indent=2))

if __name__=='__main__': main()
