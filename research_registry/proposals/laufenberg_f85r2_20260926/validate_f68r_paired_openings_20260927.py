#!/usr/bin/env python3
"""Check the two-locus intake and receipts; no semantic or native-vision proof."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
LOCI = {'f68r2.6', 'f68r2.31'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', action='store_true')
    args = parser.parse_args()
    packet = json.loads((BASE / 'F68R_PAIRED_OPENINGS_RESULT_20260927.json').read_text())
    for receipt in packet['bound_public_files']:
        relative = Path(receipt['path'])
        assert not relative.is_absolute() and '..' not in relative.parts
        assert digest(BASE / relative) == receipt['sha256'], str(relative)
    review = json.loads((BASE / 'F68R_PAIRED_OPENINGS_REVIEW_20260927.json').read_text())
    assert review['required_corrections'] == []
    for receipt in review['reviewed_artifacts']:
        relative = Path(receipt['path'])
        assert not relative.is_absolute() and '..' not in relative.parts
        assert digest(ROOT / relative) == receipt['sha256'], str(relative)
    source = json.loads((BASE / 'F68R_PAIRED_OPENINGS_SOURCE_20260927.json').read_text())
    assert set(source['scope']) == LOCI and source['new_global179_selectors'] == []
    assert len(source['groups']) == 6
    rows = next(q['rows'] for q in source['queries'] if q['id'] == 'groups')
    assert len(rows) == 58 and {r['locus'] for r in rows} == LOCI
    for group in source['groups']:
        selected = sorted((r for r in rows if (r['edition'], r['locus']) ==
                           (group['edition'], group['locus'])),
                          key=lambda r: int(r['source_group_index']))
        words = [r['ivtff_group_raw'] for r in selected]
        assert words == group['groups'] and len(words) == group['count']
        assert words[:3] == group['first_three']
        if group['locus'] == 'f68r2.31':
            assert words[1] == 'okoaiin'
        else:
            assert len(words) == 8 and words[0] == 'okeo'
    assert packet['confirmed_words'] == 0 and packet['independent_confirmation'] is False
    initial = packet['native_first_note_prefix']
    first_bytes = (BASE / initial['path']).read_bytes()[:initial['bytes']]
    assert hashlib.sha256(first_bytes).hexdigest() == initial['sha256']
    profiles = json.loads((BASE / 'F68R_ACTUAL_FORM_PROFILES_20260927.json').read_text())
    counts = {r['form']: {k: v['count'] for k, v in r['editions'].items()}
              for r in profiles['profiles']}
    assert counts == packet['exact_outside_counts']
    assert set(counts['okoaiin'].values()) == {1}
    if args.sources:
        for query in source['queries']:
            cmd = query['command']
            assert cmd[:2] == ['./vmanus-exp', 'query-tsv']
            assert cmd[3:9] == ['--selector', 'locus', '--allow', 'f68r2.6', '--allow', 'f68r2.31']
            relative = Path(cmd[2])
            assert not relative.is_absolute() and '..' not in relative.parts
            assert digest(ROOT / relative) == query['source_sha256']
            result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
            assert list(csv.DictReader(io.StringIO(result.stdout), delimiter='\t')) == query['rows']
            assert result.stderr.strip() == query['guard_stderr']
        for receipt in packet['local_images']:
            assert digest(ROOT / receipt['path']) == receipt['sha256']
    print(json.dumps({'status': 'PASS_TWO_LOCUS_REPLAY_AND_RECEIPTS',
                      'reader_locus_rows': 6, 'raw_groups': 58,
                      'source_replay': args.sources,
                      'limit': 'No validation of paleography, reading origin, body identity or meaning.'}, indent=2))


if __name__ == '__main__':
    main()
