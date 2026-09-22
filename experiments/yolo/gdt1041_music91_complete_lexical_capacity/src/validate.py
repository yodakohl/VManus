"""Independent exact-type-set reconstruction; no runner or semantic imports.

Authored without decoding the target paragraph cache. Execution requires the
public registration receipt and the runner artifacts. Known source hashes are
checked before the owned, scope-proven paragraph projection is decoded.
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess

E = Path(__file__).resolve().parents[1]
R = E.parents[2]
A = E / 'artifacts'
CACHE_PATH = 'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json'
CACHE_SHA256 = '667ca3ae0705a6bb3ccfcd09ea7ee04e28747e58d810e8fa9379f28c0f4fc89b'
LEXICON_PATH = 'research_registry/proposals/f83r_embedded_music_pair_20260922/FROZEN_LEXICON.json'
LEXICON_SHA256 = '06d70911d4392c2b2881df7b297670ce767f2792a42f1b8bb38879d482197d32'
EXPECTED_READERS = {'ZL3b': 659, 'IT2a': 690, 'RF1b': 0}
DEVELOPMENT_LEAVES = frozenset((76, 83))


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def same(actual, expected, label):
    if actual != expected:
        raise AssertionError(label)


def physical_leaf(page):
    match = re.fullmatch(r'f(\d+)[rv]\d*', page)
    if not match:
        raise AssertionError('unrecognized page selector: ' + str(page))
    leaf = int(match.group(1))
    if leaf == 84 or page.startswith('f116v'):
        raise AssertionError('closed page in purported owned source')
    return leaf


def reconstruct(paragraph, vocabulary):
    """Index all occurrences first, then use type-set difference/intersection."""
    if not paragraph['lines']:
        raise AssertionError('complete paragraph has no native lines')
    same(paragraph['lines'][0]['start'], True, 'native paragraph starts')
    same(paragraph['lines'][-1]['end'], True, 'native paragraph ends')
    occurrence_index = defaultdict(list)
    position = 0
    loci = []
    flags = []
    for line in paragraph['lines']:
        same(line['offset'], position, 'native source offset')
        same(line['locus'].rsplit('.', 1)[0], paragraph['page'], 'line page agrees with paragraph')
        words, ids = line['words'], line['source_ids']
        same(len(words), len(ids), 'parallel word/source-ID lengths')
        loci.append(line['locus'])
        flags.append(line['anchor_eligible'])
        for word, source_id in zip(words, ids):
            position += 1
            occurrence_index[word].append({
                'position': position, 'source_id': source_id, 'raw': word})
    same(position, paragraph['groups'], 'source paragraph group total')
    line_numbers = [int(locus.rsplit('.', 1)[1]) for locus in loci]
    same(line_numbers, list(range(line_numbers[0], line_numbers[0] + len(line_numbers))), 'native consecutive complete lines')
    same(paragraph['id'], paragraph['page'] + '|' + loci[0] + '-' + loci[-1], 'native paragraph identity')
    word_types = set(occurrence_index)
    known_types = word_types.intersection(vocabulary)
    unknown_types = word_types.difference(vocabulary)
    unknown = sorted(
        (item for word in unknown_types for item in occurrence_index[word]),
        key=lambda item: item['position'])
    known_positions = sum(len(occurrence_index[word]) for word in known_types)
    same(known_positions + len(unknown), position, 'type-index partition covers all groups')
    leaf = physical_leaf(paragraph['page'])
    same(paragraph['leaf'], leaf, 'physical leaf derived from exact page selector')
    return {
        'groups': position, 'types': len(word_types),
        'known_groups': known_positions, 'known_types': len(known_types),
        'unknown_types': sorted(unknown_types), 'unknown': unknown,
        'strict_anchor_eligible': all(flags), 'leaf': leaf,
        'development_leaf': leaf in DEVELOPMENT_LEAVES,
        'loci': loci, 'covered': not unknown_types,
    }


def summarize(rows):
    return {
        'rows': len(rows),
        'status_counts': dict(Counter(row['status'] for row in rows)),
        'physical_leaves': sorted(set(row['leaf'] for row in rows)),
        'strict_rows': sum(bool(row['strict_anchor_eligible']) for row in rows),
        'strict_covered': sum(bool(row['strict_anchor_eligible']) and row['status'] == 'FULL_LEXICAL_CAPACITY' for row in rows),
    }


def registration_gate():
    receipt = read(A / 'PUBLIC_REGISTRATION.json')
    commit = receipt['commit']
    if not re.fullmatch('[0-9a-f]{40}', commit):
        raise AssertionError('registration must name a full commit hash')
    lock_path = E / 'PREREG_LOCK.json'
    published_lock = subprocess.check_output(
        ['git', 'show', commit + ':' + str(lock_path.relative_to(R))], cwd=R)
    same(hashlib.sha256(published_lock).hexdigest(), digest(lock_path), 'current lock equals registered commit lock')
    lock = read(lock_path)['files']
    mandatory = {CACHE_PATH, LEXICON_PATH,
                 str((E / 'src/SPEC.json').relative_to(R)),
                 str((E / 'src/validate.py').relative_to(R)),
                 str((E / 'src/ADMITTED_SELECTORS.json').relative_to(R))}
    if not mandatory.issubset(lock):
        raise AssertionError('lock lacks mandatory independent inputs/code')
    for relative, expected_hash in lock.items():
        if Path(relative).is_absolute() or '..' in Path(relative).parts:
            raise AssertionError('nonrepository lock path')
        same(digest(R / relative), expected_hash, 'locked hash: ' + relative)
    same(digest(R / CACHE_PATH), CACHE_SHA256, 'known owned paragraph cache hash')
    same(digest(R / LEXICON_PATH), LEXICON_SHA256, 'unchanged91 full-denotation hash')
    return commit


def main():
    commit = registration_gate()
    spec = read(E / 'src/SPEC.json')
    same(spec['cache'], CACHE_PATH, 'fixed source path')
    same(spec['lexicon'], LEXICON_PATH, 'fixed lexicon path')
    same(spec['development_physical_leaves'], [76, 83], 'whole development leaves')
    same(spec['expected_reader_rows'], EXPECTED_READERS, 'full owned reader counts')
    same(spec['lexicon_count'], 91, 'declared lexicon size')
    for key, expected in [('new_values', 0), ('new_rules', 0), ('semantic_execution', False),
                          ('literal_whole_forms', True), ('no_length_threshold', True)]:
        same(spec[key], expected, 'fixed specification: ' + key)
    admission = read(R / spec['admission_projection'])
    allowed = set(admission['allowed_selectors'])
    same(len(admission['allowed_selectors']), 179, 'full admission projection')
    same(len(allowed), 179, 'unique admission selectors')
    for page in allowed:
        physical_leaf(page)
    lexicon = read(R / LEXICON_PATH)
    same(len(lexicon), 91, 'actual full lexicon size')
    vocabulary = set(lexicon)

    # This is the first target-cache decode in this implementation. The gate
    # above binds an already-owned safe derivative, not a mixed legacy source.
    source = read(R / CACHE_PATH)
    same({reader: len(paragraphs) for reader, paragraphs in source.items()},
         EXPECTED_READERS, 'all1349 native rows and RF capacity metadata')
    rows = read(A / 'ROWS.json')
    result = read(A / 'RESULT.json')
    expected_rows = []
    expected_survivors = []
    all_ids = set()
    for reader, paragraphs in source.items():
        for paragraph in paragraphs:
            # Check page admission before examining this paragraph body.
            page = paragraph['page']
            if page not in allowed:
                raise AssertionError('source paragraph outside current admission')
            physical_leaf(page)
            reconstruction = reconstruct(paragraph, vocabulary)
            identity = reader + '|' + paragraph['id']
            if identity in all_ids:
                raise AssertionError('duplicate native paragraph identity')
            all_ids.add(identity)
            partition = ('DEVELOPMENT_PHYSICAL_LEAF' if reconstruction['development_leaf']
                         else 'OTHER_ADMITTED_EXPOSED_LEAF')
            row = {
                'id': identity, 'edition': reader, 'paragraph': paragraph['id'],
                'page': page, 'leaf': reconstruction['leaf'], 'partition': partition,
                'groups': reconstruction['groups'], 'types': reconstruction['types'],
                'known_groups': reconstruction['known_groups'],
                'known_types': reconstruction['known_types'],
                'unknown_types': len(reconstruction['unknown_types']),
                'unknown': reconstruction['unknown'],
                'strict_anchor_eligible': reconstruction['strict_anchor_eligible'],
                'status': 'FULL_LEXICAL_CAPACITY' if reconstruction['covered'] else 'MISSING_FIXED_VALUES',
            }
            expected_rows.append(row)
            if reconstruction['covered']:
                expected_survivors.append({
                    'id': identity, 'partition': partition, 'native_record': paragraph,
                    'semantic_status': 'NOT_ASSESSED_NO_TRANSFER_GRAMMAR'})
    same(len(expected_rows), 1349, 'complete row population')
    same(rows, expected_rows, 'all row fields and exact ordered missing positions/source IDs')
    same(read(A / 'SURVIVORS.json'), expected_survivors, 'all survivors with complete unchanged native records')
    expected_readers = {reader: summarize([row for row in expected_rows if row['edition'] == reader])
                        for reader in EXPECTED_READERS}
    expected_partitions = {partition: summarize([row for row in expected_rows if row['partition'] == partition])
                           for partition in ('DEVELOPMENT_PHYSICAL_LEAF', 'OTHER_ADMITTED_EXPOSED_LEAF')}
    covered = [row['id'] for row in expected_rows if row['status'] == 'FULL_LEXICAL_CAPACITY']
    extensions = [row['id'] for row in expected_rows
                  if row['status'] == 'FULL_LEXICAL_CAPACITY' and row['partition'] == 'OTHER_ADMITTED_EXPOSED_LEAF']
    expected_result = {
        'status': 'COMPLETE_FIXED_LEXICAL_CAPACITY', 'registration_commit': commit,
        'rows': 1349, 'readers': expected_readers, 'partitions': expected_partitions,
        'covered': covered, 'extension_survivors': extensions,
        'decision': ('RETAIN_ALL_EXPOSED_CAPACITY_UNITS_GRAMMAR_UNASSESSED' if extensions
                     else 'STOP_UNCHANGED_MUSIC91_EXTENSION_CAPACITY'),
        'semantic_execution': False, 'new_meanings': 0, 'new_productions': 0,
        'confirmed_words': 0, 'independent_meaning_capacity': 0, 'significance_claim': False,
    }
    same(set(result), set(expected_result) | {'started_utc', 'completed_utc'}, 'result schema')
    for key, value in expected_result.items():
        same(result[key], value, 'aggregate result: ' + key)
    started = datetime.fromisoformat(result['started_utc'])
    finished = datetime.fromisoformat(result['completed_utc'])
    if started.tzinfo is None or finished.tzinfo is None or finished < started:
        raise AssertionError('invalid execution timestamp order')
    committed = datetime.fromisoformat(subprocess.check_output(
        ['git', 'show', '-s', '--format=%cI', commit], cwd=R, text=True).strip())
    if started < committed:
        raise AssertionError('target execution predates registered commit')
    fields = ['id', 'edition', 'paragraph', 'page', 'leaf', 'partition', 'groups',
              'types', 'known_groups', 'unknown_groups', 'known_types', 'unknown_types',
              'strict_anchor_eligible', 'status']
    with (A / 'CANDIDATES.tsv').open(encoding='utf-8', newline='') as handle:
        table = csv.DictReader(handle, delimiter='\t')
        same(table.fieldnames, fields, 'TSV field order')
        actual_table = list(table)
    expected_table = [{key: str(len(row['unknown']) if key == 'unknown_groups' else row[key])
                       for key in fields} for row in expected_rows]
    same(actual_table, expected_table, 'complete summary TSV')
    validation = {
        'status': 'PASS', 'completed_utc': datetime.now(timezone.utc).isoformat(),
        'registration_commit': commit, 'paragraphs_checked': len(expected_rows),
        'readers_checked': EXPECTED_READERS, 'lexicon_entries': len(vocabulary),
        'physical_partition_checked': sorted(DEVELOPMENT_LEAVES),
        'covered_units': len(covered), 'extension_survivors': len(extensions),
        'method': 'Separate type-to-occurrence index and set intersection/difference; no runner import. Full literal rows, source IDs, native boundaries/offsets, admissions, reader/leaf partitions, strict flags, retained survivor records, aggregates and TSV checked.',
        'independence_limit': 'Independent implementation by a collaborating agent using the same fixed inputs; software validation, not independent semantic evidence.',
        'semantic_execution': False, 'confirmed_words': 0, 'independent_meaning_capacity': 0,
    }
    (A / 'VALIDATION.json').write_text(json.dumps(validation, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(validation, ensure_ascii=False))


if __name__ == '__main__':
    main()
