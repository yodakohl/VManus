#!/usr/bin/env python3
"""Independent exact-source/capacity audit; no semantic execution or repair."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent

def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    source=read(HERE/'SOURCE.json'); parent=read(HERE/'PARENT.json')
    cap=read(HERE/'CAPACITY_RESULT.json'); cs=read(HERE/'CANDIDATES.json')
    decision=read(HERE/'DECISION.json'); receipt=read(HERE/'RECEIPT.json')
    original=read(ROOT/parent['source_path'])
    nomination=read(ROOT/decision['source']['path'])
    specpath=ROOT/'experiments/yolo/gdt1027_seed_rite_scope_and_identity/src/SPEC.json'
    spec=read(specpath)
    primary=ROOT/source['source_path']
    assert source['source_path']=='experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json'
    assert sha(primary)==source['source_sha256']=='667ca3ae0705a6bb3ccfcd09ea7ee04e28747e58d810e8fa9379f28c0f4fc89b'
    # This primary is the explicitly admitted, f84-free GDT928 cache.
    # Select only the two fixed IDs before accessing any record body.
    cache=read(primary)
    def select(reader, ident):
        matches=[p for p in cache[reader] if p['id']==ident]
        assert len(matches)==1
        assert matches[0]['page']=='f31r'
        return matches[0]
    assert sha(ROOT/parent['source_path'])==parent['source_sha256']
    assert sha(ROOT/decision['source']['path'])==decision['source']['sha256']
    assert sha(specpath)==cs['spec_sha256']
    for binding in nomination['source_bindings']:
        assert sha(ROOT/binding['path'])==binding['sha256'],binding['path']
    for name,expected in receipt['hashes'].items():
        if (HERE/name).exists(): assert sha(HERE/name)==expected,name
    old=original['all_30_new_lexical_entries']
    assert len(old)==30 and old==parent['all_30_values']
    assert old['qokeey']['tag']=='KNOWS'
    assert parent['record']==original['target']['complete_raw_record']
    assert parent['IT2a_alternative']==original['target']['IT2a_complete_alternative']
    assert parent['record']==select('ZL3b','f31r|f31r.1-f31r.5')
    assert parent['IT2a_alternative']==select('IT2a','f31r|f31r.1-f31r.5')
    fields=('id','quantity','knowledge','purity')
    assert [{k:c[k] for k in fields} for c in cs['candidates']]==spec['candidates']
    assert len(cs['candidates'])==cs['count']==8
    assert all(c['new_target_semantics']=='NOT_ATTEMPTED_CAPACITY_STOP' for c in cs['candidates'])
    assert 'only29 of30' in spec['different_objects_cost']
    target=source['selection_id']; assert target=='f31r|f31r.6-f31r.9'
    assert nomination['design']['target']['id']==target
    assert nomination['design']['caps']['new_whole_values']==14==decision['caps']['new_whole_values_max']
    rows={}
    for reader in ('ZL3b','IT2a'):
        p=select(reader,target); authored=source['readers'][reader]
        assert p['lines']==authored['lines']
        assert [x['locus'] for x in p['lines']]==['f31r.6','f31r.7','f31r.8','f31r.9']
        assert p['lines'][0]['start'] and p['lines'][-1]['end']
        assert not any(x['end'] for x in p['lines'][:-1])
        assert not any(x['start'] for x in p['lines'][1:])
        words=[w for line in p['lines'] for w in line['words']]
        assert len(words)==p['groups']==authored['groups']==27
        types=set(words); known=sorted(types & old.keys()); unknown=sorted(types-old.keys())
        assert dict(Counter(words))==authored['forms']
        assert len(types)==authored['types']==cap['readers'][reader]['types']
        for item in (authored,cap['readers'][reader]):
            assert item['inherited_exact_forms']==known and item['inherited_exact_count']==len(known)
            assert item['new_exact_forms']==unknown and item['new_exact_count']==len(unknown)
        terms=sorted(types & {'daiin','[s:r]air','chey'})
        assert ('qokeey' in types)==cap['capacity_gate_missing']['present_by_reader'][reader]
        assert terms==cap['capacity_gate_missing']['present_by_reader_old_term'][reader]
        parent_p=select(reader,'f31r|f31r.1-f31r.5')
        parent_n=sum(len(x['words']) for x in parent_p['lines'])
        assert parent_n==parent_p['groups']
        rows[reader]={'source_exact_all_fields':True,'continuation_groups':len(words),
            'types':len(types),'known_forms':known,'known_positions':sum(w in old for w in words),
            'new_forms':unknown,'new_types':len(unknown),'new_value_cap':14,
            'new_value_cap_pass':len(unknown)<=14,'exact_qokeey_present':'qokeey' in types,
            'exact_person_proposition_terms':terms,'knowledge_capacity_pass':bool('qokeey' in types and terms),
            'anchor_eligible_by_line':{x['locus']:x['anchor_eligible'] for x in p['lines']},
            'parent_literal_groups':parent_n,'whole_literal_groups':parent_n+len(words)}
    assert not [p for p in cache['RF1b'] if p['id']==target]
    assert all(not x['new_value_cap_pass'] and not x['knowledge_capacity_pass'] for x in rows.values())
    result={'status':'SOURCE_AND_CAPACITY_VERIFIED_WITH_WHOLE_IT_COUNT_CORRECTION',
        'created_utc':datetime.now(timezone.utc).isoformat(),'readers':rows,
        'all_eight_candidate_coordinates_exact':True,'base30_full_values_exact':True,
        'candidate_local_chey_limit':spec['different_objects_cost'],
        'rf_complete_target_records':0,'semantics_executed':False,
        'corrections':['64 is ZL37+27 only. Literal IT whole unit is35+27=62; author source retains both records correctly.'],
        'time_limit':'Author times are claimed receipt times, not independently proved public registration.',
        'input_hashes':{str(p.relative_to(ROOT)):sha(p) for p in [primary,specpath,ROOT/parent['source_path'],ROOT/decision['source']['path']]+[HERE/n for n in ['SOURCE.json','PARENT.json','CANDIDATES.json','DECISION.json','CAPACITY_RESULT.json','RECEIPT.json']]}}
    (HERE/'VALIDATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'ZL_new':rows['ZL3b']['new_types'],'IT_new':rows['IT2a']['new_types'],'literal_whole_ZL':rows['ZL3b']['whole_literal_groups'],'literal_whole_IT':rows['IT2a']['whole_literal_groups']}))

if __name__=='__main__': main()
