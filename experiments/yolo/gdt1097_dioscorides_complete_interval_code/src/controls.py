"""Independent tiny oracle, interval exhaustive checks and planted source shape."""
import collections
import itertools
import json
from pathlib import Path
import time

from model import solve, suffix_classes

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]


def ground(atoms, text, code):
    if set(code) != set(atoms) or not all(code.values()):
        return False
    if ''.join(code[a] for a in atoms) != text:
        return False
    words = list(code.values())
    return not any(i != j and u.startswith(v) for i, u in enumerate(words) for j, v in enumerate(words))


def brute(atoms, text):
    """Assign a fresh code from the actual current target prefix; no suffix API."""
    def visit(index, position, code):
        if index == len(atoms):
            return dict(code) if position == len(text) else None
        atom = atoms[index]
        if atom in code:
            w = code[atom]
            return visit(index+1, position+len(w), code) if text.startswith(w, position) else None
        endmax = len(text) - (len(atoms)-index-1)
        for end in range(position+1, endmax+1):
            word = text[position:end]
            if any(word.startswith(v) or v.startswith(word) for v in code.values()):
                continue
            code[atom] = word
            result = visit(index+1, end, code)
            del code[atom]
            if result is not None:
                return result
        return None
    return visit(0, 0, {})


def main():
    started = time.monotonic()
    strings = [''.join(s) for n in range(1, 7) for s in itertools.product('ab', repeat=n)]
    pairs = 0
    for text in strings:
        sa, ranks, classes = suffix_classes(text)
        inventory = {text[i:j] for i in range(len(text)) for j in range(i+1,len(text)+1)}
        represented = {}
        for lo, hi, low, high in classes:
            for length in range(low, high+1):
                word = text[sa[lo]:sa[lo]+length]
                assert word not in represented
                represented[word] = (lo, hi)
                expected = [r for r,p in enumerate(sa) if text.startswith(word,p)]
                assert expected == list(range(lo,hi+1))
        assert set(represented) == inventory
        for a, b in itertools.product(inventory, repeat=2):
            x,y = represented[a], represented[b]
            overlap = max(x[0],y[0]) <= min(x[1],y[1])
            assert overlap == (a.startswith(b) or b.startswith(a))
            pairs += 1
    source_patterns = [('A',), ('A','A'), ('A','B'), ('A','B','A'),
                       ('A','B','B'), ('A','B','C'), ('A','B','C','A')]
    cases, sat, unsat = 0, 0, 0
    for atoms in source_patterns:
        for text in strings:
            expected = brute(atoms,text)
            result = solve(atoms,text,seconds=2,workers=1)
            assert result['status'] in ('OPTIMAL','FEASIBLE','INFEASIBLE'), result
            found = result['status'] != 'INFEASIBLE'
            assert found == (expected is not None), (atoms,text,result,expected)
            if found:
                assert ground(atoms,text,result['full_code'])
                sat += 1
            else:
                unsat += 1
            cases += 1
    source = json.loads((ROOT/'experiments/yolo/gdt963_dioscorides_complete_content_code/src/SOURCE.json').read_text())
    atoms = source['records'][0]['atoms']
    # Unique one-character codes: exact original repetition/occurrence shape,
    # no Voyage text and no claimed realistic alphabet or decoding accuracy.
    code = {a: chr(0x400+i) for i,a in enumerate(sorted(set(atoms)))}
    text = ''.join(code[a] for a in atoms)
    domains = {a:[w] for a,w in code.items() if atoms.count(a)>1}
    planted = solve(atoms,text,domains,seconds=15,workers=1,hints=code)
    assert planted['status'] in ('OPTIMAL','FEASIBLE')
    assert ground(atoms,text,planted['full_code'])
    variable = {'A':'a','B':'ba','C':'bb'}
    result = solve(['A','B','C','B','A'], 'ababbbaa', {'B':['ba']},seconds=2,workers=1)
    assert result['status'] in ('OPTIMAL','FEASIBLE') and ground(['A','B','C','B','A'],'ababbbaa',result['full_code'])
    assert not ground(['A','B'],'aaa',{'A':'a','B':'aa'})
    report = dict(status='PASS', substring_inventories=len(strings), interval_prefix_pairs=pairs,
                  exact_oracle_cases=cases, oracle_sat=sat, oracle_unsat=unsat,
                  planted_full_source_occurrences=len(atoms), planted_status=planted['status'],
                  variable_length_domain_positive=True, forged_prefix_collision_rejected=True,
                  wall_seconds=time.monotonic()-started,
                  ceiling='Implementation controls only; no target computation or independent meaning.')
    (E/'artifacts/CONTROL_RESULTS.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
