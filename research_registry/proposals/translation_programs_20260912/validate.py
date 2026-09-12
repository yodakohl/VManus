#!/usr/bin/env python3
"""Verify the thirty-program handoff; never read manuscript payload or registry JSONL."""
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent

def main():
    document = ROOT / 'docs/TRANSLATION_PROGRAMS_30.md'
    text = document.read_text()
    bundle = json.loads((HERE / 'PROGRAMS.json').read_text())
    programs = bundle['programs']
    screen = json.loads((HERE / 'PREDECESSOR_SCREEN.json').read_text())['records']
    with (HERE / 'INDEX.tsv').open() as f:
        index = list(csv.DictReader(f, delimiter='\t'))
    expected = [f'P{i:02d}' for i in range(1, 31)]
    assert [p['plan_id'] for p in programs] == expected
    assert [p['plan_id'] for p in index] == expected
    assert [p['plan_id'] for p in screen] == expected
    assert len({p['title'] for p in programs}) == 30
    assert len({p['idea_id'] for p in index}) == 30
    assert re.findall(r'<a id="(p\d\d)"></a>', text) == [p.lower() for p in expected]
    source_paths = set()
    for program, item, nav in zip(programs, index, screen):
        pid = program['plan_id']
        proposal_path = HERE / (pid + '.json')
        proposal = json.loads(proposal_path.read_text())
        assert proposal['design']['execution'] == program
        assert len(program['steps']) == 6 and all(program['steps'])
        for field in ('starting_scope', 'starting_observation', 'provisional_assumptions',
                      'new_contribution', 'working_consequence', 'revision_or_stop',
                      'deliverable', 'predecessors', 'held_page_policy', 'human_policy'):
            assert program[field], (pid, field)
        assert program['result_status'] == 'UNTESTED_PROPOSAL'
        assert program['source_entrypoints']
        assert all(k in bundle['work_packages'] for k in program['work_packages'])
        for entry in program['source_entrypoints']:
            assert not Path(entry['path']).is_absolute()
            assert (ROOT / entry['path']).is_file(), entry['path']
            source_paths.add(entry['path'])
        assert item['title'] == program['title']
        assert item['proposal'] == str(proposal_path.relative_to(ROOT))
        assert item['idea_id'] in text
        assert nav['sha256'] == hashlib.sha256(proposal_path.read_bytes()).hexdigest()
        assert not nav['scientific_novelty_assessed']
    assert sum(p['priority'] == 'REVIEW_PRIORITY' for p in programs) == 5
    assert 'eine andere Person' not in text
    assert 'Keine Kontakte' in programs[0]['human_policy']
    assert 'f84 und f84r' in text
    # Documentation links only; do not open their payloads.
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if target.startswith('#'):
            assert target[1:] in re.findall(r'<a id="([^"]+)"></a>', text)
        else:
            assert not Path(target).is_absolute()
            path = document.parent / target.split('#')[0]
            assert path.is_file() or path.name == 'VALIDATION.json', target
    result = {
        'status': 'PASS_DOCUMENTATION_CONSISTENCY_ONLY',
        'program_count': 30, 'steps_per_program': 6, 'shortlist_count': 5,
        'registry_ids': [p['idea_id'] for p in index],
        'resolved_source_files': len(source_paths),
        'proposal_bundle_and_preadd_screen_hash_parity': True,
        'source_payloads_read_by_validator': False,
        'manuscript_experiments_run': 0,
        'scientific_novelty_or_meaning_validated': False,
        'held_pages_opened': False,
        'command': 'python research_registry/proposals/translation_programs_20260912/validate.py'
    }
    (HERE / 'VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
