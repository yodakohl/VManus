#!/usr/bin/env python3
"""Check packet identity and ordered group coverage; no semantic execution."""
import csv
import hashlib
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]


def main():
    receipt = json.loads((BASE / 'UNTIL_S_TYPED_RECEIPTS.json').read_text())
    checks = []
    for row in receipt['authored_outputs'] + receipt['frozen_inputs'] + receipt['predecessor_reports']:
        path = ROOT / row['path']
        checks.append({'file': row['path'], 'pass': path.is_file() and
                       hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']})
    # This owned125-position packet contains only already admitted f85r2 data.
    with (BASE / 'until_s_draft/ASSIGNED_OCCURRENCES.tsv').open() as stream:
        rows = list(csv.DictReader(stream, delimiter='\t'))
    expected = sorted((int(row['locus'].split('.')[-1]), int(row['group_index']), row['surface_exact'])
                      for row in rows if row['edition'] == 'ZL3b' and
                      12 <= int(row['locus'].split('.')[-1]) <= 17)
    grammar = (BASE / 'UNTIL_S_TYPED_GRAMMAR.md').read_text()
    actual = [(int(a), int(c), word) for a, c, word in
              re.findall(r'^\| `\.(\d+) G(\d+) (.+?)` \|', grammar, re.M)]
    checks.append({'check': 'ordered26 ZL table equals original assigned inventory',
                   'pass': actual == expected and len(actual) == 26})
    identities = []
    for name in ('UNTIL_S_TYPED_CLARIFICATIONS.md', 'UNTIL_S_TYPED_ROOT_REVIEW.md'):
        path = BASE / name
        identities.append({'file': path.relative_to(ROOT).as_posix(),
                           'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                           'kind': 'new root-review artifact identity, not scientific check'})
    result = {'status': 'PASS' if all(row['pass'] for row in checks) else 'FAIL',
              'scope': 'hash identity and complete ordered26-group table only; not a semantic executor, causal validation or interpretation confirmation',
              'checks': checks, 'review_artifact_identities': identities,
              'new_target_data': 0, 'confirmed_meanings': 0}
    (BASE / 'UNTIL_S_TYPED_INTEGRITY_RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'checks': len(checks), 'groups': len(actual)}))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
