"""Frozen exact lexical packing; no meanings are fitted here."""
import argparse
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
ART = EXP / 'artifacts'
MODES = ['ATOMIC_ONLY', 'ATOMIC_OR_BINARY', 'ALWAYS_DECOMPOSE_WHEN_AVAILABLE', 'EXACT_OLD_SPACE_ONLY']

def read(path):
    return json.loads(Path(path).read_text())

def dump(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def gate():
    public = read(ART / 'PUBLIC_REGISTRATION.json')
    assert public['remote_verified'] and len(public['commit']) == 40
    for item in read(EXP / 'PREREG_LOCK.json')['files']:
        assert sha(ROOT / item['path']) == item['sha256'], item['path']
    return public['commit']

def build():
    spec = read(EXP / 'src/SPEC.json')
    o = read(ROOT / spec['original'])
    e = read(ROOT / spec['extension'])
    packet = read(ROOT / spec['owned_paragraphs'])
    assert packet['RF1b'] == []
    assert o['lexicon'] == e['frozen_parent']['all_71_lexical_entries_unchanged']
    assert not o['lexicon'].keys() & e['new_17_lexical_entries'].keys()
    lex = dict(sorted((o['lexicon'] | e['new_17_lexical_entries']).items()))
    assert len(lex) == 88
    binaries = defaultdict(list)
    for u in lex:
        for v in lex:
            binaries[u + v].append([u, v])

    def analyses(w):
        parts = ([[w]] if w in lex else []) + sorted(binaries.get(w, []))
        return [dict(parts=p, tags=[lex[x]['tag'] for x in p]) for p in parts]

    units = []
    projection = o['target']['owned_projection']['records']
    for reader, name in [('PROJECTED', None), ('ZL3b', 'diplomatic_ZL3b'), ('IT2a', 'diplomatic_IT2a')]:
        lines = projection if name is None else o['target'][name]['lines']
        blocks = []
        assert len(lines) == len(o['complete_clauses']) == 9
        for line, clause in zip(lines, o['complete_clauses']):
            assert line['locus'] == clause['locus']
            words = line['raw'].split(' ') if name is None else line['words']
            groups = []
            for i, w in enumerate(words):
                sid = f"PROJECTED|{line['locus']}|G{i+1:03d}" if name is None else line['source_ids'][i]
                groups.append(dict(source_id=sid, locus=line['locus'], raw=w,
                    anchor_eligible=line.get('anchor_eligible'), analyses=analyses(w)))
            blocks.append(dict(id=clause['id'], loci=[line['locus']],
                expected_tags=clause['terminal_tags'], canonical_words=clause['raw'].split(' '), groups=groups))
        units.append(dict(id='ORIGINAL_'+reader, family='ORIGINAL', reader=reader,
            source_status='EDITORIAL_PROJECTION' if name is None else 'OWNED_DIPLOMATIC_GROUPS', blocks=blocks))
    for reader, name in [('ZL3b', 'complete_raw_record'), ('IT2a', 'alternate_IT2a_complete_record')]:
        record = e['target'][name]
        groups = []
        for line in record['lines']:
            assert len(line['source_ids']) == len(line['words'])
            for sid, w in zip(line['source_ids'], line['words']):
                groups.append(dict(source_id=sid, locus=line['locus'], raw=w,
                    anchor_eligible=line['anchor_eligible'], analyses=analyses(w)))
        clauses = e['complete_new_block_clauses']
        tags = [t for c in clauses for t in c['terminal_tags']]
        words = [w for c in clauses for w in c['words']]
        assert len(tags) == len(words) == 33
        units.append(dict(id='EXTENSION_'+reader, family='EXTENSION', reader=reader,
            source_status='OWNED_DIPLOMATIC_GROUPS', blocks=[dict(id='C10-C13',
                loci=[line['locus'] for line in record['lines']], expected_tags=tags,
                canonical_words=words, groups=groups)]))
    return dict(lexicon=lex, inventory=[dict(raw=w, analyses=analyses(w)) for w in lex],
        units=units, availability=[dict(family=f, reader='RF1b', status='NO_WHOLE_READER') for f in ['ORIGINAL','EXTENSION']])

def parse(block, mode):
    groups, target = block['groups'], block['expected_tags']
    if mode == 'EXACT_OLD_SPACE_ONLY' and [g['raw'] for g in groups] != block['canonical_words']:
        return dict(id=block['id'], count=0, edges=[])
    forward = {(0, 0): 1}
    candidates = []
    for i, group in enumerate(groups):
        choices = group['analyses']
        if mode in ['ATOMIC_ONLY', 'EXACT_OLD_SPACE_ONLY']:
            choices = [a for a in choices if len(a['parts']) == 1]
        elif mode == 'ALWAYS_DECOMPOSE_WHEN_AVAILABLE' and any(len(a['parts']) == 2 for a in choices):
            choices = [a for a in choices if len(a['parts']) == 2]
        for (gi, ti), ways in list(forward.items()):
            if gi != i:
                continue
            for a in choices:
                end = ti + len(a['tags'])
                if target[ti:end] == a['tags']:
                    forward[(i+1, end)] = forward.get((i+1, end), 0) + ways
                    candidates.append(dict(group_index=i, terminal_start=ti, terminal_end=end, **a))
    count = forward.get((len(groups), len(target)), 0)
    live = {(len(groups), len(target))}
    edges = []
    for edge in reversed(candidates):
        if (edge['group_index']+1, edge['terminal_end']) in live:
            live.add((edge['group_index'], edge['terminal_start']))
            edges.append(edge)
    edges.sort(key=lambda x: (x['group_index'], x['terminal_start'], x['parts']))
    if not count:
        assert not edges
    return dict(id=block['id'], count=count, edges=edges)

def fit(table):
    rows = []
    for unit in table['units']:
        modes = {}
        for mode in MODES:
            blocks = [parse(b, mode) for b in unit['blocks']]
            count = 1
            for b in blocks:
                count *= b['count']
            modes[mode] = dict(count=count, blocks=blocks)
        groups = [g for b in unit['blocks'] for g in b['groups']]
        unknown = [dict(source_id=g['source_id'], raw=g['raw']) for g in groups if not g['analyses']]
        rows.append(dict(id=unit['id'], groups=len(groups), modes=modes, unbound_groups=unknown,
            flagged_loci=sorted({g['locus'] for g in groups if g['anchor_eligible'] is False}),
            source_status=unit['source_status']))
    return dict(status='COMPLETE_FINITE_FIXED_STREAM_COMPARISON', units=rows,
        availability=table['availability'], confirmed_words=0, independent_confirmation_leaves=0,
        meaning_rivals='Opaque tags remain indistinguishable. Original E/H branches and extension stone/assembly attributed-claim alternatives retain old status.',
        claim_ceiling='Exact compatibility with authored fixed terminal patterns only; no learned grammar, physical execution, meaning or significance.')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--prepare', action='store_true')
    ap.add_argument('--execute', action='store_true')
    args = ap.parse_args()
    assert args.prepare != args.execute
    commit = gate()
    if args.prepare:
        assert not (ART / 'TABLE_LOCK.json').exists(), 'Never overwrite frozen alternatives'
        table = build()
        path = ART / 'ALL_ALTERNATIVES.json'
        dump(path, table)
        dump(ART / 'TABLE_LOCK.json', dict(path=str(path.relative_to(ROOT)), sha256=sha(path),
            prereg_commit=commit, frozen_utc=datetime.now(timezone.utc).isoformat(), status='FROZEN_BEFORE_FIT'))
        print('Frozen complete alternatives; no fit executed.')
    else:
        lock = read(ART / 'TABLE_LOCK.json')
        assert lock['prereg_commit'] == commit
        assert sha(ROOT / lock['path']) == lock['sha256']
        table = read(ROOT / lock['path'])
        assert table == build()
        result = fit(table)
        dump(ART / 'RESULT.json', result)
        lines = ['unit\tgroups\tunbound_groups\tflagged_loci\t'+'\t'.join(MODES)]
        for r in result['units']:
            lines.append('\t'.join(map(str,[r['id'],r['groups'],len(r['unbound_groups']),','.join(r['flagged_loci']),*[r['modes'][m]['count'] for m in MODES]])))
        (ART / 'CANDIDATE_PREDICTIONS.tsv').write_text('\n'.join(lines)+'\n')
        print('\n'.join(lines))

if __name__ == '__main__':
    main()
