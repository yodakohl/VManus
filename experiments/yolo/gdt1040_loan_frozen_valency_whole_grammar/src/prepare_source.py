#!/usr/bin/env python3
"""Extract the fixed exposed paragraph only; no grammar algorithm."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
PATHS = {
    'original': 'research_registry/proposals/raw_f83r_title_custody_loan.json',
    'offer': 'research_registry/proposals/raw_f83r_loan_frozen7_compact_construction_offer_20260922.json',
    'paragraphs': 'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json',
    'W41': 'research_registry/proposals/translation_programs_20260912/work/W41/REPORT.md',
    'GDT979': 'experiments/yolo/gdt979_partial_action_compound_accounts/REPORT.md'}


def main():
    spec = json.loads((EXP / 'src/SPEC.json').read_text())
    offer = json.loads((ROOT / PATHS['offer']).read_text())
    old = json.loads((ROOT / PATHS['original']).read_text())
    assert offer['design']['fixed_seven_full_values'] == old['design']['shared_whole_word_hypotheses']
    bindings = {name: {'path': path, 'sha256': hashlib.sha256((ROOT / path).read_bytes()).hexdigest()}
                for name, path in PATHS.items()}
    groups = []
    for row in old['design']['all_group_alignment']:
        groups.append({'locus': row['locus'], 'line_index': row['group'], 'word': row['raw'],
                       'source_id': f"PROJECTED|{row['locus']}|G{row['group']:03d}",
                       'original_alignment_status': row['status']})
    models = {'PROJECTED_ZL': {'scope': 'old RAW372 report projection', 'groups': groups}}
    cache = json.loads((ROOT / PATHS['paragraphs']).read_text())
    for reader in ['ZL3b', 'IT2a']:
        units = [unit for unit in cache[reader] if unit['id'] == spec['selected_unit']]
        assert len(units) == 1
        unit = units[0]
        assert unit['page'] == 'f83r'
        gs = []
        for line in unit['lines']:
            assert len(line['words']) == len(line['source_ids'])
            for i, (word, sid) in enumerate(zip(line['words'], line['source_ids']), 1):
                gs.append({'locus': line['locus'], 'line_index': i, 'word': word, 'source_id': sid})
        models['DIPLOMATIC_' + reader] = {'scope': 'entire native flagged paragraph', 'unit': unit, 'groups': gs}
    assert not [unit for unit in cache['RF1b'] if unit['id'] == spec['selected_unit']]
    result = {'status': 'PRE_EXECUTION_EXPOSED_SOURCE_FREEZE', 'bindings': bindings,
              'frozen_seven_full_values': old['design']['shared_whole_word_hypotheses'],
              'models': models, 'RF1b': 'NO_WHOLE_READER', 'sealed': ['f84', 'f84r'],
              'independent_confirmation_capacity': 0}
    (EXP / 'src/SOURCE.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    for name, model in models.items():
        print(name, len(model['groups']), 'groups', len({g['word'] for g in model['groups']}), 'types')
    print('SOURCE_ONLY_NO_PARSER_EXECUTION')


if __name__ == '__main__':
    main()
