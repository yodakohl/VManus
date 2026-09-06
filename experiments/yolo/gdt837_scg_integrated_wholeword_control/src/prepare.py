#!/usr/bin/env python3
"""Fixed SCG source preparation and independently generated opaque controls.

No fitter or candidate score is used. Complete source gates precede any keys.
All console output is aggregate; shared gold and map-only truth stay separate.
"""
from __future__ import annotations
import argparse
from collections import Counter
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import types

BASE = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]
SPEC_PATH = Path(__file__).with_name('ENCODER_SPEC.json')
COMMIT = 'b19bcbd3ab66914570b5bb0616a9066d56d5e7ea'
INITIAL_HASH = 'a2df568ffe0eeecfad8e39e91432ac7a3db5289871ebd61a283d49c84a7cde31'
RAW_HASHES = {
 'la_ittb-ud-train.conllu': '0f0aded3ec3f697cdb8dc2294d213bdc951b127a5bc3d2114be22cd730cac5b8',
 'la_ittb-ud-dev.conllu': 'e750a8b89b2bd23459fe0226d94eafd9bd0401d95531df5618170c48b13ac83f',
 'la_ittb-ud-test.conllu': 'b25d8f12a7f483ff6152ce3b3724aabafffc1336103526229c919808f9de5f1e',
}
HELPERS = {
 'experiments/yolo/gdt832_joint_family_context_control/src/prepare.py': 'a8ca27308ab3f1fbeda1eef756c71081b602020b8b59350ba8661efd79536b77',
 'experiments/yolo/gdt834_role_blind_mixed_control/src/prepare.py': 'ae3e39cb3e39636833eaed60191181e0c01d3a443e8d634c277b1d542076ac0a',
}
REFERENCE_BASE = 'experiments/yolo/gdt834_role_blind_mixed_control/prepared'
REFERENCE_HASHES = {
 'reference.jsonl': 'dc9c57b32779b4be64911c042d8ad468f090ebbebcd9686d71a7ba422263b3e1',
 'reference_ids.json': 'b759b59a92bde4e56efc83db8b702eb37a835abecf57f18a37a92ca097010526',
 'candidates.json': '66d920e39056d6136a92c8a4509bb0d24c0d9ca9c1e01fdb9794d2f3ce663e86',
 'families.json': 'ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356',
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return digest(Path(path).read_bytes())


def canonical_json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode()


def gzip_json_bytes(value):
    stream = io.BytesIO()
    with gzip.GzipFile(filename='', mode='wb', compresslevel=9, fileobj=stream, mtime=0) as output:
        output.write(canonical_json_bytes(value))
    return stream.getvalue()


def read_json(path):
    path = Path(path)
    data = path.read_bytes()
    if path.suffix == '.gz':
        data = gzip.decompress(data)
    return json.loads(data)


def write_json(path, value, check=False):
    path = Path(path)
    data = gzip_json_bytes(value) if path.suffix == '.gz' else canonical_json_bytes(value)
    emit(path, data, check)


def emit(path, data, check=False):
    if check:
        if path.read_bytes() != data:
            raise ValueError('Reproduction mismatch: ' + path.name)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def gzip_metadata(path):
    data = Path(path).read_bytes()
    if data[:3] != b'\x1f\x8b\x08' or data[3] != 0 or data[4:8] != b'\0' * 4:
        raise ValueError('Noncanonical gzip header')
    plain = gzip.decompress(data)
    return {'compressed_sha256': digest(data), 'compressed_bytes': len(data),
            'uncompressed_sha256': digest(plain), 'uncompressed_bytes': len(plain)}


def verify(path, expected):
    if sha(path) != expected:
        raise ValueError('Frozen input changed: ' + Path(path).name)


def load_helper(relative):
    path = ROOT / relative
    verify(path, HELPERS[relative])
    module = types.ModuleType('_gdt837_' + path.parent.parent.name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def source_units(source_dir, normalizer):
    """Metadata pass selects SCG references before text/token materialization."""
    units, exclusions, all_numbers, excluded_forma = [], [], [], 0
    for filename in sorted(RAW_HASHES):
        raw = source_dir / filename
        verify(raw, RAW_HASHES[filename])
        accepted, sentence_id = {}, None
        for line in raw.open():
            if line.startswith('# sent_id = '):
                sentence_id = line.split(' = ', 1)[1].strip()
            elif line.startswith('# reference = '):
                reference = line.split(' = ', 1)[1].strip()
                match = re.fullmatch(r'ittb-scg-s([1-9][0-9]*)', reference)
                if match:
                    if sentence_id in accepted:
                        raise ValueError('Duplicate source sentence ID')
                    number = int(match[1])
                    accepted[sentence_id] = (reference, number)
                    all_numbers.append(number)
                else:
                    if re.fullmatch(r'ittb-forma-s[1-9][0-9]*', reference) is None:
                        raise ValueError('Unexpected excluded work identity')
                    excluded_forma += 1
        comments, rows, admitted = {}, [], False

        def finish():
            if not admitted:
                return
            reference, number = accepted[comments['sent_id']]
            if comments['reference'] != reference:
                raise ValueError('Metadata/payload reference mismatch')
            words, unsupported, analyses, statuses = normalizer.annotation_join(comments, rows)
            split = 'discovery' if number <= 9859 else 'held'
            if unsupported:
                exclusions.append({'source_reference': reference, 'split': split, 'words': len(words)})
                return
            book = 'I' if number <= 4306 else 'II' if number <= 9859 else 'III' if number <= 17721 else 'IV'
            units.append({'paragraph_id': f'SCG:s{number}', 'source_reference': reference,
                'source_reference_number': number, 'source_file': filename,
                'source_sentence_id': comments['sent_id'], 'book': book, 'split': split,
                'words': words, 'lemma_sets': analyses, 'annotation_status': statuses})

        for line in raw.open():
            line = line.rstrip('\n')
            if not line:
                finish()
                comments, rows, admitted = {}, [], False
            elif line.startswith('# sent_id = '):
                sentence_id = line.split(' = ', 1)[1]
                admitted = sentence_id in accepted
                if admitted:
                    comments['sent_id'] = sentence_id
            elif admitted and line.startswith('# ') and ' = ' in line:
                key, value = line[2:].split(' = ', 1)
                comments[key] = value
            elif admitted and not line.startswith('#'):
                fields = line.split('\t')
                if len(fields) != 10:
                    raise ValueError('CoNLL-U schema')
                rows.append(fields)
        finish()
    if sorted(all_numbers) != list(range(1, 23688)):
        raise ValueError('Complete canonical SCG order missing or duplicated')
    units.sort(key=lambda row: row['source_reference_number'])
    return units, exclusions, excluded_forma


def source_phase(source_dir, check=False):
    spec = read_json(SPEC_PATH)
    normalizer = load_helper(list(HELPERS)[0])
    head = subprocess.check_output(['git', '-C', str(source_dir), 'rev-parse', 'HEAD'], text=True).strip()
    if head != COMMIT:
        raise ValueError('Pinned ITTB commit changed')
    for filename in [*RAW_HASHES, 'README.md', 'LICENSE.txt']:
        if (source_dir / filename).read_bytes() != subprocess.check_output(['git', '-C', str(source_dir), 'show', COMMIT + ':' + filename]):
            raise ValueError('Source differs from pinned commit')
    inherited_path = ROOT / 'experiments/yolo/gdt836_integrated_wholeword_precedence/src/ENCODER_SPEC.json'
    inherited = read_json(inherited_path)
    for field in ['letter_alphabet', 'suffix_values', 'suffix_minimum_stem_characters', 'wholeword_values', 'precedence',
                  'minimum_discovery_paragraphs', 'minimum_held_paragraphs', 'minimum_discovery_occurrences_active_suffix_or_wholeword',
                  'minimum_discovery_occurrences_held_active_literal', 'minimum_held_novel_composed_form_occurrences',
                  'minimum_held_unambiguous_novel_composed_lemma_occurrences', 'deduplication_audit_words']:
        if spec[field] != inherited[field]:
            raise ValueError('Inherited source rule or gate changed')
    if spec['discovery_reference_range'] != [1, 9859] or spec['held_reference_range'] != [9860, 23687]:
        raise ValueError('Fixed book split changed')
    for filename, expected in REFERENCE_HASHES.items():
        original = ROOT / REFERENCE_BASE / filename
        verify(original, expected)
        emit(BASE / 'prepared' / filename, original.read_bytes(), check)
    reference = [json.loads(line) for line in (BASE / 'prepared/reference.jsonl').read_text().splitlines()]
    candidates = read_json(BASE / 'prepared/candidates.json')
    units, excluded, excluded_forma = source_units(source_dir, normalizer)
    discovery_forms = {word for unit in units if unit['split'] == 'discovery' for word in unit['words']}
    discovery_lemmas = {lemma for unit in units if unit['split'] == 'discovery' for analysis in unit['lemma_sets'] if analysis for lemma in analysis}
    counts, supports = {}, {split: Counter() for split in ('discovery', 'held')}
    for split in supports:
        selected = [unit for unit in units if unit['split'] == split]
        for unit in selected:
            unit['novel_form'] = [word not in discovery_forms for word in unit['words']]
            unit['novel_lemma'] = [None if analysis is None or len(analysis) != 1 else analysis[0] not in discovery_lemmas for analysis in unit['lemma_sets']]
            unit['composed'] = [word not in spec['wholeword_values'] for word in unit['words']]
            for word in unit['words']:
                supports[split].update(normalizer.logical_encode_word(word, spec))
        counts[split] = {'source_sentence_units': len(selected), 'words': sum(len(unit['words']) for unit in selected),
            'types': len({word for unit in selected for word in unit['words']}),
            'novel_composed_forms': sum(new and composed for unit in selected for new, composed in zip(unit['novel_form'], unit['composed'])),
            'unambiguous_novel_composed_lemmas': sum(new is True and composed for unit in selected for new, composed in zip(unit['novel_lemma'], unit['composed'])),
            'annotation_status_counts': dict(Counter(status for unit in selected for status in unit['annotation_status']))}
    active = set(supports['discovery']) | set(supports['held'])
    rule_metadata = {}
    for role, nominal in [('L', 26), ('S', 4), ('W', 8)]:
        rules = {atom for atom in active if atom[0] == role}
        held_rules = {atom for atom in supports['held'] if atom[0] == role}
        rule_metadata[role] = {'nominal': nominal, 'active': len(rules), 'inactive': nominal - len(rules),
            'minimum_D_active_occurrences': min((supports['discovery'][atom] for atom in rules), default=0),
            'minimum_D_held_active_occurrences': min((supports['discovery'][atom] for atom in held_rules), default=0),
            'held_only_rules': sum(supports['discovery'][atom] == 0 for atom in held_rules),
            'active_rules_below_8_D': sum(supports['discovery'][atom] < 8 for atom in rules)}
    control_windows = {tuple(words) for unit in units for words in normalizer.windows(unit['words'], 20)}
    overlap = sum(any(tuple(words) in control_windows for words in normalizer.windows(sentence, 20)) for sentence in reference)
    missing = set(spec['wholeword_values']) - set(candidates['wholeword_pool'])
    gates = {'D_units': counts['discovery']['source_sentence_units'] >= spec['minimum_discovery_paragraphs'],
        'H_units': counts['held']['source_sentence_units'] >= spec['minimum_held_paragraphs'],
        'active_S_8D': rule_metadata['S']['minimum_D_active_occurrences'] >= spec['minimum_discovery_occurrences_active_suffix_or_wholeword'],
        'active_W_8D': rule_metadata['W']['minimum_D_active_occurrences'] >= spec['minimum_discovery_occurrences_active_suffix_or_wholeword'],
        'held_active_L_1D': rule_metadata['L']['minimum_D_held_active_occurrences'] >= spec['minimum_discovery_occurrences_held_active_literal'],
        'H_new_composed_forms_100': counts['held']['novel_composed_forms'] >= spec['minimum_held_novel_composed_form_occurrences'],
        'H_new_unambiguous_composed_lemmas_30': counts['held']['unambiguous_novel_composed_lemmas'] >= spec['minimum_held_unambiguous_novel_composed_lemma_occurrences'],
        'all_true_W_in_frozen_candidates': not missing, 'reference_exact20_overlap_zero': overlap == 0}
    initial = {'status': 'SOURCE_CAPACITY_PASS' if all(gates.values()) else 'SOURCE_CAPACITY_STOP', 'gates': gates,
        'failed_gates': [name for name, value in gates.items() if not value],
        'split': 'SCG I-II s1-9859 discovery / III-IV s9860-23687 held; source-sentence units',
        'partitions': counts, 'rules': rule_metadata, 'reference_exact20_overlap_sentences': overlap,
        'excluded_unrepresentable_units': excluded, 'excluded_forma_concordance_units_by_metadata': excluded_forma,
        'canonical_source_ids_before_exclusion': len(units) + len(excluded), 'missing_W_candidate_count': len(missing), 'keys_generated': False}
    initial_path = BASE / 'prepared/INITIAL_CAPACITY.json'
    verify(initial_path, INITIAL_HASH)
    if (json.dumps(initial, indent=2, sort_keys=True) + '\n').encode() != initial_path.read_bytes():
        raise ValueError('Initial source-capacity snapshot did not reproduce byte-exactly')
    source_gold = {'schema': 'GDT837_SOURCE_TRUTH_V1', 'unit_type': 'source_sentence', 'paragraphs': units}
    gold_path = BASE / 'confirmation/source_truth.json.gz'
    write_json(gold_path, source_gold, check)
    inventory_path = BASE / 'prepared/inventory.json'
    write_json(inventory_path, {'schema': 'GDT837_OPAQUE_INVENTORY_V1', 'primitive_ids': [f'X{i:02d}' for i in range(38)]}, check)
    metadata_path = BASE / 'prepared/UNITS.json.gz'
    write_json(metadata_path, {'schema': 'GDT837_SOURCE_UNIT_METADATA_V1', 'unit_type': 'source_sentence', 'plaintext_included': False,
        'units': [{**{key: unit[key] for key in ['paragraph_id', 'source_reference', 'source_reference_number', 'source_file',
            'source_sentence_id', 'book', 'split']}, 'word_count': len(unit['words'])} for unit in units]}, check)
    manifest = {'schema': 'GDT837_SOURCE_MANIFEST_V1', 'repository': 'https://github.com/UniversalDependencies/UD_Latin-ITTB.git',
        'commit': COMMIT, 'license': 'CC BY-NC-SA 3.0', 'raw_source_sha256': RAW_HASHES,
        'documentation_sha256': {name: sha(source_dir / name) for name in ['README.md', 'LICENSE.txt']},
        'helpers_sha256': HELPERS, 'inherited_gates': {'path': inherited_path.relative_to(ROOT).as_posix(), 'sha256': sha(inherited_path)},
        'reference_sha256': {REFERENCE_BASE + '/' + name: expected for name, expected in REFERENCE_HASHES.items()},
        'freshness': spec['freshness'], 'boundary_claim': spec['boundary_claim'], 'source_dependent_key_selection': False,
        'excluded_work': 'ittb-forma concordances, selected out by reference identity in a metadata-only first pass',
        'known_orthography_difference': 'ITTB uses u where native Monarchia sometimes writes v; original spellings are retained on both sides'}
    manifest_path = BASE / 'sources/MANIFEST.json'
    write_json(manifest_path, manifest, check)
    for filename in ['README.md', 'LICENSE.txt']:
        emit(BASE / 'sources' / filename, (source_dir / filename).read_bytes(), check)
    capacity = {**initial, 'schema': 'GDT837_SOURCE_CAPACITY_V1', 'unit_type': 'source_sentence',
        'initial_snapshot_sha256': INITIAL_HASH, 'encoder_spec_sha256': sha(SPEC_PATH),
        'source_prepare_sha256': sha(Path(__file__)), 'source_manifest_sha256': sha(manifest_path),
        'shared_source_truth': gzip_metadata(gold_path), 'unit_metadata': gzip_metadata(metadata_path),
        'prepared_input_sha256': {name: sha(BASE / 'prepared' / name) for name in [*REFERENCE_HASHES, 'inventory.json']},
        'historical_keys_and_fits_require_fixed_capacity_pass': True}
    write_json(BASE / 'prepared/CAPACITY.json', capacity, check)
    return capacity


def generation_phase(check=False):
    spec = read_json(SPEC_PATH)
    capacity = read_json(BASE / 'prepared/CAPACITY.json')
    if capacity['status'] != 'SOURCE_CAPACITY_PASS':
        raise ValueError('Source gate stops before any keys')
    verify(SPEC_PATH, capacity['encoder_spec_sha256'])
    verify(Path(__file__), capacity['source_prepare_sha256'])
    for name, expected in capacity['prepared_input_sha256'].items():
        verify(BASE / 'prepared' / name, expected)
    source_path = BASE / 'confirmation/source_truth.json.gz'
    if gzip_metadata(source_path) != capacity['shared_source_truth']:
        raise ValueError('Shared original source changed')
    source = read_json(source_path)
    generator = load_helper(list(HELPERS)[1])
    worlds, compressed_files = [], {'confirmation/source_truth.json.gz': gzip_metadata(source_path),
                                  'prepared/UNITS.json.gz': gzip_metadata(BASE / 'prepared/UNITS.json.gz')}
    for seed in spec['world_seeds']:
        typed_key, opaque_to_typed, key = generator.make_maps(seed, spec)
        typed_to_opaque = {typed: opaque for opaque, typed in opaque_to_typed.items()}
        cipher_hashes = {}
        for split in ['discovery', 'held']:
            paragraphs = []
            for unit in source['paragraphs']:
                if unit['split'] != split:
                    continue
                typed_words = [generator.HELPER.encode_word(word, typed_key, spec) for word in unit['words']]
                words = [[typed_to_opaque[atom] for atom in word] for word in typed_words]
                if [''.join(key[atom]['output'] for atom in word) for word in words] != unit['words']:
                    raise ValueError('Original-spelling generator roundtrip failed')
                paragraphs.append({'paragraph_id': unit['paragraph_id'], 'words': words})
            packet = {'schema': 'GDT837_OPAQUE_CIPHERTEXT_V1', 'world_id': seed, 'split': split,
                      'unit_type': 'source_sentence', 'paragraphs': paragraphs}
            relative = f'prepared/world_{seed}_{split}.json.gz'
            write_json(BASE / relative, packet, check)
            compressed_files[relative] = gzip_metadata(BASE / relative)
            cipher_hashes[split] = compressed_files[relative]['compressed_sha256']
        truth = {'schema': 'GDT837_WORLD_TRUTH_V1', 'world_id': seed, 'unit_type': 'source_sentence',
            'decode_map': key, 'typed_decode_map': typed_key, 'opaque_to_typed': opaque_to_typed,
            'source_truth_sha256': capacity['shared_source_truth']['compressed_sha256'],
            'encoder_spec_sha256': sha(SPEC_PATH), 'ciphertext_sha256': cipher_hashes}
        relative = f'confirmation/world_{seed}_truth.json.gz'
        write_json(BASE / relative, truth, check)
        compressed_files[relative] = gzip_metadata(BASE / relative)
        worlds.append({'world_id': seed, 'ciphertext_sha256': cipher_hashes,
            'map_only_truth_sha256': compressed_files[relative]['compressed_sha256'], 'original_spelling_roundtrip_pass': True})
    result = {'schema': 'GDT837_GENERATION_V1', 'status': 'OPAQUE_CONTROLS_GENERATED_UNFITTED',
        'capacity_sha256': sha(BASE / 'prepared/CAPACITY.json'), 'encoder_spec_sha256': sha(SPEC_PATH),
        'worlds': worlds, 'gzip_files': compressed_files, 'gzip_header': {'filename': '', 'mtime': 0, 'compression_level': 9},
        'shared_source_gold_copies': 1, 'world_truth_contains_source_words': False,
        'same_opaque_packet_for_all_fit_conditions': True, 'condition_or_score_information_in_encoder': False,
        'plaintext_keys_or_decoded_examples_in_console': False}
    write_json(BASE / 'prepared/GENERATION.json', result, check)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, default=BASE / 'runtime/ittb_source')
    parser.add_argument('--phase', choices=['sources', 'generate', 'all'], default='sources')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.phase in ['sources', 'all']:
        capacity = source_phase(args.source_dir, args.check)
        print(json.dumps({'status': capacity['status'], 'failed_gates': capacity['failed_gates'],
                          'partitions': capacity['partitions'], 'keys_generated': False}, sort_keys=True))
        if capacity['status'] != 'SOURCE_CAPACITY_PASS':
            return
    if args.phase in ['generate', 'all']:
        generation = generation_phase(args.check)
        print(json.dumps({'status': generation['status'], 'worlds': len(generation['worlds']),
            'gzip_files': {name: {field: value for field, value in metadata.items() if field.endswith('_bytes')}
                          for name, metadata in generation['gzip_files'].items()},
            'plaintext_keys_or_decoded_examples_in_console': False}, sort_keys=True))


if __name__ == '__main__':
    main()
