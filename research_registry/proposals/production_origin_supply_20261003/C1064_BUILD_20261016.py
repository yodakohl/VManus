"""Symbolic cumulative packet-state differences, not a key search or reading."""
from pathlib import Path
from collections import Counter
import argparse, hashlib, json

BASE = Path(__file__).resolve().parent
ROOT = next(p for p in BASE.parents if (p/'vmanus-work').exists())
PLAN = BASE/'C1064_PLAN_20261016.json'
LOCK = BASE/'C1064_CODE_LOCK_20261016.json'
OUTPUT = BASE/'C1064_DERIVATION_20261016.json'
SCAFFOLD = BASE/'E1063_SCAFFOLD_20261016.json'
SIGNS = ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/src/SPEC.json'
TRIPLES = ROOT/'experiments/yolo/gdt857_cyclic_inventory_triple_bound/artifacts/HITS.json'
VALIDATOR = BASE/'C1064_VALIDATE_20261016.py'
MOD = 27


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return str(path.relative_to(ROOT))


def unique_parse(raw, signs):
    paths = [[] for _ in range(len(raw)+1)]
    paths[0] = [()]
    for i in range(len(raw)):
        for prefix in paths[i]:
            for j,s in enumerate(signs):
                if raw.startswith(s,i) and len(paths[i+len(s)])<2:
                    paths[i+len(s)].append(prefix+(j,))
    return paths[-1][0] if raw and len(paths[-1])==1 else None


def difference(current, previous, b):
    coefficients = Counter(current)
    for key,value in previous.items():
        coefficients[key] -= value
    coefficients[b] += 1
    return {k:v % MOD for k,v in sorted(coefficients.items()) if v % MOD}


def expression(coefficients):
    return '('+' + '.join(str(v)+'*'+k for k,v in sorted(coefficients.items()))+') mod 27'


def controls():
    checked = 0
    for previous in range(MOD):
        for source in range(MOD):
            for b in range(MOD):
                state = (previous+source-b)%MOD
                assert (state-previous+b)%MOD == source
                checked += 1
    assert difference({'u':1},{'u':1},'b') == {'b':1}
    assert difference({'w':2},{'u':1},'b') == {'b':1,'u':26,'w':2}
    # One erroneous observed state changes two consecutive decoded differences.
    states=[2,8,13,4]; damaged=[2,15,13,4]
    values=lambda ss:[(ss[i]-(ss[i-1] if i else 0)+5)%MOD for i in range(len(ss))]
    assert [(b-a)%MOD for a,b in zip(values(states),values(damaged))] == [0,7,20,0]
    # Symbolic interior states telescope; an incoming state is retained.
    previous={'IN:toy':1}; summed=Counter()
    for current in [{'u1':1},{'w':2},{'w':2}]:
        summed.update(difference(current,previous,'b'));previous=current
    assert {k:v%MOD for k,v in summed.items() if v%MOD} == {'IN:toy':26,'b':3,'w':2}
    for b in range(MOD):
        assert [(7-12+b)%MOD,(7-7+b)%MOD,(7-7+b)%MOD][1:] == [b,b]
    assert unique_parse('ch',['c','h','ch']) is None
    assert unique_parse('ch',['c','ch']) == (1,)
    assert unique_parse('a@1;',['a']) is None
    return dict(status='PASS_SOURCE_FREE_ONLY',modular_roundtrips=checked,
                telescoping=True,opaque_shared_state=True,error_adjacent_plus_minus=True,
                triple_last_two_equal_b=True,parser_fixtures=3,native_access=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--controls',action='store_true')
    if parser.parse_args().controls:
        print(json.dumps(controls(),sort_keys=True));return
    lock,plan=read(LOCK),read(PLAN)
    hashes={x['path']:x['sha256'] for x in lock['files']}
    assert len(hashes)==len(lock['files']) and lock['locked_utc']
    required={rel(PLAN),rel(Path(__file__).resolve()),rel(VALIDATOR),rel(SCAFFOLD),rel(SIGNS),rel(TRIPLES)}
    required.update(x['path'] for x in plan['inputs'])
    assert required <= hashes.keys(), sorted(required-hashes.keys())
    for path,digest in hashes.items():assert sha(ROOT/path)==digest,path
    for item in plan['inputs']:assert hashes[item['path']]==item['sha256'],item['path']
    assert plan['source']==rel(SCAFFOLD) and plan['triple_source']==rel(TRIPLES) and plan['modulus']==MOD
    scaffold,signs,hits=read(SCAFFOLD),read(SIGNS)['signs'],read(TRIPLES)
    assert signs==plan['signs']
    assert len(signs)==22 and len(set(signs))==22 and all(signs)
    result=dict(status='RELAXED_CUMULATIVE_STATE_EQUATIONS_NO_KEY_OR_PLAINTEXT',
                pins=[dict(path=k,sha256=v) for k,v in sorted(hashes.items())],
                code_lock=dict(path=rel(LOCK),sha256=sha(LOCK),locked_utc=lock['locked_utc']),
                modulus=MOD,signs=signs,reader_parameters={},source_units=scaffold['source_units'],units=[])
    seen=set();account=Counter(source_units=0,source_groups=0,unique_groups=0,opaque_groups=0,known_zero_differences=0)
    for wrapper in scaffold['source_units']:
        uid,unit=wrapper['unit_id'],wrapper['source_unit'];reader=unit['edition']
        assert reader in ('IT2a','ZL3b','RF1b')
        params=dict(weights=['w_'+reader+'_'+str(i) for i in range(22)],b='b_'+reader)
        if reader in result['reader_parameters']:assert result['reader_parameters'][reader]==params
        result['reader_parameters'][reader]=params
        initial=dict(kind='INCOMING',coefficients={'IN:'+uid:1}) if reader=='RF1b' else dict(kind='RESET',coefficients={})
        out=dict(unit_id=uid,reader=reader,boundary_status=unit['boundary_status'],initial_state=initial,
                 rows=[],zero_difference_source_ids=[])
        previous=initial;index=0
        for line in unit['lines']:
            locus=line['metadata']['locus']
            assert line['metadata']['page'] in ('f75r','f75v') and line['metadata']['edition']==reader
            for original in line['groups']:
                assert len(original)==len(unit['group_columns'])
                group=dict(zip(unit['group_columns'],original));sid=group['source_group_id'];raw=group['ivtff_group_raw']
                assert sid not in seen;seen.add(sid);index+=1
                parsed=unique_parse(raw,signs)
                if parsed is None:
                    vector=None;current=dict(kind='OPAQUE',coefficients={'u_'+uid+'_'+str(index):1})
                    account['opaque_groups']+=1
                else:
                    counts=Counter(parsed);vector=[counts[i] for i in range(22)]
                    current=dict(kind='SUM',coefficients={params['weights'][i]:n for i,n in enumerate(vector) if n})
                    account['unique_groups']+=1
                coefficients=difference(current['coefficients'],previous['coefficients'],params['b'])
                zero=(current['kind']==previous['kind']=='SUM' and current['coefficients']==previous['coefficients'])
                if zero:out['zero_difference_source_ids'].append(sid);account['known_zero_differences']+=1
                out['rows'].append(dict(source_group_id=sid,locus=locus,raw=raw,source_group=group,
                    index_in_message=index,parse_status='OPAQUE' if parsed is None else 'UNIQUE',
                    units=None if parsed is None else [signs[i] for i in parsed],count_vector=vector,
                    current_state=current,previous_state=previous,source_coefficients_mod27=coefficients,
                    source_expression=expression(coefficients),zero_difference_known_same_counts=zero))
                previous=current
        result['units'].append(out);account['source_units']+=1;account['source_groups']+=index
    assert account['source_units']==6 and account['source_groups']==588
    for hit in hits:
        groups=hit['groups'];assert len(groups)==3
        assert len({g['ivtff_group_raw'] for g in groups})==1
        assert all(a['right_separator']==b['left_separator']=='DEFINITE_SPACE' for a,b in zip(groups,groups[1:]))
    result['triple_obligation']=dict(source_path=rel(TRIPLES),source_sha256=sha(TRIPLES),witnesses=hits,
        derivation='AAA -> (hA-prev+b),b,b',
        zero_b_limit='With b=0 the last two decoded characters are SPACE SPACE; incompatible with an added source rule forbidding adjacent spaces. The broad1064 domain permits repeated spaces and is not excluded.',
        no_new_census=True)
    result['accounting']=dict(account)
    result['limits']=['Symbolic source equations only; no bank, q, vocabulary, key, plaintext or likelihood fit.',
        'Weights and b are shared within each reader across both units; readers are not pooled.',
        'IT/ZL assume complete source messages with incoming state0; each RF window has its own unknown incoming state.',
        'Physical line breaks do not reset state. Opaque groups have fresh state variables reused in the next difference.',
        'Known zero differences imply only source character b, not SPACE unless b=0.',
        'Old857triple witnesses impose a separate global uninterrupted-span obligation, not new paragraph observations.',
        'No actual source output, word meaning, historical bank or fit is asserted.']
    OUTPUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],accounting=result['accounting']),sort_keys=True))


if __name__=='__main__':main()
