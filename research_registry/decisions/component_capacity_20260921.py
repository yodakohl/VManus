"""Independent small preflight recount of two unselected writer proposals."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASES = [('IDEA000473', 'raw_palladius_fixed_f82r_comparison_writer_20260921.json'),
         ('IDEA000474', 'raw_euclid_i5_fixed_f82r_capacity_20260921.json')]


def main():
    rows = []
    for idea, name in CASES:
        path = ROOT / 'research_registry/proposals' / name
        proposal = json.loads(path.read_text())
        program = proposal['program']
        arities = program.get('fixed_arities', program.get('arities'))
        atoms = []

        def visit(node):
            if isinstance(node, str):
                atoms.append(node)
                return
            head, *children = node
            assert len(children) == arities[head], head
            atoms.append(head)
            for child in children:
                visit(child)

        visit(program['ast'])
        assert atoms == program['preorder_atoms']
        assert dict(Counter(atoms)) == program.get('atom_counts', program.get('counts'))
        target = ROOT / proposal['target']['file']
        assert hashlib.sha256(target.read_bytes()).hexdigest() == proposal['target']['sha256']
        words = json.loads(target.read_text())['words']
        n, t, w, k = len(atoms), len(set(atoms)), len(words), len(set(words))
        c, alphabet = sum(map(len, words)), len(set(''.join(words)))
        max_word_types = t + n - w
        min_characters = n + max(0, t - alphabet)
        rows.append(dict(idea=idea, proposal=str(path.relative_to(ROOT)),
                         proposal_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                         atoms=n, atom_types=t, groups=w, word_types=k, characters=c,
                         alphabet=alphabet, maximum_word_types=max_word_types,
                         minimum_distinct_code_characters=min_characters,
                         word_capacity_ok=n >= w and max_word_types >= k,
                         character_capacity_ok=min_characters <= c,
                         status='EXACT_SUPPLIED_WRITER_CONTRADICTED',
                         diplomatic_scope='Normalized working copy only; see GDT1015 SCOPE_CORRECTION.md'))
    assert rows[0]['maximum_word_types'] < rows[0]['word_types']
    assert rows[1]['minimum_distinct_code_characters'] > rows[1]['characters']
    result = dict(chronology='Independent post-draft preflight; no solver or blind preregistration claimed.',
                  rows=rows, solver_calls=0, confirmed_words=0,
                  word_bound='N atoms in W nonempty seam-preserving words allow at most N-W multiatom groups. At most T singleton strings plus N-W compound strings.',
                  character_bound='At most A distinct length-one codes exist over A characters; T-A remaining distinct nonempty codes add at least one character each.',
                  decision='Do not implement either exact writer; do not infer exclusion of source subjects or all compositional encodings.')
    output = Path(__file__).with_suffix('.json')
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(rows, indent=2))


if __name__ == '__main__':
    main()
