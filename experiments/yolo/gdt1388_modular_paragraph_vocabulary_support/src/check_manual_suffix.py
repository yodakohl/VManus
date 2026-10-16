"""Check two preregistered posthoc necessary suffixes, without a decoder rerun."""
from pathlib import Path
import hashlib
import json

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]


def main():
    plan = json.loads((E / 'artifacts/MANUAL_SUFFIX_PLAN.json').read_text())
    source = ROOT / plan['source']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == plan['sha256']
    words = set(source.read_text().split())
    assert all(w and all('a' <= c <= 'z' for c in w) for w in words)
    counts = {}
    for reader, suffix in plan['suffixes'].items():
        matches = sorted(w for w in words if w.endswith(suffix))
        counts[reader] = {'suffix': suffix, 'matching_types': len(matches), 'first_ten_witnesses': matches[:10],
                          'consequence': 'ALL_LOCAL_LATIN_ALIGNMENTS_EXCLUDED' if not matches else 'REMAINS_UNKNOWN'}
    result = {'status': 'EXACT_FIXED_SUFFIX_CENSUS', 'vocabulary_size': len(words), 'cases': counts,
              'source_sha256': plan['sha256'],
              'plan_sha256': hashlib.sha256((E / 'artifacts/MANUAL_SUFFIX_PLAN.json').read_bytes()).hexdigest(),
              'program_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'limits': plan['decision']}
    (E / 'artifacts/MANUAL_SUFFIX_RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
