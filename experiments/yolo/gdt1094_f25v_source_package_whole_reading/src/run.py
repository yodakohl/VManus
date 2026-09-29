#!/usr/bin/env python3
"""Complete descriptive account; unchanged GDT1051 replay, no decoder."""
import csv
import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parents[1]
LEGACY = ROOT / 'experiments/yolo/gdt1051_frozen_grammar_local_application/src/run.py'
spec = importlib.util.spec_from_file_location('frozen_gdt1051', LEGACY)
formal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(formal)


def compute():
    with (BASE / 'src/TARGET_RAW.tsv').open() as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    assert len(rows) == 176 and {r['page'] for r in rows} == {'f25v'}
    groups = [formal.parse_group('f25v_complete_paragraph', r) for r in rows]
    chunks = formal.make_chunks(groups, formal.load_merges())
    byline = defaultdict(list)
    for r in rows:
        byline[r['edition'], r['locus']].append(r)
    lines, inventory, summaries = [], [], {}
    for (edition, locus), line in sorted(byline.items()):
        assert [int(r['source_group_index']) for r in line] == list(range(1, len(line) + 1))
        assert all(int(r['source_group_count']) == len(line) for r in line)
        w = [r['ivtff_group_raw'] for r in line]
        lines.append(dict(edition=edition, locus=locus, raw_group_count=len(w), raw_groups=' '.join(w),
            exact_daiin=w.count('daiin'), adjacent_daiin_pairs=sum(a == b == 'daiin' for a, b in zip(w, w[1:])),
            paragraph_start=line[0]['paragraph_start'], paragraph_end=line[-1]['paragraph_end']))
    for edition in ('ZL3b', 'IT2a', 'RF1b'):
        rr = [r for r in rows if r['edition'] == edition]
        counts = Counter(r['ivtff_group_raw'] for r in rr)
        summaries[edition] = dict(raw_groups=len(rr), types=len(counts), exact_daiin=counts['daiin'],
            physical_lines=sum(k[0] == edition for k in byline),
            adjacent_daiin_pairs=sum(r['adjacent_daiin_pairs'] for r in lines if r['edition'] == edition))
        for word, count in sorted(counts.items(), key=lambda z: (-z[1], z[0])):
            inventory.append(dict(edition=edition, raw_form=word, count=count,
                positions=';'.join(f"{r['locus']}:{r['source_group_index']}" for r in rr if r['ivtff_group_raw'] == word)))
    profiles = []
    for p in json.loads((BASE / 'src/WORD_PROFILES.json').read_text())['profiles']:
        for edition, v in p['editions'].items():
            profiles.append(dict(raw_form=p['form'], edition=edition, admitted_count=v['count'],
                admitted_pages=v['pages_with_form'], rank=v['rank'], starts=v['positions']['start'],
                middles=v['positions']['middle'], ends=v['positions']['end'], adjacent_self_pairs=v['repetition']['adjacent_pairs']))
    packages = json.loads((BASE / 'src/PACKAGES.json').read_text())['packages']
    candidates = [dict(package=p['id'], required_relations='; '.join(p['relations']),
        observed_target='Complete seven-line target inventoried; no fixed lexical/argument assignment',
        target_contradiction='NOT_TESTED: no complete candidate writer or reading',
        ambiguity='Neither selected nor refuted; source-matching role substitutions remain free',
        independent_confirmation_capacity=0) for p in packages]
    result = dict(schema='gdt1094-exploratory-account-v1',
        status='FULL_PASSAGE_ACCOUNTED_NO_COMPLETE_SEMANTIC_READING', summaries=summaries,
        source_packages=len(candidates), raw_groups=len(groups),
        formal_parsable_groups=sum(g['wrapper_host'] is not None for g in groups),
        hard_chunks=len(chunks), formal_parsable_chunks=sum(c['units'] is not None for c in chunks),
        fixed_semantic_tests=0, complete_semantic_candidates=0, confirmed_words=0,
        independent_confirmation_capacity=0,
        inference='No coherent target reading obtained; this does not empirically refute the source packages.',
        access_correction='f25v already admitted in the 179-selector text contract; no new text admission.',
        input_hashes={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (BASE / 'src/TARGET_RAW.tsv', BASE / 'src/WORD_PROFILES.json', BASE / 'src/PACKAGES.json', LEGACY, formal.MERGES)},
        sealed_data={'f84': 'FORBIDDEN', 'f84r': 'FORBIDDEN'})
    return result, dict(groups=groups, chunks=chunks), dict(FULL_PASSAGE=lines, FORM_INVENTORY=inventory,
        PROFILE_SUMMARY=profiles, CANDIDATES=candidates)


def main():
    result, replay, tables = compute()
    for name, obj in [('RESULT.json', result), ('FORMAL_REPLAY.json', replay)]:
        (BASE / 'artifacts' / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
    for name, rows in tables.items():
        with (BASE / 'artifacts' / (name + '.tsv')).open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
            w.writeheader(); w.writerows(rows)
    print(json.dumps(result['summaries'], indent=2))


if __name__ == '__main__':
    main()
