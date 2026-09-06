#!/usr/bin/env python3
"""Exploratory source census after GDT834, before GDT835 registration.

No language-model score, fit, candidate comparison or encoder-collision query.
All 42 discovery occurrences are included; no exemplary contexts are selected.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import statistics
import types

BASE = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]
HELPER = 'experiments/yolo/gdt832_joint_family_context_control/src/prepare.py'
HELPER_HASH = 'a8ca27308ab3f1fbeda1eef756c71081b602020b8b59350ba8661efd79536b77'
TRUTH = 'experiments/yolo/gdt834_role_blind_mixed_control/sealed/source_truth.json'
TRUTH_HASH = '16cf8d525bd8b5f1e55bfed223869d7eb552154f0db97eed7dccea0f7ef2755f'
REFERENCE = 'experiments/yolo/gdt834_role_blind_mixed_control/prepared/reference.jsonl'
REFERENCE_HASH = 'dc9c57b32779b4be64911c042d8ad468f090ebbebcd9686d71a7ba422263b3e1'
RAW_HASHES = {
    'la_udante-ud-train.conllu': '7308e1b9145bc5c4e6febc1149722a8fed89b2cf5a59a9a83ec53744de57744f',
    'la_udante-ud-dev.conllu': '11d96611add7862a886ca77bebc4bb32c8d314a2f6eec6f1a6a2d116abaae7e4',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(path, expected):
    if sha(path) != expected:
        raise ValueError('Bound source changed: ' + path.name)


def helper():
    path = ROOT / HELPER
    verify(path, HELPER_HASH)
    module = types.ModuleType('_gdt835_source_helper')
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def guarded_sentences(path, work):
    """Filter on sent_id before materializing any other work's text or rows."""
    comments, rows, admitted = {}, [], False
    for line in path.open():
        line = line.rstrip('\n')
        if not line:
            if admitted:
                yield comments, rows
            comments, rows, admitted = {}, [], False
        elif line.startswith('# sent_id = '):
            value = line.split(' = ', 1)[1]
            admitted = value.startswith(work + '-')
            if admitted:
                comments['sent_id'] = value
        elif admitted and line.startswith('# ') and ' = ' in line:
            key, value = line[2:].split(' = ', 1)
            comments[key] = value
        elif admitted and not line.startswith('#'):
            row = line.split('\t')
            if len(row) != 10:
                raise ValueError('CoNLL-U schema')
            rows.append(row)
    if admitted:
        yield comments, rows


def features(row):
    return dict(pair.split('=', 1) for pair in row[5].split('|') if '=' in pair)


def written_join(comments, rows, normalizer):
    words, labels, positions, covered = [], [], {}, {}
    for row in rows:
        token_id = row[0]
        if '-' in token_id:
            lo, hi = map(int, token_id.split('-'))
            forms, bad = normalizer(row[1])
            for i in range(lo, hi + 1):
                covered[str(i)] = row[0]
                positions[str(i)] = len(words)
            words.extend(forms)
            labels.extend([None] * len(forms))
        elif token_id.isdigit() and token_id not in covered:
            forms, bad = normalizer(row[1])
            positions[token_id] = len(words)
            words.extend(forms)
            labels.extend([row if len(forms) == 1 and not bad else None] * len(forms))
    if words != normalizer(comments['text'])[0]:
        raise ValueError('Written sentence alignment mismatch')
    return words, labels, positions, covered


def summarize(records, targets):
    aggregate = {}
    for word in sorted(targets):
        rows = [row for row in records if row['word'] == word]
        item = {'occurrences': len(rows)}
        for field in ['lemma', 'upos', 'deprel', 'case', 'head_upos', 'head_relation', 'finite_predicate_mood']:
            item[field] = dict(sorted(Counter(row[field] for row in rows).items()))
        distances = [row['head_distance_absolute'] for row in rows if row['head_distance_absolute'] is not None]
        item['head_distance_absolute'] = {'minimum': min(distances), 'median': statistics.median(distances),
            'maximum': max(distances), 'beyond_immediate_neighbor': sum(d > 1 for d in distances)}
        item['head_direction'] = dict(Counter('after' if row['head_distance_signed'] > 0 else 'before'
            for row in rows if row['head_distance_signed'] is not None))
        item['finite_anchor_available'] = sum(bool(row['finite_predicate_distances_absolute']) for row in rows)
        item['finite_anchor_all_beyond_immediate_neighbors'] = sum(bool(row['finite_predicate_distances_absolute'])
            and min(row['finite_predicate_distances_absolute']) > 1 for row in rows)
        item['finite_anchor_all_forms_in_reference'] = sum(bool(row['finite_predicate_forms_known_reference'])
            and all(row['finite_predicate_forms_known_reference']) for row in rows)
        item['head_lemma_known_reference'] = sum(row['head_lemma_known_reference'] for row in rows)
        item['finite_mood_by_upos'] = {upos: dict(Counter(row['finite_predicate_mood'] for row in rows if row['upos'] == upos))
            for upos in sorted({row['upos'] for row in rows})}
        for field in ['sentence_initial', 'sentence_final', 'cross_sentence_left_bigram', 'cross_sentence_right_bigram',
                      'punct_before_removed', 'punct_after_removed']:
            item[field] = sum(row[field] for row in rows)
        item['sentence_finite_verb_count'] = {'minimum': min(row['all_source_sentence_finite_verbs'] for row in rows),
            'median': statistics.median(row['all_source_sentence_finite_verbs'] for row in rows),
            'maximum': max(row['all_source_sentence_finite_verbs'] for row in rows)}
        aggregate[word] = item
    return aggregate


def audit(source_dir):
    module = helper()
    normalize = module.normalized_words
    for name, digest in RAW_HASHES.items():
        verify(source_dir / name, digest)
    verify(ROOT / TRUTH, TRUTH_HASH)
    verify(ROOT / REFERENCE, REFERENCE_HASH)
    gold = json.loads((ROOT / TRUTH).read_text())
    expected_sentences = {}
    for paragraph in gold['paragraphs']:
        if paragraph['split'] != 'discovery':
            continue
        for sentence, (start, stop) in zip(paragraph['source_sentence_ids'], paragraph['sentence_word_spans']):
            expected_sentences[sentence] = {'paragraph_id': paragraph['paragraph_id'], 'start': start,
                'words': paragraph['words'][start:stop], 'annotation_status': paragraph['annotation_status'][start:stop]}
    reference_sentences = list(guarded_sentences(source_dir / 'la_udante-ud-train.conllu', 'Mon'))
    reference_words = [normalize(c['text'])[0] for c, rows in reference_sentences]
    if reference_words != [json.loads(line) for line in (ROOT / REFERENCE).read_text().splitlines()]:
        raise ValueError('Reference does not exactly reproduce frozen native input')
    reference_vocabulary = {word for sentence in reference_words for word in sentence}
    reference_lemmas = set()
    for comments, rows in reference_sentences:
        words, labels, positions, covered = written_join(comments, rows, normalize)
        reference_lemmas.update(row[2] for row in labels if row is not None)
    discovery_sentences = [(c, rows) for c, rows in guarded_sentences(source_dir / 'la_udante-ud-dev.conllu', 'Epi')
                           if c['sent_id'] in expected_sentences]
    if len(discovery_sentences) != len(expected_sentences):
        raise ValueError('Discovery sentence inventory mismatch')
    aggregates, discovery_records, raw_counts, excluded_components = {}, [], Counter(), []
    for name, sentences, targets in [('discovery', discovery_sentences, {'ut', 'quod'}),
                                     ('reference', reference_sentences, {'ut', 'quod', 'cum'})]:
        records = []
        for sentence_index, (comments, rows) in enumerate(sentences):
            words, labels, positions, covered = written_join(comments, rows, normalize)
            by_id = {row[0]: row for row in rows if row[0].isdigit()}
            if name == 'discovery':
                expected = expected_sentences[comments['sent_id']]
                if expected['words'] != words:
                    raise ValueError('Source differs from original control words')
                for row in by_id.values():
                    forms = normalize(row[1])[0]
                    if len(forms) == 1 and forms[0] in targets:
                        raw_counts[forms[0]] += 1
                        if row[0] in covered:
                            excluded_components.append({'sentence_id': comments['sent_id'], 'token_id': row[0],
                                'word': forms[0], 'multiword_container_id': covered[row[0]],
                                'reason': 'Syntactic component is not a standalone written control word'})
            for index, (word, row) in enumerate(zip(words, labels)):
                if word not in targets:
                    continue
                if row is None:
                    raise ValueError('A target has no exact single-token join')
                head = by_id.get(row[6])
                finite = []
                if head is not None:
                    if features(head).get('VerbForm') == 'Fin':
                        finite.append(head)
                    finite += [x for x in by_id.values() if x[6] == head[0]
                        and (x[7] == 'cop' or x[7].startswith('aux')) and features(x).get('VerbForm') == 'Fin']
                moods = sorted({features(anchor).get('Mood', 'UNKNOWN') for anchor in finite})
                previous_same = sentence_index > 0 and sentences[sentence_index - 1][0]['citation_hierarchy'] == comments['citation_hierarchy']
                next_same = sentence_index + 1 < len(sentences) and sentences[sentence_index + 1][0]['citation_hierarchy'] == comments['citation_hierarchy']
                raw_position = rows.index(row)
                signed_distance = positions[head[0]] - index if head is not None and head[0] in positions else None
                record = {'sentence_id': comments['sent_id'], 'citation_hierarchy': comments['citation_hierarchy'],
                    'token_id': row[0], 'normalized_sentence_word_index': index, 'word': word,
                    'lemma': row[2], 'upos': row[3], 'deprel': row[7], 'target_features': row[5],
                    'case': features(row).get('Case', 'NONE'), 'head_token_id': row[6],
                    'head_upos': head[3] if head else 'ROOT', 'head_relation': head[7] if head else 'ROOT',
                    'head_lemma': head[2] if head else 'ROOT', 'head_features': head[5] if head else None,
                    'head_distance_absolute': abs(signed_distance) if signed_distance is not None else None,
                    'head_distance_signed': signed_distance,
                    'finite_predicate_token_ids': [anchor[0] for anchor in finite],
                    'finite_predicate_mood': '+'.join(moods) if moods else 'NO_DIRECT_FINITE_ANCHOR',
                    'finite_predicate_distances_absolute': [abs(positions[anchor[0]] - index) for anchor in finite],
                    'finite_predicate_distances_signed': [positions[anchor[0]] - index for anchor in finite],
                    'finite_predicate_forms_known_reference': [normalize(anchor[1])[0][0] in reference_vocabulary for anchor in finite],
                    'head_lemma_known_reference': head[2] in reference_lemmas if head else False,
                    'sentence_initial': index == 0, 'sentence_final': index == len(words) - 1,
                    'cross_sentence_left_bigram': index == 0 and previous_same,
                    'cross_sentence_right_bigram': index == len(words) - 1 and next_same,
                    'punct_before_removed': raw_position > 0 and rows[raw_position - 1][3] == 'PUNCT',
                    'punct_after_removed': raw_position + 1 < len(rows) and rows[raw_position + 1][3] == 'PUNCT',
                    'all_source_sentence_finite_verbs': sum(features(x).get('VerbForm') == 'Fin' for x in by_id.values())}
                if name == 'discovery':
                    record.update(paragraph_id=expected['paragraph_id'],
                        normalized_paragraph_word_index=expected['start'] + index,
                        frozen_annotation_status=expected['annotation_status'][index])
                records.append(record)
        aggregates[name] = summarize(records, targets)
        if name == 'discovery':
            discovery_records = records
    if Counter(row['word'] for row in discovery_records) != {'ut': 25, 'quod': 17}:
        raise ValueError('Not the complete fixed 42-occurrence census')
    source_notes = {
        'status': 'UNEXECUTED_METADATA_ONLY_SOURCE_CANDIDATES',
        'freshness_scope': 'Neither Que nor Egl was used as a control in GDT832-834. No new word/rule capacities, plaintext interpretation, encoder or keys were examined.',
        'Questio': {'metadata': 'One heading, contiguous Paragraphus_1 through Paragraphus_88',
            'candidate_partition_before_word_rule_counts': 'Original citation runs 1-44 discovery;45-88 held',
            'partition_limit': 'Mechanical source-order midpoint, not an attested chapter division',
            'primary_README_caveat': 'Technical/philosophical prose; disputed authorship'},
        'Eclogues': {'metadata': 'Four ordered units I, II_, III_, IV with irregular Paragraphus labels',
            'candidate_partition_before_word_rule_counts': 'Whole units I and II_ discovery;III_ and IV held',
            'primary_README_caveat': 'Four responsive bucolic poems: two Dante, two Giovanni del Virgilio; different genre and multiple authors'},
        'selection': 'No new control selected or generated'}
    return {'schema': 'GDT835_EXPLORATORY_SOURCE_CONTEXT_V1', 'status': 'SOURCE_CENSUS_COMPLETE',
        'performed_before_analysis_registration': True, 'post_GDT834_result_exploratory': True,
        'no_likelihood_scoring_fitting_or_collision_inspection': True,
        'cohort': 'Every standalone normalized ut/quod in the original GDT834 discovery source; all42, no example selection',
        'distance_definition': 'Native normalized written-word indexes; signed=head-minus-target, positive follows target. MWT components share their written container position. Immediate neighbor means absolute distance1.',
        'finite_anchor_definition': 'Annotated dependency head when VerbForm=Fin, plus its directly attached cop/aux children with VerbForm=Fin. No nearest-verb heuristic, recursive clause reconstruction or selected mood correction.',
        'raw_UD_syntactic_token_counts': dict(raw_counts), 'excluded_MWT_components': excluded_components,
        'annotation_join_status': dict(Counter(row['frozen_annotation_status'] for row in discovery_records)),
        'annotation_limits': [
            'CoNLL-U provides one selected analysis, not all linguistically possible readings; exact joins do not establish unique syntax.',
            'The primary README describes converted and corrected morphology/POS, manually annotated then corrected heads/relations, and modern segmentation adjustments.',
            'Missing direct finite anchors can reflect infinitives or elliptical comparisons; they are not automatically annotation errors.',
            'Observed mood or case tags are preserved even if questionable; no hand correction or categorical ut/quod/cum rule was chosen.',
            'Sparse literal predicate-form coverage and different construction frequencies limit direct transfer from Monarchia to Epistolae.',
            'Gold UD heads or target roles are explanatory source evidence here; a future decoder could not receive them for blind ciphertext.',
            'No clause-role distinction by itself proves that every alternative is ungrammatical; pronoun omission and multifunctional words remain possible.'],
        'aggregate': aggregates, 'discovery_occurrences': discovery_records,
        'unexecuted_source_note': source_notes,
        'source_sha256': {HELPER: HELPER_HASH, TRUTH: TRUTH_HASH, REFERENCE: REFERENCE_HASH,
            'UDante/' + 'la_udante-ud-train.conllu': RAW_HASHES['la_udante-ud-train.conllu'],
            'UDante/' + 'la_udante-ud-dev.conllu': RAW_HASHES['la_udante-ud-dev.conllu'],
            'UDante/README.md': sha(source_dir / 'README.md'), 'src/source_context_audit.py': sha(Path(__file__))},
        'primary_source': {'repository': 'https://github.com/UniversalDependencies/UD_Latin-UDante.git',
            'commit': 'e02420457780c6fbb503ba39a7d8798ab6a8645c', 'license': 'CC BY-NC-SA 3.0'}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, default=BASE / 'runtime/udante_source')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = audit(args.source_dir)
    target = BASE / 'artifacts/SOURCE_CONTEXT.json'
    data = (json.dumps(result, indent=2, sort_keys=True) + '\n').encode()
    if args.check:
        if target.read_bytes() != data:
            raise ValueError('Source-context artifact replay mismatch')
    else:
        target.write_bytes(data)
    print(json.dumps({'status': result['status'], 'discovery_occurrences': len(result['discovery_occurrences']),
        'raw_UD_syntactic_token_counts': result['raw_UD_syntactic_token_counts'],
        'annotation_join_status': result['annotation_join_status'],
        'no_likelihood_scoring_fitting_or_collision_inspection': True}, sort_keys=True))


if __name__ == '__main__':
    main()
