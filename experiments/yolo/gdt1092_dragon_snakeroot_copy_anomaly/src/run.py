#!/usr/bin/env python3
"""Replay the registered four-feature image decision; no image classifier."""
import csv
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def decide():
    with (BASE / 'src/OBSERVED.tsv').open(encoding='utf-8', newline='') as fh:
        rows = list(csv.DictReader(fh, delimiter='\t'))
    assert [r['feature_id'] for r in rows] == ['F1', 'F2', 'F3', 'F4']
    assert all(r['match'] in {'YES', 'NO', 'UNCLEAR'} and r['observation'] for r in rows)
    with (BASE / 'src/SOURCE.tsv').open(encoding='utf-8', newline='') as fh:
        sources = list(csv.DictReader(fh, delimiter='\t'))
    assert [(r['role'], r['folio'], r['canvas_id']) for r in sources] == [
        ('historical_source', 'Sloane 4016 f38r', '84'),
        ('voynich_target', 'MS 408 f25v', '1006123')]
    strict = all(r['match'] == 'YES' for r in rows)
    return {'experiment_id': 'GDT1092', 'criterion': 'all four fixed source features YES',
            'feature_matches': {r['feature_id']: r['match'] for r in rows},
            'strict_candidate': strict,
            'decision': 'STRICT_SOURCE_OWNER_CANDIDATE' if strict else 'NO_RARE_COPY_ANOMALY_MATCH',
            'claim_ceiling': 'visual source-owner capacity only; no Voynich word or species'}


if __name__ == '__main__':
    out = BASE / 'artifacts/RESULT.json'
    out.write_text(json.dumps(decide(), indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(out)
