#!/usr/bin/env python3
"""Check deterministic replay; visual observations remain explicitly manual."""
import json
from pathlib import Path
from run import result

BASE = Path(__file__).resolve().parents[1]


def main():
    saved = json.loads((BASE / 'artifacts' / 'RESULT.json').read_text(encoding='utf-8'))
    computed = result()
    passed = saved == computed and saved['decision'] == 'NO_THREE_PART_NAMED_SOURCE_OWNER'
    validation = {'experiment_id': 'GDT1093', 'status': 'PASS' if passed else 'FAIL',
                  'checks': ['309_unique_official_canvas_receipts', 'fixed_shortlist',
                             'three_feature_owner_rule_replay', 'saved_result_equals_replay'],
                  'limits': 'Does not independently validate visual coding.'}
    (BASE / 'artifacts' / 'VALIDATION.json').write_text(json.dumps(validation, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(validation, sort_keys=True))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
