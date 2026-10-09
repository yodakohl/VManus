"""Validate a post-result corollary; only old report examples, no native cache."""
import hashlib
import json
from pathlib import Path

BASE = Path('research_registry/proposals/production_origin_supply_20261003')
NOTE = BASE / 'CHART977_REPEAT_SOURCE_CONSTRAINT_20261008.json'
note = json.loads(NOTE.read_text())
source_report = Path(note['inputs'][1]).read_text()
rows = []
for form, spec in note['manual_predictions'].items():
    assert form in source_report and spec['locus'] in source_report
    units = spec['units']
    assert ''.join(units) == form
    for phase in (0, 1):
        pairs = []
        for start in range(phase, len(units) - 1, 2):
            allowed = []
            for value in range(24):
                a, b = divmod(value, 4)
                if start > 0 and ((a == 0) != (units[start] == units[start - 1])):
                    continue
                if (b == 0) != (units[start + 1] == units[start]):
                    continue
                allowed.append(value)
            pairs.append({'start': start, 'units': units[start:start + 2], 'allowed_source_indices': allowed})
        forced = [p['start'] for p in pairs if p['allowed_source_indices'] == [0]]
        assert forced == spec['zero_pair_starts_0based'][str(phase)]
        assert all(start + 2 < len(units) for start in forced)
        rows.append({'form': form, 'phase': phase, 'complete_pairs': pairs,
                     'forced_zero_starts': forced, 'later_output_exists': True})
# Independent alignment count on an all-equal run, excluding its unknown first rank.
controls = []
for run_length in range(2, 101):
    counts = []
    for first_pair_start in (0, 1):
        pairs = [(i, i + 1) for i in range(first_pair_start, run_length - 1, 2)]
        counts.append(sum(i >= 1 for i, j in pairs))
    assert min(counts) == (run_length - 2) // 2
    assert max(counts) == (run_length - 1) // 2
    controls.append({'run_length': run_length, 'counts': counts})
# A three-label repeat has only two known zero ranks and need not contain a whole00 pair.
assert controls[1]['counts'] == [0, 1]
# Four equal labels force exactly one known complete00 under both phases.
assert controls[2]['counts'] == [1, 1]
result = {'status': 'PASS', 'scope': 'Necessary source-index sets only; no actual chart feasibility, new native counts or meanings',
          'manual_cases': rows, 'run_alignment_controls': controls,
          'input_hashes': {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in note['inputs'] + [str(NOTE), __file__]}}
out = BASE / 'CHART977_REPEAT_SOURCE_RESULT_20261008.json'
out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': result['status'], 'manual_phase_cases': len(rows), 'run_lengths_checked': len(controls), 'result': str(out)}))
