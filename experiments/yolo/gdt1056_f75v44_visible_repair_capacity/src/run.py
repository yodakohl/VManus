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
EXPECTED = '654edf15a65d1a2bb0d7bb4995f8f6fba1625d5eed847c9b6969d1c44e385a23'
INDICATORS = ('erasure_or_abrasion', 'overwritten_or_retraced_stroke',
              'supralinear_insertion', 'local_ink_interruption', 'baseline_disturbance')


def main() -> int:
    manifest = json.loads((HERE / 'experiment.json').read_text())
    for item in manifest['inputs']:
        assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256']
    digest = hashlib.sha256(IMAGE.read_bytes()).hexdigest()
    assert digest == EXPECTED
    observation = json.loads((HERE / 'artifacts/OBSERVATION.json').read_text())
    assert observation['target_locus'] == 'f75v.44' and observation['target_group'] == 11
    assert observation['control_groups'] == [5, 6, 7, 8, 9, 10, 12]
    assert observation['source_image_sha256'] == digest
    values = [observation['indicators'][key] for key in INDICATORS]
    assert all(x in ('SEEN', 'NOT_SEEN_AT_RESOLUTION', 'UNCERTAIN') for x in values)
    if 'SEEN' in values:
        decision = 'VISIBLE_REPAIR'
    elif 'UNCERTAIN' in values:
        decision = 'UNDECIDABLE'
    else:
        decision = 'NO_VISIBLE_REPAIR_AT_AVAILABLE_RESOLUTION'
    result = {'experiment_id': 'GDT1056', 'decision': decision,
              'source_image_sha256': digest, 'observation': observation,
              'claim_ceiling': 'Visible repair capacity only; no authorial intention or word meaning.'}
    (HERE / 'artifacts/RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'experiment_id': 'GDT1056', 'decision': decision}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
