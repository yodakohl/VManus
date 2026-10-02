#!/usr/bin/env python3
"""Read-only frozen-account replay; optional source-only mechanical summary."""
import argparse
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-only', action='store_true')
    args = parser.parse_args()
    if not args.source_only:
        import AUTHOR_FULL
        print(json.dumps(AUTHOR_FULL.account(), ensure_ascii=False, indent=2))
        return
    source = json.loads((BASE / 'src/SOURCE.json').read_text())
    baseline = json.loads((BASE / 'src/BASELINE34.json').read_text())
    counts = {'ZL3b': sum(len(x['words']) for x in source['whole_record']['lines']),
              'IT2a': sum(len(x['words']) for x in source['alternative_reader_records']['IT2a']['lines'])}
    print(json.dumps({'status': 'SOURCE_SUMMARY_NOT_SCIENTIFIC_OUTCOME',
                      'groups': counts, 'literal_baseline_types': len(baseline['entries']),
                      'author_release': 'PUBLIC_ROOT_RELEASE_RECORDED', 'confirmed_words': 0}, indent=2))


if __name__ == '__main__':
    main()
