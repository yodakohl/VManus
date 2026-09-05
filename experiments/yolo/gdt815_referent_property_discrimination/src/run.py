#!/usr/bin/env python3
"""Source-bound referent cards; no semantic frequency score."""
import argparse
import csv
import importlib.util
import io
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
EXP = Path(__file__).resolve().parent.parent
ROOT = EXP.parents[2]
READERS = ['zl3b_clean', 'it2a_clean', 'rf1b_clean']
loader = importlib.util.spec_from_file_location('source_guard', ROOT /
    'experiments/yolo/gdt812_additional_page_semantic_bridge/src/family_probe.py')
guard = importlib.util.module_from_spec(loader)
loader.loader.exec_module(guard)


def tsv(rows):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def build():
    prior = json.loads((ROOT / 'experiments/yolo/gdt813_f17_content_word_transfer/src/SPEC.json').read_text())
    spec = json.loads((EXP / 'src/SPEC.json').read_text())
    pages = prior['source_selectors']
    guard.require(len(set(pages)) == 39 and spec['sealed_data'] == ['f84', 'f84r']
                  and not any(p.startswith('f84') for p in pages), 'Scope or seals changed')
    rows, query1 = guard.query('transcription/voynich_zl3b_lines.tsv',
        ['page', 'locus', 'kind', 'paragraph_start', 'paragraph_end', 'eva_clean'], pages)
    alt, query2 = guard.query('transcription/voynich_cross_transcription_lines.tsv',
                            ['page', 'locus', *READERS], pages)
    by_locus, cross = {r['locus']: r for r in rows}, {r['locus']: r for r in alt}
    guard.require(set(by_locus) == set(cross), 'Reader coverage changed')
    for locus, row in by_locus.items():
        guard.require(row['page'] == cross[locus]['page'] and row['eva_clean'] == cross[locus]['zl3b_clean'], 'Reader mismatch')
        row.update({k: cross[locus][k] for k in READERS})
    cards, trials, links = [], [], []
    for card_id, loci in spec['cards']:
        source = [by_locus[locus] for locus in loci]
        for reader in READERS:
            lines = [r[reader] for r in source]
            card = {'card_id': card_id, 'page': source[0]['page'], 'source_loci': ','.join(loci),
                    'kind': source[0]['kind'], 'reader': reader,
                    'source_lines_json': json.dumps(lines, ensure_ascii=False)}
            cards.append(card)
            for model, gloss in spec['models'].items():
                mapping = prior['shared_hypotheses'] | {'okaiin': gloss}
                trials.append(card | {'model': model, 'literal_hypotheses_json': json.dumps(
                    [mapping.get(w, '[' + w + ']') for line in lines for w in line.split()],
                    ensure_ascii=False), 'confidence': spec['confidence']})
    for link in spec['carrier_links']:
        label, prose, target = [by_locus[link[k]] for k in ('label', 'prose', 'target')]
        guard.require(label['kind'] == 'L' and prose['kind'] == target['kind'] == 'P', 'Carrier record types')
        for reader in READERS:
            guard.require(label[reader].split() == [link['carrier']] and link['carrier'] in prose[reader].split()
                          and 'okaiin' in target[reader].split(), 'Declared exact carrier missing')
            links.append({'carrier': link['carrier'], 'label_locus': link['label'],
                          'prose_locus': link['prose'], 'target_locus': link['target'], 'reader': reader,
                          'label_text': label[reader], 'prose_text': prose[reader], 'target_text': target[reader],
                          'relation': link['relation'], 'referent_identity': 'UNIDENTIFIED'})
    correction = {reader: {'f81v.4_last_word': by_locus['f81v.4'][reader].split()[-1],
                          'f81v.5_first_two': by_locus['f81v.5'][reader].split()[:2]} for reader in READERS}
    result = {'experiment_id': 'GDT815', 'status': 'SOURCE_CARDS_NOT_SEMANTIC_VALIDATION',
              'source_selectors': pages, 'visual_page_keys': 34, 'source_loci': len(rows),
              'construction_cards': len(spec['cards']), 'source_card_rows': len(cards),
              'literal_rows': len(trials), 'carrier_links': len(spec['carrier_links']),
              'carrier_reader_rows': len(links), 'f81v_correction': correction,
              'guarded_queries': [query1, query2], 'new_admissions': 0,
              'confirmed_lexemes': 0, 'confirmed_plaintext_clauses': 0,
              'dictionary_changed': False, 'meanings_validated': False,
              'no_score_no_ranking': True, 'sealed_data': ['f84', 'f84r']}
    contacts = list(csv.DictReader((EXP / 'src/CARRIER_LINKS.tsv').open(), delimiter='\t'))
    packets = []
    for contact in contacts:
        page = contact['source_locus'].split('.')[0]
        packets.append({'edge_id': contact['bridge_id'], 'batch_id': 'GDT815_CONTEXT',
            'page': page, 'physical_folio': re.match(r'f\d+', page).group(),
            'diagram_unit_id': 'WRITTEN_CONTEXT_NOT_OWNER',
            'pivot_visual_id': 'UNASSIGNED_CONTEXT', 'pivot_locus': contact['source_locus'],
            'target_visual_id': 'UNASSIGNED_CONTEXT', 'target_locus': contact['target_locus'].split(',')[-1],
            'relation_type': contact['relation_kind'], 'direction_basis': 'WRITTEN_ORDER_ONLY',
            'ownership_basis': 'NO_DECODED_OWNER', 'geometry_only_selection': 'FALSE',
            'source_manifest_id': 'GDT815', 'page_crop_sha256': 'NONE',
            'pivot_crop_sha256': 'NONE', 'target_crop_sha256': 'NONE',
            'source_aware_localizer': 'text_referent_auditor', 'relation_reviewer': 'coordinator',
            'relation_confidence': 'LOW', 'ambiguity_state': 'TEXT_CONTACT_NOT_SEMANTIC_RELATION',
            'formal_access_state': 'UNSEALED_ALREADY_INSPECTED', 'fold_assignment': 'EXPLORATORY',
            'eligibility_status': 'INELIGIBLE_TEXT_ONLY'})
    return {'CARDS.tsv': tsv(cards), 'LITERAL_TRIALS.tsv': tsv(trials),
            'CARRIER_LINKS.tsv': tsv(links), 'RELATION_PACKET.tsv': tsv(packets),
            'RESULT.json': json.dumps(result, indent=2, sort_keys=True) + '\n'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for name, value in build().items():
        path = EXP / 'artifacts' / name
        if args.check:
            guard.require(path.read_text() == value, 'Artifact differs: ' + name)
        else:
            path.write_text(value)
    print('PASS_SOURCE_REPLAY_ONLY; 10 cards, 3 readers, 6 candidates; no semantic score')


if __name__ == '__main__':
    main()
