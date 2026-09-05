#!/usr/bin/env python3
"""Separate same-author coverage/substitution audit; no semantic validation."""
import argparse
import copy
import csv
import json
from collections import Counter
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
ROOT = EXP.parents[2]
PRIOR = ROOT/'experiments/yolo/gdt822_qokeey_physical_fire_context/artifacts'


def read(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def audit(trials, hits, coverage):
    groups = read(PRIOR/'SOURCE_GROUPS.tsv')
    expected_hits = {g['source_group_id']: g for g in groups if g['ivtff_group_raw'] == 'qol'}
    assert len(hits) == len({h['source_group_id'] for h in hits}) == len(expected_hits) == 101
    assert {h['source_group_id'] for h in hits} == set(expected_hits)
    for h in hits:
        assert all(h[k] == v for k,v in expected_hits[h['source_group_id']].items())
    loci = {g['locus'] for g in expected_hits.values()}
    contexts = read(PRIOR/'CONTEXTS.tsv')
    required = {c['block_id'] for c in contexts if c['locus'] in loci}
    assert len(coverage) == len(required) == 15 and {b['block_id'] for b in coverage} == required
    old_blocks = {b['block_id']: b for b in read(PRIOR/'BLOCKS.tsv')}
    for b in coverage:
        assert b['complete'] == '1' and b['kind'] == 'P'
        assert all(b[k] == v for k,v in old_blocks[b['block_id']].items())
        assert json.loads(b['qol_loci_json']) == [l for l in json.loads(b['loci_json']) if l in loci]
    key = lambda r: (r['world'], r['locus'], r['edition'])
    originals = {key(r): r for r in read(PRIOR/'TRIALS.tsv') if r['locus'] in loci}
    assert len(trials) == len({key(t) for t in trials}) == len(originals) == 222
    assert {key(t) for t in trials} == set(originals)
    changed = 0
    for t in trials:
        o = originals[key(t)]
        assert all(t[k] == o[k] for k in o if k not in ['literal_json','confidence'])
        words = json.loads(t['source_groups_json'])
        old, new = json.loads(o['literal_json']), json.loads(t['literal_json'])
        ids = json.loads(t['source_group_ids_json'])
        assert len(words) == len(old) == len(new) == len(ids)
        for word, before, after, gid in zip(words, old, new, ids):
            if word == 'qol':
                assert gid in expected_hits and before == '[qol]' and after == 'daraus?'
                changed += 1
            else:
                assert after == before
        assert t['confidence'] == 'C0_EXPLORATORY_WHOLE_MEANING_NOT_IDENTIFICATION'
    assert changed == 202
    reviewed = [c for c in contexts if c['block_id'] in required]
    assert len(reviewed) == 217 and Counter(c['kind'] for c in reviewed) == {'P':208,'L':9}
    assert all(not c['page'].startswith('f84') for c in contexts)
    return dict(exact_reader_groups=101, target_loci=len(loci), literal_rows=len(trials),
        changed_positions=changed, complete_P_blocks=15, reread_loci=217)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    trials, hits, coverage = [read(EXP/'artifacts'/name) for name in ['TRIALS.tsv','EXACT_HITS.tsv','COVERAGE.tsv']]
    counts = audit(trials, hits, coverage)
    mutations = {}
    def rejected(name, ts, hs, cs):
        try:
            audit(ts, hs, cs)
        except AssertionError:
            mutations[name] = 'REJECTED'
        else:
            raise AssertionError('Mutation survived: '+name)
    rejected('omit_one_qol', trials, hits[:-1], coverage)
    rejected('omit_complete_paragraph', trials, hits, coverage[:-1])
    for name, loc, edition, word, replacement in [
        ('change_water_to_fire','f75r.33','IT2a','qokain','Feuer?'),
        ('split_joined_qolchedy','f77r.34','ZL3b','qolchedy','daraus wird?'),
        ('drop_second_source_reference','f77r.38','IT2a','qol',''),
        ('causal_sense_drift','f81r.20','IT2a','qol','deshalb?')]:
        ts = copy.deepcopy(trials)
        row = next(t for t in ts if t['locus'] == loc and t['edition'] == edition and t['world'] == 'ASCENT')
        words = json.loads(row['source_groups_json']); values = json.loads(row['literal_json'])
        index = max(i for i,w in enumerate(words) if w == word)
        values[index] = replacement; row['literal_json'] = json.dumps(values, ensure_ascii=False)
        rejected(name, ts, hits, coverage)
    result = json.loads((EXP/'artifacts/RESULT.json').read_text())
    assert result['exact_qol_reader_groups'] == counts['exact_reader_groups']
    assert result['reread_loci'] == counts['reread_loci']
    assert result['literal_rows'] == counts['literal_rows']
    assert result['all39_qol_census'] is False and result['meanings_validated'] is False
    output = json.dumps(dict(status='PASS', validator='SAME_AUTHOR_SEPARATE_IMPLEMENTATION_NOT_SEMANTIC_REVIEW',
        counts=counts, mutation_checks=mutations, meanings_validated=False), indent=2, sort_keys=True)+'\n'
    path = EXP/'artifacts/VALIDATION.json'
    if args.check:
        assert path.read_text() == output
    else:
        path.write_text(output)
    print('GDT823 coverage and unchanged-word audit PASS; six mutations rejected; no semantic proof')


if __name__ == '__main__':
    main()
