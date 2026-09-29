#!/usr/bin/env python3
"""Replay only the five admitted loci and validate complete accounting."""
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def main():
    result = json.loads((HERE / 'CLOCK_DOM_EXTENSION_RESULT.json').read_text())
    source = ROOT / 'experiments/yolo/gdt1030_clock_whole_reference_consequences/src/SOURCE.json'
    assert hashlib.sha256(source.read_bytes()).hexdigest() == result['source_sha256']
    lex = {r['form']: r for r in json.loads(source.read_text())['lexicon']}
    projection = HERE / 'CLOCK_DOM_F108V.tsv'
    assert hashlib.sha256(projection.read_bytes()).hexdigest() == result['projection_sha256']
    saved = list(csv.DictReader(projection.open(), delimiter='\t'))
    columns = list(saved[0])
    command = [str(ROOT / 'vmanus-exp'), 'query-tsv',
               'experiments/semantic_assumptions/results/source_separator_transcription.tsv',
               '--selector', 'locus']
    for line in range(7, 12):
        command += ['--allow', f'f108v.{line}']
    command += ['--columns', ','.join(columns), '--forbid-prefix', 'f84',
                '--forbid-prefix', 'f84r']
    replay = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    assert list(csv.DictReader(io.StringIO(replay.stdout), delimiter='\t')) == saved
    assert len(saved) == 164
    for edition, account in result['editions'].items():
        rows = [r for r in saved if r['edition'] == edition]
        assert account['groups'] == len(rows)
        assert account['types'] == len({r['ivtff_group_raw'] for r in rows})
        for raw, annotated in zip(rows, account['rows'], strict=True):
            assert all(annotated[k] == v for k, v in raw.items())
            assert annotated['fixed_value'] == lex.get(raw['ivtff_group_raw'])
            assert bool(annotated['derived_alternatives']) == (raw['ivtff_group_raw'] == 'shckhaiin')
        for line in range(7, 12):
            group = [r for r in rows if r['locus'] == f'f108v.{line}']
            assert [int(r['source_group_index']) for r in group] == list(range(1, len(group) + 1))
            assert all(int(r['source_group_count']) == len(group) for r in group)
        if edition in ('ZL3b', 'IT2a'):
            assert rows[0]['paragraph_start'] == '1'
            assert rows[-1]['paragraph_end'] == '1'
        else:
            assert {r['paragraph_start'] for r in rows} == {'0'}
            assert {r['paragraph_end'] for r in rows} == {'0'}
        unknown = [r for r in account['rows'] if r['status'] == 'UNASSIGNED']
        assert account['unassigned_positions'] == len(unknown)
        assert account['unassigned_types'] == len({r['ivtff_group_raw'] for r in unknown})
    output = {'status': 'PASS_LITERAL_ACCOUNTING_ONLY', 'raw_groups': 164,
              'whole_paragraph_readings': ['ZL3b', 'IT2a'], 'comparison_window': 'RF1b',
              'new_meaning_test': False, 'new_confirmed_word': False}
    (HERE / 'CLOCK_DOM_EXTENSION_VALIDATION.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output))


if __name__ == '__main__':
    main()
