"""Registered census of original cells in the unchanged JOINT inventories."""
from common import *
from wrappers import contradictions
from wrapper_independent import saturation_errors
import collections
import subprocess


def main():
    checklock()
    receipt = read(A/'PUBLIC_REGISTRATION.json')
    subprocess.run(['git', 'cat-file', '-e', receipt['commit']+'^{commit}'], check=True, cwd=R)
    cases = read(A/'PREDICTIONS.json')
    scopes = {}
    for case in cases:
        index = case['context_index']
        assert index not in scopes or scopes[index] == case['groups']
        scopes[index] = case['groups']
    originals = read(A/'ORIGINAL_CANDIDATES.json')
    rows = []
    for original in originals:
        for index, groups in sorted(scopes.items()):
            one = contradictions(original['code'], groups)
            two = saturation_errors(original['code'], groups)
            assert bool(one) == bool(two)
            rows.append(dict(original_id=original['id'], context_index=index,
                             status='CONTRADICTED' if one else 'COMPATIBLE',
                             orbit_errors=one, permutation_errors=two))
    survivors = sorted({r['original_id'] for r in rows if r['status'] == 'COMPATIBLE'})
    result = dict(rows=rows, counts=dict(collections.Counter(r['status'] for r in rows)),
                  original_survivors=survivors, survivor_count=len(survivors),
                  continue_full_worlds=0 < len(survivors) < len(originals),
                  registration_commit=receipt['commit'],
                  scope='Known original cells of each unchanged joint inventory; not original-only recurrent inventory.',
                  completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    put('PRECURSOR.json', result)
    print(json.dumps({k: v for k, v in result.items() if k != 'rows'}, indent=2))


if __name__ == '__main__':
    main()
