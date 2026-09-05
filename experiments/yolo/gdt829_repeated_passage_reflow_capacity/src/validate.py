#!/usr/bin/env python3
"""Independent source reconstruction for GDT829; does not import the runner.

Target values are used internally only to recognize eligibility, then discarded.
The published validation contains no target values or directional statistics.
"""
import argparse
import copy
import csv
import hashlib
import io
import itertools
import json
import math
import re
import subprocess
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
ROOT = EXP.parents[2]
ART = EXP / 'artifacts'
DRAWINGS = {'DRAWING_INTERRUPTION', 'DRAWING_INTERRUPTION_UNALIGNED'}
LETTERS = re.compile(r'(?:[A-Za-z]|@[0-9]+;)\Z')
FIELDS = ['occurrence_id', 'edition', 'page', 'leaf', 'locus',
          'source_group_index', 'family_id', 'body_json', 'left_json',
          'right_json', 'primary_certain']
LAYOUT_FIELDS = ['occurrence_id', 'edition', 'family_id', 'line_final', 'hand',
                 'segment_id', 'window_start', 'window_end']
PAIR_FIELDS = ['edition', 'family_id', 'occurrence_1', 'occurrence_2',
               'same_known_hand', 'primary_certain']
COMPONENT_FIELDS = ['edition', 'component_id', 'families_json', 'leaves_json',
                    'selected_pair_json']


def require(condition, label):
    if not condition:
        raise ValueError(label)


def canon(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(value).hexdigest()


def atoms(raw):
    """A stack lexer, independent of runner implementation."""
    result = []
    cursor = 0
    closes = {'[': ']', '{': '}', '<': '>'}
    while cursor < len(raw):
        start = cursor
        char = raw[cursor]
        if char == '@':
            entity = re.match(r'@[0-9]+;', raw[cursor:])
            require(entity is not None, 'Malformed extended entity')
            cursor += len(entity[0])
        elif char in closes:
            stack = [closes[char]]
            cursor += 1
            while stack and cursor < len(raw):
                char = raw[cursor]
                if char in closes:
                    stack.append(closes[char])
                elif char in closes.values():
                    require(char == stack[-1], 'Mismatched annotation delimiter')
                    stack.pop()
                cursor += 1
            require(not stack, 'Unclosed annotation')
        else:
            require(char not in closes.values(), 'Unmatched annotation closer')
            cursor += 1
        result.append(raw[start:cursor])
    return result


def as_records(source):
    grouped = defaultdict(list)
    seen = set()
    for row in source:
        require(row['source_group_id'] not in seen, 'Duplicate source group')
        seen.add(row['source_group_id'])
        grouped[(row['edition'], row['page'], row['locus'])].append(row)
    records = {}
    uniform = ['edition', 'page', 'locus', 'source_row_index', 'kind', 'hand',
               'paragraph_start', 'paragraph_end', 'source_group_count']
    for key, groups in grouped.items():
        groups.sort(key=lambda row: int(row['source_group_index']))
        size = len(groups)
        for i, row in enumerate(groups, 1):
            require(int(row['source_group_index']) == i and
                    int(row['source_group_count']) == size, 'Source group numbering')
            require(all(row[column] == groups[0][column] for column in uniform),
                    'Nonuniform source row metadata')
            require(row['source_group_id'] == f'{key[0]}|{key[2]}|G{i:03d}',
                    'Source group identifier')
            if i > 1:
                require(groups[i-2]['right_separator'] == row['left_separator'],
                        'Asymmetric source separator')
        require(groups[0]['left_separator'] == 'LINE_START' and
                groups[-1]['right_separator'] == 'LINE_END', 'Source line endpoints')
        metadata = {column: groups[0][column] for column in uniform}
        metadata['groups'] = groups
        records[key] = metadata
    return records


def numeric_locus(record):
    match = re.fullmatch(re.escape(record['page']) + r'\.([0-9]+)', record['locus'])
    return int(match[1]) if match else None


def consecutive(a, b):
    ai, bi = numeric_locus(a), numeric_locus(b)
    return (a['page'] == b['page'] and ai is not None and bi == ai + 1 and
            int(b['source_row_index']) == int(a['source_row_index']) + 1)


def scaffold(records):
    """First bounded parent paragraphs, then maximal contiguous P runs."""
    pages = defaultdict(list)
    for (edition, page, _), row in records.items():
        if edition == 'ZL3b':
            pages[page].append(row)
    bounded = []
    for page in sorted(pages):
        pending = None
        for row in sorted(pages[page], key=lambda item: int(item['source_row_index'])):
            if row['paragraph_start'] == '1':
                pending = []
            if pending is not None:
                pending.append(row)
                if row['kind'] == 'P' and row['paragraph_end'] == '1':
                    bounded.append(pending)
                    pending = None
    segments = []
    for parent in bounded:
        run = []
        for row in parent:
            if row['kind'] != 'P' or numeric_locus(row) is None:
                if run:
                    segments.append(run)
                run = []
                continue
            if run and not consecutive(run[-1], row):
                segments.append(run)
                run = []
            run.append(row)
        if run:
            segments.append(run)
    return segments, len(bounded)


def alternate_segments(segments, records, edition):
    admitted = []
    disagreement = 0
    dropped = 0
    for segment in segments:
        rows = [records.get((edition, row['page'], row['locus'])) for row in segment]
        if (any(row is None or row['kind'] != 'P' for row in rows) or
                any(not consecutive(a, b) for a, b in zip(rows, rows[1:]))):
            dropped += 1
            continue
        disagreement += sum((a['paragraph_start'], a['paragraph_end']) !=
                            (b['paragraph_start'], b['paragraph_end'])
                            for a, b in zip(segment, rows))
        admitted.append(rows)
    return admitted, dropped, disagreement


def drawing_split(segment):
    blocks = []
    pending = []
    for row in segment:
        for group in row['groups']:
            if group['left_separator'] in DRAWINGS:
                if pending:
                    blocks.append(pending)
                pending = []
            pending.append(group)
    if pending:
        blocks.append(pending)
    return blocks


def encode_block(groups):
    tokens = []
    targets = []
    for i, group in enumerate(groups):
        if i:
            separator = group['left_separator']
            require(separator in {'LINE_START', 'DEFINITE_SPACE', 'UNCERTAIN_SMALL_SPACE'},
                    'Unexpected unsplit separator')
            tokens.append(['g', 'UNCERTAIN_SMALL_SPACE' if
                           separator == 'UNCERTAIN_SMALL_SPACE' else 'GAP'])
        parsed = atoms(group['ivtff_group_raw'])
        require(parsed, 'Empty source group')
        tokens.extend(['a', atom] for atom in parsed)
        if len(parsed) > 1 and parsed[-1] in {'l', 'm'}:
            # Never retain which ending was observed.
            targets.append((len(tokens) - 1, parsed[:-1], group))
    return tokens, targets


def flank(tokens, position, direction, length):
    cursor = position + direction
    count = 0
    indices = []
    while 0 <= cursor < len(tokens) and count < length:
        indices.append(cursor)
        count += tokens[cursor][0] == 'a'
        cursor += direction
    if count != length:
        return None
    return sorted(indices)


def certain(signature):
    return (all(LETTERS.fullmatch(atom) for atom in signature['body']) and
            all((LETTERS.fullmatch(value) if kind == 'a' else value == 'GAP')
                for kind, value in signature['left'] + signature['right']))


def reconstruct(source, spec):
    records = as_records(source)
    zl_segments, parent_count = scaffold(records)
    census, layouts = {}, {}
    metrics = {'bounded_zl_paragraphs': parent_count,
               'zl_scaffold_segments': len(zl_segments), 'editions': {}}
    for edition in spec['editions']:
        segments, dropped, disagreement = alternate_segments(zl_segments, records, edition)
        blocks = [block for segment in segments for block in drawing_split(segment)]
        metrics['editions'][edition] = dict(segments_retained=len(segments),
                                           segments_dropped=dropped,
                                           alternate_flag_disagreements=disagreement,
                                           drawing_split_segments=len(blocks))
        for groups in blocks:
            segment_id = (edition + ':' + groups[0]['source_group_id'] + '--' +
                          groups[-1]['source_group_id'])
            tokens, candidates = encode_block(groups)
            for target, body, group in candidates:
                left = flank(tokens, target, -1, spec['flank_atoms'])
                right = flank(tokens, target, 1, spec['flank_atoms'])
                if left is None or right is None:
                    continue
                signature = dict(body=body, left=[tokens[i] for i in left],
                                 right=[tokens[i] for i in right])
                family = digest(canon(signature).encode())
                oid = group['source_group_id']
                leaf_match = re.match(r'f[0-9]+', group['page'])
                require(leaf_match is not None, 'Unrecognized physical leaf')
                require(oid not in census, 'Repeated occurrence across scaffold segments')
                census[oid] = dict(occurrence_id=oid, edition=edition,
                                  page=group['page'], leaf=leaf_match[0],
                                  locus=group['locus'],
                                  source_group_index=group['source_group_index'],
                                  family_id=family, body_json=canon(body),
                                  left_json=canon(signature['left']),
                                  right_json=canon(signature['right']),
                                  primary_certain=str(int(certain(signature))))
                layouts[oid] = dict(occurrence_id=oid, edition=edition, family_id=family,
                                    line_final=str(int(group['right_separator'] == 'LINE_END')),
                                    hand=group['hand'], segment_id=segment_id,
                                    window_start=str(left[0]), window_end=str(right[-1]))
    return census, layouts, metrics


def expected_families(census):
    groups = defaultdict(list)
    for row in census.values():
        groups[(row['edition'], row['family_id'])].append(row['occurrence_id'])
    return {key: sorted(ids) for key, ids in groups.items() if len(ids) >= 2}


def same_hand(first, second, spec):
    return (first == second and first not in spec['known_hand_exclusions'])


def derive_pairs(census, layouts, families, spec):
    pairs = []
    for (edition, family), ids in sorted(families.items()):
        for first, second in itertools.combinations(ids, 2):
            if layouts[first]['line_final'] == layouts[second]['line_final']:
                continue
            pairs.append(dict(edition=edition, family_id=family,
                              occurrence_1=first, occurrence_2=second,
                              same_known_hand=str(int(same_hand(layouts[first]['hand'],
                                                                layouts[second]['hand'], spec))),
                              primary_certain=str(int(census[first]['primary_certain'] ==
                                                       census[second]['primary_certain'] == '1'))))
    return pairs


def derive_components(census, families, pairs, spec):
    components = []
    for edition in spec['editions']:
        edition_families = sorted(family for ed, family in families if ed == edition)
        parent = {family: family for family in edition_families}
        def find(family):
            while parent[family] != family:
                parent[family] = parent[parent[family]]
                family = parent[family]
            return family
        leaf_owner = {}
        for family in edition_families:
            for oid in families[(edition, family)]:
                leaf = census[oid]['leaf']
                if leaf in leaf_owner:
                    one, two = find(family), find(leaf_owner[leaf])
                    parent[max(one, two)] = min(one, two)
                else:
                    leaf_owner[leaf] = family
        groups = defaultdict(list)
        for family in edition_families:
            groups[find(family)].append(family)
        for number, family_group in enumerate(sorted(groups.values()), 1):
            leaves = sorted({census[oid]['leaf'] for family in family_group
                             for oid in families[(edition, family)]})
            eligible = sorted([row['family_id'], row['occurrence_1'], row['occurrence_2']]
                              for row in pairs if row['edition'] == edition and
                              row['family_id'] in family_group and
                              row['same_known_hand'] == row['primary_certain'] == '1')
            components.append(dict(edition=edition, component_id=f'{edition}:C{number:04d}',
                                   families_json=canon(family_group), leaves_json=canon(leaves),
                                   selected_pair_json=canon(eligible[0] if eligible else [])))
    return components


def exact_power(n):
    """Rational sign-test rejection and power; no floating-point tail decision."""
    null = [Fraction(math.comb(n, k), 2**n) for k in range(n + 1)]
    rejection = []
    for k in range(n + 1):
        two_sided = min(Fraction(1), 2 * sum(null[:min(k, n-k) + 1]))
        if two_sided <= Fraction(1, 100):
            rejection.append(k)
    size = sum(null[k] for k in rejection)
    power = sum(Fraction(math.comb(n, k) * 4**k, 5**n) for k in rejection)
    return rejection, size, power


def synthetic_rows(lines, page='f1r', edition='ZL3b', numbers=None, row_numbers=None,
                   kinds=None, flags=None, hand='1'):
    """Each line is a list of (raw_group, separator_after) fixture tuples."""
    rows = []
    numbers = numbers or list(range(1, len(lines) + 1))
    row_numbers = row_numbers or list(range(1, len(lines) + 1))
    kinds = kinds or ['P'] * len(lines)
    flags = flags or [('1' if i == 0 else '0', '1' if i == len(lines)-1 else '0')
                      for i in range(len(lines))]
    for index, groups in enumerate(lines):
        locus = f'{page}.{numbers[index]}'
        for gi, (raw, after) in enumerate(groups):
            rows.append(dict(source_group_id=f'{edition}|{locus}|G{gi+1:03d}',
                             edition=edition, page=page, locus=locus, kind=kinds[index],
                             hand=hand, paragraph_start=flags[index][0],
                             paragraph_end=flags[index][1],
                             source_row_index=str(row_numbers[index]),
                             source_group_index=str(gi+1), source_group_count=str(len(groups)),
                             left_separator='LINE_START' if gi == 0 else groups[gi-1][1],
                             right_separator='LINE_END' if gi == len(groups)-1 else after,
                             ivtff_group_raw=raw))
    return rows


def self_tests(spec):
    tests = {}
    tests['opaque_entity_and_nested_annotation'] = (
        atoms('a@152;b[x{q}:y]c') == ['a', '@152;', 'b', '[x{q}:y]', 'c'])
    malformed = ['@152', '[a', 'a]', '[{x]}', '<a}']
    rejected = 0
    for raw in malformed:
        try:
            atoms(raw)
        except ValueError:
            rejected += 1
    tests['malformed_atom_rejection'] = rejected == len(malformed)
    fixture_spec = dict(spec, editions=['ZL3b'])
    # The target occurs after exactly twelve preceding letters and before twelve
    # following letters. Both observed fixture endings are deliberately unchanged.
    inline = synthetic_rows([[('abcdefghijkl', 'DEFINITE_SPACE'), ('qrstuvwxyl', 'DEFINITE_SPACE'),
                              ('nopqrstuvwxy', 'LINE_END')]])
    reflow = synthetic_rows([[('abcdefghijkl', 'DEFINITE_SPACE'), ('qrstuvwxyl', 'LINE_END')],
                             [('nopqrstuvwxy', 'LINE_END')]], page='f2r')
    first, lay_first, _ = reconstruct(inline, fixture_spec)
    second, lay_second, _ = reconstruct(reflow, fixture_spec)
    first_target = next(row for row in first.values() if row['source_group_index'] == '2')
    second_target = next(row for row in second.values() if row['source_group_index'] == '2')
    tests['definite_gap_equals_admissible_reflow_gap'] = first_target['family_id'] == second_target['family_id']
    merged = first | second
    layout = lay_first | lay_second
    families = expected_families(merged)
    pairs = derive_pairs(merged, layout, families, fixture_spec)
    tests['unchanged_ending_pair_retained'] = len(pairs) == 1
    uncertain = copy.deepcopy(inline)
    uncertain[1]['right_separator'] = uncertain[2]['left_separator'] = 'UNCERTAIN_SMALL_SPACE'
    changed, _, _ = reconstruct(uncertain, fixture_spec)
    changed_target = next(row for row in changed.values() if row['source_group_index'] == '2')
    tests['uncertain_gap_distinct_and_nonprimary'] = (
        changed_target['family_id'] != first_target['family_id'] and changed_target['primary_certain'] == '0')
    entity = copy.deepcopy(inline)
    entity[1]['ivtff_group_raw'] = 'qrstuvwx@152;l'
    entity_census, _, _ = reconstruct(entity, fixture_spec)
    entity_target = next(row for row in entity_census.values() if row['source_group_index'] == '2')
    tests['extended_entity_not_ascii_split'] = (
        '@152;' in json.loads(entity_target['body_json']) and entity_target['primary_certain'] == '1')
    barrier_results = []
    for variant in ['paragraph', 'numeric_locus', 'source_row', 'label', 'drawing']:
        fixture = copy.deepcopy(reflow)
        if variant == 'paragraph':
            for row in fixture:
                row['paragraph_start'] = row['paragraph_end'] = '1'
        elif variant == 'numeric_locus':
            for row in fixture:
                if row['locus'] == 'f2r.2':
                    row['locus'] = 'f2r.4'
                    row['source_group_id'] = 'ZL3b|f2r.4|G001'
        elif variant == 'source_row':
            fixture[-1]['source_row_index'] = '4'
        elif variant == 'label':
            fixture[-1]['kind'] = 'L'
        else:
            fixture = copy.deepcopy(inline)
            fixture[1]['right_separator'] = fixture[2]['left_separator'] = 'DRAWING_INTERRUPTION'
        values, _, _ = reconstruct(fixture, fixture_spec)
        barrier_results.append(not any(row['source_group_index'] == '2' for row in values.values()))
    tests['paragraph_numeric_source_label_drawing_barriers'] = all(barrier_results)
    no_boundaries = copy.deepcopy(inline)
    for row in no_boundaries:
        row['paragraph_start'] = row['paragraph_end'] = '0'
    tests['unbounded_paragraph_excluded'] = not reconstruct(no_boundaries, fixture_spec)[0]
    alt = synthetic_rows([[('abcdefghijkl', 'DEFINITE_SPACE'), ('qrstuvwxyl', 'LINE_END')],
                           [('nopqrstuvwxy', 'LINE_END')]], page='f2r', edition='IT2a',
                          row_numbers=[7, 9])
    combined_spec = dict(spec, editions=['ZL3b', 'IT2a'])
    combined, _, _ = reconstruct(reflow + alt, combined_spec)
    tests['alternate_nonconsecutive_segment_excluded'] = all(row['edition'] == 'ZL3b' for row in combined.values())
    # Disjoint contexts sharing recto/verso of a leaf must form one block.
    fake_census = {}
    fake_families = {}
    for family, pages in [('a', ['f10r', 'f11r']), ('b', ['f10v', 'f12r']),
                           ('c', ['f12v2', 'f13r'])]:
        ids = []
        for index, page in enumerate(pages):
            oid = family + str(index)
            ids.append(oid)
            fake_census[oid] = dict(leaf=re.match(r'f[0-9]+', page)[0])
        fake_families[('ZL3b', family)] = ids
    comps = derive_components(fake_census, fake_families, [], fixture_spec)
    tests['sameleaf_sides_panels_and_transitive_clustering'] = (
        len(comps) == 1 and json.loads(comps[0]['families_json']) == ['a', 'b', 'c'])
    n32 = exact_power(32)
    n33 = exact_power(33)
    tests['exact_power_32_vs_33'] = (
        n32[0] == list(range(9)) + list(range(24, 33)) and
        n32[2] >= Fraction(4, 5) and n33[2] < Fraction(4, 5) and
        all(exact_power(n)[2] < Fraction(4, 5) for n in range(1, 32)))
    require(all(tests.values()), 'Synthetic control failure: ' + ','.join(k for k, v in tests.items() if not v))
    return tests


def query(spec):
    command = ['./vmanus-exp', 'query-tsv', spec['source_atlas'], '--selector', 'page']
    for selector in spec['allowed_selectors']:
        command += ['--allow', selector]
    command += ['--columns', ','.join(spec['columns']), '--forbid-prefix', 'f84', '--forbid-prefix', 'f84r']
    process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=True)
    stats = [json.loads(line[12:]) for line in process.stderr.splitlines() if line.startswith('GUARD_STATS ')]
    reader = csv.DictReader(io.StringIO(process.stdout), delimiter='\t')
    require(reader.fieldnames == spec['columns'] and len(stats) == 1, 'Guarded source schema/stats')
    rows = list(reader)
    require(len(rows) == stats[0]['selected'], 'Guarded source selection count')
    require(all(row['page'] in spec['allowed_selectors'] and not row['page'].startswith('f84')
                for row in rows), 'Guarded source admission')
    return rows, dict(command=command, stats=stats[0],
                     projection_sha256=digest(process.stdout.encode()))


def table(name, fields):
    with (ART / name).open(newline='') as stream:
        reader = csv.DictReader(stream, delimiter='\t')
        require(reader.fieldnames == fields, 'Artifact schema: ' + name)
        rows = list(reader)
    for row in rows:
        require(None not in row and all(value is not None for value in row.values()),
                'Artifact malformed TSV: ' + name)
        for key in row:
            if key.endswith('_json'):
                row[key] = canon(json.loads(row[key]))
    return rows


def equal_rows(observed, expected, label):
    require(Counter(canon(row) for row in observed) == Counter(canon(row) for row in expected), label)


def validate(spec, tests):
    source, guard = query(spec)
    census, layouts, metrics = reconstruct(source, spec)
    families = expected_families(census)
    recurrent_ids = {oid for ids in families.values() for oid in ids}
    pairs = derive_pairs(census, layouts, families, spec)
    components = derive_components(census, families, pairs, spec)
    expected = {'MASKED_OCCURRENCES.tsv': (FIELDS, list(census.values())),
                'RECURRENT_CONTEXTS.tsv': (FIELDS, [census[oid] for oid in recurrent_ids]),
                'LAYOUT.tsv': (LAYOUT_FIELDS, [layouts[oid] for oid in recurrent_ids]),
                'PAIRS.tsv': (PAIR_FIELDS, pairs),
                'COMPONENTS.tsv': (COMPONENT_FIELDS, components)}
    for name, (fields, rows) in expected.items():
        equal_rows(table(name, fields), rows, 'Independent source reconstruction: ' + name)
    freeze = json.loads((ART / 'MASKED_FREEZE.json').read_text())
    hashes = {name: digest((ART / name).read_bytes()) for name in
              ['MASKED_OCCURRENCES.tsv', 'RECURRENT_CONTEXTS.tsv']}
    require(freeze['selection_hashes'] == hashes and
            freeze['target_outcomes_exposed'] is False and
            freeze['line_finality_exposed'] is False, 'Masked inventory byte freeze')
    registration_hashes = {
        str(path.relative_to(ROOT)): digest(path.read_bytes())
        for path in [EXP / 'PREREGISTRATION.md', EXP / 'src/SPEC.json']}
    require(freeze['preregistration_hashes'] == registration_hashes,
            'Current specification and preregistration match extraction lock')
    capacity = {edition: sum(row['edition'] == edition and
                             bool(json.loads(row['selected_pair_json'])) for row in components)
                for edition in spec['editions']}
    result = json.loads((ART / 'RESULT.json').read_text())
    require(result.get('experiment_id') == 'GDT829', 'Result identity')
    require(result['source_groups'] == len(source) and
            result['source_records'] == len(as_records(source)), 'Result source coverage')
    require(result['guarded_query'] == guard, 'Result guarded provenance')
    require(result['selection_hashes'] == hashes, 'Result selection hashes')
    require(result['target_outcomes_exposed'] is False and
            result['direction_test_run'] is False and
            result['new_admissions'] == result['confirmed_lexemes'] == 0 and
            result['sealed_data'] == spec['sealed_data'] and
            result['alternate_readings_independent'] is False, 'Result claim ceiling')
    require(set(result['by_edition']) == set(spec['editions']), 'Result edition scope')
    expected_counts = {}
    for edition in spec['editions']:
        expected_counts[edition] = dict(
            masked_occurrences=sum(row['edition'] == edition for row in census.values()),
            recurrent_families=sum(ed == edition for ed, _ in families),
            recurrent_occurrences=sum(census[oid]['edition'] == edition for oid in recurrent_ids),
            cross_layout_pairs=sum(row['edition'] == edition for row in pairs),
            same_known_hand_certain_pairs=sum(row['edition'] == edition and
                                             row['same_known_hand'] == row['primary_certain'] == '1'
                                             for row in pairs),
            components=sum(row['edition'] == edition for row in components),
            independent_primary_upper_bound=capacity[edition])
        require(all(result['by_edition'][edition].get(key) == value
                    for key, value in expected_counts[edition].items()), 'Result edition counts')
        expected_status = ('CAPACITY_FAIL_UPPER_BOUND' if capacity[edition] < 32
                           else 'POTENTIALLY_FEASIBLE_ONLY')
        require(result['by_edition'][edition]['status'] == expected_status,
                'Edition upper-bound capacity status')
    require(result['status'] == result['by_edition']['ZL3b']['status'] and
            result['stage'] == spec['stage'], 'Primary-only aggregate status and stage')
    return dict(experiment_id='GDT829', validator='INDEPENDENT_SOURCE_RECONSTRUCTION',
                status='PASS', source_projection_sha256=guard['projection_sha256'],
                source_projected_groups=len(source), masked_occurrences=len(census),
                recurrent_context_families=len(families), recurrent_occurrences=len(recurrent_ids),
                cross_layout_pairs=len(pairs), components=len(components),
                primary_capacity_upper_bounds_by_edition=capacity,
                verified_edition_counts=expected_counts,
                independently_reconstructed_scaffold=metrics,
                masked_file_sha256=hashes, synthetic_controls=tests,
                target_value_column_or_directional_statistics_emitted=False,
                cryptographic_blinding=False,
                limitations=[
                    'Reconstructs the registered atlas projection; does not independently reread manuscript images or prove the human atlas correct.',
                    'Physical-leaf components are conservative dependency blocks, not proof of statistical independence.',
                    'Current files can verify the byte freeze; chronology is established by versioned preregistration and the runner protocol, not by hashes alone.',
                    'Masking is procedural: overlapping flanks and source identifiers can allow target recovery, and historical source exposure is not erased.',
                    'No target direction test, language, meaning, allography or semantic relation is validated.'
                ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--self-test', action='store_true', help='Synthetic fixtures only; no source access')
    group.add_argument('--check', action='store_true', help='Read-only full reconstruction')
    args = parser.parse_args()
    spec = json.loads((EXP / 'src/SPEC.json').read_text())
    require(spec['experiment_id'] == 'GDT829' and spec['flank_atoms'] == 12 and
            spec['sealed_data'] == ['f84', 'f84r'] and len(spec['allowed_selectors']) == 179,
            'Registered design/scope')
    tests = self_tests(spec)
    if args.self_test:
        print(json.dumps(dict(status='PASS', synthetic_controls=tests), sort_keys=True))
        return
    validation = validate(spec, tests)
    if not args.check:
        (ART / 'VALIDATION.json').write_text(json.dumps(validation, indent=2, sort_keys=True) + '\n')
    print(json.dumps(validation, sort_keys=True))


if __name__ == '__main__':
    main()
