"""Descriptive word evidence and explicitly conditional candidate checks.

No decoder, inferred parts of speech, learned meanings or semantic score.
The profile cache is disposable; assessed research remains in the registry.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from tools import word_profiles

ROOT = Path(__file__).resolve().parents[1]
DOSSIER = Path('research_registry/proposals/laufenberg_f85r2_20260926')
CATALOG = DOSSIER / 'WORD_EVIDENCE.json'
OBLIGATIONS = ('distribution', 'repetition_and_position', 'constructions',
               'form_relations', 'grammar', 'meaning_discriminator')
RULES = {'allowed_kinds', 'allowed_positions', 'max_per_locus',
         'forbidden_next', 'required_previous', 'required_next'}
CEILING = (
    'Descriptive exposed-data audit. Physical lines are not sentences. '
    'A rule violation contradicts only the declared conjunction of assumptions. '
    'Compatibility, word frequency, spelling similarity and formal roles do not '
    'identify a meaning. Readers are alternatives, not independent evidence. '
    'No significance, calibrated probability or confirmed translation.'
)


def relative_file(value: str, root: Path = ROOT) -> Path:
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise ValueError('expected nonempty repository-relative path')
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError('missing or out-of-repository file: ' + value)
    return path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_evidence(root: Path = ROOT) -> dict:
    data = json.loads(relative_file(str(CATALOG), root).read_text())
    if data.get('schema_version') != 1 or not isinstance(data.get('entries'), list):
        raise ValueError('unsupported evidence catalog schema')
    ids = set()
    for entry in data['entries']:
        if entry['id'] in ids:
            raise ValueError('duplicate evidence ID: ' + entry['id'])
        ids.add(entry['id'])
        if not entry.get('forms') or not entry.get('sources'):
            raise ValueError('evidence entry lacks forms or source')
        for source in entry['sources']:
            path = relative_file(source['path'], root)
            if digest(path) != source['sha256']:
                raise ValueError('stale evidence source: ' + source['path'])
            start, end = source['line_start'], source['line_end']
            if not 1 <= start <= end <= len(path.read_text().splitlines()):
                raise ValueError('invalid evidence line range: ' + source['path'])
    return data


def evidence_for(catalog: dict, form: str) -> list[dict]:
    return [entry for entry in catalog['entries']
            if form in entry['forms'] or '*' in entry['forms']]


def word_card(conn, form: str, catalog: dict, limit: int = 8) -> dict:
    card = word_profiles.profile(conn, form, limit=limit)
    card['prior_evidence'] = evidence_for(catalog, form)
    card['history_coverage'] = 'CURATED_SUBSET_NOT_EXHAUSTIVE'
    card['further_history_commands'] = [
        './vmanus-work ideas search ' + form,
    ]
    # Existing index, no parallel registry; lexical hits are navigation only.
    from tools import research_registry
    try:
        card['history_navigation'] = research_registry.search(ROOT, form, limit=min(limit, 8))
    except (ValueError, OSError) as exc:
        card['history_navigation'] = {'status': 'UNAVAILABLE_NOT_ABSENT', 'error': str(exc)}
    card['selection_obligations'] = list(OBLIGATIONS)
    return card


def require_strings(value, label: str, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty) or any(
            not isinstance(x, str) or not x.strip() for x in value):
        raise ValueError(label + ' must be a list of nonempty strings')
    if len(value) != len(set(value)):
        raise ValueError(label + ' contains duplicates')
    return value


def validate_contract(contract: dict) -> None:
    if contract.get('schema_version') != 1:
        raise ValueError('unsupported contract schema')
    if not isinstance(contract.get('id'), str) or not contract['id'].strip():
        raise ValueError('contract ID required')
    assignments = contract.get('assignments')
    if not isinstance(assignments, list) or not assignments:
        raise ValueError('nonempty assignments required')
    forms = set()
    for assignment in assignments:
        form = assignment.get('form')
        if not isinstance(form, str) or not form.isascii() or not form.isalpha() or form != form.lower():
            raise ValueError('assignment forms must be literal lowercase ASCII groups')
        if form in forms:
            raise ValueError('duplicate assignment: ' + form)
        forms.add(form)
        if not isinstance(assignment.get('meaning'), str) or not assignment['meaning'].strip():
            raise ValueError('explicit proposed meaning required')
        accounts = assignment.get('accounts', {})
        if not isinstance(accounts, dict) or set(accounts) - set(OBLIGATIONS):
            raise ValueError('unknown account category')
        for name, account in accounts.items():
            if not isinstance(account, dict) or account.get('status') not in {'unaddressed', 'hypothesis', 'source_supported'}:
                raise ValueError('invalid account status: ' + name)
            if not isinstance(account.get('note'), str) or not account['note'].strip():
                raise ValueError('account note required: ' + name)
            if account['status'] == 'source_supported' and not account.get('sources'):
                raise ValueError('source_supported account lacks sources')
    scope = contract.get('scope', {})
    if set(scope) - {'pages', 'editions', 'kinds'}:
        raise ValueError('unknown scope key')
    for name in ('pages', 'editions', 'kinds'):
        if name in scope and not (name == 'pages' and scope[name] == 'all_admitted'):
            require_strings(scope[name], 'scope.' + name)
    if scope.get('pages') != 'all_admitted' and any(
            p.startswith('f84') for p in scope.get('pages', [])):
        raise ValueError('sealed selector requested')
    if not isinstance(contract.get('predictions', []), list):
        raise ValueError('predictions must be a list')
    ids = set()
    for rule in contract.get('predictions', []):
        rid = rule.get('id')
        if not isinstance(rid, str) or not rid.strip() or rid in ids:
            raise ValueError('prediction IDs must be nonempty and unique')
        ids.add(rid)
        if rule.get('form') not in forms or rule.get('rule') not in RULES:
            raise ValueError('unknown prediction form or rule')
        permitted = {'id', 'form', 'rule', 'strength', 'basis', 'assumptions',
                     'maximum' if rule['rule'] == 'max_per_locus' else 'values'}
        if set(rule) - permitted:
            raise ValueError('unknown prediction field')
        if rule.get('strength') not in {'necessary', 'expectation'}:
            raise ValueError('prediction strength must be necessary or expectation')
        if not isinstance(rule.get('basis'), str) or not rule['basis'].strip():
            raise ValueError('prediction needs an explicit basis')
        require_strings(rule.get('assumptions'), 'prediction assumptions')
        if rule['rule'] == 'max_per_locus':
            if type(rule.get('maximum')) is not int or rule['maximum'] < 0:
                raise ValueError('maximum must be a nonnegative integer')
        else:
            allowed = require_strings(rule.get('values'), 'prediction values')
            if rule['rule'] == 'allowed_positions' and set(allowed) - {'start', 'middle', 'end', 'single'}:
                raise ValueError('unknown physical position')
    require_strings(contract.get('reviewed_evidence_ids', []), 'reviewed_evidence_ids', True)


def selected_rows(rows: list[dict], scope: dict) -> list[dict]:
    selected = []
    for row in rows:
        if scope.get('pages', 'all_admitted') != 'all_admitted' and row['page'] not in scope['pages']:
            continue
        if 'editions' in scope and row['edition'] not in scope['editions']:
            continue
        if 'kinds' in scope and row['kind'] not in scope['kinds']:
            continue
        selected.append(row)
    return selected


def evaluate_rule(rule: dict, rows: list[dict], limit: int = 8) -> dict:
    """Evaluate every occurrence, retaining full counts and a bounded sample.

    The supplied rows already have scope filtering applied. max_per_locus
    counts independently per reader, never joins alternative readings.
    """
    per_locus = Counter((r['edition'], r['locus']) for r in rows)
    values = rule.get('values', [])
    checks = {
        'allowed_kinds': lambda r: r['kind'] in values,
        'allowed_positions': lambda r: r['position'] in values,
        'max_per_locus': lambda r: per_locus[(r['edition'], r['locus'])] <= rule.get('maximum', 0),
        'forbidden_next': lambda r: r['next_literal'] not in values,
        'required_previous': lambda r: r['previous_literal'] in values,
        'required_next': lambda r: r['next_literal'] in values,
    }
    failures = [r for r in rows if not checks[rule['rule']](r)]
    by_reader = {}
    for edition in sorted({r['edition'] for r in rows}):
        subset = [r for r in rows if r['edition'] == edition]
        bad = [r for r in failures if r['edition'] == edition]
        by_reader[edition] = {
            'tested_occurrences': len(subset), 'violating_occurrences': len(bad),
            'violating_loci': len({r['locus'] for r in bad}),
            'counterexamples': bad[:limit],
        }
    # A zero-case rule cannot pass vacuously. Reader totals are not independent N.
    status = 'NO_CAPACITY' if not rows else (
        'CONDITIONAL_CONTRADICTION' if failures and rule['strength'] == 'necessary'
        else 'EXPECTATION_MISMATCH' if failures else 'COMPATIBLE_IN_DECLARED_SCOPE')
    return {'id': rule['id'], 'form': rule['form'], 'rule': rule['rule'],
            'strength': rule['strength'], 'basis': rule['basis'],
            'assumptions': rule['assumptions'], 'status': status,
            'by_reader': by_reader,
            'counterexample_limit_per_reader': limit,
            'all_occurrences_evaluated': True}


def review_contract(conn, contract: dict, catalog: dict, limit: int = 8) -> dict:
    validate_contract(contract)
    scope = contract.get('scope', {})
    # Reject unknown selectors/editions instead of silently treating them as zero.
    actual = {key: {r[0] for r in conn.execute('SELECT DISTINCT ' + key + ' FROM groups')}
              for key in ('page', 'edition', 'kind')}
    for field, column in [('pages', 'page'), ('editions', 'edition'), ('kinds', 'kind')]:
        if field in scope and scope[field] != 'all_admitted':
            unknown = set(scope[field]) - actual[column]
            if unknown:
                raise ValueError('unavailable ' + field + ': ' + ', '.join(sorted(unknown)))
    known_ids = {entry['id'] for entry in catalog['entries']}
    acknowledged = set(contract.get('reviewed_evidence_ids', []))
    if acknowledged - known_ids:
        raise ValueError('unknown reviewed evidence IDs')
    rows_by_form, cards, obligations, missing_reviews = {}, [], {}, set()
    for assignment in contract['assignments']:
        form = assignment['form']
        rows_by_form[form] = selected_rows(word_profiles.occurrences(conn, form), scope)
        card = word_card(conn, form, catalog, limit)
        cards.append(card)
        relevant = {entry['id'] for entry in card['prior_evidence']}
        missing_reviews |= relevant - acknowledged
        accounts = assignment.get('accounts', {})
        obligations[form] = {
            'unaddressed': [name for name in OBLIGATIONS
                            if name not in accounts or accounts[name]['status'] == 'unaddressed'],
            'author_accounts': accounts,
            'account_validation': 'AUTHOR_ASSERTIONS_NOT_AUTOMATICALLY_VERIFIED',
        }
    results = [evaluate_rule(rule, rows_by_form[rule['form']], limit)
               for rule in contract.get('predictions', [])]
    if any(r['status'] == 'CONDITIONAL_CONTRADICTION' for r in results):
        surface = 'CONTRADICTED_DECLARED_RULES'
    elif not results:
        surface = 'NO_TESTABLE_PREDICTIONS'
    elif any(r['status'] == 'NO_CAPACITY' for r in results):
        surface = 'INCOMPLETE_CAPACITY'
    elif any(r['status'] == 'EXPECTATION_MISMATCH' for r in results):
        surface = 'EXPECTATION_MISMATCH'
    else:
        surface = 'NO_CONTRADICTION_IN_DECLARED_RULES'
    return {
        'schema_version': 1, 'contract_id': contract['id'],
        'purpose': contract.get('purpose', 'exploratory audit'),
        'scope': scope or {'pages': 'all_admitted'},
        'source_receipt': word_profiles.receipt(conn),
        'source_packet': contract.get('source_packet'),
        'implementation_sha256': digest(Path(__file__)),
        'evidence_catalog_sha256': digest(ROOT / CATALOG),
        'assignments': contract['assignments'],
        'profiles': cards, 'predictions': results, 'surface_decision': surface,
        'unreviewed_relevant_evidence': sorted(missing_reviews),
        'obligations': obligations,
        'semantic_decision': 'NO_AUTOMATIC_MEANING_PREFERENCE',
        'selection_status': ('NOT_READY_FOR_PREFERENCE' if
                             surface != 'NO_CONTRADICTION_IN_DECLARED_RULES' or
                             missing_reviews or any(x['unaddressed'] for x in obligations.values())
                             else 'EXPLORATORY_CANDIDATE_REQUIRES_SEMANTIC_REVIEW'),
        'claim_ceiling': CEILING,
    }


def render_card(card: dict) -> str:
    lines = ['## ' + card['form'], '',
             '| Reader | Count | Rank | Selectors | Share | Start / middle / end / single | Adjacent repeat |',
             '|---|---:|---:|---:|---:|---|---:|']
    for edition, item in card['editions'].items():
        pos = item['positions']
        share = 100 * item['count'] / item['total_groups'] if item['total_groups'] else 0
        lines.append(f"| {edition} | {item['count']} | {item['rank']} | "
                     f"{item['pages_with_form']}/{item['pages_total']} | {share:.3f}% | "
                     + ' / '.join(str(pos.get(p, 0)) for p in ['start', 'middle', 'end', 'single'])
                     + f" | {item['repetition']['adjacent_pairs']} |")
    lines += ['', 'Exact raw groups; all admitted exposed data. Line positions are physical, not syntactic.', '']
    for edition, item in card['editions'].items():
        for dimension in ('section', 'currier', 'kind'):
            counts = ', '.join(str(x['value']) + ':' + str(x['count']) + '/' + str(x['total_groups'])
                               for x in item['strata'][dimension])
            lines.append(edition + ' ' + dimension + ' (word/all groups): ' + counts)
        repeated = item['repetition']
        lines.append(f"{edition} repeated loci: {repeated['repeated_lines']}; maximum per locus: {repeated['max_per_line']}")
        for side in ('previous', 'next'):
            lines.append(edition + ' ' + side + ': ' + ', '.join(
                x['form'] + ':' + str(x['count']) for x in item['neighbors'][side]))
        lines.append(edition + ' one-edit spellings (not established morphology): ' + ', '.join(
            x['form'] + ':' + str(x['count']) for x in item['spelling_neighbors']))
    lines.append('')
    for entry in card['prior_evidence']:
        statement = entry['statement']
        if len(statement) > 165:
            statement = statement[:162] + '…'
        lines.append(f"- {entry['id']} [{entry['kind']}]: {statement}")
    if card['prior_evidence']:
        lines.append('Previews only. Before selection read full scope, dependencies, limits and sources with words evidence ID.')
    if not card['prior_evidence']:
        lines.append('No curated entry; this is NOT evidence of absent research.')
    navigation = card['history_navigation']
    lines += ['', 'Registry navigation (not reviewed evidence):']
    for hit in navigation.get('results', []):
        lines.append('- ' + hit['id'] + ' [' + hit['verdict'] + ']: ' + hit['title'])
    if navigation.get('status') == 'UNAVAILABLE_NOT_ABSENT':
        lines.append('Unavailable: ' + navigation['error'])
    lines += ['Broader history: ' + '; '.join(card['further_history_commands']), '']
    return '\n'.join(lines)


def render_review(result: dict) -> str:
    lines = ['# ' + result['contract_id'], '',
             'Surface decision: **' + result['surface_decision'] + '**',
             'Selection: **' + result['selection_status'] + '**',
             'Meaning: **' + result['semantic_decision'] + '**', '', result['claim_ceiling'], '']
    for form, entry in result['obligations'].items():
        lines.append(form + ' unresolved: ' + (', '.join(entry['unaddressed']) or 'none stated; accounts need review'))
    if result['unreviewed_relevant_evidence']:
        lines.append('Prior evidence not acknowledged: ' + ', '.join(result['unreviewed_relevant_evidence']))
    for prediction in result['predictions']:
        lines += ['', prediction['id'] + ': ' + prediction['status']]
        for edition, item in prediction['by_reader'].items():
            lines.append(f"- {edition}: {item['violating_occurrences']}/{item['tested_occurrences']} violating occurrences")
            for row in item['counterexamples']:
                lines.append('  ' + row['source_group_id'] + ': ' + str(row['previous_literal']) + ' ['
                             + row['ivtff_group_raw'] + '] ' + str(row['next_literal']))
    lines += ['', *[render_card(card) for card in result['profiles']]]
    return '\n'.join(lines) + '\n'


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog='vmanus-work words', description=CEILING)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('profile', 'review'):
        sub = commands.add_parser(name)
        sub.add_argument('forms' if name == 'profile' else 'contract', nargs='+' if name == 'profile' else None)
        sub.add_argument('--json', action='store_true', dest='as_json')
        sub.add_argument('--limit', type=int, default=8)
        sub.add_argument('--rebuild', action='store_true')
        if name == 'review':
            sub.add_argument('--fail-unready', action='store_true',
                             help='exit 1 for a missing/contradicted selection contract; never confirms meaning')
    evidence = commands.add_parser('evidence', help='full source-bound scope and limits for one curated evidence entry')
    evidence.add_argument('id')
    args = parser.parse_args(argv)
    try:
        catalog = load_evidence()
        if args.command == 'evidence':
            entries = [entry for entry in catalog['entries'] if entry['id'] == args.id]
            if not entries:
                raise ValueError('unknown evidence ID')
            print(json.dumps(entries[0], ensure_ascii=False, indent=2))
            return 0
        if not 1 <= args.limit <= 20:
            raise ValueError('limit must be 1..20')
        contract = None
        if args.command == 'review':
            path = relative_file(args.contract)
            contract = json.loads(path.read_text())
            validate_contract(contract)
            for binding in [contract.get('source_packet')] + [
                    source for assignment in contract['assignments']
                    for account in assignment.get('accounts', {}).values()
                    for source in account.get('sources', [])]:
                if binding is not None and digest(relative_file(binding['path'])) != binding['sha256']:
                    raise ValueError('stale candidate source binding')
        elif len(args.forms) > 16:
            raise ValueError('at most 16 forms per bounded request')
        conn = word_profiles.ensure_cache(rebuild=args.rebuild)
        try:
            if args.command == 'profile':
                result = {'source_receipt': word_profiles.receipt(conn),
                          'profiles': [word_card(conn, form, catalog, args.limit) for form in args.forms],
                          'claim_ceiling': CEILING}
                rendered = '\n'.join(render_card(card) for card in result['profiles'])
            else:
                result = review_contract(conn, contract, catalog, args.limit)
                result['contract_sha256'] = digest(path)
                rendered = render_review(result)
        finally:
            conn.close()
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.as_json else rendered)
        return int(args.command == 'review' and args.fail_unready and
                   result['selection_status'] == 'NOT_READY_FOR_PREFERENCE')
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    raise SystemExit(main())
