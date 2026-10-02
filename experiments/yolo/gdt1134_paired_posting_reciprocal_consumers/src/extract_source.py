#!/usr/bin/env python3
"""Project the three owned loci and attach unchanged formal units."""
from collections import defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / 'experiments/yolo/gdt605_multisymbol_unit_alphabet/src'))
from separator_crossing import collapse, apply_bpe

SOURCE = 'research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929/L_F105V_COMPLETE_PARAGRAPH.tsv'
MERGES = 'experiments/yolo/gdt605_multisymbol_unit_alphabet/artifacts/gdt605_bpe_merges.tsv'
COLUMNS = 'source_group_id,edition,page,locus,source_group_index,source_group_count,paragraph_start,paragraph_end,left_separator,right_separator,ivtff_group_raw'
LOCI = ['f105v.5', 'f105v.6', 'f105v.7']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    registration = json.loads((BASE / 'src/REGISTRATION.json').read_text())
    for path, digest in registration['input_pins'].items():
        assert sha(ROOT / path) == digest, path
    command = ['./vmanus-exp', 'query-tsv', SOURCE, '--selector', 'locus']
    for locus in LOCI:
        command.extend(['--allow', locus])
    command.extend(['--columns', COLUMNS])
    query = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    rows = list(csv.DictReader(io.StringIO(query.stdout), delimiter='\t'))
    assert len(rows) == 90
    with (ROOT / MERGES).open(newline='') as handle:
        merge_rows = list(csv.DictReader(handle, delimiter='\t'))
    assert [int(r['rank']) for r in merge_rows] == list(range(1, 65))
    merges = [(r['left'], r['right'], r['merged'], int(r['train_occurrences'])) for r in merge_rows]
    byline = defaultdict(list)
    for row in rows:
        assert row['page'] == 'f105v' and row['locus'] in LOCI
        byline[row['edition'], row['locus']].append(row)
    lines = []
    for (reader, locus), line_rows in sorted(byline.items()):
        assert [int(r['source_group_index']) for r in line_rows] == list(range(1, len(line_rows) + 1))
        assert all(int(r['source_group_count']) == len(line_rows) for r in line_rows)
        chunks, pending = [], []
        for row in line_rows:
            pending.append(row)
            if row['right_separator'] == 'UNCERTAIN_SMALL_SPACE':
                continue
            pure = all(re.fullmatch('[a-z]+', r['ivtff_group_raw']) for r in pending)
            raw = ''.join(r['ivtff_group_raw'] for r in pending)
            units = list(apply_bpe(collapse(raw), merges)) if pure else None
            chunks.append({'source_ids': [r['source_group_id'] for r in pending],
                           'raw_groups': [r['ivtff_group_raw'] for r in pending],
                           'fixed_units': units, 'native_rows': pending})
            pending = []
        assert not pending
        lines.append({'edition': reader, 'locus': locus, 'chunks': chunks,
                      'native_group_count': len(line_rows)})
    result = {'experiment': 'GDT1134', 'source_path': SOURCE,
              'source_sha256': sha(ROOT / SOURCE), 'command': command,
              'guard': query.stderr.strip(), 'native_columns': COLUMNS.split(','),
              'native_rows': rows, 'lines': lines,
              'fixed_merge_path': MERGES, 'fixed_merge_sha256': sha(ROOT / MERGES),
              'prior_project_exposure': True, 'new_admission': False,
              'paragraph_boundary': 'ZL/IT complete paragraph; RF complete spatial counterpart',
              'seals': ['f84', 'f84r'], 'reserves_opened': False}
    (BASE / 'src/SOURCE.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'native_rows': len(rows), 'lines': len(lines),
                      'hardchunks': sum(len(x['chunks']) for x in lines),
                      'source_sha256': sha(BASE / 'src/SOURCE.json')}))


if __name__ == '__main__':
    main()
