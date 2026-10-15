"""Independent source, symbolic dependency and partial-table validation."""
import hashlib
import json
from pathlib import Path

H = Path(__file__).resolve().parent
ROOT = H.parents[2]
def load(name):
    return json.loads((H / name).read_text())
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def ordered(lines):
    return sorted(lines, key=lambda l: int(l['metadata']['source_row_index']))
def main():
    j = load('EXEC_SERIAL_TRACE_20261015.json')
    plan = load('EXEC_SERIAL_PLAN_20261015.json')['design']
    for entry in plan['sources']:
        assert sha(ROOT / entry['path']) == entry['sha256']
    for path, value in j['input_sha256'].items():
        assert sha(ROOT / path) == value
    assert j['builder_sha256'] == sha(H / 'EXEC_SERIAL_BUILD_20261015.py')
    assert j['limits'] == plan['semantics'] and j['assumptions'] == plan['assumptions']
    old = load('LOCAL_RELATION95_READING_20261015.json')
    repeat = load('RESERVE80_REPEAT_SOURCE_20261015.json')
    p45 = load('F45R_WHOLE_PAGE_SOURCE_20261015.json')
    p89 = load('F89R1_Q2_SOURCE_20261015.json')
    sources = {'f45r': p45['readers']['IT2a'], 'f89r1': p89['readers']['IT2a'],
               'f115r': {'group_columns': repeat['readers']['IT2a']['records'][0]['group_columns'],
                        'lines': [repeat['readers']['IT2a']['records'][0]['line']]}}
    assert j['prior_alignment_documents'] == old['documents']
    assert j['old_anchors'] == {'status': 'INACTIVE_PROVENANCE_ONLY', 'sites': old['explicit_anchor_sites']}
    assert len(j['old_anchors']['sites']) == 5
    rows, addresses, allids = {}, {}, []
    for doc in j['source_documents']:
        src = sources[doc['page']]
        assert doc['group_columns'] == src['group_columns']
        assert doc['lines'] == ordered(src['lines'])
        for line in doc['lines']:
            for v in line['groups']:
                g = dict(zip(doc['group_columns'], v)); sid = g['source_group_id']
                assert sid not in rows
                rows[sid] = g
                addresses[sid] = (doc['page'], len(allids), line['metadata']['locus'])
                allids.append(sid)
    assert len(allids) == 143 and len(j['source_documents']) == 3
    wanted, other = [], []
    for doc in old['documents']:
        for record in doc['records']:
            for con in record['constructions']:
                if any(r['relation'] == 'daiin' for r in con['relations']):
                    wanted.append((con['id'], con['descriptor'], con['source_ids'], con['raw']))
                else:
                    other.append(con)
    assert j['unknown_other_constructions'] == other
    extra = ['IT2a|f115r.17|G%03d' % n for n in (3, 4, 5)]
    wanted.append(('f115r.17/G003-G005', 'qotchy', extra, ['qotchy', 'daiin', 'daiin']))
    assert len(wanted) == len(j['constructions']) == 11
    consumed, expected_apps, cons = [], [], {}
    for (cid, head, ids, words), c in zip(wanted, j['constructions']):
        assert (c['id'], c['head'], c['source_ids'], c['raw']) == (cid, head, ids, words)
        assert [rows[s]['ivtff_group_raw'] for s in ids] == words
        assert c['page'] == addresses[ids[0]][0]
        if len(ids) == 1:
            assert words[0] in ('daldaiin', 'doldaiin')
            assert head == {'daldaiin': 'dal', 'doldaiin': 'dol'}[words[0]]
            appids, encoding = ids, 'FINITE_FUSION'
        else:
            assert words[0] == head and set(words[1:]) == {'daiin'}
            appids = ids[1:]
            encoding = 'FREE_REPEAT' if len(appids) > 1 else 'FREE'
        assert c['application_source_ids'] == appids and c['encoding'] == encoding
        for a,b in zip(ids,ids[1:]):
            assert addresses[b][1] == addresses[a][1] + 1
            assert rows[a]['right_separator'] == rows[b]['left_separator'] == 'DEFINITE_SPACE'
        consumed.extend(ids); cons[cid] = c
        expected_apps.extend((cid, head, sid) for sid in appids)
    assert len(consumed) == len(set(consumed)) == 20
    assert j['unread_source_ids'] == [s for s in allids if s not in set(consumed)]
    assert len(j['unread_source_ids']) == 123
    assert len(expected_apps) == len(j['applications']) == 12
    assert j['function_identity']['heads'] == sorted({x[1] for x in expected_apps})
    assert len(j['function_identity']['heads']) == 10
    assert j['function_identity']['native_assignments'] == {}
    assert 'partial' in j['function_identity']['rule'] and 'alias' in j['function_identity']['rule']
    expected_links, starts, bychain = [], [], {}
    previous = None
    for expected, a in zip(expected_apps, j['applications']):
        assert (a['construction'], a['head'], a['source_id']) == expected
        assert a['function'] == 'F[' + a['head'] + ']'
        assert a['output_if_defined'] == a['function'] + '(' + a['input'] + ')'
        assert a['status'] == 'SYMBOLIC_NOT_NATIVE_EXECUTION'
        c = cons[a['construction']]
        # Establish links from source adjacency, independently of saved chain IDs.
        linked = False
        if previous:
            pc = cons[previous['construction']]
            if pc['id'] == c['id']:
                linked = True
            else:
                x,y = pc['source_ids'][-1],c['source_ids'][0]
                linked = (addresses[x][0] == addresses[y][0] and
                          addresses[y][1] == addresses[x][1] + 1 and
                          addresses[x][2] == addresses[y][2] and
                          rows[x]['right_separator'] == rows[y]['left_separator'] == 'DEFINITE_SPACE')
        if linked:
            assert a['input'] == previous['output_if_defined']
            assert a['chain'] == previous['chain']
            expected_links.append(dict(from_application=previous['id'], to_application=a['id'],
                                       kind='CONDITIONAL_SERIAL_OUTPUT_TO_INPUT'))
        else:
            starts.append(a['input'])
            assert a['chain'] not in bychain
            assert a['input'].startswith('s_boundary_')
        bychain.setdefault(a['chain'], []).append(a)
        previous = a
    assert len(starts) == len(set(starts)) == len(bychain) == 10
    assert j['serial_links'] == expected_links and len(expected_links) == 2
    assert len(j['local_chains']) == 10
    for chain in j['local_chains']:
        aa = bychain[chain['id']]
        assert chain['applications'] == [a['id'] for a in aa]
        assert chain['expression'] == aa[-1]['output_if_defined']
        assert chain['boundary_input'] == 'UNBOUND_NOT_RESET'
        assert chain['native_executability'] == 'UNKNOWN_PARTIAL_FUNCTIONS_AND_INPUT'
        ids=[]
        for a in aa:
            for sid in cons[a['construction']]['source_ids']:
                if sid not in ids: ids.append(sid)
        assert chain['source_ids'] == ids
    assert set(j['reader_local_full_spans']) == {'IT2a','ZL3b','RF1b'}
    for ed, bundle in j['reader_local_full_spans'].items():
        assert bundle['f115r17'] == repeat['readers'][ed]['records']
        p=p89['readers'][ed]
        line=next(l for l in p['lines'] if l['metadata']['locus']=='f89r1.9')
        assert bundle['f89r1_9'] == dict(group_columns=p['group_columns'],line=line)
    examples = j['formal_examples']
    assert examples['status'] == 'FINITE_SYNTHETIC_TABLES_NOT_NATIVE_FUNCTION_VALUES'
    assert {c['name'] for c in examples['cases']} == {'serial_versus_reset','idempotent','involution','partial_exhaustion'}
    for c in examples['cases']:
        for mode in ('serial','reset_rival'):
            current=c['input']; steps=[]; valid=True
            for symbol in c['order']:
                inp=current if mode=='serial' else c['input']
                matches=[pair[1] for pair in c['function_tables'][symbol] if pair[0]==inp]
                assert len(matches)<=1
                out=matches[0] if matches else None
                steps.append(dict(function=symbol,input=inp,status='DEFINED' if matches else 'UNDEFINED',output=out))
                if not matches: valid=False;break
                assert out in c['finite_domain'];current=out
            assert c[mode] == dict(steps=steps,executable=valid,final=current if valid else None)
    assert j['summary'] == dict(raw_groups=143,constructions=11,applications=12,
        contributing_groups=20,unread_groups=123,local_chains=10,serial_links=2,inactive_anchors=5,confirmed_words=0)
    return {'status':'PASS','source_groups':143,'constructions':11,'applications':12,
            'contributing_groups':20,'unread_groups':123,'unbound_chain_inputs':10,'source_supported_local_links':2,
            'retired_anchors':5,'unknown_functions':10,'toy_cases':4,
            'native_execution_or_meaning_validation':False,
            'limits':'Exact source/alignment and conditional symbolic links; finite synthetic partial-function examples only.'}

if __name__=='__main__':
    result=main()
    result['hashes']={n:sha(H/n) for n in ['EXEC_SERIAL_PLAN_20261015.json','EXEC_SERIAL_TRACE_20261015.json','EXEC_SERIAL_VALIDATE_20261015.py']}
    (H/'EXEC_SERIAL_VALIDATION_20261015.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))
