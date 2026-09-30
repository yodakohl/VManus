#!/usr/bin/env python3
"""Retain complete admitted prose from the selector-guarded cache."""
import csv
import gzip
import hashlib
import io
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT))
from tools.word_profiles import COLUMNS, ensure_cache, receipt

def main():
    lock = json.loads((BASE / 'PREREG_LOCK.json').read_text())
    for path, digest in lock['sha256'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
    conn = ensure_cache(ROOT)
    provenance = receipt(conn)
    rows = [dict(r) for r in conn.execute('SELECT * FROM groups WHERE kind=? ORDER BY edition,page,locus,source_group_index', ('P',))]
    conn.close()
    allowed = provenance['inputs']['selectors']
    assert all(r['page'] in allowed and not r['page'].startswith('f84') and r['page'] != 'f116v' for r in rows)
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=COLUMNS, delimiter='\t', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    blob = gzip.compress(buffer.getvalue().encode(), mtime=0)
    (BASE / 'artifacts/SOURCE.tsv.gz').write_bytes(blob)
    leaves = defaultdict(lambda: {'admitted_selectors': [], 'prose_selectors': [], 'groups': 0})
    for page in allowed:
        leaf = re.match(r'f\d+', page).group()
        leaves[leaf]['admitted_selectors'].append(page)
    for r in rows:
        leaf = re.match(r'f\d+', r['page']).group()
        leaves[leaf]['groups'] += 1
        if r['page'] not in leaves[leaf]['prose_selectors']:
            leaves[leaf]['prose_selectors'].append(r['page'])
    for leaf, item in leaves.items():
        item['partition'] = 'original_fitting_replay' if leaf in ('f9', 'f50') else 'additional_exposed_screen'
        item['standard_r_and_v_admitted'] = {leaf+'r', leaf+'v'} <= set(item['admitted_selectors'])
        item['native_foldout_completeness_asserted'] = False
        item['independent_meaning_confirmation'] = False
    data = {'cache_receipt': provenance, 'selection': 'all admitted rows of kind P; complete cache projection',
            'columns': list(COLUMNS), 'groups': len(rows), 'source_gzip_sha256': hashlib.sha256(blob).hexdigest(),
            'physical_leaves': dict(sorted(leaves.items())), 'reserves_opened': [],
            'paragraph_flags_retained': False, 'all_source_schema_columns_retained': False}
    (BASE / 'artifacts/SOURCE_RECEIPT.json').write_text(json.dumps(data, indent=2)+'\n')
    print(json.dumps({'groups': len(rows), 'admitted_selectors': len(allowed), 'prose_selectors': len({r['page'] for r in rows})}))

if __name__ == '__main__':
    main()
