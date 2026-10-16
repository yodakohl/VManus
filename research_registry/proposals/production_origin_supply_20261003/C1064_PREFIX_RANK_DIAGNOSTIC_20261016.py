"""Public-control coefficient-prefix diagnostic; never reads plaintext or keys."""
import hashlib
import itertools
import json
import math
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'vmanus-work').exists())

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def invariants(rows, width):
    """Invertible row/column operations over Z/27; return diagonal valuations."""
    a = np.array(rows, dtype=np.int64).reshape((-1, width)) % 27
    vals = []
    for k in range(min(a.shape)):
        block = a[k:, k:]
        location = None
        for v, modulus in [(0, 3), (1, 9), (2, 27)]:
            hits = np.argwhere(block % modulus != 0)
            if len(hits):
                location = hits[0]
                break
        if location is None:
            break
        i, j = (int(location[0])+k, int(location[1])+k)
        a[[k, i], :] = a[[i, k], :]
        a[:, [k, j]] = a[:, [j, k]]
        divisor = 3 ** v
        unit = int(a[k, k]) // divisor
        a[k, :] = a[k, :] * pow(unit, -1, 27) % 27
        assert a[k, k] == divisor
        if k + 1 < len(a):
            assert np.all(a[k+1:, k] % divisor == 0)
            factors = a[k+1:, k] // divisor
            a[k+1:, :] = (a[k+1:, :] - factors[:, None] * a[k, :]) % 27
        # Clearing the pivot row by column operations changes no other row:
        # its pivot column is already zero off the diagonal.
        assert np.all(a[k, k+1:] % divisor == 0)
        a[k, k+1:] = 0
        vals.append(v)
    return dict(rank_mod3=vals.count(0), diagonal_3_valuations=vals,
                image_log3=sum(3-v for v in vals))

def controls():
    matrices = [[[3]], [[9]], [[1],[3]], [[3],[1]], [[3,0],[0,9]],
                [[3,1],[0,3]], [[0,0],[0,0]], [[1,2],[4,5],[7,8]]]
    for rows in matrices:
        width = len(rows[0])
        images = {tuple(sum(x*y for x,y in zip(row,key)) % 27 for row in rows)
                  for key in itertools.product(range(27), repeat=width)}
        assert 3 ** invariants(rows, width)['image_log3'] == len(images)
    return dict(status='PASS_EXHAUSTIVE_SMALL_PARAMETER_IMAGES', matrices=len(matrices),
                scope='Source-free arithmetic checks only; not recovery controls')

def affine_kernel_step(basis, row):
    residual = np.array(row, dtype=np.int64) @ basis % 27
    g = math.gcd(27, *(int(x) for x in residual))
    if g < 27:
        j = next(j for j, d in enumerate(residual) if math.gcd(int(d), 27) == g)
        vector = basis[:, j] * pow(int(residual[j]) // g, -1, 27) % 27
        updated = (basis - vector[:, None] * (residual // g)[None, :]) % 27
        updated[:, j] = ((27 // g) * vector) % 27
        basis = updated
    return basis, g

def main():
    note = HERE / 'C1064_PREFIX_RANK_DECISION_20261016.json'
    decision = json.loads(note.read_text())
    assert datetime.now(timezone.utc) < datetime.fromisoformat(decision['deadline_utc'])
    checked = controls()
    source = ROOT / decision['input']
    data = json.loads(source.read_text())
    assert set(data) == {'cases'} and len(data['cases']) == 18
    cases = []
    for case in data['cases']:
        assert set(case) == {'id', 'units'}
        assert len(case['units']) in (77, 120)
        previous = [0]*22
        rows, steps = [], []
        image_exp = 0
        basis = np.eye(23, dtype=np.int64)
        for position, packet in enumerate(case['units'], 1):
            assert packet and all(type(u) is int and 0 <= u < 22 for u in packet)
            current = [packet.count(j) for j in range(22)]
            rows.append([(x-y) % 27 for x,y in zip(current, previous)] + [1])
            state = invariants(rows, 23)
            increase = state['image_log3'] - image_exp
            assert 0 <= increase <= 3
            options = 3 ** increase
            basis, g = affine_kernel_step(basis, rows[-1])
            assert options == 27 // g
            kind = 'FULLY_DETERMINED' if options == 1 else 'FREE_27' if options == 27 else 'PARTIAL'
            steps.append(dict(position=position, rank_mod3=state['rank_mod3'],
                              image_log3=state['image_log3'], next_character_options=options,
                              affine_g=g,
                              constraint_kind=kind))
            image_exp = state['image_log3']
            previous = current
        snapshots = {}
        for n in [10,20,30,40,len(steps)]:
            prefix = steps[:n]
            snapshots[str(n)] = dict(rank_mod3=prefix[-1]['rank_mod3'], image_log3=prefix[-1]['image_log3'],
                fully_determined=sum(s['constraint_kind']=='FULLY_DETERMINED' for s in prefix),
                partial=sum(s['constraint_kind']=='PARTIAL' for s in prefix),
                fully_free=sum(s['constraint_kind']=='FREE_27' for s in prefix))
        cases.append(dict(id=case['id'], message_length=len(steps), snapshots=snapshots,
                          first_constrained_position=next((s['position'] for s in steps if s['next_character_options']<27), None),
                          first_fully_determined_position=next((s['position'] for s in steps if s['next_character_options']==1), None),
                          steps=steps))
    summary = {}
    for length in [77,120]:
        subset = [c for c in cases if c['message_length']==length]
        summary[str(length)] = dict(cases=len(subset),
            first_constraint_positions=[c['first_constrained_position'] for c in subset],
            rank_ranges={str(n):[min(c['snapshots'][str(n)]['rank_mod3'] for c in subset),
                                max(c['snapshots'][str(n)]['rank_mod3'] for c in subset)] for n in [10,20,30,40,length]},
            constrained_position_ranges={str(n):[min(c['snapshots'][str(n)]['fully_determined']+c['snapshots'][str(n)]['partial'] for c in subset),
                                                   max(c['snapshots'][str(n)]['fully_determined']+c['snapshots'][str(n)]['partial'] for c in subset)] for n in [10,20,30,40,length]})
    result = dict(status='EXACT_PUBLIC_CONTROL_PREFIX_CONSTRAINT_ACCOUNTING_NOT_RECOVERY',
                  computed_utc=datetime.now(timezone.utc).isoformat(),
                  hashes={str(p.relative_to(ROOT)):sha(p) for p in [note,source,Path(__file__)]},
                  controls=checked, cases=cases, summary_by_length=summary,
                  independent_arithmetic_check='Every prefix image-ratio option count agrees with independently formulated affine-kernel generator update; no plaintext right-hand side required.',
                  interpretation=['Every step option count is image(A_i)/image(A_i-1), exactly1,3,9or27 over unrestricted Z27 parameters.',
                                  'Compatible preceding character values are assumed, not guessed or read. Constraint right-hand sides still depend on those values.',
                                  'Mod3 row dependence alone does not distinguish one from3or9possible next characters; finite-ring image ratios retain that difference.',
                                  'Free/partial/determined counts concern next-character extensions, not recovered key columns or identified meanings.',
                                  'No true plaintext,key,private seed,case association,sourceLM or native text read. No decoder selected.'])
    output = HERE / 'C1064_PREFIX_RANK_RESULT_20261016.json'
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(summary,sort_keys=True))

if __name__ == '__main__':
    main()
