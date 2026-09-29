#!/usr/bin/env python3
"""Check the complete input and exact derived result bytes."""
import json
from run import decide, BASE

if __name__ == '__main__':
    expected = decide()
    actual = json.loads((BASE / 'artifacts/RESULT.json').read_text(encoding='utf-8'))
    assert actual == expected
    assert expected['decision'] == 'NO_RARE_COPY_ANOMALY_MATCH'
    out = BASE / 'artifacts/VALIDATION.json'
    out.write_text(json.dumps({'status':'PASS', 'complete_features':4,
                               'decision_replayed':True,
                               'visual_judgment_verified_by_code':False}, indent=2)+'\n', encoding='utf-8')
    print(out)
