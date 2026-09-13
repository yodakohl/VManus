"""Reconstruct the source census and exhaust all registered antecedent pairs."""
import collections
import csv
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parent
ROOT = next(p for p in E.parents if (p / 'vmanus-work').exists())
W2, W5, W7 = (E.parent / n for n in ['W02', 'W05', 'W07'])
spec = json.loads((E / 'SPEC.json').read_text())
for f in spec['inputs']:
    assert hashlib.sha256((ROOT / f['path']).read_bytes()).hexdigest() == f['sha256']

def read(p):
    with p.open() as f: return list(csv.DictReader(f, delimiter='\t'))

source = json.loads((W2 / 'SOURCE.json').read_text())
alt = json.loads((W2 / 'ALTERNATE_LINES.json').read_text())['readings']
lex = {r['form']: r for r in read(W2 / 'LEXICON.tsv')}
old = read(W5 / 'ARGUMENTS.tsv')
qual = read(W5 / 'QUALITY_ASSERTIONS.tsv')
hosts = [t['hosts']['ZL3b'][0] for t in source['targets']]
packets = {}
for ed, lines in alt.items():
    lm = {l['metadata']['locus']: l['groups'] for l in lines}
    for p in hosts:
        assert not p['page'].startswith('f84')
        packets[ed, p['id']] = [(f"{l['locus']}:{i}", g['ivtff_group_raw']) for l in p['lines'] for i, g in enumerate(lm[l['locus']], 1)]
frames = read(E / 'FRAMES.tsv')
expected_targets = {(ed, p, i) for (ed, p), pairs in packets.items() for i, w in pairs if w == 'ychor'}
assert len(frames) == len(expected_targets) == 40
assert {(r['edition'], r['paragraph'], r['target']) for r in frames} == expected_targets
assert collections.Counter(r['edition'] for r in frames) == {'ZL3b': 13, 'IT2a': 14, 'RF1b': 13}
for r in frames:
    pairs = packets[r['edition'], r['paragraph']]
    loc = r['target'].rsplit(':', 1)[0]
    loci = list(dict.fromkeys(i.rsplit(':', 1)[0] for i, w in pairs))
    assert r['previous_locus'] == loci[loci.index(loc) - 1]
    assert r['all_prior_loci'].split(';') == loci[:loci.index(loc)]
    assert r['target_raw'] == ' '.join(w for i, w in pairs if i.rsplit(':', 1)[0] == loc)

kernels = read(E / 'KERNELS.tsv')
def kk(r): return r['edition'], r['grammar'], r['paragraph'], r['kernel']
index = {kk(r): r for r in kernels}
expected_kernel_ids = set()
for a in old:
    k = a['edition'], a['variant'], a['paragraph'], a['operation'] + ':ACT'
    expected_kernel_ids.add(k); r = index[k]
    assert r['patient'] == a['patient'] and r['patient_form'] == a['patient_form'] and r['second'] == a['coingredient']
    assert r['predicate'] == 'ACT:' + a['form'] and r['debts'] == a['debts']
    debt = set(filter(None, a['debts'].split(';')))
    complete = bool(a['patient']) and not bool(debt & {'MISSING_PATIENT', 'MISSING_RELATION_PARTNER', 'EXTRACT_PATIENT_NOT_BOUND'})
    assert (r['complete_U'] == 'True') == complete
    assert (r['complete_D'] == 'True') == (complete and 'MISSING_COINGREDIENT' not in debt)
for q in qual:
    if q['kind'] != 'STANDALONE': continue
    k = 'ZL3b', q['variant'], q['paragraph'], q['mention'] + ':STATE:' + q['axis']
    expected_kernel_ids.add(k); r = index[k]
    assert r['patient'] == q['patient'] and r['patient_form'] == q['patient_form'] and r['debts'] == q['debts']
    assert r['predicate'] == 'STATE:' + ':'.join(q[v] for v in ['axis', 'value', 'scope'])
    assert (r['complete_U'] == 'True') == (r['complete_D'] == 'True') == bool(q['patient'])
assert len(kernels) == len(index) and set(index) == expected_kernel_ids

comparisons = read(E / 'ADDITIVE_COMPARISON.tsv')
links = read(E / 'ADDITIVE_LINKS.tsv')
expected_comparisons, expected_links = set(), set()
for ed, p, target in expected_targets:
    order = {i: n for n, (i, w) in enumerate(packets[ed, p])}
    loc = target.rsplit(':', 1)[0]
    for g in spec['grammars']:
        rows = [r for r in kernels if (r['edition'], r['grammar'], r['paragraph']) == (ed, g, p)]
        prev = [r for r in rows if order[r['mention']] < order[target]]
        body = [r for r in rows if r['locus'] == loc]
        for mix in spec['mix_models']:
            for model in ['AT', 'AP']:
                key = ed, g, mix, model, p, target
                expected_comparisons.add(key)
                cp = [r for r in comparisons if tuple(r[k] for k in ['edition', 'grammar', 'mix', 'model', 'paragraph', 'target']) == key]
                assert len(cp) == 1
                matched = []
                for q in body:
                    if q['complete_' + mix] != 'True': continue
                    candidates = [a for a in prev if a['complete_' + mix] == 'True']
                    if model == 'AT':
                        candidates = [a for a in candidates if a['patient_form'] == q['patient_form'] and a['predicate'] != q['predicate']]
                    else:
                        candidates = [a for a in candidates if a['predicate'] == q['predicate'] and a['patient_form'] != q['patient_form']]
                    matched.extend((a['kernel'], q['kernel']) for a in candidates)
                expected_links |= {key + pair for pair in matched}
                covered = {b for a, b in matched}; r = cp[0]
                assert int(r['prior_kernels']) == len(prev) and int(r['body_kernels']) == len(body)
                assert int(r['complete_body_kernels']) == sum(a['complete_' + mix] == 'True' for a in body)
                assert int(r['possible_prior_links']) == len(matched) and int(r['linked_body_kernels']) == len(covered)
                assert (r['all_registered_body_kernels_linked'] == 'True') == (bool(body) and len(covered) == len(body))
assert len(comparisons) == len(expected_comparisons)
assert {(r['edition'],r['grammar'],r['mix'],r['model'],r['paragraph'],r['target'],r['prior_kernel'],r['body_kernel']) for r in links} == expected_links
assert len(links) == len(expected_links) == 0

take = read(E / 'TAKE_ARGUMENTS.tsv'); effects = read(E / 'TAKE_OLD_EFFECTS.tsv')
assert len(take) == 120
assert {(r['edition'], r['paragraph'], r['target'], r['grammar']) for r in take} == {
    (ed, p, t, g) for ed, p, t in expected_targets for g in spec['grammars']}
mods = set(json.loads((W5 / 'SPEC.json').read_text())['transparent_roles'])
expected_effects = set()
for n in take:
    pairs = packets[n['edition'], n['paragraph']]
    pos = {i: j for j, (i, w) in enumerate(pairs)}; names = dict(pairs)
    aa = [a for a in old if (a['edition'], a['variant'], a['paragraph']) == (n['edition'], n['grammar'], n['paragraph'])]
    ops = {a['operation'] for a in aa}
    loc = n['target'].rsplit(':', 1)[0]
    line = [i for i, w in pairs if i.rsplit(':', 1)[0] == loc]
    materials = {i for i, w in pairs if lex.get(w, {}).get('role') in spec['material_roles']}
    right = [i for i in line[1:] if i in materials and not any(pos[n['target']] < pos[o] < pos[i] for o in ops)]
    earlier = [i for i, w in pairs if i in materials and pos[i] < pos[n['target']]]
    patient = right[0] if right else earlier[-1] if earlier else ''
    rule = 'LOCAL_RIGHT' if right else 'PARAGRAPH_CARRY' if earlier else 'MISSING'
    j = 1
    while j < len(line) and line[j] in ops: j += 1
    members = line[1:j]
    if members and n['grammar'] != 'B':
        tail = j
        if n['grammar'] == 'M':
            while tail < len(line) and lex.get(names[line[tail]], {}).get('role') in mods: tail += 1
        if tail < len(line) and line[tail] in materials:
            patient = line[tail]; rule = 'SHARED_RIGHT_' + n['grammar']
            expected_effects |= {(n['edition'], n['grammar'], n['target'], member, patient) for member in members}
    assert n['patient'] == patient and n['patient_form'] == names.get(patient, '') and n['rule'] == rule
    assert n['added_commands'] == '1' and not n['new_written_product']
assert {(e['edition'],e['grammar'],e['target'],e['old_operation'],e['N_patient']) for e in effects} == expected_effects
assert len(effects) == 6 and all(e['old_patient'] == e['N_patient'] and e['patient_changes'] == 'False' for e in effects)
chains = read(E / 'TAKE_BODY_CHAINS.tsv')
expected_chains = {(n['edition'], n['grammar'], n['target'], a['operation'], n['patient']) for n in take for a in old
    if (a['edition'], a['variant'], a['paragraph']) == (n['edition'], n['grammar'], n['paragraph']) and n['patient']
    and n['patient'] == a['patient'] and a['operation'].rsplit(':', 1)[0] == n['target'].rsplit(':', 1)[0]}
assert len(chains) == len(expected_chains) == 69
assert {(r['edition'],r['grammar'],r['target'],r['body_operation'],r['common_patient']) for r in chains} == expected_chains

alignment = read(E / 'ALIGNMENT.tsv'); oldalign = read(W7 / 'ALIGNMENT.tsv')
assert len(alignment) == len(oldalign) == 900
for r, o in zip(alignment, oldalign):
    assert all(r[k] == o[k] for k in ['paragraph', 'locus', 'index', 'raw'])
    if r['raw'] == 'ychor':
        assert r['additive'] == 'ferner' and r['N'] == 'nimm' and r['Z'] == '[ychor: Rahmenbedeutung offen]'
    else:
        value = 'durcharbeiten [U] / zwei Materialien vermischen [D]' if lex.get(r['raw'], {}).get('role') == 'MIX' else o['P_U']
        assert r['additive'] == r['N'] == r['Z'] == value
text = (E / 'READING.md').read_text()
for p in hosts:
    for l in p['lines']:
        assert text.count(l['locus'] + ': `' + ' '.join(l['words']) + '`') == 1
result = json.loads((E / 'RESULT.json').read_text())
assert result['frame_rows'] == 40 and result['comparison_rows'] == 480 and result['link_rows'] == 0
assert result['primary_targets'] == 13 and result['body_assumed_groups'] == 517 and result['unread_body_groups'] == 370
assert result['empirical_global_winner'] is None and not result['held_access'] and not result['significance_claim']
assert result['meaning_identifications'] == result['independent_confirmation_capacity'] == 0
out = dict(status='PASS', verified='all raw targets including IT-only extra; exact fixed kernels and all AT/AP antecedent pairs; N bindings and unchanged old patients; all full paragraph groups',
    frames=40, kernels=len(kernels), additive_links=len(links), take_arguments=120, take_body_links=69,
    primary_quality_scope='W05 STANDALONE only', alternate_quality_scope='NOT_RECOMPUTED',
    independent_observer=False, meaning_validation=False,
    script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
(E / 'VALIDATION.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(out, ensure_ascii=False))
