#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    source = json.loads((BASE / 'src/SOURCE.json').read_text())
    observations = json.loads((BASE / 'src/OBSERVATIONS.json').read_text())
    rows = observations['candidate_loci']
    if len(rows) != 12 or len({r['id'] for r in rows}) != 12:
        raise ValueError('complete twelve-locus checklist required')
    if sum(r['historical_role'] == 'star_field_center' for r in rows) != 4:
        raise ValueError('four center fields required')
    if sum(r['historical_role'] == 'radial_title_or_boundary' for r in rows) != 8:
        raise ValueError('eight radial items required')
    owner = bool(observations['unique_twelve_sector_owner_gate']) and all(r['trier_same_sector_owner'] for r in rows)
    phase = bool(observations['authorial_orientation_gate']) and any(c['authorial_named_bearing'] for c in observations['orientation_candidates'])
    result = {
        'experiment_id': 'GDT1085',
        'source_image_sha256': source['full_image_sha256'],
        'panel_image_sha256': source['panel_detail_sha256'],
        'observations_sha256': sha256(BASE / 'src/OBSERVATIONS.json'),
        'candidate_count': len(rows),
        'center_count': 4,
        'radial_count': 8,
        'trier_same_sector_owner_count': sum(bool(r['trier_same_sector_owner']) for r in rows),
        'twelve_sector_owner_gate': owner,
        'authorial_orientation_gate': phase,
        'decision': 'BOTH_GATES_VISIBLE' if owner and phase else 'NO_CURRENT_LEXICAL_CAPACITY',
        'claim_ceiling': 'visual capacity only; no text or translated name'
    }
    (BASE / 'artifacts/RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
