"""Selector-first intake with a source/prediction lock before target access."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess

E = Path(__file__).resolve().parents[1]
R = E.parents[2]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('phase', choices=['discovery', 'additional', 'taurus'])
    a = ap.parse_args()
    lock = json.loads((E / 'PREREG_LOCK.json').read_text())
    for rel, h in lock['files'].items():
        assert sha(E / rel) == h, 'preregistration changed: ' + rel
    for rel, h in lock['source_files'].items():
        assert sha(R / rel) == h, 'source changed: ' + rel
    if a.phase != 'discovery':
        frozen = json.loads((E / 'DISCOVERY_FREEZE.json').read_text())
        for rel, h in frozen['files'].items():
            assert sha(E / rel) == h, 'discovery freeze changed: ' + rel
    s = json.loads((E / 'src/SPEC.json').read_text())
    pages = s['intake_phases'][a.phase]
    columns = ['source_group_id', 'edition', 'locus', 'page', 'kind',
               'source_group_index', 'source_group_count', 'left_separator',
               'right_separator', 'ivtff_group_raw']
    cmd = ['./vmanus-exp', 'query-tsv', s['source'], '--selector', 'page']
    for page in pages:
        assert page in s['page_sign'] and not page.startswith('f84')
        cmd += ['--allow', page]
    cmd += ['--columns', ','.join(columns), '--forbid-prefix', 'f84',
            '--forbid-prefix', 'f84r']
    proc = subprocess.run(cmd, cwd=R, capture_output=True, text=True, check=True)
    stats = [json.loads(x[12:]) for x in proc.stderr.splitlines()
             if x.startswith('GUARD_STATS ')]
    assert len(stats) == 1 and stats[0]['selected'] > 0, 'empty guarded input'
    # Only admitted selectors are materialized; non-label groups are not retained.
    rows = [r for r in csv.DictReader(io.StringIO(proc.stdout), delimiter='\t')
            if r['kind'] == s['kind'] and r['edition'] in s['editions']]
    counts = {}
    for edition in s['editions']:
        counts[edition] = {}
        for page in pages:
            n = len({r['locus'] for r in rows
                     if r['edition'] == edition and r['page'] == page})
            counts[edition][page] = n
            assert n == s['expected_labels'][page], ('intake locus count', edition, page, n)
    payload = {'phase': a.phase, 'rows': rows, 'label_locus_counts': counts}
    text = json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + '\n'
    out = E / 'artifacts' / ('INPUT_' + a.phase.upper() + '.json')
    if out.exists():
        assert out.read_text() == text, 'frozen projection changed'
    else:
        out.write_text(text)
    receipt = {'phase': a.phase, 'command': cmd, 'guard': stats[0],
               'selected_label_groups': len(rows), 'label_locus_counts': counts,
               'projection_sha256': sha(out), 'prior_project_exposure': True,
               'new_image_access': False, 'reserves_accessed': False}
    (E / 'src' / ('INTAKE_' + a.phase.upper() + '.json')).write_text(
        json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k: v for k, v in receipt.items() if k != 'command'}))


if __name__ == '__main__':
    main()
