"""Independent implementation, same author; structural construction only."""
from pathlib import Path
from itertools import product
import json,hashlib
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def read(name):return json.loads((A/name).read_text())
def expansions(text,entries):
    # Forward dynamic program over positions, distinct expanded messages and path counts.
    states=[{} for _ in range(len(text)+1)];states[0][()]=1
    for i,current in enumerate(states):
        for e in entries:
            if text.startswith(e['surface'],i):
                dest=states[i+len(e['surface'])]
                for source,ways in current.items():
                    new=source+tuple(e['expansion']);dest[new]=dest.get(new,0)+ways
    return states[-1]
def main():
    for p,h in read('REGISTRATION_LOCK.json')['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    assert read('RUN_RECEIPT.json')['runner_sha256']==hashlib.sha256((D/'src/run.py').read_bytes()).hexdigest()
    table=read('TABLE.json');codes=table['primitive'];entries=table['entries'];byname={e['name']:e for e in entries}
    assert len(byname)==len(entries)==30
    expected=dict(zip(['U0','U1','U2','U3','U4','U5','U6','WORD_BREAK','OPEN','CLOSE'],['dal','al','ch','ol','y','dy','or','m','p','f']))
    assert codes==expected
    assert all(a==b or not codes[a].startswith(codes[b]) for a in codes for b in codes)
    for e in entries:
        assert e['surface'] and e['expansion']
        assert e['surface']==''.join(codes[u] for u in e['expansion'])
        if e['kind']=='primitive':assert e['expansion']==[e['name']]
        else:assert e['kind']=='transparent_alias' and all(u.startswith('U') for u in e['expansion'])
    expected_aliases={(f'U{i}'+suffix,tuple([f'U{i}']+tail)) for i in range(4)
        for suffix,tail in [('_Y',['U4']),('_DY',['U5']),('_OR',['U6']),('_DOUBLE',[f'U{i}']),('_DOUBLE_DY',[f'U{i}','U5'])]}
    assert {(e['name'],tuple(e['expansion'])) for e in entries if e['kind']=='transparent_alias'}==expected_aliases
    total=multi=ways_total=maximum=0;digest=hashlib.sha256()
    for n in range(5):
        for message in product([f'U{i}' for i in range(7)],repeat=n):
            text=''.join(codes[u] for u in message);seen=expansions(text,entries)
            assert set(seen)=={message};ways=seen[message]
            total+=1;multi+=ways>1;ways_total+=ways;maximum=max(maximum,ways)
            digest.update((json.dumps([message,text,ways],separators=(',',':'))+'\n').encode())
    for fixture in read('STRUCTURE_FIXTURES.json'):
        assert fixture['surface']==''.join(codes[u] for u in fixture['source'])
        assert expansions(fixture['surface'],entries)=={tuple(fixture['source']):fixture['parse_count']}
    for fixture in read('TEACHING.json'):
        source=tuple(fixture['source']);assert source==tuple(fixture['expanded_message'])
        all_values=expansions(fixture['surface'],entries);assert all_values.keys()=={source}
        assert len(fixture['parses'])==all_values[source]
        assert len({tuple(path) for path in fixture['parses']})==len(fixture['parses'])
        for path in fixture['parses']:
            assert ''.join(byname[k]['surface'] for k in path)==fixture['surface']
            assert tuple(u for k in path for u in byname[k]['expansion'])==source
    bad=entries+[{'name':'INDEPENDENT_WHOLE','surface':'olol','expansion':['NEW_VALUE']}]
    assert set(expansions('olol',bad))=={('U3','U3'),('NEW_VALUE',)}
    negatives=read('COUNTEREXAMPLES.json');assert len(negatives)==4
    assert negatives[0]['expansions']==[['NEW_VALUE'],['U3','U3']]
    assert negatives[0]['longest_match_choice']==['NEW_VALUE']
    for witness in negatives[1:]:
        left=''.join(codes[u] for u in witness['first']);right=''.join(codes[u] for u in witness['second'])
        assert left!=right and [left,right]==witness['distinct_correct_surfaces']
        if witness['kind']=='erased_word_boundary':assert left.replace(codes['WORD_BREAK'],'')==right
        if witness['kind']=='erased_scope':
            erase=lambda s:s.replace(codes['OPEN'],'').replace(codes['CLOSE'],'')
            assert erase(left)==erase(right)==witness['collapsed_surface']
    result=read('RESULT.json')
    assert (result['enumerated_messages'],result['multiple_parse_messages'],result['total_parse_paths'],result['maximum_paths_one_message'])==(total,multi,ways_total,maximum)
    assert result['canonical_enumeration_sha256']==digest.hexdigest()
    assert result['status']=='CONSTRUCTIVE_MESSAGE_UNIQUENESS_WITH_MULTIPLE_PARSES'
    assert result['native_words_assigned']==0 and not result['native_statistics_tested']
    v={'status':'PASS','scope':'Fixed artificial table prefix freedom, exact transparent expansion, all finite parses and paid-boundary counterexamples',
       'same_author':True,'native_data_test':False,'native_meaning_validation':False,
       'general_proof_basis':['prefix_free_primitive_code','every_alias_equals_primitive_encoding_of_its_exact_expansion','source_structure_markers_are_preserved'],
       'enumerated_messages':total,'validator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (A/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
if __name__=='__main__':main()
