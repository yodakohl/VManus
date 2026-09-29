"""Same-author separate accounting checks, not vision or meaning validation."""
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]


def validate():
    lock = json.loads((BASE / 'src/PREREG_LOCK.json').read_text())
    for path, digest in lock['files'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
    source = json.loads((BASE / 'src/SOURCE.json').read_text())
    rows = json.loads((BASE / 'src/OBSERVED.json').read_text())
    result = json.loads((BASE / 'artifacts/RESULT.json').read_text())
    assert source['canvas'] == '1006123' and source['selector'] == 'f25v'
    assert source['source_url'].endswith('/1006123/full/3000,/0/default.jpg')
    assert [r['feature'] for r in rows] == [
        'LEAF_CONTINUITY', 'SEPARATE_SHAFT', 'TETHER', 'DISTINCT_BODY', 'SECOND_ACTOR']
    assert all(r['judgment'] is None and r['status'] == 'NOT_OBSERVED_MISSING_INPUT'
               for r in rows)
    assert result['decision'] == 'MISSING_REGISTERED_HIGHRES_INPUT'
    assert result['observations'] == rows and result['planned_observations'] == 5
    for key in ['executed_visual_observations', 'negative_visual_observations',
                'confirmed_words', 'fixed_semantic_tests']:
        assert result[key] == 0
    assert not result['new_target_pixels_opened']
    out = {'status': 'PASS', 'scope': 'missing-input accounting and preregistration integrity only',
           'visual_validation': False, 'meaning_validation': False}
    (BASE / 'artifacts/VALIDATION.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out))


if __name__ == '__main__':
    validate()
