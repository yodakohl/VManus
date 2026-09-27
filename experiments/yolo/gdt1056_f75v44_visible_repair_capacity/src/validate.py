#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / 'AGENTS.md').is_file() and (candidate / '.git').exists():
            return candidate
    raise RuntimeError('VManus repository root not found')


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parents[1]
IMAGE = ROOT / 'experiments/yolo/gdt852_f75v_native_join_split_spacing/runtime/f75v.jpg'


def main() -> int:
    source = json.loads((ROOT / 'experiments/yolo/gdt852_f75v_native_join_split_spacing/artifacts/SOURCES.json').read_text())
    digest = hashlib.sha256(IMAGE.read_bytes()).hexdigest()
    assert digest == source['sha256'] == '654edf15a65d1a2bb0d7bb4995f8f6fba1625d5eed847c9b6969d1c44e385a23'
    observation = json.loads((HERE / 'artifacts/OBSERVATION.json').read_text())
    result = json.loads((HERE / 'artifacts/RESULT.json').read_text())
    lock = json.loads((HERE / 'src/PREREG_LOCK.json').read_text())
    for item, filename in [('method_sha256', 'METHOD.md'), ('preregistration_sha256', 'PREREGISTRATION.md')]:
        assert lock[item] == hashlib.sha256((HERE / filename).read_bytes()).hexdigest()
    assert lock['source_image_sha256'] == digest
    assert result['observation'] == observation
    assert observation['source_page'] == 'f75v' and observation['target_locus'] == 'f75v.44'
    assert observation['target_group'] == 11 and observation['control_groups'] == [5, 6, 7, 8, 9, 10, 12]
    required = ('erasure_or_abrasion', 'overwritten_or_retraced_stroke', 'supralinear_insertion',
                'local_ink_interruption', 'baseline_disturbance')
    values = [observation['indicators'][key] for key in required]
    assert all(v in ('SEEN', 'NOT_SEEN_AT_RESOLUTION', 'UNCERTAIN') for v in values)
    expected = ('VISIBLE_REPAIR' if 'SEEN' in values else
                'UNDECIDABLE' if 'UNCERTAIN' in values else
                'NO_VISIBLE_REPAIR_AT_AVAILABLE_RESOLUTION')
    assert result['decision'] == expected and result['source_image_sha256'] == digest
    validation = {'experiment_id': 'GDT1056', 'status': 'PASS', 'decision': expected,
                  'scope': 'image identity, preregistration lock, observation schema and decision mapping only; no paleographic or semantic validation'}
    (HERE / 'artifacts/VALIDATION.json').write_text(json.dumps(validation, indent=2, sort_keys=True) + '\n')
    print(json.dumps(validation))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
