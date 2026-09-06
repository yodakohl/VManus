#!/usr/bin/env python3
"""Reproduce the fixed Questio source-capacity STOP; no key generator or fit."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import types

BASE = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]
RAW_NAME = 'la_udante-ud-train.conllu'
RAW_SHA256 = '7308e1b9145bc5c4e6febc1149722a8fed89b2cf5a59a9a83ec53744de57744f'
INITIAL_SHA256 = 'f92960e81c7d00df316ad55c2f8c27c9579e88f8d79e556924a5e4d4da61f213'
HELPERS = {
    'experiments/yolo/gdt832_joint_family_context_control/src/prepare.py': 'a8ca27308ab3f1fbeda1eef756c71081b602020b8b59350ba8661efd79536b77',
    'experiments/yolo/gdt835_wholeword_precedence_audit/src/source_context_audit.py': 'd9034b9aabd712defa859075dc8f54cbea620ff0ecab2057f5b8cbb838c75244',
}
UPSTREAM_BASE = 'experiments/yolo/gdt834_role_blind_mixed_control'
UPSTREAM = {
    'src/ENCODER_SPEC.json': '7475b71abac50e8e4e6bc3bb2c1f1bf6c13eb45dcadcc684251c513f890b4f7c',
    'prepared/reference.jsonl': 'dc9c57b32779b4be64911c042d8ad468f090ebbebcd9686d71a7ba422263b3e1',
    'prepared/reference_ids.json': 'b759b59a92bde4e56efc83db8b702eb37a835abecf57f18a37a92ca097010526',
    'prepared/candidates.json': '66d920e39056d6136a92c8a4509bb0d24c0d9ca9c1e01fdb9794d2f3ce663e86',
    'prepared/families.json': 'ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encode_json(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def verify(path, expected):
    if sha(path) != expected:
        raise ValueError('Frozen input changed: ' + path.name)


def load_helper(relative):
    path = ROOT / relative
    verify(path, HELPERS[relative])
    module = types.ModuleType('_gdt836_' + path.stem)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def compute(source_dir):
    source_helper = load_helper(next(iter(HELPERS)))
    guarded = load_helper(list(HELPERS)[1]).guarded_sentences
    raw = source_dir / RAW_NAME
    verify(raw, RAW_SHA256)
    for relative, expected in UPSTREAM.items():
        verify(ROOT / UPSTREAM_BASE / relative, expected)
    initial_path = BASE / 'prepared/INITIAL_CAPACITY.json'
    verify(initial_path, INITIAL_SHA256)
    spec = json.loads((BASE / 'src/ENCODER_SPEC.json').read_text())
    inherited = json.loads((ROOT / UPSTREAM_BASE / 'src/ENCODER_SPEC.json').read_text())
    for field in ['letter_alphabet', 'suffix_values', 'suffix_minimum_stem_characters', 'wholeword_values', 'precedence',
                  'minimum_discovery_paragraphs', 'minimum_held_paragraphs',
                  'minimum_discovery_occurrences_active_suffix_or_wholeword',
                  'minimum_discovery_occurrences_held_active_literal', 'minimum_held_novel_composed_form_occurrences',
                  'minimum_held_unambiguous_novel_composed_lemma_occurrences', 'deduplication_audit_words']:
        if spec[field] != inherited[field]:
            raise ValueError('Inherited rule or threshold changed: ' + field)
    if spec['discovery_citation_numbers'] != [1, 44] or spec['held_citation_numbers'] != [45, 88]:
        raise ValueError('Fixed midpoint partition changed')
    reference = [json.loads(line) for line in (ROOT / UPSTREAM_BASE / 'prepared/reference.jsonl').read_text().splitlines()]
    candidates = json.loads((ROOT / UPSTREAM_BASE / 'prepared/candidates.json').read_text())
    paragraphs, last, occurrences, excluded, reused = [], None, Counter(), [], []
    for comments, rows in guarded(raw, 'Que'):
        citation = comments['citation_hierarchy']
        heading, label = citation.split(',')
        number = int(label.split('_')[1])
        if heading != spec['source_heading'] or label != f'Paragraphus_{number}' or not 1 <= number <= 88:
            raise ValueError('Unexpected source citation')
        split = 'discovery' if number <= 44 else 'held'
        if citation != last:
            occurrences[citation] += 1
            occurrence = occurrences[citation]
            if occurrence > 1:
                reused.append(citation)
            paragraphs.append({'id': citation + f':occurrence_{occurrence}', 'citation': citation,
                'occurrence': occurrence, 'split': split, 'words': [], 'analyses': [], 'statuses': [],
                'source_sentence_ids': [], 'unsupported': False})
            last = citation
        words, bad, analyses, statuses = source_helper.annotation_join(comments, rows)
        paragraph = paragraphs[-1]
        paragraph['words'].extend(words)
        paragraph['analyses'].extend(analyses)
        paragraph['statuses'].extend(statuses)
        paragraph['source_sentence_ids'].append(comments['sent_id'])
        paragraph['unsupported'] |= bad
    for paragraph in paragraphs:
        if paragraph['unsupported']:
            excluded.append({'split': paragraph['split'], 'citation_id': paragraph['id'], 'word_count': len(paragraph['words'])})
    paragraphs = [paragraph for paragraph in paragraphs if not paragraph['unsupported']]
    discovery_words = {word for p in paragraphs if p['split'] == 'discovery' for word in p['words']}
    discovery_lemmas = {lemma for p in paragraphs if p['split'] == 'discovery' for analysis in p['analyses'] if analysis for lemma in analysis}
    counts, supports = {}, {split: Counter() for split in ['discovery', 'held']}
    for split in supports:
        selected = [paragraph for paragraph in paragraphs if paragraph['split'] == split]
        counts[split] = {'paragraphs': len(selected), 'sentences': sum(len(p['source_sentence_ids']) for p in selected),
            'words': sum(len(p['words']) for p in selected), 'types': len({word for p in selected for word in p['words']}),
            'novel_composed_forms': sum(word not in discovery_words and word not in spec['wholeword_values'] for p in selected for word in p['words']),
            'unambiguous_novel_composed_lemmas': sum(analysis is not None and len(analysis) == 1 and analysis[0] not in discovery_lemmas
                and word not in spec['wholeword_values'] for p in selected for word, analysis in zip(p['words'], p['analyses'])),
            'annotation_status_counts': dict(Counter(status for p in selected for status in p['statuses']))}
        for paragraph in selected:
            for word in paragraph['words']:
                supports[split].update(source_helper.logical_encode_word(word, spec))
    active = set(supports['discovery']) | set(supports['held'])
    rule_metadata = {}
    for role, nominal in [('L', 26), ('S', 4), ('W', 8)]:
        rules = {atom for atom in active if atom[0] == role}
        held_rules = {atom for atom in supports['held'] if atom[0] == role}
        rule_metadata[role] = {'nominal': nominal, 'active': len(rules), 'inactive': nominal - len(rules),
            'minimum_D_active_occurrences': min([supports['discovery'][atom] for atom in rules], default=0),
            'minimum_D_held_active_occurrences': min([supports['discovery'][atom] for atom in held_rules], default=0),
            'held_only_rules': sum(supports['discovery'][atom] == 0 for atom in held_rules),
            'active_rules_below_8_D': sum(supports['discovery'][atom] < 8 for atom in rules)}
    control_windows = {tuple(words) for p in paragraphs for words in source_helper.windows(p['words'], 20)}
    overlap = sum(any(tuple(words) in control_windows for words in source_helper.windows(sentence, 20)) for sentence in reference)
    missing = set(spec['wholeword_values']) - set(candidates['wholeword_pool'])
    gates = {'D_runs': counts['discovery']['paragraphs'] >= spec['minimum_discovery_paragraphs'],
        'H_runs': counts['held']['paragraphs'] >= spec['minimum_held_paragraphs'],
        'active_S_8D': rule_metadata['S']['minimum_D_active_occurrences'] >= spec['minimum_discovery_occurrences_active_suffix_or_wholeword'],
        'active_W_8D': rule_metadata['W']['minimum_D_active_occurrences'] >= spec['minimum_discovery_occurrences_active_suffix_or_wholeword'],
        'held_active_L_1D': rule_metadata['L']['minimum_D_held_active_occurrences'] >= spec['minimum_discovery_occurrences_held_active_literal'],
        'H_new_composed_forms_100': counts['held']['novel_composed_forms'] >= spec['minimum_held_novel_composed_form_occurrences'],
        'H_new_unambiguous_composed_lemmas_30': counts['held']['unambiguous_novel_composed_lemmas'] >= spec['minimum_held_unambiguous_novel_composed_lemma_occurrences'],
        'all_true_W_in_frozen_candidates': not missing,
        'reference_exact20_overlap_zero': overlap == 0}
    initial = {'status': 'SOURCE_CAPACITY_PASS' if all(gates.values()) else 'SOURCE_CAPACITY_STOP',
        'gates': gates, 'failed_gates': [key for key, value in gates.items() if not value],
        'split': 'Que citation1-44 discovery/45-88 held, fixed before word/rule counts',
        'partitions': counts, 'rules': rule_metadata, 'reference_exact20_overlap_sentences': overlap,
        'excluded_whole_paragraphs': excluded, 'reused_citation_events': len(reused),
        'missing_W_candidate_count': len(missing), 'keys_generated': False}
    if encode_json(initial) != initial_path.read_bytes():
        raise ValueError('Initial immutable capacity snapshot did not reproduce byte-exactly')
    paragraph_metadata = {'schema': 'GDT836_PARAGRAPH_METADATA_V1', 'plaintext_included': False, 'paragraphs': [
        {'paragraph_id': 'Que:' + p['citation'].replace(',', ':') + (f":occurrence_{p['occurrence']}" if p['occurrence'] > 1 else ''),
         'citation_hierarchy': p['citation'], 'citation_occurrence': p['occurrence'], 'split': p['split'],
         'source_sentence_ids': p['source_sentence_ids'], 'word_count': len(p['words']),
         'annotation_status_counts': dict(Counter(p['statuses']))} for p in paragraphs]}
    manifest = {'schema': 'GDT836_SOURCE_MANIFEST_V1',
        'repository': 'https://github.com/UniversalDependencies/UD_Latin-UDante.git',
        'commit': 'e02420457780c6fbb503ba39a7d8798ab6a8645c', 'license': 'CC BY-NC-SA 3.0',
        'control_source': {'file': RAW_NAME, 'sha256': RAW_SHA256, 'work_selector_before_payload': 'Que'},
        'raw_documentation': {name: sha(source_dir / name) for name in ['README.md', 'LICENSE.txt']},
        'helpers_sha256': HELPERS,
        'frozen_reference_and_encoder_sha256': {UPSTREAM_BASE + '/' + name: digest for name, digest in UPSTREAM.items()},
        'initial_snapshot_sha256': INITIAL_SHA256,
        'paragraph_unit': spec['paragraph_unit'], 'source_authorship': 'Disputed according to primary UDante README',
        'normalization_or_reference_changes': False, 'historical_keys_ciphertexts_fits_generated': False}
    capacity = {**initial, 'schema': 'GDT836_SOURCE_CAPACITY_V1', 'original_initial_snapshot_sha256': INITIAL_SHA256,
        'encoder_spec_sha256': sha(BASE / 'src/ENCODER_SPEC.json'),
        'source_manifest_sha256': hashlib.sha256(encode_json(manifest)).hexdigest(),
        'paragraph_metadata_sha256': hashlib.sha256(encode_json(paragraph_metadata)).hexdigest(),
        'historical_fit_allowed': False, 'reproduction': 'Initial snapshot reproduced byte-for-byte; no source/deck/partition/threshold changes'}
    return capacity, paragraph_metadata, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, default=BASE / 'runtime/udante_source')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    capacity, paragraphs, manifest = compute(args.source_dir)
    outputs = {'prepared/CAPACITY.json': encode_json(capacity), 'prepared/PARAGRAPHS.json': encode_json(paragraphs),
        'sources/MANIFEST.json': encode_json(manifest),
        'sources/README.md': (args.source_dir / 'README.md').read_bytes(),
        'sources/LICENSE.txt': (args.source_dir / 'LICENSE.txt').read_bytes()}
    for relative, data in outputs.items():
        path = BASE / relative
        if args.check:
            if path.read_bytes() != data:
                raise ValueError('Source artifact replay mismatch: ' + relative)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(json.dumps({'status': capacity['status'], 'failed_gates': capacity['failed_gates'],
        'held_only_literal_rules': capacity['rules']['L']['held_only_rules'],
        'initial_snapshot_byte_exact': True, 'keys_generated': False, 'historical_fit_allowed': False}, sort_keys=True))


if __name__ == '__main__':
    main()
