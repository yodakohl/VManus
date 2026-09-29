#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = next(p for p in BASE.parents if (p / 'AGENTS.md').is_file())

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    source = json.loads((BASE / 'src/SOURCE.json').read_text())
    obs = json.loads((BASE / 'src/OBSERVATIONS.json').read_text())
    result = json.loads((BASE / 'artifacts/RESULT.json').read_text())
    checks = {
        'frozen_method_hash': sha256(BASE / 'METHOD.md') == source['method_sha256_before_pixels'],
        'frozen_admission_hash': sha256(BASE / 'src/PAGE_ADMISSIONS.tsv') == source['admission_sha256_before_pixels'],
        'frozen_scope_hash': sha256(ROOT / 'docs/VOYNICH_DATA_SCOPE_20260929_F68V2_IMAGE.md') == source['scope_sha256_before_pixels'],
        'full_image_hash_if_cached': not (BASE / 'runtime/f68v_1006197.jpg').exists() or sha256(BASE / 'runtime/f68v_1006197.jpg') == source['full_image_sha256'],
        'panel_image_hash_if_cached': not (BASE / 'runtime/f68v2_panel.jpg').exists() or sha256(BASE / 'runtime/f68v2_panel.jpg') == source['panel_detail_sha256'],
        'observation_hash': sha256(BASE / 'src/OBSERVATIONS.json') == result['observations_sha256'],
        'locus_inventory': sorted(r['id'] for r in obs['candidate_loci']) == sorted([f'F{i}' for i in range(1,9)] + ['C_top','C_right','C_bottom','C_left']),
        'no_trier_owner': sum(bool(r['trier_same_sector_owner']) for r in obs['candidate_loci']) == result['trier_same_sector_owner_count'],
        'decision_logic': result['decision'] == ('BOTH_GATES_VISIBLE' if result['twelve_sector_owner_gate'] and result['authorial_orientation_gate'] else 'NO_CURRENT_LEXICAL_CAPACITY'),
        'no_sealed_access': all('f84' not in str(x).lower() for x in (source['canvas_id'], source['full_image_url'], source['panel_detail_url']))
    }
    output = {'status':'PASS' if all(checks.values()) else 'FAIL', 'checks': checks, 'meaning':'source/inventory/decision integrity; human visual judgment is not machine-validated'}
    (BASE / 'artifacts/VALIDATION.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output, indent=2))
    return 0 if output['status'] == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
