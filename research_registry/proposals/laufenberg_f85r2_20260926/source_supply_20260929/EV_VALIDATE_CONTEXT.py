#!/usr/bin/env python3
"""Reproduce guarded complete-context accounting; never validate meaning."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess

BASE = Path('research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929')
INPUT = Path('transcription/voynich_zl3b_lines.tsv')
LOCI = ['f68r1.1', 'f68r1.2', 'f68r1.3', 'f68r1.4', 'f68r1.26']
COLUMNS = 'page,locus,kind,paragraph_start,paragraph_end,token_count,eva_clean,ivtff_raw'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def reproduce():
    args = ['./vmanus-exp', 'query-tsv', str(INPUT), '--selector', 'locus']
    for locus in LOCI:
        args.extend(['--allow', locus])
    args.extend(['--columns', COLUMNS])
    response = subprocess.run(args, check=True, text=True, capture_output=True)
    rows = list(csv.DictReader(io.StringIO(response.stdout), delimiter='\t'))
    assert [r['locus'] for r in rows] == LOCI
    assert all(r['page'] == 'f68r1' for r in rows)
    assert rows[0]['paragraph_start'] == '1' and rows[3]['paragraph_end'] == '1'
    assert all(r['kind'] == 'P' for r in rows[:4]) and rows[4]['kind'] == 'L'
    source = json.loads((BASE / 'EV_SOURCE_EVENTS.json').read_text())
    cache = json.loads((BASE / 'U_PLINY_COMPLETE_PASSAGES.json').read_text())
    for section in source['sections'].values():
        actual = cache
        for key in section['source_json_pointer'].strip('/').split('/'):
            actual = actual[int(key)] if isinstance(actual, list) else actual[key]
        assert actual == section['latin']
        assert hashlib.sha256(actual.encode()).hexdigest() == section['sha256_utf8']
    spans = 0
    for constraint in source['constraints']:
        for item in constraint['evidence']:
            text = source['sections'][str(item['section'])]['latin']
            assert text[item['start_char_in_section']:item['end_char_exclusive']] == item['latin']
            spans += 1
    parent = json.loads((BASE / 'ET_F111R_AUTHOR.json').read_text())
    fixed = parent['parent_values_unchanged']
    dictionary = dict(fixed['parent32']['G']['dictionary'])
    for key in ['EQ14', 'ES13']:
        values = fixed[key]
        # Prior authored packet stores these scoped exact-whole maps directly.
        if 'dictionary' in values:
            values = values['dictionary']
        assert isinstance(values, dict)
        dictionary.update(values)
    tokens = [(r['locus'], i, token) for r in rows[:4] for i, token in enumerate(r['eva_clean'].split(), 1)]
    assert len(tokens) == sum(int(r['token_count']) for r in rows[:4]) == 28
    known = [{'locus': locus, 'position': i, 'whole': token, 'fixed_C0_value': dictionary[token]} for locus, i, token in tokens if token in dictionary]
    authored = json.loads((BASE / 'EV_PARAGRAPH_AUTHOR.json').read_text())
    assert [(r['locus'], r['position'], r['token']) for r in authored['whole_group_accounting']] == tokens
    declared_parses = [r for r in authored['whole_group_accounting'] if 'parse' in r]
    assert len(declared_parses) == 7
    assert all(''.join(r['parse']) == r['token'] for r in declared_parses)
    assert authored['source_events_sha256_unchanged'] == digest(BASE / 'EV_SOURCE_EVENTS.json')
    evidence = {
        'status': 'GUARDED_LITERAL_SOURCE_CONTEXT_REPLAY_PASS_ONLY',
        'input': str(INPUT), 'input_sha256': digest(INPUT),
        'source_events_sha256': digest(BASE / 'EV_SOURCE_EVENTS.json'),
        'prior_author_sha256': digest(BASE / 'ET_F111R_AUTHOR.json'),
        'selectors': LOCI, 'columns': COLUMNS.split(','),
        'guard_stats': response.stderr.strip(),
        'native_P_loci': LOCI[:4], 'native_P_groups': len(tokens),
        'distinct_complete_forms_in_P': len({x[2] for x in tokens}),
        'local_label': rows[4]['eva_clean'],
        'literal_label_prose_positions': [{'locus': l, 'position': i} for l, i, t in tokens if t == rows[4]['eva_clean']],
        'source_sections_verified': len(source['sections']), 'source_spans_verified': spans,
        'fixed_medical_C0_overlap': known,
        'medical_C0_unassigned_P_groups': len(tokens) - len(known),
        'local_author_sha256': digest(BASE / 'EV_PARAGRAPH_AUTHOR.json'),
        'authored_group_accounting': 28, 'exact_authored_parses_checked': 7,
        'meaning_validation': False, 'confirmed_words': 0,
        'independent_confirmation_leaves': 0,
        'scope': 'ZL3b native paragraph only; no full IT/RF inference or new admission',
    }
    return response.stdout, evidence

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    context, evidence = reproduce()
    encoded = json.dumps(evidence, ensure_ascii=False, indent=2) + '\n'
    if args.write:
        (BASE / 'EV_ACTUAL_CONTEXT.tsv').write_text(context)
        (BASE / 'EV_LITERAL_VALIDATION.json').write_text(encoded)
    else:
        assert (BASE / 'EV_ACTUAL_CONTEXT.tsv').read_text() == context
        assert (BASE / 'EV_LITERAL_VALIDATION.json').read_text() == encoded
    print(json.dumps({'status': evidence['status'], 'P_groups': evidence['native_P_groups'], 'distinct_forms': evidence['distinct_complete_forms_in_P'], 'source_spans': evidence['source_spans_verified'], 'medical_C0_overlap': evidence['fixed_medical_C0_overlap'], 'meaning_validation': False}))

if __name__ == '__main__':
    main()
