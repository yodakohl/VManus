#!/usr/bin/env python3
"""Reproduce the registered projection/profile tables without changing artifacts.

Uses selector-first guarded access and the existing admitted-profile cache.
Does not author meanings, select examples or parse excluded source rows.
"""
import collections
import csv
import io
import json
from pathlib import Path
import subprocess

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
ART = BASE / 'artifacts'


def command(args):
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=True)


def main():
    receipt = json.loads((ART / 'ACCESS_RECEIPT.json').read_text())
    native = command(receipt['command'])
    assert native.stdout == (ART / 'NATIVE_GROUPS.tsv').read_text(), 'native projection differs'
    rows = list(csv.DictReader(io.StringIO(native.stdout), delimiter='\t'))
    local = collections.Counter(r['ivtff_group_raw'] for r in rows if r['edition'] == 'IT2a')
    forms = sorted(local)
    profiles = []
    for start in range(0, len(forms), 16):
        data = json.loads(command(['./vmanus-work', 'words', 'profile', *forms[start:start+16],
                                  '--json', '--limit', '2']).stdout)
        for card in data['profiles']:
            profiles.append({'form': card['form'], 'matching': card['matching'],
                             'editions': {e: {k: v for k, v in d.items() if k != 'examples'}
                                          for e, d in card['editions'].items()}, 'notes': card['notes']})
    assert profiles == json.loads((ART / 'WORD_PRIORS.json').read_text())['profiles'], 'profile values differ'
    table = io.StringIO()
    writer = csv.writer(table, delimiter='\t', lineterminator='\n')
    writer.writerow(['form','local_IT_count','admitted_IT_count','pages','rank','start','middle','end',
                     'single','repeated_lines','adjacent_pairs','max_per_line'])
    for card in profiles:
        data = card['editions']['IT2a']
        writer.writerow([card['form'], local[card['form']], data['count'], data['pages_with_form'], data['rank'],
                         *[data['positions'][k] for k in ['start','middle','end','single']],
                         *[data['repetition'][k] for k in ['repeated_lines','adjacent_pairs','max_per_line']]])
    assert table.getvalue() == (ART / 'WORD_PRIORS_COMPACT.tsv').read_text(), 'compact table differs'
    print(json.dumps({'status':'EXACT_INPUT_REPRODUCTION_ONLY','native_rows':len(rows),
                      'IT_forms':len(forms),'scientific_validation':False,
                      'cache_scope':'179 prior selectors; excludes later-admitted f101r'}))


if __name__ == '__main__':
    main()
