#!/usr/bin/env python3
"""Independent raw-cut DFS validator; no imports from the primary implementation."""
import argparse
import functools
import hashlib
import json
import re
import subprocess
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
ORIGINAL = 'experiments/yolo/gdt1023_amulet_complete_typed_assembly/src/SOURCE.json'
EXTENSION = 'research_registry/proposals/raw_f108r_amulet_frozen71_complete_commentary_20260921.json'
MODES = ('ATOMIC_ONLY', 'ATOMIC_OR_BINARY', 'ALWAYS_DECOMPOSE_WHEN_AVAILABLE', 'EXACT_OLD_SPACE_ONLY')


def read(path):
    return json.loads(Path(path).read_text())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def same(actual, expected, label):
    # bool and int must not compare equal accidentally.
    if type(actual) is not type(expected):
        raise AssertionError(f'{label}: type mismatch')
    if isinstance(expected, dict):
        if set(actual) != set(expected):
            raise AssertionError(f'{label}: keys mismatch {set(actual)^set(expected)}')
        for key in expected:
            same(actual[key], expected[key], f'{label}.{key}')
    elif isinstance(expected, list):
        if len(actual) != len(expected):
            raise AssertionError(f'{label}: length mismatch')
        for i, (a, e) in enumerate(zip(actual, expected)):
            same(a, e, f'{label}[{i}]')
    elif actual != expected:
        raise AssertionError(f'{label}: value mismatch')


def analyses(raw, lexicon):
    """Enumerate literal cut positions, independently of dictionary pair products."""
    result = []
    if raw in lexicon:
        result.append({'parts': [raw], 'tags': [lexicon[raw]['tag']]})
    for cut in range(1, len(raw)):
        left, right = raw[:cut], raw[cut:]
        if left in lexicon and right in lexicon:
            result.append({'parts': [left, right],
                           'tags': [lexicon[left]['tag'], lexicon[right]['tag']]})
    return sorted(result, key=lambda a: (len(a['parts']), a['parts']))


def choices(group, mode):
    options = group['analyses']
    binary = [a for a in options if len(a['parts']) == 2]
    if mode in ('ATOMIC_ONLY', 'EXACT_OLD_SPACE_ONLY'):
        return [a for a in options if len(a['parts']) == 1]
    if mode == 'ALWAYS_DECOMPOSE_WHEN_AVAILABLE':
        return binary or [a for a in options if len(a['parts']) == 1]
    assert mode == 'ATOMIC_OR_BINARY'
    return options


def edge_key(edge):
    return (edge['group_index'], edge['terminal_start'], tuple(edge['parts']))


def solve_block(block, mode):
    groups, wanted = block['groups'], block['expected_tags']
    if mode == 'EXACT_OLD_SPACE_ONLY' and [g['raw'] for g in groups] != block['canonical_words']:
        return {'id': block['id'], 'count': 0, 'edges': []}
    n, m = len(groups), len(wanted)
    options = [choices(g, mode) for g in groups]

    @functools.lru_cache(maxsize=None)
    def suffix(i, j):
        if i == n:
            return int(j == m)
        if j >= m:
            return 0
        total = 0
        for alternative in options[i]:
            k = j + len(alternative['tags'])
            if k <= m and wanted[j:k] == alternative['tags']:
                total += suffix(i + 1, k)
        return total

    total = suffix(0, 0)
    # Traverse only root-reachable nodes whose suffix has a complete parse.
    # This records every and only successful lexical edge, even for same tags.
    successful, seen = {}, set()
    def visit(i, j):
        if (i, j) in seen or i == n:
            return
        seen.add((i, j))
        for a in options[i]:
            k = j + len(a['tags'])
            if k <= m and wanted[j:k] == a['tags'] and suffix(i + 1, k):
                edge = {'group_index': i, 'terminal_start': j, 'terminal_end': k,
                        'parts': a['parts'], 'tags': a['tags']}
                successful[edge_key(edge)] = edge
                visit(i + 1, k)
    if total:
        visit(0, 0)
    return {'id': block['id'], 'count': total,
            'edges': [successful[k] for k in sorted(successful)]}


def solve_units(units):
    results = []
    for unit in units:
        modes = {}
        for mode in MODES:
            blocks = [solve_block(block, mode) for block in unit['blocks']]
            count = 1
            for block in blocks:
                count *= block['count']
            modes[mode] = {'count': count, 'blocks': blocks}
        results.append({'id': unit['id'], 'modes': modes})
    return results


def command(*args):
    return subprocess.check_output(args, cwd=ROOT, text=False, timeout=30).strip()


def local_path(path):
    p = Path(path)
    if p.is_absolute() or '..' in p.parts:
        raise AssertionError('non-repository path')
    result = ROOT / p
    if not result.resolve().is_relative_to(ROOT.resolve()):
        raise AssertionError('path escapes repository')
    return result


def registration_gate():
    receipt = read(EXP / 'artifacts/PUBLIC_REGISTRATION.json')
    assert receipt.get('remote_verified') is True
    commit = receipt['commit']
    assert re.fullmatch(r'[0-9a-f]{40}', commit), 'registration must use a full commit id'
    resolved = command('git', 'rev-parse', f'{commit}^{{commit}}').decode()
    assert resolved == commit
    remote_lines = command('git', 'ls-remote', '--heads', 'origin', 'main').decode().splitlines()
    assert len(remote_lines) == 1 and remote_lines[0].split()[1] == 'refs/heads/main'
    remote = remote_lines[0].split()[0]
    subprocess.run(['git', 'merge-base', '--is-ancestor', commit, remote], cwd=ROOT, check=True, timeout=30)
    subprocess.run(['git', 'merge-base', '--is-ancestor', commit, 'HEAD'], cwd=ROOT, check=True, timeout=30)
    lock_path = EXP / 'PREREG_LOCK.json'
    rel_lock = str(lock_path.relative_to(ROOT))
    registered_lock = subprocess.check_output(['git', 'show', f'{commit}:{rel_lock}'], cwd=ROOT, timeout=30)
    assert registered_lock == lock_path.read_bytes(), 'registered lock changed'
    lock = read(lock_path)
    files = lock['files']
    assert isinstance(files, list) and files
    paths = [item['path'] for item in files]
    assert len(paths) == len(set(paths)), 'duplicate lock entry'
    required = {ORIGINAL, EXTENSION, str(Path(__file__).resolve().relative_to(ROOT)),
                str((EXP/'src/run.py').relative_to(ROOT)), str((EXP/'METHOD.md').relative_to(ROOT)),
                str((EXP/'PREREGISTRATION.md').relative_to(ROOT)),
                str((EXP/'src/SPEC.json').relative_to(ROOT)),
                'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json'}
    assert required <= set(paths), 'missing claim-bearing registration file'
    for item in files:
        path, expected = item['path'], item['sha256']
        assert re.fullmatch(r'[0-9a-f]{64}', expected)
        assert digest(local_path(path).read_bytes()) == expected, f'working hash changed: {path}'
        committed = subprocess.check_output(['git','show',f'{commit}:{path}'],cwd=ROOT,timeout=30)
        assert digest(committed) == expected, f'committed hash changed: {path}'
    table = read(EXP/'artifacts/TABLE_LOCK.json')
    assert table['prereg_commit'] == commit
    table_path = local_path(table['path'])
    assert table_path.resolve() == (EXP/'artifacts/ALL_ALTERNATIVES.json').resolve()
    assert digest(table_path.read_bytes()) == table['sha256']
    return receipt


def self_test():
    tests = 0
    def check(actual, expected):
        nonlocal tests
        same(actual, expected, f'synthetic{tests+1}')
        tests += 1
    lex = {w:{'tag':t,'meaning':w,'status':'SYNTHETIC'} for w,t in
           [('a','A'),('b','B'),('ab','X'),('c','C'),('bc','BC'),('a?','UNCERTAIN')]}
    check(analyses('ab',lex),[{'parts':['ab'],'tags':['X']},{'parts':['a','b'],'tags':['A','B']}])
    check(analyses('abc',lex),[{'parts':['a','bc'],'tags':['A','BC']},{'parts':['ab','c'],'tags':['X','C']}])
    check(analyses('?',lex),[])
    check(analyses('a?',lex),[{'parts':['a?'],'tags':['UNCERTAIN']}])
    def block(words,tags,canonical=None):
        return {'id':'SYN','canonical_words':canonical if canonical is not None else words,
                'expected_tags':tags,'groups':[{'raw':w,'analyses':analyses(w,lex)} for w in words]}
    b=block(['ab'],['A','B'],['a','b'])
    for mode,expected in zip(MODES,[0,1,1,0]): check(solve_block(b,mode)['count'],expected)
    b=block(['ab'],['X'])
    for mode,expected in zip(MODES,[1,1,0,1]):check(solve_block(b,mode)['count'],expected)
    check(solve_block(block(['a','b'],['X']),'ATOMIC_OR_BINARY')['count'],0)
    check(solve_block(block(['abc'],['A','B','C']),'ATOMIC_OR_BINARY')['count'],0)
    check(solve_block(block(['unknown'],['A']),'ATOMIC_OR_BINARY')['count'],0)
    check(solve_block(block(['a'],[]),'ATOMIC_OR_BINARY')['count'],0)
    check(solve_block(block([],[]),'ATOMIC_OR_BINARY')['count'],1)
    # Same-tag lexical alternatives must remain two separate complete paths.
    lx={w:{'tag':'T'} for w in ['a','ab','bc','c']}
    synthetic={'id':'DUP','canonical_words':['abc'],'expected_tags':['T','T'],
               'groups':[{'raw':'abc','analyses':analyses('abc',lx)}]}
    ans=solve_block(synthetic,'ATOMIC_OR_BINARY')
    check(ans['count'],2);check(len(ans['edges']),2)
    # One valid local edge with a dead suffix may not survive in the DAG.
    dead={'id':'DEAD','canonical_words':['abc','z'],'expected_tags':['T','T','Z'],
          'groups':synthetic['groups']+[{'raw':'z','analyses':[]}]}
    check(solve_block(dead,'ATOMIC_OR_BINARY'),{'id':'DEAD','count':0,'edges':[]})
    # Clause seams may be inside one packed group; physical block seams cannot.
    check(solve_block(block(['ab'],['A','B']),'ATOMIC_OR_BINARY')['count'],1)
    check(solve_units([{'id':'LINES','blocks':[block(['a'],['A','B']),block(['b'],[])]}])[0]['modes']['ATOMIC_OR_BINARY']['count'],0)
    check(solve_units([{'id':'MULTI','blocks':[synthetic,synthetic]}])[0]['modes']['ATOMIC_OR_BINARY']['count'],4)
    print(json.dumps({'status':'PASS','synthetic_checks':tests,'manuscript_access':False}))


# Independent source reconstruction is defined below; metadata schema comes
# from the public specification, never from the primary implementation.

def reconstruct():
    original = read(ROOT / ORIGINAL)
    extension = read(ROOT / EXTENSION)
    old = original['lexicon']
    new = extension['new_17_lexical_entries']
    assert len(old) == 71 and len(new) == 17
    same(extension['frozen_parent']['all_71_lexical_entries_unchanged'], old,
         'frozen original dictionary')
    assert not set(old).intersection(new)
    lexicon = {**old, **new}
    assert len(lexicon) == 88 and all(isinstance(w, str) and w for w in lexicon)
    for value in lexicon.values():
        assert set(value) == {'tag', 'meaning', 'status'}
        assert all(isinstance(v, str) for v in value.values())
    clauses = original['complete_clauses']
    assert len(clauses) == 9
    extra = extension['complete_new_block_clauses']
    assert len(extra) == 4
    same(extension['frozen_parent']['all_nine_complete_clauses_unchanged'], clauses,
         'frozen original clauses')

    def groups_for_line(line, projected=False):
        if projected:
            # Exact inherited ASCII spaces; no strip, uncertainty removal or aliases.
            words = line['raw'].split(' ')
            assert all(words)
            ids = [f"PROJECTED|{line['locus']}|G{i:03d}" for i in range(1, len(words)+1)]
            flag = None
        else:
            words = line['words']
            ids = line['source_ids']
            flag = line['anchor_eligible']
        assert len(words) == len(ids)
        return [{'source_id': sid, 'locus': line['locus'], 'raw': raw,
                 'anchor_eligible': flag, 'analyses': analyses(raw, lexicon)}
                for sid, raw in zip(ids, words)]

    units = []
    for reader, field in [('PROJECTED','owned_projection'),
                          ('ZL3b','diplomatic_ZL3b'), ('IT2a','diplomatic_IT2a')]:
        projected = reader == 'PROJECTED'
        rows = original['target'][field]['records' if projected else 'lines']
        assert len(rows) == 9
        blocks = []
        for row, clause in zip(rows, clauses):
            assert row['locus'] == clause['locus']
            blocks.append({'id': clause['id'], 'loci': [row['locus']],
                           'expected_tags': clause['terminal_tags'],
                           'canonical_words': clause['raw'].split(' '),
                           'groups': groups_for_line(row, projected)})
        units.append({'id':f'ORIGINAL_{reader}', 'family':'ORIGINAL', 'reader':reader,
                      'source_status':'EDITORIAL_PROJECTION' if projected else 'OWNED_DIPLOMATIC_GROUPS',
                      'blocks':blocks})
    all_tags = [tag for clause in extra for tag in clause['terminal_tags']]
    canonical = [word for clause in extra for word in clause['words']]
    assert len(all_tags) == len(canonical) == 33
    for reader, field in [('ZL3b','complete_raw_record'),
                          ('IT2a','alternate_IT2a_complete_record')]:
        rows = extension['target'][field]['lines']
        assert [row['locus'] for row in rows] == ['f108r.45','f108r.46','f108r.47']
        block = {'id':'C10-C13', 'loci':[row['locus'] for row in rows],
                 'expected_tags':all_tags, 'canonical_words':canonical,
                 'groups':[g for row in rows for g in groups_for_line(row)]}
        units.append({'id':f'EXTENSION_{reader}', 'family':'EXTENSION', 'reader':reader,
                      'source_status':'OWNED_DIPLOMATIC_GROUPS', 'blocks':[block]})
    # These are inherited whole-reader boundaries, not substituted RF line spans.
    packet = read(ROOT/'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json')
    assert packet['RF1b'] == []
    assert extension['target']['RF1b'].startswith('No complete matching paragraph record')
    availability = [{'family':family, 'reader':'RF1b', 'status':'NO_WHOLE_READER'}
                    for family in ('ORIGINAL','EXTENSION')]
    return {'lexicon':lexicon,
            'inventory':[{'raw':word,'analyses':analyses(word,lexicon)} for word in sorted(lexicon)],
            'units':units, 'availability':availability}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--self-test',action='store_true')
    parser.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    if args.self_test:
        assert not args.execute
        self_test();return
    if not args.execute:
        parser.error('choose --self-test or --execute; no implicit target run')
    receipt=registration_gate()
    spec=read(EXP/'src/SPEC.json')
    assert spec['original']==ORIGINAL and spec['extension']==EXTENSION
    same(spec['modes'],list(MODES),'SPEC.modes')
    same(spec['maximum_terminals_per_group'],2,'SPEC.maximum_terminals_per_group')
    same(spec['recursive'],False,'SPEC.recursive')
    same(spec['cross_raw_space_fusion'],False,'SPEC.cross_raw_space_fusion')
    expected=reconstruct()
    actual=read(EXP/'artifacts/ALL_ALTERNATIVES.json')
    same(actual,expected,'ALL_ALTERNATIVES')
    result=read(EXP/'artifacts/RESULT.json')
    expected_units=solve_units(expected['units'])
    for computed, unit in zip(expected_units, expected['units']):
        groups=[g for block in unit['blocks'] for g in block['groups']]
        computed.update(groups=len(groups),
                        unbound_groups=[{'source_id':g['source_id'],'raw':g['raw']}
                                        for g in groups if not g['analyses']],
                        flagged_loci=sorted({g['locus'] for g in groups
                                             if g['anchor_eligible'] is False}),
                        source_status=unit['source_status'])
    same(result['units'],expected_units,'RESULT.units')
    validation={'status':'PASS','method':'independent literal-cut enumeration and memoized depth-first suffix counts',
                'prereg_commit':receipt['commit'],'all_alternatives_equal':True,'all_unit_mode_counts_and_successful_edges_equal':True,
                'unit_count':len(expected_units),'meaning_confirmation':False}
    (EXP/'artifacts/VALIDATION.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(validation,ensure_ascii=False))


if __name__=='__main__':
    main()
