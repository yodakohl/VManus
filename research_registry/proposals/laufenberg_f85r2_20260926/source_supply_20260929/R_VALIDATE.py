#!/usr/bin/env python3
"""Documentary integrity only: no candidate meaning, parser or target test."""
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

packet = json.loads((BASE / 'R_COMPLETE_UNITS.json').read_text())
source = Path(packet['source'])
assert sha(source) == packet['sha256']
source_data = json.loads(source.read_text())
allowed = {f'f75v.{n}' for n in range(43, 50)}
accounting = json.loads((BASE / 'R_LOCAL_ACCOUNTING.json').read_text())['readers']
counts = {}
for unit in packet['units']:
    edition = unit['edition']
    original = next(e for e in source_data if e['edition'] == edition)
    selected = [line for line in original['lines'] if line['metadata']['locus'] in allowed]
    assert selected == unit['lines']
    assert original['group_columns'] == unit['group_columns']
    assert len(selected) == 7
    if edition != 'RF1b':
        assert selected[0]['metadata']['paragraph_start'] == '1'
        assert selected[-1]['metadata']['paragraph_end'] == '1'
    words = [g[2] for line in selected for g in line['groups']]
    counter = Counter(words)
    counts[edition] = len(words)
    assert accounting[edition]['total'] == len(words)
    assert accounting[edition]['total_types'] == len(counter)
    for form, count in accounting[edition]['literal_assigned'].items():
        assert counter[form] == count
    connectors = []
    for line in selected:
        groups = line['groups']
        for i, group in enumerate(groups):
            if group[2] in {'qokar', 'tol'}:
                connectors.append({
                    'locus': line['metadata']['locus'], 'index': group[1],
                    'literal': group[2],
                    'next_literal': groups[i+1][2] if i+1 < len(groups) else None,
                    'right_boundary': group[4],
                })
    assert connectors == accounting[edition]['connectors']
    line47 = next(line for line in selected if line['metadata']['locus'] == 'f75v.47')
    groups = line47['groups']
    i = next(i for i,g in enumerate(groups) if g[2] == 'shedy')
    assert groups[i-1][2] == 'ol'
    assert groups[i-1][4] == groups[i][3] == 'DEFINITE_SPACE'
    assert any(g[2] == 'olshedy' for g in groups)
assert counts == {'ZL3b': 75, 'IT2a': 77, 'RF1b': 73}

card = json.loads((BASE / 'R_01_PREDICATION_RESTRICTION.json').read_text())
assert card['design']['status'] == 'RAW_UNREVIEWED_NOT_SELECTED_NOT_TESTED'
profiles = json.loads((BASE / 'R_WORD_PROFILES.json').read_text())
assert profiles['source_receipt']['guard_stats'] == {
    'selected': 96184, 'skipped_forbidden': 2122, 'skipped_not_allowed': 17164,
}
assert profiles['source_receipt']['inputs']['selector_count'] == 179

primary_paths = [
    source,
    Path('experiments/yolo/gdt824_qolchedy_fixed_composition/WORKING_THEORY.md'),
    Path('experiments/yolo/gdt839_boundary_conservation_screen/REPORT.md'),
    Path('experiments/yolo/gdt850_qolchedy_join_split_context_inventory/REPORT.md'),
    Path('experiments/yolo/gdt851_primitive_tandem_raw_group_discovery/REPORT.md'),
    Path('experiments/yolo/gdt852_f75v_native_join_split_spacing/REPORT.md'),
    Path('experiments/yolo/gdt853_spacing_context_transfer/REPORT.md'),
    Path('experiments/yolo/gdt1056_f75v44_visible_repair_capacity/REPORT.md'),
    Path('experiments/yolo/gdt1046_f85_faculty_nominalizer_consequences/REPORT.md'),
    Path('research_registry/work_batches/ten_hours_20260915/RAW_SUPPLY_PROVENANCE_CORRECTIONS.md'),
]
outputs = sorted(p for p in BASE.glob('R_*') if p.is_file() and p.name != 'R_INTEGRITY_RECEIPT.json')
for path in outputs:
    text = path.read_text()
    forbidden_prefixes = [chr(47) + name + chr(47) for name in ('home', 'tmp', 'root')]
    assert not any(prefix in text for prefix in forbidden_prefixes)
receipt = {
    'completed_utc': datetime.now(timezone.utc).isoformat(),
    'start_utc': '2026-09-29T11:14:58+00:00',
    'bound_minutes': 40,
    'result': 'PASS_DOCUMENTARY_INTEGRITY_ONLY',
    'meaning': 'Exact source projection, flags, literal counts and hashes; not a semantic validation or a new target test.',
    'idea_added': 'IDEA000771',
    'new_idea_count': 1,
    'complete_line_records': 21,
    'source_groups_by_reader': counts,
    'primary_inputs': {str(p): sha(p) for p in primary_paths},
    'outputs': {str(p): sha(p) for p in outputs},
}
(BASE / 'R_INTEGRITY_RECEIPT.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'result': receipt['result'], 'counts': counts, 'idea': receipt['idea_added'], 'completed_utc': receipt['completed_utc']}, ensure_ascii=False))
