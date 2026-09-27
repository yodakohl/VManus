"""Reproduce the first word-selection audit; independently recount its inputs.

This is an exposed-data engineering check, not a decipherment experiment.
Run with --check to compare the published deterministic compact result.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import subprocess
from collections import Counter, defaultdict

from tools import word_profiles as profiles
from tools.word_evidence import (CATALOG, DOSSIER, ROOT, digest, load_evidence,
                                 review_contract, validate_contract)

FORMS = ('daiin', 'dar', 'aiin', 'dain', 'dair', 'qodaiin', 'qo')
RESULT = DOSSIER / 'WORD_SELECTION_RESULT.json'
WINTER = DOSSIER / 'WORD_SELECTION_WINTER.json'
CONTROLS = DOSSIER / 'WORD_SELECTION_CONTROLS.json'


def independent_recount(cards):
    """Fresh guard projection, direct counters; no profile/cache SQL reused."""
    with (ROOT / profiles.ALLOWLIST).open(newline='') as handle:
        pages = [row['page'] for row in csv.DictReader(handle, delimiter='\t')]
    if len(pages) != 179 or any(page.startswith('f84') for page in pages):
        raise ValueError('unexpected admission')
    columns = ['edition', 'page', 'locus', 'section', 'currier', 'hand', 'kind',
               'source_group_index', 'source_group_count', 'ivtff_group_raw']
    command = [str(ROOT / 'vmanus-exp'), 'query-tsv', str(profiles.SOURCE),
               '--selector', 'page', '--columns', ','.join(columns)]
    for page in pages:
        command += ['--allow', page]
    run = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    rows = list(csv.DictReader(io.StringIO(run.stdout), delimiter='\t'))
    checks = 0
    for card in cards:
        form = card['form']
        for edition, observed in card['editions'].items():
            corpus = [r for r in rows if r['edition'] == edition]
            hits = [r for r in corpus if r['ivtff_group_raw'] == form]
            vocabulary = Counter(r['ivtff_group_raw'] for r in corpus)
            lines = Counter((r['page'], r['locus']) for r in hits)
            literal = {(r['page'], r['locus'], int(r['source_group_index'])): r['ivtff_group_raw'] for r in corpus}
            positions = Counter('single' if int(r['source_group_count']) == 1 else
                                'start' if int(r['source_group_index']) == 1 else
                                'end' if r['source_group_index'] == r['source_group_count'] else 'middle'
                                for r in hits)
            expected = {
                'count': len(hits), 'total_groups': len(corpus),
                'rank': 1 + sum(n > len(hits) for n in vocabulary.values()) if hits else None,
                'pages_with_form': len({r['page'] for r in hits}),
                'pages_total': len({r['page'] for r in corpus}),
                'positions': {p: positions[p] for p in ['start', 'middle', 'end', 'single']},
                'repetition': {
                    'lines_with_form': len(lines), 'repeated_lines': sum(n > 1 for n in lines.values()),
                    'adjacent_pairs': sum(literal.get((r['page'], r['locus'], int(r['source_group_index']) + 1)) == form for r in hits),
                    'max_per_line': max(lines.values(), default=0),
                },
            }
            for key, value in expected.items():
                if observed[key] != value:
                    raise ValueError(f'independent recount mismatch: {form}/{edition}/{key}')
                checks += 1
            for field in ['section', 'currier', 'hand', 'kind']:
                totals, counts = Counter(r[field] for r in corpus), Counter(r[field] for r in hits)
                values = [{'value': value, 'count': counts[value], 'total_groups': totals[value]} for value in sorted(totals)]
                if observed['strata'][field] != values:
                    raise ValueError(f'independent stratum mismatch: {form}/{edition}/{field}')
                checks += 1
    return {'status': 'PASS_DESCRIPTIVE_RECOUNT', 'forms': len(cards),
            'separate_readers': 3, 'comparisons': checks,
            'interpretation': 'Engineering fidelity only; no grammar or meaning validation.'}


def compact_review(result):
    return {key: value for key, value in result.items() if key not in {'profiles', 'source_receipt'}}


def run_audit():
    catalog = load_evidence()
    winter = json.loads((ROOT / WINTER).read_text())
    controls = json.loads((ROOT / CONTROLS).read_text())
    binding = winter['source_packet']
    if digest(ROOT / binding['path']) != binding['sha256']:
        raise ValueError('stale original candidate binding')
    original = json.loads((ROOT / binding['path']).read_text())  # already-owned f85r2 author packet
    for assignment in winter['assignments']:
        if original['lexicon'][assignment['form']]['value'] != assignment['meaning']:
            raise ValueError('audit changed original base meaning')
    for contract in [winter, *controls]:
        validate_contract(contract)
    conn = profiles.ensure_cache()
    try:
        cards = [profiles.profile(conn, form, limit=3) for form in FORMS]
        reviewed = review_contract(conn, winter, catalog, limit=3)
        tested = [review_contract(conn, contract, catalog, limit=3) for contract in controls]
        source = profiles.receipt(conn)
    finally:
        conn.close()
    validation = independent_recount(cards)
    # Golden behavior comes from the earlier explicit counts, not a preferred gloss.
    if reviewed['surface_decision'] != 'NO_TESTABLE_PREDICTIONS' or reviewed['selection_status'] != 'NOT_READY_FOR_PREFERENCE':
        raise ValueError('free seasonal assignment was promoted')
    expected = ['CONTRADICTED_DECLARED_RULES', 'CONTRADICTED_DECLARED_RULES', 'NO_CONTRADICTION_IN_DECLARED_RULES']
    if [result['surface_decision'] for result in tested] != expected:
        raise ValueError('engineering controls did not retain declared global/local scope')
    end_only = tested[0]['predictions'][0]['by_reader']
    if {key: value['violating_occurrences'] for key, value in end_only.items()} != {'ZL3b': 601, 'IT2a': 620, 'RF1b': 518}:
        raise ValueError('known whole-prose end-only countercases changed')
    if any(result['semantic_decision'] != 'NO_AUTOMATIC_MEANING_PREFERENCE' for result in tested):
        raise ValueError('an engineering control was promoted to meaning')
    bound = [CATALOG, WINTER, CONTROLS, DOSSIER / 'WORD_SELECTION_DECISION.md',
             'tools/word_profiles.py', 'tools/word_evidence.py', 'tools/word_selection_audit.py']
    return {
        'schema_version': 1, 'status': 'ENGINEERING_AND_PRIOR_AUDIT_NO_NEW_TRANSLATION',
        'source_receipt': source,
        'bindings': {str(path): digest(ROOT / path) for path in bound},
        'profiles': cards, 'seasonal_assignment': compact_review(reviewed),
        'engineering_controls': [compact_review(result) for result in tested],
        'validation': validation,
        'decision': 'Require exposed-corpus word evidence and explicit scoped consequences before preferring new meanings. IDEA595 season bases remain ungrounded; no replacement gloss selected.',
        'limits': [
            'All inputs were already exposed; this is not prospective confirmation.',
            'The evidence catalog is a curated subset, not an exhaustive historical review.',
            'Surface counts constrain declared models, not arbitrary semantic labels.',
            'No probability, significance, source language or part of speech is inferred.',
            'Local physical-line compatibility does not generalize to other loci or sentence syntax.',
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = run_audit()
    if args.check:
        saved = json.loads((ROOT / RESULT).read_text())
        if saved != result:
            raise SystemExit('FAIL: published word-selection result differs; inspect inputs and code')
        print('PASS: exact published result and independent descriptive recount; no semantic validation')
    else:
        (ROOT / RESULT).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        print('Wrote ' + str(RESULT) + '; independent recount PASS')


if __name__ == '__main__':
    main()
