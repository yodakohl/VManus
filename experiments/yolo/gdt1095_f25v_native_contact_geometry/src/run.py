"""Replay the acquisition stop; no visual negatives from missing pixels."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def run():
    source = json.loads((BASE / 'src/SOURCE.json').read_text())
    rows = json.loads((BASE / 'src/OBSERVED.json').read_text())
    assert source['status'] == 'MISSING_REGISTERED_HIGHRES_INPUT'
    assert source['image_bytes_received'] == source['native_views'] == 0
    assert len(rows) == 5 and all(r['judgment'] is None for r in rows)
    result = {
        'experiment_id': 'GDT1095', 'decision': source['status'],
        'planned_observations': 5, 'executed_visual_observations': 0,
        'negative_visual_observations': 0, 'observations': rows,
        'new_target_pixels_opened': False, 'confirmed_words': 0,
        'fixed_semantic_tests': 0,
        'scope': 'f25v detail unavailable; f84/f84r and reserves closed',
    }
    (BASE / 'artifacts/RESULT.json').write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    run()
