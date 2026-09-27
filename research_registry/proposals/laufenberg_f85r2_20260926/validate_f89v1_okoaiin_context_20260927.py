#!/usr/bin/env python3
"""Reconstruct a bounded paragraph comparison; no semantic validation."""
import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
LOCI = [f'f89v1.{i}' for i in range(13, 21)]


def read(name):
    return json.loads((BASE / name).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', action='store_true')
    args = parser.parse_args()
    packet = read('F89V1_OKOAIIN_CONTEXT_RESULT_20260927.json')
    for r in packet['bound_public_files']:
        p = Path(r['path'])
        assert not p.is_absolute() and '..' not in p.parts
        assert sha(BASE / p) == r['sha256'], str(p)
    review = read('F89V1_OKOAIIN_CONTEXT_REVIEW_20260927.json')
    assert review['required_corrections'] == []
    for r in review['reviewed_artifacts']:
        assert sha(ROOT / r['path']) == r['sha256'], r['path']
    source = read('F89V1_OKOAIIN_CONTEXT_SOURCE_20260927.json')
    assert source['registered_scope'] == LOCI and len(source['units']) == 24
    rows = source['query']['rows']
    assert len(rows) == 230 and {r['locus'] for r in rows} == set(LOCI)
    rings = read(packet['prior_ring_packet']['path'])['groups']
    assert sha(BASE / packet['prior_ring_packet']['path']) == packet['prior_ring_packet']['sha256']
    for result in packet['analyses']:
        edition = result['edition']
        stream = []
        occurrences = []
        for locus in LOCI:
            line = sorted((r for r in rows if r['edition'] == edition and r['locus'] == locus),
                          key=lambda r: int(r['source_group_index']))
            words = [r['ivtff_group_raw'] for r in line]
            unit = next(u for u in source['units'] if u['edition'] == edition and u['locus'] == locus)
            assert words == unit['groups']
            assert sorted({r['paragraph_start'] for r in line}) == unit['paragraph_start']
            assert sorted({r['paragraph_end'] for r in line}) == unit['paragraph_end']
            stream.extend(words)
            occurrences.extend({'locus': locus, 'group_index': i+1, 'form': w}
                               for i, w in enumerate(words)
                               if w in ('okoaiin', 'okaiin', 'qokaiin', 'chokaiin'))
        counts = Counter(stream)
        assert len(stream) == result['raw_groups'] and len(counts) == result['distinct_raw_forms']
        assert {w: n for w, n in counts.items() if n > 1} == result['repeated_forms']
        assert occurrences == result['family_form_occurrences'] and counts['okoaiin'] == 1
        for overlap in result['ring_overlaps']:
            ring = next(r['groups'] for r in rings if r['edition'] == edition and r['locus'] == overlap['ring_locus'])
            assert sorted(set(stream) & set(ring)) == overlap['shared_forms']
            pairs = set(zip(stream, stream[1:])) & set(zip(ring, ring[1:]))
            assert [list(p) for p in sorted(pairs)] == overlap['linear_bigrams']
    assert packet['confirmed_words'] == 0 and packet['new_target_admissions'] == []
    if args.sources:
        query = source['query']
        cmd = query['command']
        expected = ['./vmanus-exp', 'query-tsv', 'experiments/semantic_assumptions/results/source_separator_transcription.tsv', '--selector', 'locus']
        for locus in LOCI:
            expected += ['--allow', locus]
        assert cmd[:-2] == expected and cmd[-2] == '--columns'
        assert sha(ROOT / cmd[2]) == query['source_sha256']
        run = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
        assert list(csv.DictReader(io.StringIO(run.stdout), delimiter='\t')) == rows
        assert run.stderr.strip() == query['guard_stderr']
        history = read('F89V1_OKOAIIN_HISTORICAL_BOUNDS_20260927.json')
        cache = BASE / history['source']
        assert sha(cache) == history['source_sha256']
        text = cache.read_text()
        for entry in history['entries']:
            a, b = entry['unicode_character_bounds']
            assert hashlib.sha256(text[a:b].encode()).hexdigest() == entry['html_fragment_sha256']
    print(json.dumps({'status': 'PASS_CONTEXT_REPLAY_AND_RECEIPTS_ONLY',
                      'reader_locus_rows': 24, 'raw_groups': 230, 'source_replay': args.sources,
                      'limit': 'No independent source translation, word meaning or grammar verification.'}, indent=2))


if __name__ == '__main__':
    main()
