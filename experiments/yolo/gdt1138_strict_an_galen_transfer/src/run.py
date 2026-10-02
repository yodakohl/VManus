#!/usr/bin/env python3
"""Read-only prospective source check; no candidate execution before release."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def main():
    source = json.loads((BASE / 'src/SOURCE.json').read_text())
    baseline = json.loads((BASE / 'src/BASELINE34.json').read_text())
    counts = {'ZL3b': sum(len(x['words']) for x in source['whole_record']['lines']),
              'IT2a': sum(len(x['words']) for x in source['alternative_reader_records']['IT2a']['lines'])}
    print(json.dumps({'status': 'PROSPECTIVE_SOURCE_ONLY_NOT_SCIENTIFIC_EXECUTION',
                      'groups': counts, 'literal_baseline_types': len(baseline['entries']),
                      'author_release': 'ROOT_REQUIRED', 'confirmed_words': 0}, indent=2))


if __name__ == '__main__':
    main()
