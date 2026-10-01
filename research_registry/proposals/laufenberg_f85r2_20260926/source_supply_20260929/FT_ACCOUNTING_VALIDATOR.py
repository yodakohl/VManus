#!/usr/bin/env python3
"""Frozen FT source accounting; optional author row accounting, never meaning."""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
READERS = ('ZL3b', 'IT2a', 'RF1b')
EXPECTED = {
    'FT_SOURCE_PACKET.json': '31de602d3d3a6b1c58caf5563159a3f757fe05995971f9319b769c4bbb95fa26',
    'FT_SOURCE_GROUPS.tsv': 'd72590c4350134270156f928fe4d9d377e2fac1f920bcacd2573b16f3bd80928',
    'FT_SOURCE_RECEIPT.json': 'c41d92b31060a7591225a61e71ec7d0820c809dbeb119c4417727516cb523433',
    'FT_WORD_PRIORS.json': '37eadbb4499609b9eb469be46613a72bbcb86e6234dd495ee5e3b8e3b4d6a5a9',
    'FT_WORD_PRIORS.md': '39a85c77d84cbe2c90496dd6881cb416267ea644d0b8df68eb74b9b7af752fcd',
}
COUNTS = {
    'F83_P4': (33, 32, 32), 'F83_P5': (62, 60, 63),
    'F83_Q1': (11, 11, 11), 'F83_Q2': (16, 16, 17),
    'F83_CAPTION_45': (1, 1, 1), 'F83_CAPTION_46': (1, 1, 1),
    'F83_CAPTION_50': (1, 1, 1), 'F83_CAPTION_51': (1, 1, 1),
    'F77_P2': (92, 92, 92), 'F77_OTCHDY_LABEL': (1, 1, 1),
}
MARKERS = {'DEFINITE_SPACE': '.', 'UNCERTAIN_SMALL_SPACE': ',',
           'DRAWING_INTERRUPTION': '<->', 'DRAWING_INTERRUPTION_UNALIGNED': '<~>'}
SOURCE_FIELDS = ('source_group_id', 'edition', 'locus', 'page', 'section',
                 'currier', 'hand', 'code', 'kind', 'grammar_scope',
                 'source_row_index', 'source_group_index', 'source_group_count',
                 'paragraph_start', 'paragraph_end', 'left_separator',
                 'right_separator', 'ivtff_group_raw')
FLAG_FIELDS = ('paragraph_start', 'paragraph_end', 'code', 'kind', 'grammar_scope')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ledger', action='append', default=[], metavar='AUTHOR.json',
                        help='Explicit frozen author JSON filename in this dossier; inspect row identity only.')
    parser.add_argument('--output', default='FT_ACCOUNTING_VALIDATION.json', metavar='RESULT.json',
                        help='Result filename in this dossier; choose a separate filename for author runs.')
    args = parser.parse_args()
    if Path(args.output).name != args.output or not args.output.endswith('.json') or args.output in EXPECTED or args.output in args.ledger:
        parser.error('--output must be a JSON filename in this dossier, distinct from all input files')
    checks = []
    def check(name, condition):
        checks.append({'check': name, 'passed': bool(condition)})
    hashes = {name: digest(BASE / name) for name in EXPECTED}
    for name, expected in EXPECTED.items():
        check('frozen_hash:' + name, hashes[name] == expected)
    packet = json.loads((BASE / 'FT_SOURCE_PACKET.json').read_text())
    receipt = json.loads((BASE / 'FT_SOURCE_RECEIPT.json').read_text())
    with (BASE / 'FT_SOURCE_GROUPS.tsv').open(newline='') as stream:
        table = list(csv.DictReader(stream, delimiter='\t'))
    contexts = packet['contexts']
    source = {g['source_group_id']: g for c in contexts for g in c['groups']}
    expected_loci = {f'f83r.{n}' for n in range(25, 56)} | {f'f77r.{n}' for n in range(25, 38)} | {'f77r.49'}
    check('receipt_packet_hash', receipt['packet_sha256'] == EXPECTED['FT_SOURCE_PACKET.json'])
    check('receipt_table_hash', receipt['groups_sha256'] == EXPECTED['FT_SOURCE_GROUPS.tsv'])
    check('655_unique_source_groups', len(source) == sum(len(c['groups']) for c in contexts) == 655)
    check('655_unique_TSV_groups', len(table) == len({g['source_group_id'] for g in table}) == 655)
    check('45_exact_loci', {g['locus'] for g in source.values()} == expected_loci == set(receipt['selected_loci']))
    check('no_sealed_or_unadmitted_page', {g['page'] for g in source.values()} == {'f77r', 'f83r'})
    check('30_exact_contexts', len(contexts) == len(COUNTS) * 3 and
          {(c['unit_id'], c['edition']) for c in contexts} == {(u, e) for u in COUNTS for e in READERS})
    by_context = {(c['unit_id'], c['edition']): c for c in contexts}
    flat = []
    for unit, expected_counts in COUNTS.items():
        for edition, expected_count in zip(READERS, expected_counts):
            ctx = by_context[(unit, edition)]
            key = unit + ':' + edition
            groups = ctx['groups']
            lines = ctx['lines']
            check('unit_count:' + key, len(groups) == ctx['literal_group_count'] == expected_count)
            check('unit_positions:' + key, [g['unit_position'] for g in groups] == list(range(1, expected_count + 1)))
            check('complete_loci:' + key, [line['locus'] for line in lines] == ctx['loci'] and ctx['missing_loci'] == [])
            line_groups = [g for line in lines for g in line['groups']]
            check('lines_equal_context_groups:' + key,
                  [{f: g[f] for f in SOURCE_FIELDS} for g in groups] == line_groups)
            for line in lines:
                gs = line['groups']
                ids = [f"{edition}|{line['locus']}|G{n:03d}" for n in range(1, len(gs) + 1)]
                label = key + ':' + line['locus']
                check('native_IDs_ordinals_count:' + label,
                      [g['source_group_id'] for g in gs] == ids and
                      [int(g['source_group_index']) for g in gs] == list(range(1, len(gs) + 1)) and
                      all(int(g['source_group_count']) == line['group_count'] == len(gs) for g in gs))
                check('native_flags:' + label, all(all(g[f] == line['flags'][f] for f in FLAG_FIELDS) for g in gs) and
                      all(g['edition'] == edition and g['locus'] == line['locus'] and g['page'] == ctx['page'] for g in gs))
                check('native_separator_seams:' + label, gs[0]['left_separator'] == 'LINE_START' and
                      gs[-1]['right_separator'] == 'LINE_END' and
                      all(a['right_separator'] == b['left_separator'] and a['right_separator'] in MARKERS for a, b in zip(gs, gs[1:])))
                body = ''.join(g['ivtff_group_raw'] + MARKERS.get(g['right_separator'], '') for g in gs)
                check('verbatim_body:' + label, body == line['ivtff_body_reconstructed_from_verbatim_groups'])
                if edition == 'ZL3b':
                    native = line['native_zl_line']
                    raw = native['ivtff_raw']
                    check('native_ZL_row_flags_body:' + label,
                          raw.replace('<%>', '').replace('<$>', '') == body and
                          str(int('<%>' in raw)) == native['paragraph_start'] == gs[0]['paragraph_start'] and
                          str(int('<$>' in raw)) == native['paragraph_end'] == gs[0]['paragraph_end'] and
                          all(native[f] == gs[0][f] for f in ('page', 'locus', 'code', 'kind')))
            check('native_boundary_lists:' + key,
                  ctx['native_paragraph_start_loci'] == [l['locus'] for l in lines if l['flags']['paragraph_start'] == '1'] and
                  ctx['native_paragraph_end_loci'] == [l['locus'] for l in lines if l['flags']['paragraph_end'] == '1'])
            for group in groups:
                flat.append({'unit_id': unit, 'scope': ctx['scope'], **group})
    check('TSV_exact_all_fields_and_order', [{k: str(v) for k, v in row.items()} for row in flat] == table)
    totals = {e: sum(len(c['groups']) for c in contexts if c['edition'] == e and c['scope'] == 'FT_PRIMARY_LOWER_COUPLED') for e in READERS}
    predecessors = {e: sum(len(c['groups']) for c in contexts if c['edition'] == e and c['scope'] != 'FT_PRIMARY_LOWER_COUPLED') for e in READERS}
    check('literal_primary_126_123_127', totals == {'ZL3b': 126, 'IT2a': 123, 'RF1b': 127})
    check('predecessor_93_each', predecessors == dict.fromkeys(READERS, 93))
    flag_counts = {e: {f: sum(l['flags'][f] == '1' for c in contexts if c['edition'] == e for l in c['lines']) for f in ('paragraph_start', 'paragraph_end')} for e in READERS}
    check('native_boundary_counts_not_imputed', flag_counts == {
        'ZL3b': {'paragraph_start': 5, 'paragraph_end': 5},
        'IT2a': {'paragraph_start': 4, 'paragraph_end': 4},
        'RF1b': {'paragraph_start': 0, 'paragraph_end': 0}})
    captions = {(c['unit_id'], c['edition']): c['groups'][0]['ivtff_group_raw'] for c in contexts if c['record_kind'] == 'LABEL'}
    check('native_caption50_variants', tuple(captions[('F83_CAPTION_50', e)] for e in READERS) == ('sasoldal', 'saroldal', 's@221;roldal'))
    check('other_captions_and_predecessor_label_exact', all(all(captions[(u, e)] == form for e in READERS) for u, form in {
        'F83_CAPTION_45': 'chtorol', 'F83_CAPTION_46': 'olsaiin',
        'F83_CAPTION_51': 'darolsy', 'F77_OTCHDY_LABEL': 'otchdy'}.items()))
    # Repeated whole forms index source identities only, not meanings.
    repeat_index = {e: {form: [g['source_group_id'] for c in contexts if c['edition'] == e for g in c['groups'] if g['ivtff_group_raw'] == form]
                       for form in sorted({g['ivtff_group_raw'] for c in contexts if c['edition'] == e for g in c['groups']})}
                    for e in READERS}
    ledger_results = []
    for name in args.ledger:
        if Path(name).name != name or not name.endswith('.json'):
            parser.error('--ledger accepts a JSON filename in this dossier only')
        doc = json.loads((BASE / name).read_text())
        roots = [doc[k] for k in ('rows', 'group_ledger', 'source_group_ledger', 'primary_rows',
                 'alternate_rows', 'predecessor_rows', 'alternatives', 'primary_ledger',
                 'alternative_ledger', 'predecessor_ledger', 'ledger', 'ledgers') if k in doc]
        identities = []
        def extract(node):
            if isinstance(node, list):
                for item in node: extract(item)
            elif isinstance(node, dict):
                sid = node.get('source_group_id', node.get('ID', node.get('id')))
                raw = node.get('ivtff_group_raw', node.get('raw', node.get('form')))
                if isinstance(sid, str) and isinstance(raw, str):
                    identities.append((sid, raw))
                else:
                    for value in node.values():
                        if isinstance(value, (list, dict)): extract(value)
        for root in roots: extract(root)
        ids = [sid for sid, _ in identities]
        prefix = 'author_row_accounting:' + name + ':'
        check(prefix + '655_unique_complete_IDs', len(ids) == len(set(ids)) == 655 and set(ids) == set(source))
        check(prefix + 'exact_raw_wholes', all(sid in source and raw == source[sid]['ivtff_group_raw'] for sid, raw in identities))
        check(prefix + 'native_order_within_unit_and_reader', all(
            [sid for sid in ids if sid in {g['source_group_id'] for g in ctx['groups']}] == [g['source_group_id'] for g in ctx['groups']] for ctx in contexts))
        observed_index = {e: {form: [sid for sid, raw in identities if sid in source and source[sid]['edition'] == e and raw == form] for form in repeat_index[e]} for e in READERS}
        check(prefix + 'repeat_whole_ID_sets', all(set(observed_index[e][f]) == set(wanted) for e, forms in repeat_index.items() for f, wanted in forms.items()))
        declared = doc.get('shared_packet_sha256', doc.get('source_packet_sha256', doc.get('target_sha256')))
        check(prefix + 'declared_packet_hash', declared == EXPECTED['FT_SOURCE_PACKET.json'])
        ledger_results.append({'file': name, 'sha256': digest(BASE / name), 'recognized_identity_rows': len(ids),
                               'semantic_fields_inspected': False, 'schema_scope': 'recognized ledger lists; IDs/raw forms/order only'})
    errors = [c['check'] for c in checks if not c['passed']]
    result = {'status': 'PASS_SOURCE_ACCOUNTING_ONLY' if not errors else 'FAIL_ACCOUNTING',
              'source_hashes': hashes, 'validator_sha256': digest(Path(__file__)),
              'counts': {'source_groups': len(source), 'loci': len(expected_loci), 'primary': totals, 'predecessors': predecessors, 'native_boundary_flags': flag_counts},
              'checks': checks, 'errors': errors, 'author_ledgers': ledger_results,
              'whole_repeat_ID_index': repeat_index,
              'semantic_validation': False, 'grammar_execution_validation': False,
              'independent_meaning_confirmation': False,
              'limits': 'Frozen source identities, raw groups, separators, flags, and authored row coverage only. No semantic prose, word meaning, state transition, image owner, parser, uniqueness of reading, null test, or translation is validated. Optional ledger PASS conserves IDs; it does not validate contribution values or execution.'}
    (BASE / args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'checks': len(checks), 'errors': errors,
                      'counts': result['counts'], 'author_ledgers': ledger_results}))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
