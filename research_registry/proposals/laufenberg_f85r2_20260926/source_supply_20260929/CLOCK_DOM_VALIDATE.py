#!/usr/bin/env python3
"""Recheck descriptive counts, full rare-hit lists and frozen input identity."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from tools.word_profiles import ensure_cache, receipt


def main():
    result = json.loads((HERE / 'CLOCK_DOM_RESULT.json').read_text())
    for name, key in (
        ('CLOCK_DOM_DECISION.md', 'design_sha256'),
        ('CLOCK_DOM_PROFILES.json', 'profiles_sha256'),
        ('S_DOM_PREFLIGHT.json', 'fixed_inventory_preflight_sha256'),
    ):
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == result[key], name
    profiles = json.loads((HERE / 'CLOCK_DOM_PROFILES.json').read_text())
    conn = ensure_cache()
    assert profiles['source_receipt'] == receipt(conn)
    assert receipt(conn)['inputs']['selector_count'] == 179
    assert not any(x.startswith('f84') or x == 'f116v'
                   for x in receipt(conn)['inputs']['selectors'])
    expected = ('chckhy', 'chckhaiin', 'shckhy', 'shckhaiin', 'alolshey',
                'alolsheaiin', 'aiin', 'qokaiin', 'chaiin')
    assert tuple(result['counts']) == expected
    cells = 0
    for form, editions in result['counts'].items():
        for edition, observed in editions.items():
            count, selectors = conn.execute(
                'SELECT COUNT(*), COUNT(DISTINCT page) FROM groups '
                'WHERE ivtff_group_raw=? AND edition=?', (form, edition)
            ).fetchone()
            assert observed == {'groups': count, 'selectors': selectors}
            cells += 1
            if form in result['all_counterpart_occurrences']:
                all_ids = {x[0] for x in conn.execute(
                    'SELECT source_group_id FROM groups WHERE ivtff_group_raw=? '
                    'AND edition=?', (form, edition))}
                saved = result['all_counterpart_occurrences'][form][edition]
                assert {x['source_group_id'] for x in saved} == all_ids
                assert len(saved) == count
    conn.close()
    output = {'status': 'PASS_PROFILE_INTEGRITY_ONLY', 'checked_cells': cells,
              'complete_rare_form_lists': 9, 'meaning_tests': 0,
              'confirmed_meanings': 0, 'independent_meaning_confirmation': 0}
    (HERE / 'CLOCK_DOM_VALIDATION.json').write_text(
        json.dumps(output, indent=2) + '\n')
    print(json.dumps(output))


if __name__ == '__main__':
    main()
