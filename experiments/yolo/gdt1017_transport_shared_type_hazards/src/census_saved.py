"""Registered complete census of all29 saved GDT1013 positive witnesses."""
from common import *
from joint import canonical_original
from worker import bounded
import concurrent.futures
import collections
import subprocess


def job(j):
    case, engine, witness = j
    args = dict(original_parse=canonical_original(case), parse=witness['parse'], variant=case['variant'])
    one = bounded('joint', args)
    two = bounded('joint', dict(**args, independent=True))
    if one['status'] == two['status'] == 'COMPLETE':
        assert one['result'] == two['result']
        result = one['result']
        assert result['local_original_status'] == result['local_added_status'] == 'COHERENT'
        proof = []
        s,g=inputs()
        model=load(s['model'],'provenance993')
        provenance=[]
        for owner,parsed in [('original',args['original_parse']),('added',args['parse'])]:
            program=model.compile_reading(parsed,args['variant'])
            provenance.extend(dict(owner=owner,clause=node['clause'],start=node['start'],end=node['end'],kind=node['kind'],pair=node['pair']) for node in program['nodes'] if 'pair' in node)
        for label, world in [('original', result['original']), ('added', result)]:
            imported = {tuple(x) for x in world['hazards']} - {tuple(x) for x in world['asserted_hazards']}
            for path_no, path in enumerate(world['paths']):
                if not path['without_safety_consistent']:
                    continue
                local = {tuple(x) for x in world['asserted_hazards']}
                old_bad = [v for v in path['safety_violations'] if tuple(v['pair']) in local]
                if old_bad:
                    continue
                for violation in path['safety_violations']:
                    if tuple(violation['pair']) in imported:
                        proof.append(dict(direction='added_to_original' if label == 'original' else 'original_to_added',
                                          path=path_no, **violation))
        return dict(case=case['id'], engine=engine, status=result['status'],
                    original_cargo=result['original']['cargo'], added_cargo=result['cargo'],
                    original_asserted=result['original']['asserted_hazards'],
                    added_asserted=result['asserted_hazards'], union=result['union_hazards'],
                    assertion_provenance=provenance, imported_state_conflicts=proof,
                    primary=one, independent=two)
    return dict(case=case['id'], engine=engine, status='UNKNOWN_REPLAY', primary=one, independent=two)


def main():
    checklock()
    receipt = read(A/'PUBLIC_REGISTRATION.json')
    subprocess.run(['git', 'cat-file', '-e', receipt['commit']+'^{commit}'], check=True, cwd=R)
    s, g = inputs()
    cases = read(A/'PREDICTIONS.json')
    primary, independent = read(R/s['source_saved_primary']), read(R/s['source_saved_independent'])
    jobs = []
    for case, p, q in zip(cases, primary, independent, strict=True):
        assert case['id'] == p['id'] == q['id']
        for engine, result in [('primary', p), ('independent', q['independent'])]:
            if result['status'] == 'sat':
                jobs.append((case, engine, result['witness']))
    assert len(jobs) == 29
    with concurrent.futures.ThreadPoolExecutor(max_workers=s['workers']) as pool:
        rows = list(pool.map(job, jobs))
    put('SAVED_WITNESS_CENSUS.json', dict(rows=rows, counts=dict(collections.Counter(r['status'] for r in rows)),
                                        scope='Every saved positive1013witness;not the complete extension space.',
                                        completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
    print(json.dumps(dict(saved=len(rows), counts=dict(collections.Counter(r['status'] for r in rows)))))


if __name__ == '__main__':
    main()
